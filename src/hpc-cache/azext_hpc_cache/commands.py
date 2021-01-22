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
    from ._client_factory import cf_skus
    hpc_cache_skus = CliCommandType(
        operations_tmpl='azext_hpc_cache.vendored_sdks.storagecache.operations._skus_operations#SkusOperations.{}',
        client_factory=cf_skus)
    with self.command_group('hpc-cache skus', hpc_cache_skus, client_factory=cf_skus) as g:
        g.custom_command('list', 'list_hpc_cache_skus')

    from ._client_factory import cf_usage_models
    hpc_cache_usage_models = CliCommandType(
        operations_tmpl='azext_hpc_cache.vendored_sdks.storagecache.operations._usage_models_operations#UsageModelsOperations.{}',
        client_factory=cf_usage_models)
    with self.command_group('hpc-cache usage-model', hpc_cache_usage_models, client_factory=cf_usage_models) as g:
        g.custom_command('list', 'list_hpc_cache_usage_model')

    from ._client_factory import cf_caches
    hpc_cache_caches = CliCommandType(
        operations_tmpl='azext_hpc_cache.vendored_sdks.storagecache.operations._caches_operations#CachesOperations.{}',
        client_factory=cf_caches)
    with self.command_group('hpc-cache', hpc_cache_caches, client_factory=cf_caches) as g:
        g.custom_command('create', 'create_hpc_cache', supports_no_wait=True)
        g.custom_command('update', 'update_hpc_cache')
        g.custom_command('delete', 'delete_hpc_cache', supports_no_wait=True)
        g.custom_show_command('show', 'get_hpc_cache')
        g.custom_command('list', 'list_hpc_cache')
        g.custom_command('flush', 'flush_hpc_cache')
        g.custom_command('start', 'start_hpc_cache', supports_no_wait=True)
        g.custom_command('stop', 'stop_hpc_cache', supports_no_wait=True)
        g.custom_command('upgrade-firmware', 'upgrade_firmware_hpc_cache')
        g.wait_command('wait')

    from ._client_factory import cf_storage_targets
    hpc_cache_storage_targets = CliCommandType(
        operations_tmpl='azext_hpc_cache.vendored_sdks.storagecache.operations._storage_targets_operations#StorageTargetsOperations.{}',
        client_factory=cf_storage_targets)
    with self.command_group('hpc-cache blob-storage-target', hpc_cache_storage_targets, client_factory=cf_storage_targets) as g:
        g.custom_command('add', 'create_hpc_cache_blob_storage_target')
        g.custom_command('update', 'update_hpc_cache_blob_storage_target')

    with self.command_group('hpc-cache storage-target', hpc_cache_storage_targets, client_factory=cf_storage_targets) as g:
        g.custom_command('remove', 'delete_hpc_cache_storage_target')
        g.custom_show_command('show', 'get_hpc_cache_storage_target')
        g.custom_command('list', 'list_hpc_cache_storage_target')

    with self.command_group('hpc-cache nfs-storage-target', hpc_cache_storage_targets, client_factory=cf_storage_targets) as g:
        g.custom_command('add', 'create_hpc_cache_nfs_storage_target')
        g.custom_command('update', 'update_hpc_cache_nfs_storage_target')

    with self.command_group('hpc-cache', is_experimental=True) as g:
        pass
