# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    resource_group_name_type,
    get_location_type
)
from azext_migrate.actions import (
    AddProject,
    AddMachines,
    AddAssessment
)


def load_arguments(self, _):

    with self.argument_context('migrate location check-name-availability') as c:
        c.argument('location_name', id_part=None, help='The desired region for the name check.')
        c.argument('name', id_part=None, help='The name to check for availability')
        c.argument('_type', options_list=['--type'], id_part=None, help='The resource type. Must be set to Microsoft.Migrate/projects')

    with self.argument_context('migrate assessment-options show') as c:
        c.argument('location_name', id_part=None, help='Azure region in which the project is created.')

    with self.argument_context('migrate projects list') as c:
        c.argument('resource_group_name', resource_group_name_type)

    with self.argument_context('migrate projects show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')

    with self.argument_context('migrate projects create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('project', id_part=None, help='New or Updated project object.', action=AddProject, nargs='+')

    with self.argument_context('migrate projects update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('project', id_part=None, help='New or Updated project object.', action=AddProject, nargs='+')

    with self.argument_context('migrate projects delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')

    with self.argument_context('migrate projects get-keys') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')

    with self.argument_context('migrate machines list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')

    with self.argument_context('migrate machines show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('machine_name', id_part=None, help='Unique name of a machine in private datacenter.')

    with self.argument_context('migrate groups list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')

    with self.argument_context('migrate groups show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('group_name', id_part=None, help='Unique name of a group within a project.')

    with self.argument_context('migrate groups create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('group_name', id_part=None, help='Unique name of a group within a project.')
        c.argument('e_tag', id_part=None, help='For optimistic concurrency control.')
        c.argument('machines', id_part=None, help='List of machine names that are part of this group.', action=AddMachines, nargs='+')

    with self.argument_context('migrate groups delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('group_name', id_part=None, help='Unique name of a group within a project.')

    with self.argument_context('migrate assessments list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('group_name', id_part=None, help='Unique name of a group within a project.')

    with self.argument_context('migrate assessments show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('group_name', id_part=None, help='Unique name of a group within a project.')
        c.argument('assessment_name', id_part=None, help='Unique name of an assessment within a project.')

    with self.argument_context('migrate assessments create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('group_name', id_part=None, help='Unique name of a group within a project.')
        c.argument('assessment_name', id_part=None, help='Unique name of an assessment within a project.')
        c.argument('assessment', id_part=None, help='New or Updated Assessment object.', action=AddAssessment, nargs='+')

    with self.argument_context('migrate assessments delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('group_name', id_part=None, help='Unique name of a group within a project.')
        c.argument('assessment_name', id_part=None, help='Unique name of an assessment within a project.')

    with self.argument_context('migrate assessments get-report-download-url') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('group_name', id_part=None, help='Unique name of a group within a project.')
        c.argument('assessment_name', id_part=None, help='Unique name of an assessment within a project.')

    with self.argument_context('migrate assessed-machines list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('group_name', id_part=None, help='Unique name of a group within a project.')
        c.argument('assessment_name', id_part=None, help='Unique name of an assessment within a project.')

    with self.argument_context('migrate assessed-machines show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', id_part=None, help='Name of the Azure Migrate project.')
        c.argument('group_name', id_part=None, help='Unique name of a group within a project.')
        c.argument('assessment_name', id_part=None, help='Unique name of an assessment within a project.')
        c.argument('assessed_machine_name', id_part=None, help='Unique name of an assessed machine evaluated as part of an assessment.')

    with self.argument_context('migrate operations list') as c:
        pass
