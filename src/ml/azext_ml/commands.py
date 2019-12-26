# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from ._client_factory import cf_operations
    ml_operations = CliCommandType(
        operations_tmpl='azext_ml.vendored_sdks.machinelearning.operations._operations_operations#OperationsOperations.{}',
        client_factory=cf_operations)
    with self.command_group('ml', ml_operations, client_factory=cf_operations) as g:
        g.custom_command('list', 'list_ml')

    from ._client_factory import cf_workspaces
    ml_workspaces = CliCommandType(
        operations_tmpl='azext_ml.vendored_sdks.machinelearning.operations._workspaces_operations#WorkspacesOperations.{}',
        client_factory=cf_workspaces)
    with self.command_group('ml', ml_workspaces, client_factory=cf_workspaces) as g:
        g.custom_command('create', 'create_ml')
        g.custom_command('update', 'update_ml')
        g.custom_command('delete', 'delete_ml')
        g.custom_command('show', 'get_ml')
        g.custom_command('list', 'list_ml')
        g.custom_command('resync_storage_keys', 'resync_storage_keys_ml')
        g.custom_command('list_workspace_keys', 'list_workspace_keys_ml')
