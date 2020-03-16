# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)


def load_arguments(self, _):
    name_type = CLIArgumentType(
        options_list=['--name', '-n'],
        help='The name of the Dedicated capacity. It must be at least 3 characters in length, and no more than 63.')
    sku_name_type = CLIArgumentType(
        arg_type=get_enum_type(['A1', 'A2', 'A3', 'A4', 'A5', 'A6']),
        help='Name of the SKU level. For more information, please refer to '
             'https://azure.microsoft.com/en-us/pricing/details/power-bi-embedded/.'
    )
    sku_tier_type = CLIArgumentType(
        arg_type=get_enum_type(['PBIE_Azure']),
        help='The name of the Azure pricing tier to which the SKU applies.'
    )
    administration_type = CLIArgumentType(
        help='An array of administrator user identities.', nargs='+'
    )

    with self.argument_context('powerbi embedded-capacity') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('name', name_type)

    with self.argument_context('powerbi embedded-capacity create') as c:
        c.argument('sku_name', sku_name_type)
        c.argument('sku_tier', sku_tier_type)
        c.argument('tags', tags_type)
        c.argument('administration_members', administration_type)
        c.argument('location', get_location_type(self.cli_ctx))

    with self.argument_context('powerbi embedded-capacity update') as c:
        c.argument('sku_name', sku_name_type)
        c.argument('sku_tier', sku_tier_type)
        c.argument('tags', tags_type)
        c.argument('administration_members', administration_type)
