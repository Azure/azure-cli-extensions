# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)


def load_arguments(self, _):

    with self.argument_context('migrateprojects database-instance show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')
        c.argument('database_instance_name', help='Unique name of a database instance in Azure migration hub.')

    with self.argument_context('migrateprojects database-instance enumerate-database-instance') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')
        c.argument('continuation_token', help='The continuation token.')
        c.argument('page_size', help='The number of items to be returned in a single page. This value is honored only if it is less than the 100.')

    with self.argument_context('migrateprojects database show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')
        c.argument('database_name', help='Unique name of a database in Azure migration hub.')

    with self.argument_context('migrateprojects database enumerate-database') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')
        c.argument('continuation_token', help='The continuation token.')
        c.argument('page_size', help='The number of items to be returned in a single page. This value is honored only if it is less than the 100.')

    with self.argument_context('migrateprojects event show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')
        c.argument('event_name', help='Unique name of an event within a migrate project.')

    with self.argument_context('migrateprojects event delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')
        c.argument('event_name', help='Unique name of an event within a migrate project.')

    with self.argument_context('migrateprojects event enumerate-event') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')
        c.argument('continuation_token', help='The continuation token.')
        c.argument('page_size', help='The number of items to be returned in a single page. This value is honored only if it is less than the 100.')

    with self.argument_context('migrateprojects machine show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')
        c.argument('machine_name', help='Unique name of a machine in Azure migration hub.')

    with self.argument_context('migrateprojects machine enumerate-machine') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')
        c.argument('continuation_token', help='The continuation token.')
        c.argument('page_size', help='The number of items to be returned in a single page. This value is honored only if it is less than the 100.')

    with self.argument_context('migrateprojects migrate-project show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')

    with self.argument_context('migrateprojects migrate-project delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')

    with self.argument_context('migrateprojects migrate-project put-migrate-project') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')
        c.argument('e_tag', help='Gets or sets the eTag for concurrency control.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help='Gets or sets the Azure location in which migrate project is created.')
        c.argument('properties', arg_type=CLIArgumentType(options_list=['--properties'], help='Gets or sets the nested properties.'))
        c.argument('tags', tags_type, help='Gets or sets the tags.')

    with self.argument_context('migrateprojects migrate-project patch-migrate-project') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')
        c.argument('e_tag', help='Gets or sets the eTag for concurrency control.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help='Gets or sets the Azure location in which migrate project is created.')
        c.argument('properties', arg_type=CLIArgumentType(options_list=['--properties'], help='Gets or sets the nested properties.'))
        c.argument('tags', tags_type, help='Gets or sets the tags.')

    with self.argument_context('migrateprojects migrate-project register-tool') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')
        c.argument('tool', arg_type=get_enum_type(['ServerDiscovery', 'ServerAssessment', 'ServerMigration', 'Cloudamize', 'Turbonomic', 'Zerto', 'CorentTech', 'ServerAssessmentV1', 'ServerMigration_Replication', 'Carbonite', 'DataMigrationAssistant', 'DatabaseMigrationService']), help='Gets or sets the tool to be registered.')

    with self.argument_context('migrateprojects migrate-project refresh-migrate-project-summary') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')
        c.argument('goal', arg_type=get_enum_type(['Servers', 'Databases']), help='Gets or sets the goal for which summary needs to be refreshed.')

    with self.argument_context('migrateprojects solution show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')
        c.argument('solution_name', help='Unique name of a migration solution within a migrate project.')

    with self.argument_context('migrateprojects solution delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')
        c.argument('solution_name', help='Unique name of a migration solution within a migrate project.')

    with self.argument_context('migrateprojects solution put-solution') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')
        c.argument('solution_name', help='Unique name of a migration solution within a migrate project.')
        c.argument('etag', help='Gets or sets the ETAG for optimistic concurrency control.')
        c.argument('properties', arg_type=CLIArgumentType(options_list=['--properties'], help='Gets or sets the properties of the solution.'))

    with self.argument_context('migrateprojects solution patch-solution') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')
        c.argument('solution_name', help='Unique name of a migration solution within a migrate project.')
        c.argument('etag', help='Gets or sets the ETAG for optimistic concurrency control.')
        c.argument('properties', arg_type=CLIArgumentType(options_list=['--properties'], help='Gets or sets the properties of the solution.'))

    with self.argument_context('migrateprojects solution get-config') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')
        c.argument('solution_name', help='Unique name of a migration solution within a migrate project.')

    with self.argument_context('migrateprojects solution cleanup-solution-data') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')
        c.argument('solution_name', help='Unique name of a migration solution within a migrate project.')

    with self.argument_context('migrateprojects solution enumerate-solution') as c:
        c.argument('resource_group_name', resource_group_name_type, help='Name of the Azure Resource Group that migrate project is part of.')
        c.argument('migrate_project_name', help='Name of the Azure Migrate project.')
