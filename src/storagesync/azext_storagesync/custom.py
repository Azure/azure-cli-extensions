# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument
from azure.cli.core.util import sdk_no_wait


def create_storagesync_storage_sync_service(client,
                                            resource_group_name,
                                            storage_sync_service_name,
                                            tags=None,
                                            location=None):
    body = {}
    body['location'] = location  # str
    body['tags'] = tags  # dictionary
    return client.create(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, parameters=body)


def delete_storagesync_storage_sync_service(client,
                                            resource_group_name,
                                            storage_sync_service_name):
    return client.delete(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name)


def get_storagesync_storage_sync_service(client,
                                         resource_group_name,
                                         storage_sync_service_name):
    return client.get(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name)


def list_storagesync_storage_sync_service(client,
                                          resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()


def create_storagesync_sync_group(client,
                                  resource_group_name,
                                  storage_sync_service_name,
                                  sync_group_name):
    return client.create(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name)


def delete_storagesync_sync_group(client,
                                  resource_group_name,
                                  storage_sync_service_name,
                                  sync_group_name):
    return client.delete(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name)


def get_storagesync_sync_group(client,
                               resource_group_name,
                               storage_sync_service_name,
                               sync_group_name):
    return client.get(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name)


def list_storagesync_sync_group(client,
                                resource_group_name,
                                storage_sync_service_name):
    return client.list_by_storage_sync_service(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name)


def create_storagesync_cloud_endpoint(client,
                                      resource_group_name,
                                      storage_sync_service_name,
                                      sync_group_name,
                                      cloud_endpoint_name,
                                      storage_account_resource_id=None,
                                      azure_file_share_name=None,
                                      storage_account_tenant_id=None,
                                      no_wait=False):
    body = {}
    body['storage_account_resource_id'] = storage_account_resource_id  # str
    body['azure_file_share_name'] = azure_file_share_name  # str
    body['storage_account_tenant_id'] = storage_account_tenant_id  # str
    return sdk_no_wait(no_wait, client.create, resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name, cloud_endpoint_name=cloud_endpoint_name, parameters=body)


def delete_storagesync_cloud_endpoint(client,
                                      resource_group_name,
                                      storage_sync_service_name,
                                      sync_group_name,
                                      cloud_endpoint_name,
                                      no_wait=False):
    return sdk_no_wait(no_wait, client.delete, resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name, cloud_endpoint_name=cloud_endpoint_name)


def get_storagesync_cloud_endpoint(client,
                                   resource_group_name,
                                   storage_sync_service_name,
                                   sync_group_name,
                                   cloud_endpoint_name):
    return client.get(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name, cloud_endpoint_name=cloud_endpoint_name)


def list_storagesync_cloud_endpoint(client,
                                    resource_group_name,
                                    storage_sync_service_name,
                                    sync_group_name):
    return client.list_by_sync_group(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name)


def create_storagesync_server_endpoint(client,
                                       resource_group_name,
                                       storage_sync_service_name,
                                       sync_group_name,
                                       server_endpoint_name,
                                       server_resource_id,
                                       server_local_path,
                                       cloud_tiering=None,
                                       volume_free_space_percent=None,
                                       tier_files_older_than_days=None,
                                       offline_data_transfer=None,
                                       offline_data_transfer_share_name=None,
                                       no_wait=False):
    body = {}
    body['server_resource_id'] = server_resource_id  # str
    body['server_local_path'] = server_local_path  # str
    body['cloud_tiering'] = cloud_tiering  # str
    body['volume_free_space_percent'] = volume_free_space_percent  # int
    body['tier_files_older_than_days'] = tier_files_older_than_days  # int
    body['offline_data_transfer'] = offline_data_transfer  # str
    body['offline_data_transfer_share_name'] = offline_data_transfer_share_name  # str
    return sdk_no_wait(no_wait, client.create, resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name, server_endpoint_name=server_endpoint_name, parameters=body)


def update_storagesync_server_endpoint(client,
                                       resource_group_name,
                                       storage_sync_service_name,
                                       sync_group_name,
                                       server_endpoint_name,
                                       cloud_tiering=None,
                                       volume_free_space_percent=None,
                                       tier_files_older_than_days=None,
                                       offline_data_transfer=None,
                                       offline_data_transfer_share_name=None,
                                       no_wait=False):
    body = {}
    if cloud_tiering is not None:
        body['cloud_tiering'] = cloud_tiering  # str
    if volume_free_space_percent is not None:
        body['volume_free_space_percent'] = volume_free_space_percent  # number
    if tier_files_older_than_days is not None:
        body['tier_files_older_than_days'] = tier_files_older_than_days  # number
    if offline_data_transfer is not None:
        body['offline_data_transfer'] = offline_data_transfer  # str
    if offline_data_transfer_share_name is not None:
        body['offline_data_transfer_share_name'] = offline_data_transfer_share_name  # str
    return sdk_no_wait(no_wait, client.update, resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name, server_endpoint_name=server_endpoint_name, parameters=body)


def delete_storagesync_server_endpoint(client,
                                       resource_group_name,
                                       storage_sync_service_name,
                                       sync_group_name,
                                       server_endpoint_name,
                                       no_wait=False):
    return sdk_no_wait(no_wait, client.delete, resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name, server_endpoint_name=server_endpoint_name)


def get_storagesync_server_endpoint(client,
                                    resource_group_name,
                                    storage_sync_service_name,
                                    sync_group_name,
                                    server_endpoint_name):
    return client.get(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name, server_endpoint_name=server_endpoint_name)


def list_storagesync_server_endpoint(client,
                                     resource_group_name,
                                     storage_sync_service_name,
                                     sync_group_name):
    return client.list_by_sync_group(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name)


def delete_storagesync_registered_server(client,
                                         resource_group_name,
                                         storage_sync_service_name,
                                         server_id,
                                         no_wait=False):
    return sdk_no_wait(no_wait, client.delete, resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, server_id=server_id)


def get_storagesync_registered_server(client,
                                      resource_group_name,
                                      storage_sync_service_name,
                                      server_id):
    return client.get(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, server_id=server_id)


def list_storagesync_registered_server(client,
                                       resource_group_name,
                                       storage_sync_service_name):
    return client.list_by_storage_sync_service(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name)
