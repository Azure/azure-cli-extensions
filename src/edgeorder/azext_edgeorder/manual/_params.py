# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azext_edgeorder.action import (
    AddNotificationPreferences,
    AddManagementResourcePreferences,
)


def load_arguments(self, _):
    with self.argument_context('edgeorder order-item update') as c:
        c.argument('notification_email_list', options_list=['--notif-email-list'], nargs='+',
                   help='Additional notification email list.')
        c.argument('notification_preferences', options_list=['--notif-preferences'], action=AddNotificationPreferences,
                   nargs='+', help='Notification preferences.', arg_group='Preferences')
        c.argument('management_resource_preferences', options_list=['--mgmt-preferences'],
                   action=AddManagementResourcePreferences, nargs='+',
                   help='Preferences related to the Management resource.', arg_group='Preferences')
