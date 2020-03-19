# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from azext_migrateprojects.generated._client_factory import cf_database_instance
    migrateprojects_database_instance = CliCommandType(
        operations_tmpl='azext_migrateprojects.vendored_sdks.migrateprojects.operations._database_instance_operations#DatabaseInstanceOperations.{}',
        client_factory=cf_database_instance)
    with self.command_group('migrateprojects database-instance', migrateprojects_database_instance, client_factory=cf_database_instance) as g:
        g.custom_show_command('show', 'migrateprojects_database_instance_show')
        g.custom_command('enumerate-database-instance', 'migrateprojects_database_instance_enumerate_database_instance')

    from azext_migrateprojects.generated._client_factory import cf_database
    migrateprojects_database = CliCommandType(
        operations_tmpl='azext_migrateprojects.vendored_sdks.migrateprojects.operations._database_operations#DatabaseOperations.{}',
        client_factory=cf_database)
    with self.command_group('migrateprojects database', migrateprojects_database, client_factory=cf_database) as g:
        g.custom_show_command('show', 'migrateprojects_database_show')
        g.custom_command('enumerate-database', 'migrateprojects_database_enumerate_database')

    from azext_migrateprojects.generated._client_factory import cf_event
    migrateprojects_event = CliCommandType(
        operations_tmpl='azext_migrateprojects.vendored_sdks.migrateprojects.operations._event_operations#EventOperations.{}',
        client_factory=cf_event)
    with self.command_group('migrateprojects event', migrateprojects_event, client_factory=cf_event) as g:
        g.custom_show_command('show', 'migrateprojects_event_show')
        g.custom_command('delete', 'migrateprojects_event_delete')
        g.custom_command('enumerate-event', 'migrateprojects_event_enumerate_event')

    from azext_migrateprojects.generated._client_factory import cf_machine
    migrateprojects_machine = CliCommandType(
        operations_tmpl='azext_migrateprojects.vendored_sdks.migrateprojects.operations._machine_operations#MachineOperations.{}',
        client_factory=cf_machine)
    with self.command_group('migrateprojects machine', migrateprojects_machine, client_factory=cf_machine) as g:
        g.custom_show_command('show', 'migrateprojects_machine_show')
        g.custom_command('enumerate-machine', 'migrateprojects_machine_enumerate_machine')

    from azext_migrateprojects.generated._client_factory import cf_migrate_project
    migrateprojects_migrate_project = CliCommandType(
        operations_tmpl='azext_migrateprojects.vendored_sdks.migrateprojects.operations._migrate_project_operations#MigrateProjectOperations.{}',
        client_factory=cf_migrate_project)
    with self.command_group('migrateprojects migrate-project', migrateprojects_migrate_project, client_factory=cf_migrate_project) as g:
        g.custom_show_command('show', 'migrateprojects_migrate_project_show')
        g.custom_command('delete', 'migrateprojects_migrate_project_delete')
        g.custom_command('put-migrate-project', 'migrateprojects_migrate_project_put_migrate_project')
        g.custom_command('patch-migrate-project', 'migrateprojects_migrate_project_patch_migrate_project')
        g.custom_command('register-tool', 'migrateprojects_migrate_project_register_tool')
        g.custom_command('refresh-migrate-project-summary', 'migrateprojects_migrate_project_refresh_migrate_project_summary')

    from azext_migrateprojects.generated._client_factory import cf_solution
    migrateprojects_solution = CliCommandType(
        operations_tmpl='azext_migrateprojects.vendored_sdks.migrateprojects.operations._solution_operations#SolutionOperations.{}',
        client_factory=cf_solution)
    with self.command_group('migrateprojects solution', migrateprojects_solution, client_factory=cf_solution) as g:
        g.custom_show_command('show', 'migrateprojects_solution_show')
        g.custom_command('delete', 'migrateprojects_solution_delete')
        g.custom_command('put-solution', 'migrateprojects_solution_put_solution')
        g.custom_command('patch-solution', 'migrateprojects_solution_patch_solution')
        g.custom_command('get-config', 'migrateprojects_solution_get_config')
        g.custom_command('cleanup-solution-data', 'migrateprojects_solution_cleanup_solution_data')
        g.custom_command('enumerate-solution', 'migrateprojects_solution_enumerate_solution')
