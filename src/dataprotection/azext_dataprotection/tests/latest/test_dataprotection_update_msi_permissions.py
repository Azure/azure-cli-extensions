# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import
# WARNING: This test only works when run in the devbox.

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer, live_only
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
import unittest
import time


def create_vault_and_policy(test, useSystemAssigned=True):
    if useSystemAssigned:
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
    else:
        backup_vault = test.cmd('az dataprotection backup-vault create '
                                '-g "{rg}" --vault-name "{vaultName}" -l {location} '
                                '--storage-settings datastore-type="VaultStore" type="LocallyRedundant" --type UserAssigned '
                                '--uami {uamiUrl} '
                                '--soft-delete-state Off',
                                checks=[
                                    test.exists('identity.userAssignedIdentities')
                                ]).get_output_in_json()

        # Fix for 'Cannot find user or service principal in graph database' error. Confirming sp is created for the backup vault.
        sp_list = []
        while backup_vault['identity']['userAssignedIdentities']['{uamiUrl}']['principalId'] not in sp_list:
            sp_list = test.cmd('az ad sp list --display-name "{vaultName}" --query [].id').get_output_in_json()
            time.sleep(10)

    policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type "{dataSourceType}"').get_output_in_json()
    test.kwargs.update({"policy": policy_json})

    policy = test.cmd('az dataprotection backup-policy create -n "{policyName}" --policy "{policy}" -g "{rg}" --vault-name "{vaultName}"').get_output_in_json()
    test.kwargs.update({"policyId": policy['id']})


class UpdateMSIPermissionsScenarioTest(ScenarioTest):

    # Regression scaffold for the AzureElasticSAN backup permissions path in
    # custom.py::dataprotection_backup_instance_update_msi_permissions, which assigns
    # Elastic SAN Snapshot Exporter (data source) + Disk Snapshot Contributor (snapshot RG)
    # from Manifests/AzureElasticSAN.py::backupVaultPermissions.
    # Enable once a stable eSAN live test environment is available.
    @unittest.skip("Requires dedicated live Azure Elastic SAN backup/restore test environment.")
    @live_only()
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='clitest-dpp-updatemsipermissions-', location='eastus2euap')
    def test_dataprotection_update_msi_permissions_esan_backup(test):
        test.kwargs.update({
            'location': 'eastus2euap',
            'vaultName': 'clitest-bkp-vault',
            'policyName': 'esanpolicy',
            'dataSourceType': 'AzureElasticSAN',
            'operation': 'Backup',
            'permissionsScope': 'Resource',
            'volumeGroupId': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/esan-rg/providers/Microsoft.ElasticSan/elasticSans/esan1/volumeGroups/vg1',
            'friendlyName': 'clitest-esan-friendly',
            'resourceSelector': 'source-vol-1',
        })
        create_vault_and_policy(test)

        backup_config_json = test.cmd('az dataprotection backup-instance initialize-backupconfig '
                                      '--datasource-type "{dataSourceType}" '
                                      '--resource-selectors "{resourceSelector}"').get_output_in_json()
        test.kwargs.update({
            "backupConfig": backup_config_json,
        })

        backup_instance_json = test.cmd('az dataprotection backup-instance initialize '
                                        '--datasource-id "{volumeGroupId}" '
                                        '--datasource-location "{location}" '
                                        '--datasource-type "{dataSourceType}" '
                                        '--policy-id "{policyId}" '
                                        '--backup-configuration "{backupConfig}" '
                                        '--friendly-name "{friendlyName}"').get_output_in_json()
        test.kwargs.update({
            "backupInstance": backup_instance_json,
        })

        test.cmd('az dataprotection backup-instance update-msi-permissions '
                 '-g "{rg}" --vault-name "{vaultName}" '
                 '--datasource-type "{dataSourceType}" '
                 '--operation "{operation}" '
                 '--permissions-scope "{permissionsScope}" '
                 '--backup-instance "{backupInstance}" --yes')

    # This is a regression scaffold for the AzureElasticSAN restore allow-list path in
    # custom.py::dataprotection_backup_instance_update_msi_permissions.
    # Enable once a stable eSAN live test environment is available.
    @unittest.skip("Requires dedicated live Azure Elastic SAN backup/restore test environment.")
    @live_only()
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='clitest-dpp-updatemsipermissions-', location='eastus2euap')
    def test_dataprotection_update_msi_permissions_esan_restore(test):
        test.kwargs.update({
            'location': 'eastus2euap',
            'vaultName': 'clitest-bkp-vault',
            'policyName': 'esanpolicy',
            'dataSourceType': 'AzureElasticSAN',
            'operation': 'Restore',
            'permissionsScope': 'Resource',
            'sourceDataStore': 'OperationalStore',
            'recoveryPointId': 'dummy-recovery-point-id',
            'targetVolumeGroupId': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/esan-rg/providers/Microsoft.ElasticSan/elasticSans/esan1/volumeGroups/vg1',
            'snapshotRgId': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/esan-snapshot-rg',
            'restoreConfig': '{"object_type":"GenericRestoreDatasourceCriteria","resource_selectors":{"object_type":"ResourceListSelectionCriteria","resource_identifiers":["source-vol-1"],"resource_name_overrides":{"source-vol-1":"target-vol-1"}}}',
        })
        create_vault_and_policy(test)

        restore_request_json = test.cmd('az dataprotection backup-instance restore initialize-for-item-recovery '
                                        '--datasource-type "{dataSourceType}" '
                                        '--restore-location "{location}" '
                                        '--source-datastore "{sourceDataStore}" '
                                        '--recovery-point-id "{recoveryPointId}" '
                                        '--target-resource-id "{targetVolumeGroupId}" '
                                        '--mi-system-assigned true '
                                        '--restore-configuration "{restoreConfig}"').get_output_in_json()
        test.kwargs.update({
            "restoreRequest": restore_request_json,
        })

        test.cmd('az dataprotection backup-instance update-msi-permissions '
                 '-g "{rg}" --vault-name "{vaultName}" '
                 '--datasource-type "{dataSourceType}" '
                 '--operation "{operation}" '
                 '--permissions-scope "{permissionsScope}" '
                 '--snapshot-resource-group-id "{snapshotRgId}" '
                 '--restore-request-object "{restoreRequest}" --yes')

    @live_only()
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='clitest-dpp-updatemsipermissions-', location='centraluseuap')
    def test_dataprotection_update_msi_permissions_disk_uami(test):
        test.kwargs.update({
            'location': 'centraluseuap',
            'vaultName': "clitest-bkp-vault",
            'policyName': 'diskpolicy',
            'dataSourceType': 'AzureDisk',
            'diskId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.Compute/disks/clitest-disk-donotdelete',
            'operation': "Backup",
            'permissionsScope': "Resource",
            'uamiUrl': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/dppcliuamiccy'
        })
        create_vault_and_policy(test, useSystemAssigned=False)
        backup_instance_json = test.cmd('az dataprotection backup-instance initialize --datasource-type "{dataSourceType}" '
                                        '-l {location} --policy-id "{policyId}" --datasource-id "{diskId}" --snapshot-rg "{rg}" '
                                        '--uami {uamiUrl} --tags Owner=dppclitest').get_output_in_json()
        test.kwargs.update({
            "backupInstance": backup_instance_json,
        })
        test.cmd('az dataprotection backup-instance update-msi-permissions '
                 '-g "{rg}" --vault-name "{vaultName}" '
                 '--datasource-type "{dataSourceType}" '
                 '--operation "{operation}" '
                 '--permissions-scope "{permissionsScope}" '
                 '--uami "{uamiUrl}" '
                 '--backup-instance "{backupInstance}" --yes')
        # time.sleep(10)

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

    # Uses persistent Cosmos DB accounts pre-provisioned in cosmos-bugbash-CLIrg-6 (subscription
    # 97cda027-4279-4cde-b4ff-19afa0021d87). The test provisions a fresh backup vault in a
    # ResourceGroupPreparer-managed RG and exercises update-msi-permissions for the AzureCosmosDB
    # workload, which assigns Reader on the data source RG and Cosmos DB Operator on the data source
    # (see Manifests/AzureCosmosDB.py::backupVaultPermissions).
    @live_only()
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='clitest-dpp-updatemsipermissions-', location='eastus2euap')
    def test_dataprotection_update_msi_permissions_cosmosdb(test):
        test.kwargs.update({
            'location': 'eastus2euap',
            'vaultName': 'clitest-bkp-vault',
            'policyName': 'cosmospolicy',
            'dataSourceType': 'AzureCosmosDB',
            'operation': 'Backup',
            'permissionsScope': 'ResourceGroup',
            'cosmosDbName': 'cosmosbugbash-cli6-src',
            'cosmosDbId': '/subscriptions/97cda027-4279-4cde-b4ff-19afa0021d87/resourceGroups/cosmos-bugbash-CLIrg-6/providers/Microsoft.DocumentDB/databaseAccounts/cosmosbugbash-cli6-src',
        })
        create_vault_and_policy(test)

        backup_instance_guid = "faec6818-0720-11ec-bd1b-c8f750f92764"
        backup_instance_json = test.cmd('az dataprotection backup-instance initialize --datasource-type "{dataSourceType}" '
                                        '-l "{location}" --policy-id "{policyId}" --datasource-id "{cosmosDbId}"').get_output_in_json()
        backup_instance_json["backup_instance_name"] = (test.kwargs['cosmosDbName'] + "-" +
                                                       test.kwargs['cosmosDbName'] + "-" +
                                                       backup_instance_guid)
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

    # Uses persistent Cosmos DB accounts pre-provisioned in cosmos-bugbash-CLIrg-6 (subscription
    # 97cda027-4279-4cde-b4ff-19afa0021d87). The test provisions a fresh backup vault in a
    # ResourceGroupPreparer-managed RG and exercises update-msi-permissions --operation Restore
    # for the AzureCosmosDB workload, which assigns Cosmos DB Operator on the target Cosmos DB
    # account (see Manifests/AzureCosmosDB.py::backupVaultRestorePermissions). This is the
    # regression test for the fix that adds AzureCosmosDB to the Restore allow-list in
    # custom.py::dataprotection_backup_instance_update_msi_permissions.
    @live_only()
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='clitest-dpp-updatemsipermissions-', location='eastus2euap')
    def test_dataprotection_update_msi_permissions_cosmosdb_restore(test):
        test.kwargs.update({
            'location': 'eastus2euap',
            'vaultName': 'clitest-bkp-vault',
            'policyName': 'cosmospolicy',
            'dataSourceType': 'AzureCosmosDB',
            'operation': 'Restore',
            'permissionsScope': 'Resource',
            'sourceDataStore': 'VaultStore',
            'recoveryPointId': 'dummy-recovery-point-id',
            'targetCosmosDbId': '/subscriptions/97cda027-4279-4cde-b4ff-19afa0021d87/resourceGroups/cosmos-bugbash-CLIrg-6/providers/Microsoft.DocumentDB/databaseAccounts/cosmosbugbash-cli6-tgt',
        })
        create_vault_and_policy(test)

        restore_request_json = test.cmd('az dataprotection backup-instance restore initialize-for-data-recovery '
                                        '--datasource-type "{dataSourceType}" '
                                        '--restore-location "{location}" '
                                        '--source-datastore "{sourceDataStore}" '
                                        '--recovery-point-id "{recoveryPointId}" '
                                        '--target-resource-id "{targetCosmosDbId}"').get_output_in_json()
        test.kwargs.update({
            "restoreRequest": restore_request_json,
        })

        test.cmd('az dataprotection backup-instance update-msi-permissions '
                 '-g "{rg}" --vault-name "{vaultName}" '
                 '--datasource-type "{dataSourceType}" '
                 '--operation "{operation}" '
                 '--permissions-scope "{permissionsScope}" '
                 '--restore-request-object "{restoreRequest}" --yes')
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
