# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.parameters import (
    tags_type,
    get_location_type,
    name_type)
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from .actions import (ActionAddAction, ResourceTypeAddAction, ValidationAddAction)


def load_arguments(self, _):
    with self.argument_context('custom-providers resource-provider') as c:
        c.argument('resource_provider_name', arg_type=name_type, help='The name of the resource provider.')
        c.argument('location',
                   arg_type=get_location_type(self.cli_ctx),
                   validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('actions', options_list=['--action', '-a'], action=ActionAddAction, nargs='+')
        c.argument('resource_types', options_list=['--resource-type', '-r'], action=ResourceTypeAddAction, nargs='+')
        c.argument('validations', options_list=['--validation', '-v'], action=ValidationAddAction, nargs='+')
