# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


def create_storagesync_storage_sync_service(cmd, client,
                                            resource_group,
                                            name,
                                            location,
                                            tags=None,
                                            properties=None):
    body = {}
    body['location'] = location  # str
    body['tags'] = tags  # dictionary
    body['properties'] = properties  # unknown-primary[object]
    return client.create(resource_group_name=resource_group, storage_sync_service_name=name, parameters=body)


def update_storagesync_storage_sync_service(cmd, client,
                                            resource_group,
                                            name,
                                            location=None,
                                            tags=None,
                                            properties=None):
    body = {}
    if location is not None:
        body['location'] = location  # str
    if tags is not None:
        body['tags'] = tags  # dictionary
    if properties is not None:
        body['properties'] = properties  # unknown-primary[object]
    return client.create(resource_group_name=resource_group, storage_sync_service_name=name, parameters=body)


def delete_storagesync_storage_sync_service(cmd, client,
                                            resource_group,
                                            name):
    return client.delete(resource_group_name=resource_group, storage_sync_service_name=name)


def get_storagesync_storage_sync_service(cmd, client,
                                         resource_group,
                                         name):
    return client.get(resource_group_name=resource_group, storage_sync_service_name=name)


def list_storagesync_storage_sync_service(cmd, client,
                                          resource_group=None):
    if resource_group is not None:
        return client.list_by_resource_group(resource_group_name=resource_group)
    return client.list_by_subscription()


def check_name_availability_storagesync_storage_sync_service(cmd, client,
                                                             location_name,
                                                             name,
                                                             _type):
    body = {}
    body['name'] = name  # str
    body['type'] = _type  # str
    return client.check_name_availability(location_name=location_name, parameters=body)


def create_storagesync_sync_group(cmd, client,
                                  resource_group,
                                  storage_sync_service_name,
                                  name,
                                  properties=None):
    return client.create(resource_group_name=resource_group, storage_sync_service_name=storage_sync_service_name, sync_group_name=name, properties=properties)


def update_storagesync_sync_group(cmd, client,
                                  resource_group,
                                  storage_sync_service_name,
                                  name,
                                  properties=None):
    return client.create(resource_group_name=resource_group, storage_sync_service_name=storage_sync_service_name, sync_group_name=name, properties=properties)


def delete_storagesync_sync_group(cmd, client,
                                  resource_group,
                                  storage_sync_service_name,
                                  name):
    return client.delete(resource_group_name=resource_group, storage_sync_service_name=storage_sync_service_name, sync_group_name=name)


def get_storagesync_sync_group(cmd, client,
                               resource_group,
                               storage_sync_service_name,
                               name):
    return client.get(resource_group_name=resource_group, storage_sync_service_name=storage_sync_service_name, sync_group_name=name)


def list_storagesync_sync_group(cmd, client,
                                resource_group,
                                storage_sync_service_name):
    return client.list_by_storage_sync_service(resource_group_name=resource_group, storage_sync_service_name=storage_sync_service_name)


def create_storagesync_cloud_endpoint(cmd, client,
                                      resource_group,
                                      storage_sync_service_name,
                                      sync_group_name,
                                      name,
                                      storage_account_resource_id=None,
                                      azure_file_share_name=None,
                                      storage_account_tenant_id=None,
                                      friendly_name=None):
    body = {}
    body['storage_account_resource_id'] = storage_account_resource_id  # str
    body['azure_file_share_name'] = azure_file_share_name  # str
    body['storage_account_tenant_id'] = storage_account_tenant_id  # str
    body['friendly_name'] = friendly_name  # str
    return client.create(resource_group_name=resource_group, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name, cloud_endpoint_name=name, parameters=body)


def update_storagesync_cloud_endpoint(cmd, client,
                                      resource_group,
                                      storage_sync_service_name,
                                      sync_group_name,
                                      name,
                                      storage_account_resource_id=None,
                                      azure_file_share_name=None,
                                      storage_account_tenant_id=None,
                                      friendly_name=None):
    body = {}
    if storage_account_resource_id is not None:
        body['storage_account_resource_id'] = storage_account_resource_id  # str
    if azure_file_share_name is not None:
        body['azure_file_share_name'] = azure_file_share_name  # str
    if storage_account_tenant_id is not None:
        body['storage_account_tenant_id'] = storage_account_tenant_id  # str
    if friendly_name is not None:
        body['friendly_name'] = friendly_name  # str
    return client.create(resource_group_name=resource_group, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name, cloud_endpoint_name=name, parameters=body)


def delete_storagesync_cloud_endpoint(cmd, client,
                                      resource_group,
                                      storage_sync_service_name,
                                      sync_group_name,
                                      name):
    return client.delete(resource_group_name=resource_group, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name, cloud_endpoint_name=name)


def get_storagesync_cloud_endpoint(cmd, client,
                                   resource_group,
                                   storage_sync_service_name,
                                   sync_group_name,
                                   name):
    return client.get(resource_group_name=resource_group, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name, cloud_endpoint_name=name)


def list_storagesync_cloud_endpoint(cmd, client,
                                    resource_group,
                                    storage_sync_service_name,
                                    sync_group_name):
    return client.list_by_sync_group(resource_group_name=resource_group, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name)


def trigger_change_detection_storagesync_cloud_endpoint(cmd, client,
                                                        resource_group,
                                                        storage_sync_service_name,
                                                        sync_group_name,
                                                        name,
                                                        azure_file_share=None,
                                                        partition=None,
                                                        replica_group=None,
                                                        request_id=None,
                                                        azure_file_share_uri=None,
                                                        status=None,
                                                        source_azure_file_share_uri=None,
                                                        backup_metadata_property_bag=None,
                                                        restore_file_spec=None,
                                                        pause_wait_for_sync_drain_time_period_in_seconds=None,
                                                        failed_file_list=None,
                                                        directory_path=None,
                                                        change_detection_mode=None,
                                                        paths=None):
    body = {}
    body['azure_file_share'] = azure_file_share  # str
    body['partition'] = partition  # str
    body['replica_group'] = replica_group  # str
    body['request_id'] = request_id  # str
    body['azure_file_share_uri'] = azure_file_share_uri  # str
    body['status'] = status  # str
    body['source_azure_file_share_uri'] = source_azure_file_share_uri  # str
    body['backup_metadata_property_bag'] = backup_metadata_property_bag  # str
    body['restore_file_spec'] = restore_file_spec
    body['pause_wait_for_sync_drain_time_period_in_seconds'] = pause_wait_for_sync_drain_time_period_in_seconds  # number
    body['failed_file_list'] = failed_file_list  # str
    body['directory_path'] = directory_path  # str
    body['change_detection_mode'] = change_detection_mode  # str
    body['paths'] = None if paths is None else paths
    return client.trigger_change_detection(resource_group_name=resource_group, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name, cloud_endpoint_name=name, parameters=body)


def create_storagesync_server_endpoint(cmd, client,
                                       resource_group,
                                       storage_sync_service_name,
                                       sync_group_name,
                                       name,
                                       cloud_tiering=None,
                                       volume_free_space_percent=None,
                                       tier_files_older_than_days=None,
                                       offline_data_transfer=None,
                                       offline_data_transfer_share_name=None):
    body = {}
    body['cloud_tiering'] = cloud_tiering  # str
    body['volume_free_space_percent'] = volume_free_space_percent  # number
    body['tier_files_older_than_days'] = tier_files_older_than_days  # number
    body['offline_data_transfer'] = offline_data_transfer  # str
    body['offline_data_transfer_share_name'] = offline_data_transfer_share_name  # str
    return client.create(resource_group_name=resource_group, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name, server_endpoint_name=name, parameters=body)


def update_storagesync_server_endpoint(cmd, client,
                                       resource_group,
                                       storage_sync_service_name,
                                       sync_group_name,
                                       name,
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
    return client.create(resource_group_name=resource_group, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name, server_endpoint_name=name, parameters=body)


def delete_storagesync_server_endpoint(cmd, client,
                                       resource_group,
                                       storage_sync_service_name,
                                       sync_group_name,
                                       name):
    return client.delete(resource_group_name=resource_group, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name, server_endpoint_name=name)


def get_storagesync_server_endpoint(cmd, client,
                                    resource_group,
                                    storage_sync_service_name,
                                    sync_group_name,
                                    name):
    return client.get(resource_group_name=resource_group, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name, server_endpoint_name=name)


def list_storagesync_server_endpoint(cmd, client,
                                     resource_group,
                                     storage_sync_service_name,
                                     sync_group_name):
    return client.list_by_sync_group(resource_group_name=resource_group, storage_sync_service_name=storage_sync_service_name, sync_group_name=sync_group_name)


def create_storagesync_registered_server(cmd, client,
                                         resource_group,
                                         name,
                                         server_id,
                                         server_certificate=None,
                                         agent_version=None,
                                         server_osversion=None,
                                         last_heart_beat=None,
                                         server_role=None,
                                         cluster_id=None,
                                         cluster_name=None,
                                         friendly_name=None):
    body = {}
    body['server_certificate'] = server_certificate  # str
    body['agent_version'] = agent_version  # str
    body['server_osversion'] = server_osversion  # str
    body['last_heart_beat'] = last_heart_beat  # str
    body['server_role'] = server_role  # str
    body['cluster_id'] = cluster_id  # str
    body['cluster_name'] = cluster_name  # str
    body['friendly_name'] = friendly_name  # str
    return client.create(resource_group_name=resource_group, storage_sync_service_name=name, server_id=server_id, parameters=body)


def update_storagesync_registered_server(cmd, client,
                                         resource_group,
                                         name,
                                         server_id,
                                         server_certificate=None,
                                         agent_version=None,
                                         server_osversion=None,
                                         last_heart_beat=None,
                                         server_role=None,
                                         cluster_id=None,
                                         cluster_name=None,
                                         friendly_name=None):
    body = {}
    if server_certificate is not None:
        body['server_certificate'] = server_certificate  # str
    if agent_version is not None:
        body['agent_version'] = agent_version  # str
    if server_osversion is not None:
        body['server_osversion'] = server_osversion  # str
    if last_heart_beat is not None:
        body['last_heart_beat'] = last_heart_beat  # str
    if server_role is not None:
        body['server_role'] = server_role  # str
    if cluster_id is not None:
        body['cluster_id'] = cluster_id  # str
    if cluster_name is not None:
        body['cluster_name'] = cluster_name  # str
    if friendly_name is not None:
        body['friendly_name'] = friendly_name  # str
    return client.create(resource_group_name=resource_group, storage_sync_service_name=name, server_id=server_id, parameters=body)


def delete_storagesync_registered_server(cmd, client,
                                         resource_group,
                                         name,
                                         server_id):
    return client.delete(resource_group_name=resource_group, storage_sync_service_name=name, server_id=server_id)


def get_storagesync_registered_server(cmd, client,
                                      resource_group,
                                      name,
                                      server_id):
    return client.get(resource_group_name=resource_group, storage_sync_service_name=name, server_id=server_id)


def list_storagesync_registered_server(cmd, client,
                                       resource_group,
                                       name):
    return client.list_by_storage_sync_service(resource_group_name=resource_group, storage_sync_service_name=name)
