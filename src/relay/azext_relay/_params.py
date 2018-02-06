# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.parameters import (tags_type, get_enum_type, resource_group_name_type)
# pylint: disable=line-too-long


def load_arguments_namespace(self, _):
    with self.argument_context('relay') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('namespace_name', options_list=['--namespace-name'], help='name of the Namespace')

    with self.argument_context('relay namespace exists') as c:
        c.argument('namespace_name', options_list=['--name', '-n'], help='name of the Namespace')

    with self.argument_context('relay namespace create') as c:
        c.argument('namespace_name', options_list=['--name', '-n'], help='name of the Namespace')
        c.argument('tags', options_list=['--tags', '-t'], arg_type=tags_type, help='tags for the namespace in Key value pair format')
        c.argument('location', options_list=['--location', '-l'], help='Location')
        c.argument('skutier', options_list=['--sku-tier'], arg_type=get_enum_type(['Basic', 'Standard']))
        c.argument('capacity', options_list=['--capacity'], type=int, help='Capacity for Sku')

    # region Namespace Get
    for scope in ['relay namespace show', 'relay namespace delete']:
        with self.argument_context(scope) as c:
            c.argument('namespace_name', options_list=['--name', '-n'], help='name of the Namespace')

    # region Namespace Authorizationrule
    for scope in ['relay namespace authorizationrule', 'relay namespace authorizationrule keys list', 'relay namespace authorizationrule keys renew']:
        with self.argument_context(scope) as c:
            c.argument('authorization_rule_name', options_list=['--name', '-n'], help='name of the Namespace AuthorizationRule')

    with self.argument_context('relay namespace authorizationrule create') as c:
        c.argument('accessrights', options_list=['--access-rights'], arg_type=get_enum_type(['Send', 'Listen', 'Manage']), help='Authorization rule rights of type list')

    with self.argument_context('relay namespace authorizationrule keys renew') as c:
        c.argument('key_type', options_list=['--key-name'], arg_type=get_enum_type(['PrimaryKey', 'SecondaryKey']), help='specifies Primary or Secondary key needs to be reset')


# region - WCF Relay Create
def load_arguments_wcfrelay(self, _):
    with self.argument_context('relay wcfrelay') as c:
        c.argument('relay_name', options_list=['--name', '-n'], help='Name of WCF Relay')

    with self.argument_context('relay wcfrelay create') as c:
        c.argument('relay_type', options_list=['--relay-type'], arg_type=get_enum_type(['NetTcp', 'Http']), help='WCF relay type.')
        c.argument('requires_client_authorization', options_list=['--requires-client-authorization'], type=bool, help='True if client authorization is needed for this relay; otherwise, false.')
        c.argument('requires_transport_security', options_list=['--requires-transport-security'], type=bool, help='True if transport security is needed for this relay; otherwise, false.')
        c.argument('user_metadata', options_list=['--user-metadata'], help='The usermetadata is a placeholder to store user-defined string data for the WCF Relay endpoint. For example, it can be used to store descriptive data, such as list of teams and their contact information. Also, user-defined configuration settings can be stored.')

    # region WCF Relay Authorizationrule
    for scope in ['relay wcfrelay authorizationrule', 'relay wcfrelay authorizationrule keys list', 'relay wcfrelay authorizationrule keys renew']:
        with self.argument_context(scope) as c:
            c.argument('authorization_rule_name', options_list=['--name', '-n'], help='name of the WCF Relay AuthorizationRule')
            c.argument('relay_name', options_list=['--wcfrelay-name'], help='name of the WCF Relay')

    with self.argument_context('relay wcfrelay authorizationrule create') as c:
        c.argument('rights', options_list=['--access-rights'], arg_type=get_enum_type(['Send', 'Listen', 'Manage']), help='AuthorizationRule rights of type list')

    with self.argument_context('relay wcfrelay authorizationrule keys renew') as c:
        c.argument('key_type', options_list=['--key-name'], arg_type=get_enum_type(['PrimaryKey', 'SecondaryKey']))


# region - Hybrid Connection Create
def load_arguments_hybridconnections(self, _):
    with self.argument_context('relay hybrid-connections') as c:
        c.argument('hybrid_connection_name', options_list=['--name', '-n'], help='Name of Hybrid Connection')

    with self.argument_context('relay hybrid-connections create') as c:
        c.argument('requires_client_authorization', options_list=['--requires-client-authorization'], type=bool, help='True if client authorization is needed for this relay; otherwise, false.')
        c.argument('user_metadata', options_list=['--user-metadata'], help='The usermetadata is a placeholder to store user-defined string data for the Hybrid Connection endpoint. For example, it can be used to store descriptive data, such as list of teams and their contact information. Also, user-defined configuration settings can be stored.')

    # region Hybrid Connection Authorizationrule
    for scope in ['relay hybrid-connections authorizationrule', 'relay hybrid-connections authorizationrule keys list', 'relay Hybrid Connection authorizationrule keys renew']:
        with self.argument_context(scope) as c:
            c.argument('authorization_rule_name', options_list=['--name', '-n'], help='name of the Hybrid Connection AuthorizationRule')
            c.argument('hybrid_connection_name', options_list=['--hybrid-connection-name'], help='name of the Hybrid Connection')

    with self.argument_context('relay hybrid-connections authorizationrule create') as c:
        c.argument('rights', options_list=['--access-rights'], arg_type=get_enum_type(['Send', 'Listen', 'Manage']), help='AuthorizationRule rights of type list')

    with self.argument_context('relay hybrid-connections authorizationrule keys renew') as c:
        c.argument('key_type', options_list=['--key-name'], arg_type=get_enum_type(['PrimaryKey', 'SecondaryKey']))
