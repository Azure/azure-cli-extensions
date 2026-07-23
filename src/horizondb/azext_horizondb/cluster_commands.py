# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from azext_horizondb._client_factory import (
    cf_horizondb_clusters,
    cf_horizondb_parameter_groups,
    cf_horizondb_firewall_rules,
    cf_horizondb_private_endpoint_connections,
    cf_horizondb_private_link_resources)
from azext_horizondb.utils._transformers import (
    table_transform_output)
from azext_horizondb.utils.validators import (
    validate_private_endpoint_connection_id)


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

    parameter_group_commands = CliCommandType(
        operations_tmpl='azext_horizondb.commands.parameter_group_commands#{}')

    firewall_rule_custom = CliCommandType(
        operations_tmpl='azext_horizondb.commands.firewall_rule_commands#{}',
        client_factory=cf_horizondb_firewall_rules)
    private_endpoint_commands = CliCommandType(
        operations_tmpl='azext_horizondb.commands.private_endpoint_commands#{}')
    horizondb_private_endpoint_connections_sdk = CliCommandType(
        operations_tmpl='azext_horizondb.vendored_sdks.operations#HorizonDbPrivateEndpointConnectionsOperations.{}',
        client_factory=cf_horizondb_private_endpoint_connections
    )
    horizondb_private_link_resources_sdk = CliCommandType(
        operations_tmpl='azext_horizondb.vendored_sdks.operations#HorizonDbPrivateLinkResourcesOperations.{}',
        client_factory=cf_horizondb_private_link_resources
    )

    with self.command_group('horizondb', horizondb_clusters_sdk,
                            custom_command_type=custom_commands,
                            client_factory=cf_horizondb_clusters) as g:
        g.custom_command('create', 'horizondb_cluster_create', table_transformer=table_transform_output)
        g.custom_command('update', 'horizondb_cluster_update', supports_no_wait=True)
        g.custom_command('delete', 'horizondb_cluster_delete')
        g.custom_command('list', 'horizondb_cluster_list')
        g.show_command('show', 'get')

    with self.command_group('horizondb parameter-group', horizondb_parameter_groups_sdk,
                            custom_command_type=parameter_group_commands,
                            client_factory=cf_horizondb_parameter_groups) as g:
        g.custom_command('create', 'horizondb_parameter_group_create', supports_no_wait=True)
        g.custom_command('delete', 'horizondb_parameter_group_delete', supports_no_wait=True)
        g.custom_command('list', 'horizondb_parameter_group_list')
        g.custom_command('list-connections', 'horizondb_parameter_group_list_connections')
        g.show_command('show', 'get')

    with self.command_group('horizondb firewall-rule', firewall_rule_custom,
                            custom_command_type=firewall_rule_custom,
                            client_factory=cf_horizondb_firewall_rules) as g:
        g.custom_command('create', 'horizondb_firewall_rule_create')
        g.custom_command('update', 'horizondb_firewall_rule_update')
        g.custom_command('delete', 'horizondb_firewall_rule_delete')
        g.custom_show_command('show', 'horizondb_firewall_rule_get')
        g.custom_command('list', 'horizondb_firewall_rule_list')

    with self.command_group('horizondb private-endpoint-connection',
                            horizondb_private_endpoint_connections_sdk,
                            custom_command_type=private_endpoint_commands,
                            client_factory=cf_horizondb_private_endpoint_connections) as g:
        g.custom_command('list', 'horizondb_private_endpoint_connection_list')
        g.show_command('show', 'get', validator=validate_private_endpoint_connection_id)
        g.command('delete', 'begin_delete', validator=validate_private_endpoint_connection_id)
        g.custom_command('approve', 'horizondb_approve_private_endpoint_connection',
                         validator=validate_private_endpoint_connection_id)
        g.custom_command('reject', 'horizondb_reject_private_endpoint_connection',
                         validator=validate_private_endpoint_connection_id)

    with self.command_group('horizondb private-link-resource',
                            horizondb_private_link_resources_sdk,
                            custom_command_type=private_endpoint_commands,
                            client_factory=cf_horizondb_private_link_resources) as g:
        g.custom_command('list', 'horizondb_private_link_resource_list')
        g.custom_show_command('show', 'horizondb_private_link_resource_get')
