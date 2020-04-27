# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class PeeringScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_peering')
    def test_peering(self, resource_group):

        self.kwargs.update({
            'name': 'test1'
        })

        self.cmd('az peering service create --resource-group {rg} --name "MyPeeringService" --location eastus --peering-service-location "California" --peering-service-provider "Kordia Limited"', checks=[
        ])

        self.cmd('az peering service prefix create --resource-group {rg} --peering-service-name "MyPeeringService" --name "MyPeeringServicePrefix" --prefix "192.168.1.0/24"', checks=[
        ])

        self.cmd('az peering service prefix delete --resource-group {rg} --peering-service-name "MyPeeringService" --name "MyPeeringServicePrefix"', checks=[
        ])

        self.cmd('az peering service delete --resource-group {rg} --name "MyPeeringService"', checks=[
        ])
