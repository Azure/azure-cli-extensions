# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


# pylint: disable=line-too-long
def load_command_table(self, _):

    with self.command_group('mysql flexible-server') as g:
        g.custom_command('connect', 'connect_to_flexible_server_mysql')
        g.custom_command('execute', 'execute_flexible_server_mysql')

    with self.command_group('postgres flexible-server') as g:
        g.custom_command('connect', 'connect_to_flexible_server_postgres')
        g.custom_command('execute', 'execute_flexible_server_postgres')
