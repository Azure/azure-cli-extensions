# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    get_three_state_flag,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)


def load_arguments(self, _):

    with self.argument_context('notificationhubs namespace list') as c:
        pass

    with self.argument_context('notificationhubs namespace create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('sku_name', arg_type=get_enum_type(['Free', 'Basic', 'Standard']), id_part=None, help='Name of the notification hub sku')
        c.argument('sku_tier', id_part=None, help='The tier of particular sku')
        c.argument('sku_size', id_part=None, help='The Sku size')
        c.argument('sku_family', id_part=None, help='The Sku Family')
        c.argument('sku_capacity', id_part=None, help='The capacity of the resource')

    with self.argument_context('notificationhubs namespace update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('sku_name', arg_type=get_enum_type(['Free', 'Basic', 'Standard']), id_part=None, help='Name of the notification hub sku')
        c.argument('sku_tier', id_part=None, help='The tier of particular sku')
        c.argument('sku_size', id_part=None, help='The Sku size')
        c.argument('sku_family', id_part=None, help='The Sku Family')
        c.argument('sku_capacity', id_part=None, help='The capacity of the resource')

    with self.argument_context('notificationhubs namespace delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')

    with self.argument_context('notificationhubs namespace show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')

    with self.argument_context('notificationhubs namespace list') as c:
        c.argument('resource_group', resource_group_name_type)

    with self.argument_context('notificationhubs namespace check_availability') as c:
        c.argument('name', id_part=None, help='The namespace name to check.')
        pass

    with self.argument_context('notificationhubs namespace authorization_rule list_keys') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('name', id_part=None, help='The connection string of the namespace for the specified authorizationRule.')

    with self.argument_context('notificationhubs namespace authorization_rule regenerate_keys') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('name', id_part=None, help='The connection string of the namespace for the specified authorizationRule.')
        c.argument('policy_key', arg_type=get_enum_type(['Primary Key', 'Secondary Key']),id_part=None, help='Name of the key that has to be regenerated for the Namespace Authorization Rule.')

    with self.argument_context('notificationhubs namespace authorization_rule show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('name', id_part=None, help='Authorization rule name.')

    with self.argument_context('notificationhubs namespace authorization_rule list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')

    with self.argument_context('notificationhubs namespace authorization_rule create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('name', id_part=None, help='Authorization rule name.')
        c.argument('rights', id_part=None, help='The rights associated with the rule.')

    with self.argument_context('notificationhubs namespace authorization_rule delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('name', id_part=None, help='Authorization rule name.')

    with self.argument_context('notificationhubs hub create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('sku_name', arg_type=get_enum_type(['Free', 'Basic', 'Standard']), id_part=None, help='Name of the notification hub sku')
        c.argument('sku_tier', id_part=None, help='The tier of particular sku')
        c.argument('sku_size', id_part=None, help='The Sku size')
        c.argument('sku_family', id_part=None, help='The Sku Family')
        c.argument('sku_capacity', id_part=None, help='The capacity of the resource')
        c.argument('registration_ttl', id_part=None, help='The RegistrationTtl of the created NotificationHub')

    with self.argument_context('notificationhubs hub update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('sku_name', arg_type=get_enum_type(['Free', 'Basic', 'Standard']), id_part=None, help='Name of the notification hub sku')
        c.argument('sku_tier', id_part=None, help='The tier of particular sku')
        c.argument('sku_size', id_part=None, help='The Sku size')
        c.argument('sku_family', id_part=None, help='The Sku Family')
        c.argument('sku_capacity', id_part=None, help='The capacity of the resource')

    with self.argument_context('notificationhubs hub delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')

    with self.argument_context('notificationhubs hub show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')

    with self.argument_context('notificationhubs hub list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')

    with self.argument_context('notificationhubs hub check_availability') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name to check.')

    with self.argument_context('notificationhubs hub authorization_rule regenerate_keys') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('name', id_part=None, help='The authorization rule name.')
        c.argument('policy_key', arg_type=get_enum_type(['Primary Key', 'Secondary Key']),id_part=None, help='Name of the key that has to be regenerated for the Notification Hub Authorization Rule.')

    with self.argument_context('notificationhubs hub get_pns_credentials') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')

    with self.argument_context('notificationhubs hub authorization_rule list_keys') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('name', id_part=None, help='The authorization rule name.')

    with self.argument_context('notificationhubs hub debug_send') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('payload', id_part=None, help='The payload for message.')

    with self.argument_context('notificationhubs hub authorization_rule list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')

    with self.argument_context('notificationhubs hub authorization_rule show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('name', id_part=None, help='The connection string of the NotificationHub for the specified authorizationRule.')

    with self.argument_context('notificationhubs hub authorization_rule create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('name', id_part=None, help='The connection string of the NotificationHub for the specified authorizationRule.')
        c.argument('rights', id_part=None, help='The rights associated with the rule.')

    with self.argument_context('notificationhubs hub authorization_rule delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('name', id_part=None, help='The connection string of the NotificationHub for the specified authorizationRule.')

    with self.argument_context('notificationhubs hub credential gcm update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('google_api_key', id_part=None, help='Google GCM/FCM API key.')

    with self.argument_context('notificationhubs hub credential adm update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('client_id', id_part=None, help='The client identifier.')
        c.argument('client_secret', id_part=None, help='The credential secret access key.')

    with self.argument_context('notificationhubs hub credential apns update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('apns_certificate', id_part=None, help='The APNS certificate.')
        c.argument('certificate_key', id_part=None, help='The certificate key.')
        c.argument('key_id', id_part=None, help='A 10-character key identifier (kid) key, obtained from your developer account')
        c.argument('app_name', id_part=None, help='The name of the application')
        c.argument('app_id', id_part=None, help='The issuer (iss) registered claim key, whose value is your 10-character Team ID, obtained from your developer account')
        c.argument('token', id_part=None, help='Provider Authentication Token, obtained through your developer account.')

    with self.argument_context('notificationhubs hub credential baidu update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('baidu_api_key', id_part=None, help='Baidu API key.') 
        c.argument('baidu_secret_key', id_part=None, help='Baidu secret key.') 

    with self.argument_context('notificationhubs hub credential mpns update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('mpns_certificate', id_part=None, help='The MPNS certificate.')
        c.argument('certificate_key', id_part=None, help='The certificate key for this credential.') 
        # c.argument('thumbprint', id_part=None, help='The MPNS certificate Thumbprint.') 

    with self.argument_context('notificationhubs hub credential wns update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('package_sid', id_part=None, help='The package ID for this credential.')
        c.argument('secret_key', id_part=None, help='The secret key.') 
