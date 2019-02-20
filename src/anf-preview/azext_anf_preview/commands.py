# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from azure.cli.core.commands import CliCommandType
from ._client_factory import (
    accounts_mgmt_client_factory,
    pools_mgmt_client_factory,
    volumes_mgmt_client_factory,
    mount_targets_mgmt_client_factory,
    snapshots_mgmt_client_factory)
from ._exception_handler import netapp_exception_handler


def load_command_table(self, _):
    anf_accounts_sdk = CliCommandType(
        operations_tmpl='azext_anf_preview.vendored_sdks.operations.accounts_operations#AccountsOperations.{}',
        client_factory=accounts_mgmt_client_factory,
        exception_handler=netapp_exception_handler
    )

    anf_pools_sdk = CliCommandType(
        operations_tmpl='azext_anf_preview.vendored_sdks.operations.pools_operations#PoolsOperations.{}',
        client_factory=pools_mgmt_client_factory,
        exception_handler=netapp_exception_handler
    )

    anf_volumes_sdk = CliCommandType(
        operations_tmpl='azext_anf_preview.vendored_sdks.operations.volumes_operations#VolumesOperations.{}',
        client_factory=volumes_mgmt_client_factory,
        exception_handler=netapp_exception_handler
    )

    anf_mount_targets_sdk = CliCommandType(
        operations_tmpl='azext_anf_preview.vendored_sdks.operations.mount_targets_operations#MountTargetsOperations.{}',
        client_factory=mount_targets_mgmt_client_factory,
        exception_handler=netapp_exception_handler
    )

    anf_snapshots_sdk = CliCommandType(
        operations_tmpl='azext_anf_preview.vendored_sdks.operations.snapshots_operations#SnapshotsOperations.{}',
        client_factory=snapshots_mgmt_client_factory,
        exception_handler=netapp_exception_handler
    )

    with self.command_group('anf account', anf_accounts_sdk) as g:
        g.show_command('show', 'get')
        g.command('list', 'list')
        g.command('delete', 'delete')
        g.custom_command('create', 'create_account', client_factory=accounts_mgmt_client_factory,
                         doc_string_source='azext_anf_preview.vendored_sdks.models#NetAppAccount')
        g.generic_update_command('update', setter_name='update', custom_func_name='update_account',
                                 setter_arg_name='tags',
                                 doc_string_source='azext_anf_preview.vendored_sdks.models#NetAppAccountPatch')

    with self.command_group('anf pool', anf_pools_sdk) as g:
        g.show_command('show', 'get')
        g.command('list', 'list')
        g.command('delete', 'delete')
        g.custom_command('create', 'create_pool', client_factory=pools_mgmt_client_factory,
                         doc_string_source='azext_anf_preview.vendored_sdks.models#CapacityPool')
        g.generic_update_command('update', setter_name='create_or_update', custom_func_name='update_pool',
                                 setter_arg_name='body',
                                 doc_string_source='azext_anf_preview.vendored_sdks.models#CapacityPool')

    with self.command_group('anf volume', anf_volumes_sdk) as g:
        g.show_command('show', 'get')
        g.command('list', 'list')
        g.command('delete', 'delete')
        g.custom_command('create', 'create_volume', client_factory=volumes_mgmt_client_factory,
                         doc_string_source='azext_anf_preview.vendored_sdks.models#Volume')
        g.generic_update_command('update', setter_name='update', custom_func_name='patch_volume',
                                 setter_arg_name='body',
                                 doc_string_source='azext_anf_preview.vendored_sdks.models#VolumePatch')

    with self.command_group('anf mount-target', anf_mount_targets_sdk) as g:
        g.command('list', 'list')

    with self.command_group('anf snapshot', anf_snapshots_sdk) as g:
        g.show_command('show', 'get')
        g.command('list', 'list')
        g.command('delete', 'delete')
        g.custom_command('create', 'create_snapshot', client_factory=snapshots_mgmt_client_factory,
                         doc_string_source='azext_anf_preview.vendored_sdks.models#Snapshot')
