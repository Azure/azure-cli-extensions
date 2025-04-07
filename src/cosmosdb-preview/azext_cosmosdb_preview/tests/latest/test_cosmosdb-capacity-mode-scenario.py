# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from knack.util import CLIError
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class Cosmosdb_previewCapacityModeScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_capacity_mode', location='eastus2')
    def test_cosmosdb_capacity_mode_account_create(self):
        self.kwargs.update({
            'acc1': self.create_random_name(prefix='capacity-mode', length=20),
            'acc2': self.create_random_name(prefix='capacity-mode', length=20),
            'acc3': self.create_random_name(prefix='capacity-mode', length=20),
            'loc': 'eastus2',
            'tar': '0=1200 1=1200',
            'src': '2'
        })

        # create serverless capacity mode account
        self.cmd('az cosmosdb create -n {acc1} -g {rg} --locations regionName="{loc}" --capacity-mode serverless')
        self.cmd('az cosmosdb show -n {acc1} -g {rg}', checks=[
            self.check('capacityMode', "Serverless"),
        ])
        print('Created Serverless capacity mode enabled account')

        # delete account
        self.cmd('az cosmosdb delete -n {acc1} -g {rg} --yes')

        # create serverless capacity mode account
        self.cmd('az cosmosdb create -n {acc2} -g {rg} --locations regionName="{loc}" --capacity-mode Provisioned')
        self.cmd('az cosmosdb show -n {acc2} -g {rg}', checks=[
            self.check('capacityMode', "Provisioned"),
        ])
        print('Created Provisioned capacity mode enabled account')

        # delete account
        self.cmd('az cosmosdb delete -n {acc2} -g {rg} --yes')

        # create default capacity mode account
        self.cmd('az cosmosdb create -n {acc3} -g {rg} --locations regionName="{loc}"')
        self.cmd('az cosmosdb show -n {acc3} -g {rg}', checks=[
            self.check('capacityMode', "Provisioned"),
        ])
        print('Created Provisioned capacity mode enabled account')

        # delete account
        self.cmd('az cosmosdb delete -n {acc3} -g {rg} --yes')
        

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_capacity_mode', location='eastus2')
    def test_cosmosdb_capacity_mode_change(self):
        # col = self.create_random_name(prefix='cli', length=15)
        # db_name = self.create_random_name(prefix='cli', length=15)
        # Assumption: There exists a cosmosTest rg.
        self.kwargs.update({
            'acc1': self.create_random_name(prefix='capacity-mode', length=20),
            'loc': 'eastus2',
            'tar': '0=1200 1=1200',
            'src': '2'
        })

        # create serverless capacity mode account
        self.cmd('az cosmosdb create -n {acc1} -g {rg} --locations regionName="{loc}" --capacity-mode serverless')
        self.cmd('az cosmosdb show -n {acc1} -g {rg}', checks=[
            self.check('capacityMode', "Serverless"),
        ])
        print('Created Serverless capacity mode enabled account.')

        # change burst capacity, capacity mode should not change.
        self.cmd('az cosmosdb update -n {acc1} -g {rg} --enable-burst-capacity false')
        self.cmd('az cosmosdb show -n {acc1} -g {rg}', checks=[
            self.check('capacityMode', "Serverless"),
        ])
        print('Account remained Serverless even after updating burst capacity.')

        # change capacity mode to provisioned.
        self.cmd('az cosmosdb update -n {acc1} -g {rg} --capacity-mode provisioned')
        self.cmd('az cosmosdb show -n {acc1} -g {rg}', checks=[
            self.check('capacityMode', "Provisioned"),
        ])
        print('Changed capacity mode')

        # delete account
        self.cmd('az cosmosdb delete -n {acc1} -g {rg} --yes')
