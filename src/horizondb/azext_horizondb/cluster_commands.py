# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from azext_horizondb._client_factory import (
    cf_horizondb_clusters)
from azext_horizondb.utils._transformers import (
    table_transform_output)


# pylint: disable=too-many-locals, too-many-statements, line-too-long
def load_command_table(self, _):
    horizondb_clusters_sdk = CliCommandType(
        operations_tmpl='azext_horizondb.vendored_sdks.operations#HorizonDbClustersOperations.{}',
        client_factory=cf_horizondb_clusters
    )

    custom_commands = CliCommandType(
        operations_tmpl='azext_horizondb.commands.custom_commands#{}')
    with self.command_group('horizondb', horizondb_clusters_sdk,
                            custom_command_type=custom_commands,
                            client_factory=cf_horizondb_clusters) as g:
        g.custom_command('create', 'horizondb_cluster_create', table_transformer=table_transform_output)
        g.custom_command('delete', 'horizondb_cluster_delete')
        g.custom_command('list', 'horizondb_cluster_list')
        g.show_command('show', 'get')

    identity_commands = CliCommandType(
        operations_tmpl='azext_horizondb.commands.identity_commands#{}')
    with self.command_group('horizondb identity', horizondb_clusters_sdk,
                            custom_command_type=identity_commands,
                            client_factory=cf_horizondb_clusters) as g:
        g.custom_command('assign', 'horizondb_identity_assign', supports_no_wait=True)
        g.custom_command('list', 'horizondb_identity_list')
        g.custom_command('remove', 'horizondb_identity_remove', supports_no_wait=True)
        g.custom_command('show', 'horizondb_identity_show')
