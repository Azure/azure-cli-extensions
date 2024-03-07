# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import datetime
from glob import glob
import json
import os
import random
import shutil
import string
import re
import tarfile
import time

from knack.log import get_logger

from .utils import search_dashboard, get_dashboard
from .utils import search_library_panels, get_library_panel
from .utils import search_snapshot, get_snapshot
from .utils import search_folders, get_folder, get_folder_permissions
from .utils import search_datasource
from .utils import search_annotations

logger = get_logger(__name__)


def backup(grafana_name, grafana_url, backup_dir, components, http_headers, **kwargs):
    backup_functions = {'dashboards': _save_dashboards,
                        'library_panels': _save_library_panels,
                        'folders': _save_folders,
                        'snapshots': _save_snapshots,
                        'annotations': _save_annotations,
                        'datasources': _save_datasources}

    timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M')
    if components:
        # Backup only the components that provided via an argument
        if 'dashboards' in components:  # dashboards won't load if linked library panels don't exist
            components.insert(0, 'library_panels')
        for backup_function in components:
            backup_functions[backup_function](grafana_url, backup_dir, timestamp, http_headers, **kwargs)
    else:
        # Backup every component
        for backup_function in backup_functions.values():
            backup_function(grafana_url, backup_dir, timestamp, http_headers, **kwargs)

    _archive(grafana_name, backup_dir, timestamp)


def _archive(grafana_name, backup_dir, timestamp):
    archive_file = f'{backup_dir}/{grafana_name}-{timestamp}.tar.gz'
    backup_files = []

    for folder_name in ['folders', 'datasources', 'dashboards', 'library_panels', 'alert_channels',
                        'organizations', 'users', 'snapshots', 'versions', 'annotations']:
        backup_path = f'{backup_dir}/{folder_name}/{timestamp}'

        for file_path in glob(backup_path):
            logger.info('backup %s at: %s', folder_name, file_path)
            backup_files.append(file_path)

    if os.path.exists(archive_file):
        os.remove(archive_file)

    with tarfile.open(archive_file, "w:gz") as tar:
        for file_path in backup_files:
            tar.add(file_path)
            if not os.environ.get("AMG_DEBUG", False):
                shutil.rmtree(os.path.abspath(os.path.join(file_path, os.pardir)))
    tar.close()
    logger.warning('Created archive at: %s', archive_file)


# Save dashboards
def _save_dashboards(grafana_url, backup_dir, timestamp, http_headers, **kwargs):
    folder_path = f'{backup_dir}/dashboards/{timestamp}'
    log_file = f'dashboards_{timestamp}.txt'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    limit = 5000  # limit is 5000 above V6.2+
    current_page = 1
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

        _print_an_empty_line()
        if len(dashboards) == 0:
            break
        current_page += 1
        _get_individual_dashboard_setting_and_save(dashboards, folder_path, log_file, grafana_url, http_headers)
        _print_an_empty_line()


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


def _save_dashboard_setting(dashboard_name, file_name, dashboard_settings, folder_path):
    file_path = _save_json(file_name, dashboard_settings, folder_path, 'dashboard')
    logger.warning("Dashboard: \"%s\" is saved", dashboard_name)
    logger.info("    -> %s", file_path)


def _get_individual_dashboard_setting_and_save(dashboards, folder_path, log_file, grafana_url, http_headers):
    file_path = folder_path + '/' + log_file
    if dashboards:
        with open(file_path, 'w', encoding="utf8") as f:
            for board in dashboards:
                board_uri = "uid/" + board['uid']

                (status, content) = get_dashboard(board_uri, grafana_url, http_headers)
                if status == 200:
                    # do not back up provisioned dashboards
                    if content['meta']['provisioned']:
                        logger.warning("Dashboard: \"%s\" is provisioned, skipping...", board['title'])
                        continue
                    _save_dashboard_setting(
                        board['title'],
                        board_uri,
                        content,
                        folder_path)
                    f.write(board_uri + '\t' + board['title'] + '\n')


# Save library panels
def _save_library_panels(grafana_url, backup_dir, timestamp, http_headers, **kwargs):  # pylint: disable=unused-argument
    folder_path = f'{backup_dir}/library_panels/{timestamp}'
    log_file = f'library_panels_{timestamp}.txt'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    current_page = 1
    while True:
        panels = _get_all_library_panels_in_grafana(current_page, grafana_url, http_headers)

        _print_an_empty_line()
        if len(panels) == 0:
            break
        current_page += 1
        _get_individual_library_panel_setting_and_save(panels, folder_path, log_file, grafana_url, http_headers)
        _print_an_empty_line()


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


def _save_library_panel_setting(panel_name, file_name, library_panel_settings, folder_path):
    file_path = _save_json(file_name, library_panel_settings, folder_path, 'library_panel')
    logger.warning("Library Panel: \"%s\" is saved", panel_name)
    logger.info("    -> %s", file_path)


def _get_individual_library_panel_setting_and_save(panels, folder_path, log_file, grafana_url, http_headers):
    file_path = folder_path + '/' + log_file
    if panels:
        with open(file_path, 'w', encoding="utf8") as f:
            for panel in panels:
                panel_uri = panel['uid']

                (status, content) = get_library_panel(panel_uri, grafana_url, http_headers)
                if status == 200:
                    _save_library_panel_setting(
                        panel['name'],
                        panel_uri,
                        content['result'],
                        folder_path)
                    f.write(panel_uri + '\t' + panel['name'] + '\n')


# Save snapshots
def _save_snapshots(grafana_url, backup_dir, timestamp, http_headers, **kwargs):  # pylint: disable=unused-argument
    folder_path = f'{backup_dir}/snapshots/{timestamp}'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    _get_all_snapshots_and_save(folder_path, grafana_url, http_get_headers=http_headers)
    _print_an_empty_line()


def _save_snapshot(file_name, snapshot_setting, folder_path):
    file_name = file_name.replace('/', '_')
    random_suffix = "".join(random.choice(string.ascii_letters) for _ in range(6))
    file_path = _save_json(file_name + "_" + random_suffix, snapshot_setting, folder_path, 'snapshot')
    logger.warning("Snapshot: \"%s\" is saved", snapshot_setting.get('dashboard', {}).get("title"))
    logger.info("    -> %s", file_path)


def _get_single_snapshot_and_save(snapshot, grafana_url, http_get_headers, folder_path):
    (status, content) = get_snapshot(snapshot['key'], grafana_url, http_get_headers)
    if status == 200:
        _save_snapshot(snapshot['name'], content, folder_path)
    else:
        logger.warning("Getting snapshot %s FAILED, status: %s, msg: %s", snapshot['name'], status, content)


def _get_all_snapshots_and_save(folder_path, grafana_url, http_get_headers):
    status_code_and_content = search_snapshot(grafana_url, http_get_headers)
    if status_code_and_content[0] == 200:
        snapshots = status_code_and_content[1]
        logger.info("There are %s snapshots:", len(snapshots))
        for snapshot in snapshots:
            logger.info(snapshot)
            _get_single_snapshot_and_save(snapshot, grafana_url, http_get_headers, folder_path)
    else:
        logger.warning("Query snapshot failed, status: %s, msg: %s", status_code_and_content[0],
                       status_code_and_content[1])


# Save folders
def _save_folders(grafana_url, backup_dir, timestamp, http_headers, **kwargs):
    folder_path = f'{backup_dir}/folders/{timestamp}'
    log_file = f'folders_{timestamp}.txt'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    folders = _get_all_folders_in_grafana(grafana_url, http_get_headers=http_headers)

    # only include what users want
    folders_to_include = kwargs.get('folders_to_include')
    folders_to_exclude = kwargs.get('folders_to_exclude')
    if folders_to_include:
        folders_to_include = [f.lower() for f in folders_to_include]
        folders = [f for f in folders if f.get('title', '').lower() in folders_to_include]
    if folders_to_exclude:
        folders_to_exclude = [f.lower() for f in folders_to_exclude]
        folders = [f for f in folders if f.get('title', '').lower() not in folders_to_exclude]

    _print_an_empty_line()
    _get_individual_folder_setting_and_save(folders, folder_path, log_file, grafana_url, http_get_headers=http_headers)
    _print_an_empty_line()


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


def _save_folder_setting(folder_name, file_name, folder_settings, folder_permissions, folder_path):
    file_path = _save_json(file_name, folder_settings, folder_path, 'folder')
    logger.warning("Folder: \"%s\" is saved", folder_name)
    logger.info("    -> %s", file_path)
    file_path = _save_json(file_name, folder_permissions, folder_path, 'folder_permission')
    logger.warning("Folder permissions: %s are saved", folder_name)
    logger.info("    -> %s", file_path)


def _get_individual_folder_setting_and_save(folders, folder_path, log_file, grafana_url, http_get_headers):
    file_path = folder_path + '/' + log_file
    with open(file_path, 'w+', encoding="utf8") as f:
        for folder in folders:
            folder_uri = "uid/" + folder['uid']

            (status_folder_settings, content_folder_settings) = get_folder(folder['uid'], grafana_url, http_get_headers)
            (status_folder_permissions, content_folder_permissions) = get_folder_permissions(folder['uid'],
                                                                                             grafana_url,
                                                                                             http_get_headers)

            if status_folder_settings == 200 and status_folder_permissions == 200:
                _save_folder_setting(
                    folder['title'],
                    folder_uri,
                    content_folder_settings,
                    content_folder_permissions,
                    folder_path)
                f.write(folder_uri + '\t' + folder['title'] + '\n')


# Save annotations
def _save_annotations(grafana_url, backup_dir, timestamp, http_headers, **kwargs):  # pylint: disable=unused-argument
    folder_path = f'{backup_dir}/annotations/{timestamp}'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    _get_all_annotations_and_save(folder_path, grafana_url, http_get_headers=http_headers)
    _print_an_empty_line()


def _save_annotation(file_name, annotation_setting, folder_path):
    file_path = _save_json(file_name, annotation_setting, folder_path, 'annotation')
    logger.warning("Annotation: \"%s\" is saved", annotation_setting.get('text'))
    logger.info("    -> %s", file_path)


def _get_all_annotations_and_save(folder_path, grafana_url, http_get_headers):
    now = int(round(time.time() * 1000))
    one_month_in_ms = 31 * 24 * 60 * 60 * 1000

    ts_to = now
    ts_from = now - one_month_in_ms
    thirteen_months_retention = now - (13 * one_month_in_ms)

    while ts_from > thirteen_months_retention:
        status_code_and_content = search_annotations(grafana_url, ts_from, ts_to, http_get_headers)
        if status_code_and_content[0] == 200:
            annotations_batch = status_code_and_content[1]
            logger.info("There are %s annotations:", len(annotations_batch))
            for annotation in annotations_batch:
                logger.info(annotation)
                _save_annotation(str(annotation['id']), annotation, folder_path)
        else:
            logger.warning("Query annotation FAILED, status: %s, msg: %s", status_code_and_content[0],
                           status_code_and_content[1])

        ts_to = ts_from
        ts_from = ts_from - one_month_in_ms


# Save data sources
def _save_datasources(grafana_url, backup_dir, timestamp, http_headers, **kwargs):  # pylint: disable=unused-argument
    folder_path = f'{backup_dir}/datasources/{timestamp}'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    _get_all_datasources_and_save(folder_path, grafana_url, http_get_headers=http_headers)
    _print_an_empty_line()


def _save_datasource(file_name, datasource_setting, folder_path):
    file_path = _save_json(file_name, datasource_setting, folder_path, 'datasource')
    logger.warning("Datasource: \"%s\" is saved", datasource_setting['name'])
    logger.info("    -> %s", file_path)


def _get_all_datasources_and_save(folder_path, grafana_url, http_get_headers):
    status_code_and_content = search_datasource(grafana_url, http_get_headers)
    if status_code_and_content[0] == 200:
        datasources = status_code_and_content[1]
        logger.info("There are %s datasources:", len(datasources))
        for datasource in datasources:
            logger.info(datasource)
            datasource_name = datasource['uid']
            _save_datasource(datasource_name, datasource, folder_path)
    else:
        logger.info("Query datasource FAILED, status: %s, msg: %s", status_code_and_content[0],
                    status_code_and_content[1])


def _save_json(file_name, data, folder_path, extension, pretty_print=None):
    pattern = "^db/|^uid/"
    if re.match(pattern, file_name):
        file_name = re.sub(pattern, '', file_name)

    file_path = folder_path + '/' + file_name + '.' + extension
    with open(file_path, 'w', encoding="utf8") as f:
        if pretty_print:
            f.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
        else:
            f.write(json.dumps(data))
    return file_path


def _print_an_empty_line():
    logger.info('')
