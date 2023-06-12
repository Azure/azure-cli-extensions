# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

class TestSetupScenarios(ScenarioTest):

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='clitestdataprotection_updatemsipermissions_')
    def test_update_msi_permissions_disk(test, resource_group):
        test.kwargs.update({
            'rg': resource_group,
            'vaultName': "cli-test-bkp-vault",
            'location': 'eastus',
            'policyname': 'disk-policy',
            'diskname':'cli-test-disk'
        })

        disk_response = test.cmd('az disk create -g "{rg}" -n "{diskname}" --size-gb 4').get_output_in_json()
        test.kwargs.update({
            "diskid": disk_response["id"],
        })

        vault_response = test.cmd('az dataprotection backup-vault create '
                         '-g "{rg}" --vault-name "{vaultName}" -l {location} '
                         '--storage-settings datastore-type="VaultStore" type="LocallyRedundant" --type SystemAssigned '
                         '--soft-delete-state Off',
                         checks=[]).get_output_in_json()
        test.kwargs.update({
            "principalId": vault_response["identity"]["principalId"],
        })

        test.cmd('az dataprotection backup-vault update -g "{rg}" --vault-name "{vaultName}" --azure-monitor-alerts-for-job-failures enabled',checks=[
            test.check('properties.monitoringSettings.azureMonitorAlertSettings.alertsForAllJobFailures', 'Enabled')
        ])

        test.cmd('az dataprotection backup-vault update -g "{rg}" --vault-name "{vaultName}" --azure-monitor-alerts-for-job-failures disabled',checks=[
            test.check('properties.monitoringSettings.azureMonitorAlertSettings.alertsForAllJobFailures', 'Disabled')
        ])

        policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type AzureDisk').get_output_in_json()
        test.kwargs.update({"policyjson": policy_json})
        test.cmd('az dataprotection backup-policy create -n "{policyname}" --policy "{policyjson}" -g "{rg}" --vault-name "{vaultName}"')

        policy_id = test.cmd('az dataprotection backup-policy show -g "{rg}" --vault-name "{vaultName}" -n "{policyname}" --query "id"').get_output_in_json()
        test.kwargs.update({"policyid": policy_id})

        lifecycle_json = test.cmd('az dataprotection backup-policy retention-rule create-lifecycle'
                                ' --count 12 --type Days --source-datastore OperationalStore').get_output_in_json()
        test.kwargs.update({"lifecycle": lifecycle_json})
        policy_json = test.cmd('az dataprotection backup-policy retention-rule set '
                            ' --name Daily --policy "{policyjson}" --lifecycles "{lifecycle}"').get_output_in_json()
        test.kwargs.update({"policyjson": policy_json})

        criteria_json = test.cmd('az dataprotection backup-policy tag create-absolute-criteria --absolute-criteria FirstOfDay').get_output_in_json()
        test.kwargs.update({"criteria": criteria_json})
        policy_json = test.cmd('az dataprotection backup-policy tag set '
                            ' --name Daily --policy "{policyjson}" --criteria "{criteria}"').get_output_in_json()
        test.kwargs.update({"policyjson": policy_json})

        schedule_json = test.cmd('az dataprotection backup-policy trigger create-schedule --interval-type Hourly --interval-count 6 --schedule-days 2021-05-02T05:30:00').get_output_in_json()
        test.kwargs.update({"repeating_time_interval": schedule_json[0]})

        policy_json = test.cmd('az dataprotection backup-policy trigger set '
                            ' --policy "{policyjson}" --schedule "{repeating_time_interval}"').get_output_in_json()
        test.kwargs.update({"policyjson": policy_json})
        test.cmd('az dataprotection backup-policy create -n diskhourlypolicy --policy "{policyjson}" -g "{rg}" --vault-name "{vaultName}"')

        backup_instance_guid = "b7e6f082-b310-11eb-8f55-9cfce85d4fa1"
        backup_instance_json = test.cmd('az dataprotection backup-instance initialize --datasource-type AzureDisk'
                                        ' -l {location} --policy-id "{policyid}" --datasource-id "{diskid}" --snapshot-rg "{rg}" --tags Owner=dppclitest').get_output_in_json()
        backup_instance_json["backup_instance_name"] = test.kwargs['diskname'] + "-" + test.kwargs['diskname'] + "-" + backup_instance_guid
        test.kwargs.update({
            "backup_instance_json": backup_instance_json,
            "backup_instance_name": backup_instance_json["backup_instance_name"]
        })

        test.cmd('az dataprotection backup-instance update-msi-permissions --datasource-type AzureDisk --operation Backup --permissions-scope Resource -g "{rg}" --vault-name "{vaultName}" --backup-instance "{backup_instance_json}" --yes').get_output_in_json()

        test.cmd('az dataprotection backup-vault delete -g "{rg}" --vault-name "{vaultName}" --yes')
        test.cmd('az disk delete --name "{diskname}" --resource-group "{rg}" --yes')