# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import argparse
from knack.util import CLIError

# pylint: disable=unused-argument


def transfer_cache_name(cmd, namespace):
    namespace.cache_name = namespace.name
    del namespace.name


def process_container_resource(cmd, namespace):
    """Processes the resource group parameter from the storage account and container name"""
    if not namespace.storage_account or not namespace.container_name:
        raise ValueError('usage error: Please specify --storage-account and --container-name for blob-storage-target')
    from msrestazure.tools import is_valid_resource_id
    if not is_valid_resource_id(namespace.storage_account):
        raise ValueError('usage error: {} is not a valid resource id'.format(namespace.storage_account))
    namespace.clfs_target = '{}/blobServices/default/containers/{}'.format(
        namespace.storage_account, namespace.container_name)
    del namespace.storage_account
    del namespace.container_name


# pylint: disable=protected-access
# pylint: disable=too-few-public-methods
class JunctionAddAction(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        if not namespace.junctions:
            del namespace.junction
            namespace.junctions = []
        kwargs = {}
        for item in values:
            try:
                key, value = item.split('=', 1)
                kwargs[key] = value
            except ValueError:
                raise CLIError('usage error: {} KEY=VALUE [KEY=VALUE ...]'.format(option_string))
        if 'namespace-path' not in kwargs:
            raise CLIError('usage error: namespace-path cannot be empty in --junction')
        if 'nfs-export' not in kwargs:
            raise CLIError('usage error: nfs-export cannot be empty in --junction')
        junction = {'namespacePath': kwargs['namespace-path'], 'nfsExport': kwargs['nfs-export']}
        if 'target-path' in kwargs:
            junction['targetPath'] = kwargs['target-path']
        namespace.junctions.append(junction)
