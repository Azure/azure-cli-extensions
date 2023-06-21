# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

class BackupInstanceOperationsScenarioTest(ScenarioTest):

    def setUp(test):
        super().setUp()
        test.kwargs.update({
            'location': 'centraluseuap',
            'rg': 'clitest-dpp-rg',
            'vaultName': 'clitest-bkp-vault-persistent-bi-donotdelete',
        })

    @AllowLargeResponse()
    def test_dataprotection_backup_instance_update_protection(test):
        test.kwargs.update({
            'backupInstanceName': 'clitest-disk-persistent-bi-donotdelete-clitest-disk-persistent-bi-donotdelete-e33c80ba-0bf8-11ee-aaa6-002b670b472e'
        })
        test.addCleanup(test.cmd, 'az dataprotection backup-instance resume-protection -n "{backupInstanceName}" -g "{rg}" --vault-name "{vaultName}"')

        test.cmd('az dataprotection backup-instance wait -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --timeout 600 '
                 '--custom "properties.currentProtectionState==\'ProtectionConfigured\'"')

        test.cmd('az dataprotection backup-instance stop-protection -n "{backupInstanceName}" -g "{rg}" --vault-name "{vaultName}"')
        test.cmd('az dataprotection backup-instance show -n "{backupInstanceName}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.check('properties.currentProtectionState','ProtectionStopped')
        ])

        test.cmd('az dataprotection backup-instance resume-protection -n "{backupInstanceName}" -g "{rg}" --vault-name "{vaultName}"')
        test.cmd('az dataprotection backup-instance show -n "{backupInstanceName}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.check('properties.currentProtectionState','ProtectionConfigured')
        ])

        test.cmd('az dataprotection backup-instance suspend-backup -n "{backupInstanceName}" -g "{rg}" --vault-name "{vaultName}"')
        test.cmd('az dataprotection backup-instance show -n "{backupInstanceName}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.check('properties.currentProtectionState','BackupsSuspended')
        ])

    @AllowLargeResponse()
    def test_dataprotection_backup_instance_update_policy(test):
        test.kwargs.update({
            'backupInstanceName': 'clitestsabidonotdelete-clitestsabidonotdelete-887c3538-0bfc-11ee-acd3-002b670b472e',
            'policyName': 'blobpolicy',
            'policyId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.DataProtection/backupVaults/clitest-bkp-vault-persistent-bi-donotdelete/backupPolicies/blobpolicy',
            'altPolicyName': 'altblobpolicy',
            'altPolicyId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.DataProtection/backupVaults/clitest-bkp-vault-persistent-bi-donotdelete/backupPolicies/altblobpolicy'
        })
        test.cmd('az dataprotection backup-instance wait -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --timeout 300 '
                 '--custom "properties.currentProtectionState==\'ProtectionConfigured\'"')

        test.cmd('az dataprotection backup-instance update-policy -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --policy-id "{altPolicyId}"', checks=[
            test.check("contains(properties.policyInfo.policyId, '/{altPolicyName}')", True)
        ])
        test.cmd('az dataprotection backup-instance wait -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --timeout 300 '
                 '--custom "properties.currentProtectionState==\'ProtectionConfigured\'"')

        test.cmd('az dataprotection backup-instance update-policy -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --policy-id "{policyId}"',  checks=[
            test.check("contains(properties.policyInfo.policyId, '/{policyName}')", True)
        ])
        test.cmd('az dataprotection backup-instance wait -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --timeout 300 '
                 '--custom "properties.currentProtectionState==\'ProtectionConfigured\'"')


    @AllowLargeResponse()
    def test_dataprotection_backup_instance_list_from_resource_graph(test):
        test.kwargs.update({
            'dataSourceType': 'AzureDisk',
            'dataSourceId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.Compute/disks/clitest-disk-persistent-bi-donotdelete',
            'backupInstanceName': 'clitest-disk-persistent-bi-donotdelete-clitest-disk-persistent-bi-donotdelete-e33c80ba-0bf8-11ee-aaa6-002b670b472e'
        })
        test.cmd('az dataprotection backup-instance list-from-resourcegraph --datasource-type "{dataSourceType}" --datasource-id "{dataSourceId}"', checks=[
            test.greater_than('length([])', 0),
            test.exists("[?name == '{backupInstanceName}']")
        ])
