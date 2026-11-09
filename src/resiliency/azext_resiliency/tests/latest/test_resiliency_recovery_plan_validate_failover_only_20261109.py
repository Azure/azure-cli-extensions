# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""One native Failover qualification; Readiness is only a setup prerequisite."""
import contextlib
import io
from unittest.mock import patch

from azure.cli.testsdk.scenario_tests.decorators import AllowLargeResponse

from .recovery_plan_owned import (
    ResiliencyFailoverOnly20261108Scenario as _OwnedBase)
from .recovery_plan_safe import ResiliencySafeRecoveryPlanScenario as _SafeBase


class ResiliencyValidateFailoverOnly20261109Scenario(_OwnedBase):
    @AllowLargeResponse(size_kb=2048)
    def test_resiliency_recovery_plan_native_validate_failover_only_record_20261109(self):
        original_invoke = self.cli_ctx.invoke

        def capture_invoke(arguments, *args, **kwargs):
            if arguments[:3] != ['resiliency', 'recovery-plan', 'validate-for-failover']:
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
                self._evidence('exact-native-validate-failover-invocation', {
                    'arguments': arguments, 'nativeExitCode': code, 'raisedError': error,
                    'nativeStdout': stream.getvalue() if stream is not None else None,
                    'nativeStderr': stderr.getvalue(),
                })

        with patch.object(self.cli_ctx, 'invoke', side_effect=capture_invoke):
            _SafeBase._scenario_validate_failover(self)
