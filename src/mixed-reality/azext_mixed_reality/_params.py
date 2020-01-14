# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    resource_group_name_type,
    get_location_type
)


def load_arguments(self, _):

    with self.argument_context('mixed-reality operation list') as c:
        pass

    with self.argument_context('mixed-reality check-name-availability-local') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('name', id_part=None, help='Resource Name To Verify')
        c.argument('_type', options_list=['--type'], id_part=None, help='Fully qualified resource type which includes provider namespace')

    with self.argument_context('mixed-reality remote-rendering-account create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of an Mixed Reality Account.')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))

    with self.argument_context('mixed-reality remote-rendering-account update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of an Mixed Reality Account.')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))

    with self.argument_context('mixed-reality remote-rendering-account delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of an Mixed Reality Account.')

    with self.argument_context('mixed-reality remote-rendering-account show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of an Mixed Reality Account.')

    with self.argument_context('mixed-reality remote-rendering-account list') as c:
        c.argument('resource_group', resource_group_name_type)

    with self.argument_context('mixed-reality remote-rendering-account regenerate-keys') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of an Mixed Reality Account.')
        c.argument('serial', id_part=None, help='serial of key to be regenerated')

    with self.argument_context('mixed-reality remote-rendering-account get-keys') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of an Mixed Reality Account.')

    with self.argument_context('mixed-reality spatial-anchors-account create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of an Mixed Reality Account.')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))

    with self.argument_context('mixed-reality spatial-anchors-account update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of an Mixed Reality Account.')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))

    with self.argument_context('mixed-reality spatial-anchors-account delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of an Mixed Reality Account.')

    with self.argument_context('mixed-reality spatial-anchors-account show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of an Mixed Reality Account.')

    with self.argument_context('mixed-reality spatial-anchors-account list') as c:
        c.argument('resource_group', resource_group_name_type)

    with self.argument_context('mixed-reality spatial-anchors-account regenerate-keys') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of an Mixed Reality Account.')
        c.argument('serial', id_part=None, help='serial of key to be regenerated')

    with self.argument_context('mixed-reality spatial-anchors-account get-keys') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of an Mixed Reality Account.')
