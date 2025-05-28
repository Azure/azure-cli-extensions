# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals


def load_command_table(self, _):
    with self.command_group('notification-hub'):
        from azext_notification_hub.custom import NotificationHubCreate, NotificationHubUpdate
        self.command_table['notification-hub create'] = NotificationHubCreate(loader=self)
        self.command_table['notification-hub update'] = NotificationHubUpdate(loader=self)

    with self.command_group('notification-hub authorization-rule'):
        from azext_notification_hub.custom import RuleRegenerateKeys
        self.command_table['notification-hub authorization-rule regenerate-keys'] = RuleRegenerateKeys(loader=self)

    with self.command_group('notification-hub namespace'):
        from azext_notification_hub.custom import NamespaceCreate
        self.command_table['notification-hub namespace create'] = NamespaceCreate(loader=self)

    with self.command_group('notification-hub namespace authorization-rule'):
        from azext_notification_hub.custom import NamespaceRuleCreate, NamespaceRuleRegenerateKeys
        self.command_table['notification-hub namespace authorization-rule create'] = NamespaceRuleCreate(loader=self)
        self.command_table['notification-hub namespace authorization-rule regenerate-keys'] = NamespaceRuleRegenerateKeys(loader=self)

    with self.command_group('notification-hub credential'):
        from azext_notification_hub.custom import BaiduUpdate, ApnsUpdate, MpnsUpdate, AdmUpdate, WnsUpdate, GcmUpdate
        self.command_table['notification-hub credential gcm update'] = GcmUpdate(loader=self)
        self.command_table['notification-hub credential adm update'] = AdmUpdate(loader=self)
        self.command_table['notification-hub credential apns update'] = ApnsUpdate(loader=self)
        self.command_table['notification-hub credential wns update'] = WnsUpdate(loader=self)
        self.command_table['notification-hub credential mpns update'] = MpnsUpdate(loader=self)
        self.command_table['notification-hub credential baidu update'] = BaiduUpdate(loader=self)

    from ._client_factory import cf_notification_hubs
    from ._validators import validate_notification_message
    from azure.cli.core.commands import CliCommandType
    notificationhubs_notification_hubs = CliCommandType(
        operations_tmpl='azext_notification_hub.vendored_sdks.notificationhubs.operations.notification_hubs_operations#NotificationHubsOperations.{}',
        client_factory=cf_notification_hubs)
    with self.command_group('notification-hub', notificationhubs_notification_hubs, client_factory=cf_notification_hubs,
                            is_experimental=True) as g:
        g.custom_command('test-send', 'debug_send_notificationhubs_hub', validator=validate_notification_message)
