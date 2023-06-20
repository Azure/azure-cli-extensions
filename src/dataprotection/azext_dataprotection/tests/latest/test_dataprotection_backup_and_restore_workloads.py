# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
import time, sys
from datetime import datetime
from ..utils import track_job_to_completion , wait_for_job_exclusivity_on_datasource


class BackupAndRestoreScenarioTest(ScenarioTest):

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
            'keyVaultId':  '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/oss-clitest-rg/providers/Microsoft.KeyVault/vaults/oss-clitest-keyvault',
            'policyRuleName': 'BackupWeekly',
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
        # time.sleep(30)

        # Adding backup-instance delete as the cleanup command, will always run even if test fails.
        test.addCleanup(test.cmd, 'az dataprotection backup-instance delete -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --yes --no-wait')

        # Ensure backup-instance deletion from prev run. If instance is already deleted, it will return instantly.
        test.cmd('az dataprotection backup-instance delete -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --yes')

        test.cmd('az dataprotection backup-instance create -g "{rg}" --vault-name "{vaultName}" --backup-instance "{backupInstance}"', checks=[
            test.check('properties.provisioningState', "Succeeded")
        ])

        # Waiting for backup-instance configuration to complete. Adjust timeout if this fails for no other reason.
        test.cmd('az dataprotection backup-instance wait -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --timeout 120 '
                '--custom "properties.protectionStatus.status==\'ProtectionConfigured\'"')

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

        # Ensure no other jobs running on datasource. Required to avoid operation clashes. Requries dataSourceId kwarg to run.
        wait_for_job_exclusivity_on_datasource(test)

        test.cmd('az dataprotection backup-instance validate-for-restore -g "{rg}" --vault-name "{vaultName}" -n "{backupInstanceName}" --restore-request-object "{restoreRequest}"')
        restore_trigger_json = test.cmd('az dataprotection backup-instance restore trigger -g "{rg}" --vault-name "{vaultName}" '
                                        '-n "{backupInstanceName}" --restore-request-object "{restoreRequest}"').get_output_in_json()
        test.kwargs.update({"jobId": restore_trigger_json["jobId"]})

        test.cmd('az dataprotection job show --ids "{jobId}"', checks=[
            test.exists('properties.extendedInfo.recoveryDestination')
        ])

        track_job_to_completion(test)

        timestring = datetime.now().strftime("%d%m%Y_%H%M%S")
        test.kwargs.update({
            "targetBlobContainerUrl": "https://ossclitestsa.blob.core.windows.net/oss-clitest-blob-container",
            "targetFile": "postgres_restore_" + timestring
        })

        restore_request = test.cmd('az dataprotection backup-instance restore initialize-for-data-recovery-as-files '
                                   '--datasource-type "{dataSourceType}" --restore-location "{restoreLocation}" --source-datastore "{sourceDataStore}" '
                                   '--recovery-point-id "{recoveryPointId}" --target-blob-container-url "{targetBlobContainerUrl}" --target-file-name "{targetFile}"').get_output_in_json()
        test.kwargs.update({"restoreRequest": restore_request})

        # Ensure no other jobs running on datasource. Required to avoid operation clashes. Requries dataSourceId kwarg to run.
        wait_for_job_exclusivity_on_datasource(test)

        test.cmd('az dataprotection backup-instance validate-for-restore -g "{rg}" --vault-name "{vaultName}" -n "{backupInstanceName}" --restore-request-object "{restoreRequest}"')
        restore_trigger_json = test.cmd('az dataprotection backup-instance restore trigger -g "{rg}" --vault-name "{vaultName}" '
                                        '-n "{backupInstanceName}" --restore-request-object "{restoreRequest}"').get_output_in_json()
        test.kwargs.update({"jobId": restore_trigger_json["jobId"]})

        test.cmd('az dataprotection job show --ids "{jobId}"', checks=[
            test.exists('properties.extendedInfo.recoveryDestination')
        ])

        track_job_to_completion(test)
