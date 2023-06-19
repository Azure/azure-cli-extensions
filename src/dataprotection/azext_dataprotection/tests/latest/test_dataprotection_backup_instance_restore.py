# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
import time

def get_midpoint_of_time_range(start_time_str, end_time_str):
    """ Takes start time and end time strings as input and returns mid point as string
        in ISO format.
    """
    import dateutil.parser as dparser
    try:
        start_time = dparser.parse(start_time_str)
        end_time = dparser.parse(end_time_str)
        point_in_time = start_time + (end_time - start_time)/2
        return point_in_time.strftime("%Y-%m-%dT%H:%M:%S")
    except:
        raise Exception('One or more input dates are invalid.')


def wait_for_job_exclusivity_on_datasource(test):
    jobs_in_progress = test.cmd('az dataprotection job list-from-resourcegraph --datasource-type "{dataSourceType}" --datasource-id "{dataSourceId}" --status "InProgress"').get_output_in_json()
    while jobs_in_progress:
        time.sleep(10)
        jobs_in_progress = test.cmd('az dataprotection job list-from-resourcegraph --datasource-type "{dataSourceType}" --datasource-id "{dataSourceId}" --status "InProgress"').get_output_in_json()


def validate_and_trigger_restore(test):
    test.cmd('az dataprotection backup-instance validate-for-restore -g "{rg}" --vault-name "{vaultName}" -n "{backupInstanceName}" --restore-request-object "{restoreRequest}"')
    restore_trigger_json = test.cmd('az dataprotection backup-instance restore trigger -g "{rg}" --vault-name "{vaultName}" '
                                    '-n "{backupInstanceName}" --restore-request-object "{restoreRequest}"').get_output_in_json()
    test.kwargs.update({"jobId": restore_trigger_json["jobId"]})

    test.cmd('az dataprotection job show --ids "{jobId}"', checks=[
        test.check('properties.dataSourceName', "{dataSourceName}"),
        test.exists('properties.extendedInfo.recoveryDestination')
    ])


def track_job_to_completion(test):
    job_status = None
    while job_status != "Completed":
        time.sleep(10)
        job_response = test.cmd('az dataprotection job show --ids "{jobId}"').get_output_in_json()
        job_status = job_response["properties"]["status"]
        if job_status not in ["Completed", "InProgress"]:
            raise Exception("Undefined job status received")


class BackupInstanceRestoreScenarioTest(ScenarioTest):

    def setUp(test):
        super().setUp()
        test.kwargs.update({
            'rg': 'clitest-dpp-rg',
            'vaultName': 'clitest-bkp-vault-persistent-bi-donotdelete',
            'location': 'centraluseuap',
        })

    @AllowLargeResponse()
    def test_dataprotection_backup_instance_restore_disk(test):
        test.kwargs.update({
            'dataSourceType': 'AzureDisk',
            'sourceDataStore': 'OperationalStore',
            'backupInstanceName': 'clitest-disk-persistent-bi-donotdelete-clitest-disk-persistent-bi-donotdelete-e33c80ba-0bf8-11ee-aaa6-002b670b472e',
            'dataSourceName': 'clitest-disk-persistent-bi-donotdelete',
            'dataSourceId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.Compute/disks/clitest-disk-persistent-bi-donotdelete',
            'restoreDiskName': 'clitest-disk-restored',
            'restoreDiskId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.Compute/disks/clitest-disk-restored',
            'restoreLocation': 'centraluseuap'
        })
        recovery_point = test.cmd('az dataprotection recovery-point list --backup-instance-name "{backupInstanceName}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.greater_than('length([])', 0)
        ]).get_output_in_json()
        test.kwargs.update({
            'recoveryPointId': recovery_point[0]['name']
        })

        # Add disk deletion to cleanup tasks
        test.addCleanup(test.cmd, 'az disk delete --name "{restoreDiskName}" --resource-group "{rg}" --yes --no-wait')
        # As a failsafe, ensure restored disk from previous run is deleted
        test.cmd('az disk delete --name "{restoreDiskName}" --resource-group "{rg}" --yes')

        # Ensure no other jobs running on datasource. Required to avoid operation clashes.
        wait_for_job_exclusivity_on_datasource(test)

        restore_request = test.cmd('az dataprotection backup-instance restore  initialize-for-data-recovery '
                                   '--datasource-type "{dataSourceType}" --restore-location "{restoreLocation}" --source-datastore "{sourceDataStore}" '
                                   '--recovery-point-id "{recoveryPointId}" --target-resource-id "{restoreDiskId}"').get_output_in_json()
        test.kwargs.update({"restoreRequest": restore_request})

        validate_and_trigger_restore(test)

        # Track restore to completion
        track_job_to_completion(test)

    @AllowLargeResponse()
    def test_dataprotection_backup_instance_restore_blob(test):
        test.kwargs.update({
            'dataSourceType': 'AzureBlob',
            'sourceDataStore': 'OperationalStore',
            'backupInstanceName': 'clitestsabidonotdelete-clitestsabidonotdelete-887c3538-0bfc-11ee-acd3-002b670b472e',
            'backupInstanceId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.DataProtection/backupVaults/clitest-bkp-vault-persistent-bi-donotdelete/backupInstances/clitestsabidonotdelete-clitestsabidonotdelete-887c3538-0bfc-11ee-acd3-002b670b472e',
            'dataSourceName': 'clitestsabidonotdelete',
            'dataSourceId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.Storage/storageAccounts/clitestsabidonotdelete',
            'restoreLocation': 'centraluseuap',
        })
        restorable_time_range = test.cmd('az dataprotection restorable-time-range find -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" '
                                         '--source-data-store-type "{sourceDataStore}"', checks=[
            test.greater_than('length(properties.restorableTimeRanges)', 0)
        ]).get_output_in_json()

        restore_point_in_time = get_midpoint_of_time_range(
            restorable_time_range['properties']['restorableTimeRanges'][0]['startTime'],
            restorable_time_range['properties']['restorableTimeRanges'][0]['endTime']
        )
        test.kwargs.update({
            'restorePointInTime': restore_point_in_time
        })

        # Ensure no other jobs running on datasource. Required to avoid operation clashes.
        wait_for_job_exclusivity_on_datasource(test)

        restore_request = test.cmd('az dataprotection backup-instance restore  initialize-for-data-recovery '
                                   '--datasource-type "{dataSourceType}" --restore-location "{restoreLocation}" --source-datastore "{sourceDataStore}" '
                                   '--point-in-time "{restorePointInTime}" --backup-instance-id "{backupInstanceId}"').get_output_in_json()
        test.kwargs.update({"restoreRequest": restore_request})

        validate_and_trigger_restore(test)
