# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer,
                               JMESPathCheck, JMESPathCheckExists,
                               NoneCheck)
from msrestazure.tools import resource_id


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class DatabricksClientScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_databricks')
    def test_databricks(self, resource_group):

        self.kwargs.update({
            'workspaceName': 'my-test-workspace',
            'subscription': '0b1f6471-1bf0-4dda-aec3-cb9272f09590'
        })

        self.cmd('az account set --subscription {subscription}', checks=NoneCheck())

        self.cmd('az databricks workspace create '
                 '--resource-group {rg} '
                 '--name {workspaceName} '
                 '--location "westus" '
                 '--sku standard',
                 checks=[JMESPathCheck('name', self.kwargs.get('workspaceName', ''))])

        self.cmd('az databricks workspace update '
                 '--resource-group {rg} '
                 '--name {workspaceName} '
                 '--tags type=test',
                 checks=[JMESPathCheck('tags.type', 'test')])

        self.cmd('az databricks workspace show '
                 '--resource-group {rg} '
                 '--name {workspaceName}',
                 checks=[JMESPathCheck('name', self.kwargs.get('workspaceName', ''))])

        workspace_resource_id = resource_id(
            subscription=self.kwargs.get('subscription', ''),
            resource_group=resource_group,
            namespace='Microsoft.Databricks',
            type='workspaces',
            name=self.kwargs.get('workspaceName', ''))

        self.cmd('az databricks workspace show '
                 '--ids {}'.format(workspace_resource_id),
                 checks=[JMESPathCheck('name', self.kwargs.get('workspaceName', ''))])

        # self.cmd('az databricks workspace list',
        #          '--all'
        #          checks=[])

        self.cmd('az databricks workspace list '
                 '--resource-group {rg} ',
                 checks=[])

        self.cmd('az databricks workspace delete '
                 '--resource-group {rg} '
                 '--name {workspaceName} '
                 '-y',
                 checks=[])
