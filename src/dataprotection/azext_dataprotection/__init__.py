# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
try:
    from azext_dataprotection.manual._help import helps  # pylint: disable=unused-import
except ImportError as e:
    if e.name.endswith('manual._help'):
        pass
    else:
        raise e


class DataProtectionClientCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        dataprotection_custom = CliCommandType(
            operations_tmpl='azext_dataprotection.custom#{}')
        parent = super()
        parent.__init__(cli_ctx=cli_ctx, custom_command_type=dataprotection_custom)

    def load_command_table(self, args):
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
        try:
            from azext_dataprotection.manual.commands import load_command_table as load_command_table_manual
            load_command_table_manual(self, args)
        except ImportError as err:
            if err.name.endswith('manual.commands'):
                pass
            else:
                raise err
        return self.command_table

    def load_arguments(self, command):
        try:
            from azext_dataprotection.manual._params import load_arguments as load_arguments_manual
            load_arguments_manual(self, command)
        except ImportError as err:
            if err.name.endswith('manual._params'):
                pass
            else:
                raise err


COMMAND_LOADER_CLS = DataProtectionClientCommandsLoader
