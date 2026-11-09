"""Native Finalize revalidation of a configured Ready plan; no fabricated state transition."""
import contextlib
import io
from unittest.mock import patch

from azure.cli.testsdk.scenario_tests.decorators import AllowLargeResponse

from .recovery_plan_owned import (
    ResiliencyFailoverOnly20261108Scenario as _OwnedBase)


class ResiliencyFinalizeReadyV2Scenario(_OwnedBase):
    def _assert_same_ready_plan(self, plan, principal):
        self.assertEqual(plan['id'].lower(), self.plan_id.lower())
        self.assertEqual(plan['properties']['planState'], 'Ready')
        self.assertEqual(plan['properties']['provisioningState'], 'Succeeded')
        self.assertEqual(plan['properties']['planType'], 'Zonal')
        self.assertEqual(plan['identity']['type'], 'SystemAssigned')
        self.assertEqual(plan['identity']['principalId'], principal)
        group = plan['properties']['recoveryGroupsSetting']['defaultGroup']['properties']
        self.assertEqual(group['groupUniqueId'], self.kwargs['group_id'])

    @AllowLargeResponse(size_kb=2048)
    def test_resiliency_recovery_plan_native_finalize_ready_record_20261109_v2(self):
        original_invoke = self.cli_ctx.invoke

        def capture_invoke(arguments, *args, **kwargs):
            if arguments[:3] == ['resiliency', 'recovery-plan', 'finalize']:
                label = 'exact-native-finalize-invocation'
            elif arguments[:3] == ['resiliency', 'recovery-plan', 'wait'] and '--custom' in arguments:
                label = 'exact-native-finalize-wait-invocation'
            else:
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
                self._evidence(label, {
                    'arguments': arguments, 'nativeExitCode': code, 'raisedError': error,
                    'nativeStdout': stream.getvalue() if stream is not None else None,
                    'nativeStderr': stderr.getvalue(),
                })

        with patch.object(self.cli_ctx, 'invoke', side_effect=capture_invoke):
            created, selected = self._configure_runbook(bounded=True)
            principal = created['identity']['principalId']
            before = self._plan('show').get_output_in_json()
            self._assert_same_ready_plan(before, principal)
            self._evidence('native-finalize-revalidation-before', {
                'nativePlan': before, 'selectedNativeResource': selected})
            self.kwargs['operation_id'] = str(self.create_guid())
            finalized = self._plan('finalize --operation-id {operation_id}')
            self.assertEqual(finalized.exit_code, 0)
            output = finalized.get_output_in_json() if finalized.output.strip() else None
            self.assertIn(output, (None, {}), 'Finalize response must not be replaced with a Ready plan.')
            self._evidence('native-finalize-contract-output', {'nativeOutput': output})
            self.kwargs['finalize_principal'] = principal
            waited = self._plan(
                'wait --custom "properties.planState == \'Ready\' && properties.provisioningState == \'Succeeded\' '
                '&& identity.principalId == \'{finalize_principal}\'" '
                '--interval 5 --timeout 300')
            self.assertEqual(waited.exit_code, 0)
            self.assertEqual(waited.output.strip(), '')
            after = self._plan('show').get_output_in_json()
            self._assert_same_ready_plan(after, principal)
            self._evidence('native-finalize-revalidation-after', {
                'nativePlan': after, 'nativeWaitExitCode': waited.exit_code,
                'coverage': 'Ready-state revalidation, not Warning-to-Ready transition.'})
            self.successful_scenario = True
