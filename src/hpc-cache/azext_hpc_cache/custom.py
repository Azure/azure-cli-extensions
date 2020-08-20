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


def list_hpc_cache_skus(client):
    return client.list()


def list_hpc_cache_usage_model(client):
    return client.list()


def create_hpc_cache(client,
                     resource_group_name,
                     name,
                     tags=None,
                     location=None,
                     cache_size_gb=None,
                     subnet=None,
                     sku_name=None,
                     no_wait=False):
    body = {}
    body['tags'] = tags  # unknown-primary[object]
    body['location'] = location  # str
    body['cache_size_gb'] = cache_size_gb  # number
    body['subnet'] = subnet  # str
    body.setdefault('sku', {})['name'] = sku_name  # str
    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name=resource_group_name, cache_name=name,
                       cache=body)


def update_hpc_cache(client,
                     resource_group_name,
                     name,
                     tags=None,
                     location=None,
                     cache_size_gb=None,
                     subnet=None,
                     sku_name=None):
    body = {}
    if tags is not None:
        body['tags'] = tags  # unknown-primary[object]
    client.config.generate_client_request_id = True
    return client.update(resource_group_name=resource_group_name, cache_name=name, cache=body)


def delete_hpc_cache(client,
                     resource_group_name,
                     name,
                     no_wait=False):
    return sdk_no_wait(no_wait, client.delete, resource_group_name=resource_group_name, cache_name=name)


def get_hpc_cache(client,
                  resource_group_name,
                  name):
    return client.get(resource_group_name=resource_group_name, cache_name=name)


def list_hpc_cache(client,
                   resource_group_name=None):
    if resource_group_name is None:
        return client.list()
    return client.list_by_resource_group(resource_group_name=resource_group_name)


def flush_hpc_cache(client,
                    resource_group_name,
                    name):
    return client.flush(resource_group_name=resource_group_name, cache_name=name)


def upgrade_firmware_hpc_cache(client,
                               resource_group_name,
                               name):
    return client.upgrade_firmware(resource_group_name=resource_group_name, cache_name=name)


def start_hpc_cache(client,
                    resource_group_name,
                    name,
                    no_wait=False):
    return sdk_no_wait(no_wait, client.start, resource_group_name=resource_group_name, cache_name=name)


def stop_hpc_cache(client,
                   resource_group_name,
                   name,
                   no_wait=False):
    return sdk_no_wait(no_wait, client.stop, resource_group_name=resource_group_name, cache_name=name)


def create_hpc_cache_blob_storage_target(client,
                                         resource_group_name,
                                         cache_name,
                                         name,
                                         virtual_namespace_path,
                                         clfs_target):
    body = {}
    body['junctions'] = [{'namespacePath': virtual_namespace_path, 'targetPath': '/'}]
    body['target_type'] = 'clfs'  # str
    body.setdefault('clfs', {})['target'] = clfs_target  # str
    return client.create_or_update(resource_group_name=resource_group_name, cache_name=cache_name,
                                   storage_target_name=name, storagetarget=body)


def create_hpc_cache_nfs_storage_target(client,
                                        resource_group_name,
                                        cache_name,
                                        name,
                                        junctions,
                                        nfs3_target,
                                        nfs3_usage_model):
    body = {}
    body['junctions'] = junctions
    body['target_type'] = 'nfs3'  # str
    body.setdefault('nfs3', {})['target'] = nfs3_target  # str
    body.setdefault('nfs3', {})['usage_model'] = nfs3_usage_model  # str
    return client.create_or_update(resource_group_name=resource_group_name, cache_name=cache_name,
                                   storage_target_name=name, storagetarget=body)


def update_hpc_cache_blob_storage_target(client,
                                         resource_group_name,
                                         cache_name,
                                         name,
                                         virtual_namespace_path=None,
                                         clfs_target=None):
    body = {}
    body['target_type'] = 'clfs'
    if virtual_namespace_path is not None:
        body['junctions'] = [{'namespacePath': virtual_namespace_path, 'targetPath': '/'}]
    if clfs_target is not None:
        body.setdefault('clfs', {})['target'] = clfs_target  # str
    return client.create_or_update(resource_group_name=resource_group_name, cache_name=cache_name,
                                   storage_target_name=name, storagetarget=body)


def update_hpc_cache_nfs_storage_target(client,
                                        resource_group_name,
                                        cache_name,
                                        name,
                                        junctions=None,
                                        nfs3_target=None,
                                        nfs3_usage_model=None):
    body = {}
    body['junctions'] = junctions
    body['target_type'] = 'nfs3'  # str
    body.setdefault('nfs3', {})['target'] = nfs3_target  # str
    body.setdefault('nfs3', {})['usage_model'] = nfs3_usage_model  # str
    return client.create_or_update(resource_group_name=resource_group_name, cache_name=cache_name,
                                   storage_target_name=name, storagetarget=body)


def delete_hpc_cache_storage_target(client,
                                    resource_group_name,
                                    cache_name,
                                    name):
    return client.delete(resource_group_name=resource_group_name, cache_name=cache_name, storage_target_name=name)


def get_hpc_cache_storage_target(client,
                                 resource_group_name,
                                 cache_name,
                                 name):
    return client.get(resource_group_name=resource_group_name, cache_name=cache_name, storage_target_name=name)


def list_hpc_cache_storage_target(client,
                                  resource_group_name,
                                  cache_name):
    return client.list_by_cache(resource_group_name=resource_group_name, cache_name=cache_name)
