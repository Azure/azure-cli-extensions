# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long


def load_command_table(self, _):
    with self.command_group('aldo-edge-operator billing-configuration') as g:
        g.custom_command('show', 'show_billing_configuration')
        g.custom_command('create-or-update', 'create_or_update_billing_configuration')
        g.custom_command('list', 'list_billing_configurations')

    with self.command_group('aldo-edge-operator billing-configuration snapshot') as g:
        g.custom_command('show', 'show_billing_configuration_snapshot')
        g.custom_command('list', 'list_billing_configuration_snapshots')

