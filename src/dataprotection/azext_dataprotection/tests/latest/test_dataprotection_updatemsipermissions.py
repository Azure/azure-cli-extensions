# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

class UpdateMSIPermissionsScenarioTest(ScenarioTest):

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='clitestdataprotection_updatemsipermissions_')
    def test_dataprotection_update_msi_permissions_disk(test, resource_group):
        test.kwargs.update({
            'rg': resource_group,
            'vaultName': "cli-test-backup-vault",
            'location': 'eastus',
            'policyName': 'disk-policy',
            'diskname':'cli-test-disk'
        })

        # Use existing resources. We never actually create a backup-instance.
        disk_response = test.cmd('az disk create -g "{rg}" -n "{diskname}" --size-gb 4').get_output_in_json()
        test.kwargs.update({
            "diskId": disk_response["id"],
        })

        test.cmd('az dataprotection backup-vault create '
                '-g "{rg}" --vault-name "{vaultName}" -l {location} '
                '--storage-settings datastore-type="VaultStore" type="LocallyRedundant" --type SystemAssigned '
                '--soft-delete-state Off',
                checks=[]).get_output_in_json()

        policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type AzureDisk').get_output_in_json()
        test.kwargs.update({"policyJson": policy_json})
        policy = test.cmd('az dataprotection backup-policy create -n "{policyName}" --policy "{policyJson}" -g "{rg}" --vault-name "{vaultName}"').get_output_in_json()
        test.kwargs.update({"policyid": policy['id']})

        backup_instance_json = test.cmd('az dataprotection backup-instance initialize --datasource-type AzureDisk'
                                        ' -l {location} --policy-id "{policyid}" --datasource-id "{diskId}" --snapshot-rg "{rg}" --tags Owner=dppclitest').get_output_in_json()
        test.kwargs.update({
            "backupInstanceJson": backup_instance_json,
        })

        test.cmd('az dataprotection backup-instance update-msi-permissions --datasource-type AzureDisk --operation Backup --permissions-scope Resource -g "{rg}" --vault-name "{vaultName}" --backup-instance "{backupInstanceJson}" --yes').get_output_in_json()

