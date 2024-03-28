# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class Cosmosdb_previewMaterialiedviewScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_materializedview', location='australiaeast')
    def test_cosmosdb_materializedview(self):
        src = 'src1'
        mvName1 = 'mv1'
        mvName2 = 'mv2'
        mvDefinitionFile = 'mv.json'
        mvDefenitionFilePath = os.path.join(TEST_DIR, mvDefinitionFile).replace("\\", "\\\\")
        print('Creating Materializedview enabled account')
        db_name = self.create_random_name(prefix='cli', length=15)
        # Assumption: There exists a cosmosTest rg.
        self.kwargs.update({
            'rg': 'abpai-resources',
            'acc': 'mv-test-38129749813',
            'db_name': db_name,
            'col': src,
            'mvCol1': mvName1,
            'mvCol2': mvName2,
            'loc': 'australiaeast',
            'tar': '0=1200 1=1200',
            'src': '2',
            'mvDefinition': '"{\\"sourceCollectionId\\": \\"src1\\", \\"definition\\": \\"select * from root\\"}"',
            'mvDefinitionFilePath': mvDefenitionFilePath
        })

        # create materialized view enabled account
        self.cmd('az cosmosdb create -n {acc} -g {rg} --enable-materialized-views')
        self.cmd('az cosmosdb show -n {acc} -g {rg}', checks=[
            self.check('enableMaterializedViews', True),
        ])
        print('Created Materializedview enabled account')

        # Create database
        self.cmd('az cosmosdb sql database create -g {rg} -a {acc} -n {db_name}')

        # Create container
        self.cmd('az cosmosdb sql container create -g {rg} -a {acc} -d {db_name} -n {col} -p /pk').get_output_in_json()

        # Create Materialized view container
        print('Creatin Materializedview container {mvDefinition}')
        self.cmd('az cosmosdb sql container create -g {rg} -a {acc} -d {db_name} -n {mvCol1} -p /mvpk --materialized-view-definition @{mvDefinitionFilePath}',
                 checks=[self.check('resource.materializedViewDefinition.sourceCollectionId', "src1")])
        self.cmd('az cosmosdb sql container create -g {rg} -a {acc} -d {db_name} -n {mvCol2} -p /mvpk --materialized-view-definition {mvDefinition}',
                 checks=[self.check('resource.materializedViewDefinition.sourceCollectionId', "src1")])

        # delete account
        self.cmd('az cosmosdb delete -n {acc} -g {rg} --yes')
