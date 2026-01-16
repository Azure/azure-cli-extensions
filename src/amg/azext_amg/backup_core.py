# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time

from knack.log import get_logger

from .utils import search_dashboard, get_dashboard
from .utils import search_library_panels
from .utils import search_snapshot, get_snapshot
from .utils import search_folders, get_folder, get_folder_permissions
from .utils import search_datasource
from .utils import search_annotations

logger = get_logger(__name__)


def get_all_dashboards(grafana_url, http_headers, **kwargs):
    limit = 5000  # limit is 5000 above V6.2+
    current_page = 1

    all_dashboards = []

    # Go through all the pages, we are unsure how many pages there are
    while True:
        dashboards = _get_all_dashboards_in_grafana(current_page, limit, grafana_url, http_headers)

        # only include what users want
        folders_to_include = kwargs.get('folders_to_include')
        folders_to_exclude = kwargs.get('folders_to_exclude')
        if folders_to_include:
            folders_to_include = [f.lower() for f in folders_to_include]
            dashboards = [d for d in dashboards if (d.get('folderTitle', '').lower() in folders_to_include or
                                                    not d.get('folderTitle', '') and 'general' in folders_to_include)]
        if folders_to_exclude:
            folders_to_exclude = [f.lower() for f in folders_to_exclude]
            dashboards = [d for d in dashboards if ((d.get('folderTitle', '')
                                                    and d.get('folderTitle', '').lower() not in folders_to_exclude)
                                                    or
                                                    (not d.get('folderTitle', '')
                                                    and 'general' not in folders_to_exclude))]

        print_an_empty_line()
        if len(dashboards) == 0:
            break
        current_page += 1
        current_run_dashboards = _get_individual_dashboard_setting(dashboards, grafana_url, http_headers)
        # add the previous list to the list where we added everything.
        all_dashboards += current_run_dashboards
        print_an_empty_line()

    return all_dashboards


def _get_all_dashboards_in_grafana(page, limit, grafana_url, http_headers):
    (status, content) = search_dashboard(page,
                                         limit,
                                         grafana_url,
                                         http_headers)
    if status == 200:
        dashboards = content
        logger.info("There are %s dashboards:", len(dashboards))
        for board in dashboards:
            logger.info('name: %s', board['title'])
        return dashboards
    logger.warning("Get dashboards FAILED, status: %s, msg: %s", status, content)
    return []


def _get_individual_dashboard_setting(dashboards, grafana_url, http_headers):
    if not dashboards:
        return []

    all_individual_dashboards = []
    for board in dashboards:
        board_uri = "uid/" + board['uid']

        (status, content) = get_dashboard(board_uri, grafana_url, http_headers)
        if status == 200:
            # do not back up provisioned dashboards
            if content['meta']['provisioned']:
                logger.warning("Dashboard: \"%s\" is provisioned, skipping...", board['title'])
                continue

            all_individual_dashboards.append(content)

    return all_individual_dashboards


def get_all_library_panels(grafana_url, http_headers):
    all_panels = []
    current_page = 1
    while True:
        panels = _get_all_library_panels_in_grafana(current_page, grafana_url, http_headers)

        print_an_empty_line()
        if len(panels) == 0:
            break
        current_page += 1

        # Since we are not excluding anything. We can just add the panels to the
        # list since this is all the data we need.
        all_panels += panels
        print_an_empty_line()

    return all_panels


def _get_all_library_panels_in_grafana(page, grafana_url, http_headers):
    (status, content) = search_library_panels(page, grafana_url, http_headers)
    if status == 200:
        library_panels = content
        logger.info("There are %s library panels:", len(library_panels))
        for panel in library_panels:
            logger.info('name: %s', panel['name'])
        return library_panels
    logger.warning("Get library panel FAILED, status: %s, msg: %s", status, content)
    return []


def get_all_snapshots(grafana_url, http_headers):
    (status, content) = search_snapshot(grafana_url, http_headers)

    if status != 200:
        logger.warning("Query snapshot failed, status: %s, msg: %s", status, content)
        return []

    all_snapshots_metadata = []
    for snapshot in content:
        if not snapshot['external']:
            all_snapshots_metadata.append(snapshot)
        else:
            logger.warning("External snapshot: %s is skipped", snapshot['name'])

    logger.info("There are %s snapshots:", len(all_snapshots_metadata))

    all_snapshots = []
    for snapshot in all_snapshots_metadata:
        logger.info(snapshot)

        (individual_status, individual_content) = get_snapshot(snapshot['key'], grafana_url, http_headers)
        if individual_status == 200:
            all_snapshots.append((snapshot['key'], individual_content))
        else:
            logger.warning("Getting snapshot %s FAILED, status: %s, msg: %s",
                           snapshot['name'], individual_status, individual_content)

    return all_snapshots


def get_all_folders(grafana_url, http_headers, **kwargs):
    folders = _get_all_folders_in_grafana(grafana_url, http_get_headers=http_headers)

    # only include what users want
    folders_to_include = kwargs.get('folders_to_include')
    folders_to_exclude = kwargs.get('folders_to_exclude')
    if folders_to_include:
        folders_to_include = [f.lower() for f in folders_to_include]
        folders = [f for f in folders if
                   f.get('title', '').lower() in folders_to_include or
                   f.get('folderTitle', '').lower() in folders_to_include]
    if folders_to_exclude:
        folders_to_exclude = [f.lower() for f in folders_to_exclude]
        folders = [f for f in folders if
                   f.get('title', '').lower() not in folders_to_exclude and
                   f.get('folderTitle', '').lower() not in folders_to_exclude]

    individual_folders = []
    for folder in folders:
        (status_folder_settings, content_folder_settings) = get_folder(folder['uid'], grafana_url, http_headers)

        skip_folder_permissions = kwargs.get('skip_folder_permissions')
        (status_folder_permissions, content_folder_permissions) = get_folder_permissions(folder['uid'],
                                                                                         grafana_url,
                                                                                         http_headers)
        if skip_folder_permissions and status_folder_settings == 200:
            logger.info("Skipping folder permissions for folder %s", folder['title'])
            individual_folders.append((content_folder_settings, None))
        elif status_folder_settings == 200 and status_folder_permissions == 200:
            individual_folders.append((content_folder_settings, content_folder_permissions))
        else:
            logger.warning("Getting folder %s FAILED", folder['title'])
            logger.info("settings status: %s, settings content: %s, permissions status: %s, permissions content: %s",
                        status_folder_settings,
                        content_folder_settings,
                        status_folder_permissions,
                        content_folder_permissions)

    return individual_folders


def _get_all_folders_in_grafana(grafana_url, http_get_headers):
    status_and_content_of_all_folders = search_folders(grafana_url, http_get_headers)
    status = status_and_content_of_all_folders[0]
    content = status_and_content_of_all_folders[1]
    if status == 200:
        folders = content
        logger.info("There are %s folders:", len(content))
        for folder in folders:
            logger.info("name: %s", folder['title'])
        return folders
    logger.warning("Get folders FAILED, status: %s, msg: %s", status, content)
    return []


def get_all_annotations(grafana_url, http_headers):
    all_annotations = []
    now = int(round(time.time() * 1000))
    one_month_in_ms = 31 * 24 * 60 * 60 * 1000

    ts_to = now
    ts_from = now - one_month_in_ms
    thirteen_months_retention = now - (13 * one_month_in_ms)

    while ts_from > thirteen_months_retention:
        (status, content) = search_annotations(grafana_url, ts_from, ts_to, http_headers)
        if status == 200:
            annotations_batch = content
            logger.info("There are %s annotations:", len(annotations_batch))
            all_annotations += annotations_batch
        else:
            logger.warning("Query annotation FAILED, status: %s, msg: %s", status, content)

        ts_to = ts_from
        ts_from = ts_from - one_month_in_ms

    return all_annotations


def get_all_datasources(grafana_url, http_headers):
    (status, content) = search_datasource(grafana_url, http_headers)
    if status == 200:
        datasources = content
        logger.info("There are %s datasources:", len(datasources))
        return datasources

    logger.info("Query datasource FAILED, status: %s, msg: %s", status, content)
    return None


def print_an_empty_line():
    logger.info('')
