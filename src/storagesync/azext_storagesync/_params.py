# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)


def load_arguments(self, _):

    with self.argument_context('storagesync storage-sync-service create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of Storage Sync Service resource.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('properties', id_part=None, help='The properties of the storage sync service.')

    with self.argument_context('storagesync storage-sync-service update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of Storage Sync Service resource.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('properties', id_part=None, help='The properties of the storage sync service.')

    with self.argument_context('storagesync storage-sync-service delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of Storage Sync Service resource.')

    with self.argument_context('storagesync storage-sync-service show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of Storage Sync Service resource.')

    with self.argument_context('storagesync storage-sync-service list') as c:
        c.argument('resource_group', resource_group_name_type)

    with self.argument_context('storagesync storage-sync-service check-name-availability') as c:
        c.argument('location_name', id_part=None, help='The desired region for the name check.')
        c.argument('name', id_part=None, help='The name to check for availability')
        c.argument('_type', options_list=['--type'], id_part=None, help='The resource type. Must be set to Microsoft.StorageSync/storageSyncServices')

    with self.argument_context('storagesync sync-group create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('storage_sync_service_name', id_part=None, help='Name of Storage Sync Service resource.')
        c.argument('name', id_part=None, help='Name of Sync Group resource.')
        c.argument('properties', id_part=None, help='The parameters used to create the sync group')

    with self.argument_context('storagesync sync-group update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('storage_sync_service_name', id_part=None, help='Name of Storage Sync Service resource.')
        c.argument('name', id_part=None, help='Name of Sync Group resource.')
        c.argument('properties', id_part=None, help='The parameters used to create the sync group')

    with self.argument_context('storagesync sync-group delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('storage_sync_service_name', id_part=None, help='Name of Storage Sync Service resource.')
        c.argument('name', id_part=None, help='Name of Sync Group resource.')

    with self.argument_context('storagesync sync-group show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('storage_sync_service_name', id_part=None, help='Name of Storage Sync Service resource.')
        c.argument('name', id_part=None, help='Name of Sync Group resource.')

    with self.argument_context('storagesync sync-group list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('storage_sync_service_name', id_part=None, help='Name of Storage Sync Service resource.')

    with self.argument_context('storagesync cloud-endpoint create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('storage_sync_service_name', id_part=None, help='Name of Storage Sync Service resource.')
        c.argument('sync_group_name', id_part=None, help='Name of Sync Group resource.')
        c.argument('name', id_part=None, help='Name of Cloud Endpoint object.')
        c.argument('storage_account_resource_id', id_part=None, help='Storage Account Resource Id')
        c.argument('azure_file_share_name', id_part=None, help='Azure file share name')
        c.argument('storage_account_tenant_id', id_part=None, help='Storage Account Tenant Id')
        c.argument('friendly_name', id_part=None, help='Friendly Name')

    with self.argument_context('storagesync cloud-endpoint update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('storage_sync_service_name', id_part=None, help='Name of Storage Sync Service resource.')
        c.argument('sync_group_name', id_part=None, help='Name of Sync Group resource.')
        c.argument('name', id_part=None, help='Name of Cloud Endpoint object.')
        c.argument('storage_account_resource_id', id_part=None, help='Storage Account Resource Id')
        c.argument('azure_file_share_name', id_part=None, help='Azure file share name')
        c.argument('storage_account_tenant_id', id_part=None, help='Storage Account Tenant Id')
        c.argument('friendly_name', id_part=None, help='Friendly Name')

    with self.argument_context('storagesync cloud-endpoint delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('storage_sync_service_name', id_part=None, help='Name of Storage Sync Service resource.')
        c.argument('sync_group_name', id_part=None, help='Name of Sync Group resource.')
        c.argument('name', id_part=None, help='Name of Cloud Endpoint object.')

    with self.argument_context('storagesync cloud-endpoint show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('storage_sync_service_name', id_part=None, help='Name of Storage Sync Service resource.')
        c.argument('sync_group_name', id_part=None, help='Name of Sync Group resource.')
        c.argument('name', id_part=None, help='Name of Cloud Endpoint object.')

    with self.argument_context('storagesync cloud-endpoint list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('storage_sync_service_name', id_part=None, help='Name of Storage Sync Service resource.')
        c.argument('sync_group_name', id_part=None, help='Name of Sync Group resource.')

    with self.argument_context('storagesync cloud-endpoint trigger-change-detection') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('storage_sync_service_name', id_part=None, help='Name of Storage Sync Service resource.')
        c.argument('sync_group_name', id_part=None, help='Name of Sync Group resource.')
        c.argument('name', id_part=None, help='Name of Cloud Endpoint object.')
        c.argument('azure_file_share', id_part=None, help='Azure File Share.')
        c.argument('partition', id_part=None, help='Post Restore partition.')
        c.argument('replica_group', id_part=None, help='Post Restore replica group.')
        c.argument('request_id', id_part=None, help='Post Restore request id.')
        c.argument('azure_file_share_uri', id_part=None, help='Post Restore Azure file share uri.')
        c.argument('status', id_part=None, help='Post Restore Azure status.')
        c.argument('source_azure_file_share_uri', id_part=None, help='Post Restore Azure source azure file share uri.')
        c.argument('backup_metadata_property_bag', id_part=None, help='Pre Restore backup metadata property bag.')
        c.argument('restore_file_spec', id_part=None, help='Post Restore restore file spec array.', nargs='+')
        c.argument('pause_wait_for_sync_drain_time_period_in_seconds', id_part=None, help='Pre Restore pause wait for sync drain time period in seconds.')
        c.argument('failed_file_list', id_part=None, help='Post Restore Azure failed file list.')
        c.argument('directory_path', id_part=None, help='Relative path to a directory Azure File share for which change detection is to be performed.')
        c.argument('change_detection_mode', arg_type=get_enum_type(['Default', 'Recursive']), id_part=None, help='Change Detection Mode. Applies to a directory specified in directoryPath parameter.')
        c.argument('paths', id_part=None, help='Array of relative paths on the Azure File share to be included in the change detection. Can be files and directories.', nargs='+')

    with self.argument_context('storagesync server-endpoint create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('storage_sync_service_name', id_part=None, help='Name of Storage Sync Service resource.')
        c.argument('sync_group_name', id_part=None, help='Name of Sync Group resource.')
        c.argument('name', id_part=None, help='Name of Server Endpoint object.')
        c.argument('cloud_tiering', arg_type=get_enum_type(['on', 'off']), id_part=None, help='Cloud Tiering.')
        c.argument('volume_free_space_percent', id_part=None, help='Level of free space to be maintained by Cloud Tiering if it is enabled.')
        c.argument('tier_files_older_than_days', id_part=None, help='Tier files older than days.')
        c.argument('offline_data_transfer', arg_type=get_enum_type(['on', 'off']), id_part=None, help='Offline data transfer')
        c.argument('offline_data_transfer_share_name', id_part=None, help='Offline data transfer share name')

    with self.argument_context('storagesync server-endpoint update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('storage_sync_service_name', id_part=None, help='Name of Storage Sync Service resource.')
        c.argument('sync_group_name', id_part=None, help='Name of Sync Group resource.')
        c.argument('name', id_part=None, help='Name of Server Endpoint object.')
        c.argument('cloud_tiering', arg_type=get_enum_type(['on', 'off']), id_part=None, help='Cloud Tiering.')
        c.argument('volume_free_space_percent', id_part=None, help='Level of free space to be maintained by Cloud Tiering if it is enabled.')
        c.argument('tier_files_older_than_days', id_part=None, help='Tier files older than days.')
        c.argument('offline_data_transfer', arg_type=get_enum_type(['on', 'off']), id_part=None, help='Offline data transfer')
        c.argument('offline_data_transfer_share_name', id_part=None, help='Offline data transfer share name')

    with self.argument_context('storagesync server-endpoint delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('storage_sync_service_name', id_part=None, help='Name of Storage Sync Service resource.')
        c.argument('sync_group_name', id_part=None, help='Name of Sync Group resource.')
        c.argument('name', id_part=None, help='Name of Server Endpoint object.')

    with self.argument_context('storagesync server-endpoint show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('storage_sync_service_name', id_part=None, help='Name of Storage Sync Service resource.')
        c.argument('sync_group_name', id_part=None, help='Name of Sync Group resource.')
        c.argument('name', id_part=None, help='Name of Server Endpoint object.')

    with self.argument_context('storagesync server-endpoint list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('storage_sync_service_name', id_part=None, help='Name of Storage Sync Service resource.')
        c.argument('sync_group_name', id_part=None, help='Name of Sync Group resource.')

    with self.argument_context('storagesync registered-server create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of Storage Sync Service resource.')
        c.argument('server_id', id_part=None, help='Server Id')
        c.argument('server_certificate', id_part=None, help='Registered Server Certificate')
        c.argument('agent_version', id_part=None, help='Registered Server Agent Version')
        c.argument('server_osversion', id_part=None, help='Registered Server OS Version')
        c.argument('last_heart_beat', id_part=None, help='Registered Server last heart beat')
        c.argument('server_role', id_part=None, help='Registered Server serverRole')
        c.argument('cluster_id', id_part=None, help='Registered Server clusterId')
        c.argument('cluster_name', id_part=None, help='Registered Server clusterName')
        c.argument('friendly_name', id_part=None, help='Friendly Name')

    with self.argument_context('storagesync registered-server update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of Storage Sync Service resource.')
        c.argument('server_id', id_part=None, help='Server Id')
        c.argument('server_certificate', id_part=None, help='Registered Server Certificate')
        c.argument('agent_version', id_part=None, help='Registered Server Agent Version')
        c.argument('server_osversion', id_part=None, help='Registered Server OS Version')
        c.argument('last_heart_beat', id_part=None, help='Registered Server last heart beat')
        c.argument('server_role', id_part=None, help='Registered Server serverRole')
        c.argument('cluster_id', id_part=None, help='Registered Server clusterId')
        c.argument('cluster_name', id_part=None, help='Registered Server clusterName')
        c.argument('friendly_name', id_part=None, help='Friendly Name')

    with self.argument_context('storagesync registered-server delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of Storage Sync Service resource.')
        c.argument('server_id', id_part=None, help='Server Id')

    with self.argument_context('storagesync registered-server show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of Storage Sync Service resource.')
        c.argument('server_id', id_part=None, help='Server Id')

    with self.argument_context('storagesync registered-server list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of Storage Sync Service resource.')