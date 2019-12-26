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

    with self.argument_context('mixed-reality list') as c:
        pass

    with self.argument_context('mixed-reality check-name-availability check_name_availability_local') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx))

    with self.argument_context('mixed-reality create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of an Mixed Reality Spatial Anchors Account.')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('serial', id_part=None, help='serial of key to be regenerated')

    with self.argument_context('mixed-reality update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of an Mixed Reality Spatial Anchors Account.')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('serial', id_part=None, help='serial of key to be regenerated')

    with self.argument_context('mixed-reality delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of an Mixed Reality Spatial Anchors Account.')

    with self.argument_context('mixed-reality show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of an Mixed Reality Spatial Anchors Account.')

    with self.argument_context('mixed-reality list') as c:
        c.argument('resource_group', resource_group_name_type)

    with self.argument_context('mixed-reality regenerate_keys') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of an Mixed Reality Spatial Anchors Account.')

    with self.argument_context('mixed-reality get_keys') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='Name of an Mixed Reality Spatial Anchors Account.')
