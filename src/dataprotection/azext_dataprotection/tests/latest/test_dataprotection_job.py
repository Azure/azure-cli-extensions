# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


class JobScenarioTest(ScenarioTest):

    @AllowLargeResponse()
    def test_dataprotection_job_list_and_show(test):
        test.kwargs.update({
            'location': 'centraluseuap',
            'rg': 'clitest-dpp-rg',
            'vaultName': 'clitest-bkp-vault-persistent-bi-donotdelete',
            'dataSourceType': 'AzureDisk',
            'dataSourceId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.Compute/disks/clitest-disk-persistent-bi-donotdelete',
            'crrVaultName': 'clitest-bkp-vault-crr-donotdelete',
        })
        test.cmd('az dataprotection job list -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.greater_than('length([])', 0)
        ])

        datasource_job_list = test.cmd('az dataprotection job list-from-resourcegraph --datasource-type "{dataSourceType}" --datasource-id "{dataSourceId}"', checks=[
            test.greater_than('length([])', 0),
            test.exists('[0].name')
        ]).get_output_in_json()
        test.kwargs.update({
            'jobName': datasource_job_list[0]['name']
        })

        test.cmd('az dataprotection job show --job-id "{jobName}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.check('name', "{jobName}")
        ])

        # Test --use-secondary-region for job list and show commands
        secondary_job_list = test.cmd('az dataprotection job list -g "{rg}" -v "{crrVaultName}" --use-secondary-region', checks=[
            test.greater_than('length([])', 0),
            test.exists('[0].name')
        ]).get_output_in_json()
        test.kwargs.update({
            'secondaryJobName': secondary_job_list[0]['name']
        })

        test.cmd('az dataprotection job show --job-id "{secondaryJobName}" -g "{rg}" --vault-name "{crrVaultName}" --use-secondary-region', checks=[
            test.check('name', "{secondaryJobName}")
        ])
