# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

def load_arguments(self, _):

    from knack.arguments import CLIArgumentType
    from azure.cli.core.commands.parameters import tags_type, get_three_state_flag, resource_group_name_type
    from azure.cli.core.commands.validators import get_default_location_from_resource_group
    from ._validators import process_missing_resource_group_parameter, process_leading_hyphen

    grafana_name_type = CLIArgumentType(options_list="--grafana-name",
                                        help="Name of the Azure Managed Dashboard for Grafana.",
                                        id_part="name")

    with self.argument_context("grafana") as c:
        c.argument("tags", tags_type)
        c.argument("location", validator=get_default_location_from_resource_group)
        c.argument("grafana_name", grafana_name_type, options_list=["--name", "-n"], validator=process_missing_resource_group_parameter)
        c.argument("uid", options_list=["--unique-identifier", "--uid"],
                   help=("The unique identifier (uid) of a dashboard can be used for uniquely identifying a dashboard or data source "
                         "between multiple Grafana installs. It’s automatically generated if not provided on creating. "
                         "The uid allows having consistent URLs for accessing dashboards or data sources when syncing "
                         "between multiple Grafana installs. For uid with leading hyphen, please prepend whitespace to workaround https://bugs.python.org/issue9334"),
                   validator=process_leading_hyphen)
        c.argument("id", help=("The identifier (id) of a dashboard/data source is an auto-incrementing "
                               "numeric value and is only unique per Grafana install."))

    with self.argument_context("grafana create") as c:
        c.argument("enable_system_assigned_identity", arg_type=get_three_state_flag())
        c.argument("grafana_name", grafana_name_type, options_list=["--name", "-n"], validator=None)

    with self.argument_context("grafana delete") as c:
        c.argument('yes', options_list=['--yes', '-y'], help='Do not prompt for confirmation.', action='store_true')

    with self.argument_context("grafana dashboard") as c:
        c.argument("dashboard_definition", help="The complete dashboard model in json string, or a path to a file with such json string")

    with self.argument_context("grafana dashboard show") as c:
        c.argument("show_home_dashboard", arg_type=get_three_state_flag())

    with self.argument_context("grafana data-source") as c:
        c.argument("data_source", help="id, name, uid which can identify a data source")
        c.argument("definition", help="json string with data source definition, or a path to a file with such content")

    with self.argument_context("grafana data-source query") as c:
        c.argument("conditions", nargs="+", help="space-separated condition in a format of `<name>=<value>`")
        c.argument("time_from", options_list=["--from"], help="start time in iso 8601, e.g. '2022-01-02T16:15:00'. Default: 1 hour early")
        c.argument("time_to", options_list=["--to"], help="end time in iso 8601, e.g. '2022-01-02T17:15:00'. Default: current time ")
        c.argument("max_data_points", help="Maximum amount of data points that dashboard panel can render")
        c.argument("internal_ms", help="The time interval in milliseconds of time series")

    with self.argument_context("grafana folder") as c:
        c.argument("title", help="title of the folder")
        c.argument("folder", help="id, uid which can identify a folder")

    with self.argument_context("grafana user") as c:
        c.argument("user", help="user login name or email")
