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
from ._validators import process_container_resource, JunctionAddAction, validate_storage_account_name_or_id
from knack.arguments import CLIArgumentType

junction_type = CLIArgumentType(options_list=['--junction'],
                                help='List of Cache namespace junctions to target for namespace associations.'
                                     'The sub parameters contains: '
                                     '(1) --namespace-path: Namespace path on a Cache for a Storage Target '
                                     '(2) --nfs-export: NFS export where targetPath exists '
                                     '(3) --target-path(Optional): Path in Storage Target to '
                                     'which namespacePath points',
                                action=JunctionAddAction, nargs='+')

storage_account_type = CLIArgumentType(options_list=['--storage-account'],
                                       help='Resource ID or Name of target storage account.',
                                       validator=validate_storage_account_name_or_id)

cache_name_type = CLIArgumentType(help='Name of Cache.')

storage_target_type = CLIArgumentType(help='Name of the Storage Target.')


def load_arguments(self, _):

    with self.argument_context('hpc-cache create') as c:
        c.argument('name', cache_name_type, required=True)
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=True)
        c.argument('cache_size_gb', help='The size of this Cache, in GB.', required=True)
        c.argument('subnet', help='Subnet used for the Cache.', required=True)
        c.argument('sku_name', help='SKU name for this Cache.', required=True)

    with self.argument_context('hpc-cache update') as c:
        c.argument('name', cache_name_type)
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), deprecate_info=c.deprecate(hide=True))
        c.argument('cache_size_gb', help='The size of this Cache, in GB.', deprecate_info=c.deprecate(hide=True))
        c.argument('subnet', help='Subnet used for the Cache.', deprecate_info=c.deprecate(hide=True))
        c.argument('sku_name', help='SKU name for this Cache.', deprecate_info=c.deprecate(hide=True))

    for item in ['delete', 'show', 'flush', 'start', 'stop', 'upgrade-firmware']:
        with self.argument_context('hpc-cache {}'.format(item)) as c:
            c.argument('name', cache_name_type)

    with self.argument_context('hpc-cache wait') as c:
        c.argument('cache_name', cache_name_type, options_list=['--name', '-n'], required=True)

    with self.argument_context('hpc-cache blob-storage-target add') as c:
        c.argument('cache_name', cache_name_type)
        c.argument('name', storage_target_type)
        c.argument('virtual_namespace_path', options_list=['--virtual-namespace-path', '-v'], required=True,
                   help='Path to create for this storage target in the client-facing virtual filesystem.')
        c.extra('storage_account', storage_account_type, required=True)
        c.extra('container_name', options_list=['--container-name'], validator=process_container_resource,
                required=True, help='Name of target storage container.')
        c.ignore('clfs_target')

    with self.argument_context('hpc-cache blob-storage-target update') as c:
        c.argument('cache_name', cache_name_type)
        c.argument('name', storage_target_type)
        c.argument('virtual_namespace_path', options_list=['--virtual-namespace-path', '-v'],
                   help='Path to create for this storage target in the client-facing virtual filesystem.')
        c.extra('storage_account', storage_account_type)
        c.extra('container_name', options_list=['--container-name'], validator=process_container_resource,
                help='Name of target storage container.')
        c.ignore('clfs_target')

    with self.argument_context('hpc-cache storage-target remove') as c:
        c.argument('cache_name', cache_name_type)
        c.argument('name', storage_target_type)

    with self.argument_context('hpc-cache storage-target show') as c:
        c.argument('cache_name', cache_name_type)
        c.argument('name', storage_target_type)

    with self.argument_context('hpc-cache storage-target list') as c:
        c.argument('cache_name', cache_name_type)

    with self.argument_context('hpc-cache nfs-storage-target add') as c:
        c.argument('cache_name', cache_name_type)
        c.argument('name', storage_target_type)

        c.argument('junctions', junction_type, required=True)
        c.argument('nfs3_target', help='IP address or host name of an NFSv3 host (e.g., 10.0.44.44).', required=True)
        c.argument('nfs3_usage_model', help='Identifies the primary usage model to be used for this Storage Target.',
                   required=True)

    with self.argument_context('hpc-cache nfs-storage-target update') as c:
        c.argument('cache_name', cache_name_type)
        c.argument('name', storage_target_type)
        c.argument('junctions', junction_type)
        c.argument('nfs3_target', help='IP address or host name of an NFSv3 host (e.g., 10.0.44.44).')
        c.argument('nfs3_usage_model', help='Identifies the primary usage model to be used for this Storage Target.')
