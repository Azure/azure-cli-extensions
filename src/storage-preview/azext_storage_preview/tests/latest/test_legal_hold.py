# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, JMESPathCheck, ResourceGroupPreparer, StorageAccountPreparer)


class StorageLegalHold(ScenarioTest):
    @ResourceGroupPreparer(location='eastus2euap')
    @StorageAccountPreparer(location='eastus2euap')
    def test_storage_legal_hold(self, resource_group, storage_account):
        container_name = 'container1'
        self.cmd('storage container create --account-name {} -n {}'.format(storage_account, container_name))

        self.cmd('storage container legal-hold show --account-name {} -c {} -g {}'.format(
            storage_account, container_name, resource_group), checks=[
                JMESPathCheck("tags", [])])

        result = self.cmd('storage container legal-hold set --account-name {} -c {} -g {} --tags tag1 tag2'.format(
            storage_account, container_name, resource_group)).get_output_in_json()
        self.assertIn("tag1", result.get("tags"))
        self.assertIn("tag2", result.get("tags"))

        self.cmd('storage container legal-hold clear --account-name {} -c {} -g {} --tags tag1 tag2'.format(
            storage_account, container_name, resource_group), checks=[
                JMESPathCheck("tags", [])])
