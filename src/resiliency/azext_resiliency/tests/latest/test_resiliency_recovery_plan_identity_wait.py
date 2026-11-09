"""Native identity Wait completion predicate on an exact owned SystemAssigned plan."""
from azure.cli.testsdk.scenario_tests.decorators import AllowLargeResponse

from .recovery_plan_safe import ResiliencySafeRecoveryPlanScenario as _SafeBase


class ResiliencyIdentityWaitScenario(_SafeBase):
    @AllowLargeResponse(size_kb=2048)
    def test_resiliency_recovery_plan_native_identity_wait(self):
        created = self._create()
        self.kwargs['expected_principal'] = created['identity']['principalId']
        self.kwargs['expected_tenant'] = created['identity']['tenantId']
        before = len(self.cassette.requests) + self.cassette.play_count
        self._plan(
            'identity wait --interval 5 --timeout 120 --custom '
            '"identity.type==\'SystemAssigned\' && identity.principalId==\'{expected_principal}\' '
            '&& identity.tenantId==\'{expected_tenant}\'"')
        self.assertGreater(len(self.cassette.requests) + self.cassette.play_count, before)
        self._plan('identity show', checks=[
            self.check('type', 'SystemAssigned'),
            self.check('principalId', '{expected_principal}'),
            self.check('tenantId', '{expected_tenant}'),
        ])
        self._plan('show', checks=[
            self.check('id', created['id']),
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('properties.planType', 'Zonal'),
            self.check('properties.recoveryGroupsSetting.defaultGroup.properties.groupUniqueId', '{group_id}'),
        ])
        self.successful_scenario = True
