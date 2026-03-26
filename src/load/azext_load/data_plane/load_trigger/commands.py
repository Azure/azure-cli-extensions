# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType

admin_custom_sdk = CliCommandType(
    operations_tmpl="azext_load.data_plane.load_trigger.custom#{}"
)


def load_trigger_schedule_commands(self, _):
    with self.command_group(
        "load trigger", custom_command_type=admin_custom_sdk, is_preview=True
    ):
        pass

    with self.command_group(
        "load trigger schedule", custom_command_type=admin_custom_sdk, is_preview=True
    ) as g:
        g.custom_command("create", "create_trigger_schedule")
        g.custom_command("update", "update_trigger_schedule")
        g.custom_command("delete", "delete_trigger_schedule", confirmation=True)
        g.custom_show_command("show", "get_trigger_schedule")
        g.custom_command("pause", "pause_trigger_schedule")
        g.custom_command("enable", "enable_trigger_schedule")
        g.custom_command("list", "list_trigger_schedules")
