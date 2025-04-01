# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType

admin_custom_sdk = CliCommandType(
    operations_tmpl="azext_load.data_plane.load_notifications.custom#{}"
)


def load_notification_commands(self, _):

    with self.command_group(
        "load notification-rule", custom_command_type=admin_custom_sdk, is_preview=True
    ) as g:
        g.custom_command("create", "create_notification_rule")
        g.custom_command("update", "update_notification_rule")
        g.custom_show_command("show", "show_notification_rule")
        g.custom_command("list", "list_notification_rules")
        g.custom_command("delete", "delete_notification_rule", confirmation=True)
