# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, too-many-statements


def load_arguments(self, _):

    from knack.arguments import CLIArgumentType
    from azure.cli.core.commands.parameters import tags_type, get_three_state_flag, get_enum_type
    from azure.cli.core.commands.validators import get_default_location_from_resource_group, validate_file_or_dict
    from ._validators import process_missing_resource_group_parameter
    grafana_name_type = CLIArgumentType(options_list="--grafana-name",
                                        help="Name of the Azure Managed Grafana.",
                                        id_part="name")
    grafana_role_type = CLIArgumentType(arg_type=get_enum_type(["Admin", "Editor", "Viewer"]), options_list=["--role", "-r"],
                                        help="Grafana role name")

    with self.argument_context("grafana") as c:
        c.argument("tags", tags_type)
        c.argument("location", validator=get_default_location_from_resource_group)
        c.argument("grafana_name", grafana_name_type, options_list=["--name", "-n"], id_part=None, validator=process_missing_resource_group_parameter)
        c.argument("id", help=("The identifier (id) of a dashboard/data source is an auto-incrementing "
                               "numeric value and is only unique per Grafana install."))
        c.argument("folder", help="uid or title which can identify a folder. CLI will search with uid first, then title, till it finds a match")
        c.argument("api_key_or_token", options_list=["--api-key", "--token", '-t'],
                   help="api key or service account token, a randomly generated string used to interact with Grafana endpoint; if missing, CLI will use current logged-in user's credentials")
        c.argument("components", get_enum_type(["dashboards", "datasources", "folders", "snapshots", "annotations"]), nargs='+', options_list=["-c", "--components"], help="grafana artifact types to backup")
        c.argument("folders_to_include", nargs='+', options_list=["-i", "--folders-to-include"], help="folders to include in backup or sync")
        c.argument("folders_to_exclude", nargs='+', options_list=["-e", "--folders-to-exclude"], help="folders to exclude in backup or sync")
        c.argument("time_to_live", default="1d", help="The life duration. For example, 1d if your key is going to last fr one day. Supported units are: s,m,h,d,w,M,y")
        c.ignore("subscription")  # a help argument

    with self.argument_context("grafana backup") as c:
        c.argument("directory", options_list=["-d", "--directory"], help="directory to backup Grafana artifacts")
        c.argument("skip_folder_permissions", options_list=["-s", "--skip-folder-permissions"], arg_type=get_three_state_flag(), help="skip backing up Grafana folder permissions. Default: false")

    with self.argument_context("grafana restore") as c:
        c.argument("archive_file", options_list=["-a", "--archive-file"], help="archive to restore Grafana artifacts from")
        c.argument("remap_data_sources", options_list=["-r", "--remap-data-sources"], arg_type=get_three_state_flag(),
                   help="during restoration, update dashboards to reference data sources defined at the destination workspace through name matching")

    with self.argument_context("grafana migrate") as c:
        c.argument("source_grafana_endpoint", options_list=["-s", "--src-endpoint"], help="Grafana instance endpoint to migrate from")
        c.argument("source_grafana_token_or_api_key", options_list=["-t", "--src-token-or-key"], help="Grafana instance service token (or api key) to get access to migrate from")
        c.argument("dry_run", options_list=["-d", "--dry-run"], arg_type=get_three_state_flag(), help="Preview changes without committing. Takes priority over --overwrite.")
        c.argument("overwrite", options_list=["--overwrite"], arg_type=get_three_state_flag(), help="Overwrite previous dashboards, library panels, and folders with the same uid or title")

    with self.argument_context("grafana dashboard") as c:
        c.argument("uid", options_list=["--dashboard"], help="dashboard uid")
        c.argument("title", help="title of a dashboard")
        c.argument('overwrite', arg_type=get_three_state_flag(), help='Overwrite a dashboard with same uid')

    with self.argument_context("grafana dashboard create") as c:
        c.argument("definition", type=validate_file_or_dict, help="The complete dashboard model in json string, a path or url to a file with such content")

    with self.argument_context("grafana dashboard update") as c:
        c.argument("definition", type=validate_file_or_dict, help="The complete dashboard model in json string, a path or url to a file with such content")

    with self.argument_context("grafana dashboard import") as c:
        c.argument("definition", help="The complete dashboard model in json string, Grafana gallery id, a path or url to a file with such content")

    with self.argument_context("grafana dashboard delete") as c:
        c.ignore("ignore_error")

    with self.argument_context("grafana dashboard sync") as c:
        c.argument("source", options_list=["--source", "-s"], help="resource id of the source workspace")
        c.argument("destination", options_list=["--destination", "-d"], help="resource id of the destination workspace")
        c.argument("dry_run", arg_type=get_three_state_flag(), help="preview changes w/o committing")
        c.argument("folders", nargs="+", help="space separated folder list which sync command shall handle dashboards underneath")
        c.argument("dashboards_to_include", nargs='+', help="Space separated titles of dashboards to include in sync. Pair with --folders-to-include for folders specific")
        c.argument("dashboards_to_exclude", nargs='+', help="Space separated titles of dashboards to exclude in sync. Pair with --folders-to-exclude for folders specific")

    with self.argument_context("grafana api-key") as c:
        c.argument("key_name", help="api key name")
        c.argument("role", grafana_role_type, default="Viewer")
        c.argument("time_to_live", default="1d", help="The API key life duration. For example, 1d if your key is going to last fr one day. Supported units are: s,m,h,d,w,M,y")

    with self.argument_context("grafana api-key create") as c:
        c.argument("key", help="api key name")

    with self.argument_context("grafana api-key delete") as c:
        c.argument("key", help="id or name that identify an api-key to delete")

    with self.argument_context("grafana data-source") as c:
        c.argument("data_source", help="name, id, uid which can identify a data source. CLI will search in the order of name, id, and uid, till finds a match")
        c.argument("definition", type=validate_file_or_dict, help="json string with data source definition, or a path to a file with such content")

    with self.argument_context("grafana notification-channel") as c:
        c.argument("notification_channel", help="id, uid which can identify a data source. CLI will search in the order of id, and uid, till finds a match")
        c.argument("definition", type=validate_file_or_dict, help="json string with notification channel definition, or a path to a file with such content")
        c.argument("short", action='store_true', help="list notification channels in short format.")

    with self.argument_context("grafana data-source query") as c:
        c.argument("conditions", nargs="+", help="space-separated condition in a format of `<name>=<value>`")
        c.argument("time_from", options_list=["--from"], help="start time in iso 8601, e.g. '2022-01-02T16:15:00'. Default: 1 hour early")
        c.argument("time_to", options_list=["--to"], help="end time in iso 8601, e.g. '2022-01-02T17:15:00'. Default: current time ")
        c.argument("max_data_points", type=int, help="Maximum amount of data points that dashboard panel can render. Default: 1000")
        c.argument("query_format", help="format of the resule, e.g. table, time_series")
        c.argument("internal_ms", type=int, help="The time interval in milliseconds of time series. Default: 1000")

    with self.argument_context("grafana folder") as c:
        c.argument("title", help="title of the folder")

    with self.argument_context("grafana user") as c:
        c.argument("user", help="user login name or email")

    with self.argument_context("grafana service-account") as c:
        c.argument("service_account", help="id or name which can identify a service account")
        c.argument("is_disabled", arg_type=get_three_state_flag(), help="disable the service account. default: false")

    with self.argument_context("grafana service-account create") as c:
        c.argument("role", grafana_role_type, default="Viewer")
        c.argument("service_account", help="service account name")

    with self.argument_context("grafana service-account update") as c:
        c.argument("role", grafana_role_type)
        c.argument("new_name", help="new name of the service account")

    with self.argument_context("grafana service-account token") as c:
        c.argument("token", help="id or name which can identify a service account token")

    with self.argument_context("grafana service-account token create") as c:
        c.argument("token", help="name of the new service account token")

    with self.argument_context("grafana integrations monitor") as c:
        c.argument("monitor_name", help="name of the Azure Monitor workspace")
        c.argument("monitor_resource_group_name", options_list=["--monitor-resource-group-name", "--monitor-rg-name"], help="name of the resource group of the Azure Monitor workspace")
        c.argument("monitor_subscription_id", options_list=["--monitor-subscription-id", "--monitor-sub-id"], help="subscription id of the Azure Monitor workspace. Uses the current subscription id if not specified")
        c.argument("skip_role_assignments", options_list=["-s", "--skip-role-assignments"], arg_type=get_three_state_flag(), help="skip assigning the appropriate role on the Azure Monitor workspace to let Grafana read data from it. Default: false")
