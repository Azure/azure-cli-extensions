# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_spring_cloud._help import helps  # pylint: disable=unused-import


class spring_cloudCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_spring_cloud._client_factory import cf_spring_cloud
        spring_cloud_custom = CliCommandType(
            operations_tmpl='azext_spring_cloud.custom#{}',
            client_factory=cf_spring_cloud)
        super(spring_cloudCommandsLoader, self).__init__(cli_ctx=cli_ctx, custom_command_type=spring_cloud_custom)

    def load_command_table(self, args):
        from azext_spring_cloud.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_spring_cloud._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = spring_cloudCommandsLoader
