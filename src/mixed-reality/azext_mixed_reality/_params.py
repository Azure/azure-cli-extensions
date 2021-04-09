# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azure.cli.core.commands.parameters import (
    resource_group_name_type,
    get_location_type,
    get_enum_type,
    tags_type,
    name_type
)
from azext_mixed_reality.action import AddSku


def load_arguments(self, _):
    with self.argument_context('spatial-anchors-account') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('account_name', type=str, help='Name of an mixed reality account.',
                   options_list=['--account-name', '--name', '-n', c.deprecate(target='--spatial-anchors-account-name', hide=True)], id_part='name')  # pylint: disable=line-too-long
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False, validator=get_default_location_from_resource_group)  # pylint: disable=line-too-long
        c.argument('tags', tags_type)
        c.argument('sku', action=AddSku, nargs='+', help='The sku associated with this account')
        c.argument('kind', action=AddSku, nargs='+', help='The kind of account, if supported')
        c.argument('storage_account_name', type=str, help='The name of the storage account associated with this accountId')  # pylint: disable=line-too-long

    with self.argument_context('spatial-anchors-account key renew') as c:
        c.argument('serial', arg_type=get_enum_type(['1', '2'], '1'), help='serial of key to be regenerated.')

    with self.argument_context('remote-rendering-account') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('account_name', type=str, help='Name of an mixed reality account.', arg_type=name_type, id_part='name')  # pylint: disable=line-too-long
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)
        c.argument('sku', action=AddSku, nargs='+', help='The sku associated with this account')
        c.argument('kind', action=AddSku, nargs='+', help='The kind of account, if supported')
        c.argument('storage_account_name', type=str, help='The name of the storage account associated with this accountId')  # pylint: disable=line-too-long

    with self.argument_context('remote-rendering-account key renew') as c:
        c.argument('serial', arg_type=get_enum_type(['1', '2'], '1'), help='serial of key to be regenerated')
