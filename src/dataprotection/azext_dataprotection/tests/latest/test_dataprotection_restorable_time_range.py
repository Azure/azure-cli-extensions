# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


class RestorableTimeRangeScenarioTest(ScenarioTest):

    @AllowLargeResponse()
    def test_dataprotection_restorable_time_range_find(test):
        test.kwargs.update({
            'location': 'centraluseuap',
            'rg': 'clitest-dpp-rg',
            'vaultName': 'clitest-bkp-vault-persistent-bi-donotdelete',
            'backupInstanceName': 'clitestsabidonotdelete-clitestsabidonotdelete-887c3538-0bfc-11ee-acd3-002b670b472e',
            'sourceDataStoreType': 'OperationalStore'
        })
        test.cmd('az dataprotection restorable-time-range find --source-data-store-type "{sourceDataStoreType}" -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}"', checks=[
            test.check('id', "{backupInstanceName}"),
            test.check('properties.objectType', "AzureBackupFindRestorableTimeRangesResponse"),
            test.greater_than('length(properties.restorableTimeRanges)', 0)
        ])

        test.cmd('az dataprotection restorable-time-range find --source-data-store-type "{sourceDataStoreType}" -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                 '--start-time 2001-02-27T12:00:00.0000000Z --end-time 2002-05-14T14:00:00.0000000Z')
        test.cmd('az dataprotection restorable-time-range find --source-data-store-type "{sourceDataStoreType}" -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                 '--start-time 2051-02-27T12:00:00.0000000Z --end-time 2052-05-14T14:00:00.0000000Z')

        test.cmd('az dataprotection restorable-time-range find --source-data-store-type "{sourceDataStoreType}" -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                 '--start-time 2023-06-16T01:00:00.0000000Z --end-time 2033-06-16T01:00:00.0000000Z')
        test.cmd('az dataprotection restorable-time-range find --source-data-store-type "{sourceDataStoreType}" -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                 '--start-time 2023-06-16T01:00:00.000Z --end-time 2033-06-16T01:00:00.000Z')
        test.cmd('az dataprotection restorable-time-range find --source-data-store-type "{sourceDataStoreType}" -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                 '--start-time 2023-06-16T01:00:00.00Z --end-time 2033-06-16T01:00:00.00Z')
        test.cmd('az dataprotection restorable-time-range find --source-data-store-type "{sourceDataStoreType}" -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                 '--start-time 2023-06-16T01:00:00 --end-time 2033-06-16T01:00:00')
        test.cmd('az dataprotection restorable-time-range find --source-data-store-type "{sourceDataStoreType}" -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                 '--start-time 2023-06-16T01:00:00+05:30 --end-time 2033-06-16T01:00:00+05:30')

        test.cmd('az dataprotection restorable-time-range find --source-data-store-type "{sourceDataStoreType}" -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                 '--start-time 2023-06-16T01:00:00.0000000Z')
        test.cmd('az dataprotection restorable-time-range find --source-data-store-type "{sourceDataStoreType}" -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                 '--start-time 2023-06-16T01:00:00.000Z', expect_failure=True)
        test.cmd('az dataprotection restorable-time-range find --source-data-store-type "{sourceDataStoreType}" -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                 '--end-time 2033-06-16T01:00:00.00Z', expect_failure=True)
        test.cmd('az dataprotection restorable-time-range find --source-data-store-type "{sourceDataStoreType}" -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                 '--start-time 2023-06-16T01:00:00', expect_failure=True)
        test.cmd('az dataprotection restorable-time-range find --source-data-store-type "{sourceDataStoreType}" -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                 '--end-time 2033-06-16T01:00:00+05:30', expect_failure=True)

        test.cmd('az dataprotection restorable-time-range find --source-data-store-type "{sourceDataStoreType}" -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                 '--start-time 2033-06-16T01:00:00.0000000Z --end-time 2023-06-16T01:00:00.0000000Z', expect_failure=True)
