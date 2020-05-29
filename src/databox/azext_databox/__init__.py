# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

import azext_databox._help  # pylint: disable=unused-import


class DataBoxCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_databox._client_factory import cf_databox
        databox_custom = CliCommandType(
            operations_tmpl='azext_databox.custom#{}',
            client_factory=cf_databox)
        super(DataBoxCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                    custom_command_type=databox_custom)

    def load_command_table(self, args):
        from azext_databox.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_databox._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = DataBoxCommandsLoader
