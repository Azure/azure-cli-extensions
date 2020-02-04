# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType
from ._validators import validate_notification_message


def load_command_table(self, _):

    from ._client_factory import cf_namespaces
    notificationhubs_namespaces = CliCommandType(
        operations_tmpl='azext_notification_hub.vendored_sdks.notificationhubs.operations.namespaces_operations#NamespacesOperations.{}',
        client_factory=cf_namespaces)
    with self.command_group('notification-hub namespace', notificationhubs_namespaces, client_factory=cf_namespaces, is_preview=True) as g:
        g.custom_command('create', 'create_notificationhubs_namespace')
        g.custom_command('update', 'update_notificationhubs_namespace')
        g.custom_command('delete', 'delete_notificationhubs_namespace', supports_no_wait=True, confirmation='Are you sure to delete this namespace and all its hubs?')
        g.custom_show_command('show', 'get_notificationhubs_namespace')
        g.custom_command('list', 'list_notificationhubs_namespace')
        g.custom_command('check-availability', 'check_availability_notificationhubs_namespace')
        g.wait_command('wait')
        g.custom_show_command('authorization-rule show', 'get_authorization_rule_notificationhubs_namespace')
        g.custom_command('authorization-rule list', 'list_authorization_rules_notificationhubs_namespace')
        g.custom_command('authorization-rule create', 'create_or_update_authorization_rule_notificationhubs_namespace')
        g.custom_command('authorization-rule delete', 'delete_authorization_rule_notificationhubs_namespace', confirmation=True)
        g.custom_command('authorization-rule list-keys', 'list_keys_notificationhubs_namespace')
        g.custom_command('authorization-rule regenerate-keys', 'regenerate_keys_notificationhubs_namespace')

    from ._client_factory import cf_notification_hubs
    notificationhubs_notification_hubs = CliCommandType(
        operations_tmpl='azext_notification_hub.vendored_sdks.notificationhubs.operations.notification_hubs_operations#NotificationHubsOperations.{}',
        client_factory=cf_notification_hubs)
    with self.command_group('notification-hub', notificationhubs_notification_hubs, client_factory=cf_notification_hubs, is_preview=True) as g:
        g.custom_command('create', 'create_notificationhubs_hub')
        g.custom_command('update', 'update_notificationhubs_hub')
        g.custom_command('delete', 'delete_notificationhubs_hub', confirmation=True)
        g.custom_show_command('show', 'get_notificationhubs_hub')
        g.custom_command('list', 'list_notificationhubs_hub')
        g.custom_command('check-availability', 'check_notification_hub_availability_notificationhubs_hub')
        g.custom_command('test-send', 'debug_send_notificationhubs_hub', validator=validate_notification_message)
        g.custom_command('authorization-rule list', 'list_authorization_rules_notificationhubs_hub')
        g.custom_show_command('authorization-rule show', 'get_authorization_rule_notificationhubs_hub')
        g.custom_command('authorization-rule create', 'create_or_update_authorization_rule_notificationhubs_hub')
        g.custom_command('authorization-rule delete', 'delete_authorization_rule_notificationhubs_hub')
        g.custom_command('authorization-rule list-keys', 'list_keys_notificationhubs_hub')
        g.custom_command('authorization-rule regenerate-keys', 'regenerate_keys_notificationhubs_hub')

    with self.command_group('notification-hub credential', notificationhubs_notification_hubs, client_factory=cf_notification_hubs) as g:
        g.custom_command('list', 'get_pns_credentials_notificationhubs_hub')
        g.custom_command('gcm update', 'update_gcm_credential')
        g.custom_command('apns update', 'update_apns_credential')
        g.custom_command('wns update', 'update_wns_credential')
        g.custom_command('mpns update', 'update_mpns_credential')
        g.custom_command('adm update', 'update_adm_credential')
        g.custom_command('baidu update', 'update_baidu_credential')
