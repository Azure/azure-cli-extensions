# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json

from msrestazure.tools import is_valid_resource_id, parse_resource_id
from knack.log import get_logger
from azure.cli.core.azclierror import ArgumentUsageError
from azure.cli.core.style import print_styled_text, Style

from .custom import list_folders, create_folder
from .custom import list_data_sources
from .custom import list_dashboards, show_dashboard, delete_dashboard
from .custom import _health_endpoint_reachable, _create_dashboard, _get_grafana_endpoint, _get_data_plane_creds
from .utils import send_grafana_get, send_grafana_post, send_grafana_patch

logger = get_logger(__name__)


def sync(cmd, source, destination, folders_to_include=None, folders_to_exclude=None,
         dashboards_to_include=None, dashboards_to_exclude=None, dry_run=None):
    # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    if not is_valid_resource_id(source):
        raise ArgumentUsageError(f"'{source}' isn't a valid resource id, please refer to example commands in help")
    if not is_valid_resource_id(destination):
        raise ArgumentUsageError(f"'{destination}' isn't a valid resource id, please refer to example commands in help")

    if source.lower() == destination.lower():
        raise ArgumentUsageError("Destination workspace should be different from the source workspace")

    parsed_source = parse_resource_id(source)
    parsed_destination = parse_resource_id(destination)

    source_workspace, source_resource_group, source_subscription = (parsed_source["name"],
                                                                    parsed_source["resource_group"],
                                                                    parsed_source["subscription"])
    destination_workspace, destination_resource_group, destination_subscription = (parsed_destination["name"],
                                                                                   parsed_destination["resource_group"],
                                                                                   parsed_destination["subscription"])

    _health_endpoint_reachable(cmd, source_workspace, resource_group_name=source_resource_group,
                               subscription=source_subscription)
    _health_endpoint_reachable(cmd, destination_workspace, resource_group_name=destination_resource_group,
                               subscription=destination_subscription)
    creds = _get_data_plane_creds(cmd, api_key_or_token=None, subscription=None)
    http_headers = {
        "content-type": "application/json",
        "authorization": "Bearer " + creds[1]
    }

    # TODO: skip READ-ONLY destination dashboard (rare case)
    destination_folders = list_folders(cmd, destination_workspace, resource_group_name=destination_resource_group,
                                       subscription=destination_subscription)
    destination_folders = {f["title"].lower(): f["id"] for f in destination_folders}

    destination_data_sources = list_data_sources(cmd, destination_workspace, destination_resource_group,
                                                 subscription=destination_subscription)
    source_data_sources = list_data_sources(cmd, source_workspace, source_resource_group,
                                            subscription=source_subscription)

    from .utils import create_datasource_mapping, remap_datasource_uids
    uid_mapping = create_datasource_mapping(source_data_sources, destination_data_sources)

    source_dashboards = list_dashboards(cmd, source_workspace, resource_group_name=source_resource_group,
                                        subscription=source_subscription)

    folders_created_summary = []
    library_panels_synced_summary = {}
    dashboards_synced_summary = {}
    dashboards_skipped_summary = {}
    data_source_missed = set()

    for dashboard in source_dashboards:
        uid = dashboard["uid"]
        source_dashboard = show_dashboard(cmd, source_workspace, uid, resource_group_name=source_resource_group,
                                          subscription=source_subscription)
        folder_title = source_dashboard["meta"]["folderTitle"]
        dashboard_title = source_dashboard["dashboard"]["title"]

        should_skip = False
        if source_dashboard["meta"].get("provisioned"):
            should_skip = True
        else:
            if folders_to_include:
                should_skip = not next((f for f in folders_to_include if folder_title.lower() == f.lower()), None)
            if not should_skip and folders_to_exclude:
                should_skip = next((f for f in folders_to_exclude if folder_title.lower() == f.lower()), None)
            if dashboards_to_include:
                should_skip = not next((p for p in dashboards_to_include if p.lower() == dashboard_title.lower()), None)
            if dashboards_to_exclude:
                should_skip = next((p for p in dashboards_to_exclude if p.lower() == dashboard_title.lower()), None)
        if should_skip:
            if folder_title not in dashboards_skipped_summary:
                dashboards_skipped_summary[folder_title] = []
            dashboards_skipped_summary[folder_title].append(dashboard_title)
            continue

        # Figure out whether we shall correct the data sources. It is possible the Uids are different
        remap_datasource_uids(source_dashboard.get("dashboard"), uid_mapping, data_source_missed)

        if not dry_run:
            delete_dashboard(cmd, destination_workspace, uid, resource_group_name=destination_resource_group,
                             ignore_error=True, subscription=destination_subscription)

        # ensure the folder exists at destination side
        if folder_title.lower() == "general":
            folder_id = None
        else:
            folder_id = destination_folders.get(folder_title.lower())
            if not folder_id:
                folders_created_summary.append(folder_title)
                if not dry_run:
                    logger.warning("Creating folder: %s", folder_title)
                    new_folder = create_folder(cmd, destination_workspace, title=folder_title,
                                               resource_group_name=destination_resource_group,
                                               subscription=destination_subscription)
                    folder_id = new_folder["id"]
                destination_folders[folder_title.lower()] = folder_id or "dry run dummy"

        if folder_title not in dashboards_synced_summary:
            dashboards_synced_summary[folder_title] = []
        dashboards_synced_summary[folder_title].append(dashboard_title)
            
        # sync library panels
        library_panel_uids = set([panel["libraryPanel"]["uid"] for panel in source_dashboard["dashboard"]["panels"] if "libraryPanel" in panel])
        source_endpoint = _get_grafana_endpoint(cmd, source_resource_group, source_workspace, source_subscription)
        destination_endpoint = _get_grafana_endpoint(cmd, destination_resource_group, destination_workspace, destination_subscription)
        for library_panel_uid in library_panel_uids:
            (status, content) = send_grafana_get(f'{source_endpoint}/api/library-elements/{library_panel_uid}', http_headers)
            # TODO: error handling
            if status == 200:
                library_panel_name = content["result"]['name']
                library_panel_folder_name = content["result"]["meta"]["folderName"]

                if not dry_run:
                    logger.warning("Syncing library panel: %s", library_panel_folder_name + "/" + library_panel_name)
                    payload = {
                        'uid': content["result"]["uid"],
                        'folderUid': content["result"]["folderUid"],
                        'name': library_panel_name,
                        'model': content["result"]["model"],
                        'kind': content["result"]["kind"],
                    }
                    (status, content) = send_grafana_post(f'{destination_endpoint}/api/library-elements/', json.dumps(payload), http_headers)
                    if status >= 400 and ('name or UID already exists' in content.get('message', '')):
                        send_grafana_patch(f'{destination_endpoint}/api/library-elements/{library_panel_uid}', json.dumps(payload), http_headers)

                if library_panel_folder_name not in library_panels_synced_summary:
                    library_panels_synced_summary[library_panel_folder_name] = set()
                library_panels_synced_summary[library_panel_folder_name].add(library_panel_name)

        if not dry_run:
            logger.warning("Syncing dashboard: %s", folder_title + "/" + dashboard_title)
            _create_dashboard(cmd, destination_workspace, definition=source_dashboard, overwrite=True,
                              folder_id=folder_id, resource_group_name=destination_resource_group,
                              for_sync=True)

    if data_source_missed:
        logger.warning(("Some data sources used by dashboards are unavailable at the destination workspace: \"%s\""
                        ". Please manually configure them."), ", ".join(data_source_missed))

    output = [
        (Style.SUCCESS, "\n\nFolders created:"),
        (Style.PRIMARY, "\n    " + "\n    ".join(folders_created_summary)),
    ]

    output.append((Style.SUCCESS, "\n\nLibrary panels synced:"))
    for folder, panels in library_panels_synced_summary.items():
        output.append((Style.PRIMARY, f"\n    {folder}/\n        "))
        output.append((Style.SECONDARY, "\n        ".join(panels)))

    output.append((Style.SUCCESS, "\n\nDashboards synced:"))
    for folder, dashboards in dashboards_synced_summary.items():
        output.append((Style.PRIMARY, f"\n    {folder}/\n        "))
        output.append((Style.SECONDARY, "\n        ".join(dashboards)))

    output.append((Style.WARNING, "\n\nDashboards skipped:"))
    for folder, dashboards in dashboards_skipped_summary.items():
        output.append((Style.PRIMARY, f"\n    {folder}/\n        "))
        output.append((Style.SECONDARY, "\n        ".join(dashboards)))

    output.append((Style.IMPORTANT, f"\n\nDry run: {dry_run}\n"))

    print_styled_text(output)
