# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType
from ._client_factory import cf_workspace_collections, cf_workspaces


def load_command_table(self, _):

    powerbiembedded_workspace_collections = CliCommandType(
        operations_tmpl='azext_powerbiembedded.vendored_sdks.powerbiembedded.operations._workspace_collections_operations#WorkspaceCollectionsOperations.{}',
        client_factory=cf_workspace_collections)
    with self.command_group('powerbi-embedded workspace-collection', powerbiembedded_workspace_collections, client_factory=cf_workspace_collections) as g:
        g.custom_command('create', 'create_powerbiembedded_workspace_collection')
        g.custom_command('update', 'update_powerbiembedded_workspace_collection')
        g.custom_command('delete', 'delete_powerbiembedded_workspace_collection')
        g.custom_command('show', 'get_powerbiembedded_workspace_collection')
        g.custom_command('list', 'list_powerbiembedded_workspace_collection')
        g.custom_command('get-access-keys', 'get_access_keys_powerbiembedded_workspace_collection')
        g.custom_command('regenerate-key', 'regenerate_key_powerbiembedded_workspace_collection')

    powerbiembedded_workspaces = CliCommandType(
        operations_tmpl='azext_powerbiembedded.vendored_sdks.powerbiembedded.operations._workspaces_operations#WorkspacesOperations.{}',
        client_factory=cf_workspaces)
    with self.command_group('powerbi-embedded workspace-collection workspace', powerbiembedded_workspaces, client_factory=cf_workspaces) as g:
        g.custom_command('list', 'list_powerbiembedded_workspace_collection_workspace')

    with self.command_group('powerbi-embedded', is_preview=True):
        pass
