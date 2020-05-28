# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from msrestazure.tools import resource_id


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class DatabricksClientScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_databricks')
    def test_databricks(self, resource_group):
        subscription_id = self.get_subscription_id()
        self.kwargs.update({
            'workspace_name': 'my-test-workspace',
            'custom_workspace_name': 'my-custom-workspace',
            'managed_resource_group': 'custom-managed-rg'
        })

        self.cmd('az databricks workspace create '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '--location "eastus2euap" '
                 '--sku premium',
                 checks=[self.check('name', '{workspace_name}'),
                         self.check('sku.name', 'premium')])

        managed_resource_group_id = '/subscriptions/{}/resourceGroups/{}'.format(subscription_id, self.kwargs.get('managed_resource_group', ''))
        self.cmd('az databricks workspace create '
                 '--resource-group {rg} '
                 '--name {custom_workspace_name} '
                 '--location "westus" '
                 '--sku standard '
                 '--managed-resource-group {managed_resource_group}',
                 checks=[self.check('name', '{custom_workspace_name}'),
                         self.check('managedResourceGroupId', managed_resource_group_id)])

        self.cmd('az databricks workspace update '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '--tags type=test '
                 '--assign-identity',
                 checks=[self.check('tags.type', 'test'),
                         self.exists('storageAccountIdentity.principalId')])

        self.cmd('az databricks workspace show '
                 '--resource-group {rg} '
                 '--name {workspace_name}',
                 checks=[self.check('name', '{workspace_name}')])

        workspace_resource_id = resource_id(
            subscription=subscription_id,
            resource_group=resource_group,
            namespace='Microsoft.Databricks',
            type='workspaces',
            name=self.kwargs.get('workspace_name', ''))

        self.cmd('az databricks workspace show '
                 '--ids {}'.format(workspace_resource_id),
                 checks=[self.check('name', '{workspace_name}')])

        self.cmd('az databricks workspace list '
                 '--resource-group {rg} ',
                 checks=[])

        self.cmd('az databricks workspace delete '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '-y',
                 checks=[])

        self.cmd('az databricks workspace delete '
                 '--resource-group {rg} '
                 '--name {custom_workspace_name} '
                 '-y',
                 checks=[])
