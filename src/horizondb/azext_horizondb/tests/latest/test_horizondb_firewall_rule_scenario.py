# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (
    JMESPathCheck,
    ResourceGroupPreparer,
    ScenarioTest,
    live_only)
from .constants import DEFAULT_LOCATION, CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH, PASSWORD_PREFIX


# These scenario tests exercise the live control plane end-to-end. They are marked live-only because
# firewall-rule provisioning is not yet captured in a committed recording; run with `--live` to
# generate a cassette.
class HorizonDBFirewallRuleScenarioTest(ScenarioTest):

    location = DEFAULT_LOCATION

    @live_only()
    @AllowLargeResponse()
    @ResourceGroupPreparer(location=location)
    def test_horizondb_firewall_rule_mgmt(self, resource_group):
        cluster_name = self.create_random_name(CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH)
        admin_user = 'horizonadmin'
        admin_password = self.create_random_name(PASSWORD_PREFIX, 20)

        self.kwargs.update({
            'rg': resource_group,
            'cluster': cluster_name,
            'location': self.location,
            'admin_user': admin_user,
            'admin_password': admin_password,
            'rule': 'allowrange',
        })

        # Create a cluster and open public access to a single IP; this should auto-create a rule.
        self.cmd('horizondb create -g {rg} -n {cluster} --location {location} '
                 '--administrator-login {admin_user} --administrator-login-password {admin_password} '
                 '--version 17 --v-cores 4 --public-access 12.12.12.12 --yes',
                 checks=[JMESPathCheck('name', cluster_name)])

        # The auto-created rule should be present on the default pool.
        self.cmd('horizondb firewall-rule list -g {rg} --cluster-name {cluster}',
                 checks=[JMESPathCheck("length([?properties.startIpAddress=='12.12.12.12'])", 1)])

        # Create an explicit range rule.
        self.cmd('horizondb firewall-rule create -g {rg} --cluster-name {cluster} --name {rule} '
                 '--start-ip-address 10.0.0.0 --end-ip-address 10.0.0.255',
                 checks=[
                     JMESPathCheck('name', 'allowrange'),
                     JMESPathCheck('properties.startIpAddress', '10.0.0.0'),
                     JMESPathCheck('properties.endIpAddress', '10.0.0.255'),
                 ])

        # Show the rule.
        self.cmd('horizondb firewall-rule show -g {rg} --cluster-name {cluster} --name {rule}',
                 checks=[JMESPathCheck('name', 'allowrange')])

        # Update the rule's end IP.
        self.cmd('horizondb firewall-rule update -g {rg} --cluster-name {cluster} --name {rule} '
                 '--end-ip-address 10.0.0.128',
                 checks=[JMESPathCheck('properties.endIpAddress', '10.0.0.128')])

        # Delete the rule.
        self.cmd('horizondb firewall-rule delete -g {rg} --cluster-name {cluster} --name {rule} --yes')

        # Clean up the cluster.
        self.cmd('horizondb delete -g {rg} -n {cluster} --yes')
