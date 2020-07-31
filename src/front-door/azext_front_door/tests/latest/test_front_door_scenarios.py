# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class FrontDoorBasicScenarioTests(ScenarioTest):

    @unittest.skip("The test is not working due to the service's limitation.")
    @ResourceGroupPreparer(location='westus')
    def test_front_door_basic_scenario(self, resource_group):
        self.kwargs.update({
            'front_door': self.create_random_name('clifrontdoor', 20),
            'frontend_endpoint': 'www.mysite.com',
            'rule1': 'rule1',
            'rule2': 'rule2'
        })
        self.cmd('network front-door create -g {rg} -n {front_door} --backend-address 202.120.2.3')
        # Custom frontend endpoint must have a CNAME pointing to the default frontend host.
        # More information can be found in https://docs.microsoft.com/en-us/azure/frontdoor/front-door-custom-domain#create-a-cname-dns-record
        # Since it's not easy to have a custom domain, we skip this test for now.
        self.cmd('network front-door frontend-endpoint create -g {rg} -f {front_door} -n myclitest '
                 '--host-name {frontend_endpoint} --session-affinity-enabled')
