# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


class RecoveryPointScenarioTest(ScenarioTest):

    def setUp(test):
        super().setUp()
        test.kwargs.update({
            'location': 'centraluseuap',
            'rg': 'clitest-dpp-rg',
            'vaultName': 'clitest-bkp-vault-persistent-bi-donotdelete',
            'backupInstanceName': 'clitest-disk-persistent-bi-donotdelete-clitest-disk-persistent-bi-donotdelete-e33c80ba-0bf8-11ee-aaa6-002b670b472e',
            'crrVaultName': 'clitest-bkp-vault-crr-donotdelete',
            'crrBackupInstanceName': 'clitestcrr-ecy-postgres-8f1f81c9-8869-48c5-8b07-ef587f1b5052',
        })

    @AllowLargeResponse()
    def test_dataprotection_recovery_point_show(test):
        recovery_point_list = test.cmd('az dataprotection recovery-point list -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}"', checks=[
            test.exists('[0].properties.recoveryPointId')
        ]).get_output_in_json()
        test.kwargs.update({
            'recoveryPointId': recovery_point_list[0]['properties']['recoveryPointId']
        })

        test.cmd('az dataprotection recovery-point show -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --recovery-point-id "{recoveryPointId}"', checks=[
            test.check('properties.recoveryPointId', "{recoveryPointId}")
        ])

    @AllowLargeResponse()
    def test_dataprotection_recovery_point_list(test):
        test.cmd('az dataprotection recovery-point list -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}"', checks=[
            test.greater_than('length([])', 0)
        ])
        test.cmd('az dataprotection recovery-point list -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                 '--start-time 2023-06-16T01:00:00 --end-time 2033-06-16T01:00:00')
        test.cmd('az dataprotection recovery-point list -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                 '--start-time 2023-06-16 --end-time 2033-06-16')
        test.cmd('az dataprotection recovery-point list -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                 '--start-time 2023-06-16T01:00:00.00Z --end-time 2033-06-16T01:00:00.00Z')
        test.cmd('az dataprotection recovery-point list -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                 '--start-time 2023-06-16T01:00:00.000Z --end-time 2033-06-16T01:00:00.000Z')
        test.cmd('az dataprotection recovery-point list -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                 '--start-time 2023-06-16T01:00:00.0000000Z --end-time 2033-06-16T01:00:00.0000000Z')

        test.cmd('az dataprotection recovery-point list -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                 '--end-time 2023-06-16T01:00:00.0000000Z --start-time 2033-06-16T01:00:00', checks=[
                     test.is_empty()
                 ])

        test.cmd('az dataprotection recovery-point list -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                 '--start-time 0000-13-32T01:00:00', expect_failure=True)
        test.cmd('az dataprotection recovery-point list -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                 '--end-time 2023-12-31T25:60:00', expect_failure=True)

        test.cmd('az dataprotection recovery-point list -g "{rg}" -v "{crrVaultName}" '
                 '--backup-instance-name "{crrBackupInstanceName}" --use-secondary-region', checks=[
                     test.greater_than('length([])', 0)
                 ])
