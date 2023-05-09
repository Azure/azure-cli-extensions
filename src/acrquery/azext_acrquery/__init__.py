# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.profiles import ResourceType
from azext_acrquery._help import helps


class AcrqueryCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_acrquery._client_factory import cf_metadata
        acrquery_custom = CliCommandType(
            operations_tmpl='azext_acrquery.custom#{}',
            client_factory=cf_metadata)
        super().__init__(cli_ctx=cli_ctx, resource_type=ResourceType.MGMT_CONTAINERREGISTRY, operation_group='registries', custom_command_type=acrquery_custom)

    def load_command_table(self, args):
        from azext_acrquery.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_acrquery._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = AcrqueryCommandsLoader
