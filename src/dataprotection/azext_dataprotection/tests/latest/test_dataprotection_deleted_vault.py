# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import

import json
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


class DeletedVaultScenarioTest(ScenarioTest):

    def setUp(test):
        super().setUp()
        test.kwargs.update({
            'location': 'centraluseuap',
            'vaultName': 'cli-test-deleted-vault',
            'rg': 'clitest-dpp-rg',
            'permissionsScope': 'Resource',
            'operation': 'Backup',
            'dataSourceType': 'AzureDisk',
            'dataSourceName': 'clitest-disk-softdeletetest-bi-donotdelete',
            'dataSourceId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.Compute/disks/clitest-disk-softdeletetest-bi-donotdelete',
            'policyName': 'cli-test-disk-policy'
        })

    @AllowLargeResponse(size_kb=4096)
    def test_dataprotection_deleted_vault_operations(test):
        # 1. Create a Backup Vault
        test.addCleanup(test.cmd, 'az dataprotection backup-vault delete -g "{rg}" --vault-name "{vaultName}" -y')
        test.cmd('az dataprotection backup-vault create '
                 '-g "{rg}" --vault-name "{vaultName}" -l "{location}" '
                 '--storage-settings datastore-type="VaultStore" type="LocallyRedundant" --type "SystemAssigned"',
                 checks=[
                     test.check('name', "{vaultName}"),
                     test.check('properties.securitySettings.softDeleteSettings.state', "AlwaysOn"),
                     test.check('properties.securitySettings.softDeleteSettings.retentionDurationInDays', 14.0)
                 ])

        # 1.5 Create Backup Policy
        policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type "{dataSourceType}"').get_output_in_json()
        test.kwargs.update({"policyJson": policy_json})
        
        policy = test.cmd('az dataprotection backup-policy create -n "{policyName}" --policy "{policyJson}" -g "{rg}" --vault-name "{vaultName}"').get_output_in_json()
        test.kwargs.update({"policyId": policy['id']})

        # 2. Configure Backup for a Disk (Create Backup Instance)
        # Using a managed disk as data source
        backup_instance_guid = "b7e6f082-b310-11eb-8f55-9cfce85d4fa1"
        backup_instance_json = test.cmd('az dataprotection backup-instance initialize --datasource-type "{dataSourceType}" '
                                        '-l "{location}" --policy-id "{policyId}" --datasource-id "{dataSourceId}" --snapshot-rg "{rg}" '
                                        '--tags Owner=dppclitest Purpose=Testing').get_output_in_json()
        backup_instance_json["backup_instance_name"] = test.kwargs['dataSourceName'] + "-" + test.kwargs['dataSourceName'] + "-" + backup_instance_guid
        test.kwargs.update({
            "backupInstanceJson": backup_instance_json,
            "backupInstanceName": backup_instance_json["backup_instance_name"]
        })

        # Configure the required permissions for the Backup Instance. Only for live tests
        import time
        # time.sleep(60) # Wait for MSI to propagate
        # test.cmd('az dataprotection backup-instance update-msi-permissions '
        #          '-g "{rg}" --vault-name "{vaultName}" '
        #          '--datasource-type "{dataSourceType}" '
        #          '--operation "{operation}" '
        #          '--permissions-scope "{permissionsScope}" '
        #          '--backup-instance "{backupInstanceJson}" --yes')
        # time.sleep(30)  # Wait for a while to allow permissions to propagate

        test.cmd('az dataprotection backup-instance create -g "{rg}" --vault-name "{vaultName}" --backup-instance "{backupInstanceJson}"',
                 checks=[
                     test.exists('id')
                 ])

        # Sleep to ensure backup instance is fully created before proceeding
        time.sleep(90)

        # 3. Delete Backup Instance
        test.cmd('az dataprotection backup-instance delete -g "{rg}" --vault-name "{vaultName}" --name "{backupInstanceName}" -y')

        # 4. Delete Backup Vault
        test.cmd('az dataprotection backup-vault delete -g "{rg}" --vault-name "{vaultName}" -y')
        
        # Wait for vault to appear in deleted vaults list
        time.sleep(30)

        # 5. List deleted Backup Vaults
        # Verify our vault is in the list. The list returns DeletedBackupVaultResource where name is a GUID, so check originalBackupVaultName.
        test.cmd('az dataprotection backup-vault deleted-vault list -l "{location}"', checks=[
            test.exists("[?properties.originalBackupVaultName == '{vaultName}'] | [0]")
        ])

        # Get the deleted vault info - select the most recently deleted one
        deleted_vaults = test.cmd('az dataprotection backup-vault deleted-vault list -l "{location}"').get_output_in_json()
        matching_vaults = [v for v in deleted_vaults if v['properties']['originalBackupVaultName'] == test.kwargs['vaultName']]
        target_vault = max(matching_vaults, key=lambda v: v['properties']['resourceDeletionInfo']['deletionTime'])
        test.kwargs.update({
            'deletedVaultName': target_vault['name']
        })

        # 6. Show deleted Backup Vault
        # Show uses the name (GUID) of the deleted vault
        test.cmd('az dataprotection backup-vault deleted-vault show -n "{deletedVaultName}" -l "{location}"', checks=[
             test.check('properties.originalBackupVaultName', "{vaultName}")
        ])
        
        # 7. List Backup Instances in Deleted Vault
        time.sleep(60)  # Wait for deleted backup instances to be indexed
        test.cmd('az dataprotection backup-vault deleted-vault list-deleted-backup-instances --deleted-vault-name "{deletedVaultName}"', checks=[
            test.greater_than("length([])", 0),
            test.check("[0].properties.dataSourceInfo.resourceName", "{dataSourceName}")
        ])

        # 8. Undelete Backup Vault
        test.cmd('az dataprotection backup-vault deleted-vault undelete -g "{rg}" --vault-name "{vaultName}" --deleted-vault-name "{deletedVaultName}"', checks=[
            test.check('name', "{vaultName}"),
            test.check('properties.provisioningState', "Succeeded")
        ])

        # 9. Add System Identity to Vault. Onlyt for live tests
        # test.cmd('az dataprotection backup-vault update -g "{rg}" -v "{vaultName}" --type SystemAssigned', checks=[
        #     test.check('identity.type', "SystemAssigned")
        # ])
        # time.sleep(30)  # Wait for new MSI to propagate to AAD after re-assigning identity

        # 9.5 Configure the required permissions for the Backup Instance. Only for live tests
        # test.cmd('az dataprotection backup-instance update-msi-permissions '
        #          '-g "{rg}" --vault-name "{vaultName}" '
        #          '--datasource-type "{dataSourceType}" '
        #          '--operation "{operation}" '
        #          '--permissions-scope "{permissionsScope}" '
        #          '--backup-instance "{backupInstanceJson}" --yes')
        # time.sleep(30)  # Wait for a while to allow permissions to propagate

        # 10. Undelete (Reprotect) Backup Instance
        test.cmd('az dataprotection backup-instance deleted-backup-instance undelete -g "{rg}" -v "{vaultName}" -n "{backupInstanceName}"')
        test.cmd('az dataprotection backup-instance resume-protection -g "{rg}" -v "{vaultName}" -n "{backupInstanceName}"')
        time.sleep(120)  # Wait longer for backup instance to fully stabilize after resuming protection

        # Cleanup: Delete Backup Instance again
        test.cmd('az dataprotection backup-instance delete -g "{rg}" --vault-name "{vaultName}" --name "{backupInstanceName}" -y')

        # Cleanup: Delete vault again (this time for real, eventually)
        # Note: The vault deletion will also clean up the associated backup policy
        test.cmd('az dataprotection backup-vault delete -g "{rg}" --vault-name "{vaultName}" -y')
