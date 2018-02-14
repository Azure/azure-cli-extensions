# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.commands.parameters import (tags_type, get_enum_type, get_location_type, name_type, resource_group_name_type, get_three_state_flag)
from knack.arguments import CLIArgumentType
from azext_relay.relay.models.relay_management_client_enums import AccessRights, KeyType, SkuTier, Relaytype


rights_arg_type = CLIArgumentType(options_list=['--access-rights'], nargs='+', type=str, arg_type=get_enum_type(AccessRights), help='Authorization rule rights of type list')
key_arg_type = CLIArgumentType(options_list=['--key-name'], arg_type=get_enum_type(KeyType), help='specifies Primary or Secondary key needs to be reset')


def load_arguments_relayparams(self, _):
    with self.argument_context('relay') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('namespace_name', options_list=['--namespace-name'], help='name of the Namespace')

    with self.argument_context('relay namespace') as c:
        c.argument('namespace_name', arg_type=name_type, help='name of the Namespace')

    with self.argument_context('relay namespace create') as c:
        c.argument('tags', arg_type=tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('skutier', options_list=['--sku-tier'], arg_type=get_enum_type(SkuTier))
        c.argument('capacity', options_list=['--capacity'], type=int, help='Capacity for Sku')

    for scope in ['relay namespace authorization-rule', 'relay namespace authorization-rule keys renew', 'relay namespace authorization-rule keys list']:
        with self.argument_context(scope) as c:
            c.argument('authorization_rule_name', arg_type=name_type, help='name of the Namespace AuthorizationRule')
            c.argument('namespace_name', options_list=['--namespace-name'], help='name of the Namespace')

    with self.argument_context('relay namespace authorization-rule create') as c:
        c.argument('accessrights', arg_type=rights_arg_type)

    with self.argument_context('relay namespace authorization-rule keys renew') as c:
        c.argument('key_type', arg_type=key_arg_type)

# region WCF Relay
    with self.argument_context('relay wcf-relay') as c:
        c.argument('relay_name', arg_type=name_type, help='Name of WCF Relay')

    with self.argument_context('relay wcf-relay create') as c:
        c.argument('relay_type', options_list=['--relay-type'], arg_type=get_enum_type(Relaytype), help='WCF relay type.')
        c.argument('requires_client_authorization', options_list=['--requires-client-authorization'], arg_type=get_three_state_flag(), help='True if client authorization is needed for this relay; otherwise, false.')
        c.argument('requires_transport_security', options_list=['--requires-transport-security'], arg_type=get_three_state_flag(), help='True if transport security is needed for this relay; otherwise, false.')
        c.argument('user_metadata', help='The usermetadata is a placeholder to store user-defined string data for the WCF Relay endpoint. For example, it can be used to store descriptive data, such as list of teams and their contact information. Also, user-defined configuration settings can be stored.')

    for scope in ['relay wcf-relay authorization-rule', 'relay wcf-relay authorization-rule keys list', 'relay wcf-relay authorization-rule keys renew']:
        with self.argument_context(scope) as c:
            c.argument('authorization_rule_name', arg_type=name_type, help='name of the WCF Relay AuthorizationRule')
            c.argument('relay_name', options_list=['--wcfrelay-name'], help='name of the WCF Relay')

    with self.argument_context('relay wcf-relay authorization-rule create') as c:
        c.argument('rights', arg_type=rights_arg_type)

    with self.argument_context('relay wcf-relay authorization-rule keys renew') as c:
        c.argument('key_type', arg_type=key_arg_type)

# region Hybrid Connection
    with self.argument_context('relay hybrid-connections') as c:
        c.argument('hybrid_connection_name', arg_type=name_type, help='Name of Hybrid Connection')

    with self.argument_context('relay hybrid-connections create') as c:
        c.argument('requires_client_authorization', arg_type=get_three_state_flag(), help='True if client authorization is needed for this relay; otherwise, false.')
        c.argument('user_metadata', help='The usermetadata is a placeholder to store user-defined string data for the Hybrid Connection endpoint. For example, it can be used to store descriptive data, such as list of teams and their contact information. Also, user-defined configuration settings can be stored.')

    for scope in ['relay hybrid-connections authorization-rule', 'relay hybrid-connections authorization-rule keys list', 'relay Hybrid Connection authorization-rule keys renew']:
        with self.argument_context(scope) as c:
            c.argument('authorization_rule_name', arg_type=name_type, help='name of the Hybrid Connection AuthorizationRule')
            c.argument('hybrid_connection_name', options_list=['--hybrid-connection-name'], help='name of the Hybrid Connection')

    with self.argument_context('relay hybrid-connections authorization-rule create') as c:
        c.argument('rights', arg_type=rights_arg_type)

    with self.argument_context('relay hybrid-connections authorization-rule keys renew') as c:
        c.argument('key_type', arg_type=key_arg_type)
