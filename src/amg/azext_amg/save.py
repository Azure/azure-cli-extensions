import datetime

from .save_dashboards import save_dashboards
from .save_folders import save_folders
from .save_snapshots import save_snapshots
from .save_annotations import save_annotations
from .save_datasources import save_datasources
from .archive import archive


def save(grafana_url, backup_dir, components, http_headers):
    backup_functions = {'dashboards': save_dashboards,
                        'folders': save_folders,
                        'snapshots': save_snapshots,
                        'annotations': save_annotations,
                        'datasources': save_datasources}

    timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M')
    if components:
        # Backup only the components that provided via an argument
        for backup_function in components:
            backup_functions[backup_function](grafana_url, backup_dir, timestamp, http_headers)
    else:
        # Backup every component
        for backup_function in backup_functions.values():
            backup_function(grafana_url, backup_dir, timestamp, http_headers)

    archive(backup_dir, timestamp)
