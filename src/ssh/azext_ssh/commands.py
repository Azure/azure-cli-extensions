# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_command_table(self, _):

    with self.command_group('ssh') as g:
        g.custom_command('vm', 'ssh_vm')
        g.custom_command('config', 'ssh_config')
        g.custom_command('cert', 'ssh_cert')
