# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class Cosmosdb_previewCapacityModeScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_capacity_mode', location='australiaeast')
    def test_cosmosdb_capacity_mode_Change(self):
        # col = self.create_random_name(prefix='cli', length=15)
        # db_name = self.create_random_name(prefix='cli', length=15)
        # Assumption: There exists a cosmosTest rg.
        self.kwargs.update({
            'rg': 'cosmosTest',
            'acc': 'capacity-mode-test-38129749813',
            'loc': 'australiaeast',
            'tar': '0=1200 1=1200',
            'src': '2'
        })

        # create serverless capacity mode account
        self.cmd('az cosmosdb create -n {acc} -g {rg} --locations regionName="{loc}" --capacity-mode serverless')
        self.cmd('az cosmosdb show -n {acc} -g {rg}', checks=[
            self.check('capacityMode', "Serverless"),
        ])
        print('Created Serverless capacity mode enabled account')

        # change capacity mode to provisioned.
        self.cmd('az cosmosdb update -n {acc} -g {rg} --capacity-mode provisioned')
        self.cmd('az cosmosdb show -n {acc} -g {rg}', checks=[
            self.check('capacityMode', "Provisioned"),
        ])
        print('Changed capacity mode')

        # delete account
        self.cmd('az cosmosdb delete -n {acc} -g {rg} --yes')
