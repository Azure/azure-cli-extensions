from knack.log import get_logger

from .restore import create_dashboard, create_folder, create_library_panel, create_snapshot, create_annotation, create_datasource, set_uid_mapping
from .backup_core import get_all_dashboards, get_all_library_panels, get_all_snapshots, get_all_folders, get_all_annotations, get_all_datasources

logger = get_logger(__name__)


def migrate(backup_url, backup_headers, restore_url, restore_headers, dry_run, folders_to_include=None, folders_to_exclude=None):
    datasources_created_summary = []
    datasources_remapped_summary = []
    folders_created_summary = []

    # get all datasources to be backedup
    all_datasources = get_all_datasources(backup_url, backup_headers)
    all_restore_datasources = get_all_datasources(restore_url, restore_headers)
    # since in our remapping, we use the name and type to check if it is the same datasource.
    restore_datasources_names = {(ds['name'], ds['type']) for ds in all_restore_datasources}

    for datasource in all_datasources:
        if (datasource['name'], datasource['type']) not in restore_datasources_names:
            if not dry_run:
                create_datasource(restore_url, datasource, restore_headers)
            datasources_created_summary.append(datasource['name'])
        else:
            logger.warning("Datasource %s already exists, remapping", datasource['name'])
            datasources_remapped_summary.append(datasource['name'])
    # grab all the new datasources now. since we have created the datasources, we can now do the mapping.
    # do the mapping from the backup to the restore.
    set_uid_mapping(all_datasources, all_restore_datasources)

    all_folders = get_all_folders(backup_url, backup_headers, folders_to_include=folders_to_include, folders_to_exclude=folders_to_exclude)
    all_restore_folders = get_all_folders(backup_url, backup_headers, folders_to_include=folders_to_include, folders_to_exclude=folders_to_exclude)
    restore_folder_uids = {restore_content['uid'] for (restore_content, _) in all_restore_folders}

    for folder in all_folders:
        content_folder_settings, content_folder_permissions = folder
        # create a folder if it does not exist
        if content_folder_settings['uid'] not in restore_folder_uids:
            if not dry_run:
                create_folder(restore_url, content_folder_settings, restore_headers)
            folders_created_summary.append(content_folder_settings['title'])
        else:
            logger.warning("Folder %s already exists, skipping", content_folder_settings['title'])

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
