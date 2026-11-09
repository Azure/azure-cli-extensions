"""One native Resume; the method's _resume suffix selects the existing manual fixture."""
import contextlib
import io
from unittest.mock import patch

from azure.cli.testsdk.scenario_tests.decorators import AllowLargeResponse

from .recovery_plan_owned import (
    ResiliencyFailoverOnly20261108Scenario as _OwnedBase)


class ResiliencyResumeOnly20261109Scenario(_OwnedBase):
    def _assert_manual_fixture(self, created):
        group = created['properties']['recoveryGroupsSetting']['defaultGroup']['properties']
        self.assertEqual(group['groupUniqueId'], self.kwargs['group_id'])
        self.assertEqual(len(group['preActions']), 1)
        action = group['preActions'][0]
        self.assertEqual(action['type'], 'ManualAction')
        self.assertEqual(action['name'], self.kwargs['manual_action_name'])
        self.assertEqual(action['timeoutInMinutes'], 10)

    def _create(self, bounded=True):
        created = super()._create(bounded=bounded)
        self._assert_manual_fixture(created)
        self._evidence('native-resume-manual-fixture', {'nativePlan': created})
        return created

    @AllowLargeResponse(size_kb=2048)
    def test_resiliency_recovery_plan_native_only_record_20261109_resume(self):
        original_invoke = self.cli_ctx.invoke

        def capture_invoke(arguments, *args, **kwargs):
            if arguments[:4] != ['resiliency', 'recovery-plan', 'recovery-job', 'resume']:
                return original_invoke(arguments, *args, **kwargs)
            stderr = io.StringIO()
            code, error = None, None
            try:
                with contextlib.redirect_stderr(stderr):
                    code = original_invoke(arguments, *args, **kwargs)
                return code
            except Exception as caught:
                error = repr(caught)
                raise
            finally:
                stream = kwargs.get('out_file')
                self._evidence('exact-native-resume-invocation', {
                    'arguments': arguments, 'nativeExitCode': code, 'raisedError': error,
                    'nativeStdout': stream.getvalue() if stream is not None else None,
                    'nativeStderr': stderr.getvalue(),
                })

        with patch.object(self.cli_ctx, 'invoke', side_effect=capture_invoke):
            _, selected = self._configured()
            arguments = self._selected_request(selected, consent='Unspecified')
            self.kwargs['operation_id'] = str(self.create_guid())
            seed = self._plan('failover --operation-id {operation_id} ' + arguments).get_output_in_json()
            self.assertTrue(seed['jobId'].lower().startswith(self.plan_id.lower() + '/recoveryjobs/'))
            paused = self._observe_job(seed, expected_status='Paused', check_resources=False, operation='Failover')
            self.assertEqual(paused['id'].lower(), seed['jobId'].lower())
            self.assertEqual(paused['name'], self.kwargs['job_name'])
            self.assertEqual(paused['properties']['operation'], 'Failover')
            self.assertEqual(paused['properties']['status'], 'Paused')
            self._evidence('native-resume-paused-before', {'nativeJob': paused})
            self.kwargs['operation_id'] = str(self.create_guid())
            self.kwargs['resume_description'] = 'Native resume of explicit manual pause'
            resumed = self._plan(
                'recovery-job resume --recovery-job-name {job_name} --operation-id {operation_id} '
                '--description "{resume_description}"')
            self.assertEqual(resumed.exit_code, 0)
            output = resumed.get_output_in_json() if resumed.output.strip() else None
            self.assertIn(output, (None, {}), 'Resume success is error-free ErrorResponse or void, not job readback.')
            self._evidence('native-resume-contract-output', {
                'nativeExitCode': resumed.exit_code, 'nativeOutput': output})
            # Job Show proves the outcome only; it never substitutes for Resume's own response.
            completed = self._observe_job(seed, operation='Failover')
            self.assertEqual(completed['id'].lower(), paused['id'].lower())
            self.assertEqual(completed['properties']['operation'], 'Failover')
            self.assertEqual(completed['properties']['status'], 'Completed')
            self._evidence('native-resume-completed-after', {'nativeJob': completed})
            self.successful_scenario = True
