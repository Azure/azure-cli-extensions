# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from ..utils import track_job_to_completion


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


# Uses persistent disk and vault for both tests
class BackupInstanceCreateDeleteScenarioTest(ScenarioTest):

    def setUp(test):
        super().setUp()
        test.kwargs.update({
            'location': 'centraluseuap',
            'rg': 'clitest-dpp-rg',
            'vaultName': 'clitest-bkp-vault-donotdelete',
        })

    @AllowLargeResponse()
    def test_dataprotection_backup_instance_create_backup_delete_disk(test):
        test.kwargs.update({
            'dataSourceType': "AzureDisk",
            'permissionsScope': "Resource",
            'policyId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.DataProtection/backupVaults/clitest-bkp-vault-donotdelete/backupPolicies/diskpolicy',
            'diskName': 'clitest-disk-donotdelete',
            'diskId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.Compute/disks/clitest-disk-donotdelete',
            'policyRuleName': "BackupHourly"
        })
        backup_instance_guid = "b7e6f082-b310-11eb-8f55-9cfce85d4fa1"
        backup_instance_json = test.cmd('az dataprotection backup-instance initialize --datasource-type "{dataSourceType}" '
                                        '-l "{location}" --policy-id "{policyId}" --datasource-id "{diskId}" --snapshot-rg "{rg}" --tags Owner=dppclitest Purpose=Testing').get_output_in_json()
        backup_instance_json["backup_instance_name"] = test.kwargs['diskName'] + "-" + test.kwargs['diskName'] + "-" + backup_instance_guid
        test.kwargs.update({
            "backupInstance": backup_instance_json,
            "backupInstanceName": backup_instance_json["backup_instance_name"]
        })

        # Uncomment if validate-for-backup fails due to permission error. Only uncomment if running live.
        # test.cmd('az dataprotection backup-instance update-msi-permissions --datasource-type "{dataSourceType}" --operation Backup --permissions-scope "{permissionsScope}" '
        #          '-g "{rg}" --vault-name "{vaultName}" --backup-instance "{backupInstance}" --yes')
        # import time
        # time.sleep(30)

        backup_instance_validate_create(test)

        # Trigger ad-hoc backup and track to completion
        adhoc_backup_response = test.cmd('az dataprotection backup-instance adhoc-backup '
                                         '-n {backupInstanceName} -g {rg} --vault-name {vaultName} --rule-name "{policyRuleName}"').get_output_in_json()
        test.kwargs.update({"jobId": adhoc_backup_response["jobId"]})
        track_job_to_completion(test)

    @AllowLargeResponse()
    def test_dataprotection_backup_instance_create_and_delete_blob(test):
        test.kwargs.update({
            'dataSourceType': "AzureBlob",
            'permissionsScope': "Resource",
            'policyId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.DataProtection/backupVaults/clitest-bkp-vault-donotdelete/backupPolicies/opBlobPolicy',
            'storageAccountName': 'clitestsadonotdelete',
            'storageAccountId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.Storage/storageAccounts/clitestsadonotdelete'
        })
        backup_instance_guid = "b7e6f082-b310-11eb-8f55-9cfce85d4fa1"
        backup_instance_json = test.cmd('az dataprotection backup-instance initialize --datasource-type "{dataSourceType}" '
                                        '-l "{location}" --policy-id "{policyId}" --datasource-id "{storageAccountId}" --snapshot-rg "{rg}" --tags Owner=dppclitest Purpose=Testing').get_output_in_json()
        backup_instance_json["backup_instance_name"] = test.kwargs['storageAccountName'] + "-" + test.kwargs['storageAccountName'] + "-" + backup_instance_guid
        test.kwargs.update({
            "backupInstance": backup_instance_json,
            "backupInstanceName": backup_instance_json["backup_instance_name"]
        })

        # Uncomment if validate-for-backup fails due to permission error. Only uncomment when running live.
        # test.cmd('az dataprotection backup-instance update-msi-permissions --datasource-type "{dataSourceType}" --operation Backup --permissions-scope "{permissionsScope}" '
        #          '-g "{rg}" --vault-name "{vaultName}" --backup-instance "{backupInstance}" --yes')
        # import time
        # time.sleep(30)

        backup_instance_validate_create(test)
