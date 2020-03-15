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


def load_arguments(self, _):

    with self.argument_context('custom-providers custom-resource-provider create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the resource provider.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('actions', id_part=None, help='A list of actions that the custom resource provider implements.', nargs='+')
        c.argument('resource_types', id_part=None, help='A list of resource types that the custom resource provider implements.', nargs='+')
        c.argument('validations', id_part=None, help='A list of validations to run on the custom resource provider\'s requests.', nargs='+')

    with self.argument_context('custom-providers custom-resource-provider update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the resource provider.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('actions', id_part=None, help='A list of actions that the custom resource provider implements.', nargs='+')
        c.argument('resource_types', id_part=None, help='A list of resource types that the custom resource provider implements.', nargs='+')
        c.argument('validations', id_part=None, help='A list of validations to run on the custom resource provider\'s requests.', nargs='+')

    with self.argument_context('custom-providers custom-resource-provider delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the resource provider.')

    with self.argument_context('custom-providers custom-resource-provider show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the resource provider.')

    with self.argument_context('custom-providers custom-resource-provider list') as c:
        c.argument('resource_group', resource_group_name_type)
