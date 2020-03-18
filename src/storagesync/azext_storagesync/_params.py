# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azext_storagesync._validators import parse_storage_account, parse_server_id, parse_storage_sync_service
from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    resource_group_name_type,
    get_location_type, name_type)

from azure.cli.core.commands.validators import get_default_location_from_resource_group
from knack.arguments import CLIArgumentType


def load_arguments(self, _):
    custom_resource_group_name_type = CLIArgumentType(arg_type=resource_group_name_type, required=False)
    storage_sync_service_name_type = CLIArgumentType(arg_type=name_type, help='The name of storage sync service.', id_part='name')
    storage_sync_service_type = CLIArgumentType(options_list='--storage-sync-service', help='The name or ID of storage sync service.', validator=parse_storage_sync_service)
    sync_group_name_type = CLIArgumentType(help='The name of sync group.')
    cloud_endpoint_name_type = CLIArgumentType(help='The name of cloud endpoint.')
    server_endpoint_name_type = CLIArgumentType(help='The name of server endpoint.')
    azure_file_share_name_type = CLIArgumentType(help='The name of Azure file share.')
    storage_account_type = CLIArgumentType(options_list='--storage-account',
                                           help='The name or ID of the storage account.',
                                           validator=parse_storage_account)
    storage_account_tenant_id_type = CLIArgumentType(help='The id of the tenant that the storage account is in.')
    server_resource_id_type = CLIArgumentType(options_list=['--registered-server-id', '--server-id'],
                                              help='The resource id or GUID of the registered server.',
                                              validator=parse_server_id)
    server_id_type = CLIArgumentType(help='GUID identifying the on-premises server.')
    cloud_tiering_type = CLIArgumentType(arg_type=get_enum_type(['on', 'off']), help='A switch to enable or disable cloud tiering. With cloud tiering, infrequently used or accessed files can be tiered to Azure Files.')
    volume_free_space_percent_type = CLIArgumentType(help='The amount of free space to reserve on the volume on which the server endpoint is located. For example, if volume free space is set to 50% on a volume that has a single server endpoint, roughly half the amount of data is tiered to Azure Files. Regardless of whether cloud tiering is enabled, your Azure file share always has a complete copy of the data in the sync group.')
    offline_data_transfer_type = CLIArgumentType(arg_type=get_enum_type(['on', 'off']), help='A switch to enable or disable offline data transfer. With offline data transfer, you can use alternative means, like Azure Data Box, to transport large amounts of files into Azure without network.')
    offline_data_transfer_share_name_type = CLIArgumentType(help='The name of Azure file share that is used to transfer data offline.')
    tier_files_older_than_days_type = CLIArgumentType(help='The days that the files are older than will be tiered.')

    with self.argument_context('storagesync create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('storage_sync_service_name', storage_sync_service_name_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx),
                   validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type, default={})  # tags must be at least an empty dictionary instead of None. (May be a bug in service and will check with service team.)

    with self.argument_context('storagesync delete') as c:
        c.argument('resource_group_name', custom_resource_group_name_type)
        c.argument('storage_sync_service_name', storage_sync_service_name_type)

    with self.argument_context('storagesync show') as c:
        c.argument('resource_group_name', custom_resource_group_name_type)
        c.argument('storage_sync_service_name', storage_sync_service_name_type)

    with self.argument_context('storagesync list') as c:
        c.argument('resource_group_name', resource_group_name_type)

    with self.argument_context('storagesync sync-group create') as c:
        c.argument('resource_group_name', custom_resource_group_name_type)
        c.argument('storage_sync_service_name', storage_sync_service_type)
        c.argument('sync_group_name', sync_group_name_type, options_list=['--name', '-n'])

    with self.argument_context('storagesync sync-group delete') as c:
        c.argument('resource_group_name', custom_resource_group_name_type)
        c.argument('storage_sync_service_name', storage_sync_service_type)
        c.argument('sync_group_name', sync_group_name_type, options_list=['--name', '-n'])

    with self.argument_context('storagesync sync-group show') as c:
        c.argument('resource_group_name', custom_resource_group_name_type)
        c.argument('storage_sync_service_name', storage_sync_service_type)
        c.argument('sync_group_name', sync_group_name_type, options_list=['--name', '-n'])

    with self.argument_context('storagesync sync-group list') as c:
        c.argument('resource_group_name', custom_resource_group_name_type)
        c.argument('storage_sync_service_name', storage_sync_service_type)

    with self.argument_context('storagesync sync-group cloud-endpoint create') as c:
        c.argument('resource_group_name', custom_resource_group_name_type)
        c.argument('storage_sync_service_name', storage_sync_service_type)
        c.argument('sync_group_name', sync_group_name_type)
        c.argument('cloud_endpoint_name', cloud_endpoint_name_type, options_list=['--name', '-n'])
        c.argument('storage_account_resource_id', storage_account_type)
        c.argument('azure_file_share_name', azure_file_share_name_type)
        c.argument('storage_account_tenant_id', storage_account_tenant_id_type)

    with self.argument_context('storagesync sync-group cloud-endpoint delete') as c:
        c.argument('resource_group_name', custom_resource_group_name_type)
        c.argument('storage_sync_service_name', storage_sync_service_type)
        c.argument('sync_group_name', sync_group_name_type)
        c.argument('cloud_endpoint_name', cloud_endpoint_name_type, options_list=['--name', '-n'])

    with self.argument_context('storagesync sync-group cloud-endpoint show') as c:
        c.argument('resource_group_name', custom_resource_group_name_type)
        c.argument('storage_sync_service_name', storage_sync_service_type)
        c.argument('sync_group_name', sync_group_name_type)
        c.argument('cloud_endpoint_name', cloud_endpoint_name_type, options_list=['--name', '-n'])

    with self.argument_context('storagesync sync-group cloud-endpoint list') as c:
        c.argument('resource_group_name', custom_resource_group_name_type)
        c.argument('storage_sync_service_name', storage_sync_service_type)
        c.argument('sync_group_name', sync_group_name_type)

    with self.argument_context('storagesync sync-group cloud-endpoint wait') as c:
        c.argument('cloud_endpoint_name', cloud_endpoint_name_type, options_list=['--name', '-n'])

    with self.argument_context('storagesync sync-group server-endpoint create') as c:
        c.argument('resource_group_name', custom_resource_group_name_type)
        c.argument('storage_sync_service_name', storage_sync_service_type)
        c.argument('sync_group_name', sync_group_name_type)
        c.argument('server_endpoint_name', server_endpoint_name_type, options_list=['--name', '-n'])
        c.argument('server_resource_id', server_resource_id_type)
        c.argument('server_local_path', help='The local path of the registered server.')
        c.argument('cloud_tiering', cloud_tiering_type)
        c.argument('volume_free_space_percent', volume_free_space_percent_type)
        c.argument('tier_files_older_than_days', tier_files_older_than_days_type)
        c.argument('offline_data_transfer', offline_data_transfer_type)
        c.argument('offline_data_transfer_share_name', offline_data_transfer_share_name_type)

    with self.argument_context('storagesync sync-group server-endpoint update') as c:
        c.argument('resource_group_name', custom_resource_group_name_type)
        c.argument('storage_sync_service_name', storage_sync_service_type)
        c.argument('sync_group_name', sync_group_name_type)
        c.argument('server_endpoint_name', server_endpoint_name_type, options_list=['--name', '-n'])
        c.argument('cloud_tiering', cloud_tiering_type)
        c.argument('volume_free_space_percent', volume_free_space_percent_type)
        c.argument('tier_files_older_than_days', tier_files_older_than_days_type)
        c.argument('offline_data_transfer', offline_data_transfer_type)
        c.argument('offline_data_transfer_share_name', offline_data_transfer_share_name_type)

    with self.argument_context('storagesync sync-group server-endpoint delete') as c:
        c.argument('resource_group_name', custom_resource_group_name_type)
        c.argument('storage_sync_service_name', storage_sync_service_type)
        c.argument('sync_group_name', sync_group_name_type)
        c.argument('server_endpoint_name', server_endpoint_name_type, options_list=['--name', '-n'])

    with self.argument_context('storagesync sync-group server-endpoint show') as c:
        c.argument('resource_group_name', custom_resource_group_name_type)
        c.argument('storage_sync_service_name', storage_sync_service_type)
        c.argument('sync_group_name', sync_group_name_type)
        c.argument('server_endpoint_name', server_endpoint_name_type, options_list=['--name', '-n'])

    with self.argument_context('storagesync sync-group server-endpoint list') as c:
        c.argument('resource_group_name', custom_resource_group_name_type)
        c.argument('storage_sync_service_name', storage_sync_service_type)
        c.argument('sync_group_name', sync_group_name_type)

    with self.argument_context('storagesync sync-group server-endpoint wait') as c:
        c.argument('server_endpoint_name', server_endpoint_name_type, options_list=['--name', '-n'])

    with self.argument_context('storagesync registered-server delete') as c:
        c.argument('resource_group_name', custom_resource_group_name_type)
        c.argument('storage_sync_service_name', storage_sync_service_type)
        c.argument('server_id', server_id_type)

    with self.argument_context('storagesync registered-server show') as c:
        c.argument('resource_group_name', custom_resource_group_name_type)
        c.argument('storage_sync_service_name', storage_sync_service_type)
        c.argument('server_id', server_id_type)

    with self.argument_context('storagesync registered-server list') as c:
        c.argument('resource_group_name', custom_resource_group_name_type)
        c.argument('storage_sync_service_name', storage_sync_service_type)
