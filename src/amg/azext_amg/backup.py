from glob import glob
import datetime
import tarfile
import os
import shutil
import json
import re

from knack.log import get_logger

from .backup_core import get_dashboards, _save_library_panels, _save_folders, _save_snapshots, _save_annotations, _save_datasources

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

    dashboards = get_dashboards(grafana_url, http_headers, **kwargs)
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
