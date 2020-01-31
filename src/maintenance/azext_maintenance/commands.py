# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from azure.cli.core.commands import CliCommandType

from ._client_factory import (cf_maintenance_configurations, cf_maintenance_updates, cf_configuration_assignments, cf_apply_updates)


def load_command_table(self, _):

    maintenance_configurations_mgmt_util = CliCommandType(
        operations_tmpl='azext_maintenance.maintenance.operations.maintenance_configurations_operations#MaintenanceConfigurationsOperations.{}',
        client_factory=cf_maintenance_configurations,
        client_arg_name='self'
    )

    maintenance_updates_mgmt_util = CliCommandType(
        operations_tmpl='azext_maintenance.maintenance.operations.updates_operations#UpdatesOperations.{}',
        client_factory=cf_maintenance_updates,
        client_arg_name='self'
    )

    configuration_assignments_mgmt_util = CliCommandType(
        operations_tmpl='azext_maintenance.maintenance.operations.configuration_assignments_operations#ConfigurationAssignmentsOperations.{}',
        client_factory=cf_configuration_assignments,
        client_arg_name='self'
    )

    apply_updates_mgmt_util = CliCommandType(
        operations_tmpl='azext_maintenance.maintenance.operations.apply_updates_operations#ApplyUpdatesOperations.{}',
        client_factory=cf_apply_updates,
        client_arg_name='self'
    )

    with self.command_group('maintenance configuration', maintenance_configurations_mgmt_util, client_factory=cf_maintenance_configurations) as g:
        g.custom_command('create', 'cli_configuration_create')
        g.command('delete', 'delete')
        g.custom_command('update', 'cli_configuration_create')
        g.command('show', 'get')
        g.command('list', 'list')

    with self.command_group('maintenance update', maintenance_updates_mgmt_util, client_factory=cf_maintenance_updates) as g:
        g.custom_command('list', 'cli_update_list')

    with self.command_group('maintenance assignment', configuration_assignments_mgmt_util, client_factory=cf_configuration_assignments) as g:
        g.custom_command('create', 'cli_assignment_create')
        g.custom_command('delete', 'cli_assignment_delete')
        g.custom_command('list', 'cli_assignment_list')

    with self.command_group('maintenance applyupdate', apply_updates_mgmt_util, client_factory=cf_apply_updates) as g:
        g.custom_command('create', 'cli_applyupdate_create')
        g.custom_command('get', 'cli_applyupdate_get')
