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

    @AllowLargeResponse()
    def test_dataprotection_deleted_vault_operations(test):
        # 1. Create a Backup Vault
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

        # Configure the required permissions for the Backup Instance
        test.cmd('az dataprotection backup-instance update-msi-permissions '
                 '-g "{rg}" --vault-name "{vaultName}" '
                 '--datasource-type "{dataSourceType}" '
                 '--operation "{operation}" '
                 '--permissions-scope "{permissionsScope}" '
                 '--backup-instance "{backupInstanceJson}" --yes')
        import time
        time.sleep(30)  # Wait for a while to allow permissions to propagate

        # Adding backup-instance delete as the cleanup command, will always run even if test fails.
        test.addCleanup(test.cmd, 'az dataprotection backup-instance delete -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --yes --no-wait')
        test.cmd('az dataprotection backup-instance create -g "{rg}" --vault-name "{vaultName}" --backup-instance "{backupInstanceJson}"',
                 checks=[
                     test.exists('id')
                 ])

        # 3. Delete Backup Instance
        test.cmd('az dataprotection backup-instance delete -g "{rg}" --vault-name "{vaultName}" --name "{backupInstanceName}" -y')

        # 4. Delete Backup Vault
        test.cmd('az dataprotection backup-vault delete -g "{rg}" --vault-name "{vaultName}" -y')

        # 5. List deleted Backup Vaults
        # Verify our vault is in the list. The list returns DeletedBackupVaultResource where name is a GUID, so check originalBackupVaultName.
        test.cmd('az dataprotection backup-vault deleted-vault list -l "{location}"', checks=[
            test.check("length([?properties.originalBackupVaultName == '{vaultName}'])", 1)
        ])

        # Get the deleted vault info
        deleted_vaults = test.cmd('az dataprotection backup-vault deleted-vault list -l "{location}"').get_output_in_json()
        target_vault = next(v for v in deleted_vaults if v['properties']['originalBackupVaultName'] == test.kwargs['vaultName'])
        test.kwargs.update({
            'deletedVaultId': target_vault['id'],
            'deletedVaultName': target_vault['name']
        })

        # 6. Show deleted Backup Vault
        # Show uses the name (GUID) of the deleted vault
        test.cmd('az dataprotection backup-vault deleted-vault show -n "{deletedVaultName}" -l "{location}"', checks=[
             test.check('properties.originalBackupVaultName', "{vaultName}")
        ])
        
        # 7. List Backup Instances in Deleted Vault
        # This command expects the full ID as per the alias --deleted-vault-id
        test.cmd('az dataprotection backup-vault deleted-vault list-deleted-backup-instances --deleted-vault-id "{deletedVaultId}"', checks=[
            test.greater_than("length([])", 0),
            test.check("[0].properties.dataSourceInfo.dataSourceId", "{dataSourceId}")
        ])

        # 8. Undelete Backup Vault
        # Undelete expects the full ID
        test.cmd('az dataprotection backup-vault deleted-vault undelete -g "{rg}" --vault-name "{vaultName}" --deleted-vault-id "{deletedVaultId}"', checks=[
            test.check('name', "{vaultName}"),
            test.check('properties.provisioningState', "Succeeded")
        ])

        # 9. Add System Identity to Vault
        test.cmd('az dataprotection backup-vault update -g "{rg}" -v "{vaultName}" --type SystemAssigned', checks=[
            test.check('identity.type', "SystemAssigned")
        ])

        # 9.5 Configure the required permissions for the Backup Instance
        test.cmd('az dataprotection backup-instance update-msi-permissions '
                 '-g "{rg}" --vault-name "{vaultName}" '
                 '--datasource-type "{dataSourceType}" '
                 '--operation "{operation}" '
                 '--permissions-scope "{permissionsScope}" '
                 '--backup-instance "{backupInstanceJson}" --yes')
        import time
        time.sleep(30)  # Wait for a while to allow permissions to propagate

        # 10. Undelete (Reprotect) Backup Instance
        test.cmd('az dataprotection backup-instance resume-protection -g "{rg}" -v "{vaultName}" -n "{backupInstanceName}"')

        # Cleanup: Delete Backup Instance again
        test.cmd('az dataprotection backup-instance delete -g "{rg}" --vault-name "{vaultName}" --name "{createdBackupInstanceName}" -y')

        # Cleanup: Delete vault again (this time for real, eventually)
        test.cmd('az dataprotection backup-vault delete -g "{rg}" --vault-name "{vaultName}" -y')
