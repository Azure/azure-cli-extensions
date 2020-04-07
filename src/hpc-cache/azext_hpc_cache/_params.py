# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    resource_group_name_type,
    get_location_type
)
from ._validators import process_container_resource, transfer_cache_name


def load_arguments(self, _):

    with self.argument_context('hpc-cache skus list') as c:
        pass

    with self.argument_context('hpc-cache usage-model list') as c:
        pass

    with self.argument_context('hpc-cache create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('name', help='Name of Cache.', required=True)
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=True)
        c.argument('cache_size_gb', help='The size of this Cache, in GB.', required=True)
        c.argument('subnet', help='Subnet used for the Cache.', required=True)
        c.argument('sku_name', help='SKU name for this Cache.', required=True)

    with self.argument_context('hpc-cache update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('name', help='Name of Cache.')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('cache_size_gb', help='The size of this Cache, in GB.')
        c.argument('subnet', help='Subnet used for the Cache.')
        c.argument('sku_name', help='SKU name for this Cache.')

    with self.argument_context('hpc-cache delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('name', help='Name of Cache.')

    with self.argument_context('hpc-cache show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('name', help='Name of Cache.')

    with self.argument_context('hpc-cache wait') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.extra('name', help='Name of Cache.', validator=transfer_cache_name, required=True)
        c.ignore('cache_name')

    with self.argument_context('hpc-cache list') as c:
        c.argument('resource_group_name', resource_group_name_type, required=False)

    with self.argument_context('hpc-cache flush') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('name', help='Name of Cache.')

    with self.argument_context('hpc-cache start') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('name', help='Name of Cache.')

    with self.argument_context('hpc-cache stop') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('name', help='Name of Cache.')

    with self.argument_context('hpc-cache upgrade-firmware') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('name', help='Name of Cache.')

    with self.argument_context('hpc-cache blob-storage-target add') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('cache_name', help='Name of Cache.')
        c.argument('name', help='Name of the Storage Target.')
        c.argument('virtual_namespace_path', options_list=['--virtual-namespace-path', '-v'], required=True,
                   help='Path to create for this storage target in the client-facing virtual filesystem.')
        c.extra('storage_account', options_list=['--storage-account'], help='Resource ID of target storage account.',
                required=True)
        c.extra('container_name', options_list=['--container-name'], validator=process_container_resource,
                required=True, help='Name of target storage container.')
        c.ignore('clfs_target')

    with self.argument_context('hpc-cache blob-storage-target update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('cache_name', help='Name of Cache.')
        c.argument('name', help='Name of the Storage Target.')
        c.argument('virtual_namespace_path', options_list=['--virtual-namespace-path', '-v'],
                   help='Path to create for this storage target in the client-facing virtual filesystem.')
        c.extra('storage_account', options_list=['--storage-account'],
                help='Resource ID of target storage account.')
        c.extra('container_name', options_list=['--container-name'], validator=process_container_resource,
                help='Name of target storage container.')
        c.ignore('clfs_target')

    with self.argument_context('hpc-cache storage-target remove') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('cache_name', help='Name of Cache.')
        c.argument('name', help='Name of the Storage Target.')

    with self.argument_context('hpc-cache storage-target show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('cache_name', help='Name of Cache.')
        c.argument('name', help='Name of the Storage Target.')

    with self.argument_context('hpc-cache storage-target list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('cache_name', help='Name of Cache.')

    with self.argument_context('hpc-cache nfs-storage-target add') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('cache_name', help='Name of Cache.')
        c.argument('name', help='Name of the Storage Target.')
        from ._validators import JunctionAddAction
        c.extra('junction', help='List of Cache namespace junctions to target for namespace associations.',
                action=JunctionAddAction, nargs='+', required=True)
        c.argument('nfs3_target', help='IP address or host name of an NFSv3 host (e.g., 10.0.44.44).', required=True)
        c.argument('nfs3_usage_model', help='Identifies the primary usage model to be used for this Storage Target.',
                   required=True)
        c.ignore('junctions')

    with self.argument_context('hpc-cache nfs-storage-target update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('cache_name', help='Name of Cache.')
        c.argument('name', help='Name of the Storage Target.')
        from ._validators import JunctionAddAction
        c.extra('junction', help='List of Cache namespace junctions to target for namespace associations.', action=JunctionAddAction, nargs='+')
        c.argument('nfs3_target', help='IP address or host name of an NFSv3 host (e.g., 10.0.44.44).')
        c.argument('nfs3_usage_model', help='Identifies the primary usage model to be used for this Storage Target.')
        c.ignore('junctions')
