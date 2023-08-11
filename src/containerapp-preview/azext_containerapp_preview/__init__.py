# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_containerapp_preview._help import helps  # pylint: disable=unused-import
from azext_containerapp_preview._utils import (_get_azext_containerapp_module, auto_install_containerapp_extension_if_not_exist)


class ContainerappPreviewCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        containerapp_preview_custom = CliCommandType(
            operations_tmpl='azext_containerapp_preview.custom#{}',
            client_factory=None)
        super(ContainerappPreviewCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                                custom_command_type=containerapp_preview_custom)
        auto_install_containerapp_extension_if_not_exist(self)

    def load_command_table(self, args):
        from azext_containerapp_preview.commands import load_command_table

        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_containerapp_preview._params import load_arguments

        ga_params = _get_azext_containerapp_module("azext_containerapp._params")
        ga_params.load_arguments(self, command)
        load_arguments(self, command)


COMMAND_LOADER_CLS = ContainerappPreviewCommandsLoader
