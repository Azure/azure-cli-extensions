# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from azext_acrquery._client_factory import cf_metadata
from ._format import transform_metadata_output


def load_command_table(self, _):
    acr_metadata_util = CliCommandType(
        operations_tmpl='azext_acrquery.custom#{}',
        client_factory=cf_metadata)

    with self.command_group('acr', acr_metadata_util) as g:
        g.command('query', 'create_query', table_transformer=transform_metadata_output)
