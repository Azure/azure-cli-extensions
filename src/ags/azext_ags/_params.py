# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType


def load_arguments(self, _):

    from azure.cli.core.commands.parameters import tags_type, get_three_state_flag
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    grafana_name_type = CLIArgumentType(options_list='--grafana-name',
                                        help='Name of the Azure Managed Dashboard for Grafana.',
                                        id_part='name')

    with self.argument_context('grafana') as c:
        c.argument('tags', tags_type)
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('grafana_name', grafana_name_type, options_list=['--name', '-n'])
        c.argument('uid', options_list=['--unique-identifier', '--uid'],
                   help=("The unique identifier (uid) of a dashboard can be used for uniquely identifying a dashboard or data source "
                         "between multiple Grafana installs. It’s automatically generated if not provided on creating. "
                         "The uid allows having consistent URLs for accessing dashboards or data sources when syncing "
                         "between multiple Grafana installs"))
        c.argument('id', help=("The identifier (id) of a dashboard/data source is an auto-incrementing "
                               "numeric value and is only unique per Grafana install."))

    with self.argument_context('grafana create') as c:
        c.argument('enable_system_assigned_identity', arg_type=get_three_state_flag())

    with self.argument_context('grafana dashboard') as c:
        c.argument('dashboard_definition', help="The complete dashboard model in json string, or a path to a file with such json string")

    with self.argument_context('grafana dashboard show') as c:
        c.argument('show_home_dashboard', arg_type=get_three_state_flag())
