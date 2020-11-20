# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class FrontendEndpointScenarioTests(ScenarioTest):

    @ResourceGroupPreparer(location='westus')
    def test_frontend_endpoint_basic(self, resource_group):
        self.kwargs.update({
            'front_door': self.create_random_name('clifrontdoor', 20),
        })
        self.cmd('network front-door create -g {rg} -n {front_door} --backend-address 202.120.2.3 ')
        self.cmd('network front-door frontend-endpoint list -f {front_door} -g {rg} ',
                 checks=[
                     self.check('length(@)', 1),
                 ])
        self.cmd('network front-door frontend-endpoint show -f {front_door} -g {rg} -n DefaultFrontendEndpoint ')
