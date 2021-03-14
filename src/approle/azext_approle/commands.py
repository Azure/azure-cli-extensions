# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

def load_command_table(self, _):

    with self.command_group("approle") as g:
        g.custom_command("assignment list", "list_role_assignments")
        g.custom_command("assignment add", "add_role_assignment")
        g.custom_command("assignment remove", "remove_role_assignment")

    with self.command_group("approle", is_preview=True):
        pass
