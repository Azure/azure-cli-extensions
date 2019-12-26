# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)


def load_arguments(self, _):

    with self.argument_context('ml list') as c:
        pass

    with self.argument_context('ml create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the machine learning workspace.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('sku', id_part=None, help='The sku of the workspace.')
        c.argument('workspace_state', arg_type=get_enum_type(['Deleted', 'Enabled', 'Disabled', 'Migrated', 'Updated', 'Registered', 'Unregistered']), id_part=None, help='The current state of workspace resource.')
        c.argument('key_vault_identifier_id', id_part=None, help='The key vault identifier used for encrypted workspaces.')

    with self.argument_context('ml update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the machine learning workspace.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('sku', id_part=None, help='The sku of the workspace.')
        c.argument('workspace_state', arg_type=get_enum_type(['Deleted', 'Enabled', 'Disabled', 'Migrated', 'Updated', 'Registered', 'Unregistered']), id_part=None, help='The current state of workspace resource.')
        c.argument('key_vault_identifier_id', id_part=None, help='The key vault identifier used for encrypted workspaces.')

    with self.argument_context('ml delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the machine learning workspace.')

    with self.argument_context('ml show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the machine learning workspace.')

    with self.argument_context('ml list') as c:
        c.argument('resource_group', resource_group_name_type)

    with self.argument_context('ml resync_storage_keys') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the machine learning workspace.')

    with self.argument_context('ml list_workspace_keys') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the machine learning workspace.')
