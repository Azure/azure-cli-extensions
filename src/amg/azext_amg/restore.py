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
from knack.log import get_logger

from .utils import get_folder_id, send_grafana_post


logger = get_logger(__name__)


def restore(grafana_url, archive_file, components, http_headers):
    try:
        tarfile.is_tarfile(name=archive_file)
    except IOError as e:
        raise ArgumentUsageError(f"failed to open {archive_file} as a tar file") from e

    # Shell game magic warning: restore_function keys require the 's'
    # to be removed in order to match file extension names...
    restore_functions = collections.OrderedDict()
    restore_functions['folder'] = _create_folder
    restore_functions['dashboard'] = _create_dashboard
    restore_functions['snapshot'] = _create_snapshot
    restore_functions['annotation'] = _create_annotation
    restore_functions['datasource'] = _create_datasource

    with tarfile.open(name=archive_file, mode='r:gz') as tar:
        with tempfile.TemporaryDirectory() as tmpdir:
            tar.extractall(tmpdir)
            tar.close()
            _restore_components(grafana_url, restore_functions, tmpdir, components, http_headers)


def _restore_components(grafana_url, restore_functions, tmpdir, components, http_headers):

    if components:
        exts = [c[:-1] for c in components]
    else:
        exts = list(restore_functions.keys())
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

    result = send_grafana_post(f'{grafana_url}/api/dashboards/db', json.dumps(payload), http_headers)
    dashboard_title = content['dashboard'].get('title', '')
    logger.warning("Create dashboard \"%s\". %s", dashboard_title, "SUCCESS" if result[0] == 200 else "FAILURE")
    logger.info("status: %s, msg: %s", result[0], result[1])


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
    logger.warning("Create snapshot \"%s\". %s", snapshot['name'], "SUCCESS" if status == 200 else "FAILURE")
    logger.info("status: %s, msg: %s", status, content)


# Restore folders
def _create_folder(grafana_url, file_path, http_headers):
    with open(file_path, 'r', encoding="utf8") as f:
        data = f.read()

    folder = json.loads(data)
    result = send_grafana_post(f'{grafana_url}/api/folders', json.dumps(folder), http_headers)
    # 412 means the folder has existed
    logger.warning("Create folder \"%s\". %s", folder.get('title', ''),
                   "SUCCESS" if result[0] in [200, 412] else "FAILURE")
    logger.info("status: %s, msg: %s", result[0], result[1])


# Restore annotations
def _create_annotation(grafana_url, file_path, http_headers):
    with open(file_path, 'r', encoding="utf8") as f:
        data = f.read()

    annotation = json.loads(data)
    result = send_grafana_post(f'{grafana_url}/api/annotations', json.dumps(annotation), http_headers)
    logger.warning("Create annotation \"%s\". %s", annotation['id'], "SUCCESS" if result[0] == 200 else "FAILURE")
    logger.info("status: %s, msg: %s", result[0], result[1])


# Restore data sources
def _create_datasource(grafana_url, file_path, http_headers):
    with open(file_path, 'r', encoding="utf8") as f:
        data = f.read()

    datasource = json.loads(data)
    result = send_grafana_post(f'{grafana_url}/api/datasources', json.dumps(datasource), http_headers)
    logger.warning("Create datasource \"%s\". %s", datasource['name'], "SUCCESS" if result[0] == 200 else "FAILURE")
    logger.info("status: %s, msg: %s", result[0], result[1])
