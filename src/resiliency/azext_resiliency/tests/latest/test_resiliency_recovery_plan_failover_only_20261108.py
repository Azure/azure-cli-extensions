"""One native Failover scenario using shared terminal-gated ownership helpers."""

from azure.cli.testsdk.scenario_tests.decorators import AllowLargeResponse

from . import recovery_plan_safe as _safe_module
from .recovery_plan_owned import ResiliencyFailoverOnly20261108Scenario as _OwnedBase


class ResiliencyFailoverOnly20261108Scenario(_OwnedBase):
    @AllowLargeResponse(size_kb=2048)
    def test_resiliency_recovery_plan_native_failover_only_record_20261108(self):
        _safe_module.ResiliencySafeRecoveryPlanScenario._scenario_failover(self)
