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
    get_three_state_flag,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group


def load_arguments(self, _):
    name_arg_type = CLIArgumentType(options_list=('--name', '-n'), metavar='NAME')

    with self.argument_context('networkexperiment profiles create') as c:
        c.argument('profile_name', id_part=None, help='The Profile identifier associated with the Tenant and Partner')
        c.argument('name', id_part=None, help='Name of the Resource group within the Azure subscription.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('resource_state', arg_type=get_enum_type(['Creating', 'Enabling', 'Enabled', 'Disabling', 'Disabled', 'Deleting']), id_part=None, help='Resource status.')
        c.argument('enabled_state', arg_type=get_enum_type(['Enabled', 'Disabled']), id_part=None, help='The state of the Experiment')
        c.argument('etag', id_part=None, help='Gets a unique read-only string that changes whenever the resource is updated.')

    with self.argument_context('networkexperiment profiles update') as c:
        c.argument('profile_name', id_part=None, help='The Profile identifier associated with the Tenant and Partner')
        c.argument('name', id_part=None, help='Name of the Resource group within the Azure subscription.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('resource_state', arg_type=get_enum_type(['Creating', 'Enabling', 'Enabled', 'Disabling', 'Disabled', 'Deleting']), id_part=None, help='Resource status.')
        c.argument('enabled_state', arg_type=get_enum_type(['Enabled', 'Disabled']), id_part=None, help='The state of the Experiment')
        c.argument('etag', id_part=None, help='Gets a unique read-only string that changes whenever the resource is updated.')

    with self.argument_context('networkexperiment profiles delete') as c:
        c.argument('name', id_part=None, help='Name of the Resource group within the Azure subscription.')
        c.argument('profile_name', id_part=None, help='The Profile identifier associated with the Tenant and Partner')

    with self.argument_context('networkexperiment profiles list') as c:
        c.argument('name', id_part=None, help='Name of the Resource group within the Azure subscription.')

    with self.argument_context('networkexperiment profiles show') as c:
        c.argument('name', id_part=None, help='Name of the Resource group within the Azure subscription.')
        c.argument('profile_name', id_part=None, help='The Profile identifier associated with the Tenant and Partner')

    with self.argument_context('networkexperiment experiment create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('profile_name', id_part=None, help='The Profile identifier associated with the Tenant and Partner')
        c.argument('name', id_part=None, help='The Experiment identifier associated with the Experiment')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('description', id_part=None, help='The description of the details or intents of the Experiment')
        c.argument('endpoint_a_name', id_part=None, help='The name of the endpoint')
        c.argument('endpoint_a_endpoint', id_part=None, help='The endpoint URL')
        c.argument('endpoint_b_name', id_part=None, help='The name of the endpoint')
        c.argument('endpoint_b_endpoint', id_part=None, help='The endpoint URL')
        c.argument('enabled_state', arg_type=get_enum_type(['Enabled', 'Disabled']), id_part=None, help='The state of the Experiment')
        c.argument('resource_state', arg_type=get_enum_type(['Creating', 'Enabling', 'Enabled', 'Disabling', 'Disabled', 'Deleting']), id_part=None, help='Resource status.')

    with self.argument_context('networkexperiment experiment update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('profile_name', id_part=None, help='The Profile identifier associated with the Tenant and Partner')
        c.argument('name', id_part=None, help='The Experiment identifier associated with the Experiment')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('description', id_part=None, help='The description of the details or intents of the Experiment')
        c.argument('endpoint_a_name', id_part=None, help='The name of the endpoint')
        c.argument('endpoint_a_endpoint', id_part=None, help='The endpoint URL')
        c.argument('endpoint_b_name', id_part=None, help='The name of the endpoint')
        c.argument('endpoint_b_endpoint', id_part=None, help='The endpoint URL')
        c.argument('enabled_state', arg_type=get_enum_type(['Enabled', 'Disabled']), id_part=None, help='The state of the Experiment')
        c.argument('resource_state', arg_type=get_enum_type(['Creating', 'Enabling', 'Enabled', 'Disabling', 'Disabled', 'Deleting']), id_part=None, help='Resource status.')

    with self.argument_context('networkexperiment experiment delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('profile_name', id_part=None, help='The Profile identifier associated with the Tenant and Partner')
        c.argument('name', id_part=None, help='The Experiment identifier associated with the Experiment')

    with self.argument_context('networkexperiment experiment list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('profile_name', id_part=None, help='The Profile identifier associated with the Tenant and Partner')

    with self.argument_context('networkexperiment experiment show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('profile_name', id_part=None, help='The Profile identifier associated with the Tenant and Partner')
        c.argument('name', id_part=None, help='The Experiment identifier associated with the Experiment')
