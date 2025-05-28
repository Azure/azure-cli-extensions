# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_aosm._help import helps  # pylint: disable=unused-import


class AosmCommandsLoader(AzCommandsLoader):
    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        aosm_custom = CliCommandType(operations_tmpl="azext_aosm.custom#{}")
        super().__init__(cli_ctx=cli_ctx, custom_command_type=aosm_custom)

    def load_command_table(self, args):
        from azure.cli.core.aaz import load_aaz_command_table

        from azext_aosm.commands import load_command_table

        try:
            from . import aaz
        except ImportError:
            aaz = None
        if aaz:
            load_aaz_command_table(loader=self, aaz_pkg_name=aaz.__name__, args=args)

        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_aosm._params import load_arguments

        load_arguments(self, command)


COMMAND_LOADER_CLS = AosmCommandsLoader
