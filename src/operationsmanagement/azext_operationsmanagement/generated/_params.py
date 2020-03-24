# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    tags_type,
    resource_group_name_type,
    get_location_type
)
from azext_operationsmanagement.action import (
    AddPlan,
    AddProperties
)


def load_arguments(self, _):

    with self.argument_context('operationsmanagement solution list') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The name of the resource group to get. The na'
                   'me is case insensitive.')

    with self.argument_context('operationsmanagement solution show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The name of the resource group to get. The na'
                   'me is case insensitive.')
        c.argument('solution_name', help='User Solution Name.')

    with self.argument_context('operationsmanagement solution create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The name of the resource group to get. The na'
                   'me is case insensitive.')
        c.argument('solution_name', help='User Solution Name.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help='Resource location')
        c.argument('tags', tags_type, help='Resource tags')
        c.argument('plan', action=AddPlan, nargs='+', help='Plan for solution object supported by the OperationsManagem'
                   'ent resource provider.')
        c.argument('properties', action=AddProperties, nargs='+', help='Properties for solution object supported by the'
                   ' OperationsManagement resource provider.')

    with self.argument_context('operationsmanagement solution update') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The name of the resource group to get. The na'
                   'me is case insensitive.')
        c.argument('solution_name', help='User Solution Name.')
        c.argument('tags', tags_type, help='Resource tags')

    with self.argument_context('operationsmanagement solution delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The name of the resource group to get. The na'
                   'me is case insensitive.')
        c.argument('solution_name', help='User Solution Name.')

    with self.argument_context('operationsmanagement management-association list') as c:
        pass

    with self.argument_context('operationsmanagement management-association show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The name of the resource group to get. The na'
                   'me is case insensitive.')
        c.argument('management_association_name', help='User ManagementAssociation Name.')

    with self.argument_context('operationsmanagement management-association create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The name of the resource group to get. The na'
                   'me is case insensitive.')
        c.argument('management_association_name', help='User ManagementAssociation Name.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help='Resource location')
        c.argument('properties', action=AddProperties, nargs='+', help='Properties for ManagementAssociation object sup'
                   'ported by the OperationsManagement resource provider.')

    with self.argument_context('operationsmanagement management-association update') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The name of the resource group to get. The na'
                   'me is case insensitive.')
        c.argument('management_association_name', help='User ManagementAssociation Name.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help='Resource location')
        c.argument('properties', action=AddProperties, nargs='+', help='Properties for ManagementAssociation object sup'
                   'ported by the OperationsManagement resource provider.')

    with self.argument_context('operationsmanagement management-association delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The name of the resource group to get. The na'
                   'me is case insensitive.')
        c.argument('management_association_name', help='User ManagementAssociation Name.')

    with self.argument_context('operationsmanagement management-configuration list') as c:
        pass

    with self.argument_context('operationsmanagement management-configuration show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The name of the resource group to get. The na'
                   'me is case insensitive.')
        c.argument('management_configuration_name', help='User Management Configuration Name.')

    with self.argument_context('operationsmanagement management-configuration create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The name of the resource group to get. The na'
                   'me is case insensitive.')
        c.argument('management_configuration_name', help='User Management Configuration Name.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help='Resource location')
        c.argument('properties', action=AddProperties, nargs='+', help='Properties for ManagementConfiguration object s'
                   'upported by the OperationsManagement resource provider.')

    with self.argument_context('operationsmanagement management-configuration update') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The name of the resource group to get. The na'
                   'me is case insensitive.')
        c.argument('management_configuration_name', help='User Management Configuration Name.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help='Resource location')
        c.argument('properties', action=AddProperties, nargs='+', help='Properties for ManagementConfiguration object s'
                   'upported by the OperationsManagement resource provider.')

    with self.argument_context('operationsmanagement management-configuration delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The name of the resource group to get. The na'
                   'me is case insensitive.')
        c.argument('management_configuration_name', help='User Management Configuration Name.')
