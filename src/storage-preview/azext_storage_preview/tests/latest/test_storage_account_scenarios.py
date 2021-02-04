# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import (ScenarioTest, JMESPathCheck, ResourceGroupPreparer, StorageAccountPreparer,
                               api_version_constraint, live_only)
from azure_devtools.scenario_tests import AllowLargeResponse
from .storage_test_util import StorageScenarioMixin
from ...profiles import CUSTOM_MGMT_PREVIEW_STORAGE
from knack.util import CLIError


@api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2016-12-01')
class StorageAccountNetworkRuleTests(StorageScenarioMixin, ScenarioTest):
    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2017-06-01')
    @ResourceGroupPreparer(name_prefix='cli_test_storage_service_endpoints')
    @StorageAccountPreparer()
    def test_storage_account_network_rules(self, resource_group):
        kwargs = {
            'rg': resource_group,
            'acc': self.create_random_name(prefix='cli', length=24),
            'vnet': 'vnet1',
            'subnet': 'subnet1'
        }
        self.cmd('storage account create -g {rg} -n {acc} --bypass Metrics --default-action Deny --https-only'.format(**kwargs),
                 checks=[
                     JMESPathCheck('networkRuleSet.bypass', 'Metrics'),
                     JMESPathCheck('networkRuleSet.defaultAction', 'Deny')])
        self.cmd('storage account update -g {rg} -n {acc} --bypass Logging --default-action Allow'.format(**kwargs),
                 checks=[
                     JMESPathCheck('networkRuleSet.bypass', 'Logging'),
                     JMESPathCheck('networkRuleSet.defaultAction', 'Allow')])
        self.cmd('storage account update -g {rg} -n {acc} --set networkRuleSet.default_action=deny'.format(**kwargs),
                 checks=[
                     JMESPathCheck('networkRuleSet.bypass', 'Logging'),
                     JMESPathCheck('networkRuleSet.defaultAction', 'Deny')])

        self.cmd('network vnet create -g {rg} -n {vnet} --subnet-name {subnet}'.format(**kwargs))
        self.cmd(
            'network vnet subnet update -g {rg} --vnet-name {vnet} -n {subnet} --service-endpoints Microsoft.Storage'.format(
                **kwargs))

        self.cmd('storage account network-rule add -g {rg} --account-name {acc} --ip-address 25.1.2.3'.format(**kwargs))
        # test network-rule add idempotent
        self.cmd('storage account network-rule add -g {rg} --account-name {acc} --ip-address 25.1.2.3'.format(**kwargs))
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {acc} --ip-address 25.2.0.0/24'.format(**kwargs))
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {acc} --vnet-name {vnet} --subnet {subnet}'.format(
                **kwargs))
        self.cmd('storage account network-rule list -g {rg} --account-name {acc}'.format(**kwargs), checks=[
            JMESPathCheck('length(ipRules)', 2),
            JMESPathCheck('length(virtualNetworkRules)', 1)
        ])
        # test network-rule add idempotent
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {acc} --vnet-name {vnet} --subnet {subnet}'.format(
                **kwargs))
        self.cmd('storage account network-rule list -g {rg} --account-name {acc}'.format(**kwargs), checks=[
            JMESPathCheck('length(ipRules)', 2),
            JMESPathCheck('length(virtualNetworkRules)', 1)
        ])
        self.cmd(
            'storage account network-rule remove -g {rg} --account-name {acc} --ip-address 25.1.2.3'.format(**kwargs))
        self.cmd(
            'storage account network-rule remove -g {rg} --account-name {acc} --vnet-name {vnet} --subnet {subnet}'.format(
                **kwargs))
        self.cmd('storage account network-rule list -g {rg} --account-name {acc}'.format(**kwargs), checks=[
            JMESPathCheck('length(ipRules)', 1),
            JMESPathCheck('length(virtualNetworkRules)', 0)
        ])

    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2020-08-01-preview')
    @ResourceGroupPreparer(name_prefix='cli_test_storage_service_endpoints')
    @StorageAccountPreparer()
    def test_storage_account_resource_access_rules(self, resource_group, storage_account):
        self.kwargs = {
            'rg': resource_group,
            'sa': storage_account,
            'rid1': "/subscriptions/a7e99807-abbf-4642-bdec-2c809a96a8bc/resourceGroups/res9407/providers/Microsoft.Synapse/workspaces/testworkspace1",
            'rid2': "/subscriptions/a7e99807-abbf-4642-bdec-2c809a96a8bc/resourceGroups/res9407/providers/Microsoft.Synapse/workspaces/testworkspace2",
            'rid3': "/subscriptions/a7e99807-abbf-4642-bdec-2c809a96a8bc/resourceGroups/res9407/providers/Microsoft.Synapse/workspaces/testworkspace3",
            'tid1': "72f988bf-86f1-41af-91ab-2d7cd011db47",
            'tid2': "72f988bf-86f1-41af-91ab-2d7cd011db47"
        }

        self.cmd(
            'storage account network-rule add -g {rg} --account-name {sa} --resource-id {rid1} --tenant-id {tid1}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 1)
        ])

        # test network-rule add idempotent
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {sa} --resource-id {rid1} --tenant-id {tid1}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 1)
        ])

        # test network-rule add more
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {sa} --resource-id {rid2} --tenant-id {tid1}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 2)
        ])

        self.cmd(
            'storage account network-rule add -g {rg} --account-name {sa} --resource-id {rid3} --tenant-id {tid2}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 3)
        ])

        # remove network-rule
        self.cmd(
            'storage account network-rule remove -g {rg} --account-name {sa} --resource-id {rid1} --tenant-id {tid1}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 2)
        ])
        self.cmd(
            'storage account network-rule remove -g {rg} --account-name {sa} --resource-id {rid2} --tenant-id {tid2}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 1)
        ])


class StorageAccountBlobInventoryScenarioTest(StorageScenarioMixin, ScenarioTest):
    @AllowLargeResponse()
    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2020-08-01-preview')
    @ResourceGroupPreparer(name_prefix='cli_test_blob_inventory', location='eastus2')
    @StorageAccountPreparer(location='eastus2euap', kind='StorageV2')
    def test_storage_account_blob_inventory_policy(self, resource_group, storage_account):
        import os
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        policy_file = os.path.join(curr_dir, 'blob_inventory_policy.json').replace('\\', '\\\\')
        policy_file_no_type = os.path.join(curr_dir, 'blob_inventory_policy_no_type.json').replace('\\', '\\\\')
        self.kwargs = {'rg': resource_group,
                       'sa': storage_account,
                       'policy': policy_file,
                       'policy_no_type': policy_file_no_type}
        account_info = self.get_account_info(resource_group, storage_account)
        self.storage_cmd('storage container create -n mycontainer', account_info)

        # Create policy without type specified
        self.cmd('storage account blob-inventory-policy create --account-name {sa} -g {rg} --policy @"{policy_no_type}"',
                 checks=[JMESPathCheck("name", "DefaultInventoryPolicy"),
                         JMESPathCheck("policy.destination", "mycontainer"),
                         JMESPathCheck("policy.enabled", True),
                         JMESPathCheck("policy.rules[0].definition.filters.blobTypes[0]", "blockBlob"),
                         JMESPathCheck("policy.rules[0].definition.filters.includeBlobVersions", None),
                         JMESPathCheck("policy.rules[0].definition.filters.includeSnapshots", None),
                         JMESPathCheck("policy.rules[0].definition.filters.prefixMatch", None),
                         JMESPathCheck("policy.rules[0].enabled", True),
                         JMESPathCheck("policy.rules[0].name", "inventoryPolicyRule1"),
                         JMESPathCheck("policy.type", "Inventory"),
                         JMESPathCheck("resourceGroup", resource_group),
                         JMESPathCheck("systemData", None)])

        self.cmd('storage account blob-inventory-policy show --account-name {sa} -g {rg}',
                 checks=[JMESPathCheck("name", "DefaultInventoryPolicy"),
                         JMESPathCheck("policy.destination", "mycontainer"),
                         JMESPathCheck("policy.enabled", True),
                         JMESPathCheck("policy.rules[0].definition.filters.blobTypes[0]", "blockBlob"),
                         JMESPathCheck("policy.rules[0].definition.filters.includeBlobVersions", None),
                         JMESPathCheck("policy.rules[0].definition.filters.includeSnapshots", None),
                         JMESPathCheck("policy.rules[0].definition.filters.prefixMatch", None),
                         JMESPathCheck("policy.rules[0].enabled", True),
                         JMESPathCheck("policy.rules[0].name", "inventoryPolicyRule1"),
                         JMESPathCheck("policy.type", "Inventory"),
                         JMESPathCheck("resourceGroup", resource_group),
                         JMESPathCheck("systemData", None)])

        # Enable Versioning for Storage Account when includeBlobInventory=true in policy
        self.cmd('storage account blob-service-properties update -n {sa} -g {rg} --enable-versioning', checks=[
                 JMESPathCheck('isVersioningEnabled', True)])

        self.cmd('storage account blob-inventory-policy create --account-name {sa} -g {rg} --policy @"{policy}"',
                 checks=[JMESPathCheck("name", "DefaultInventoryPolicy"),
                         JMESPathCheck("policy.destination", "mycontainer"),
                         JMESPathCheck("policy.enabled", True),
                         JMESPathCheck("policy.rules[0].definition.filters.blobTypes[0]", "blockBlob"),
                         JMESPathCheck("policy.rules[0].definition.filters.includeBlobVersions", True),
                         JMESPathCheck("policy.rules[0].definition.filters.includeSnapshots", True),
                         JMESPathCheck("policy.rules[0].definition.filters.prefixMatch[0]", "inventoryprefix1"),
                         JMESPathCheck("policy.rules[0].definition.filters.prefixMatch[1]", "inventoryprefix2"),
                         JMESPathCheck("policy.rules[0].enabled", True),
                         JMESPathCheck("policy.rules[0].name", "inventoryPolicyRule1"),
                         JMESPathCheck("policy.type", "Inventory"),
                         JMESPathCheck("resourceGroup", resource_group),
                         JMESPathCheck("systemData", None)])

        self.cmd('storage account blob-inventory-policy show --account-name {sa} -g {rg}',
                 checks=[JMESPathCheck("name", "DefaultInventoryPolicy"),
                         JMESPathCheck("policy.destination", "mycontainer"),
                         JMESPathCheck("policy.enabled", True),
                         JMESPathCheck("policy.rules[0].definition.filters.blobTypes[0]", "blockBlob"),
                         JMESPathCheck("policy.rules[0].definition.filters.includeBlobVersions", True),
                         JMESPathCheck("policy.rules[0].definition.filters.includeSnapshots", True),
                         JMESPathCheck("policy.rules[0].definition.filters.prefixMatch[0]", "inventoryprefix1"),
                         JMESPathCheck("policy.rules[0].definition.filters.prefixMatch[1]", "inventoryprefix2"),
                         JMESPathCheck("policy.rules[0].enabled", True),
                         JMESPathCheck("policy.rules[0].name", "inventoryPolicyRule1"),
                         JMESPathCheck("policy.type", "Inventory"),
                         JMESPathCheck("resourceGroup", resource_group),
                         JMESPathCheck("systemData", None)])

        self.cmd('storage account blob-inventory-policy update --account-name {sa} -g {rg}'
                 ' --set "policy.rules[0].name=newname"')
        self.cmd('storage account blob-inventory-policy show --account-name {sa} -g {rg}',
                 checks=JMESPathCheck('policy.rules[0].name', 'newname'))

        self.cmd('storage account blob-inventory-policy delete --account-name {sa} -g {rg} -y')
        self.cmd('storage account blob-inventory-policy show --account-name {sa} -g {rg}', expect_failure=True)


class FileServicePropertiesTests(StorageScenarioMixin, ScenarioTest):
    @ResourceGroupPreparer(name_prefix='cli_file_soft_delete')
    @StorageAccountPreparer(name_prefix='filesoftdelete', kind='StorageV2', location='eastus2euap')
    def test_storage_account_file_delete_retention_policy(self, resource_group, storage_account):
        from azure.cli.core.azclierror import ValidationError
        self.kwargs.update({
            'sa': storage_account,
            'rg': resource_group,
            'cmd': 'storage account file-service-properties'
        })
        self.cmd('{cmd} show --account-name {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy', None))

        with self.assertRaises(SystemExit):
            self.cmd('{cmd} update --enable-delete-retention true -n {sa} -g {rg}')

        with self.assertRaisesRegexp(ValidationError, "Delete Retention Policy hasn't been enabled,"):
            self.cmd('{cmd} update --delete-retention-days 1 -n {sa} -g {rg}')

        with self.assertRaises(SystemExit):
            self.cmd('{cmd} update --enable-delete-retention false --delete-retention-days 1')

        self.cmd(
            '{cmd} update --enable-delete-retention true --delete-retention-days 10 -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy.enabled', True),
            JMESPathCheck('shareDeleteRetentionPolicy.days', 10))

        self.cmd('{cmd} update --delete-retention-days 1 -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy.enabled', True),
            JMESPathCheck('shareDeleteRetentionPolicy.days', 1))

        self.cmd('{cmd} update --enable-delete-retention false -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy.enabled', False),
            JMESPathCheck('shareDeleteRetentionPolicy.days', None))

        self.cmd('{cmd} show -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy.enabled', False),
            JMESPathCheck('shareDeleteRetentionPolicy.days', 0))

    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2020-08-01-preview')
    @ResourceGroupPreparer(name_prefix='cli_file_smb')
    @StorageAccountPreparer(parameter_name='storage_account1', name_prefix='filesmb1', kind='FileStorage',
                            sku='Premium_LRS', location='centraluseuap')
    @StorageAccountPreparer(parameter_name='storage_account2', name_prefix='filesmb2', kind='StorageV2')
    def test_storage_account_file_smb_multichannel(self, resource_group, storage_account1, storage_account2):

        from azure.core.exceptions import ResourceExistsError
        self.kwargs.update({
            'sa': storage_account1,
            'sa2': storage_account2,
            'rg': resource_group,
            'cmd': 'storage account file-service-properties'
        })

        with self.assertRaisesRegexp(ResourceExistsError, "SMB Multichannel is not supported for the account."):
            self.cmd('{cmd} update --mc -n {sa2} -g {rg}')

        self.cmd('{cmd} show -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy', None),
            JMESPathCheck('protocolSettings.smb.multichannel.enabled', False))

        self.cmd('{cmd} show -n {sa2} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy', None),
            JMESPathCheck('protocolSettings.smb.multichannel', None))

        self.cmd(
            '{cmd} update --enable-smb-multichannel -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('protocolSettings.smb.multichannel.enabled', True))

        self.cmd(
            '{cmd} update --enable-smb-multichannel false -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('protocolSettings.smb.multichannel.enabled', False))

        self.cmd(
            '{cmd} update --enable-smb-multichannel true -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('protocolSettings.smb.multichannel.enabled', True))

    @ResourceGroupPreparer()
    @StorageAccountPreparer()
    def test_logging_operations(self, resource_group, storage_account):
        connection_string = self.cmd(
            'storage account show-connection-string -g {} -n {} -otsv'.format(resource_group, storage_account)).output
        account_info = self.get_account_info(resource_group, storage_account)

        self.cmd('storage logging show --connection-string {}'.format(connection_string), checks=[
            JMESPathCheck('blob.read', False),
            JMESPathCheck('blob.retentionPolicy.enabled', False),
            JMESPathCheck('adls.read', False),
            JMESPathCheck('queue.read', False),
            JMESPathCheck('table.read', False),
        ])

        self.cmd('storage logging update --services b --log r --retention 1 '
                 '--connection-string {}'.format(connection_string))

        self.cmd('storage logging show --connection-string {}'.format(connection_string), checks=[
            JMESPathCheck('blob.read', True),
            JMESPathCheck('blob.retentionPolicy.enabled', True),
            JMESPathCheck('blob.retentionPolicy.days', 1)
        ])

        self.storage_cmd('storage logging update --services a --log rw --retention 3 ', account_info)

        self.storage_cmd('storage logging show ', account_info).assert_with_checks([
            JMESPathCheck('adls.read', True),
            JMESPathCheck('adls.write', True),
            JMESPathCheck('adls.delete', False),
            JMESPathCheck('blob.retentionPolicy.enabled', True),
            JMESPathCheck('blob.retentionPolicy.days', 3)
        ])

        self.cmd('storage logging off --connection-string {}'.format(connection_string))

        self.cmd('storage logging show --connection-string {}'.format(connection_string), checks=[
            JMESPathCheck('blob.delete', False),
            JMESPathCheck('blob.write', False),
            JMESPathCheck('blob.read', False),
            JMESPathCheck('blob.retentionPolicy.enabled', False),
            JMESPathCheck('blob.retentionPolicy.days', None),
            JMESPathCheck('queue.delete', False),
            JMESPathCheck('queue.write', False),
            JMESPathCheck('queue.read', False),
            JMESPathCheck('queue.retentionPolicy.enabled', False),
            JMESPathCheck('queue.retentionPolicy.days', None),
            JMESPathCheck('table.delete', False),
            JMESPathCheck('table.write', False),
            JMESPathCheck('table.read', False),
            JMESPathCheck('table.retentionPolicy.enabled', False),
            JMESPathCheck('table.retentionPolicy.days', None),
            JMESPathCheck('adls.delete', False),
            JMESPathCheck('adls.write', False),
            JMESPathCheck('adls.read', False),
            JMESPathCheck('adls.retentionPolicy.enabled', False),
            JMESPathCheck('adls.retentionPolicy.days', None),
        ])

        # Table service
        with self.assertRaisesRegexp(CLIError, "incorrect usage: for table service, the supported version for logging is `1.0`"):
            self.cmd('storage logging update --services t --log r --retention 1 '
                     '--version 2.0 --connection-string {}'.format(connection_string))

        # Set version to 1.0
        self.cmd('storage logging update --services t --log r --retention 1 --version 1.0 --connection-string {} '
                 .format(connection_string))
        import time
        time.sleep(120)
        self.cmd('storage logging show --connection-string {}'.format(connection_string), checks=[
            JMESPathCheck('table.version', '1.0'),
            JMESPathCheck('table.delete', False),
            JMESPathCheck('table.write', False),
            JMESPathCheck('table.read', True),
            JMESPathCheck('table.retentionPolicy.enabled', True),
            JMESPathCheck('table.retentionPolicy.days', 1)
        ])

        # Use default version
        self.cmd('storage logging update --services t --log r --retention 1 --connection-string {}'.format(
            connection_string))
        import time
        time.sleep(120)
        self.cmd('storage logging show --connection-string {}'.format(connection_string), checks=[
            JMESPathCheck('table.version', '1.0'),
            JMESPathCheck('table.delete', False),
            JMESPathCheck('table.write', False),
            JMESPathCheck('table.read', True),
            JMESPathCheck('table.retentionPolicy.enabled', True),
            JMESPathCheck('table.retentionPolicy.days', 1)
        ])


    @live_only()
    @ResourceGroupPreparer()
    def test_logging_error_operations(self, resource_group):
        # BlobStorage doesn't support logging for some services
        blob_storage = self.create_random_name(prefix='blob', length=24)
        self.cmd('storage account create -g {} -n {} --kind BlobStorage --access-tier hot --https-only'.format(
            resource_group, blob_storage))

        blob_connection_string = self.cmd(
            'storage account show-connection-string -g {} -n {} -otsv'.format(resource_group, blob_storage)).output
        with self.assertRaisesRegexp(CLIError, "Your storage account doesn't support logging"):
            self.cmd('storage logging show --services q --connection-string {}'.format(blob_connection_string))

        # PremiumStorage doesn't support logging for some services
        premium_storage = self.create_random_name(prefix='premium', length=24)
        self.cmd('storage account create -g {} -n {} --sku Premium_LRS --https-only'.format(
            resource_group, premium_storage))

        premium_connection_string = self.cmd(
            'storage account show-connection-string -g {} -n {} -otsv'.format(resource_group, premium_storage)).output
        with self.assertRaisesRegexp(CLIError, "Your storage account doesn't support logging"):
            self.cmd('storage logging show --services q --connection-string {}'.format(premium_connection_string))
