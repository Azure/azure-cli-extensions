# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.profiles import ResourceType


class MigrateCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        migrate_custom = CliCommandType(
            operations_tmpl='azext_migrate.custom#{}',
        )

        super().__init__(
            cli_ctx=cli_ctx,
            custom_command_type=migrate_custom
        )

    def load_command_table(self, args):
        from azext_migrate.commands \
            import load_command_table
        
        from azure.cli.core.aaz import load_aaz_command_table
        try:
            from . import aaz
        except ImportError:
            aaz = None
        if aaz:
            load_aaz_command_table(
                loader=self,
                aaz_pkg_name=aaz.__name__,
                args=args
            )
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_migrate._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = MigrateCommandsLoader
