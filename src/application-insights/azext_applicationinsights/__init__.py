# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_applicationinsights._help import helps  # pylint: disable=unused-import


class ApplicationInsightsCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_applicationinsights._client_factory import applicationinsights_data_plane_client
        applicationinsights_custom = CliCommandType(
            operations_tmpl='azext_applicationinsights.custom#{}',
            client_factory=applicationinsights_data_plane_client
        )

        super(ApplicationInsightsCommandsLoader, self).__init__(
            cli_ctx=cli_ctx,
            custom_command_type=applicationinsights_custom
        )

    def load_command_table(self, args):
        from azext_applicationinsights.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_applicationinsights._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = ApplicationInsightsCommandsLoader
