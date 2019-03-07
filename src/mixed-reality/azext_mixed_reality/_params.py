# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from knack.arguments import CLIArgumentType
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azure.cli.core.commands.parameters import (
    resource_group_name_type,
    get_resource_name_completion_list,
    get_location_type,
    get_enum_type,
    tags_type,
    name_type
)

spatial_anchors_account_name_type = CLIArgumentType(
    help='Name of the Spatial Anchors Account',
    arg_type=name_type,
    id_part='name',
    completer=get_resource_name_completion_list('Microsoft.MixedReality/spatialAnchorsAccounts')
)

spatial_anchors_account_key_type = CLIArgumentType(
    help='Key to be regenerated.',
    arg_type=get_enum_type(['primary', 'secondary']),
    options_list=['--key', '-k'],
)


def load_arguments(self, _):
    with self.argument_context('spatial-anchors-account') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('spatial_anchors_account_name', arg_type=spatial_anchors_account_name_type)

    with self.argument_context('spatial-anchors-account create') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)  # pylint: disable=line-too-long
        c.argument('tags', arg_type=tags_type)

    with self.argument_context('spatial-anchors-account key renew') as c:
        c.argument('key', arg_type=spatial_anchors_account_key_type)
