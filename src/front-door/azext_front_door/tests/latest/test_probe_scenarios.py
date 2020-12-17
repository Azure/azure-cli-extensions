# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class ProbeScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(location='westus')
    def test_probe_basic(self, resource_group):
        self.kwargs.update({
            'front_door': self.create_random_name('clifrontdoor', 20),
            'pb1': 'pb1'
        })
        self.cmd('network front-door create -g {rg} -n {front_door} --backend-address 202.120.2.3')
        self.cmd('network front-door probe create -f {front_door} -g {rg} -n {pb1} '
                 '--interval 100 '
                 '--path /abc '
                 '--enabled Disabled '
                 '--probeMethod GET '
                 '--protocol Http ',
                 checks=[
                     self.check('intervalInSeconds', 100),
                     self.check('path', '/abc'),
                     self.check('enabledState', 'Disabled'),
                     self.check('protocol', 'Http'),
                     self.check('healthProbeMethod', 'Get'),
                 ])
        self.cmd('network front-door probe update -f {front_door} -g {rg} -n {pb1} '
                 '--interval 10 '
                 '--path / '
                 '--enabled Enabled '
                 '--probeMethod HEAD '
                 '--protocol Https ',
                 checks=[
                     self.check('intervalInSeconds', 10),
                     self.check('path', '/'),
                     self.check('enabledState', 'Enabled'),
                     self.check('protocol', 'Https'),
                     self.check('healthProbeMethod', 'HEAD'),
                 ])
        self.cmd('network front-door probe list -f {front_door} -g {rg} ',
                 checks=[
                     self.check('length(@)', 2),
                 ])
        self.cmd('network front-door probe show -f {front_door} -g {rg} -n {pb1} ')
        self.cmd('network front-door probe delete -f {front_door} -g {rg} -n {pb1} ')
        self.cmd('network front-door probe list -f {front_door} -g {rg} ',
                 checks=[
                     self.check('length(@)', 1),
                 ])
