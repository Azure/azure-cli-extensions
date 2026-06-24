# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from azext_horizondb._client_factory import (
    cf_horizondb_clusters,
    cf_horizondb_parameter_groups)
from azext_horizondb.utils._transformers import (
    table_transform_output)


# pylint: disable=too-many-locals, too-many-statements, line-too-long
def load_command_table(self, _):
    horizondb_clusters_sdk = CliCommandType(
        operations_tmpl='azext_horizondb.vendored_sdks.operations#HorizonDbClustersOperations.{}',
        client_factory=cf_horizondb_clusters
    )

    horizondb_parameter_groups_sdk = CliCommandType(
        operations_tmpl='azext_horizondb.vendored_sdks.operations#HorizonDbParameterGroupsOperations.{}',
        client_factory=cf_horizondb_parameter_groups
    )

    custom_commands = CliCommandType(
        operations_tmpl='azext_horizondb.commands.custom_commands#{}')
    with self.command_group('horizondb', horizondb_clusters_sdk,
                            custom_command_type=custom_commands,
                            client_factory=cf_horizondb_clusters) as g:
        g.custom_command('create', 'horizondb_cluster_create', table_transformer=table_transform_output)
        g.custom_command('update', 'horizondb_cluster_update', supports_no_wait=True)
        g.custom_command('delete', 'horizondb_cluster_delete')
        g.custom_command('list', 'horizondb_cluster_list')
        g.show_command('show', 'get')

    with self.command_group('horizondb parameter-group', horizondb_parameter_groups_sdk,
                            custom_command_type=custom_commands,
                            client_factory=cf_horizondb_parameter_groups) as g:
        g.custom_command('create', 'horizondb_parameter_group_create', supports_no_wait=True)
        g.custom_command('delete', 'horizondb_parameter_group_delete', supports_no_wait=True)
        g.custom_command('list', 'horizondb_parameter_group_list')
        g.show_command('show', 'get')
