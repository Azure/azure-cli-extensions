# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

# pylint: disable=unused-import
# pylint: disable=line-too-long

from ._help import helps


class EventhubCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        eventhub_custom = CliCommandType(operations_tmpl='azext_eventhub.custom#{}')
        super(EventhubCommandsLoader, self).__init__(cli_ctx=cli_ctx, custom_command_type=eventhub_custom, min_profile="2017-03-10-profile")

    def load_command_table(self, args):
        from azext_eventhub.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_eventhub._params import load_arguments_namespace, load_arguments_eventhub, load_arguments_consumergroup, load_arguments_geodr
        load_arguments_namespace(self, command)
        load_arguments_eventhub(self, command)
        load_arguments_consumergroup(self, command)
        load_arguments_geodr(self, command)


COMMAND_LOADER_CLS = EventhubCommandsLoader
