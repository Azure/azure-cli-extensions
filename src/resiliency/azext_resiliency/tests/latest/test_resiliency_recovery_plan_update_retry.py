"""One latest-source metadata Update retry; diagnostics never replace its output."""

import contextlib
import io
from unittest.mock import patch

from azure.cli.testsdk.scenario_tests.decorators import AllowLargeResponse

from .recovery_plan_safe import ResiliencySafeRecoveryPlanScenario


class ResiliencyRecoveryPlanUpdateRetryScenario(ResiliencySafeRecoveryPlanScenario):
    @AllowLargeResponse(size_kb=2048)
    def test_resiliency_recovery_plan_update_retry_latest_description(self):
        created = self._create()
        self.assertEqual(created['id'].lower(), self.plan_id.lower())
        self.assertEqual(created['properties']['planDescription'], 'Native CLI recording')
        self.kwargs['update_description'] = 'Metadata Update retry ' + self.kwargs['plan_name']
        baseline = self._plan('show').get_output_in_json()
        self.assertEqual(baseline['id'].lower(), self.plan_id.lower())
        self.assertEqual(baseline['properties']['planDescription'], 'Native CLI recording')
        self.assertNotEqual(baseline['properties']['planDescription'], self.kwargs['update_description'])
        self._evidence('native-baseline-before-single-update', {
            'baselineDescription': baseline['properties']['planDescription'],
            'requestedDescription': self.kwargs['update_description'], 'nativeBaseline': baseline,
        })
        original_invoke = self.cli_ctx.invoke

        def capture_invoke(arguments, *args, **kwargs):
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
                self._evidence('exact-native-update-invocation', {
                    'arguments': arguments, 'nativeExitCode': code, 'raisedError': error,
                    'nativeStdout': stream.getvalue() if stream is not None else None,
                    'nativeStderr': stderr.getvalue(),
                })

        try:
            with patch.object(self.cli_ctx, 'invoke', side_effect=capture_invoke):
                output = self._plan(
                    'update --plan-description "{update_description}"').get_output_in_json()
        except Exception as original_error:
            # One independently bounded native Show is diagnostic only. The original
            # Update exception is always re-raised, so this cannot turn failure into PASS.
            try:
                diagnostic = self._plan('show').get_output_in_json()
                self._evidence('update-failure-native-readback-diagnostic-only', {
                    'nativeShow': diagnostic, 'updateError': repr(original_error),
                    'baselineDescription': baseline['properties']['planDescription'],
                    'requestedDescription': self.kwargs['update_description'],
                    'matchesRequestedDescription': diagnostic['properties']['planDescription']
                    == self.kwargs['update_description'],
                })
            except Exception as diagnostic_error:
                self._evidence('update-failure-native-readback-error', {
                    'updateError': repr(original_error), 'diagnosticError': repr(diagnostic_error),
                })
            raise
        self.assertEqual(output['name'], self.kwargs['plan_name'])
        self.assertEqual(output['id'].lower(), self.plan_id.lower())
        self.assertEqual(output['properties']['planDescription'], self.kwargs['update_description'])
        self.assertEqual(output['properties']['planType'], 'Zonal')
        self.assertEqual(output['identity']['type'], 'SystemAssigned')
        self.assertEqual(output['identity']['principalId'], created['identity']['principalId'])
        self.assertEqual(output['properties']['recoveryGroupsSetting']['defaultGroup']['properties']['groupUniqueId'],
                         self.kwargs['group_id'])
        self.successful_scenario = True
