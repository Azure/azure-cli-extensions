# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType
from ._validators import validate_workspace_values


def load_command_table(self, _):

    from ._client_factory import cf_workspaces
    databricks_workspaces = CliCommandType(
        operations_tmpl='azext_databricks.vendored_sdks.databricks.operations._workspaces_operations#WorkspacesOperations.{}',
        client_factory=cf_workspaces)
    with self.command_group('databricks workspace', databricks_workspaces, client_factory=cf_workspaces, is_preview=True) as g:
        g.custom_command('create', 'create_databricks_workspace', validator=validate_workspace_values, supports_no_wait=True)
        g.custom_command('update', 'update_databricks_workspace', supports_no_wait=True)
        g.custom_command('delete', 'delete_databricks_workspace', supports_no_wait=True, confirmation=True)
        g.custom_show_command('show', 'get_databricks_workspace')
        g.custom_command('list', 'list_databricks_workspace')
        g.wait_command('wait')
