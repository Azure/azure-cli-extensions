# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Native recovery-plan lifecycles against preconfigured, existing fixtures."""

import json
import os
import re
import time
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from azure.cli.testsdk.scenario_tests import RecordingProcessor
from azure.cli.testsdk.scenario_tests.const import MOCKED_SUBSCRIPTION_ID, MOCKED_TENANT_ID
from azure.cli.testsdk.scenario_tests.decorators import AllowLargeResponse

from .test_resiliency import ResiliencyScenarioTestBase


class RecoveryPlanCredentialScrubber(RecordingProcessor):
    """Standard VCR processor; never intercept native command/transport results."""

    @staticmethod
    def scrub(text):
        def url(match):
            parts = urlsplit(match.group())
            query = parse_qsl(parts.query, keep_blank_values=True)
            if not any(key.lower() in ('sig', 'c', 's', 'h') for key, _ in query):
                return match.group()
            query = [(key, 'REDACTED' if key.lower() in ('sig', 't', 'c', 's', 'h') else value)
                     for key, value in query]
            return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))
        text = re.sub(r'https://[^\s"<>\\]+', url, text)
        replacements = {
            'principalId': '00000000-0000-0000-0000-000000000004',
            'clientId': '00000000-0000-0000-0000-000000000005',
            'tenantId': MOCKED_TENANT_ID,
            'createdBy': 'recording-principal', 'lastModifiedBy': 'recording-principal',
        }
        for key, replacement in replacements.items():
            text = re.sub(r'("' + key + r'"\s*:\s*")[^"]+(")', r'\g<1>' + replacement + r'\2', text)
        return text

    def process_request(self, request):
        request.uri = self.scrub(request.uri)
        if request.body:
            body = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
            request.body = self.scrub(body).encode('utf-8')
        return request

    def process_response(self, response):
        for key in list(response.get('headers', {})):
            if any(word in key.lower() for word in ('cookie', 'authorization', 'token')):
                del response['headers'][key]
            elif key.lower() in ('location', 'azure-asyncoperation'):
                self.replace_header_fn(response, key, self.scrub)
        body = response.get('body', {}).get('string')
        if body:
            response['body']['string'] = self.scrub(body.decode('utf-8') if isinstance(body, bytes) else body)
        return response


class RecoveryPlanLifecycleScenario(ResiliencyScenarioTestBase):
    """One fresh owned plan at a time. Shared grants are setup, never test cleanup."""

    def __init__(self, method_name, *args, **kwargs):
        processors = list(kwargs.pop('recording_processors', None) or [])
        processors.append(RecoveryPlanCredentialScrubber())
        super().__init__(method_name, *args, recording_processors=processors, **kwargs)
        self.vcr.match_on = tuple(self.vcr.match_on) + ('body',)

    def setUp(self):
        super().setUp()
        self.cli_ctx.cloud.endpoints.resource_manager = 'https://eastus2euap.management.azure.com/'
        subscription = MOCKED_SUBSCRIPTION_ID
        aa = ('/subscriptions/' + subscription + '/resourceGroups/ro-cli-fixture'
              '/providers/Microsoft.Automation/automationAccounts/ro-cli-aa')
        fixture = {
            'subscriptionId': subscription, 'tenantId': MOCKED_TENANT_ID,
            'automationAccountId': aa, 'noOpRunbookId': aa + '/runbooks/ro-validation-noop',
            'storageAccountId': '/subscriptions/' + subscription + '/resourceGroups/ro-cli-fixture'
                                '/providers/Microsoft.Storage/storageAccounts/roclistorage',
        }
        identity_id = ('/subscriptions/' + subscription + '/resourcegroups/ro-cli-fixture'
                       '/providers/Microsoft.ManagedIdentity/userAssignedIdentities/ro-cli-uai')
        self.failure_runbook = aa + '/runbooks/ro-validation-failure'
        sg = 'ro-shared-recording-sg'
        if self._is_recording():
            with open(os.environ['RESILIENCY_DRILLS_FIXTURE'], encoding='utf-8-sig') as stream:
                manifest = json.load(stream)
            fixture = manifest['success']
            subscription = manifest['subscriptionId']
            self.assertEqual(subscription.lower(), fixture['subscriptionId'].lower())
            self.assertEqual(manifest['tenantId'].lower(), fixture['tenantId'].lower())
            sg = os.environ['RESILIENCY_SHARED_SERVICE_GROUP']
            identity_id = manifest['identity']['id']
            if manifest.get('failure'):
                self.failure_runbook = manifest['failure']['intentionalFailureRunbookId']
                self.name_replacer.register_name_pair(
                    self.failure_runbook, aa + '/runbooks/ro-validation-failure')
            else:
                self.failure_runbook = None
            pairs = (
                (subscription, MOCKED_SUBSCRIPTION_ID), (fixture['tenantId'], MOCKED_TENANT_ID),
                (fixture['resourceGroup'], 'ro-cli-fixture'), (fixture['automationAccount'], 'ro-cli-aa'),
                (fixture['noOpRunbookId'].rsplit('/', 1)[-1], 'ro-validation-noop'),
                (fixture['storageAccountId'].rsplit('/', 1)[-1], 'roclistorage'),
                (manifest['identity']['name'], 'ro-cli-uai'), (sg, 'ro-shared-recording-sg'),
            )
            for actual, replacement in pairs:
                self.name_replacer.register_name_pair(actual, replacement)
        self.fixture = fixture
        self.kwargs.update(sg_name=sg, subscription=subscription, uai_id=identity_id)

    def _plan(self, command, checks=None):
        return self.cmd('az resiliency recovery-plan ' + command +
                        ' --service-group-name {sg_name} --recovery-plan-name {plan_name}'
                        ' --subscription {subscription}', checks=checks)

    def _create(self, system_assigned=False, manual=False):
        self.kwargs.update(plan_name=self.create_random_name('roclidrl', 24), group_id=str(self.create_guid()))
        inventory = self.cmd('az resiliency recovery-plan list --service-group-name {sg_name}'
                             ' --subscription {subscription}').get_output_in_json()
        self.assertLess(len(inventory), 5, 'Choose another existing SG outside the recording if full.')
        self.assertFalse(any(item['name'] == self.kwargs['plan_name'] for item in inventory))
        group = {'group-unique-id': self.kwargs['group_id'], 'order-id': 0,
                 'description': 'Native CLI lifecycle'}
        if manual:
            group['pre-actions'] = [{'manual-action': {}, 'name': 'cli-manual-pause',
                                     'description': 'Explicit manual pre-action', 'timeout-in-minutes': 10}]
        self.kwargs['groups'] = json.dumps({'default-group': group})
        identity = '--system-assigned' if system_assigned else '--user-assigned {uai_id}'
        self._plan('create --plan-type Zonal --plan-description "Native CLI lifecycle" '
                   '--recovery-groups \'{groups}\' ' + identity + ' --no-wait')
        name = self.kwargs['plan_name']
        self.addCleanup(self._delete, name)
        self._plan('wait --created --interval 5 --timeout 300')
        created = self._plan('show', checks=[
            self.check('name', '{plan_name}'), self.check('properties.provisioningState', 'Succeeded'),
            self.check('properties.planType', 'Zonal'),
            self.check('identity.type', 'SystemAssigned' if system_assigned else 'UserAssigned'),
            self.check('properties.recoveryGroupsSetting.defaultGroup.properties.groupUniqueId', '{group_id}'),
        ]).get_output_in_json()
        if not system_assigned:
            self.assertEqual([key.lower() for key in created['identity']['userAssignedIdentities']],
                             [self.kwargs['uai_id'].lower()])
        self.plan_id = created['id']
        return created

    def _delete(self, name):
        self.kwargs['plan_name'] = name
        jobs = self._plan('recovery-job list').get_output_in_json()
        terminal = ('Completed', 'Failed', 'Canceled', 'Cancelled', 'CompletedWithWarnings')
        self.assertTrue(all(job['properties']['status'] in terminal for job in jobs),
                        'Retain this owned plan: a job is paused, pending or unknown; never cancel it.')
        self._plan('delete --yes --no-wait')
        self._plan('wait --deleted --interval 5 --timeout 300')
        plans = self.cmd('az resiliency recovery-plan list --service-group-name {sg_name}'
                         ' --subscription {subscription}').get_output_in_json()
        self.assertFalse(any(item['name'] == name for item in plans))

    def _poll(self, command, predicate, message):
        deadline = time.monotonic() + 300
        for _ in range(61):
            result = self._plan(command).get_output_in_json()
            if predicate(result):
                return result
            self.assertLess(time.monotonic(), deadline, message)
            time.sleep(5)
        self.fail(message)

    def _configure(self, manual=False, failure=False):
        runbook = self.failure_runbook if failure else self.fixture['noOpRunbookId']
        self.assertTrue(runbook, 'An existing intentional failure runbook is required; do not provision one.')
        self._create(manual=manual)
        resources = self._poll('recovery-resource list',
                               lambda items: any(item['properties']['resourceId'].lower() ==
                                                 self.fixture['storageAccountId'].lower() for item in items),
                               'Selected existing storage was not discovered.')
        selected = next(item for item in resources if item['properties']['resourceId'].lower() ==
                        self.fixture['storageAccountId'].lower())
        self.kwargs['resource_name'] = selected['name']
        self.storage_id = self.fixture['storageAccountId']
        changes = []
        for item in resources:
            included = item['id'] == selected['id']
            change = {'recovery-resource-unique-id': item['properties']['recoveryResourceUniqueId'],
                      'inclusion-state': 'Included' if included else 'Excluded'}
            if included:
                change.update({
                    'recovery-group-id': self.kwargs['group_id'],
                    'associated-identity': {'type': 'UserAssigned',
                                            'user-assigned-identity': self.kwargs['uai_id']},
                    'selected-protection-solution-type': 'CustomRunbook',
                    'selected-protection-solution-setting': {'custom-runbook': {
                        action: {'resource-id': runbook} for action in ('failover-action', 'reprotect-action')}},
                })
            changes.append(change)
        self.kwargs.update(changes=json.dumps(changes), operation_id=self.create_guid())
        response = self._plan("update-resource --operation-id {operation_id} "
                              "--resources-to-update '{changes}'").get_output_in_json()
        self.assertFalse(response.get('failedResources'), 'UpdateResource returned native failures.')
        self._plan('recovery-resource show --recovery-resource-name {resource_name}', checks=[
            self.check('properties.resourceId', self.storage_id, case_sensitive=False),
            self.check('properties.inclusionState', 'Included'),
            self.check('properties.protectionStatus', 'Protected'),
            self.check('properties.recoveryGroupId', '{group_id}'),
            self.check('properties.associatedIdentity.type', 'UserAssigned'),
            self.check('properties.associatedIdentity.userAssignedIdentity', '{uai_id}', case_sensitive=False),
            self.check('properties.selectedProtectionSolutionType', 'CustomRunbook'),
            self.check('properties.selectedProtectionSolutionSetting.failoverAction.resourceId', runbook),
            self.check('properties.selectedProtectionSolutionSetting.reprotectAction.resourceId', runbook),
        ])
        current = self._plan('recovery-resource list').get_output_in_json()
        self.assertEqual(len(current), len(resources))
        for item in current:
            self.assertEqual(item['properties']['inclusionState'],
                             'Included' if item['id'] == selected['id'] else 'Excluded')
        self._job(self._action('check-readiness'), 'CheckRecoveryPlanReadiness')
        return selected

    def _arguments(self, selected, operation, consent='Allowed'):
        request = {'selected-resource-ids': [selected['id']]}
        if operation == 'Failover':
            request.update({'source-locations': [], 'execution-configurations': {'user-consent': consent}})
            arguments = "--failover-direction FromSpecificLocations --failover-request-properties '{request}'"
        else:
            arguments = "--reprotect-request-properties '{request}'"
        self.kwargs['request'] = json.dumps(request)
        return arguments

    def _action(self, command):
        self.kwargs['operation_id'] = self.create_guid()
        return self._plan(command + ' --operation-id {operation_id}').get_output_in_json()

    def _void(self, command):
        self.kwargs['operation_id'] = self.create_guid()
        before = len(self.cassette.requests) + self.cassette.play_count
        result = self._plan(command + ' --operation-id {operation_id}')
        self.assertEqual(result.exit_code, 0)
        self.assertIn(result.get_output_in_json() if result.output.strip() else None, (None, {}))
        self.assertGreater(len(self.cassette.requests) + self.cassette.play_count, before,
                           'A successful native void command must still issue recorded HTTP.')

    def _job(self, response, operation, status='Completed', resources=True):
        self.assertTrue(response['jobId'].lower().startswith(self.plan_id.lower() + '/recoveryjobs/'))
        self.kwargs['job_name'] = response['jobId'].rsplit('/', 1)[-1]

        def done(job):
            self.assertEqual(job['id'].lower(), response['jobId'].lower())
            self.assertEqual(job['properties']['operation'], operation)
            actual = job['properties']['status']
            if actual == status:
                return True
            self.assertNotIn(actual, ('Failed', 'Completed', 'Paused', 'Canceled', 'Cancelled',
                                      'CompletedWithWarnings'))
            return False

        job = self._poll('recovery-job show --recovery-job-name {job_name}', done,
                         'Exact native job did not reach ' + status)
        jobs = self._plan('recovery-job list').get_output_in_json()
        matches = [item for item in jobs if item['id'].lower() == response['jobId'].lower()]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['properties']['status'], status)
        if resources:
            items = self._plan('recovery-job recovery-job-resource list '
                               '--recovery-job-name {job_name}').get_output_in_json()
            selected = [item for item in items if item['properties']['resourceId'].lower() == self.storage_id.lower()]
            self.assertEqual(len(selected), 1)
            self.assertEqual(selected[0]['properties']['status'], status)
            self.kwargs['job_resource_name'] = selected[0]['name']
            self._plan('recovery-job recovery-job-resource show --recovery-job-name {job_name} '
                       '--job-resource-name {job_resource_name}', checks=[
                           self.check('properties.resourceId', self.storage_id, case_sensitive=False),
                           self.check('properties.status', status),
                           self.check('properties.protectionSolutionType', 'CustomRunbook')])
        return job

    @AllowLargeResponse(size_kb=2048)
    def test_recovery_plan_crud_identity_lifecycle(self):
        created = self._create(system_assigned=True)
        self.kwargs.update(expected_principal=created['identity']['principalId'],
                           expected_tenant=created['identity']['tenantId'])
        self._plan('update --plan-description "Updated native lifecycle"', checks=[
            self.check('properties.planDescription', 'Updated native lifecycle'),
            self.check('name', '{plan_name}'), self.check('identity.principalId', '{expected_principal}')])
        self._plan('identity assign --system-assigned', checks=[
            self.check('type', 'SystemAssigned'), self.check('principalId', '{expected_principal}'),
            self.check('tenantId', '{expected_tenant}')])
        before = len(self.cassette.requests) + self.cassette.play_count
        waited = self._plan('identity wait --interval 5 --timeout 120 --custom '
                            '"identity.type==\'SystemAssigned\' && identity.principalId==\'{expected_principal}\' '
                            '&& identity.tenantId==\'{expected_tenant}\'"')
        self.assertEqual(waited.exit_code, 0)
        self.assertEqual(waited.output.strip(), '')
        self.assertGreater(len(self.cassette.requests) + self.cassette.play_count, before)
        self._plan('identity show', checks=[
            self.check('type', 'SystemAssigned'), self.check('principalId', '{expected_principal}'),
            self.check('tenantId', '{expected_tenant}')])
        self._plan('show', checks=[
            self.check('id', created['id']),
            self.check('properties.planDescription', 'Updated native lifecycle'),
            self.check('identity.principalId', '{expected_principal}'),
            self.check('identity.tenantId', '{expected_tenant}')])
        for command in ('identity remove --system-assigned', 'identity show'):
            self._plan(command, checks=[
                self.check('type', 'None'), self.check('principalId', None), self.check('tenantId', None)])
        self._plan('show', checks=[
            self.check('identity.type', 'None'), self.check('identity.principalId', None),
            self.check('properties.planType', 'Zonal'),
            self.check('properties.recoveryGroupsSetting.defaultGroup.properties.groupUniqueId', '{group_id}')])

    @AllowLargeResponse(size_kb=2048)
    def test_recovery_plan_shared_uai_success_lifecycle(self):
        selected = self._configure()
        for operation in ('Failover', 'Reprotect'):
            self._void('validate-for-operation --operation-name ' + operation)
            arguments = self._arguments(selected, operation)
            qualified = self._action('validate-for-' + operation.lower() + ' ' + arguments)
            matches = [item for item in qualified['recoveryResourceQualifications']
                       if item['recoveryResource']['id'].lower() == selected['id'].lower()]
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0]['operationQualificationDetails']['qualificationState'], 'Qualified')
            self.assertFalse(matches[0]['operationQualificationDetails'].get('notQualifiedReasons'))
            self._job(self._action(operation.lower() + ' ' + arguments), operation)
        self._plan('show', checks=[self.check('properties.planState', 'Ready')])
        self._void('finalize')
        before = len(self.cassette.requests) + self.cassette.play_count
        waited = self._plan('wait --interval 5 --timeout 300 --custom '
                            '"properties.planState==\'Ready\' && properties.provisioningState==\'Succeeded\'"')
        self.assertEqual(waited.exit_code, 0)
        self.assertEqual(waited.output.strip(), '')
        self.assertGreater(len(self.cassette.requests) + self.cassette.play_count, before)
        self._plan('show', checks=[
            self.check('properties.planState', 'Ready'), self.check('identity.type', 'UserAssigned'),
            self.check('id', self.plan_id),
            self.check('properties.recoveryGroupsSetting.defaultGroup.properties.groupUniqueId', '{group_id}')])

    @AllowLargeResponse(size_kb=2048)
    def test_recovery_plan_shared_uai_resume_lifecycle(self):
        selected = self._configure(manual=True)
        response = self._action('failover ' + self._arguments(selected, 'Failover', 'Unspecified'))
        self._job(response, 'Failover', status='Paused', resources=False)
        self._void('recovery-job resume --recovery-job-name {job_name} '
                   '--description "Resume the same manual-pause job"')
        self._job(response, 'Failover')

    @AllowLargeResponse(size_kb=2048)
    def test_recovery_plan_shared_uai_retry_lifecycle(self):
        # Independent from Resume: a paused pre-action must never seed the retry case.
        selected = self._configure(failure=True)
        original = self._action('reprotect ' + self._arguments(selected, 'Reprotect'))
        failed = self._job(original, 'Reprotect', status='Failed')
        self.assertNotIn('authorizationfailed', json.dumps(failed).lower())
        previous = failed['properties'].get('retryDetails', [])
        number = max((item['retryAttempt'] for item in previous), default=0)
        self._void('recovery-job retry --recovery-job-name {job_name}')
        self._poll('recovery-job show --recovery-job-name {job_name}',
                   lambda job: len(job['properties'].get('retryDetails', [])) > len(previous)
                   and job['properties']['retryDetails'][-1]['status'] == 'Failed',
                   'Retry did not finish a new attempt on the original job.')
        repeated = self._job(original, 'Reprotect', status='Failed')
        self.assertEqual(len(repeated['properties']['retryDetails']), len(previous) + 1)
        latest = repeated['properties']['retryDetails'][-1]
        self.assertEqual(latest['retryAttempt'], number + 1)
        self.assertEqual(latest['status'], 'Failed')
