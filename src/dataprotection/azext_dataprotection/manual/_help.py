# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines

from knack.help_files import helps

helps['dataprotection job list-from-resourcegraph'] = """
    type: command
    short-summary: List backup jobs across subscriptions, resource groups and vaults.
    examples:
      - name: Get backup jobs across all resource groups in current subscription which have been completed
        text: az dataprotection job list-from-resourcegraph --datasource-type AzureDisk --status Completed
      - name: Get backup jobs in a given set of vaults and in a given timerange
        text: az dataprotection job list-from-resourcegraph --datasource-type AzureDisk --vaults MyVault1 MyVault2 --start-time 2020-11-11T01:01:00 --end-time 2020-11-14T01:01:00
"""

helps['dataprotection backup-instance initialize'] = """
    type: command
    short-summary: Initialize JSON request body for configuring backup of a resource.
    examples:
      - name: Initialize backup instance request for Azure Disk
        text: az dataprotection backup-instance initialize --datasource-type AzureDisk -l southeastasia --policy-id {disk_policy_id} --datasource-id {disk_id}
"""

helps['dataprotection backup-instance update-policy'] = """
    type: command
    short-summary: Update backup policy associated with backup instance.
    examples:
      - name: Update backup policy associated with backup instance
        text: az dataprotection backup-instance update-policy --backup-instance-name MyDisk1 --policy-id {policy_id} -g MyResourceGroup --vault-name MyVault
"""

helps['dataprotection backup-instance list-from-resourcegraph'] = """
    type: command
    short-summary: List backup instances across subscriptions, resource groups and vaults.
    examples:
      - name: list backup instances across multiple vaults across multiple resource groups
        text: az dataprotection backup-instance list-from-resourcegraph --resource-groups resourceGroup1 resourceGroup2 --vaults vault1 vault2 --datasource-type AzureBlob
      - name: list backup instances in a vault which are in a protection error state.
        text: az dataprotection backup-instance list-from-resourcegraph --resource-groups resourceGroup --vaults vault --protection-status ProtectionError --datasource-type AzureDisk
"""

helps['dataprotection backup-instance update-msi-permissions'] = """
    type: command
    short-summary: Assign the required permissions needed to successfully enable backup for the datasource.
    examples:
      - name: Assign the required permissions needed to successfully enable backup for the datasource.
        text: az dataprotection backup-instance update-msi-permissions --backup-instance backup_inst.json --resource-group samarth_resource_group --vault-name samarthbackupvault --datasource-type AzureDisk --operation Backup --permissions-scope ResourceGroup
      - name: Assign the required permissions needed to successfully enable restore for the datasource.
        text: az dataprotection backup-instance update-msi-permissions --datasource-type AzureKubernetesService --operation Restore --permissions-scope Resource --resource-group sampleRG --vault-name samplevault --restore-request-object aksrestore.json --snapshot-resource-group-id /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sampleRG
"""

helps['dataprotection backup-policy get-default-policy-template'] = """
    type: command
    short-summary: Get default policy template for a given datasource type.
    examples:
      - name: Get default policy template for Azure Disk
        text: az dataprotection backup-policy get-default-policy-template --datasource-type AzureDisk
"""

helps['dataprotection backup-policy trigger'] = """
    type: group
    short-summary: Manage backup schedule of a backup policy.
"""

helps['dataprotection backup-policy trigger create-schedule'] = """
    type: command
    short-summary: create backup schedule of a policy.
    examples:
      - name: create weekly backup schedule where backup is taken twice a week.
        text: az dataprotection backup-policy trigger create-schedule --interval-type Weekly --interval-count 1 --schedule-days 2021-05-02T05:30:00 2021-05-03T05:30:00
      - name: create hourly backup schedule where backup frequency is every 4 hours
        text: az dataprotection backup-policy trigger create-schedule --interval-type Hourly --interval-count 6 --schedule-days 2021-05-02T05:30:00
"""

helps['dataprotection backup-policy trigger set'] = """
    type: command
    short-summary: Associate backup schedule to a backup policy.
    examples:
      - name: associate daily backup schedule
        text: az dataprotection backup-policy trigger set --policy policy.json --schedule R/2021-05-02T05:30:00+00:00/P1D
"""

helps['dataprotection backup-policy retention-rule'] = """
    type: group
    short-summary: Create lifecycles and add or remove retention rules in a backup policy.
"""

helps['dataprotection backup-policy retention-rule create-lifecycle'] = """
    type: command
    short-summary: Create lifecycle for Azure Retention rule.
    examples:
      - name: create daily lifecycle
        text: az dataprotection backup-policy retention-rule create-lifecycle --retention-duration-count 12 --retention-duration-type Days --source-datastore OperationalStore
"""

helps['dataprotection backup-policy retention-rule set'] = """
    type: command
    short-summary: Add new retention rule or update existing retention rule.
    examples:
      - name: Add daily retention rule
        text: az dataprotection backup-policy retention-rule set --lifecycles dailylifecycle.json --name Daily --policy policy.json
"""

helps['dataprotection backup-policy retention-rule remove'] = """
    type: command
    short-summary: remove existing retention rule in a backup policy
    examples:
      - name: Remove retention rule
        text: az dataprotection backup-policy retention-rule remove --name Daily --policy policy.json
"""

helps['dataprotection backup-policy tag'] = """
    type: group
    short-summary: Create criterias and add or remove tag in policy.
"""

helps['dataprotection backup-policy tag create-absolute-criteria'] = """
    type: command
    short-summary: Create absolute criteria.
    examples:
      - name: create absolute criteria
        text: az dataprotection backup-policy tag create-absolute-criteria --absolute-criteria FirstOfDay
"""

helps['dataprotection backup-policy tag create-generic-criteria'] = """
    type: command
    short-summary: create generic criteria
    examples:
      - name: Create generic criteria
        text: az dataprotection backup-policy tag create-generic-criteria --days-of-week Sunday Monday
"""

helps['dataprotection backup-policy tag set'] = """
    type: command
    short-summary: Add new tag or update existing tag of a backup policy.
    examples:
      - name: Add tag for daily retention in a backup policy.
        text: az dataprotection backup-policy tag set --criteria criteria.json --name Daily --policy policy.json
"""

helps['dataprotection backup-policy tag remove'] = """
    type: command
    short-summary: Remove existing tag from a backup policy.
    examples:
      - name: Remove daily tag.
        text: az dataprotection backup-policy tag remove --name Daily --policy policy.json
"""

helps['dataprotection backup-instance restore initialize-for-data-recovery'] = """
    type: command
    short-summary: Initialize restore request object to recover all backed up data in a backup vault.
    examples:
      - name: initialize restore request for azure disk backup instance
        text: az dataprotection backup-instance restore initialize-for-data-recovery --datasource-type AzureDisk --restore-location centraluseuap --source-datastore OperationalStore --target-resource-id {restore_disk_id} --recovery-point-id b7e6f082-b310-11eb-8f55-9cfce85d4fae
"""

helps['dataprotection backup-instance restore initialize-for-data-recovery-as-files'] = """
    type: command
    short-summary: Initialize restore request object to recover all backed up data as files in a backup vault.
    examples:
      - name: initialize restore request for azure database as files for postgresql server backup instance
        text: az dataprotection backup-instance restore initialize-for-data-recovery-as-files --datasource-type AzureDatabaseForPostgreSQL --restore-location centraluseuap --source-datastore VaultStore --target-blob-container-url {target_blob_container_url} --target-file-name {target_file_name} --recovery-point-id 9a4ab128e2d441d6a575ecd85903bd81
"""

helps['dataprotection backup-instance restore initialize-for-item-recovery'] = """
    type: command
    short-summary: Initialize restore request object to recover specified items of backed up data in a backup vault.
    examples:
      - name: initialize restore request for azure blob backup instance
        text: az dataprotection backup-instance restore initialize-for-item-recovery --datasource-type AzureBlob --restore-location centraluseuap --source-datastore OperationalStore --backup-instance-id {backup_instance_id}  --point-in-time 2021-05-26T15:00:00 --container-list container1 container2
"""

helps['dataprotection resource-guard list-protected-operations'] = """
    type: command
    short-summary:  Lists protected operations associated with a ResourceGuard.
    examples:
      - name: List ResourceGuard protected operations
        text: az dataprotection resource-guard list-protected-operations --resource-group "SampleResourceGroup" --resource-guard-name "swaggerExample" --resource-type "Microsoft.RecoveryServices/vaults"
"""

helps['dataprotection backup-instance initialize-backupconfig'] = """
    type: command
    short-summary: Initialize JSON request body for initializing and configuring backup of an AzureKubernetesService resource.
    examples:
      - name: Initialize backup configuration
        text: az dataprotection backup-instance initialize-backupconfig --datasource-type AzureKubernetesService --label-selectors key=val foo=bar --excluded-namespaces excludeNS1 excludeNS2
"""

helps['dataprotection backup-instance initialize-restoreconfig'] = """
    type: command
    short-summary: Initialize JSON request body for initializing and configuring restore of an AzureKubernetesService resource.
    examples:
      - name: Initialize restore configuration
        text: az dataprotection backup-instance initialize-restoreconfig --datasource-type AzureKubernetesService
"""

helps['dataprotection backup-instance validate-for-backup'] = """
    type: command
    short-summary: Validate whether configure backup will be successful or not.
    examples:
      - name: Validate for backup
        text: az dataprotection backup-instance validate-for-backup -g sarath-rg --vault-name sarath-vault --backup-instance backup_instance.json
"""

helps['dataprotection backup-instance restore trigger'] = """
    type: command
    short-summary: Triggers restore for a BackupInstance.
    examples:
      - name: Trigger a restore operation
        text: az dataprotection backup-instance restore trigger -g sample_rg --vault-name sample_backupvault --backup-instance-name sample_biname-fd53a211-3f3e-4c7e-ba45-81050e27c0be  --restore-request-object restorerequestobject.json
      - name: Trigger a cross-region-restore operation
        text: az dataprotection backup-instance restore trigger -g sample_rg --vault-name sample_backupvault --backup-instance-name sample_biname-fd53a211-3f3e-4c7e-ba45-81050e27c0be  --restore-request-object restorerequestobject.json --use-secondary-region
"""

helps['dataprotection backup-instance validate-for-restore'] = """
    type: command
    short-summary: Validates if Restore can be triggered for a DataSource.
    examples:
      - name: Validate for restore
        text: az dataprotection backup-instance validate-for-restore -g sample_rg --vault-name sample_backupvault --backup-instance-name sample_biname-fd53a211-3f3e-4c7e-ba45-81050e27c0be --restore-request-object restorerequestobject.json
      - name: Validate for cross-region-restore
        text: az dataprotection backup-instance validate-for-restore -g sample_rg --vault-name sample_backupvault --backup-instance-name sample_biname-fd53a211-3f3e-4c7e-ba45-81050e27c0be --restore-request-object restorerequestobject.json --use-secondary-region
"""

helps['dataprotection backup-vault list-from-resourcegraph'] = """
    type: command
    short-summary: List backup vaults across subscriptions, resource groups and vaults.
    examples:
      - name: Fetch a specific backup vault
        text: az dataprotection backup-vault list-from-resourcegraph --subscriptions 00000000-0000-0000-0000-000000000000 --resource-groups sample_rg --vaults sample_vault
"""

helps['dataprotection job show'] = """
    type: command
    short-summary: Get a job with id in a backup vault.
    examples:
      - name: Get Job
        text: az dataprotection job show --job-id "00000000-0000-0000-0000-000000000000" --resource-group "BugBash1" --vault-name "BugBashVaultForCCYv11"
"""

helps['dataprotection job list'] = """
    type: command
    short-summary: Returns list of jobs belonging to a backup vault.
    examples:
      - name: Get Jobs
        text: az dataprotection job list --resource-group "BugBash1" --vault-name "BugBashVaultForCCYv11"
"""

helps['dataprotection recovery-point list'] = """
    type: command
    short-summary: Returns a list of Recovery Points for a DataSource in a vault.
    examples:
      - name: List of Recovery Points in a Vault
        text: az dataprotection recovery-point list --backup-instance-name "sample_biname-00000000-0000-0000-0000-000000000000" --resource-group "sample_rg" --vault-name "sample_vault"
"""
