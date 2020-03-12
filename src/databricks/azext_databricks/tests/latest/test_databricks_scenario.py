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
            'workspace_name': 'my-test-workspace',
            'subscription': '00000000-0000-0000-0000-000000000000',
            'custom_workspace_name': 'my-custom-workspace',
            'managed_resource_group': 'custom-managed-rg'
        })

        self.cmd('az databricks workspace create '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '--location "westus" '
                 '--sku standard',
                 checks=[JMESPathCheck('name', self.kwargs.get('workspace_name', '')),
                         JMESPathCheck('sku.name', self.kwargs.get('sku.name', 'standard'))])

        managed_resource_group_id = '/subscriptions/{}/resourceGroups/{}'.format(self.kwargs.get('subscription', ''), self.kwargs.get('managed_resource_group', ''))
        self.cmd('az databricks workspace create '
                 '--resource-group {rg} '
                 '--name {custom_workspace_name} '
                 '--location "westus" '
                 '--sku standard '
                 '--managed-resource-group {managed_resource_group} '
                 '--relay-namespace-name custom-relay-space '
                 '--storage-account-name customdbstorage '
                 '--storage-account-sku Standard_LRS',
                 checks=[JMESPathCheck('name', self.kwargs.get('custom_workspace_name', '')),
                         JMESPathCheck('parameters.relayNamespaceName.value', 'custom-relay-space'),
                         JMESPathCheck('parameters.storageAccountName.value', 'customdbstorage'),
                         JMESPathCheck('parameters.storageAccountSkuName.value', 'Standard_LRS'),
                         JMESPathCheck('managedResourceGroupId', managed_resource_group_id)])

        self.cmd('az databricks workspace update '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '--tags type=test',
                 checks=[JMESPathCheck('tags.type', 'test')])

        self.cmd('az databricks workspace show '
                 '--resource-group {rg} '
                 '--name {workspace_name}',
                 checks=[JMESPathCheck('name', self.kwargs.get('workspace_name', ''))])

        workspace_resource_id = resource_id(
            subscription=self.kwargs.get('subscription', ''),
            resource_group=resource_group,
            namespace='Microsoft.Databricks',
            type='workspaces',
            name=self.kwargs.get('workspace_name', ''))

        self.cmd('az databricks workspace show '
                 '--ids {}'.format(workspace_resource_id),
                 checks=[JMESPathCheck('name', self.kwargs.get('workspace_name', ''))])

        # todo service 502
        # self.cmd('az databricks workspace list',
        #          '--resource-group='
        #          checks=[])

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
