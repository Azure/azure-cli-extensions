# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class LoadBalancingScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(location='westus')
    def test_load_balancing_basic(self, resource_group):
        self.kwargs.update({
            'front_door': self.create_random_name('clifrontdoor', 20),
            'lb1': 'lb1'
        })
        self.cmd('network front-door create -g {rg} -n {front_door} --backend-address 202.120.2.3')
        self.cmd('network front-door load-balancing create -f {front_door} -g {rg} -n {lb1} '
                 '--sample-size 5 '
                 '--successful-samples-required 1 '
                 '--additional-latency 100 ',
                 checks=[
                     self.check('sampleSize', 5),
                     self.check('successfulSamplesRequired', 1),
                     self.check('additionalLatencyMilliseconds', 100),
                 ])
        self.cmd('network front-door load-balancing update -f {front_door} -g {rg} -n {lb1} '
                 '--sample-size 4 '
                 '--successful-samples-required 2 '
                 '--additional-latency 10 ',
                 checks=[
                     self.check('sampleSize', 4),
                     self.check('successfulSamplesRequired', 2),
                     self.check('additionalLatencyMilliseconds', 10),
                 ])
        self.cmd('network front-door load-balancing list -f {front_door} -g {rg} ',
                 checks=[
                     self.check('length(@)', 2),
                 ])
        self.cmd('network front-door load-balancing show -f {front_door} -g {rg} -n {lb1} ')
        self.cmd('network front-door load-balancing delete -f {front_door} -g {rg} -n {lb1} ')
        self.cmd('network front-door load-balancing list -f {front_door} -g {rg} ',
                 checks=[
                     self.check('length(@)', 1),
                 ])
