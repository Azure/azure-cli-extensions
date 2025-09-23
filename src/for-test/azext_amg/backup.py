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

from knack.log import get_logger

from .backup_core import (get_all_dashboards, get_all_library_panels, get_all_folders, get_all_snapshots,
                          get_all_annotations, get_all_datasources, print_an_empty_line)

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

    return _archive(grafana_name, backup_dir, timestamp)


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

    return archive_file


def _save_dashboards(grafana_url, backup_dir, timestamp, http_headers, **kwargs):
    folder_path = f'{backup_dir}/dashboards/{timestamp}'
    log_file = f'dashboards_{timestamp}.txt'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    dashboards = get_all_dashboards(grafana_url, http_headers, **kwargs)
    # now go through all the dashboards and save them
    for dashboard_content in dashboards:
        dashboard = dashboard_content['dashboard']
        board_uri = "uid/" + dashboard['uid']
        _save_dashboard_setting(dashboard['title'], board_uri, dashboard_content, folder_path)

        log_file_path = folder_path + '/' + log_file
        with open(log_file_path, 'w', encoding="utf8") as f:
            f.write(board_uri + '\t' + dashboard['title'] + '\n')


def _save_dashboard_setting(dashboard_name, file_name, dashboard_settings, folder_path):
    file_path = _save_json(file_name, dashboard_settings, folder_path, 'dashboard')
    logger.warning("Dashboard: \"%s\" is saved", dashboard_name)
    logger.info("    -> %s", file_path)


# Save library panels
def _save_library_panels(grafana_url, backup_dir, timestamp, http_headers, **kwargs):  # pylint: disable=unused-argument
    folder_path = f'{backup_dir}/library_panels/{timestamp}'
    log_file = f'library_panels_{timestamp}.txt'
    log_file_path = folder_path + '/' + log_file

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    all_panels = get_all_library_panels(grafana_url, http_headers)
    if not all_panels:
        return

    with open(log_file_path, 'w', encoding="utf8") as f:
        for panel in all_panels:
            panel_uri = panel['uid']
            _save_library_panel_setting(panel['name'],
                                        panel_uri,
                                        panel,
                                        folder_path)
            f.write(panel_uri + '\t' + panel['name'] + '\n')


def _save_library_panel_setting(panel_name, file_name, library_panel_settings, folder_path):
    file_path = _save_json(file_name, library_panel_settings, folder_path, 'library_panel')
    logger.warning("Library Panel: \"%s\" is saved", panel_name)
    logger.info("    -> %s", file_path)


# Save snapshots
def _save_snapshots(grafana_url, backup_dir, timestamp, http_headers, **kwargs):  # pylint: disable=unused-argument
    folder_path = f'{backup_dir}/snapshots/{timestamp}'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    all_snapshots = get_all_snapshots(grafana_url, http_headers)
    for _, snapshot in all_snapshots:
        # same thing as the metadata[name] from the list snapshots API.
        _save_snapshot(snapshot['dashboard']['title'], snapshot, folder_path)
    print_an_empty_line()


def _save_snapshot(file_name, snapshot_setting, folder_path):
    file_name = file_name.replace('/', '_')
    random_suffix = "".join(random.choice(string.ascii_letters) for _ in range(6))
    file_path = _save_json(file_name + "_" + random_suffix, snapshot_setting, folder_path, 'snapshot')
    logger.warning("Snapshot: \"%s\" is saved", snapshot_setting.get('dashboard', {}).get("title"))
    logger.info("    -> %s", file_path)


# Save folders
def _save_folders(grafana_url, backup_dir, timestamp, http_headers, **kwargs):
    folder_path = f'{backup_dir}/folders/{timestamp}'
    log_file = f'folders_{timestamp}.txt'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    folders = get_all_folders(grafana_url, http_headers, **kwargs)

    print_an_empty_line()
    log_file_path = folder_path + '/' + log_file
    with open(log_file_path, 'w+', encoding="utf8") as f:
        for folder_set in folders:
            # TODO: back up folder permissions
            folder_settings, _ = folder_set
            folder_uri = "uid/" + folder_settings['uid']

            _save_folder_setting(
                folder_settings['title'],
                folder_uri,
                folder_settings,
                folder_settings,
                folder_path)
            f.write(folder_uri + '\t' + folder_settings['title'] + '\n')
    print_an_empty_line()


def _save_folder_setting(folder_name, file_name, folder_settings, folder_permissions, folder_path):
    file_path = _save_json(file_name, folder_settings, folder_path, 'folder')
    logger.warning("Folder: \"%s\" is saved", folder_name)
    logger.info("    -> %s", file_path)
    file_path = _save_json(file_name, folder_permissions, folder_path, 'folder_permission')
    logger.warning("Folder permissions: %s are saved", folder_name)
    logger.info("    -> %s", file_path)


# Save annotations
def _save_annotations(grafana_url, backup_dir, timestamp, http_headers, **kwargs):  # pylint: disable=unused-argument
    folder_path = f'{backup_dir}/annotations/{timestamp}'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    all_annotations = get_all_annotations(grafana_url, http_headers)
    for annotation in all_annotations:
        annotation_id = str(annotation['id'])
        _save_annotation(annotation_id, annotation, folder_path)
    print_an_empty_line()


def _save_annotation(file_name, annotation_setting, folder_path):
    file_path = _save_json(file_name, annotation_setting, folder_path, 'annotation')
    logger.warning("Annotation: \"%s\" is saved", annotation_setting.get('text'))
    logger.info("    -> %s", file_path)


# Save data sources
def _save_datasources(grafana_url, backup_dir, timestamp, http_headers, **kwargs):  # pylint: disable=unused-argument
    folder_path = f'{backup_dir}/datasources/{timestamp}'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    all_datasources = get_all_datasources(grafana_url, http_headers)
    for datasource in all_datasources:
        datasource_name = datasource['uid']
        _save_datasource(datasource_name, datasource, folder_path)
    print_an_empty_line()


def _save_datasource(file_name, datasource_setting, folder_path):
    file_path = _save_json(file_name, datasource_setting, folder_path, 'datasource')
    logger.warning("Datasource: \"%s\" is saved", datasource_setting['name'])
    logger.info("    -> %s", file_path)


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
