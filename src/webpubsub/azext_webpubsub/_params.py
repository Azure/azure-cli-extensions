# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    tags_type,
    get_three_state_flag,
    get_enum_type,
)
from .vendored_sdks.azure_mgmt_webpubsub.models import WebPubSubRequestType
from ._actions import (
    EventHandlerTemplateUpdateAction,
    IPRuleTemplateUpdateAction
)
from ._validator import validate_network_rule, validate_ip_rule

WEBPUBSUB_KEY_TYPE = ['primary', 'secondary', 'salt']
PERMISSION_TYPE = ['joinLeaveGroup', 'sendToGroup']


def load_arguments(self, _):
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    webpubsub_name_type = CLIArgumentType(options_list='--webpubsub-name',
                                          help='Name of the webpubsub.', id_part='name')
    webpubsubhub_name_type = CLIArgumentType(help='Name of the hub.', id_part='child_name_1')
    webpubsub_custom_certificate_name_type = CLIArgumentType(
        help='Name of the custom certificate.', id_part='child_name_1')
    webpubsub_custom_domain_name_type = CLIArgumentType(
        help='Name of the custom domain.', id_part='child_name_2')
    webpubsub_replica_name_type = CLIArgumentType(help='Name of the replica.', id_part='child_name_1')

    with self.argument_context('webpubsub') as c:
        c.argument('tags', tags_type)
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('webpubsub_name', webpubsub_name_type, options_list=['--name', '-n'])

    with self.argument_context('webpubsub create') as c:
        c.argument('sku', help='The sku name of the webpubsub service. Allowed values: Free_F1, Standard_S1, Premium_P1')
        c.argument('unit_count', help='The number of webpubsub service unit count', type=int)
        c.argument('kind', help='The kind of the webpubsub service. Allowed values: WebPubSub, SocketIO')
        c.argument('service_mode', help='The mode used in kind: SocketIO. Allowed values: Default, Serverless')

    with self.argument_context('webpubsub update') as c:
        c.argument('sku', help='The sku name of the webpubsub service. Allowed values: Free_F1, Standard_S1, Premium_P1')
        c.argument('unit_count', help='The number of webpubsub service unit count', type=int)
        c.argument('service_mode', help='The mode used in kind: SocketIO. Allowed values: Default, Serverless')
        c.argument('client_cert_enabled',
                   help='Enable or disable client certificate authentication for a WebPubSub Service', arg_type=get_three_state_flag())
        c.argument('disable_local_auth',
                   help='Enable or disable local auth for a WebPubSub Service', arg_type=get_three_state_flag())
        c.argument('region_endpoint_enabled',
                   help='Enable or disable region endpoint for a WebPubSub Service', arg_type=get_three_state_flag())

    with self.argument_context('webpubsub key regenerate') as c:
        c.argument('key_type', arg_type=get_enum_type(WEBPUBSUB_KEY_TYPE), help='The name of access key to regenerate')

    # Network Rule
    with self.argument_context('webpubsub network-rule update', validator=validate_network_rule) as c:
        c.argument('connection_name', nargs='*', help='Space-separeted list of private endpoint connection name.',
                   required=False, arg_group='Private Endpoint Connection')
        c.argument('public_network', arg_type=get_three_state_flag(),
                   help='Set rules for public network.', required=False, arg_group='Public Network')
        c.argument('allow', arg_type=get_enum_type(WebPubSubRequestType), nargs='*',
                   help='The allowed virtual network rule. Space-separeted list of scope to assign.', type=WebPubSubRequestType, required=False)
        c.argument('deny', arg_type=get_enum_type(WebPubSubRequestType), nargs='*',
                   help='The denied virtual network rule. Space-separeted list of scope to assign.', type=WebPubSubRequestType, required=False)

    for scope in ['webpubsub network-rule ip-rule add', 'webpubsub network-rule ip-rule remove']:
        with self.argument_context(scope, validator=validate_ip_rule) as c:
            c.argument('ip_rule', action=IPRuleTemplateUpdateAction, nargs='*',
                       help='The IP rule for the hub.', required=True)

    for scope in ['webpubsub hub delete',
                  'webpubsub hub show']:
        with self.argument_context(scope) as c:
            c.argument('hub_name', webpubsubhub_name_type)

    for scope in ['webpubsub hub update',
                  'webpubsub hub create']:
        with self.argument_context(scope) as c:
            c.argument('hub_name', help='The hub to manage')
            c.argument('event_handler', action=EventHandlerTemplateUpdateAction, nargs='*',
                       help='Template item for event handler settings. Use key=value pattern to set properties. Supported keys are "url-template", "user-event-pattern", "system-event", "auth-type" and "auth-resource". Setting multiple "system-event" results in an array and for other properties, only last set takes active.')
            c.argument('allow_anonymous', arg_type=get_three_state_flag(
            ), help='Set if anonymous connections are allowed for this hub. True means allow and False means deny.')
            c.argument('websocket_keepalive',
                       help='The WebSocket keep-alive interval in seconds for all clients in the hub. Valid range: 1 to 120. Default to 20 seconds.')

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

    # Replica
    for scope in ['webpubsub replica create',
                  'webpubsub replica list',
                  'webpubsub replica delete',
                  'webpubsub replica show',
                  'webpubsub replica start',
                  'webpubsub replica stop',
                  'webpubsub replica restart']:
        with self.argument_context(scope) as c:
            c.argument('sku', help='The sku name of the replica. Currently allowed values: Premium_P1')
            c.argument('unit_count', help='The number of webpubsub service unit count', type=int)
            c.argument('replica_name', webpubsub_replica_name_type)

    for scope in ['webpubsub replica create',
                  'webpubsub replica list',
                  'webpubsub replica update']:
        with self.argument_context(scope) as c:
            c.argument('webpubsub_name', webpubsub_name_type, options_list=['--name', '-n'], id_part=None)

    for scope in ['webpubsub replica show',
                  'webpubsub replica delete']:
        with self.argument_context(scope) as c:
            c.argument('webpubsub_name', webpubsub_name_type, options_list=['--name', '-n'])

    with self.argument_context('webpubsub replica update') as c:
        c.argument('replica_name', webpubsub_replica_name_type)
        c.argument('unit_count', help='The number of webpubsub service unit count', type=int)
        c.argument('region_endpoint_enabled',
                   help='Enable or disable region endpoint for a WebPubSub Service', arg_type=get_three_state_flag())

    # Custom Certificate
    for scope in ['webpubsub custom-certificate create',
                  'webpubsub custom-certificate show',
                  'webpubsub custom-certificate delete',
                  'webpubsub custom-certificate list']:
        with self.argument_context(scope) as c:
            c.argument('webpubsub_name', webpubsub_name_type, id_part=None)
            c.argument('certificate_name', webpubsub_custom_certificate_name_type)

    for scope in ['webpubsub custom-certificate create']:
        with self.argument_context(scope) as c:
            c.argument('key_vault_base_uri', help="Key vault base URI. For example, `https://contoso.vault.azure.net`.")
            c.argument('key_vault_secret_name', help="Key vault secret name where certificate is stored.")
            c.argument('key_vault_secret_version',
                       help="Key vault secret version where certificate is stored. If empty, will use latest version.")

    # Custom Domain
    for scope in ['webpubsub custom-domain create',
                  'webpubsub custom-domain show',
                  'webpubsub custom-domain delete',
                  'webpubsub custom-domain list']:
        with self.argument_context(scope) as c:
            c.argument('webpubsub_name', webpubsub_name_type, id_part=None)
            c.argument('name', webpubsub_custom_domain_name_type)

    for scope in ['webpubsub custom-domain create']:
        with self.argument_context(scope) as c:
            c.argument('domain_name', help="Custom domain name. For example, `contoso.com`.")
            c.argument('certificate_resource_id', help="Resource ID of the certificate.")

    # Managed Identity
    with self.argument_context('webpubsub identity assign') as c:
        c.argument(
            'identity', help="Assigns managed identities to the service. Use '[system]' to refer to the system-assigned identity or a resource ID to refer to a user-assigned identity. You can only assign either one of them.")
