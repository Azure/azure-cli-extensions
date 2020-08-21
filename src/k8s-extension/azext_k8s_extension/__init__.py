# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_k8s_extension._help import helps  # pylint: disable=unused-import


class K8sExtensionCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_k8s_extension._client_factory import cf_k8s_extension
        k8s_extension_custom = CliCommandType(
            operations_tmpl='azext_k8s_extension.custom#{}',
            client_factory=cf_k8s_extension)
        super(K8sExtensionCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                  custom_command_type=k8s_extension_custom)

    def load_command_table(self, args):
        from azext_k8s_extension.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_k8s_extension._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = K8sExtensionCommandsLoader
