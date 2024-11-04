# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_test2._help import helps  # pylint: disable=unused-import


class Test2CommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_test2._client_factory import cf_test2
        test2_custom = CliCommandType(
            operations_tmpl='azext_test2.custom#{}',
            client_factory=cf_test2)
        super(Test2CommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                  custom_command_type=test2_custom)

    def load_command_table(self, args):
        from azext_test2.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_test2._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = Test2CommandsLoader
