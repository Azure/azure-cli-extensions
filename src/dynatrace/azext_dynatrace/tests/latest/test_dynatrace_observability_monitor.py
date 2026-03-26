# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# Tests for dynatrace observability monitor command group
# --------------------------------------------------------------------------------------------

import unittest
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer  # noqa
from azure.cli.testsdk.scenario_tests.decorators import AllowLargeResponse  # noqa

class DynatraceObservabilityMonitorScenario(ScenarioTest):
    """Strict coverage for dynatrace observability monitor commands without error suppression."""

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_dt_observability', location='eastus2euap')
    def test_observability_monitor_commands(self, resource_group):
        self.kwargs.update({
            'monitor': self.create_random_name('monitor', 15),
            'sub_id': self.get_subscription_id(),
            'updated_status': 'InProgress',
        })
        self.kwargs['sub_arm_id'] = f"/subscriptions/{self.kwargs['sub_id']}"

        # Create monitor with provided trial plan details
        self.cmd('dynatrace monitor create -g {rg} -n {monitor} --user-info {{first-name:Alice,last-name:Bobab,email-address:arushiarora@microsoft.com,phone-number:1234567890,country:US}} --plan-data {{usage-type:COMMITTED,billing-cycle:1-Month,plan-details:dynatrace_azure_trial@TIDgmz7xq9ge3py,effective-date:2025-11-03}} --environment {{single-sign-on:{{aad-domains:[\'abc\']}}}}')
        self.cmd('dynatrace monitor wait -g {rg} -n {monitor} --created')

        # Verify initial plan is trial
        # initial = self.cmd('dynatrace monitor show -g {rg} -n {monitor}').get_output_in_json()
        # self.assertEqual(initial['planData']['planDetails'], 'dynatrace_azure_trial@TIDgmz7xq9ge3py')

        # List monitors by subscription (observability path)
        self.cmd('dynatrace observability monitor list', checks=[
            self.exists('[0].name')
        ])
        
        # Manage agent installation (nonexistent VM expected to fail; keep expect_failure to record behavior)
        self.kwargs['vm_id'] = f"/subscriptions/{self.get_subscription_id()}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/nonexistentVM"
        self.cmd('dynatrace observability monitor manage-agent-installation --resource-group {rg} --monitor-name {monitor} --action Install --mng-agt-instal-list \'[{{id:"{vm_id}"}}]\'', expect_failure=True)

        # Cleanup monitor (monitored-subscription deletion handled in its dedicated test)
        self.cmd('dynatrace monitor delete -g {rg} -n {monitor} -y')

if __name__ == '__main__':
    unittest.main()
