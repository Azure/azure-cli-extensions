# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from argcomplete.completers import FilesCompleter
from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    get_location_type,
    file_type
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group

from ._validators import validate_cert_file


def load_arguments(self, _):
    payload_type = CLIArgumentType(
        options_list=['--payload'],
        help='The payload for the message in JSON format. '
    )

    with self.argument_context('notificationhubs namespace create') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('sku_name', arg_type=get_enum_type(['Free', 'Basic', 'Standard']), id_part=None, help='Name of the notification hub sku')

    with self.argument_context('notificationhubs namespace update') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('tags', tags_type)
        c.argument('sku_name', arg_type=get_enum_type(['Free', 'Basic', 'Standard']), id_part=None, help='Name of the notification hub sku')

    with self.argument_context('notificationhubs namespace delete') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')

    with self.argument_context('notificationhubs namespace show') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')

    with self.argument_context('notificationhubs namespace list') as c:
        pass

    with self.argument_context('notificationhubs namespace check-availability') as c:
        c.argument('name', id_part=None, options_list=['--name', '-n'], help='The namespace name to check.')

    with self.argument_context('notificationhubs namespace authorization-rule list-keys') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('rule_name', id_part=None, options_list=['--name', '-n'], help='The authorization rule name.')

    with self.argument_context('notificationhubs namespace authorization-rule regenerate-keys') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('rule_name', id_part=None, options_list=['--name', '-n'], help='The authorization rule name.')
        c.argument('policy_key', arg_type=get_enum_type(['Primary Key', 'Secondary Key']), id_part=None, help='Name of the key that has to be regenerated for the Namespace Authorization Rule.')

    with self.argument_context('notificationhubs namespace authorization-rule show') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('rule_name', id_part=None, options_list=['--name', '-n'], help='The authorization rule name.')

    with self.argument_context('notificationhubs namespace authorization-rule list') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')

    with self.argument_context('notificationhubs namespace authorization-rule create') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('rule_name', id_part=None, options_list=['--name', '-n'], help='The authorization rule name.')
        c.argument('rights', id_part=None, nargs='+', help='The rights associated with the rule.')

    with self.argument_context('notificationhubs namespace authorization-rule delete') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('rule_name', id_part=None, options_list=['--name', '-n'], help='The authorization rule name.')

    with self.argument_context('notificationhubs create') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('sku_name', arg_type=get_enum_type(['Free', 'Basic', 'Standard']), id_part=None, help='Name of the notification hub sku')
        c.argument('registration_ttl', id_part=None, help='The RegistrationTtl of the created NotificationHub')

    with self.argument_context('notificationhubs update') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('tags', tags_type)
        c.argument('sku_name', arg_type=get_enum_type(['Free', 'Basic', 'Standard']), id_part=None, help='Name of the notification hub sku')

    with self.argument_context('notificationhubs delete') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')

    with self.argument_context('notificationhubs show') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')

    with self.argument_context('notificationhubs list') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')

    with self.argument_context('notificationhubs check-availability') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name to check.')

    with self.argument_context('notificationhubs authorization-rule regenerate-keys') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('rule_name', id_part=None, options_list=['--name', '-n'], help='The authorization rule name.')
        c.argument('policy_key', arg_type=get_enum_type(['Primary Key', 'Secondary Key']), id_part=None, help='Name of the key that has to be regenerated for the Notification Hub Authorization Rule.')

    with self.argument_context('notificationhubs credential list') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')

    with self.argument_context('notificationhubs authorization-rule list-keys') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('rule_name', id_part=None, options_list=['--name', '-n'], help='The authorization rule name.')

    with self.argument_context('notificationhubs test-send') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('notification_format', arg_type=get_enum_type(['apple', 'baidu', 'gcm', 'template', 'windows', 'windowsphone']), id_part=None, help='The format of notification message.')
        c.argument('message', id_part=None, help='The message body to send. If not None, payload will be ignored')
        c.argument('title', id_part=None, help='The title of the notification.')
        c.argument('payload', arg_type=payload_type, id_part=None)
        c.argument('tag', id_part=None, help='You can send test notifications to a specific set of registrations using this option. Leave this field empty if you like to send push notifications to 10 random registrations on the selected platform.')

    with self.argument_context('notificationhubs authorization-rule list') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')

    with self.argument_context('notificationhubs authorization-rule show') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('rule_name', id_part=None, options_list=['--name', '-n'], help='The authorization rule name.')

    with self.argument_context('notificationhubs authorization-rule create') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('rule_name', id_part=None, options_list=['--name', '-n'], help='The authorization rule name.')
        c.argument('rights', id_part=None, nargs='+', help='The rights associated with the rule. Separated by comma.')

    with self.argument_context('notificationhubs authorization-rule delete') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('rule_name', id_part=None, options_list=['--name', '-n'], help='The authorization rule name.')

    with self.argument_context('notificationhubs credential gcm update') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('google_api_key', id_part=None, help='Google GCM/FCM API key.')

    with self.argument_context('notificationhubs credential adm update') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('client_id', id_part=None, help='The client identifier.')
        c.argument('client_secret', id_part=None, help='The credential secret access key.')

    with self.argument_context('notificationhubs credential apns update') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('apns_certificate', type=file_type, id_part=None, help='The APNS certificate.', validator=validate_cert_file, completer=FilesCompleter())
        c.argument('certificate_key', id_part=None, help='The certificate key.')
        c.argument('endpoint', id_part=None, help='The endpoint of this credential. Example values:"gateway.sandbox.push.apple.com","gateway.push.apple.com"')
        c.argument('key_id', id_part=None, help='A 10-character key identifier (kid) key, obtained from your developer account')
        c.argument('app_name', id_part=None, help='The name of the application/bundle id.')
        c.argument('app_id', id_part=None, help='The issuer (iss) registered claim key, whose value is your 10-character Team ID, obtained from your developer account')
        c.argument('token', id_part=None, help='Provider Authentication Token, obtained through your developer account.')

    with self.argument_context('notificationhubs credential baidu update') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('api_key', id_part=None, help='Baidu API key.')
        c.argument('secret_key', id_part=None, help='Baidu secret key.')

    with self.argument_context('notificationhubs credential mpns update') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('mpns_certificate', type=file_type, id_part=None, help='The MPNS certificate.', validator=validate_cert_file, completer=FilesCompleter())
        c.argument('certificate_key', id_part=None, help='The certificate key for this credential.')

    with self.argument_context('notificationhubs credential wns update') as c:
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('package_sid', id_part=None, help='The package ID for this credential.')
        c.argument('secret_key', id_part=None, help='The secret key.')
