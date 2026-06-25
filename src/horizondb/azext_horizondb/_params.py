# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-statements

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    resource_group_name_type,
    get_location_type,
    tags_type,
    get_enum_type)
from azure.cli.core.local_context import LocalContextAttribute, LocalContextAction
from .utils.validators import (
    validate_replica_count)


def load_arguments(self, _):    # pylint: disable=too-many-statements, too-many-locals

    # HorizonDB
    # pylint: disable=too-many-locals, too-many-branches
    def _horizondb_params():

        yes_arg_type = CLIArgumentType(
            options_list=['--yes', '-y'],
            action='store_true',
            help='Do not prompt for confirmation.'
        )

        cluster_name_arg_type = CLIArgumentType(
            metavar='NAME',
            options_list=['--name', '-n'],
            id_part='name',
            help="Name of the cluster. The name can contain only lowercase letters, numbers, and the hyphen (-) character. Minimum 3 characters and maximum 63 characters.",
            local_context_attribute=LocalContextAttribute(
                name='cluster_name',
                actions=[LocalContextAction.SET, LocalContextAction.GET],
                scopes=['horizondb']))

        administrator_login_arg_type = CLIArgumentType(
            options_list=['--administrator-login', '-u'],
            help='The administrator login name for the cluster.',
            required=True)

        administrator_login_password_arg_type = CLIArgumentType(
            options_list=['--administrator-login-password', '-p'],
            help='The administrator login password.')

        version_arg_type = CLIArgumentType(
            options_list=['--version', '-v'],
            help='The version of the HorizonDb cluster.')

        replica_count_arg_type = CLIArgumentType(
            options_list=['--replica-count', '-r'],
            type=int,
            validator=validate_replica_count,
            help='Number of replicas. Must be between 1 and 16, inclusive.')

        v_cores_arg_type = CLIArgumentType(
            options_list=['--v-cores'],
            type=int,
            help='Number of vCores.')

        zone_placement_policy_arg_type = CLIArgumentType(
            options_list=['--zone-placement-policy', '-z'],
            arg_type=get_enum_type(['Strict', 'BestEffort']),
            help='Defines how replicas are placed across availability zones.')

        parameter_group_arg_type = CLIArgumentType(
            options_list=['--parameter-group'],
            help='The resource ID of the parameter group.')
        cluster_name_resource_arg_type = CLIArgumentType(
            metavar='NAME',
            options_list=['--cluster-name', '-c'],
            id_part=None,
            help="Name of the cluster. The name can contain only lowercase letters, numbers, and the hyphen (-) character. Minimum 3 characters and maximum 63 characters.",
            local_context_attribute=LocalContextAttribute(
                name='cluster_name',
                actions=[LocalContextAction.SET, LocalContextAction.GET],
                scopes=['horizondb']))
        private_endpoint_connection_name_arg_type = CLIArgumentType(
            options_list=['--name', '-n'],
            help='The name of the private endpoint connection associated with the HorizonDB cluster. '
                 'Required if --id is not specified.')
        private_endpoint_connection_id_arg_type = CLIArgumentType(
            options_list=['--id'],
            help='The resource ID of the private endpoint connection associated with the HorizonDB cluster. '
                 'If specified --cluster-name/-c and --name/-n, this should be omitted.')
        private_endpoint_connection_description_arg_type = CLIArgumentType(
            options_list=['--description', '-d'],
            help='Comments for the approval or rejection.')
        private_link_resource_group_name_arg_type = CLIArgumentType(
            options_list=['--group-name'],
            help='The private link resource group name. For HorizonDB this is the pool name, for example DefaultPool.')

        with self.argument_context('horizondb') as c:
            c.argument('resource_group_name', arg_type=resource_group_name_type)
            c.argument('cluster_name', arg_type=cluster_name_arg_type)

        with self.argument_context('horizondb create') as c:
            c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False)
            c.argument('tags', tags_type)
            c.argument('administrator_login', arg_type=administrator_login_arg_type)
            c.argument('administrator_login_password', arg_type=administrator_login_password_arg_type, required=True)
            c.argument('version', arg_type=version_arg_type)
            c.argument('replica_count', arg_type=replica_count_arg_type)
            c.argument('v_cores', arg_type=v_cores_arg_type)
            c.argument('zone_placement_policy', arg_type=zone_placement_policy_arg_type)

        with self.argument_context('horizondb update') as c:
            c.argument('tags', tags_type)
            c.argument('administrator_login_password', arg_type=administrator_login_password_arg_type)
            c.argument('v_cores', arg_type=v_cores_arg_type)
            c.argument('parameter_group', arg_type=parameter_group_arg_type)

        with self.argument_context('horizondb delete') as c:
            c.argument('yes', arg_type=yes_arg_type)

        for scope in ['show', 'delete', 'approve', 'reject']:
            with self.argument_context('horizondb private-endpoint-connection {}'.format(scope)) as c:
                c.argument('resource_group_name', arg_type=resource_group_name_type, required=False)
                c.argument('cluster_name', arg_type=cluster_name_resource_arg_type, required=False)
                c.argument('private_endpoint_connection_name',
                           arg_type=private_endpoint_connection_name_arg_type,
                           required=False)
                c.extra('connection_id',
                        arg_type=private_endpoint_connection_id_arg_type,
                        required=False)
                if scope in ['approve', 'reject']:
                    c.argument('description',
                               arg_type=private_endpoint_connection_description_arg_type,
                               required=True)

        with self.argument_context('horizondb private-endpoint-connection list') as c:
            c.argument('cluster_name', arg_type=cluster_name_resource_arg_type)

        with self.argument_context('horizondb private-link-resource list') as c:
            c.argument('cluster_name', arg_type=cluster_name_resource_arg_type)

        with self.argument_context('horizondb private-link-resource show') as c:
            c.argument('cluster_name', arg_type=cluster_name_resource_arg_type)
            c.argument('group_name', arg_type=private_link_resource_group_name_arg_type, required=True)

    _horizondb_params()
