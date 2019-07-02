# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_apimgmt._help import helps  # pylint: disable=unused-import


class ApimgmtCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_apimgmt._client_factory import cf_apimgmt
        apimgmt_custom = CliCommandType(
            operations_tmpl='azext_apimgmt.custom#{}',
            client_factory=cf_apimgmt)
        super(ApimgmtCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                  custom_command_type=apimgmt_custom)

    def load_command_table(self, args):
        from azext_apimgmt.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_apimgmt._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = ApimgmtCommandsLoader
