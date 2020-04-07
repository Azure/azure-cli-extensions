# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from ._client_factory import cf_storage_sync_services
    storagesync_storage_sync_services = CliCommandType(
        operations_tmpl='azext_storagesync.vendored_sdks.storagesync.operations._storage_sync_services_operations#StorageSyncServicesOperations.{}',
        client_factory=cf_storage_sync_services)
    with self.command_group('storagesync', storagesync_storage_sync_services, client_factory=cf_storage_sync_services) as g:
        g.custom_command('create', 'create_storagesync_storage_sync_service')
        g.custom_command('delete', 'delete_storagesync_storage_sync_service', confirmation=True)
        g.custom_show_command('show', 'get_storagesync_storage_sync_service')
        g.custom_command('list', 'list_storagesync_storage_sync_service')

    from ._client_factory import cf_sync_groups
    storagesync_sync_groups = CliCommandType(
        operations_tmpl='azext_storagesync.vendored_sdks.storagesync.operations._sync_groups_operations#SyncGroupsOperations.{}',
        client_factory=cf_sync_groups)
    with self.command_group('storagesync sync-group', storagesync_sync_groups, client_factory=cf_sync_groups) as g:
        g.custom_command('create', 'create_storagesync_sync_group')
        g.custom_command('delete', 'delete_storagesync_sync_group', confirmation=True)
        g.custom_show_command('show', 'get_storagesync_sync_group')
        g.custom_command('list', 'list_storagesync_sync_group')

    from ._client_factory import cf_cloud_endpoints
    storagesync_cloud_endpoints = CliCommandType(
        operations_tmpl='azext_storagesync.vendored_sdks.storagesync.operations._cloud_endpoints_operations#CloudEndpointsOperations.{}',
        client_factory=cf_cloud_endpoints)
    with self.command_group('storagesync sync-group cloud-endpoint', storagesync_cloud_endpoints, client_factory=cf_cloud_endpoints) as g:
        g.custom_command('create', 'create_storagesync_cloud_endpoint', supports_no_wait=True)
        g.custom_command('delete', 'delete_storagesync_cloud_endpoint', supports_no_wait=True, confirmation=True)
        g.custom_show_command('show', 'get_storagesync_cloud_endpoint')
        g.custom_command('list', 'list_storagesync_cloud_endpoint')
        g.wait_command('wait')

    from ._client_factory import cf_server_endpoints
    storagesync_server_endpoints = CliCommandType(
        operations_tmpl='azext_storagesync.vendored_sdks.storagesync.operations._server_endpoints_operations#ServerEndpointsOperations.{}',
        client_factory=cf_server_endpoints)
    with self.command_group('storagesync sync-group server-endpoint', storagesync_server_endpoints, client_factory=cf_server_endpoints) as g:
        g.custom_command('create', 'create_storagesync_server_endpoint', supports_no_wait=True)
        g.custom_command('update', 'update_storagesync_server_endpoint', supports_no_wait=True)
        g.custom_command('delete', 'delete_storagesync_server_endpoint', supports_no_wait=True, confirmation=True)
        g.custom_show_command('show', 'get_storagesync_server_endpoint')
        g.custom_command('list', 'list_storagesync_server_endpoint')
        g.wait_command('wait')

    from ._client_factory import cf_registered_servers
    storagesync_registered_servers = CliCommandType(
        operations_tmpl='azext_storagesync.vendored_sdks.storagesync.operations._registered_servers_operations#RegisteredServersOperations.{}',
        client_factory=cf_registered_servers)
    with self.command_group('storagesync registered-server', storagesync_registered_servers, client_factory=cf_registered_servers) as g:
        g.custom_command('delete', 'delete_storagesync_registered_server', supports_no_wait=True, confirmation=True)
        g.custom_show_command('show', 'get_storagesync_registered_server')
        g.custom_command('list', 'list_storagesync_registered_server')
        g.wait_command('wait')

    with self.command_group('storagesync', is_experimental=True) as g:
        pass
