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
from azext_peering.action import (
    PeeringAddDirectConnections,
    PeeringAddExchangeConnections
)


def load_arguments(self, _):

    with self.argument_context('peering legacy list') as c:
        c.argument('peering_location', id_part=None, help='The location of the peering.')
        c.argument('kind', id_part=None, help='The kind of the peering.')

    with self.argument_context('peering asn create') as c:
        c.argument('name', id_part=None, help='The peer ASN name.')
        c.argument('peer_asn', id_part=None, help='The Autonomous System Number (ASN) of the peer.')
        c.argument('emails', id_part=None, help='The list of email addresses.')
        c.argument('phone', id_part=None, help='The list of contact numbers.')
        c.argument('peer_name', id_part=None, help='The name of the peer.')
        c.argument('validation_state', arg_type=get_enum_type(['None', 'Pending', 'Approved', 'Failed']), id_part=None, help='The validation state of the ASN associated with the peer.')

    with self.argument_context('peering asn update') as c:
        c.argument('name', id_part=None, help='The peer ASN name.')
        c.argument('peer_asn', id_part=None, help='The Autonomous System Number (ASN) of the peer.')
        c.argument('emails', id_part=None, help='The list of email addresses.')
        c.argument('phone', id_part=None, help='The list of contact numbers.')
        c.argument('peer_name', id_part=None, help='The name of the peer.')
        c.argument('validation_state', arg_type=get_enum_type(['None', 'Pending', 'Approved', 'Failed']), id_part=None, help='The validation state of the ASN associated with the peer.')

    with self.argument_context('peering asn delete') as c:
        c.argument('name', id_part=None, help='The peer ASN name.')

    with self.argument_context('peering asn list') as c:
        pass

    with self.argument_context('peering asn show') as c:
        c.argument('name', id_part=None, help='The peer ASN name.')

    with self.argument_context('peering location list') as c:
        c.argument('kind', id_part=None, help='The kind of the peering.')
        c.argument('direct_peering_type', id_part=None, help='The type of direct peering.')

    with self.argument_context('peering create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the peering.')
        c.argument('sku_name', arg_type=get_enum_type(['Basic_Exchange_Free', 'Basic_Direct_Free', 'Premium_Direct_Free', 'Premium_Exchange_Metered', 'Premium_Direct_Metered', 'Premium_Direct_Unlimited']), id_part=None, help='The name of the peering SKU.')
        c.argument('sku_tier', arg_type=get_enum_type(['Basic', 'Premium']), id_part=None, help='The tier of the peering SKU.')
        c.argument('sku_family', arg_type=get_enum_type(['Direct', 'Exchange']), id_part=None, help='The family of the peering SKU.')
        c.argument('sku_size', arg_type=get_enum_type(['Free', 'Metered', 'Unlimited']), id_part=None, help='The size of the peering SKU.')
        c.argument('kind', arg_type=get_enum_type(['Direct', 'Exchange']), id_part=None, help='The kind of the peering.')
        c.argument('direct_connections', id_part=None, help='The set of connections that constitute a direct peering.', action=PeeringAddDirectConnections, nargs='+')
        c.argument('direct_peer_asn', id_part=None, help='The reference of the peer ASN.')
        c.argument('direct_direct_peering_type', arg_type=get_enum_type(['Edge', 'Transit', 'Cdn', 'Internal']), id_part=None, help='The type of direct peering.')
        c.argument('exchange_connections', id_part=None, help='The set of connections that constitute an exchange peering.', action=PeeringAddExchangeConnections, nargs='+')
        c.argument('exchange_peer_asn', id_part=None, help='The reference of the peer ASN.')
        c.argument('peering_location', id_part=None, help='The location of the peering.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)

    with self.argument_context('peering update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the peering.')
        c.argument('sku_name', arg_type=get_enum_type(['Basic_Exchange_Free', 'Basic_Direct_Free', 'Premium_Direct_Free', 'Premium_Exchange_Metered', 'Premium_Direct_Metered', 'Premium_Direct_Unlimited']), id_part=None, help='The name of the peering SKU.')
        c.argument('sku_tier', arg_type=get_enum_type(['Basic', 'Premium']), id_part=None, help='The tier of the peering SKU.')
        c.argument('sku_family', arg_type=get_enum_type(['Direct', 'Exchange']), id_part=None, help='The family of the peering SKU.')
        c.argument('sku_size', arg_type=get_enum_type(['Free', 'Metered', 'Unlimited']), id_part=None, help='The size of the peering SKU.')
        c.argument('kind', arg_type=get_enum_type(['Direct', 'Exchange']), id_part=None, help='The kind of the peering.')
        c.argument('direct_connections', id_part=None, help='The set of connections that constitute a direct peering.', action=PeeringAddDirectConnections, nargs='+')
        c.argument('direct_peer_asn', id_part=None, help='The reference of the peer ASN.')
        c.argument('direct_direct_peering_type', arg_type=get_enum_type(['Edge', 'Transit', 'Cdn', 'Internal']), id_part=None, help='The type of direct peering.')
        c.argument('exchange_connections', id_part=None, help='The set of connections that constitute an exchange peering.', action=PeeringAddExchangeConnections, nargs='+')
        c.argument('exchange_peer_asn', id_part=None, help='The reference of the peer ASN.')
        c.argument('peering_location', id_part=None, help='The location of the peering.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)

    with self.argument_context('peering delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the peering.')

    with self.argument_context('peering list') as c:
        c.argument('resource_group', resource_group_name_type)

    with self.argument_context('peering show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the peering.')

    with self.argument_context('peering service location list') as c:
        pass

    with self.argument_context('peering service prefix create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('peering_service_name', id_part=None, help='The name of the peering service.')
        c.argument('name', id_part=None, help='The name of the prefix.')
        c.argument('prefix', id_part=None, help='The prefix from which your traffic originates.', required=True)

    with self.argument_context('peering service prefix update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('peering_service_name', id_part=None, help='The name of the peering service.')
        c.argument('name', id_part=None, help='The name of the prefix.')
        c.argument('prefix', id_part=None, help='The prefix from which your traffic originates.')

    with self.argument_context('peering service prefix delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('peering_service_name', id_part=None, help='The name of the peering service.')
        c.argument('name', id_part=None, help='The name of the prefix.')

    with self.argument_context('peering service prefix list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('peering_service_name', id_part=None, help='The name of the peering service.')

    with self.argument_context('peering service prefix show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('peering_service_name', id_part=None, help='The name of the peering service.')
        c.argument('name', id_part=None, help='The name of the prefix.')

    with self.argument_context('peering service provider list') as c:
        pass

    with self.argument_context('peering service create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the peering service.')
        c.argument('peering_service_location', id_part=None, help='The PeeringServiceLocation of the Customer.', required=True)
        c.argument('peering_service_provider', id_part=None, help='The MAPS Provider Name.', required=True)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)

    with self.argument_context('peering service update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the peering service.')
        c.argument('peering_service_location', id_part=None, help='The PeeringServiceLocation of the Customer.')
        c.argument('peering_service_provider', id_part=None, help='The MAPS Provider Name.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)

    with self.argument_context('peering service delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the peering service.')

    with self.argument_context('peering service list') as c:
        c.argument('resource_group', resource_group_name_type)

    with self.argument_context('peering service show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the peering service.')
