# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from unittest import mock
from azure.cli.testsdk import (ScenarioTest, JMESPathCheck)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse, record_only

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class MicrosoftStorageSyncScenarioTest(ScenarioTest):
    @AllowLargeResponse()
    @record_only()
    def test_storagesync(self):
        # setup
        resource_group_name = "rgteststoragesync2"
        storage_account_name = "sateststoragesync2"
        sync_service_name = "testsyncservice"
        sync_group_name = "testsyncgroup"
        cloud_endpoint_name = "testcloudendpoint"
        server_endpoint_name = "testserverendpoint"
        file_share_name = "testfileshare"

        self.kwargs.update({
            'rg': resource_group_name,
            'sa': storage_account_name,
            'sync_service_name': sync_service_name,
            'sync_group_name': sync_group_name,
            'cloud_endpoint_name': cloud_endpoint_name,
            'server_endpoint_name': server_endpoint_name,
            'file_share_name': file_share_name,
        })
        self.cmd('az group create -n {rg} -l westus')
        self.cmd('az storage account create -n {sa} -g {rg}')
        storage_account_key = self.cmd('az storage account keys list -n {sa} -g {rg}').get_output_in_json()[0]["value"]
        self.kwargs.update({"storage_account_key": storage_account_key})

        self.cmd('az storage share create '
                 '--name {file_share_name} '
                 '--quota 1 '
                 '--account-name {sa} --account-key {storage_account_key}')

        # run
        self.cmd('az storagesync check-name-availability --location-name westus --name {sync_service_name} '
                 '--type Microsoft.StorageSync/storageSyncServices')

        self.cmd('az storagesync create '
                 '--resource-group {rg} '
                 '--name {sync_service_name} '
                 '--tags key1=value1',
                 checks=[JMESPathCheck('name', sync_service_name)])

        self.cmd('az storagesync show '
                 '--resource-group {rg} '
                 '--name {sync_service_name}',
                 checks=[JMESPathCheck('storageSyncServiceStatus', 0)])

        self.cmd('az storagesync list '
                 '--resource-group {rg}',
                 checks=[JMESPathCheck('length(@)', 1)])

        self.cmd('az storagesync private-endpoint-connection list '
                 '--resource-group {rg} --storage-sync-service {sync_service_name}')

        self.cmd('az storagesync sync-group create '
                 '--resource-group {rg} '
                 '--storage-sync-service {sync_service_name} '
                 '--name {sync_group_name}',
                 checks=[JMESPathCheck('name', sync_group_name),
                         JMESPathCheck('syncGroupStatus', 0)])

        self.cmd('az storagesync sync-group show '
                 '--resource-group {rg} '
                 '--storage-sync-service {sync_service_name} '
                 '--name {sync_group_name}',
                 checks=[JMESPathCheck('name', sync_group_name),
                         JMESPathCheck('syncGroupStatus', 0)])

        self.cmd('az storagesync sync-group list '
                 '--resource-group {rg} '
                 '--storage-sync-service {sync_service_name}',
                 checks=[JMESPathCheck('length(@)', 1)])

        # need to add role assignment with permission
        sp_id = self.cmd('az ad sp list --display-name "Microsoft.StorageSync"').get_output_in_json()[0]["id"]
        sa_id = self.cmd('az storage account show -n {sa}').get_output_in_json()["id"]
        self.kwargs.update({"sp_id": sp_id, "sa_id": sa_id})
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd('az role assignment create --assignee {sp_id} --role "Reader and Data Access" --scope {sa_id}')

        self.cmd('az storagesync sync-group cloud-endpoint create '
                 '--resource-group {rg} '
                 '--storage-sync-service {sync_service_name} '
                 '--sync-group-name {sync_group_name} '
                 '--name {cloud_endpoint_name} '
                 '--storage-account {sa} '
                 '--azure-file-share-name {file_share_name}',
                 checks=[JMESPathCheck('provisioningState', 'Succeeded')])

        self.cmd('az storagesync sync-group cloud-endpoint show '
                 '--resource-group {rg} '
                 '--storage-sync-service {sync_service_name} '
                 '--sync-group-name {sync_group_name} '
                 '--name {cloud_endpoint_name}',
                 checks=[JMESPathCheck('name', cloud_endpoint_name)])

        self.cmd('az storagesync sync-group cloud-endpoint list '
                 '--resource-group {rg} '
                 '--storage-sync-service {sync_service_name} '
                 '--sync-group-name {sync_group_name}',
                 checks=[JMESPathCheck('length(@)', 1)])

        self.cmd('az storagesync sync-group cloud-endpoint trigger-change-detection '
                 '--resource-group {rg} '
                 '--storage-sync-service {sync_service_name} '
                 '--sync-group-name {sync_group_name} '
                 '--name {cloud_endpoint_name}')

        # need to create and register Windows server and run agent manually
        # https://learn.microsoft.com/en-us/azure/storage/file-sync/file-sync-deployment-guide?tabs=azure-portal%2Cproactive-portal
        # https://www.microsoft.com/en-us/download/details.aspx?id=57159

        server_list = self.cmd('az storagesync registered-server list '
                               '--resource-group {rg} '
                               '--storage-sync-service {sync_service_name}').get_output_in_json()
        self.assertEqual(1, len(server_list))

        server_id = server_list[0]['serverId']
        self.kwargs.update({
            'server_id': server_id
        })

        self.cmd('az storagesync registered-server show '
                 '--resource-group {rg} '
                 '--storage-sync-service {sync_service_name} '
                 '--server-id {server_id}',
                 checks=[JMESPathCheck('provisioningState', 'Succeeded'),
                         JMESPathCheck('serverId', server_id)])

        self.cmd('az storagesync sync-group server-endpoint create '
                 '--resource-group {rg} '
                 '--storage-sync-service {sync_service_name} '
                 '--sync-group-name {sync_group_name} '
                 '--name {server_endpoint_name} '
                 '--server-id {server_id} '
                 '--server-local-path "d:\\syncfolder" '
                 '--cloud-tiering "on" '
                 '--tier-files-older-than-days 20 '
                 '--volume-free-space-percent 80 ',
                 checks=[JMESPathCheck('provisioningState', 'Succeeded'),
                         JMESPathCheck('name', server_endpoint_name)])

        self.cmd('az storagesync sync-group server-endpoint update '
                 '--resource-group {rg} '
                 '--storage-sync-service {sync_service_name} '
                 '--sync-group-name {sync_group_name} '
                 '--name {server_endpoint_name} '
                 '--tier-files-older-than-days 10',
                 checks=[JMESPathCheck('provisioningState', 'Succeeded'),
                         JMESPathCheck('tierFilesOlderThanDays', 10)])

        self.cmd('az storagesync sync-group server-endpoint show '
                 '--resource-group {rg} '
                 '--storage-sync-service {sync_service_name} '
                 '--sync-group-name {sync_group_name} '
                 '--name {server_endpoint_name} ',
                 checks=[JMESPathCheck('provisioningState', 'Succeeded'),
                         JMESPathCheck('name', server_endpoint_name)])

        self.cmd('az storagesync sync-group server-endpoint list '
                 '--resource-group {rg} '
                 '--storage-sync-service {sync_service_name} '
                 '--sync-group-name {sync_group_name}',
                 checks=[JMESPathCheck('length(@)', 1)])

        self.cmd('az storagesync registered-server delete '
                 '--resource-group {rg} '
                 '--storage-sync-service {sync_service_name} '
                 '--server-id {server_id} '
                 '-y',
                 checks=[])

        self.cmd('az storagesync sync-group server-endpoint delete '
                 '--resource-group {rg} '
                 '--storage-sync-service {sync_service_name} '
                 '--sync-group-name {sync_group_name} '
                 '--name {server_endpoint_name} '
                 '-y',
                 checks=[])

        self.cmd('az storagesync sync-group cloud-endpoint delete '
                 '--resource-group {rg} '
                 '--storage-sync-service {sync_service_name} '
                 '--sync-group-name {sync_group_name} '
                 '--name {cloud_endpoint_name} '
                 '-y',
                 checks=[])

        self.cmd('az storagesync sync-group delete '
                 '--resource-group {rg} '
                 '--storage-sync-service {sync_service_name} '
                 '--name {sync_group_name} '
                 '-y',
                 checks=[])

        self.cmd('az storagesync delete '
                 '--resource-group {rg} '
                 '--name {sync_service_name} '
                 '-y',
                 checks=[])

        self.cmd('az storagesync show '
                 '--resource-group {rg} '
                 '--name {sync_service_name}',
                 expect_failure=True)

        # tear down
        self.cmd('az storage share delete '
                 '--name {file_share_name} '
                 '--account-name {sa} --account-key {storage_account_key} '
                 '--delete-snapshots include')
