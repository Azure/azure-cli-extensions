# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from azext_horizondb._client_factory import (
    cf_horizondb_clusters,
    cf_horizondb_firewall_rules)
from azext_horizondb.utils._transformers import (
    table_transform_output)


# pylint: disable=too-many-locals, too-many-statements, line-too-long
def load_command_table(self, _):
    horizondb_clusters_sdk = CliCommandType(
        operations_tmpl='azext_horizondb.vendored_sdks.operations#HorizonDbClustersOperations.{}',
        client_factory=cf_horizondb_clusters
    )

    horizondb_firewall_rules_sdk = CliCommandType(
        operations_tmpl='azext_horizondb.vendored_sdks.operations#HorizonDbFirewallRulesOperations.{}',
        client_factory=cf_horizondb_firewall_rules
    )

    custom_commands = CliCommandType(
        operations_tmpl='azext_horizondb.commands.custom_commands#{}')
    firewall_custom_commands = CliCommandType(
        operations_tmpl='azext_horizondb.commands.firewall_commands#{}')
    with self.command_group('horizondb', horizondb_clusters_sdk,
                            custom_command_type=custom_commands,
                            client_factory=cf_horizondb_clusters) as g:
        g.custom_command('create', 'horizondb_cluster_create', table_transformer=table_transform_output)
        g.custom_command('delete', 'horizondb_cluster_delete')
        g.custom_command('list', 'horizondb_cluster_list')
        g.show_command('show', 'get')

    with self.command_group('horizondb firewall-rule', horizondb_firewall_rules_sdk,
                            custom_command_type=firewall_custom_commands,
                            client_factory=cf_horizondb_firewall_rules) as g:
        g.custom_command('create', 'horizondb_firewall_rule_create')
        g.custom_command('delete', 'horizondb_firewall_rule_delete', confirmation=False)
        g.custom_command('update', 'horizondb_firewall_rule_update')
        g.custom_command('list', 'horizondb_firewall_rule_list')
        g.show_command('show', 'get')
