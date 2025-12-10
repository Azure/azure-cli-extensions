# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# Dedicated tests for dynatrace monitored-subscription command group
# --------------------------------------------------------------------------------------------

import unittest
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer  # noqa
from azure.cli.testsdk.scenario_tests.decorators import AllowLargeResponse  # noqa

class DynatraceMonitoredSubscriptionScenario(ScenarioTest):
    """Isolated lifecycle coverage for dynatrace monitored-subscription commands without error suppression."""

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_dt_monitoredsub', location='eastus2euap')
    def test_monitored_subscription_commands(self, resource_group):
        # Arrange
        self.kwargs.update({
            'monitor': self.create_random_name('monitor', 15),
            'subscription_id': '/SUBSCRIPTIONS/b16e4b4e-2ed8-4f32-bac1-0e3eb56bef5c',  # normalized variable name
            'subs_id': '/subscriptions/b16e4b4e-2ed8-4f32-bac1-0e3eb56bef5c',
            'updated_status': 'InProgress'
        })

        # Create monitor starting
        self.cmd('dynatrace monitor create -g {rg} -n {monitor} --user-info {{first-name:Alice,last-name:Bobab,email-address:arushiarora@microsoft.com,phone-number:1234567890,country:US}} --plan-data {{usage-type:COMMITTED,billing-cycle:MONTHLY,plan-details:azureportalintegration_privatepreview@TIDgmz7xq9ge3py,effective-date:2024-10-10}} --environment {{single-sign-on:{{aad-domains:[\'abc\']}}}}')
        self.cmd('dynatrace monitor wait -g {rg} -n {monitor} --created')

        # Create monitored subscription (default resource) - build JSON list via preformatted string to prevent kwargs KeyError
        self.cmd('dynatrace monitor monitored-subscription create --resource-group {rg} --monitor-name {monitor} --monitored-sub-list "[{{\\"subscription-id\\":\\"{subscription_id}\\",\\"status\\":\\"Active\\"}}]" ', checks=[
            self.check('name', 'default'),
            self.check('properties.monitoredSubscriptionList[0].status', 'Active'),
            self.check('properties.provisioningState', 'Succeeded')
        ])

        # List monitored subscriptions
        self.cmd('dynatrace monitor monitored-subscription list --resource-group {rg} --monitor-name {monitor}', checks=[
            self.check('[0].name', 'default')
        ])

        # Show monitored subscription
        self.cmd('dynatrace monitor monitored-subscription show --resource-group {rg} --monitor-name {monitor}', checks=[
            self.check('name', 'default'),
            self.exists('properties.monitoredSubscriptionList[0].tagRules.provisioningState'),
            self.check('properties.monitoredSubscriptionList[0].status', 'Active')
        ])

        # Delete monitored subscription (async allowed)
        self.cmd('dynatrace monitor monitored-subscription delete --resource-group {rg} --monitor-name {monitor} --yes --no-wait')

        # Cleanup monitor
        self.cmd('dynatrace monitor delete -g {rg} -n {monitor} -y')

if __name__ == '__main__':
    unittest.main()
