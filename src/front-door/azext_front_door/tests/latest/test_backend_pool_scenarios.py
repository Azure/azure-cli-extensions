# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from knack.util import CLIError


class BackendPoolScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(location='westus', additional_tags={'owner': 'jingnanxu'})
    def test_backend_pool_basic(self, resource_group):
        self.kwargs.update({
            'front_door': self.create_random_name('clifrontdoor', 20),
            'bkp1': 'bkp1',
            'lb1': 'lb1',
            'pb1': 'pb1'
        })
        self.cmd('network front-door create -g {rg} -n {front_door} --backend-address 202.120.2.3')

        self.cmd('network front-door backend-pool create -f {front_door} -g {rg} -n {bkp1} '
                 '--address 202.120.2.3 '
                 '--load-balancing DefaultLoadBalancingSettings '
                 '--probe DefaultProbeSettings ',
                 checks=[
                     self.check('backends[0].address', '202.120.2.3'),
                     self.check('ends_with(loadBalancingSettings.id, `DefaultLoadBalancingSettings`)', True),
                     self.check('ends_with(healthProbeSettings.id, `DefaultProbeSettings`)', True)
                 ])

        self.cmd('network front-door backend-pool list -f {front_door} -g {rg} ',
                 checks=[
                     self.check('length(@)', 2),
                 ])
        self.cmd('network front-door backend-pool show -f {front_door} -g {rg} -n {bkp1} ')
        self.cmd('network front-door backend-pool delete -f {front_door} -g {rg} -n {bkp1} ')
        self.cmd('network front-door backend-pool list -f {front_door} -g {rg} ',
                 checks=[
                     self.check('length(@)', 1),
                 ])

    @ResourceGroupPreparer(location='westus', additional_tags={'owner': 'jingnanxu'})
    def test_backend_pool_backend(self, resource_group):
        self.kwargs.update({
            'front_door': self.create_random_name('clifrontdoor', 20),
            'bkp1': 'bkp1',
            'lb1': 'lb1',
            'pb1': 'pb1'
        })
        self.cmd('network front-door create -g {rg} -n {front_door} --backend-address 202.120.2.3')

        self.cmd('network front-door backend-pool create -f {front_door} -g {rg} -n {bkp1} '
                 '--address 202.120.2.3 '
                 '--load-balancing DefaultLoadBalancingSettings '
                 '--probe DefaultProbeSettings ',
                 checks=[
                     self.check('backends[0].address', '202.120.2.3'),
                     self.check('ends_with(loadBalancingSettings.id, `DefaultLoadBalancingSettings`)', True),
                     self.check('ends_with(healthProbeSettings.id, `DefaultProbeSettings`)', True)
                 ])

        # Fix Issue: https://github.com/Azure/azure-cli/issues/17269
        self.cmd('network front-door backend-pool backend add '
                 '--resource-group {rg} '
                 '--front-door-name {front_door} '
                 '--pool-name {bkp1} '
                 '--address 202.120.2.3 '
                 '--backend-host-header "" '
                 '--disabled true '
                 '--http-port 80 '
                 '--https-port 443 '
                 '--priority 2 '
                 '--weight 1 ',
                 checks=[
                     self.check('backendHostHeader', '')
                 ])

        # Fix Iussue: https://github.com/Azure/azure-cli/issues/17270
        self.cmd('network front-door backend-pool backend update '
                 '--resource-group {rg} '
                 '--front-door-name {front_door} '
                 '--pool-name {bkp1} '
                 '--index 2 '
                 '--disabled false ',
                 checks=[
                     self.check('enabledState', 'Enabled'),
                     self.check('backendHostHeader', '')
                 ])

        with self.assertRaises(CLIError):
            self.cmd('network front-door backend-pool backend update '
                    '--resource-group {rg} '
                    '--front-door-name {front_door} '
                    '--pool-name {bkp1} '
                    '--index 3 '
                    '--disabled false ')
