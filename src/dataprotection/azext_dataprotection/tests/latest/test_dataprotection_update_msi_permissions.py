# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer, live_only
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
import time


def create_vault_and_policy(test):
    backup_vault = test.cmd('az dataprotection backup-vault create '
                            '-g "{rg}" --vault-name "{vaultName}" -l {location} '
                            '--storage-settings datastore-type="VaultStore" type="LocallyRedundant" --type SystemAssigned '
                            '--soft-delete-state Off',
                            checks=[
                                test.exists('identity.principalId')
                            ]).get_output_in_json()

    # Fix for 'Cannot find user or service principal in graph database' error. Confirming sp is created for the backup vault.
    sp_list = []
    while backup_vault['identity']['principalId'] not in sp_list:
        sp_list = test.cmd('az ad sp list --display-name "{vaultName}" --query [].id').get_output_in_json()
        time.sleep(10)

    policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type "{dataSourceType}"').get_output_in_json()
    test.kwargs.update({"policy": policy_json})

    policy = test.cmd('az dataprotection backup-policy create -n "{policyName}" --policy "{policy}" -g "{rg}" --vault-name "{vaultName}"').get_output_in_json()
    test.kwargs.update({"policyId": policy['id']})


class UpdateMSIPermissionsScenarioTest(ScenarioTest):

    @live_only()
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='clitest-dpp-updatemsipermissions-', location='centraluseuap')
    def test_dataprotection_update_msi_permissions_disk(test):
        test.kwargs.update({
            'location': 'centraluseuap',
            'vaultName': "clitest-bkp-vault",
            'policyName': 'diskpolicy',
            'dataSourceType': 'AzureDisk',
            'diskId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.Compute/disks/clitest-disk-donotdelete',
            'operation': "Backup",
            'permissionsScope': "Resource"
        })
        create_vault_and_policy(test)
        backup_instance_json = test.cmd('az dataprotection backup-instance initialize --datasource-type "{dataSourceType}" '
                                        '-l {location} --policy-id "{policyId}" --datasource-id "{diskId}" --snapshot-rg "{rg}" --tags Owner=dppclitest').get_output_in_json()
        test.kwargs.update({
            "backupInstance": backup_instance_json,
        })
        test.cmd('az dataprotection backup-instance update-msi-permissions '
                 '-g "{rg}" --vault-name "{vaultName}" '
                 '--datasource-type "{dataSourceType}" '
                 '--operation "{operation}" '
                 '--permissions-scope "{permissionsScope}" '
                 '--backup-instance "{backupInstance}" --yes')
        # time.sleep(10)

    @live_only()
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='clitest-dpp-updatemsipermissions-', location='centraluseuap')
    def test_dataprotection_update_msi_permissions_oss(test):
        test.kwargs.update({
            'location': 'centraluseuap',
            'vaultName': "clitest-bkp-vault",
            'policyName': 'osspolicy',
            'dataSourceType': 'AzureDatabaseForPostgreSQL',
            'secretStoreType': 'AzureKeyVault',
            'permissionsScope': 'ResourceGroup',
            'operation': 'Backup',
            "ossServer": "oss-clitest-server",
            "ossDb": "postgres",
            "ossDbId": "/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/oss-clitest-rg/providers/Microsoft.DBforPostgreSQL/servers/oss-clitest-server/databases/postgres",
            "secretStoreUri": "https://oss-clitest-keyvault.vault.azure.net/secrets/oss-clitest-secret",
            "keyVaultId": "/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/oss-clitest-rg/providers/Microsoft.KeyVault/vaults/oss-clitest-keyvault"
        })
        create_vault_and_policy(test)
        backup_instance_guid = "faec6818-0720-11ec-bd1b-c8f750f92764"
        backup_instance_json = test.cmd('az dataprotection backup-instance initialize --datasource-type "{dataSourceType}" '
                                        '-l "{location}" --policy-id "{policyId}" --datasource-id "{ossDbId}" --secret-store-type "{secretStoreType}" --secret-store-uri "{secretStoreUri}"').get_output_in_json()
        backup_instance_json["backup_instance_name"] = test.kwargs['ossServer'] + "-" + test.kwargs['ossDb'] + "-" + backup_instance_guid
        test.kwargs.update({
            "backupInstance": backup_instance_json,
            "backupInstanceName": backup_instance_json["backup_instance_name"]
        })

        test.cmd('az dataprotection backup-instance update-msi-permissions '
                 '-g "{rg}" '
                 '--vault-name "{vaultName}" '
                 '--backup-instance "{backupInstance}" '
                 '--datasource-type "{dataSourceType}" '
                 '--permissions-scope "{permissionsScope}" '
                 '--operation "{operation}" '
                 '--keyvault-id "{keyVaultId}" --yes')
        # time.sleep(10)

    @live_only()
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='clitest-dpp-updatemsipermissions-', location='eastus2euap')
    def test_dataprotection_update_msi_permissions_aks(test):
        test.kwargs.update({
            'location': 'eastus2euap',
            'vaultName': 'clitest-bkp-vault',
            'policyName': 'akspolicy',
            'dataSourceType': 'AzureKubernetesService',
            'aksClusterId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/oss-clitest-rg/providers/Microsoft.ContainerService/managedClusters/clitest-cluster1-donotdelete',
            'operation': 'Backup',
            'permissionsScope': 'ResourceGroup',
            'friendlyName': 'clitest-aks-friendly'
        })
        create_vault_and_policy(test)
        backup_config_json = test.cmd('az dataprotection backup-instance initialize-backupconfig --datasource-type AzureKubernetesService', checks=[
            test.check('include_cluster_scope_resources', True),
            test.check('snapshot_volumes', True)
        ]).get_output_in_json()
        test.kwargs.update({
            "backupConfig": backup_config_json
        })
        backup_instance_json = test.cmd('az dataprotection backup-instance initialize '
                                        '--datasource-id "{aksClusterId}" '
                                        '--datasource-location "{location}" '
                                        '--datasource-type "{dataSourceType}" '
                                        '--policy-id "{policyId}" '
                                        '--backup-configuration "{backupConfig}" '
                                        '--friendly-name "{friendlyName}" '
                                        '--snapshot-resource-group-name "{rg}"').get_output_in_json()
        test.kwargs.update({
            "backupInstance": backup_instance_json,
        })
        test.cmd('az dataprotection backup-instance update-msi-permissions '
                 '-g "{rg}" --vault-name "{vaultName}" '
                 '--datasource-type "{dataSourceType}" '
                 '--operation "{operation}" '
                 '--permissions-scope "{permissionsScope}" '
                 '--backup-instance "{backupInstance}" --yes')
        # time.sleep(10)
