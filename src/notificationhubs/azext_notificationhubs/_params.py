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
        c.argument('is_availiable', arg_type=get_three_state_flag(), id_part=None, help='True if the name is available and can be used to create new Namespace/NotificationHub. Otherwise false.')
        c.argument('rights', id_part=None, help='The rights associated with the rule.', nargs='+')
        c.argument('policy_key', id_part=None, help='Name of the key that has to be regenerated for the Namespace/Notification Hub Authorization Rule. The value can be Primary Key/Secondary Key.')

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
        c.argument('is_availiable', arg_type=get_three_state_flag(), id_part=None, help='True if the name is available and can be used to create new Namespace/NotificationHub. Otherwise false.')
        c.argument('rights', id_part=None, help='The rights associated with the rule.', nargs='+')
        c.argument('policy_key', id_part=None, help='Name of the key that has to be regenerated for the Namespace/Notification Hub Authorization Rule. The value can be Primary Key/Secondary Key.')

    with self.argument_context('notificationhubs namespace delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')

    with self.argument_context('notificationhubs namespace show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')

    with self.argument_context('notificationhubs namespace list') as c:
        c.argument('resource_group', resource_group_name_type)

    with self.argument_context('notificationhubs namespace check_availability') as c:
        pass

    with self.argument_context('notificationhubs namespace list_keys') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('name', id_part=None, help='The connection string of the namespace for the specified authorizationRule.')

    with self.argument_context('notificationhubs namespace regenerate_keys') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('name', id_part=None, help='The connection string of the namespace for the specified authorizationRule.')

    with self.argument_context('notificationhubs namespace get_authorization_rule') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('name', id_part=None, help='The connection string of the namespace for the specified authorizationRule.')

    with self.argument_context('notificationhubs namespace list_authorization_rules') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')

    with self.argument_context('notificationhubs namespace create_or_update_authorization_rule') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('name', id_part=None, help='The connection string of the namespace for the specified authorizationRule.')

    with self.argument_context('notificationhubs namespace delete_authorization_rule') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('name', id_part=None, help='The connection string of the namespace for the specified authorizationRule.')

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
        c.argument('is_availiable', arg_type=get_three_state_flag(), id_part=None, help='True if the name is available and can be used to create new Namespace/NotificationHub. Otherwise false.')
        c.argument('rights', id_part=None, help='The rights associated with the rule.', nargs='+')
        c.argument('policy_key', id_part=None, help='Name of the key that has to be regenerated for the Namespace/Notification Hub Authorization Rule. The value can be Primary Key/Secondary Key.')

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
        c.argument('is_availiable', arg_type=get_three_state_flag(), id_part=None, help='True if the name is available and can be used to create new Namespace/NotificationHub. Otherwise false.')
        c.argument('rights', id_part=None, help='The rights associated with the rule.', nargs='+')
        c.argument('policy_key', id_part=None, help='Name of the key that has to be regenerated for the Namespace/Notification Hub Authorization Rule. The value can be Primary Key/Secondary Key.')

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

    with self.argument_context('notificationhubs hub check_notification_hub_availability') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')

    with self.argument_context('notificationhubs hub regenerate_keys') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('name', id_part=None, help='The connection string of the NotificationHub for the specified authorizationRule.')

    with self.argument_context('notificationhubs hub get_pns_credentials') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')

    with self.argument_context('notificationhubs hub list_keys') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('name', id_part=None, help='The connection string of the NotificationHub for the specified authorizationRule.')

    with self.argument_context('notificationhubs hub debug_send') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')

    with self.argument_context('notificationhubs hub list_authorization_rules') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')

    with self.argument_context('notificationhubs hub get_authorization_rule') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('name', id_part=None, help='The connection string of the NotificationHub for the specified authorizationRule.')

    with self.argument_context('notificationhubs hub create_or_update_authorization_rule') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('name', id_part=None, help='The connection string of the NotificationHub for the specified authorizationRule.')

    with self.argument_context('notificationhubs hub delete_authorization_rule') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('namespace_name', id_part=None, help='The namespace name.')
        c.argument('notification_hub_name', id_part=None, help='The notification hub name.')
        c.argument('name', id_part=None, help='The connection string of the NotificationHub for the specified authorizationRule.')
