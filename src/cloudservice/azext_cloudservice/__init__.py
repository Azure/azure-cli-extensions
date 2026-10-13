# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=import-outside-toplevel

from azure.cli.core import AzCommandsLoader


class ComputeManagementClientCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        cloud_service_custom = CliCommandType(operations_tmpl='azext_cloudservice.custom#{}')
        super().__init__(cli_ctx=cli_ctx, custom_command_type=cloud_service_custom)

    def load_command_table(self, args):
        from azure.cli.core.aaz import load_aaz_command_table
        from azext_cloudservice import aaz
        from azext_cloudservice.commands import load_command_table

        load_aaz_command_table(loader=self, aaz_pkg_name=aaz.__name__, args=args)
        # Registered after the AAZ table so the overrides replace the generated entries.
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_cloudservice._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = ComputeManagementClientCommandsLoader
