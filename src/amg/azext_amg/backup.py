from glob import glob
import datetime
import tarfile
import os
import shutil

from knack.log import get_logger

from .backup_core import _save_dashboards, _save_library_panels, _save_folders, _save_snapshots, _save_annotations, _save_datasources

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

