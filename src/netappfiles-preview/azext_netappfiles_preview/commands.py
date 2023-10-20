# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from azure.cli.core.commands import CliCommandType
from ._client_factory import (
    volumes_mgmt_client_factory)
from ._exception_handler import netapp_exception_handler


def load_command_table(self, _):

    netappfiles_volumes_sdk = CliCommandType(
        operations_tmpl='azext_netappfiles_preview.vendored_sdks.operations.volumes_operations#VolumesOperations.{}',
        client_factory=volumes_mgmt_client_factory,
        exception_handler=netapp_exception_handler
    )

    # netappfiles_mount_targets_sdk = CliCommandType(
    #     operations_tmpl='azext_netappfiles_preview.vendored_sdks.operations.mount_targets_operations#MountTargetsOperations.{}',
    #     client_factory=mount_targets_mgmt_client_factory,
    #     exception_handler=netapp_exception_handler
    # )

    # with self.command_group('netappfiles account', netappfiles_accounts_sdk) as g:
    #     g.show_command('show', 'get')
    #     g.command('list', 'list')
    #     g.command('delete', 'delete')
    #     g.custom_command('create', 'create_account',
    #                      client_factory=accounts_mgmt_client_factory,
    #                      doc_string_source='azext_netappfiles_preview.vendored_sdks.models#NetAppAccount',
    #                      exception_handler=netapp_exception_handler)
    #     g.custom_command('set', 'update_account',
    #                      client_factory=accounts_mgmt_client_factory,
    #                      doc_string_source='azext_netappfiles_preview.vendored_sdks.models#NetAppAccount',
    #                      exception_handler=netapp_exception_handler)
    #     g.generic_update_command('update',
    #                              setter_name='update',
    #                              custom_func_name='patch_account',
    #                              setter_arg_name='body',
    #                              doc_string_source='azext_netappfiles_preview.vendored_sdks.models#NetAppAccountPatch',
    #                              exception_handler=netapp_exception_handler)

    # with self.command_group('netappfiles pool', netappfiles_pools_sdk) as g:
    #     g.show_command('show', 'get')
    #     g.command('list', 'list')
    #     g.command('delete', 'delete')
    #     g.custom_command('create', 'create_pool',
    #                      client_factory=pools_mgmt_client_factory,
    #                      doc_string_source='azext_netappfiles_preview.vendored_sdks.models#CapacityPool',
    #                      exception_handler=netapp_exception_handler)
    #     g.generic_update_command('update',
    #                              setter_name='update',
    #                              custom_func_name='patch_pool',
    #                              setter_arg_name='body',
    #                              doc_string_source='azext_netappfiles_preview.vendored_sdks.models#CapacityPool',
    #                              exception_handler=netapp_exception_handler)

    with self.command_group('netappfiles volume', netappfiles_volumes_sdk):
        from .custom import VolumeCreate, VolumeUpdate
        self.command_table["netappfiles volume create"] = VolumeCreate(loader=self)
        self.command_table["netappfiles volume update"] = VolumeUpdate(loader=self)
    #     g.show_command('show', 'get')
    #     g.command('list', 'list')
    #     g.command('delete', 'delete')
    #     g.custom_command('create', 'create_volume',
    #                      client_factory=volumes_mgmt_client_factory,
    #                      doc_string_source='azext_netappfiles_preview.vendored_sdks.models#Volume',
    #                      exception_handler=netapp_exception_handler)
    #     g.generic_update_command('update',
    #                              setter_name='update',
    #                              custom_func_name='patch_volume',
    #                              setter_arg_name='body',
    #                              doc_string_source='azext_netappfiles_preview.vendored_sdks.models#VolumePatch',
    #                              exception_handler=netapp_exception_handler)

    # with self.command_group('netappfiles mount-target', netappfiles_mount_targets_sdk) as g:
    #     g.command('list', 'list')
