# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader


class SupportCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        super().__init__(cli_ctx=cli_ctx)

    def load_command_table(self, args):
        from azext_support.commands import load_command_table
        from azure.cli.core.aaz import load_aaz_command_table

        try:
            from . import aaz
        except ImportError:
            aaz = None
        if aaz:
            load_aaz_command_table(loader=self, aaz_pkg_name=aaz.__name__, args=args)
        load_command_table(self, args)
        return self.command_table


COMMAND_LOADER_CLS = SupportCommandsLoader
