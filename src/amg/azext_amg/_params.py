# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long


def load_arguments(self, _):

    from knack.arguments import CLIArgumentType
    from azure.cli.core.commands.parameters import tags_type, get_three_state_flag, get_enum_type
    from azure.cli.core.commands.validators import get_default_location_from_resource_group
    from ._validators import process_missing_resource_group_parameter
    from azext_amg.vendored_sdks.models import ZoneRedundancy
    grafana_name_type = CLIArgumentType(options_list="--grafana-name",
                                        help="Name of the Azure Managed Dashboard for Grafana.",
                                        id_part="name")

    with self.argument_context("grafana") as c:
        c.argument("tags", tags_type)
        c.argument("location", validator=get_default_location_from_resource_group)
        c.argument("grafana_name", grafana_name_type, options_list=["--name", "-n"], id_part=None, validator=process_missing_resource_group_parameter)
        c.argument("id", help=("The identifier (id) of a dashboard/data source is an auto-incrementing "
                               "numeric value and is only unique per Grafana install."))
        c.argument("folder", help="id, uid, title which can identify a folder. CLI will search in the order of id, uid, and title, till finds a match")

    with self.argument_context("grafana create") as c:
        c.argument("grafana_name", grafana_name_type, options_list=["--name", "-n"], validator=None)
        c.argument("zone_redundancy", arg_type=get_enum_type(ZoneRedundancy), help="Indicates whether or not zone redundancy should be enabled. Default: Disabled")
        c.argument("skip_system_assigned_identity", options_list=["-s", "--skip-system-assigned-identity"], arg_type=get_three_state_flag(), help="Do not enable system assigned identity")
        c.argument("skip_role_assignments", arg_type=get_three_state_flag(), help="Do not create role assignments for managed identity and the current login user")
        c.argument("principal_ids", nargs="+", help="space-separated Azure AD object ids for users, groups, etc to be made as Grafana Admins. Once provided, CLI won't make the current logon user as Grafana Admin")

    with self.argument_context("grafana dashboard") as c:
        c.argument("uid", options_list=["--dashboard"], help="dashboard uid")
        c.argument("definition", help="The complete dashboard model in json string, a path or url to a file with such content")
        c.argument("title", help="title of a dashboard")
        c.argument('overwrite', arg_type=get_three_state_flag(), help='Overwrite a dashboard with same uid')

    with self.argument_context("grafana dashboard import") as c:
        c.argument("definition", help="The complete dashboard model in json string, Grafana gallery id, a path or url to a file with such content")

    with self.argument_context("grafana data-source") as c:
        c.argument("data_source", help="name, id, uid which can identify a data source. CLI will search in the order of name, id, and uid, till finds a match")
        c.argument("definition", help="json string with data source definition, or a path to a file with such content")

    with self.argument_context("grafana data-source query") as c:
        c.argument("conditions", nargs="+", help="space-separated condition in a format of `<name>=<value>`")
        c.argument("time_from", options_list=["--from"], help="start time in iso 8601, e.g. '2022-01-02T16:15:00'. Default: 1 hour early")
        c.argument("time_to", options_list=["--to"], help="end time in iso 8601, e.g. '2022-01-02T17:15:00'. Default: current time ")
        c.argument("max_data_points", help="Maximum amount of data points that dashboard panel can render")
        c.argument("query_format", help="format of the resule, e.g. table, time_series")
        c.argument("internal_ms", help="The time interval in milliseconds of time series")

    with self.argument_context("grafana folder") as c:
        c.argument("title", help="title of the folder")

    with self.argument_context("grafana user") as c:
        c.argument("user", help="user login name or email")
