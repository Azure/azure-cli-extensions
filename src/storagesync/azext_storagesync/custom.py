# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument
import uuid

import pythoncom
import win32com.client

import abc


class IEcsManagement(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def register_sync_server(self, service_uri, subscription_id, storage_sync_service_name, resource_group_name,
                             certificate_provider_name, certificate_hash_algorithm, certificate_key_length,
                             monitoring_data_path):
        return


class EcsManagementInteropClient(IEcsManagement):
    _reg_clsid_ = "{41E24E95-D45A-11D2-852C-204C4F4F5020}"

    def __init__(self):
        clsid = pythoncom.MakeIID('{3EC1199D-20EB-40C0-8294-EB684E89AB2B}')
        iid = pythoncom.MakeIID('{F29EAB44-2C63-4ACE-8C05-67C2203CBED2}')
        mgmt_object = pythoncom.CoCreateInstance(clsid, None, pythoncom.CLSCTX_LOCAL_SERVER, iid)

    def register_sync_server(self, service_uri, subscription_id, storage_sync_service_name, resource_group_name,
                             certificate_provider_name, certificate_hash_algorithm, certificate_key_length,
                             monitoring_data_path):
        return


def create_storagesync_storage_sync_service(client,
                                            resource_group_name,
                                            storage_sync_service_name,
                                            location=None,
                                            tags=None):
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
    if resource_group_name is not None:
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
                                      storage_account_tenant_id=None):
    body = {}
    body['storage_account_resource_id'] = storage_account_resource_id  # str
    body['azure_file_share_name'] = azure_file_share_name  # str
    body['storage_account_tenant_id'] = storage_account_tenant_id  # str
    return client.create(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name, cloud_endpoint_name=cloud_endpoint_name, parameters=body)


def delete_storagesync_cloud_endpoint(client,
                                      resource_group_name,
                                      storage_sync_service_name,
                                      sync_group_name,
                                      cloud_endpoint_name):
    return client.delete(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name, cloud_endpoint_name=cloud_endpoint_name)


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
                                       offline_data_transfer_share_name=None):
    body = {}
    body['server_resource_id'] = server_resource_id  # str
    body['server_local_path'] = server_local_path  # str
    body['cloud_tiering'] = cloud_tiering  # str
    body['volume_free_space_percent'] = volume_free_space_percent  # number
    body['tier_files_older_than_days'] = tier_files_older_than_days  # number
    body['offline_data_transfer'] = offline_data_transfer  # str
    body['offline_data_transfer_share_name'] = offline_data_transfer_share_name  # str
    return client.create(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name, server_endpoint_name=server_endpoint_name, parameters=body)


def update_storagesync_server_endpoint(client,
                                       resource_group_name,
                                       storage_sync_service_name,
                                       sync_group_name,
                                       server_endpoint_name,
                                       cloud_tiering=None,
                                       volume_free_space_percent=None,
                                       tier_files_older_than_days=None,
                                       offline_data_transfer=None,
                                       offline_data_transfer_share_name=None):
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
    return client.update(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name, server_endpoint_name=server_endpoint_name, parameters=body)


def delete_storagesync_server_endpoint(client,
                                       resource_group_name,
                                       storage_sync_service_name,
                                       sync_group_name,
                                       server_endpoint_name):
    return client.delete(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name, server_endpoint_name=server_endpoint_name)


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


def create_storagesync_registered_server(client,
                                         resource_group_name,
                                         storage_sync_service_name):
    body = {}
    xl = win32com.client.Dispatch("Excel.Application")
    mgmt_object = pythoncom.CoCreateInstance(uuid.UUID('{3EC1199D-20EB-40C0-8294-EB684E89AB2B}'), None, pythoncom.CLSCTX_LOCAL_SERVER,
                               uuid.UUID('{F29EAB44-2C63-4ACE-8C05-67C2203CBED2}'))
    # Generate from local call
    server_id = None
    server_certificate = None,
    agent_version = None,
    server_osversion = None,
    last_heart_beat = None,
    server_role = None,
    cluster_id = None,
    cluster_name = None,
    friendly_name = None
    # Generate from local call
    body['server_certificate'] = server_certificate  # str
    body['agent_version'] = agent_version  # str
    body['server_osversion'] = server_osversion  # str
    body['last_heart_beat'] = last_heart_beat  # str
    body['server_role'] = server_role  # str
    body['cluster_id'] = cluster_id  # str
    body['cluster_name'] = cluster_name  # str
    body['friendly_name'] = friendly_name  # str
    return client.create(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, server_id=server_id, parameters=body)


def delete_storagesync_registered_server(client,
                                         resource_group_name,
                                         storage_sync_service_name,
                                         server_id):
    return client.delete(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, server_id=server_id)


def get_storagesync_registered_server(client,
                                      resource_group_name,
                                      storage_sync_service_name,
                                      server_id):
    return client.get(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name, server_id=server_id)


def list_storagesync_registered_server(client,
                                       resource_group_name,
                                       storage_sync_service_name):
    return client.list_by_storage_sync_service(resource_group_name=resource_group_name, storage_sync_service_name=storage_sync_service_name)


def rollover_certificate_storagesync_registered_server(client,
                                                       resource_group,
                                                       storage_sync_service_name):
    body = {}
    server_id = None  # Generate from local call
    return client.trigger_rollover(resource_group_name=resource_group, storage_sync_service_name=storage_sync_service_name, server_id=server_id, parameters=body)
