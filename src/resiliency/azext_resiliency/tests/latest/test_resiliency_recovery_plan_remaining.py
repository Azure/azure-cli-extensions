"""Previously recorded recovery commands omitted from the initial test delivery."""
import json
import time

from azure.cli.testsdk.scenario_tests.decorators import AllowLargeResponse

from .recovery_plan_native import ResiliencyNativeRecoveryPlanScenario as _NativeBase


class ResiliencyRemainingRecoveryPlanScenario(_NativeBase):
    def test_resiliency_recovery_plan_native_identity_remove(self):
        self._create()
        self._plan('identity remove --system-assigned', checks=[
            self.check('type', 'None'), self.check('principalId', None), self.check('tenantId', None),
        ])
        self._plan('identity show', checks=[
            self.check('type', 'None'), self.check('principalId', None), self.check('tenantId', None),
        ])
        self._plan('show', checks=[
            self.check('identity.type', 'None'),
            self.check('identity.principalId', None),
            self.check('properties.planType', 'Zonal'),
            self.check('properties.recoveryGroupsSetting.defaultGroup.properties.groupUniqueId', '{group_id}'),
        ])

    def test_resiliency_recovery_plan_native_validate_for_operation(self):
        created, _ = self._configure_runbook(bounded=True)
        self._authorize_runbooks(created['identity']['principalId'])
        self._readiness()
        self.kwargs['operation_id'] = str(self.create_guid())
        before = len(self.cassette.requests) + self.cassette.play_count
        response = self._plan(
            'validate-for-operation --operation-id {operation_id} --operation-name Failover'
        ).get_output_in_json()
        self.assertEqual(response, {})
        self.assertGreater(len(self.cassette.requests) + self.cassette.play_count, before)
        self._plan('show', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('properties.planType', 'Zonal'),
            self.check('properties.recoveryGroupsSetting.defaultGroup.properties.groupUniqueId', '{group_id}'),
            self.check('identity.principalId', created['identity']['principalId']),
        ])

    @AllowLargeResponse(size_kb=2048)
    def test_resiliency_recovery_plan_native_runbook_validate_reprotect(self):
        created, selected = self._configure_runbook(bounded=True)
        self._authorize_runbooks(created['identity']['principalId'])
        self._readiness()
        self._qualify('Reprotect', selected)

    @AllowLargeResponse(size_kb=2048)
    def test_resiliency_recovery_plan_native_runbook_reprotect(self):
        created, selected = self._configure_runbook(bounded=True)
        self._authorize_runbooks(created['identity']['principalId'])
        self._readiness()
        arguments = self._action_arguments('Reprotect', selected)
        self.kwargs['operation_id'] = str(self.create_guid())
        response = self._plan('reprotect --operation-id {operation_id} ' + arguments).get_output_in_json()
        self._observe_job(response, operation='Reprotect')

    @AllowLargeResponse(size_kb=2048)
    def test_resiliency_recovery_plan_native_runbook_retry(self):
        created, selected = self._configure_runbook(failure=True, bounded=True)
        self._authorize_runbooks(created['identity']['principalId'])
        self._readiness()
        arguments = self._action_arguments('Reprotect', selected)
        self.kwargs['operation_id'] = str(self.create_guid())
        original_action = self._plan(
            'reprotect --operation-id {operation_id} ' + arguments).get_output_in_json()
        failed = self._observe_job(original_action, expected_status='Failed', operation='Reprotect')
        self.assertNotIn('authorizationfailed', json.dumps(failed).lower())
        previous_attempts = len(failed['properties'].get('retryDetails', []))
        previous_number = max(
            (item['retryAttempt'] for item in failed['properties'].get('retryDetails', [])), default=0)
        self.kwargs['operation_id'] = str(self.create_guid())
        before_retry = len(self.cassette.requests) + self.cassette.play_count
        retried = self._plan(
            'recovery-job retry --recovery-job-name {job_name} --operation-id {operation_id}'
        ).get_output_in_json()
        self.assertNotIn('error', retried)
        self.assertNotIn('jobId', retried)
        self.assertGreater(len(self.cassette.requests) + self.cassette.play_count, before_retry)
        deadline = time.time() + 300
        while True:
            current = self._plan('recovery-job show --recovery-job-name {job_name}').get_output_in_json()
            details = current['properties'].get('retryDetails', [])
            if len(details) > previous_attempts and details[-1].get('status') == 'Failed':
                break
            self.assertLess(time.time(), deadline, 'Native Retry did not create an attempt on the exact job.')
            time.sleep(15)
        failed_again = self._observe_job(original_action, expected_status='Failed', operation='Reprotect')
        self.assertGreater(len(failed_again['properties']['retryDetails']), previous_attempts)
        latest = failed_again['properties']['retryDetails'][-1]
        self.assertEqual(latest['retryAttempt'], previous_number + 1)
        self.assertEqual(latest['status'], 'Failed')
