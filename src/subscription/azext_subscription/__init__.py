# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-import
# pylint: disable=line-too-long

from azure.cli.core import AzCommandsLoader
from ._help import helps


class SubscriptionCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        subscription_custom = CliCommandType(operations_tmpl='azext_subscription.custom#{}')
        super(SubscriptionCommandsLoader, self).__init__(cli_ctx=cli_ctx, custom_command_type=subscription_custom)

    def load_command_table(self, args):
        from azext_subscription.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_subscription._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = SubscriptionCommandsLoader
