# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from ._client_factory import cf_location
    migrate_location = CliCommandType(
        operations_tmpl='azext_migrate.vendored_sdks.migrate.operations._location_operations#LocationOperations.{}',
        client_factory=cf_location)
    with self.command_group('migrate location', migrate_location, client_factory=cf_location) as g:
        g.custom_command('check-name-availability', 'migrate_location_check_name_availability')

    from ._client_factory import cf_assessment_options
    migrate_assessment_options = CliCommandType(
        operations_tmpl='azext_migrate.vendored_sdks.migrate.operations._assessment_options_operations#AssessmentOptionsOperations.{}',
        client_factory=cf_assessment_options)
    with self.command_group('migrate assessment-options', migrate_assessment_options, client_factory=cf_assessment_options) as g:
        g.custom_show_command('show', 'migrate_assessment_options_show')

    from ._client_factory import cf_projects
    migrate_projects = CliCommandType(
        operations_tmpl='azext_migrate.vendored_sdks.migrate.operations._projects_operations#ProjectsOperations.{}',
        client_factory=cf_projects)
    with self.command_group('migrate projects', migrate_projects, client_factory=cf_projects) as g:
        g.custom_command('list', 'migrate_projects_list')
        g.custom_show_command('show', 'migrate_projects_show')
        g.custom_command('create', 'migrate_projects_create')
        g.custom_command('update', 'migrate_projects_update')
        g.custom_command('delete', 'migrate_projects_delete')
        g.custom_command('get-keys', 'migrate_projects_get_keys')

    from ._client_factory import cf_machines
    migrate_machines = CliCommandType(
        operations_tmpl='azext_migrate.vendored_sdks.migrate.operations._machines_operations#MachinesOperations.{}',
        client_factory=cf_machines)
    with self.command_group('migrate machines', migrate_machines, client_factory=cf_machines) as g:
        g.custom_command('list', 'migrate_machines_list')
        g.custom_show_command('show', 'migrate_machines_show')

    from ._client_factory import cf_groups
    migrate_groups = CliCommandType(
        operations_tmpl='azext_migrate.vendored_sdks.migrate.operations._groups_operations#GroupsOperations.{}',
        client_factory=cf_groups)
    with self.command_group('migrate groups', migrate_groups, client_factory=cf_groups) as g:
        g.custom_command('list', 'migrate_groups_list')
        g.custom_show_command('show', 'migrate_groups_show')
        g.custom_command('create', 'migrate_groups_create')
        g.custom_command('delete', 'migrate_groups_delete')

    from ._client_factory import cf_assessments
    migrate_assessments = CliCommandType(
        operations_tmpl='azext_migrate.vendored_sdks.migrate.operations._assessments_operations#AssessmentsOperations.{}',
        client_factory=cf_assessments)
    with self.command_group('migrate assessments', migrate_assessments, client_factory=cf_assessments) as g:
        g.custom_command('list', 'migrate_assessments_list')
        g.custom_show_command('show', 'migrate_assessments_show')
        g.custom_command('create', 'migrate_assessments_create')
        g.custom_command('delete', 'migrate_assessments_delete')
        g.custom_command('get-report-download-url', 'migrate_assessments_get_report_download_url')

    from ._client_factory import cf_assessed_machines
    migrate_assessed_machines = CliCommandType(
        operations_tmpl='azext_migrate.vendored_sdks.migrate.operations._assessed_machines_operations#AssessedMachinesOperations.{}',
        client_factory=cf_assessed_machines)
    with self.command_group('migrate assessed-machines', migrate_assessed_machines, client_factory=cf_assessed_machines) as g:
        g.custom_command('list', 'migrate_assessed_machines_list')
        g.custom_show_command('show', 'migrate_assessed_machines_show')

    from ._client_factory import cf_operations
    migrate_operations = CliCommandType(
        operations_tmpl='azext_migrate.vendored_sdks.migrate.operations._operations_operations#OperationsOperations.{}',
        client_factory=cf_operations)
    with self.command_group('migrate operations', migrate_operations, client_factory=cf_operations) as g:
        g.custom_command('list', 'migrate_operations_list')
