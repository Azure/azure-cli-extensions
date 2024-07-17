from knack.log import get_logger
from azure.cli.core.style import print_styled_text, Style

from .restore import create_dashboard, create_folder, create_library_panel, create_snapshot, create_annotation, create_datasource, set_uid_mapping
from .backup_core import get_all_dashboards, get_all_library_panels, get_all_snapshots, get_all_folders, get_all_annotations, get_all_datasources

logger = get_logger(__name__)


def migrate(backup_url, backup_headers, restore_url, restore_headers, dry_run, overwrite, folders_to_include=None, folders_to_exclude=None):
    # get all datasources to be backedup
    all_datasources = get_all_datasources(backup_url, backup_headers)
    all_restore_datasources = get_all_datasources(restore_url, restore_headers)
    (datasources_created_summary, datasources_remapped_summary) = _migrate_datasources(all_datasources, all_restore_datasources, restore_url, restore_headers, dry_run)

    all_folders = get_all_folders(backup_url, backup_headers, folders_to_include=folders_to_include, folders_to_exclude=folders_to_exclude)
    all_restore_folders = get_all_folders(restore_url, restore_headers, folders_to_include=folders_to_include, folders_to_exclude=folders_to_exclude)
    folders_created_summary = _migrate_folders(all_folders, all_restore_folders, restore_url, restore_headers, dry_run, overwrite)

    all_dashboards = get_all_dashboards(backup_url, backup_headers, folders_to_include=folders_to_include, folders_to_exclude=folders_to_exclude)
    all_library_panels = get_all_library_panels(backup_url, backup_headers)
    (library_panels_synced_summary, dashboards_synced_summary) = _migrate_library_panels_and_dashboards(all_dashboards, all_library_panels, restore_url, restore_headers, dry_run, overwrite)

    # get the list of snapshots to backup
    all_snapshots = get_all_snapshots(backup_url, backup_headers)
    snapshots_synced_summary = _migrate_snapshots(all_snapshots, restore_url, restore_headers, dry_run)
   
    # get all the annotations
    all_annotations = get_all_annotations(backup_url, backup_headers)
    annotations_synced_summary = _migrate_annotations(all_annotations, restore_url, restore_headers, dry_run)

    sync_status = "will be synced" if dry_run else "synced"
    output = [
        (Style.IMPORTANT, f"\n\nDry run: {dry_run if dry_run else False}\n"),
        (Style.IMPORTANT, f"Overwrite dashboards, folders, and library panels: {overwrite if overwrite else False}\n"),
    ]

    if len(datasources_created_summary) > 0:
        output.append((Style.SUCCESS, "\n\nDatasources created:"))
        output.append((Style.PRIMARY, "\n    " + "\n    ".join(datasources_created_summary)))
    if len(datasources_remapped_summary) > 0:
        output.append((Style.SUCCESS, "\n\nDatasources remapped:"))
        output.append((Style.PRIMARY, "\n    " + "\n    ".join(datasources_remapped_summary)))

    if len(folders_created_summary) > 0:
        output.append((Style.SUCCESS, "\n\nFolders created:"))
        output.append((Style.PRIMARY, "\n    " + "\n    ".join(folders_created_summary)))

    output.append((Style.SUCCESS, f"\n\nLibrary panels {sync_status}:"))
    for folder, panels in library_panels_synced_summary.items():
        output.append((Style.PRIMARY, f"\n    {folder}/\n        "))
        output.append((Style.SECONDARY, "\n        ".join(panels)))

    output.append((Style.SUCCESS, f"\n\nDashboards {sync_status}:"))
    for folder, dashboards in dashboards_synced_summary.items():
        output.append((Style.PRIMARY, f"\n    {folder}/\n        "))
        output.append((Style.SECONDARY, "\n        ".join(dashboards)))

    output.append((Style.SUCCESS, f"\n\nSnapshots {sync_status}:"))
    for folder, snapshots in snapshots_synced_summary.items():
        output.append((Style.PRIMARY, f"\n    {folder}/\n        "))
        output.append((Style.SECONDARY, "\n        ".join(snapshots)))

    output.append((Style.SUCCESS, f"\n\nAnnotations {sync_status} (by id):"))
    output.append((Style.PRIMARY, "\n    " + "\n    ".join(annotations_synced_summary)))

    print_styled_text(output)


def _migrate_datasources(all_datasources, all_restore_datasources, restore_url, restore_headers, dry_run):
    datasources_created_summary = []
    datasources_remapped_summary = []

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

    return (datasources_created_summary, datasources_remapped_summary)


def _migrate_folders(all_folders, all_restore_folders, restore_url, restore_headers, dry_run, overwrite):
    folders_created_summary = []
    restore_folder_uids = {restore_content['uid'] for (restore_content, _) in all_restore_folders}
    restore_folder_uids = set()

    for folder in all_folders:
        content_folder_settings, content_folder_permissions = folder
        # create a folder if it does not exist
        if content_folder_settings['uid'] not in restore_folder_uids:
            if not dry_run:
                # TODO: if uids match, but the folder title is different, we should update the folder title.
                create_folder(restore_url, content_folder_settings, restore_headers, overwrite)
            folders_created_summary.append(content_folder_settings['title'])
        else:
            logger.warning("Folder %s already exists, skipping", content_folder_settings['title'])
    return folders_created_summary


def _migrate_library_panels_and_dashboards(all_dashboards, all_library_panels, restore_url, restore_headers, dry_run, overwrite):
    library_panels_synced_summary = {}
    dashboards_synced_summary = {}

    library_panels_uids_to_update = _get_all_library_panels_uids_from_dashboards(all_dashboards)
    # only update the library panels that are not included / excluded.
    all_library_panels_filtered = [panel for panel in all_library_panels if panel['uid'] in library_panels_uids_to_update]
    for library_panel in all_library_panels_filtered:
        library_panel['id'] = None
        if not dry_run:
            # in create_library_panel, it does the patch if the library panel already exists.
            # TODO: only overwrite, if people say force update.
            create_library_panel(restore_url, library_panel, restore_headers, overwrite)

        panel_folder_name = library_panel['meta']['folderName']
        if panel_folder_name not in library_panels_synced_summary:
            library_panels_synced_summary[panel_folder_name] = set()
        library_panels_synced_summary[panel_folder_name].add(library_panel['name'])

    # we don't backup provisioned dashboards, so we don't need to restore them
    for dashboard in all_dashboards:
        dashboard['dashboard']['id'] = None
        # Overwrite takes care of delete & create.
        if not dry_run:
            create_dashboard(restore_url, dashboard, restore_headers, overwrite)

        folder_title = dashboard['meta']['folderTitle']
        if folder_title not in dashboards_synced_summary:
            dashboards_synced_summary[folder_title] = []
        dashboards_synced_summary[folder_title].append(dashboard['dashboard']['title'])

    return (library_panels_synced_summary, dashboards_synced_summary)


def _get_all_library_panels_uids_from_dashboards(all_dashboards):
    library_panels_uids_to_update = set()
    for dashboard in all_dashboards:
        for panel in dashboard['dashboard']['panels']:
            if panel.get('libraryPanel'):
                library_panels_uids_to_update.add(panel['libraryPanel']['uid'])

    return library_panels_uids_to_update


def _migrate_snapshots(all_snapshots, restore_url, restore_headers, dry_run):
    snapshots_synced_summary = {}
    for snapshot in all_snapshots:
        if not dry_run:
            create_snapshot(restore_url, snapshot, restore_headers)
        
        try:
            snapshot_name = snapshot['dashboard']['title']
        except KeyError:
            snapshot_name = "Untitled Snapshot"

        snapshot_folder_title = snapshot['meta']['folderTitle']
        if snapshot_folder_title not in snapshots_synced_summary:
            snapshots_synced_summary[snapshot_folder_title] = []
        snapshots_synced_summary[snapshot_folder_title].append(snapshot_name)
    return snapshots_synced_summary


def _migrate_annotations(all_annotations, restore_url, restore_headers, dry_run):
    annotations_synced_summary = []
    for annotation in all_annotations:
        if not dry_run:
            create_annotation(restore_url, annotation, restore_headers)

        # can do text to get the text, annotations don't have titles.
        # annotations_synced_summary.append(annotation['text'])
        annotations_synced_summary.append(str(annotation['id']))

    return annotations_synced_summary
