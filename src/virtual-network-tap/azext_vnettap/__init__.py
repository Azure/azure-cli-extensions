# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

import azext_vnettap._help  # pylint: disable=unused-import


class VirtualNetworkTapCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        vtap_custom = CliCommandType(
            operations_tmpl='azext_vnettap.custom#{}'
        )
        super().__init__(cli_ctx=cli_ctx, custom_command_type=vtap_custom)

    def load_command_table(self, args):
        from .commands import load_command_table
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

    def load_arguments(self, args):
        from ._params import load_arguments
        load_arguments(self, args)


COMMAND_LOADER_CLS = VirtualNetworkTapCommandsLoader
