# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals


def load_command_table(self, _):
    with self.command_group('notification-hub credential'):
        from azext_notification_hub.aaz.latest.notification_hub.credential.gcm import Create as GcmUpdate
        from azext_notification_hub.aaz.latest.notification_hub.credential.adm import Create as AdmUpdate
        from azext_notification_hub.aaz.latest.notification_hub.credential.wns import Create as WnsUpdate
        from azext_notification_hub.custom import BaiduUpdate, ApnsUpdate, MpnsUpdate
        self.command_table['notification-hub credential gcm update'] = GcmUpdate(loader=self)
        self.command_table['notification-hub credential adm update'] = AdmUpdate(loader=self)
        self.command_table['notification-hub credential apns update'] = ApnsUpdate(loader=self)
        self.command_table['notification-hub credential wns update'] = WnsUpdate(loader=self)
        self.command_table['notification-hub credential mpns update'] = MpnsUpdate(loader=self)
        self.command_table['notification-hub credential baidu update'] = BaiduUpdate(loader=self)
