# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azure.cli.core.commands import CliCommandType
from azext_spring._help import helps  # pylint: disable=unused-import
from azext_spring._client_factory import cf_spring
from azext_spring.commands import load_command_table
from azext_spring._params import load_arguments


class springCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        spring_custom = CliCommandType(
            operations_tmpl='azext_spring.custom#{}',
            client_factory=cf_spring)
        super(springCommandsLoader, self).__init__(cli_ctx=cli_ctx, custom_command_type=spring_custom)

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
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        load_arguments(self, command)


COMMAND_LOADER_CLS = springCommandsLoader
