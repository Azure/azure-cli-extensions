# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

def load_command_table(self, _):

    with self.command_group('vme') as g:
        g.custom_command('upgrade', 'upgrade_vme')
        g.custom_command('install', 'install_vme')
        g.custom_command('uninstall', 'uninstall_vme')
