# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long


def load_command_table(self, _):
    with self.command_group('staticwebapp enterprise-edge', is_preview=True) as g:
        g.custom_command('enable', 'enable_staticwebapp_enterprise_edge')
        g.custom_command('disable', 'disable_staticwebapp_enterprise_edge')
        g.custom_show_command('show', 'show_staticwebapp_enterprise_edge_status')
