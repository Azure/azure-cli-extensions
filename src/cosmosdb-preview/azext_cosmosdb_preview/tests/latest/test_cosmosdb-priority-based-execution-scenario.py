# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class Cosmosdb_previewPriorityBasedExecutionScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_priority_based_execution', location='westus')
    def test_cosmosdb_sql_priority_based_execution(self):
        # col = self.create_random_name(prefix='cli', length=15)
        # db_name = self.create_random_name(prefix='cli', length=15)
        # Assumption: There exists a cosmosTest rg.
        self.kwargs.update({
            'rg': 'cosmosTest',
            'acc': 'priority-based-execution-test',
            'loc': 'westus',
            'tar': '0=1200 1=1200',
            'src': '2'
        })

        # create priority based execution enabled account
        self.cmd('az cosmosdb create -n {acc} -g {rg} --enable-priority-based-execution')
        self.cmd('az cosmosdb show -n {acc} -g {rg}', checks=[
            self.check('enablePriorityBasedExecution', True),
        ])
        print('Created account with Priority Based Execution Enabled')

        # set default priority level to low priority
        self.cmd('az cosmosdb update -n {acc} -g {rg} --default-priority-level Low')
        self.cmd('az cosmosdb show -n {acc} -g {rg}', checks=[
            self.check('defaultPriorityLevel', 'Low'),
        ])
        print('Set Default Priority Level to Low')

        # disable Priority Based Execution
        self.cmd('az cosmosdb update -n {acc} -g {rg} --enable-priority-based-execution false')
        self.cmd('az cosmosdb show -n {acc} -g {rg}', checks=[
            self.check('enablePriorityBasedExecution', False),
        ])
        print('Disabled Priority Based Execution')

        # enable Priority Based Execution
        self.cmd('az cosmosdb update -n {acc} -g {rg} --enable-priority-based-execution')
        self.cmd('az cosmosdb show -n {acc} -g {rg}', checks=[
            self.check('enablePriorityBasedExecution', True),
        ])
        print('Enabled Priority Based Execution')

        # set default priority level to high priority
        self.cmd('az cosmosdb update -n {acc} -g {rg} --default-priority-level High')
        self.cmd('az cosmosdb show -n {acc} -g {rg}', checks=[
            self.check('defaultPriorityLevel', 'High'),
        ])
        print('Set Default Priority Level to High')

        # delete account
        self.cmd('az cosmosdb delete -n {acc} -g {rg} --yes')
