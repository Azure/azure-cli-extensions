# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

def load_command_table(self, _):

    with self.command_group('hybrid-appliance', is_preview=True) as g:
        g.custom_command('validate', 'validate_hybrid_appliance')
        g.custom_command('create', 'create_hybrid_appliance')
        g.custom_command('upgrade', 'upgrade_hybrid_appliance')
        g.custom_command('delete', 'delete_hybrid_appliance')
        g.custom_command('troubleshoot', 'collect_logs')
