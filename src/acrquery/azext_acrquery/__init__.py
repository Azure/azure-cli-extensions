# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azext_acrquery._help import helps  # pylint: disable=unused-import
from ._client_factory import cf_metadata
from azure.cli.core.commands import CliCommandType
from ._format import transform_metadata_output


class AcrqueryCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        acrquery_custom = CliCommandType(
            operations_tmpl='azext_acrquery.custom#{}',
            client_factory=cf_metadata)
        super(AcrqueryCommandsLoader, self).__init__(cli_ctx=cli_ctx, custom_command_type=acrquery_custom)

    def load_command_table(self, _):
        acr_metadata_util = CliCommandType(
            operations_tmpl='azext_acrquery.custom#{}',
            client_factory=cf_metadata)

        with self.command_group('acr', acr_metadata_util) as g:
            g.custom_command('query', 'create_query')

        return self.command_table

    def load_arguments(self, command):
        from azext_acrquery._params import load_arguments
        load_arguments(self, command)
        pass


COMMAND_LOADER_CLS = AcrqueryCommandsLoader
