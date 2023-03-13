# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azure.cli.core.commands import CliCommandType
from azext_spring_cloud._help import helps  # pylint: disable=unused-import
from azext_spring_cloud._client_factory import cf_spring_cloud
from azext_spring_cloud.commands import load_command_table
from azext_spring_cloud._params import load_arguments


class spring_cloudCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        spring_cloud_custom = CliCommandType(
            operations_tmpl='azext_spring_cloud.custom#{}',
            client_factory=cf_spring_cloud)
        super(spring_cloudCommandsLoader, self).__init__(cli_ctx=cli_ctx, custom_command_type=spring_cloud_custom)

    def load_command_table(self, args):
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        load_arguments(self, command)


COMMAND_LOADER_CLS = spring_cloudCommandsLoader
