# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_health_models._help import helps  # pylint: disable=unused-import


class HealthModelsCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        health_models_custom = CliCommandType(
            operations_tmpl='azext_health_models.custom#{}')
        super().__init__(cli_ctx=cli_ctx, custom_command_type=health_models_custom)

    def load_command_table(self, args):
        from azure.cli.core.aaz import load_aaz_command_table
        from . import aaz
        load_aaz_command_table(loader=self, aaz_pkg_name=aaz.__name__, args=args)
        from azext_health_models.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_health_models._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = HealthModelsCommandsLoader
