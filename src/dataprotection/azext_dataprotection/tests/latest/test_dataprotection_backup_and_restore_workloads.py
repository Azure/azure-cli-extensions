# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from datetime import datetime
from ..utils import track_job_to_completion, wait_for_job_exclusivity_on_datasource


def backup_instance_validate_create(test):
    # Adding backup-instance delete as the cleanup command, will always run even if test fails.
    test.addCleanup(test.cmd, 'az dataprotection backup-instance delete -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --yes --no-wait')

    # Ensure backup-instance deletion from prev run. If instance is already deleted, it will return instantly.
    test.cmd('az dataprotection backup-instance delete -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --yes')

    test.cmd('az dataprotection backup-instance validate-for-backup -g "{rg}" --vault-name "{vaultName}" --backup-instance "{backupInstance}"', checks=[
        test.check('objectType', 'OperationJobExtendedInfo')
    ])
    backup_instance = test.cmd('az dataprotection backup-instance create -g "{rg}" --vault-name "{vaultName}" --backup-instance "{backupInstance}"', checks=[
        test.check('properties.provisioningState', "Succeeded")
    ]).get_output_in_json()
    test.kwargs.update({
        'backupInstanceId': backup_instance['id']
    })

    test.cmd('az dataprotection backup-instance list -g "{rg}" --vault-name "{vaultName}"', checks=[
        test.exists("[?name == '{backupInstanceName}']")
    ])
    test.cmd('az dataprotection backup-instance show --ids "{backupInstanceId}"', checks=[
        test.check('name', "{backupInstanceName}")
    ])

    # Waiting for backup-instance configuration to complete. Adjust timeout if this fails for no other reason.
    test.cmd('az dataprotection backup-instance wait -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --timeout 120 '
             '--custom "properties.protectionStatus.status==\'ProtectionConfigured\'"')


class BackupAndRestoreScenarioTest(ScenarioTest):

    # Uses a persistent vault and DS
    @AllowLargeResponse()
    def test_dataprotection_backup_and_restore_oss(test):
        test.kwargs.update({
            'location': 'centraluseuap',
            'rg': 'clitest-dpp-rg',
            'vaultName': 'clitest-bkp-vault-donotdelete',
            'restoreLocation': 'centraluseuap',
            'dataSourceType': 'AzureDatabaseForPostgreSQL',
            'sourceDataStore': 'VaultStore',
            'secretStoreType': 'AzureKeyVault',
            'permissionsScope': 'ResourceGroup',
            'operation': 'Backup',
            'ossRg': "oss-clitest-rg",
            'ossServer': 'oss-clitest-server',
            'ossDb': 'postgres',
            'ossDbId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/oss-clitest-rg/providers/Microsoft.DBforPostgreSQL/servers/oss-clitest-server/databases/postgres',
            'policyId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.DataProtection/backupVaults/clitest-bkp-vault-donotdelete/backupPolicies/osspolicy',
            'secretStoreUri': 'https://oss-clitest-keyvault.vault.azure.net/secrets/oss-clitest-secret',
            'keyVaultId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/oss-clitest-rg/providers/Microsoft.KeyVault/vaults/oss-clitest-keyvault',
            'policyRuleName': 'BackupWeekly',
            "targetBlobContainerUrl": "https://ossclitestsa.blob.core.windows.net/oss-clitest-blob-container",
        })
        backup_instance_guid = "faec6818-0720-11ec-bd1b-c8f750f92764"
        backup_instance_json = test.cmd('az dataprotection backup-instance initialize --datasource-type "{dataSourceType}" '
                                        '-l "{location}" --policy-id "{policyId}" --datasource-id "{ossDbId}" --secret-store-type "{secretStoreType}" --secret-store-uri "{secretStoreUri}"').get_output_in_json()
        backup_instance_json["backup_instance_name"] = test.kwargs['ossServer'] + "-" + test.kwargs['ossDb'] + "-" + backup_instance_guid
        test.kwargs.update({
            "backupInstance": backup_instance_json,
            "backupInstanceName": backup_instance_json["backup_instance_name"]
        })

        # Uncomment if validate-for-backup fails due to permission error. Only uncomment when running live.
        # test.cmd('az dataprotection backup-instance update-msi-permissions '
        #          '-g "{rg}" '
        #          '--vault-name "{vaultName}" '
        #          '--backup-instance "{backupInstance}" '
        #          '--datasource-type "{dataSourceType}" '
        #          '--permissions-scope "{permissionsScope}" '
        #          '--operation "{operation}" '
        #          '--keyvault-id "{keyVaultId}" --yes')

        backup_instance_validate_create(test)

        # Ensure no other jobs running on datasource. Required to avoid operation clashes. Requries dataSourceId kwarg to run.
        wait_for_job_exclusivity_on_datasource(test)

        # Trigger ad-hoc backup and track to completion
        adhoc_backup_response = test.cmd('az dataprotection backup-instance adhoc-backup '
                                         '-n {backupInstanceName} -g {rg} --vault-name {vaultName} --rule-name "{policyRuleName}"').get_output_in_json()
        test.kwargs.update({"jobId": adhoc_backup_response["jobId"]})
        track_job_to_completion(test)

        recovery_point = test.cmd('az dataprotection recovery-point list --backup-instance-name "{backupInstanceName}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.greater_than('length([])', 0)
        ]).get_output_in_json()
        test.kwargs.update({
            'recoveryPointId': recovery_point[0]['name']
        })

        timestring = datetime.now().strftime("%d%m%Y_%H%M%S")
        test.kwargs.update({
            "targetOssDbId": test.kwargs["ossDbId"] + "_restore_" + timestring
        })

        restore_request = test.cmd('az dataprotection backup-instance restore initialize-for-data-recovery '
                                   '--datasource-type "{dataSourceType}" --restore-location "{restoreLocation}" --source-datastore "{sourceDataStore}" '
                                   '--recovery-point-id "{recoveryPointId}" --target-resource-id "{targetOssDbId}" '
                                   '--secret-store-type "{secretStoreType}" --secret-store-uri "{secretStoreUri}"').get_output_in_json()
        test.kwargs.update({"restoreRequest": restore_request})

        test.cmd('az dataprotection backup-instance validate-for-restore -g "{rg}" --vault-name "{vaultName}" -n "{backupInstanceName}" --restore-request-object "{restoreRequest}"')

        # Ensure no other jobs running on datasource. Required to avoid operation clashes. Requries dataSourceId kwarg to run.
        wait_for_job_exclusivity_on_datasource(test)

        restore_trigger_json = test.cmd('az dataprotection backup-instance restore trigger -g "{rg}" --vault-name "{vaultName}" '
                                        '-n "{backupInstanceName}" --restore-request-object "{restoreRequest}"').get_output_in_json()
        test.kwargs.update({"jobId": restore_trigger_json["jobId"]})

        test.cmd('az dataprotection job show --ids "{jobId}"', checks=[
            test.exists('properties.extendedInfo.recoveryDestination')
        ])

        track_job_to_completion(test)

        timestring = datetime.now().strftime("%d%m%Y_%H%M%S")
        test.kwargs.update({
            "targetFile": "postgres_restore_" + timestring
        })

        restore_request = test.cmd('az dataprotection backup-instance restore initialize-for-data-recovery-as-files '
                                   '--datasource-type "{dataSourceType}" --restore-location "{restoreLocation}" --source-datastore "{sourceDataStore}" '
                                   '--recovery-point-id "{recoveryPointId}" --target-blob-container-url "{targetBlobContainerUrl}" --target-file-name "{targetFile}"').get_output_in_json()
        test.kwargs.update({"restoreRequest": restore_request})

        test.cmd('az dataprotection backup-instance validate-for-restore -g "{rg}" --vault-name "{vaultName}" -n "{backupInstanceName}" --restore-request-object "{restoreRequest}"')

        # Ensure no other jobs running on datasource. Required to avoid operation clashes. Requries dataSourceId kwarg to run.
        wait_for_job_exclusivity_on_datasource(test)

        restore_trigger_json = test.cmd('az dataprotection backup-instance restore trigger -g "{rg}" --vault-name "{vaultName}" '
                                        '-n "{backupInstanceName}" --restore-request-object "{restoreRequest}"').get_output_in_json()
        test.kwargs.update({"jobId": restore_trigger_json["jobId"]})

        test.cmd('az dataprotection job show --ids "{jobId}"', checks=[
            test.exists('properties.extendedInfo.recoveryDestination')
        ])

        track_job_to_completion(test)

    # Uses a persistent vault and DS
    @AllowLargeResponse()
    def test_dataprotection_backup_and_restore_aks(test):
        test.kwargs.update({
            'location': 'eastus2euap',
            'restoreLocation': 'eastus2euap',
            'rg': 'clitest-dpp-rg',
            'rgId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/oss-clitest-rg',
            'vaultName': "clitest-bkp-vault-aks-donotdelete",
            'policyId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.DataProtection/backupVaults/clitest-bkp-vault-aks-donotdelete/backupPolicies/akspolicy',
            'dataSourceType': 'AzureKubernetesService',
            'sourceDataStore': 'OperationalStore',
            'aksClusterName': 'clitest-cluster1-donotdelete',
            'aksClusterId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/oss-clitest-rg/providers/Microsoft.ContainerService/managedClusters/clitest-cluster1-donotdelete',
            'friendlyName': "clitest-friendly-aks",
            'permissionsScope': "ResourceGroup",
            'policyRuleName': 'BackupHourly',
        })
        backup_instance_guid = "faec6818-0720-11ec-bd1b-c8f750f92764"
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
        backup_instance_json["backup_instance_name"] = test.kwargs['aksClusterName'] + "-" + test.kwargs['aksClusterName'] + "-" + backup_instance_guid
        test.kwargs.update({
            "backupInstance": backup_instance_json,
            "backupInstanceName": backup_instance_json["backup_instance_name"]
        })

        # Uncomment if validate-for-backup fails due to permission error. Only uncomment when running live.
        # test.cmd('az dataprotection backup-instance update-msi-permissions '
        #          '-g "{rg}" --vault-name "{vaultName}" '
        #          '--datasource-type "{dataSourceType}" '
        #          '--operation "Backup" '
        #          '--permissions-scope "{permissionsScope}" '
        #          '--backup-instance "{backupInstance}" --yes')

        backup_instance_validate_create(test)

        # Ensure no other jobs running on datasource. Required to avoid operation clashes. Requries dataSourceId kwarg to run.
        wait_for_job_exclusivity_on_datasource(test)

        # Trigger ad-hoc backup and track to completion
        adhoc_backup_response = test.cmd('az dataprotection backup-instance adhoc-backup '
                                         '-n {backupInstanceName} -g {rg} --vault-name {vaultName} --rule-name "{policyRuleName}"').get_output_in_json()
        test.kwargs.update({"jobId": adhoc_backup_response["jobId"]})
        track_job_to_completion(test)

        recovery_point = test.cmd('az dataprotection recovery-point list --backup-instance-name "{backupInstanceName}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.greater_than('length([])', 0)
        ]).get_output_in_json()
        test.kwargs.update({
            'recoveryPointId': recovery_point[0]['name']
        })

        restore_config_json = test.cmd('az dataprotection backup-instance initialize-restoreconfig --datasource-type "{dataSourceType}"', checks=[
            test.check("persistent_volume_restore_mode", "RestoreWithVolumeData"),
            test.check("conflict_policy", "Skip"),
            test.check("include_cluster_scope_resources", True)
        ]).get_output_in_json()
        test.kwargs.update({
            "restoreConfig": restore_config_json
        })

        restore_request = test.cmd('az dataprotection backup-instance restore initialize-for-item-recovery'
                                   ' --datasource-type "{dataSourceType}" '
                                   '--restore-location "{restoreLocation}" '
                                   '--source-datastore "{sourceDataStore}" '
                                   '--recovery-point-id "{recoveryPointId}" '
                                   '--backup-instance-id "{backupInstanceId}" '
                                   '--restore-configuration "{restoreConfig}"').get_output_in_json()
        test.kwargs.update({"restoreRequest": restore_request})

        # Uncomment if validate-for-restore fails due to permission error. Only uncomment when running live.
        # test.cmd('az dataprotection backup-instance update-msi-permissions '
        #          '-g "{rg}" --vault-name "{vaultName}" '
        #          '--datasource-type "{dataSourceType}" '
        #          '--operation "Restore" '
        #          '--permissions-scope "{permissionsScope}" '
        #          '--restore-request-object "{restoreRequest}" '
        #          '--snapshot-resource-group-id "{rgId}" --yes')

        test.cmd('az dataprotection backup-instance validate-for-restore -g "{rg}" --vault-name "{vaultName}" -n "{backupInstanceName}" --restore-request-object "{restoreRequest}"')

        # Ensure no other jobs running on datasource. Required to avoid operation clashes. Requries dataSourceId kwarg to run.
        wait_for_job_exclusivity_on_datasource(test)

        restore_trigger_json = test.cmd('az dataprotection backup-instance restore trigger -g "{rg}" --vault-name "{vaultName}" '
                                        '-n "{backupInstanceName}" --restore-request-object "{restoreRequest}"').get_output_in_json()
        test.kwargs.update({"jobId": restore_trigger_json["jobId"]})

        test.cmd('az dataprotection job show --ids "{jobId}"', checks=[
            test.exists('properties.extendedInfo.recoveryDestination')
        ])

        track_job_to_completion(test)

    # Uses a persistent vault and DS
    @AllowLargeResponse()
    def test_dataprotection_backup_and_restore_pgflex(test):
        test.kwargs.update({
            'location': 'eastus2euap',
            'rg': 'clitest-dpp-ecy-rg',
            'vaultName': 'clitest-bkp-vault-ecy-donotdelete',
            'restoreLocation': 'eastus2euap',
            'dataSourceType': 'AzureDatabaseForPostgreSQLFlexibleServer',
            'sourceDataStore': 'VaultStore',
            'permissionsScope': 'ResourceGroup',
            'operation': 'Backup',
            'restoreOperation': 'Restore',
            'pgflexName': 'clitest-pgflex-server',
            'pgflexDsId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-ecy-rg/providers/Microsoft.DBforPostgreSQL/flexibleServers/clitest-pgflex-server',
            'policyId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-ecy-rg/providers/Microsoft.DataProtection/backupVaults/clitest-bkp-vault-ecy-donotdelete/backupPolicies/pgflexpolicy',
            'policyRuleName': 'BackupWeekly',
            'targetBlobContainerUrl': 'https://clitestecysa.blob.core.windows.net/clitestpgflexblob',
            'targetFileName': 'targetpgflex',
            'targetStorageAccount': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-ecy-rg/providers/Microsoft.Storage/storageAccounts/clitestecysa',
        })
        backup_instance_guid = "faec6818-0720-11ec-bd1b-c8f750f92764"
        backup_instance_json = test.cmd('az dataprotection backup-instance initialize --datasource-type "{dataSourceType}" '
                                        '-l "{location}" --policy-id "{policyId}" --datasource-id "{pgflexDsId}"').get_output_in_json()
        backup_instance_json["backup_instance_name"] = test.kwargs['pgflexName'] + "-" + backup_instance_guid
        test.kwargs.update({
            "backupInstance": backup_instance_json,
            "backupInstanceName": backup_instance_json["backup_instance_name"]
        })

        # Uncomment if validate-for-backup fails due to permission error. Only uncomment when running live.
        # test.cmd('az dataprotection backup-instance update-msi-permissions '
        #          '-g "{rg}" '
        #          '--vault-name "{vaultName}" '
        #          '--backup-instance "{backupInstance}" '
        #          '--datasource-type "{dataSourceType}" '
        #          '--permissions-scope "{permissionsScope}" '
        #          '--operation "{operation}" --yes')

        backup_instance_validate_create(test)

        # Ensure no other jobs running on datasource. Required to avoid operation clashes. Requries dataSourceId kwarg to run.
        wait_for_job_exclusivity_on_datasource(test)

        # Trigger ad-hoc backup and track to completion
        adhoc_backup_response = test.cmd('az dataprotection backup-instance adhoc-backup '
                                         '-n {backupInstanceName} -g {rg} --vault-name {vaultName} --rule-name "{policyRuleName}"').get_output_in_json()
        test.kwargs.update({"jobId": adhoc_backup_response["jobId"]})
        track_job_to_completion(test)

        recovery_point = test.cmd('az dataprotection recovery-point list --backup-instance-name "{backupInstanceName}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.greater_than('length([])', 0)
        ]).get_output_in_json()
        test.kwargs.update({
            'recoveryPointId': recovery_point[0]['name']
        })

        restore_request = test.cmd('az dataprotection backup-instance restore initialize-for-data-recovery-as-files '
                                   '--datasource-type "{dataSourceType}" --restore-location "{restoreLocation}" --source-datastore "{sourceDataStore}" '
                                   '--recovery-point-id "{recoveryPointId}" --target-blob-container-url "{targetBlobContainerUrl}" '
                                   '--target-file-name "{targetFileName}"').get_output_in_json()
        test.kwargs.update({"restoreRequest": restore_request})

        # Uncomment if validate-for-backup fails due to permission error. Only uncomment when running live.
        # test.cmd('az dataprotection backup-instance update-msi-permissions '
        #          '-g "{rg}" '
        #          '--vault-name "{vaultName}" '
        #          '--restore-request-object "{restoreRequest}" '
        #          '--datasource-type "{dataSourceType}" '
        #          '--permissions-scope "{permissionsScope}" '
        #          '--operation "{restoreOperation}" '
        #          '--target-storage-account-id "{targetStorageAccount}" --yes')

        test.cmd('az dataprotection backup-instance validate-for-restore -g "{rg}" --vault-name "{vaultName}" -n "{backupInstanceName}" --restore-request-object "{restoreRequest}"')

        # # Ensure no other jobs running on datasource. Required to avoid operation clashes. Requries dataSourceId kwarg to run.
        wait_for_job_exclusivity_on_datasource(test)

        restore_trigger_json = test.cmd('az dataprotection backup-instance restore trigger -g "{rg}" --vault-name "{vaultName}" '
                                        '-n "{backupInstanceName}" --restore-request-object "{restoreRequest}"').get_output_in_json()
        test.kwargs.update({"jobId": restore_trigger_json["jobId"]})

        test.cmd('az dataprotection job show --ids "{jobId}"', checks=[
            test.exists('properties.extendedInfo.recoveryDestination')
        ])

        track_job_to_completion(test)

    # Uses a persistent vault and DS
    @AllowLargeResponse()
    def test_dataprotection_backup_and_restore_mysql(test):
        test.kwargs.update({
            'location': 'eastus2euap',
            'rg': 'clitest-dpp-ecy-rg',
            'vaultName': 'clitest-bkp-vault-ecy-donotdelete',
            'restoreLocation': 'eastus2euap',
            'dataSourceType': 'AzureDatabaseForMySQL',
            'sourceDataStore': 'VaultStore',
            'permissionsScope': 'ResourceGroup',
            'operation': 'Backup',
            'restoreOperation': 'Restore',
            'mysqlName': 'clitest-mysql-server',
            'mysqlDsId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-ecy-rg/providers/Microsoft.DBforMySQL/flexibleServers/clitest-mysql-server',
            'policyId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-ecy-rg/providers/Microsoft.DataProtection/backupVaults/clitest-bkp-vault-ecy-donotdelete/backupPolicies/mysqlpolicy',
            'policyRuleName': 'BackupWeekly',
            'targetBlobContainerUrl': 'https://clitestecysa.blob.core.windows.net/clitestmysqlblob',
            'targetFileName': 'targetmysql',
            'targetStorageAccount': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-ecy-rg/providers/Microsoft.Storage/storageAccounts/clitestecysa',
        })
        backup_instance_guid = "faec6818-0720-11ec-bd1b-c8f750f92764"
        backup_instance_json = test.cmd('az dataprotection backup-instance initialize --datasource-type "{dataSourceType}" '
                                        '-l "{location}" --policy-id "{policyId}" --datasource-id "{mysqlDsId}"').get_output_in_json()
        backup_instance_json["backup_instance_name"] = test.kwargs['mysqlName'] + "-" + backup_instance_guid
        test.kwargs.update({
            "backupInstance": backup_instance_json,
            "backupInstanceName": backup_instance_json["backup_instance_name"]
        })

        # Uncomment if validate-for-backup fails due to permission error. Only uncomment when running live.
        # test.cmd('az dataprotection backup-instance update-msi-permissions '
        #          '-g "{rg}" '
        #          '--vault-name "{vaultName}" '
        #          '--backup-instance "{backupInstance}" '
        #          '--datasource-type "{dataSourceType}" '
        #          '--permissions-scope "{permissionsScope}" '
        #          '--operation "{operation}" --yes')

        backup_instance_validate_create(test)

        # Ensure no other jobs running on datasource. Required to avoid operation clashes. Requries dataSourceId kwarg to run.
        wait_for_job_exclusivity_on_datasource(test)

        # Trigger ad-hoc backup and track to completion
        adhoc_backup_response = test.cmd('az dataprotection backup-instance adhoc-backup '
                                         '-n {backupInstanceName} -g {rg} --vault-name {vaultName} --rule-name "{policyRuleName}"').get_output_in_json()
        test.kwargs.update({"jobId": adhoc_backup_response["jobId"]})
        track_job_to_completion(test)

        recovery_point = test.cmd('az dataprotection recovery-point list --backup-instance-name "{backupInstanceName}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.greater_than('length([])', 0)
        ]).get_output_in_json()
        test.kwargs.update({
            'recoveryPointId': recovery_point[0]['name']
        })

        restore_request = test.cmd('az dataprotection backup-instance restore initialize-for-data-recovery-as-files '
                                   '--datasource-type "{dataSourceType}" --restore-location "{restoreLocation}" --source-datastore "{sourceDataStore}" '
                                   '--recovery-point-id "{recoveryPointId}" --target-blob-container-url "{targetBlobContainerUrl}" '
                                   '--target-file-name "{targetFileName}"').get_output_in_json()
        test.kwargs.update({"restoreRequest": restore_request})

        # Uncomment if validate-for-backup fails due to permission error. Only uncomment when running live.
        # test.cmd('az dataprotection backup-instance update-msi-permissions '
        #          '-g "{rg}" '
        #          '--vault-name "{vaultName}" '
        #          '--restore-request-object "{restoreRequest}" '
        #          '--datasource-type "{dataSourceType}" '
        #          '--permissions-scope "{permissionsScope}" '
        #          '--operation "{restoreOperation}" '
        #          '--target-storage-account-id "{targetStorageAccount}" --yes')

        test.cmd('az dataprotection backup-instance validate-for-restore -g "{rg}" --vault-name "{vaultName}" -n "{backupInstanceName}" --restore-request-object "{restoreRequest}"')

        # # Ensure no other jobs running on datasource. Required to avoid operation clashes. Requries dataSourceId kwarg to run.
        wait_for_job_exclusivity_on_datasource(test)

        restore_trigger_json = test.cmd('az dataprotection backup-instance restore trigger -g "{rg}" --vault-name "{vaultName}" '
                                        '-n "{backupInstanceName}" --restore-request-object "{restoreRequest}"').get_output_in_json()
        test.kwargs.update({"jobId": restore_trigger_json["jobId"]})

        test.cmd('az dataprotection job show --ids "{jobId}"', checks=[
            test.exists('properties.extendedInfo.recoveryDestination')
        ])

        track_job_to_completion(test)
