# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

import os
from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk import ResourceGroupPreparer
from .. import (
    raise_if,
    calc_coverage
)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class GatewayScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_gateway')
    def test_gateway(self):
        rand_string = 'test'
        self.kwargs.update({
            'machine': 'testmachine',
            'rg': 'manojamp',
            'location': 'eastus2euap',
            'gatewayName': 'myGateway',
            'newResourceGroup': 'ytongtest',
        })

        self.cmd('az arc gateway create '
                '--resource-group "{rg}" '
                '--location "{location}" '
                '--name "{gatewayName}" '
                '--allowed-features *',
                checks=[
                    self.check('name', '{gatewayName}')
                ])
        
        self.cmd('az arc gateway list',
                checks=[
                    self.check('length(@)', 5)
                ])

        self.cmd('az arc gateway show '
                '--resource-group "{rg}" '
                '--name "{gatewayName}"',
                checks=[
                    self.check('length(@)', 10)
                ])

        self.cmd('az arc gateway update '
                '--resource-group "{rg}" '
                '--name "{gatewayName}"',
                checks=[
                    self.check('resourceGroup','{rg}')
                ])

        self.cmd('az arc gateway delete '
                '--resource-group "{rg}" '
                '--name "{gatewayName}" --yes',
                checks=[])