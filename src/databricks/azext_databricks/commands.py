# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType
from ._validators import validate_workspace_values, validate_network_id


def load_command_table(self, _):

    from ._client_factory import cf_workspaces, cf_vnet_peering
    databricks_workspaces = CliCommandType(
        operations_tmpl='azext_databricks.vendored_sdks.databricks.operations._workspaces_operations#WorkspacesOperations.{}',
        client_factory=cf_workspaces)

    databricks_vnet_peering = CliCommandType(
        operations_tmpl='azext_databricks.vendored_sdks.databricks.operations._vnet_peering_operations#VNetPeeringOperations.{}',
        client_factory=cf_vnet_peering)

    with self.command_group('databricks workspace', databricks_workspaces, client_factory=cf_workspaces) as g:
        g.custom_command('create', 'create_databricks_workspace', validator=validate_workspace_values, supports_no_wait=True)
        g.custom_command('update', 'update_databricks_workspace', supports_no_wait=True)
        g.custom_command('delete', 'delete_databricks_workspace', supports_no_wait=True, confirmation=True)
        g.custom_show_command('show', 'get_databricks_workspace')
        g.custom_command('list', 'list_databricks_workspace')
        g.wait_command('wait')

    with self.command_group('databricks workspace vnet-peering', databricks_vnet_peering, client_factory=cf_vnet_peering) as g:
        g.custom_command('create', 'create_databricks_vnet_peering', validator=validate_network_id('remote_virtual_network'), supports_no_wait=True)
        g.custom_command('update', 'update_databricks_vnet_peering', supports_no_wait=True)
        g.custom_command('delete', 'delete_databricks_vnet_peering', supports_no_wait=True)
        g.command('list', 'list_by_workspace')
        g.show_command('show', 'get')
        g.wait_command('wait')
