# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-import

from azure.cli.core import AzCommandsLoader
from ._help import helps


class ServicebusCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        servicebus_custom = CliCommandType(operations_tmpl='azext_servicebus.custom#{}')
        super(ServicebusCommandsLoader, self).__init__(cli_ctx=cli_ctx, custom_command_type=servicebus_custom,
                                                       min_profile="2017-03-10-profile")

    def load_command_table(self, args):
        from azext_servicebus.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_servicebus._params import load_arguments_namespace, load_arguments_queue, load_arguments_topic,\
            load_arguments_subscription, load_arguments_rule, load_arguments_geodr
        load_arguments_namespace(self, command)
        load_arguments_queue(self, command)
        load_arguments_topic(self, command)
        load_arguments_subscription(self, command)
        load_arguments_rule(self, command)
        load_arguments_geodr(self, command)


COMMAND_LOADER_CLS = ServicebusCommandsLoader
