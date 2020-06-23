# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class FrontDoorBasicScenarioTests(ScenarioTest):

    @ResourceGroupPreparer(location='westus')
    def test_front_door_basic_scenario(self, resource_group):
        self.kwargs.update({
            'front_door': self.create_random_name('clifrontdoor', 20),
            'frontend_endpoint': 'www.mysite.com',
            'rule1': 'rule1',
            'rule2': 'rule2'
        })
        self.cmd('network front-door create -g {rg} -n {front_door} --backend-address 202.120.2.3')
        self.cmd('network dns zone create -g {rg} -n {front_door}.azurefd.net')
        self.cmd('network dns record-set cname set-record -g {rg} -z {front_door}.azurefd.net -n MyRecordSet -c {frontend_endpoint}')
        self.cmd('network front-door frontend-endpoint create -g {rg} -f {front_door} -n myclitest '
                 '--host-name {frontend_endpoint} --session-affinity-enabled')
