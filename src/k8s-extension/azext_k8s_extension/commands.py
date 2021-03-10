# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_k8s_extension._client_factory import (cf_k8s_extension, cf_k8s_extension_operation)


def load_command_table(self, _):

    k8s_extension_sdk = CliCommandType(
        operations_tmpl='azext_k8s_extension.vendored_sdks.operations#K8sExtensionsOperations.{}',
        client_factory=cf_k8s_extension)

    with self.command_group('k8s-extension', k8s_extension_sdk, client_factory=cf_k8s_extension_operation,
                            is_preview=True) \
            as g:
        g.custom_command('create', 'create_k8s_extension')
        g.custom_command('update', 'update_k8s_extension')
        g.custom_command('delete', 'delete_k8s_extension', confirmation=True)
        g.custom_command('list', 'list_k8s_extension')
        g.custom_show_command('show', 'show_k8s_extension')
