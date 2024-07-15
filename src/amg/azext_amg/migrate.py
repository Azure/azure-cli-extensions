from knack.log import get_logger
from azure.cli.core.style import print_styled_text, Style

from .restore import create_dashboard, create_folder, create_library_panel, create_snapshot, create_annotation, create_datasource, set_uid_mapping
from .backup_core import get_all_dashboards, get_all_library_panels, get_all_snapshots, get_all_folders, get_all_annotations, get_all_datasources

logger = get_logger(__name__)


def migrate(backup_url, backup_headers, restore_url, restore_headers, dry_run, folders_to_include=None, folders_to_exclude=None):
    # TODO: refactor, make helper functions that this will call and just return the summaries.
    datasources_created_summary = []
    datasources_remapped_summary = []
    folders_created_summary = []
    library_panels_synced_summary = {}
    dashboards_synced_summary = {}
    snapshots_synced_summary = {}
    annotations_synced_summary = []

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
    all_restore_folders = get_all_folders(restore_url, restore_headers, folders_to_include=folders_to_include, folders_to_exclude=folders_to_exclude)
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

    # get all the dashboards first, so we can get the library panels
    all_dashboards = get_all_dashboards(backup_url, backup_headers, folders_to_include=folders_to_include, folders_to_exclude=folders_to_exclude)

    all_library_panels = get_all_library_panels(backup_url, backup_headers)
    library_panels_uids_to_update = get_all_library_panels_uids_from_dashboards(all_dashboards)
    # only update the library panels that are not included / excluded.
    all_library_panels_filtered = [panel for panel in all_library_panels if panel['uid'] in library_panels_uids_to_update]
    for library_panel in all_library_panels_filtered:
        library_panel['id'] = None
        if not dry_run:
            # in create_library_panel, it does the patch if the library panel already exists.
            create_library_panel(restore_url, library_panel, restore_headers)

        panel_folder_name = library_panel['meta']['folderName']
        if panel_folder_name not in library_panels_synced_summary:
            library_panels_synced_summary[panel_folder_name] = set()
        library_panels_synced_summary[panel_folder_name].add(library_panel['name'])

    # we don't backup provisioned dashboards, so we don't need to restore them
    for dashboard in all_dashboards:
        dashboard['dashboard']['id'] = None
        # TODO: add the override flag, we don't need to delete & create, override will just do it.
        if not dry_run:
            create_dashboard(restore_url, dashboard, restore_headers)

        folder_title = dashboard['meta']['folderTitle']
        if folder_title not in dashboards_synced_summary:
            dashboards_synced_summary[folder_title] = []
        dashboards_synced_summary[folder_title].append(dashboard['dashboard']['title'])

    # get the list of snapshots to backup
    all_snapshots = get_all_snapshots(backup_url, backup_headers)
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

    # get all the annotations
    all_annotations = get_all_annotations(backup_url, backup_headers)
    for annotation in all_annotations:
        if not dry_run:
            create_annotation(restore_url, annotation, restore_headers)

        # can do text to get the text, annotations don't have titles.
        # annotations_synced_summary.append(annotation['text'])
        annotations_synced_summary.append(annotation['id'])

    output = [
        (Style.IMPORTANT, f"\n\nDry run: {dry_run if dry_run else False}\n"),
        (Style.SUCCESS, "\n\nDatasources created:"),
        (Style.PRIMARY, "\n    " + "\n    ".join(datasources_created_summary)),
        (Style.SUCCESS, "\n\nFolders created:"),
        (Style.PRIMARY, "\n    " + "\n    ".join(folders_created_summary)),
    ]

    output.append((Style.SUCCESS, "\n\nLibrary panels synced:"))
    for folder, panels in library_panels_synced_summary.items():
        output.append((Style.PRIMARY, f"\n    {folder}/\n        "))
        output.append((Style.SECONDARY, "\n        ".join(panels)))

    output.append((Style.SUCCESS, "\n\nDashboards synced:"))
    for folder, dashboards in dashboards_synced_summary.items():
        output.append((Style.PRIMARY, f"\n    {folder}/\n        "))
        output.append((Style.SECONDARY, "\n        ".join(dashboards)))

    output.append((Style.SUCCESS, "\n\nSnapshots synced:"))
    for folder, snapshots in snapshots_synced_summary.items():
        output.append((Style.PRIMARY, f"\n    {folder}/\n        "))
        output.append((Style.SECONDARY, "\n        ".join(snapshots)))

    output.append((Style.SUCCESS, "\n\nAnnotations synced:"))
    output.append((Style.PRIMARY, "\n    " + "\n    ".join(annotations_synced_summary)))

    print_styled_text(output)


def get_all_library_panels_uids_from_dashboards(all_dashboards):
    library_panels_uids_to_update = set()
    for dashboard in all_dashboards:
        for panel in dashboard['dashboard']['panels']:
            if panel.get('libraryPanel'):
                library_panels_uids_to_update.add(panel['libraryPanel']['uid'])

    return library_panels_uids_to_update
