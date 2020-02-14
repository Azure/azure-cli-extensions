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
from azure.cli.core.commands.validators import get_default_location_from_resource_group


def load_arguments(self, _):

    with self.argument_context('powerbi embedded-capacity create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the Dedicated capacity. It must be at least 3 characters in length, and no more than 63.')
        c.argument('sku_name', id_part=None, help='Name of the SKU level.')
        c.argument('sku_tier', arg_type=get_enum_type(['PBIE_Azure']), id_part=None, help='The name of the Azure pricing tier to which the SKU applies.')
        c.argument('tags', tags_type)
        c.argument('administration_members', id_part=None, help='An array of administrator user identities.', nargs='+')
        c.argument('location', get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)

    with self.argument_context('powerbi embedded-capacity update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the Dedicated capacity. It must be at least 3 characters in length, and no more than 63.')
        c.argument('sku_name', id_part=None, help='Name of the SKU level.')
        c.argument('sku_tier', arg_type=get_enum_type(['PBIE_Azure']), id_part=None, help='The name of the Azure pricing tier to which the SKU applies.')
        c.argument('tags', tags_type)
        c.argument('administration_members', id_part=None, help='An array of administrator user identities.', nargs='+')

    with self.argument_context('powerbi embedded-capacity delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the Dedicated capacity. It must be at least 3 characters in length, and no more than 63.')

    with self.argument_context('powerbi embedded-capacity show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the Dedicated capacity. It must be at least 3 characters in length, and no more than 63.')

    with self.argument_context('powerbi embedded-capacity list') as c:
        c.argument('resource_group', resource_group_name_type)
