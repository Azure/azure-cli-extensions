# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from ._client_factory import (cf_shared_vm_extensions, cf_shared_vm_extension_versions)


def load_command_table(self, _):

    # TODO: Add command type here
    # compute-preview_sdk = CliCommandType(
    #    operations_tmpl='<PATH>.operations#None.{}',
    #    client_factory=cf_compute-preview)

    compute_shared_vm_extensions_sdk = CliCommandType(
        operations_tmpl='azext_compute_preview.vendored_sdks.v2019_12.operations#SharedVmExtensionsOperations.{}',
        client_factory=cf_shared_vm_extensions,
        operation_group='shared_vm_extensions'
    )

    compute_shared_vm_extension_versions_sdk = CliCommandType(
        operations_tmpl='azext_compute_preview.vendored_sdks.v2019_12.operations#SharedVmExtensionVersionsOperations.{}',
        client_factory=cf_shared_vm_extension_versions,
        operation_group='shared_vm_extension_versions'
    )

    # with self.command_group('compute-preview') as g:
    #     g.custom_command('create', 'create_compute-preview')
    #     # g.command('delete', 'delete')
    #     g.custom_command('list', 'list_compute-preview')
    #     # g.show_command('show', 'get')
    #     # g.generic_update_command('update', setter_name='update', custom_func_name='update_compute-preview')

    with self.command_group('vm extension publish', compute_shared_vm_extensions_sdk,
                            client_factory=cf_shared_vm_extensions, is_preview=True) as g:
        g.custom_command('create', 'create_publish')
        g.show_command('show', 'get')
        g.command('delete', 'delete')
        g.generic_update_command('update', custom_func_name='update_publish')

    with self.command_group('vm extension publish-version', compute_shared_vm_extension_versions_sdk,
                            client_factory=cf_shared_vm_extension_versions, is_preview=True) as g:
        g.custom_command('create', 'create_publish_version')
        g.show_command('show', 'get')
        g.command('delete', 'delete')
        g.generic_update_command('update', custom_func_name='update_publish_version')
