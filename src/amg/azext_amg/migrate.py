from knack.log import get_logger

from .restore import create_dashboard, create_folder, create_library_panel, create_snapshot, create_annotation, create_datasource, set_uid_mapping
from .backup_core import get_all_dashboards, get_all_library_panels, get_all_snapshots, get_all_folders, get_all_annotations, get_all_datasources

logger = get_logger(__name__)


def migrate(backup_url, backup_headers, restore_url, restore_headers, folders_to_include=None, folders_to_exclude=None):
    # get all datasources to be backedup
    all_datasources = get_all_datasources(backup_url, backup_headers)
    for datasource in all_datasources:
        create_datasource(restore_url, datasource, restore_headers)
    # grab all the new datasources now. since we have created the datasources, we can now do the mapping.
    restore_datasources = get_all_datasources(restore_url, restore_headers)
    # do the mapping from the backup to the restore.
    set_uid_mapping(all_datasources, restore_datasources)

    all_folders = get_all_folders(backup_url, backup_headers, folders_to_include=folders_to_include, folders_to_exclude=folders_to_exclude)
    for folder in all_folders:
        content_folder_settings, content_folder_permissions = folder
        create_folder(restore_url, content_folder_settings, restore_headers)

    all_library_panels = get_all_library_panels(backup_url, backup_headers)
    for library_panel in all_library_panels:
        library_panel['id'] = None
        create_library_panel(restore_url, library_panel, restore_headers)

    all_dashboards = get_all_dashboards(backup_url, backup_headers, folders_to_include=folders_to_include, folders_to_exclude=folders_to_exclude)
    for dashboard in all_dashboards:
        dashboard['dashboard']['id'] = None
        create_dashboard(restore_url, dashboard, restore_headers)

    # get the list of snapshots to backup
    all_snapshots = get_all_snapshots(backup_url, backup_headers)
    for snapshot in all_snapshots:
        create_snapshot(restore_url, snapshot, restore_headers)

    # get all the annotations
    all_annotations = get_all_annotations(backup_url, backup_headers)
    for annotation in all_annotations:
        create_annotation(restore_url, annotation, restore_headers)
