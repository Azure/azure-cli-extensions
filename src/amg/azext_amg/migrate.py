from knack.log import get_logger

from .backup import backup
from .restore import restore, create_dashboard
from .backup_core import get_all_dashboards, get_all_library_panels, get_all_snapshots, get_all_folders, get_all_annotations, get_all_datasources

logger = get_logger(__name__)


def migrate(backup_grafana_name, backup_url, backup_directory, components, backup_headers,
            restore_url, restore_headers, data_sources, folders_to_include=None, folders_to_exclude=None):
    archive_file = backup(grafana_name=backup_grafana_name,
                          grafana_url=backup_url,
                          backup_dir=backup_directory,
                          components=components,
                          http_headers=backup_headers,
                          folders_to_include=folders_to_include,
                          folders_to_exclude=folders_to_exclude)

    restore(grafana_url=restore_url,
            archive_file=archive_file,
            components=components,
            http_headers=restore_headers,
            destination_datasources=data_sources)

    # get all datasources
    # all_datasources = get_all_datasources(backup_url, backup_headers)

    # get all folders
    # all_folders = get_all_folders(backup_url, backup_headers, folders_to_include=folders_to_include, folders_to_exclude=folders_to_exclude)

    # all_library_panels = get_all_library_panels(backup_url, backup_headers)
    # now go through all the library panels and save them, make sure to logger.warning()

    # get the list of dashboards to backup
    # all_dashboards = get_all_dashboards(backup_url, backup_headers, folders_to_include=folders_to_include, folders_to_exclude=folders_to_exclude)
    # for dashboard in all_dashboards:
    #     dashboard['dashboard']['id'] = None
    #     create_dashboard(restore_url, dashboard, restore_headers)

    # get the list of snapshots to backup
    # all_snapshots = get_all_snapshots(backup_url, backup_headers)

    # get all the annotations
    # all_annotations = get_all_annotations(backup_url, backup_headers)


def _create_or_update_dashboard():
    pass