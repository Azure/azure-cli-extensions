# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azext_acrcssc._client_factory import cf_acr


def load_command_table(self, _):
    # required to mark the command as 'preview', can be expanded if additional commands are added
    self.command_group("acr supply-chain", client_factory=cf_acr, is_preview=True)

    with self.command_group("acr supply-chain workflow", client_factory=cf_acr, is_preview=True) as g:
        g.custom_command("create", "create_acrcssc")
        g.custom_command("update", "update_acrcssc")
        g.custom_command("delete", "delete_acrcssc")
        g.custom_show_command("show", "show_acrcssc")
        g.custom_command("cancel-run", "cancel_runs")
        g.custom_command("list", "list_scan_status")
