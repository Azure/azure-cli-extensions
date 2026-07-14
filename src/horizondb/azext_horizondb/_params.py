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
    validate_replica_count,
    public_access_validator,
    ip_address_validator)


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

        source_cluster_arg_type = CLIArgumentType(
            options_list=['--source-cluster'],
            help='Name or resource identifier of the source Azure HorizonDB cluster to restore from.')

        restore_time_arg_type = CLIArgumentType(
            options_list=['--restore-time'],
            help='The point in time in UTC to restore from (ISO8601 format), e.g., 2026-07-15T02:10:00+00:00. '
                 'During preview, you must set restore time to be at least 5 minutes before the current time. '
                 "If --restore-time isn't specified, during preview, it will internally be adjusted to 6 minutes "
                 'before now.')

        parameter_group_arg_type = CLIArgumentType(
            options_list=['--parameter-group'],
            help='The resource ID of the parameter group.')

        public_access_create_arg_type = CLIArgumentType(
            options_list=['--public-access'],
            validator=public_access_validator,
            help="Determines the public access for the cluster by creating a firewall rule on the "
                 "default pool. Enter a single IP address or a range of IP addresses (dash-separated, "
                 "no spaces) to be included in the allowed list of IPs. Specifying 'All' allows public "
                 "access from any IP (0.0.0.0-255.255.255.255). 'Enabled' detects your current client "
                 "IP and prompts to allow it. 'None' and 'Disabled' do not create a firewall rule. "
                 "Acceptable values: 'Enabled', 'Disabled', 'All', 'None', '{startIP}' and "
                 "'{startIP}-{endIP}' where each IP ranges from 0.0.0.0 to 255.255.255.255.")

        public_access_update_arg_type = CLIArgumentType(
            options_list=['--public-access'],
            arg_type=get_enum_type(['Enabled', 'Disabled']),
            help="Enable or disable public access on the cluster. 'Enabled' detects your current "
                 "client IP and prompts to create a firewall rule on the default pool. 'Disabled' "
                 "points you to the 'az horizondb firewall-rule' commands to remove public access.")

        firewall_cluster_name_arg_type = CLIArgumentType(
            options_list=['--cluster-name', '-c'],
            id_part=None,
            help='Name of the HorizonDB cluster.')

        firewall_rule_name_arg_type = CLIArgumentType(
            options_list=['--name', '-n'],
            id_part=None,
            help='The name of the firewall rule.')

        start_ip_address_arg_type = CLIArgumentType(
            options_list=['--start-ip-address'],
            help='The start IP address of the firewall rule (IPv4). Must be dotted-quad format. Use '
                 '0.0.0.0 to represent all Azure-internal IP addresses.')

        end_ip_address_arg_type = CLIArgumentType(
            options_list=['--end-ip-address'],
            help='The end IP address of the firewall rule (IPv4). Must be dotted-quad format. Use '
                 '0.0.0.0 to represent all Azure-internal IP addresses.')

        firewall_rule_description_arg_type = CLIArgumentType(
            options_list=['--description'],
            help='The description of the firewall rule.')

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
            c.argument('public_access', arg_type=public_access_create_arg_type)
            c.argument('yes', arg_type=yes_arg_type)

        with self.argument_context('horizondb restore') as c:
            c.argument('tags', tags_type)
            c.argument('source_cluster', arg_type=source_cluster_arg_type)
            c.argument('restore_time', arg_type=restore_time_arg_type)

        with self.argument_context('horizondb update') as c:
            c.argument('tags', tags_type)
            c.argument('administrator_login_password', arg_type=administrator_login_password_arg_type)
            c.argument('v_cores', arg_type=v_cores_arg_type)
            c.argument('parameter_group', arg_type=parameter_group_arg_type)
            c.argument('public_access', arg_type=public_access_update_arg_type)
            c.argument('yes', arg_type=yes_arg_type)

        with self.argument_context('horizondb delete') as c:
            c.argument('yes', arg_type=yes_arg_type)

        with self.argument_context('horizondb firewall-rule') as c:
            c.argument('resource_group_name', arg_type=resource_group_name_type)
            c.argument('cluster_name', arg_type=firewall_cluster_name_arg_type)
            c.argument('firewall_rule_name', arg_type=firewall_rule_name_arg_type)

        with self.argument_context('horizondb firewall-rule create') as c:
            c.argument('start_ip_address', arg_type=start_ip_address_arg_type, validator=ip_address_validator)
            c.argument('end_ip_address', arg_type=end_ip_address_arg_type)
            c.argument('description', arg_type=firewall_rule_description_arg_type)

        with self.argument_context('horizondb firewall-rule update') as c:
            c.argument('start_ip_address', arg_type=start_ip_address_arg_type, validator=ip_address_validator)
            c.argument('end_ip_address', arg_type=end_ip_address_arg_type)
            c.argument('description', arg_type=firewall_rule_description_arg_type)

        with self.argument_context('horizondb firewall-rule delete') as c:
            c.argument('yes', arg_type=yes_arg_type)

    _horizondb_params()
