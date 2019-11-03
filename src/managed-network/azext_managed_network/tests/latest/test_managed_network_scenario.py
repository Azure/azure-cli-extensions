# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ManagedNetworkScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_managed_network')
    def test_managed_network(self, resource_group):

        self.kwargs.update({
            'name': 'test1'
        })

        self.cmd('az managed-network create '
                 '--resource-group {rg} '
                 '--name "MyManagedNetwork" '
                 '--location westus',
                 checks=[])

        self.cmd('az managed-network group create '
                 '--resource-group {rg} '
                 '--managed-network-name "MyManagedNetwork" '
                 '--name "MyManagedNetworkGroup"',
                  checks=[])

        self.cmd('az managed-network scope-assignment create '
                 '--scope "subscriptions/{sub}" '
                 '--name "MyScopeAssignment"',
                 checks=[])

        self.cmd('az managed-network peering-policy create '
                 '--resource-group {rg} '
                 '--managed-network-name "MyManagedNetwork" '
                 '--name "MyHubAndSpoke"',
                 checks=[])

        # EXAMPLE NOT FOUND: ManagedNetworksGet
        # EXAMPLE NOT FOUND: ManagedNetworksListByResourceGroup
        # EXAMPLE NOT FOUND: ManagedNetworksListBySubscription
        # EXAMPLE NOT FOUND: ScopeAssignmentsGet
        # EXAMPLE NOT FOUND: ScopeAssignmentsList
        # EXAMPLE NOT FOUND: ManagementNetworkGroupsGet
        # EXAMPLE NOT FOUND: ManagedNetworksGroupsListByManagedNetwork
        # EXAMPLE NOT FOUND: ManagedNetworkPeeringPoliciesGet
        # EXAMPLE NOT FOUND: ManagedNetworkPeeringPoliciesListByManagedNetwork
        self.cmd('az managed-network peering-policy delete '
                 '--resource-group {rg} '
                 '--managed-network-name "MyManagedNetwork" '
                 '--name "myHubAndSpoke"',
                 checks=[])

        self.cmd('az managed-network scope-assignment delete '
                 '--scope "subscriptions/{sub}" '
                 '--name "MyScopeAssignment"',
                 checks=[])

        self.cmd('az managed-network group delete '
                 '--resource-group {rg} '
                 '--managed-network-name "MyManagedNetwork" '
                 '--name "MyManagedNetworkGroup"',
                 checks=[])

        self.cmd('az managed-network delete '
                 '--resource-group {rg} '
                 '--name "MyManagedNetwork"',
                 checks=[])
