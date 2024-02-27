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


class ConfigScenarioTest(ScenarioTest):

    @AllowLargeResponse()
    def test_dataprotection_aks_backup_and_restore_initialize_configs(test):
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
            'payloadBackupHooks': "[{ \'name\':\'name1\',\'namespace\':\'ns1\' },{ \'name\':\'name2\',\'namespace\':\'ns2\'}]",
            'payloadRestoreHooks': "[{'name':'restorehookname','namespace':'default'},{'name':'restorehookname1','namespace':'hrweb'}]",
        })

        # backup_instance_guid = "faec6818-0720-11ec-bd1b-c8f750f92764"
        test.cmd('az dataprotection backup-instance initialize-backupconfig --datasource-type AzureKubernetesService '
                 '--backup-hook-refs "{payloadBackupHooks}"',
                 checks=[
                     test.check('include_cluster_scope_resources', True),
                     test.check('snapshot_volumes', True),
                     test.check('length(backup_hook_references)', 2),
                     test.check('backup_hook_references[0].name', 'name1')
                 ])

        test.cmd('az dataprotection backup-instance initialize-restoreconfig --datasource-type "{dataSourceType}" '
                 '--restore-hook-refs "{payloadRestoreHooks}"',
                 checks=[
                     test.check("persistent_volume_restore_mode", "RestoreWithVolumeData"),
                     test.check("conflict_policy", "Skip"),
                     test.check("include_cluster_scope_resources", True),
                     test.check('length(restore_hook_references)', 2),
                     test.check('restore_hook_references[0].name', 'restorehookname')
                 ])
