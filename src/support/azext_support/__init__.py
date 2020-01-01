# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_support._help import helps  # pylint: disable=unused-import


class SupportCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_support._client_factory import cf_support
        support_custom = CliCommandType(
            operations_tmpl='azext_support.custom#{}',
            client_factory=cf_support)
        super(SupportCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                    custom_command_type=support_custom)

    def load_command_table(self, args):
        from azext_support.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_support._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = SupportCommandsLoader
