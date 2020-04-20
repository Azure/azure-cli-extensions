# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azext_account.generated._help import helps  # pylint: disable=unused-import


class SubscriptionClientCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_account.generated._client_factory import cf_account
        account_custom = CliCommandType(
            operations_tmpl='azext_account.custom#{}',
            client_factory=cf_account)
        super(SubscriptionClientCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                               custom_command_type=account_custom)

    def load_command_table(self, args):
        from azext_account.generated.commands import load_command_table
        load_command_table(self, args)
        try:
            from azext_account.manual.commands import load_command_table as load_command_table_manual
            load_command_table_manual(self, args)
        except ImportError:
            pass
        return self.command_table

    def load_arguments(self, command):
        from azext_account.generated._params import load_arguments
        load_arguments(self, command)
        try:
            from azext_account.manual._params import load_arguments as load_arguments_manual
            load_arguments_manual(self, command)
        except ImportError:
            pass


COMMAND_LOADER_CLS = SubscriptionClientCommandsLoader
