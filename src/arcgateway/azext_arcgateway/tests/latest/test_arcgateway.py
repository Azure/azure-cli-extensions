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
    def test_setting(self):
        rand_string = 'test'
        self.kwargs.update({
            'machine': 'testmachine',
            'rg': 'manojamp',
            'location': 'eastus2euap',
            'subscription': '00000000-0000-0000-0000-000000000000',
            'gatewayName': 'myGateway',
            'newResourceGroup': 'ytongtest',
        })


        # gateway
        self.cmd('az arcgateway create '
                '--resource-group "{newResourceGroup}" '
                '--subscription "{subscription}" '
                '--location {location} '            
                '--name {gatewayName}',
                 checks=[]) 

        self.cmd('az arcgateway create '
                '--resource-group "{newResourceGroup}" '
                '--subscription "{subscription}" '
                '--location {location} '            
                '--name {gatewayName}',
                 checks=[]) 

        self.cmd('az arcgateway create '
                '--resource-group "{newResourceGroup}" '
                '--subscription "{subscription}" '
                '--location {location} '            
                '--name {gatewayName}',
                 checks=[]) 


        # settings
        self.cmd('az arcgateway settings update '
                '--resource-group "{newResourceGroup}" '
                '--subscription "{subscription}" '
                '--base-provider "Microsoft.HybridCompute" '
                '--base-resource-type "machines" '
                '--base-resource-name "testmachine" '
                '--settings-resource-name "default" '
                '--gateway-resource-id "/subscriptions/{subscription}/resourceGroups/manojamp/providers/Microsoft.HybridCompute/gateways/amkgw1" '              
                '--name "default"',
                checks=[]) 
