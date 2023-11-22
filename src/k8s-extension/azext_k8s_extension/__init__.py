# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from . import consts

from ._help import helps  # pylint: disable=unused-import


class K8sExtensionCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from ._client_factory import cf_k8s_extension
        k8s_extension_custom = CliCommandType(
            operations_tmpl=consts.EXTENSION_PACKAGE_NAME + '.custom#{}',
            client_factory=cf_k8s_extension)
        super().__init__(cli_ctx=cli_ctx,
                         custom_command_type=k8s_extension_custom)

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

    def load_arguments(self, command):
        from ._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = K8sExtensionCommandsLoader
