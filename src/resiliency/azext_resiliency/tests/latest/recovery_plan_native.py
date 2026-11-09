# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Serial native recovery-plan recordings using an explicitly approved shared fixture."""

import json
import os
import re
import time
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from azure.cli.core._profile import Profile
from azure.cli.testsdk.scenario_tests import RecordingProcessor
from azure.cli.testsdk.scenario_tests.recording_processors import SubscriptionRecordingProcessor
from azure.cli.testsdk.scenario_tests.const import MOCKED_SUBSCRIPTION_ID, MOCKED_TENANT_ID

from .test_resiliency import ResiliencyScenarioTestBase


class RecoveryPlanSubscriptionScrubber(SubscriptionRecordingProcessor):
    """Keep the cross-subscription runbook fixture distinct from the plan's subscription."""

    def __init__(self):
        super().__init__(MOCKED_SUBSCRIPTION_ID)
        self.secondary = '00000000-0000-0000-0000-000000000003'
        self.secondary_actual = self.secondary

    def _replace_subscription_id(self, val):
        def replace(match):
            subscription = match.group(2)
            replacement = self.secondary if subscription.lower() in (
                self.secondary.lower(), self.secondary_actual.lower()) else MOCKED_SUBSCRIPTION_ID
            return match.group(1) + replacement
        return re.sub(
            r'((?:/|\\/|https://graph\.windows\.net/)subscriptions?(?:/|\\/))'
            r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
            replace, val, flags=re.IGNORECASE)


class RecoveryPlanSignedMonitorScrubber(RecordingProcessor):
    """Scrub signed monitor values consistently in recorded request and response URLs."""

    def __init__(self, scenario):
        self.scenario = scenario

    def _wire_evidence(self, kind, value):
        destination = os.environ.get('RESILIENCY_SCENARIO_EVIDENCE')
        if not destination:
            return
        directory = Path(destination)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / (self.scenario + '-wire.jsonl')
        with path.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps({'time': time.time(), 'kind': kind, **value}, default=str) + '\n')

    @staticmethod
    def _scrub(text):
        def replace(match):
            parts = urlsplit(match.group(0))
            query = parse_qsl(parts.query, keep_blank_values=True)
            if not any(key.lower() in ('sig', 'c', 's', 'h') for key, _ in query):
                return match.group(0)
            clean = [(key, 'REDACTED' if key.lower() in ('sig', 'c', 's', 'h', 't') else value)
                     for key, value in query]
            return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(clean), parts.fragment))
        return re.sub(r'https://[^\s"<>\\]+', replace, text)

    def process_request(self, request):
        request.uri = self._scrub(request.uri)
        headers = {key: value for key, value in request.headers.items()
                   if not any(marker in key.lower() for marker in ('authorization', 'cookie', 'token'))}
        body = request.body.decode('utf-8', errors='replace') if isinstance(request.body, bytes) else request.body
        self._wire_evidence('request', {
            'method': request.method, 'uri': request.uri, 'headers': headers,
            'body': '[OMITTED]' if 'login.' in request.uri or '/oauth' in request.uri else body,
        })
        return request

    def process_response(self, response):
        for header in ('location', 'azure-asyncoperation'):
            self.replace_header_fn(response, header, self._scrub)
        body = response.get('body', {}).get('string')
        if isinstance(body, bytes):
            body = body.decode('utf-8', errors='replace')
        self._wire_evidence('response', {
            'status': response.get('status'), 'headers': {
                key: value for key, value in response.get('headers', {}).items()
                if not any(marker in key.lower() for marker in ('authorization', 'cookie', 'token'))},
            'body': body,
        })
        return response


class ResiliencyNativeRecoveryPlanScenario(ResiliencyScenarioTestBase):
    SAME_SUBSCRIPTION_FIXTURE = False

    @classmethod
    def _playback_fixture(cls):
        subscription = MOCKED_SUBSCRIPTION_ID if cls.SAME_SUBSCRIPTION_FIXTURE else '00000000-0000-0000-0000-000000000003'
        fixture = {
            'subscriptionId': subscription, 'tenantId': MOCKED_TENANT_ID,
            'serviceGroup': 'ro-shared-recording-sg', 'resourceGroup': 'ro-cli-custom-fixture',
            'automationAccount': 'ro-cli-validation-aa',
        }
        aa = ('/subscriptions/' + subscription + '/resourceGroups/' + fixture['resourceGroup']
              + '/providers/Microsoft.Automation/automationAccounts/' + fixture['automationAccount'])
        fixture.update(noOpRunbookId=aa + '/runbooks/ro-validation-noop',
                       intentionalFailureRunbookId=None if cls.SAME_SUBSCRIPTION_FIXTURE
                       else aa + '/runbooks/ro-validation-failure')
        return fixture

    @staticmethod
    def _validate_runbook_id(runbook_id, automation_id, label):
        prefix = automation_id + '/runbooks/'
        if not isinstance(runbook_id, str) or not runbook_id.lower().startswith(prefix.lower()):
            raise ValueError(label + ' must be an explicit child of the manifest Automation Account.')
        name = runbook_id[len(prefix):]
        if not name or any(char in name for char in '/\\?#%'):
            raise ValueError(label + ' must identify exactly one runbook, without a URL/query.')
        return runbook_id

    def _prepare_live_fixture(self, actual, context, shared_group):
        actual = dict(actual)
        same = actual['subscriptionId'].lower() == context.lower()
        if same != self.SAME_SUBSCRIPTION_FIXTURE:
            raise ValueError('Live fixture subscription relationship does not match this scenario class.')
        aa = ('/subscriptions/' + actual['subscriptionId'] + '/resourceGroups/' + actual['resourceGroup']
              + '/providers/Microsoft.Automation/automationAccounts/' + actual['automationAccount'])
        if actual.get('automationAccountId', aa).lower() != aa.lower():
            raise ValueError('Manifest Automation Account ID disagrees with its component fields.')
        self._validate_runbook_id(actual.get('noOpRunbookId'), aa, 'noOpRunbookId')
        failure = actual.get('intentionalFailureRunbookId')
        if failure is not None:
            self._validate_runbook_id(failure, aa, 'intentionalFailureRunbookId')
            if failure.lower() == actual['noOpRunbookId'].lower():
                raise ValueError('Intentional failure runbook must not alias the no-op runbook.')
        # Same-subscription mode must never classify the real primary as secondary.
        self.subscription_scrubber.secondary_actual = (
            self.subscription_scrubber.secondary if same else actual['subscriptionId'])
        actual['serviceGroup'] = shared_group
        fake = self._playback_fixture()
        for key in ('subscriptionId', 'tenantId', 'serviceGroup', 'resourceGroup', 'automationAccount'):
            self.name_replacer.register_name_pair(actual[key], fake[key])
        self.name_replacer.register_name_pair(actual['noOpRunbookId'].rsplit('/', 1)[-1], 'ro-validation-noop')
        if failure:
            self.name_replacer.register_name_pair(failure.rsplit('/', 1)[-1], 'ro-validation-failure')
        self.name_replacer.register_name_pair(context, MOCKED_SUBSCRIPTION_ID)
        return actual

    def _runbook_for_configuration(self, failure):
        runbook = self.failure_runbook_id if failure else self.runbook_id
        validated = self._validate_runbook_id(
            runbook, self.automation_id, 'intentionalFailureRunbookId' if failure else 'noOpRunbookId')
        if failure and validated.lower() == self.runbook_id.lower():
            raise ValueError('Intentional failure runbook must not alias the no-op runbook.')
        return validated

    def __init__(self, method_name, *args, **kwargs):
        processors = list(kwargs.pop('recording_processors', None) or [])
        processors.append(RecoveryPlanSignedMonitorScrubber(method_name))
        super().__init__(method_name, *args, recording_processors=processors, **kwargs)
        # Also pin serialized native request bodies (resource exclusions, identities and runbooks).
        self.vcr.match_on = tuple(self.vcr.match_on) + ('body',)
        self.subscription_scrubber = RecoveryPlanSubscriptionScrubber()
        self.recording_processors = [
            self.subscription_scrubber if isinstance(processor, SubscriptionRecordingProcessor) else processor
            for processor in self.recording_processors
        ]

    def setUp(self):
        super().setUp()
        self.cli_ctx.cloud.endpoints.resource_manager = 'https://eastus2euap.management.azure.com/'
        if not self._is_recording() and not self.SAME_SUBSCRIPTION_FIXTURE:
            # Standard testsdk playback provides one fake cached subscription. The native AAZ
            # resource-ID validator also resolves the cross-subscription runbook's subscription.
            # Supply only offline authentication metadata; HTTP responses still come from VCR.
            subscriptions = Profile(cli_ctx=self.cli_ctx).load_cached_subscriptions()
            secondary = dict(subscriptions[0])
            secondary.update(id=self.subscription_scrubber.secondary,
                             name='Shared runbook playback subscription', isDefault=False)
            profile_patch = patch.object(
                Profile, 'load_cached_subscriptions', return_value=[*subscriptions, secondary])
            profile_patch.start()
            self.addCleanup(profile_patch.stop)
        fixture = self._playback_fixture()
        context = MOCKED_SUBSCRIPTION_ID
        if self._is_recording():
            fixture_path = os.environ.get('RESILIENCY_CUSTOM_RUNBOOK_FIXTURE')
            shared_group = os.environ.get('RESILIENCY_SHARED_SERVICE_GROUP')
            context = os.environ.get('RESILIENCY_TEST_SUBSCRIPTION_ID')
            self.assertTrue(fixture_path, 'An explicit approved fixture manifest is required.')
            self.assertTrue(shared_group, 'An explicit approved shared service group is required.')
            self.assertTrue(context, 'An explicit enrollment subscription context is required.')
            with open(fixture_path, encoding='utf-8-sig') as fixture_file:
                actual = json.load(fixture_file)
            fixture = self._prepare_live_fixture(actual, context, shared_group)
        self.kwargs.update({
            'sg_name': fixture['serviceGroup'],
            'context_subscription': context,
            'fixture_subscription': fixture['subscriptionId'],
            'plan_name': self.create_random_name('roclinat', 24),
            'group_id': str(self.create_guid()),
        })
        self.runbook_id = fixture['noOpRunbookId']
        self.failure_runbook_id = fixture.get('intentionalFailureRunbookId')
        self.automation_id = self.runbook_id.rsplit('/runbooks/', 1)[0]

    def _plan(self, command, checks=None):
        self._evidence('native-command-start', {'command': command, 'pending': True})
        result = self.cmd(
            'az resiliency recovery-plan ' + command +
            ' --service-group-name {sg_name} --recovery-plan-name {plan_name} '
            '--subscription {context_subscription}', checks=checks)
        try:
            output = result.get_output_in_json()
        except ValueError:
            output = None
        self._evidence('native-command-result', {'command': command, 'nativeOutput': output})
        return result

    def _evidence(self, label, value):
        destination = os.environ.get('RESILIENCY_SCENARIO_EVIDENCE')
        if not self._is_recording() or not destination:
            return
        directory = Path(destination)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / (self._testMethodName + '.jsonl')
        row = {
            'time': time.time(), 'label': label, 'plan': self.kwargs['plan_name'],
            'serviceGroup': self.kwargs['sg_name'], **value,
        }
        # Local diagnostic sidecar only. Formal recording remains the standard VCR YAML.
        with path.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(row) + '\n')

    def _list(self):
        return self.cmd('az resiliency recovery-plan list --service-group-name {sg_name} '
                        '--subscription {context_subscription}').get_output_in_json()

    def _create(self, bounded=False):
        self.bounded_cleanup = bounded
        inventory = self._list()
        self.assertLess(len(inventory), 5, 'The shared service group must stay within its five-plan limit.')
        self.assertFalse(any(item['name'].startswith('roclinat') for item in inventory),
                         'Another CLI recording plan must be cleaned up before this serial scenario.')
        self.kwargs['groups'] = json.dumps({
            'default-group': {
                'group-unique-id': self.kwargs['group_id'], 'order-id': 0,
                'description': 'Native shared-fixture recording group',
            },
        })
        self.addCleanup(self._delete)
        command = (
            'create --plan-type Zonal --plan-description "Native CLI recording" '
            '--system-assigned --recovery-groups \'{groups}\'')
        checks = [
            self.check('name', '{plan_name}'),
            self.check('properties.provisioningState', 'Succeeded'),
        ]
        if bounded:
            # Action prerequisites use the native asynchronous option and native bounded wait.
            # The dedicated Create contract scenario above still tests synchronous Create output.
            self._plan(command + ' --no-wait')
            self._plan('wait --created --interval 10 --timeout 300')
            return self._plan('show', checks=checks).get_output_in_json()
        return self._plan(command, checks=checks).get_output_in_json()

    def _delete(self):
        self._plan('delete --yes --no-wait' if self.bounded_cleanup else 'delete --yes')
        self._plan('wait --deleted --interval 5 --timeout 300')
        self.assertFalse(any(item['name'] == self.kwargs['plan_name'] for item in self._list()))

    def _storage(self):
        deadline = time.time() + 300
        while True:
            resources = self._plan('recovery-resource list').get_output_in_json()
            storage = [item for item in resources
                       if '/providers/microsoft.storage/storageaccounts/' in item['properties']['resourceId'].lower()]
            if storage:
                selected = sorted(storage, key=lambda item: item['properties']['resourceId'].lower())[0]
                self.kwargs['resource_name'] = selected['name']
                self.storage_id = selected['properties']['resourceId']
                return resources, selected
            self.assertLess(time.time(), deadline, 'Native inventory did not expose a current storage member.')
            time.sleep(15)

    def _configure_runbook(self, failure=False, bounded=False):
        runbook = self._runbook_for_configuration(failure)
        created = self._create(bounded=bounded)
        resources, selected = self._storage()
        changes = []
        for item in resources:
            change = {
                'recovery-resource-unique-id': item['properties']['recoveryResourceUniqueId'],
                'inclusion-state': 'Included' if item['id'] == selected['id'] else 'Excluded',
            }
            if item['id'] == selected['id']:
                change.update({
                    'recovery-group-id': self.kwargs['group_id'],
                    'associated-identity': {'type': 'SystemAssigned'},
                    'selected-protection-solution-type': 'CustomRunbook',
                    'selected-protection-solution-setting': {
                        'custom-runbook': {
                            action: {'resource-id': runbook}
                            for action in ('failover-action', 'reprotect-action')
                        },
                    },
                })
            changes.append(change)
        self.kwargs.update({'changes': json.dumps(changes), 'operation_id': str(self.create_guid())})
        updated = self._plan(
            'update-resource --operation-id {operation_id} --resources-to-update \'{changes}\''
        ).get_output_in_json()
        self.assertFalse(updated.get('failedResources'), 'Native UpdateResource reported failures.')
        self._plan('recovery-resource show --recovery-resource-name {resource_name}', checks=[
            self.check('properties.inclusionState', 'Included'),
            self.check('properties.selectedProtectionSolutionType', 'CustomRunbook'),
            self.check('properties.recoveryGroupId', '{group_id}'),
            self.check('properties.selectedProtectionSolutionSetting.failoverAction.resourceId', runbook),
            self.check('properties.selectedProtectionSolutionSetting.reprotectAction.resourceId', runbook),
        ])
        current = self._plan('recovery-resource list').get_output_in_json()
        self.assertEqual(len(current), len(resources))
        for item in current:
            expected = 'Included' if item['id'] == selected['id'] else 'Excluded'
            self.assertEqual(item['properties']['inclusionState'], expected)
        return created, selected

    def _action_arguments(self, operation, selected):
        request = {'selected-resource-ids': [selected['id']]}
        if operation == 'Failover':
            zones = selected['properties'].get('resourcePhysicalZones', [])
            locations = zones or [selected['properties']['resourceLocation']]
            self.assertTrue(locations[0], 'The native member inventory must identify a source location.')
            request.update({
                'source-locations': [locations[0]],
                'execution-configurations': {'user-consent': 'Allowed'},
            })
            arguments = ("--failover-direction FromSpecificLocations "
                         "--failover-request-properties '{action_request}'")
        else:
            arguments = "--reprotect-request-properties '{action_request}'"
        self.kwargs['action_request'] = json.dumps(request)
        return arguments

    def _qualify(self, operation, selected):
        self.kwargs.update({'operation_id': str(self.create_guid()), 'operation_name': operation})
        before = len(self.cassette.requests) + self.cassette.play_count
        validation = self._plan(
            'validate-for-operation --operation-id {operation_id} --operation-name {operation_name}'
        ).get_output_in_json()
        self.assertEqual(validation, {})
        self.assertGreater(len(self.cassette.requests) + self.cassette.play_count, before)
        arguments = self._action_arguments(operation, selected)
        self.kwargs['operation_id'] = str(self.create_guid())
        result = self._plan(
            'validate-for-' + operation.lower() + ' --operation-id {operation_id} ' + arguments
        ).get_output_in_json()
        matches = [item for item in result['recoveryResourceQualifications']
                   if item['recoveryResource']['id'].lower() == selected['id'].lower()]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['operationQualificationDetails']['qualificationState'], 'Qualified')
        self.assertFalse(matches[0]['operationQualificationDetails'].get('notQualifiedReasons'))
        return arguments

    def _readiness(self):
        self.kwargs['operation_id'] = str(self.create_guid())
        response = self._plan('check-readiness --operation-id {operation_id}').get_output_in_json()
        return self._observe_job(response, operation='CheckRecoveryPlanReadiness')

    def _failover(self, selected):
        arguments = self._action_arguments('Failover', selected)
        self.kwargs['operation_id'] = str(self.create_guid())
        response = self._plan('failover --operation-id {operation_id} ' + arguments).get_output_in_json()
        return self._observe_job(response, operation='Failover')

    def _authorize_runbooks(self, principal_id):
        grants = (
            (self.automation_id, '4fe576fe-1146-4730-92eb-48519fa6bf9f'),
            (self.automation_id, 'acdd72a7-3385-48ef-bd42-f606fba81ae7'),
            (self.storage_id, 'acdd72a7-3385-48ef-bd42-f606fba81ae7'),
        )
        for scope, role in grants:
            subscription = scope.split('/')[2]
            self.kwargs.update({
                'assignment_scope': scope, 'assignment_role': role,
                'assignment_principal': principal_id, 'assignment_subscription': subscription,
            })
            # Native exact-principal lookup plus exact scope/role matching. Existing grants are
            # evidence of authorization only, never ownership and never registered for cleanup.
            existing = self._role_cmd(
                'az role assignment list --scope {assignment_scope} '
                '--assignee-object-id {assignment_principal} '
                '--fill-principal-name false --fill-role-definition-name false '
                '--subscription {assignment_subscription}'
            ).get_output_in_json()
            matches = [
                assignment for assignment in existing
                if assignment['principalId'].lower() == principal_id.lower()
                and assignment['scope'].lower() == scope.lower()
                and assignment['roleDefinitionId'].lower().endswith('/' + role)
            ]
            self.assertLessEqual(len(matches), 1)
            if matches:
                self._evidence('existing-role-not-owned', {'assignment': matches[0]})
                continue
            name = str(self.create_guid())
            assignment_id = scope + '/providers/Microsoft.Authorization/roleAssignments/' + name
            self.kwargs.update({
                'assignment_name': name, 'assignment_scope': scope,
                'assignment_role': role, 'assignment_principal': principal_id,
            })
            assignment = self._role_cmd(
                'az role assignment create --name {assignment_name} --scope {assignment_scope} '
                '--role {assignment_role} --assignee-object-id {assignment_principal} '
                '--assignee-principal-type ServicePrincipal --subscription {assignment_subscription}'
            ).get_output_in_json()
            self.assertEqual(assignment['name'], name)
            self.assertEqual(assignment['principalId'], principal_id)
            self.assertEqual(assignment['scope'].lower(), scope.lower())
            self.assertTrue(assignment['roleDefinitionId'].lower().endswith('/' + role))
            self.addCleanup(self._delete_role, assignment_id)
            self._evidence('created-role-owned', {'assignment': assignment})

    def _delete_role(self, assignment_id):
        self._role_cmd('az role assignment delete --ids ' + assignment_id +
                       ' --subscription {context_subscription}')
        self._evidence('removed-owned-role', {'assignmentId': assignment_id})

    def _role_cmd(self, command):
        # Keep setup and RO requests on the approved process-local Canary endpoint.
        self.assertTrue(command.startswith('az role assignment '))
        self.assertEqual(self.cli_ctx.cloud.endpoints.resource_manager,
                         'https://eastus2euap.management.azure.com/')
        return self.cmd(command)

    def _observe_job(self, response, expected_status='Completed', check_resources=True, operation=None):
        self.assertIn('jobId', response, 'Native action output must return jobId; no response substitution.')
        self.kwargs['job_name'] = response['jobId'].rstrip('/').rsplit('/', 1)[-1]
        self.assertTrue(self.kwargs['job_name'])
        deadline = time.time() + 900
        terminal = ('Failed', 'Canceled', 'Cancelled', 'CompletedWithWarnings', 'Paused', 'Completed')
        while True:
            job = self._plan('recovery-job show --recovery-job-name {job_name}').get_output_in_json()
            self.assertEqual(job['name'], self.kwargs['job_name'])
            self.assertEqual(job['id'].lower(), response['jobId'].lower())
            if operation:
                self.assertEqual(job['properties']['operation'], operation)
            if job['properties']['status'] == expected_status:
                break
            self.assertNotIn(job['properties']['status'], terminal)
            self.assertLess(time.time(), deadline, 'Native recovery job exceeded the bounded interval.')
            time.sleep(15)
        jobs = self._plan('recovery-job list').get_output_in_json()
        matches = [item for item in jobs if item['name'] == self.kwargs['job_name']]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['properties']['status'], expected_status)
        if operation:
            self.assertEqual(matches[0]['properties']['operation'], operation)
        if not check_resources:
            return job
        job_resources = self._plan(
            'recovery-job recovery-job-resource list --recovery-job-name {job_name}').get_output_in_json()
        selected = [item for item in job_resources
                    if item['properties']['resourceId'].lower() == self.storage_id.lower()]
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]['properties']['status'], expected_status)
        self.kwargs['job_resource_name'] = selected[0]['name']
        self._plan(
            'recovery-job recovery-job-resource show --recovery-job-name {job_name} '
            '--job-resource-name {job_resource_name}', checks=[
                self.check('properties.resourceId', self.storage_id),
                self.check('properties.status', expected_status),
                self.check('properties.protectionSolutionType', 'CustomRunbook'),
            ])
        return job
