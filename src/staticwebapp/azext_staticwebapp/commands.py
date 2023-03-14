# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_command_table(self, _):
    with self.command_group('staticwebapp dbconnection', is_preview=True) as g:
        g.custom_command('create', 'create_dbconnection')
        g.custom_show_command('show', 'show_dbconnection')
        g.custom_command('delete', 'delete_dbconnection', confirmation=True)
