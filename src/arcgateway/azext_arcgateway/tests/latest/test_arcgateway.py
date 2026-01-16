# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import requests

from azure.cli.testsdk.scenario_tests import AllowLargeResponse, live_only
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)
from azure.cli.testsdk.checkers import StringContainCheckIgnoreCase, JMESPathCheckExists, JMESPathCheckNotExists

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ArcGatewayScenario(ScenarioTest):
    @live_only()
    @ResourceGroupPreparer(name_prefix='cli_test_arcgateway')
    def test_arcgateway(self):
        rand_string = 'test'
        self.kwargs.update({
            'machine': 'testmachine',
            'location': 'eastus',
            'subscription': 'b24cc8ee-df4f-48ac-94cf-46edf36b0fae',
            'gatewayName': 'myArcgateway',
            'newResourceGroup': 'ytongtest',
        })

        self.cmd('az arcgateway create '
                '--resource-group "{newResourceGroup}" '
                '--subscription "{subscription}" '
                '--location {location} '            
                '--name {gatewayName}',
                 checks=[]) 

        self.cmd('az arcgateway list '
                '--subscription "{subscription}"',
                 checks=[]) 

        self.cmd('az arcgateway show '
                '--resource-group "{newResourceGroup}" '
                '--subscription "{subscription}" '         
                '--name {gatewayName}',
                 checks=[]) 

        self.cmd('az arcgateway settings update '
                '--resource-group "{newResourceGroup}" '
                '--subscription "{subscription}" '
                '--base-provider "Microsoft.HybridCompute" '
                '--base-resource-type "machines" '
                '--base-resource-name "testmachine" '
                '--gateway-resource-id "/subscriptions/{subscription}/resourceGroups/{newResourceGroup}/providers/Microsoft.HybridCompute/gateways/{gatewayName}"',
                checks=[]) 

        self.cmd('az arcgateway delete -y '
                '--resource-group "{newResourceGroup}" '
                '--subscription "{subscription}" '         
                '--name {gatewayName}',
                 checks=[]) 
