# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import collections
import json
from glob import glob
import tarfile
import tempfile

from azure.cli.core.azclierror import ArgumentUsageError
from azure.cli.core.style import print_styled_text, Style
from knack.log import get_logger

from .utils import (get_folder_id, send_grafana_post, send_grafana_patch,
                    send_grafana_get, create_datasource_mapping, remap_datasource_uids)

logger = get_logger(__name__)

uid_mapping = {}


def restore(grafana_url, archive_file, components, http_headers, destination_datasources=None):
    try:
        tarfile.is_tarfile(name=archive_file)
    except IOError as e:
        raise ArgumentUsageError(f"failed to open {archive_file} as a tar file") from e

    restore_functions = collections.OrderedDict()
    restore_functions['folder'] = _create_folder
    restore_functions['dashboard'] = _create_dashboard
    restore_functions['library_panel'] = _create_library_panel
    restore_functions['snapshot'] = _create_snapshot
    restore_functions['annotation'] = _create_annotation
    restore_functions['datasource'] = _create_datasource

    with tarfile.open(name=archive_file, mode='r:gz') as tar:
        with tempfile.TemporaryDirectory() as tmpdir:
            tar.extractall(tmpdir)
            tar.close()
            _restore_components(grafana_url, restore_functions, tmpdir, components, http_headers,
                                destination_datasources=destination_datasources)


def _restore_components(grafana_url, restore_functions, tmpdir, components, http_headers, destination_datasources=None):

    if components:
        exts = [c[:-1] for c in components]
    else:
        exts = list(restore_functions.keys())

    # to re-map data sources, create a mapping from source to destination workspace before transform the dashboards
    if destination_datasources:
        if "datasource" in exts:  # first let us skip datasource restoration
            exts.pop(exts.index("datasource"))
        datasource_backups = glob(f'{tmpdir}/**/*.datasource', recursive=True)
        if not datasource_backups:
            logger.warning('"remap data source" is on, but data sources info wasn\'t archived to transform dashboards')

        source_datasources = []
        for file_path in datasource_backups:
            with open(file_path, 'r', encoding="utf8") as f:
                data = f.read()
            datasource = json.loads(data)
            source_datasources.append(datasource)

        global uid_mapping  # pylint: disable=global-statement
        uid_mapping = create_datasource_mapping(source_datasources, destination_datasources)

    if "dashboard" in exts:  # dashboard restoration can't work if linked library panels don't exist
        exts.insert(0, "library_panel")

    if "folder" in exts:  # make "folder" be the first to restore, so dashboards can be positioned under a right folder
        exts.insert(0, exts.pop(exts.index("folder")))

    for ext in exts:
        for file_path in glob(f'{tmpdir}/**/*.{ext}', recursive=True):
            logger.info('Restoring %s: %s', ext, file_path)
            restore_functions[ext](grafana_url, file_path, http_headers)


# Restore dashboards
def _create_dashboard(grafana_url, file_path, http_headers):
    with open(file_path, 'r', encoding="utf8") as f:
        data = f.read()

    content = json.loads(data)
    content['dashboard']['id'] = None

    payload = {
        'dashboard': content['dashboard'],
        'folderId': get_folder_id(content, grafana_url, http_post_headers=http_headers),
        'overwrite': True
    }

    datasources_missed = set()
    remap_datasource_uids(payload, uid_mapping, datasources_missed)

    result = send_grafana_post(f'{grafana_url}/api/dashboards/db', json.dumps(payload), http_headers)
    dashboard_title = content['dashboard'].get('title', '')
    print_styled_text([
        (Style.WARNING, f'Create dashboard {dashboard_title}: '),
        (Style.SUCCESS, 'SUCCESS') if result[0] == 200 else (Style.ERROR, 'FAILURE')
    ])
    logger.info("status: %s, msg: %s", result[0], result[1])


# Restore Library Panel
def _create_library_panel(grafana_url, file_path, http_headers):
    with open(file_path, 'r', encoding="utf8") as f:
        data = f.read()

    payload = json.loads(data)
    payload['id'] = None
    payload['folderId'] = get_folder_id(payload, grafana_url, http_post_headers=http_headers)

    datasources_missed = set()
    remap_datasource_uids(payload, uid_mapping, datasources_missed)

    panel_name = payload.get('name', '')

    (status, content) = send_grafana_post(f'{grafana_url}/api/library-elements', json.dumps(payload), http_headers)
    if status >= 400 and ('name or UID already exists' in content.get('message', '')):
        uid = payload['uid']
        panel_uri = f'{grafana_url}/api/library-elements/{uid}'
        (status, content) = send_grafana_get(panel_uri, http_headers)
        if status == 200:
            patch_payload = {
                'name': panel_name,
                'model': payload['model'],
                'version': content['result']['version'],
                'kind': payload['kind']
            }
            (status, content) = send_grafana_patch(f'{grafana_url}/api/library-elements/{uid}',
                                                   json.dumps(patch_payload), http_headers)
    print_styled_text([
        (Style.WARNING, f'Create library panel {panel_name}: '),
        (Style.SUCCESS, 'SUCCESS') if status == 200 else (Style.ERROR, 'FAILURE')
    ])
    logger.info("status: %s, msg: %s", status, content)


# Restore snapshots
def _create_snapshot(grafana_url, file_path, http_headers):
    with open(file_path, 'r', encoding="utf8") as f:
        data = f.read()

    snapshot = json.loads(data)
    try:
        snapshot['name'] = snapshot['dashboard']['title']
    except KeyError:
        snapshot['name'] = "Untitled Snapshot"

    (status, content) = send_grafana_post(f'{grafana_url}/api/snapshots', json.dumps(snapshot), http_headers)
    snapshot_name = snapshot['name']
    print_styled_text([
        (Style.WARNING, f'Create snapshot {snapshot_name}: '),
        (Style.SUCCESS, 'SUCCESS') if status == 200 else (Style.ERROR, 'FAILURE')
    ])
    logger.info("status: %s, msg: %s", status, content)


# Restore folders
def _create_folder(grafana_url, file_path, http_headers):
    with open(file_path, 'r', encoding="utf8") as f:
        data = f.read()

    folder = json.loads(data)
    result = send_grafana_post(f'{grafana_url}/api/folders', json.dumps(folder), http_headers)
    folder_name = folder.get('title', '')
    # 412 means the folder already exists
    print_styled_text([
        (Style.WARNING, f'Create folder {folder_name}: '),
        (Style.SUCCESS, 'SUCCESS') if result[0] in [200, 412] else (Style.ERROR, 'FAILURE')
    ])
    logger.info("status: %s, msg: %s", result[0], result[1])


# Restore annotations
def _create_annotation(grafana_url, file_path, http_headers):
    with open(file_path, 'r', encoding="utf8") as f:
        data = f.read()

    annotation = json.loads(data)
    result = send_grafana_post(f'{grafana_url}/api/annotations', json.dumps(annotation), http_headers)
    annotation_id = annotation['id']
    print_styled_text([
        (Style.WARNING, f'Create annotation {annotation_id}: '),
        (Style.SUCCESS, 'SUCCESS') if result[0] == 200 else (Style.ERROR, 'FAILURE')
    ])
    logger.info("status: %s, msg: %s", result[0], result[1])


# Restore data sources
def _create_datasource(grafana_url, file_path, http_headers):
    with open(file_path, 'r', encoding="utf8") as f:
        data = f.read()

    datasource = json.loads(data)
    result = send_grafana_post(f'{grafana_url}/api/datasources', json.dumps(datasource), http_headers)
    datasource_name = datasource['name']
    # 409 means the data source already exists
    print_styled_text([
        (Style.WARNING, f'Create datasource {datasource_name}: '),
        (Style.SUCCESS, 'SUCCESS') if result[0] in [200, 409] else (Style.ERROR, 'FAILURE')
    ])
    logger.info("status: %s, msg: %s", result[0], result[1])
