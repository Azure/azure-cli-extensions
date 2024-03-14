# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


class BackupPolicyScenarioTest(ScenarioTest):

    def setUp(test):
        super().setUp()
        test.kwargs.update({
            'location': 'centraluseuap',
            'vaultName': 'clitest-bkp-vault',
        })

    @ResourceGroupPreparer(name_prefix='clitest-dpp-backuppolicy-', location='centraluseuap')
    @AllowLargeResponse()
    def test_dataprotection_backup_policy_create_and_delete(test):
        test.cmd('az dataprotection backup-vault create -g "{rg}" --vault-name "{vaultName}" -l "{location}" '
                 '--storage-settings datastore-type="VaultStore" type="LocallyRedundant" --type "SystemAssigned" --soft-delete-state "Off"')

        disk_policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type AzureDisk').get_output_in_json()
        test.kwargs.update({"diskPolicy": disk_policy_json})
        test.cmd('az dataprotection backup-policy create -n "diskpolicy" --policy "{diskPolicy}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.check('properties.datasourceTypes[0]', "Microsoft.Compute/disks")
        ])
        test.cmd('az dataprotection backup-policy delete -n "diskpolicy" -g "{rg}" --vault-name "{vaultName}" -y')

        blob_policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type AzureBlob').get_output_in_json()
        test.kwargs.update({"blobPolicy": blob_policy_json})
        test.cmd('az dataprotection backup-policy create -n "blobpolicy" --policy "{blobPolicy}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.check('properties.datasourceTypes[0]', "Microsoft.Storage/storageAccounts/blobServices")
        ])
        test.cmd('az dataprotection backup-policy delete -n "blobpolicy" -g "{rg}" --vault-name "{vaultName}" -y')

        oss_policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type AzureDatabaseForPostgreSQL').get_output_in_json()
        test.kwargs.update({"ossPolicy": oss_policy_json})
        test.cmd('az dataprotection backup-policy create -n "osspolicy" --policy "{ossPolicy}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.check('properties.datasourceTypes[0]', "Microsoft.DBforPostgreSQL/servers/databases")
        ])
        test.cmd('az dataprotection backup-policy delete -n "osspolicy" -g "{rg}" --vault-name "{vaultName}" -y')

        aks_policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type AzureKubernetesService').get_output_in_json()
        test.kwargs.update({"aksPolicy": aks_policy_json})
        test.cmd('az dataprotection backup-policy create -n "akspolicy" --policy "{aksPolicy}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.check('properties.datasourceTypes[0]', "Microsoft.ContainerService/managedClusters")
        ])
        test.cmd('az dataprotection backup-policy delete -n "akspolicy" -g "{rg}" --vault-name "{vaultName}" -y')

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='clitest-dpp-backuppolicy-', location='centraluseuap')
    def test_dataprotection_backup_policy_manual(test):
        test.cmd('az dataprotection backup-vault create -g "{rg}" --vault-name "{vaultName}" -l "{location}" '
                 '--storage-settings datastore-type="VaultStore" type="LocallyRedundant" --type "SystemAssigned" --soft-delete-state "Off"')

        disk_policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type AzureDisk', checks=[
            test.check('datasourceTypes[0]', "Microsoft.Compute/disks")
        ]).get_output_in_json()
        test.kwargs.update({
            'policyName': "disk-policy",
            "diskPolicy": disk_policy_json
        })

        lifecycle_json = test.cmd('az dataprotection backup-policy retention-rule create-lifecycle --count 12 --type Days --source-datastore OperationalStore', checks=[
            test.check('deleteAfter.duration', "P12D"),
            test.check('sourceDataStore.dataStoreType', "OperationalStore")
        ]).get_output_in_json()
        test.kwargs.update({"lifecycle": lifecycle_json})

        disk_policy_json = test.cmd('az dataprotection backup-policy retention-rule set --name Daily --policy "{diskPolicy}" --lifecycles "{lifecycle}"', checks=[
            test.check("length(policyRules[?objectType == 'AzureRetentionRule'])", 2),
        ]).get_output_in_json()
        test.kwargs.update({"diskPolicy": disk_policy_json})

        test.cmd('az dataprotection backup-policy retention-rule remove --name Daily --policy "{diskPolicy}"', checks=[
            test.check("length(policyRules[?objectType == 'AzureRetentionRule'])", 1)
        ])

        criteria_json = test.cmd('az dataprotection backup-policy tag create-absolute-criteria --absolute-criteria FirstOfDay', checks=[
            test.check('objectType', "ScheduleBasedBackupCriteria")
        ]).get_output_in_json()
        test.kwargs.update({"criteria": criteria_json})

        disk_policy_json = test.cmd('az dataprotection backup-policy tag set --name Daily --policy "{diskPolicy}" --criteria "{criteria}"', checks=[
            test.check("length(policyRules[0].trigger.taggingCriteria)", 2)
        ]).get_output_in_json()
        test.kwargs.update({"diskPolicy": disk_policy_json})

        test.cmd('az dataprotection backup-policy tag remove --name Daily --policy "{diskPolicy}"', checks=[
            test.check("length(policyRules[0].trigger.taggingCriteria)", 1)
        ])

        schedule_json = test.cmd('az dataprotection backup-policy trigger create-schedule --interval-type Hourly --interval-count 6 --schedule-days 2021-05-02T05:30:00', checks=[
            test.check('[0]', "R/2021-05-02T05:30:00+00:00/PT6H")
        ]).get_output_in_json()
        test.kwargs.update({"repeating_time_interval": schedule_json[0]})

        disk_policy_json = test.cmd('az dataprotection backup-policy trigger set --policy "{diskPolicy}" --schedule "{repeating_time_interval}"', checks=[
            test.check('policyRules[0].trigger.schedule.repeatingTimeIntervals[0]', "R/2021-05-02T05:30:00+00:00/PT6H")
        ]).get_output_in_json()
        test.kwargs.update({"diskPolicy": disk_policy_json})
        test.cmd('az dataprotection backup-policy create -n "{policyName}" --policy "{diskPolicy}" -g "{rg}" --vault-name "{vaultName}"')

        test.cmd('az dataprotection backup-policy list -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.exists("[?name == '{policyName}']")
        ])
        test.cmd('az dataprotection backup-policy show -g "{rg}" --vault-name "{vaultName}" -n "{policyName}"', checks=[
            test.check('name', "{policyName}")
        ])

    @AllowLargeResponse()
    def test_dataprotection_backup_policy_generic_criteria(test):
        test.cmd('az dataprotection backup-policy tag create-generic-criteria --days-of-month 1 2 27 28 LaSt', checks=[
            test.check('length(days_of_month)', 5)
        ])
        test.cmd('az dataprotection backup-policy tag create-generic-criteria --days-of-month 29', expect_failure=True)
        test.cmd('az dataprotection backup-policy tag create-generic-criteria --days-of-month -1', expect_failure=True)
        test.cmd('az dataprotection backup-policy tag create-generic-criteria --days-of-month 0', expect_failure=True)
        test.cmd('az dataprotection backup-policy tag create-generic-criteria --days-of-week Monday Tuesday Wednesday Thursday Friday Saturday Sunday', checks=[
            test.check('length(days_of_the_week)', 7)
        ])
        test.cmd('az dataprotection backup-policy tag create-generic-criteria --weeks-of-month FIRST second Third FoUrtH Last', checks=[
            test.check('length(weeks_of_the_month)', 5)
        ])
        test.cmd('az dataprotection backup-policy tag create-generic-criteria --months-of-year '
                 'JANUARY February MarCh april May June July August September October November December', checks=[
                     test.check('length(months_of_year)', 12)
                 ])
