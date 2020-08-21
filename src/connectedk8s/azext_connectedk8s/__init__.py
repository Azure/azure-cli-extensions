# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_connectedk8s._help import helps  # pylint: disable=unused-import


class Connectedk8sCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_connectedk8s._client_factory import cf_connectedk8s
        connectedk8s_custom = CliCommandType(
            operations_tmpl='azext_connectedk8s.custom#{}',
            client_factory=cf_connectedk8s)
        super(Connectedk8sCommandsLoader, self).__init__(cli_ctx=cli_ctx, custom_command_type=connectedk8s_custom)

    def load_command_table(self, args):
        from azext_connectedk8s.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_connectedk8s._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = Connectedk8sCommandsLoader
