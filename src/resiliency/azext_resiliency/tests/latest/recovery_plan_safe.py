# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Six bounded Nov8 standard scenarios; pending workflows retain their owned fixtures."""

import json
import os
import time
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

from azure.cli.testsdk.scenario_tests import RecordingProcessor
from azure.cli.testsdk.scenario_tests.decorators import AllowLargeResponse
from requests.sessions import Session

from .recovery_plan_safe_cleanup import OwnedScenarioLedger
from .recovery_plan_native import ResiliencyNativeRecoveryPlanScenario as _NativeBase


class _RawWireEvidence(RecordingProcessor):
    """Capture noncredential wire evidence BEFORE standard identifier/header sanitizers."""

    def __init__(self, scenario):
        self.scenario = scenario

    def save(self, value):
        directory = os.environ.get('RESILIENCY_SCENARIO_EVIDENCE')
        if not directory or not self.scenario._is_recording():
            return
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        target = path / (self.scenario._testMethodName + '-raw-wire.jsonl')
        value.update(time=time.time(), command=self.scenario.active_command)
        with target.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(value, default=str) + '\n')

    @staticmethod
    def headers(headers):
        return {key: value for key, value in headers.items()
                if not any(part in key.lower() for part in ('authorization', 'cookie', 'token', 'secret'))}

    def process_request(self, request):
        body = request.body.decode('utf-8', errors='replace') if isinstance(request.body, bytes) else request.body
        self.save({
            'kind': 'request', 'method': request.method, 'uri': request.uri,
            'headers': self.headers(request.headers),
            'body': '[OMITTED]' if 'login.' in request.uri or '/oauth' in request.uri else body,
        })
        return request

    def process_response(self, response):
        body = response.get('body', {}).get('string')
        if isinstance(body, bytes):
            body = body.decode('utf-8', errors='replace')
        headers = {key.lower(): value for key, value in response.get('headers', {}).items()}
        location = headers.get('azure-asyncoperation') or headers.get('location')
        if location and self.scenario.active_command:
            location = location[0] if isinstance(location, list) else location
            if '/operationstatuses/' in location.lower():
                self.scenario.expected_monitors[self.scenario.active_command] = urlsplit(location).path
        try:
            monitor = json.loads(body) if body else {}
        except ValueError:
            monitor = {}
        if isinstance(monitor, dict) and monitor.get('status') in ('Succeeded', 'Failed', 'Canceled', 'Cancelled'):
            self.scenario.terminal_monitors[self.scenario.active_command] = monitor
        self.save({'kind': 'response', 'status': response.get('status'),
                   'headers': self.headers(response.get('headers', {})), 'body': body})
        return response


class _DeclaredScenariosOnly(type):
    """Reuse native helpers without discovering the inherited historical scenarios."""

    def __getattribute__(cls, name):
        if name.startswith('test_') and name not in type.__getattribute__(cls, '__dict__'):
            return None
        return super().__getattribute__(name)


class ResiliencySafeRecoveryPlanScenario(_NativeBase, metaclass=_DeclaredScenariosOnly):
    SAME_SUBSCRIPTION_FIXTURE = True

    def __init__(self, method_name, *args, **kwargs):
        super().__init__(method_name, *args, **kwargs)
        self.active_command = None
        self.expected_monitors = {}
        self.terminal_monitors = {}
        self.recording_processors.insert(0, _RawWireEvidence(self))

    def addCleanup(self, function, *args, **kwargs):
        # PO-001: do not inherit unconditional grant or plan deletion callbacks.
        if getattr(function, '__self__', None) is self and function.__name__ in ('_delete', '_delete_role'):
            return
        super().addCleanup(function, *args, **kwargs)

    def setUp(self):
        super().setUp()
        self.successful_scenario = False
        self.plan_type = 'Zonal'
        self.kwargs['manual_action_name'] = self.create_random_name('roclipause', 20)
        self.plan_id = (
            '/providers/Microsoft.Management/serviceGroups/' + self.kwargs['sg_name']
            + '/providers/Microsoft.AzureResilienceManagement/recoveryPlans/' + self.kwargs['plan_name'])
        self.ledger = OwnedScenarioLedger(self.plan_id, self._persist_ledger)
        self.addCleanup(self._coordinated_cleanup)
        if self._is_recording() and os.environ.get('RESILIENCY_SCENARIO_EVIDENCE'):
            original = Session.send

            def capture(session, request, **kwargs):
                response = original(session, request, **kwargs)
                # Supplemental private capture only; the ORIGINAL response is returned
                # unchanged and the formal recording remains ordinary ScenarioTest YAML.
                credentials = 'login.' in request.url or '/oauth' in request.url
                body = request.body.decode('utf-8', errors='replace') if isinstance(request.body, bytes) else request.body
                try:
                    response_body = response.json()
                except ValueError:
                    response_body = response.text
                target = Path(os.environ['RESILIENCY_SCENARIO_EVIDENCE']) / (
                    self._testMethodName + '-transport.jsonl')
                target.parent.mkdir(parents=True, exist_ok=True)
                row = {
                    'time': time.time(), 'command': self.active_command, 'method': request.method,
                    'uri': request.url, 'requestHeaders': _RawWireEvidence.headers(request.headers),
                    'requestBody': '[OMITTED]' if credentials else body, 'status': response.status_code,
                    'responseHeaders': _RawWireEvidence.headers(response.headers),
                    'responseBody': '[OMITTED]' if credentials else response_body,
                }
                if request.method == 'PUT' and response.status_code in (200, 201) and isinstance(response_body, dict):
                    self.ledger.confirm_creation_from_native(response_body, self.kwargs['group_id'])
                with target.open('a', encoding='utf-8') as stream:
                    stream.write(json.dumps(row, default=str) + '\n')
                return response

            transport_patch = patch.object(Session, 'send', capture)
            transport_patch.start()
            self.addCleanup(transport_patch.stop)

    def _persist_ledger(self, state):
        directory = os.environ.get('RESILIENCY_SCENARIO_EVIDENCE')
        if not directory or not self._is_recording():
            return
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        target = path / (self._testMethodName + '-ownership.json')
        temporary = target.with_suffix('.tmp')
        with temporary.open('w', encoding='utf-8') as stream:
            json.dump(state, stream, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)

    def _plan(self, command, checks=None):
        verb = command.split()[0]
        if verb == 'create':
            command = command.replace('--plan-type Zonal', '--plan-type ' + self.plan_type)
            if self._testMethodName.endswith('_resume'):
                groups = json.loads(self.kwargs['groups'])
                groups['default-group']['pre-actions'] = [{
                    'manual-action': {}, 'name': self.kwargs['manual_action_name'],
                    'description': 'Explicit native manual pause before failover',
                    'timeout-in-minutes': 10,
                }]
                self.kwargs['groups'] = json.dumps(groups)
        tracked = verb in (
            'create', 'update', 'identity', 'update-resource', 'check-readiness', 'failover',
            'reprotect', 'finalize', 'validate-for-failover', 'validate-for-operation')
        tracked = tracked and not (verb == 'identity' and command.startswith('identity show'))
        tracked = tracked or command.startswith('recovery-job resume')
        key = command + ':' + str(self.kwargs.get('operation_id', ''))
        if tracked:
            self.ledger.action_started(key)
        self.active_command = command
        try:
            result = super()._plan(command, checks=checks)
        except Exception as error:
            self._evidence('native-command-error', {'command': command, 'nativeError': repr(error)})
            monitor = self.terminal_monitors.get(command)
            expected = self.expected_monitors.get(command)
            if tracked and monitor and expected:
                self.ledger.resolve_nonworkflow_terminal(key, monitor, expected)
            raise
        if tracked:
            try:
                output = result.get_output_in_json()
            except ValueError:
                output = None
            # Receipt of a job ID does not prove terminal state: cleanup independently
            # queries the authoritative inventory and rejects Paused/InProgress/unknown.
            if verb not in ('check-readiness', 'failover', 'reprotect') or isinstance(output, dict) and output.get('jobId'):
                self.ledger.action_resolved(key)
        return result

    def _create(self, bounded=True):
        created = super()._create(bounded=bounded)
        self.assertEqual(created['properties']['planType'], self.plan_type)
        self.assertEqual(created['identity']['type'], 'SystemAssigned')
        self.assertTrue(self.ledger.confirm_creation_from_native(created, self.kwargs['group_id']))
        return created

    def _cleanup_snapshot(self):
        shown = self._plan('show').get_output_in_json()
        self.assertEqual(shown['id'].lower(), self.plan_id.lower())
        jobs = self._plan('recovery-job list').get_output_in_json()
        return {
            'provisioningState': shown['properties']['provisioningState'], 'jobs': jobs,
            'identityPrincipal': shown['identity']['principalId'],
            'groupUniqueId': shown['properties']['recoveryGroupsSetting']['defaultGroup']['properties']['groupUniqueId'],
        }

    def _coordinated_cleanup(self):
        result = self.ledger.cleanup(
            self._cleanup_snapshot, lambda assignment: _NativeBase._delete_role(self, assignment),
            lambda: _NativeBase._delete(self))
        self._evidence('coordinated-cleanup', self.ledger.state)
        if self.successful_scenario:
            self.assertTrue(result, 'A passing scenario must complete terminal-gated cleanup.')

    def _authorize_runbooks(self, principal_id):
        self._authorize_grants(principal_id, (
            (self.automation_id, '4fe576fe-1146-4730-92eb-48519fa6bf9f'),
            (self.automation_id, 'acdd72a7-3385-48ef-bd42-f606fba81ae7'),
            (self.storage_id, 'acdd72a7-3385-48ef-bd42-f606fba81ae7'),
        ))

    def _authorize_grants(self, principal_id, grants):
        for scope, role in grants:
            self.kwargs.update(assignment_scope=scope, assignment_role=role,
                               assignment_principal=principal_id, assignment_subscription=scope.split('/')[2])
            self.active_command = 'role assignment list'
            existing = self._role_cmd(
                'az role assignment list --scope {assignment_scope} --assignee-object-id {assignment_principal} '
                '--fill-principal-name false --fill-role-definition-name false '
                '--subscription {assignment_subscription}').get_output_in_json()
            matches = [item for item in existing if item['principalId'].lower() == principal_id.lower()
                       and item['scope'].lower() == scope.lower()
                       and item['roleDefinitionId'].lower().endswith('/' + role)]
            self.assertLessEqual(len(matches), 1)
            if matches:
                self._evidence('existing-role-not-owned', {'assignment': matches[0]})
                continue
            self.kwargs['assignment_name'] = str(self.create_guid())
            assignment_id = scope + '/providers/Microsoft.Authorization/roleAssignments/' + self.kwargs['assignment_name']
            self.ledger.assignment_intent(assignment_id, principal_id, scope, role)
            self.active_command = 'role assignment create'
            try:
                response = self._role_cmd(
                    'az role assignment create --name {assignment_name} --scope {assignment_scope} '
                    '--role {assignment_role} --assignee-object-id {assignment_principal} '
                    '--assignee-principal-type ServicePrincipal --subscription {assignment_subscription}'
                ).get_output_in_json()
                self.ledger.assignment_confirmed(assignment_id, response)
                self._evidence('created-role-owned', {'assignment': response})
            except Exception:
                self.ledger.assignment_ambiguous(assignment_id)
                raise

    def _observe_job(self, response, expected_status='Completed', check_resources=True, operation=None):
        # This loop polls genuine native exact-job output, not an operation-status/REST substitute.
        self.assertIn('jobId', response)
        self.kwargs['job_name'] = response['jobId'].rsplit('/', 1)[-1]
        deadline = time.monotonic() + 300
        while True:
            job = self._plan('recovery-job show --recovery-job-name {job_name}').get_output_in_json()
            self.assertEqual(job['id'].lower(), response['jobId'].lower())
            self.assertEqual(job['properties']['operation'], operation)
            if job['properties']['status'] == expected_status:
                break
            self.assertNotIn(job['properties']['status'], OwnedScenarioLedger.TERMINAL_JOB_STATES)
            self.assertLess(time.monotonic(), deadline, 'Pending: native job exceeded 300-second observation budget.')
            time.sleep(10)
        # Reuse the existing concrete list/resource checks; the expected state is already observed.
        return super()._observe_job(response, expected_status, check_resources, operation)

    def _selected_request(self, selected, consent='Allowed'):
        """Explicit-resource scope, not fabricated source-zone coverage."""
        self.assertEqual(self.plan_type, 'Zonal')
        current = self._plan(
            'recovery-resource show --recovery-resource-name {resource_name}').get_output_in_json()
        self.assertEqual(current['id'].lower(), selected['id'].lower())
        self.assertTrue(current['id'].lower().startswith(self.plan_id.lower() + '/recoveryresources/'))
        self.assertIn('/providers/microsoft.storage/storageaccounts/', self.storage_id.lower())
        self.assertEqual(current['properties']['resourceId'].lower(), self.storage_id.lower())
        self.assertEqual(current['properties']['inclusionState'], 'Included')
        self.assertEqual(current['properties']['protectionStatus'], 'Protected')
        self.assertEqual(current['properties']['selectedProtectionSolutionType'], 'CustomRunbook')
        self.kwargs['action_request'] = json.dumps({
            # Public 2026-10-01 schema requires array presence, but permits zero
            # entries. Resource selection supplies scope without inventing a zone.
            'source-locations': [],
            'selected-resource-ids': [current['id']],
            'execution-configurations': {'user-consent': consent},
        })
        self._evidence('validated-selected-resource-request', {'planType': self.plan_type, 'nativeMember': current})
        return "--failover-direction FromSpecificLocations --failover-request-properties '{action_request}'"

    def _configure_runbook(self, failure=False, bounded=True):
        runbook = self._runbook_for_configuration(failure)
        created = self._create(bounded=bounded)
        resources, selected = self._storage()
        # Resource/AA permissions are fixture prerequisites, not a fallback response.
        # Authorize BEFORE UpdateResource can validate the selected plan identity.
        self._authorize_runbooks(created['identity']['principalId'])
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
                        'custom-runbook': {action: {'resource-id': runbook}
                                           for action in ('failover-action', 'reprotect-action')},
                    },
                })
            changes.append(change)
        self.kwargs.update(changes=json.dumps(changes), operation_id=str(self.create_guid()))
        updated = self._plan(
            "update-resource --operation-id {operation_id} --resources-to-update '{changes}'").get_output_in_json()
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
            self.assertEqual(item['properties']['inclusionState'], 'Included' if item['id'] == selected['id'] else 'Excluded')
        return created, selected

    def _configured(self, readiness=True):
        created, selected = self._configure_runbook(bounded=True)
        if readiness:
            self._readiness()
        return created, selected

    @AllowLargeResponse(size_kb=2048)
    def _scenario_update_output(self):
        created = self._create()
        self._plan('recovery-resource list')
        output = self._plan('update --plan-description "Updated native CLI recording"').get_output_in_json()
        diagnostic = self._plan('show').get_output_in_json()
        self._evidence('diagnostic-persistence-only', {'nativeShow': diagnostic})
        self.assertEqual(output['name'], self.kwargs['plan_name'])
        self.assertEqual(output['properties']['planDescription'], 'Updated native CLI recording')
        self.assertEqual(output['properties']['planType'], 'Zonal')
        self.assertEqual(output['identity']['type'], 'SystemAssigned')
        self.assertEqual(output['identity']['principalId'], created['identity']['principalId'])
        self.assertEqual(output['properties']['recoveryGroupsSetting']['defaultGroup']['properties']['groupUniqueId'],
                         self.kwargs['group_id'])
        self.successful_scenario = True

    @AllowLargeResponse(size_kb=2048)
    def _scenario_assign_output(self):
        created = self._create()
        self._plan('identity show', checks=[self.check('principalId', created['identity']['principalId'])])
        output = self._plan('identity assign --system-assigned').get_output_in_json()
        diagnostic = self._plan('show').get_output_in_json()
        self._evidence('diagnostic-persistence-only', {'nativeShow': diagnostic})
        self.assertEqual(output['type'], 'SystemAssigned')
        self.assertEqual(output['principalId'], created['identity']['principalId'])
        self.assertEqual(output['tenantId'], created['identity']['tenantId'])
        self.successful_scenario = True

    @AllowLargeResponse(size_kb=2048)
    def _scenario_validate_failover(self):
        _, selected = self._configured()
        arguments = self._selected_request(selected)
        self.kwargs['operation_id'] = str(self.create_guid())
        output = self._plan('validate-for-failover --operation-id {operation_id} ' + arguments).get_output_in_json()
        matches = [item for item in output['recoveryResourceQualifications']
                   if item['recoveryResource']['id'].lower() == selected['id'].lower()]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['operationQualificationDetails']['qualificationState'], 'Qualified')
        self.assertFalse(matches[0]['operationQualificationDetails'].get('notQualifiedReasons'))
        self.successful_scenario = True

    @AllowLargeResponse(size_kb=2048)
    def _scenario_failover(self):
        _, selected = self._configured()
        arguments = self._selected_request(selected)
        self.kwargs['operation_id'] = str(self.create_guid())
        output = self._plan('failover --operation-id {operation_id} ' + arguments).get_output_in_json()
        self._observe_job(output, operation='Failover')
        self.successful_scenario = True

    @AllowLargeResponse(size_kb=2048)
    def _scenario_resume(self):
        _, selected = self._configured()
        arguments = self._selected_request(selected, consent='Unspecified')
        self.kwargs['operation_id'] = str(self.create_guid())
        output = self._plan('failover --operation-id {operation_id} ' + arguments).get_output_in_json()
        self._observe_job(output, expected_status='Paused', check_resources=False, operation='Failover')
        self.kwargs['operation_id'] = str(self.create_guid())
        before = len(self.cassette.requests) + self.cassette.play_count
        resumed = self._plan(
            'recovery-job resume --recovery-job-name {job_name} --operation-id {operation_id} '
            '--description "Native resume of explicit manual pause"').get_output_in_json()
        self.assertNotIn('error', resumed)
        self.assertGreater(len(self.cassette.requests) + self.cassette.play_count, before)
        self._observe_job(output, operation='Failover')
        self.successful_scenario = True

    @AllowLargeResponse(size_kb=2048)
    def _scenario_finalize(self):
        # Native evidence proved newly discovered members require explicit decisions,
        # and Included resources require a valid protection solution. Use the known
        # CustomRunbook resource configuration with least-scope permissions, but NEVER
        # require completed Readiness or Failover before independently invoking Finalize.
        created, selected = self._configure_runbook(bounded=True)
        self._evidence('independent-finalize-configured-member', {'nativeResource': selected})
        before = self._plan('show').get_output_in_json()
        self.assertEqual(before['id'].lower(), self.plan_id.lower())
        self.assertEqual(before['properties']['planState'], 'Warning',
                         'Finalize needs a real Warning-to-Ready fixture, not an already-Ready no-op.')
        self.assertEqual(before['properties']['provisioningState'], 'Succeeded')
        self.assertEqual(before['identity']['principalId'], created['identity']['principalId'])
        self.kwargs['operation_id'] = str(self.create_guid())
        finalized = self._plan('finalize --operation-id {operation_id}')
        self.assertEqual(finalized.exit_code, 0)
        output = finalized.get_output_in_json() if finalized.output.strip() else None
        self.assertIn(output, (None, {}), 'Finalize success is an error-free ErrorResponse or void, not a plan.')
        self._evidence('native-finalize-contract-output', {'nativeOutput': output})
        self.kwargs['finalize_principal'] = created['identity']['principalId']
        # Wait's own native predicate proves completion; never relabel GET output as
        # the Finalize response. A successful native wait intentionally emits nothing.
        waited = self._plan(
            'wait --custom "properties.planState == \'Ready\' && properties.provisioningState == \'Succeeded\' '
            '&& properties.planType == \'Zonal\' && identity.principalId == \'{finalize_principal}\'" '
            '--interval 5 --timeout 300')
        self.assertEqual(waited.exit_code, 0)
        self.assertEqual(waited.output.strip(), '', 'A timeout/error result is not successful native wait completion.')
        self._evidence('native-finalize-completion', {
            'fromPlanState': 'Warning', 'toPlanState': 'Ready', 'nativeWaitExitCode': waited.exit_code,
        })
        self.successful_scenario = True
