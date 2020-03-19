# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from azure.cli.core.commands import CliCommandType

from ._client_factory import (cf_maintenance_configurations, cf_maintenance_updates, cf_configuration_assignments, cf_apply_updates)


def load_command_table(self, _):

    maintenance_configurations_mgmt_util = CliCommandType(
        operations_tmpl='azext_maintenance.vendored_sdks.operations.maintenance_configurations_operations#MaintenanceConfigurationsOperations.{}',
        client_factory=cf_maintenance_configurations
    )

    maintenance_updates_mgmt_util = CliCommandType(
        operations_tmpl='azext_maintenance.vendored_sdks.operations.updates_operations#UpdatesOperations.{}',
        client_factory=cf_maintenance_updates
    )

    configuration_assignments_mgmt_util = CliCommandType(
        operations_tmpl='azext_maintenance.vendored_sdks.operations.configuration_assignments_operations#ConfigurationAssignmentsOperations.{}',
        client_factory=cf_configuration_assignments
    )

    apply_updates_mgmt_util = CliCommandType(
        operations_tmpl='azext_maintenance.vendored_sdks.operations.apply_updates_operations#ApplyUpdatesOperations.{}',
        client_factory=cf_apply_updates
    )

    with self.command_group('maintenance configuration', maintenance_configurations_mgmt_util, client_factory=cf_maintenance_configurations) as g:
        g.custom_command('create', 'cli_configuration_create')
        g.command('delete', 'delete')
        g.custom_command('update', 'cli_configuration_create')
        g.show_command('show', 'get')
        g.command('list', 'list')

    with self.command_group('maintenance update', maintenance_updates_mgmt_util, client_factory=cf_maintenance_updates) as g:
        g.custom_command('list', 'cli_update_list')

    with self.command_group('maintenance assignment', configuration_assignments_mgmt_util, client_factory=cf_configuration_assignments) as g:
        g.custom_command('create', 'cli_assignment_create')
        g.custom_command('delete', 'cli_assignment_delete')
        g.custom_command('list', 'cli_assignment_list')

    with self.command_group('maintenance applyupdate', apply_updates_mgmt_util, client_factory=cf_apply_updates) as g:
        g.custom_command('create', 'cli_applyupdate_create')
        g.custom_command('get', 'cli_applyupdate_get', deprecate_info=g.deprecate(redirect='maintenance applyupdate show'))
        g.custom_command('show', 'cli_applyupdate_get')
