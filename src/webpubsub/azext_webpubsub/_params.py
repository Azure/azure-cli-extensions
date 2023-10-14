# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    tags_type,
    get_three_state_flag,
    get_enum_type
)
from .vendored_sdks.azure_mgmt_webpubsub.models import WebPubSubRequestType
from ._actions import (
    EventHandlerTemplateUpdateAction
)
from ._validator import validate_network_rule

WEBPUBSUB_KEY_TYPE = ['primary', 'secondary', 'salt']
PERMISSION_TYPE = ['joinLeaveGroup', 'sendToGroup']


def load_arguments(self, _):
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    webpubsub_name_type = CLIArgumentType(options_list='--webpubsub-name-name', help='Name of the Webpubsub.', id_part='name')
    webpubsubhub_name_type = CLIArgumentType(help='Name of the hub.', id_part='child_name_1')

    with self.argument_context('webpubsub') as c:
        c.argument('tags', tags_type)
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('webpubsub_name', webpubsub_name_type, options_list=['--name', '-n'])

    with self.argument_context('webpubsub create') as c:
        c.argument('sku', help='The sku name of the webpubsub service. Allowed values: Free_F1, Standard_S1, Premium_P1')
        c.argument('unit_count', help='The number of webpubsub service unit count', type=int)
        c.argument('kind', help='The kind of the webpubsub service. Allowed values: WebPubSub, SocketIO')

    with self.argument_context('webpubsub update') as c:
        c.argument('sku', help='The sku name of the webpubsub service. Allowed values: Free_F1, Standard_S1, Premium_P1')
        c.argument('unit_count', help='The number of webpubsub service unit count', type=int)

    with self.argument_context('webpubsub key regenerate') as c:
        c.argument('key_type', arg_type=get_enum_type(WEBPUBSUB_KEY_TYPE), help='The name of access key to regenerate')

    # Network Rule
    with self.argument_context('webpubsub network-rule update', validator=validate_network_rule) as c:
        c.argument('connection_name', nargs='*', help='Space-separeted list of private endpoint connection name.', required=False, arg_group='Private Endpoint Connection')
        c.argument('public_network', arg_type=get_three_state_flag(), help='Set rules for public network.', required=False, arg_group='Public Network')
        c.argument('allow', arg_type=get_enum_type(WebPubSubRequestType), nargs='*', help='The allowed virtual network rule. Space-separeted list of scope to assign.', type=WebPubSubRequestType, required=False)
        c.argument('deny', arg_type=get_enum_type(WebPubSubRequestType), nargs='*', help='The denied virtual network rule. Space-separeted list of scope to assign.', type=WebPubSubRequestType, required=False)

    for scope in ['webpubsub hub delete',
                  'webpubsub hub show']:
        with self.argument_context(scope) as c:
            c.argument('hub_name', webpubsubhub_name_type)

    for scope in ['webpubsub hub update',
                  'webpubsub hub create']:
        with self.argument_context(scope) as c:
            c.argument('hub_name', help='The hub to manage')
            c.argument('event_handler', action=EventHandlerTemplateUpdateAction, nargs='*', help='Template item for event handler settings. Use key=value pattern to set properties. Supported keys are "url-template", "user-event-pattern", "system-event", "auth-type" and "auth-resource". Setting multiple "system-event" results in an array and for other properties, only last set takes active.')
            c.argument('allow_anonymous', arg_type=get_three_state_flag(), help='Set if anonymous connections are allowed for this hub. True means allow and False means deny.')

    with self.argument_context('webpubsub hub list') as c:
        c.argument('webpubsub_name', webpubsub_name_type, options_list=['--name', '-n'], id_part=None)

    with self.argument_context('webpubsub client') as c:
        c.argument('hub_name', help='The hub which client connects to')

    with self.argument_context('webpubsub service') as c:
        c.argument('hub_name', help='The hub to manage.')

    for scope in ['webpubsub service broadcast', 'webpubsub service connection send', 'webpubsub service group send', 'webpubsub service user send']:
        with self.argument_context(scope) as c:
            c.argument('payload', help='A string payload to send.')

    for scope in ['webpubsub service connection',
                  'webpubsub service group add-connection',
                  'webpubsub service group remove-connection',
                  'webpubsub service permission grant',
                  'webpubsub service permission revoke',
                  'webpubsub service permission check']:
        with self.argument_context(scope) as c:
            c.argument('connection_id', help='The connection id.')

    for scope in ['webpubsub service group',
                  'webpubsub service permission grant',
                  'webpubsub service permission revoke',
                  'webpubsub service permission check']:
        with self.argument_context(scope) as c:
            c.argument('group_name', help='The group name.')

    for scope in ['webpubsub client',
                  'webpubsub service group add-user',
                  'webpubsub service group remove-user',
                  'webpubsub service user']:
        with self.argument_context(scope) as c:
            c.argument('user_id', help='The user id.')

    with self.argument_context('webpubsub service permission') as c:
        c.argument('permission', arg_type=get_enum_type(PERMISSION_TYPE), help='The permission')
