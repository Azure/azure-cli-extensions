from knack.log import get_logger
from azure.cli.core.style import print_styled_text, Style

from .restore import create_dashboard, create_folder, create_library_panel, create_snapshot, create_annotation, create_datasource, set_uid_mapping, check_folder_exists, check_library_panel_exists, check_dashboard_exists
from .backup_core import get_all_dashboards, get_all_library_panels, get_all_snapshots, get_all_folders, get_all_annotations, get_all_datasources

logger = get_logger(__name__)


def migrate(backup_url, backup_headers, restore_url, restore_headers, dry_run, overwrite, folders_to_include=None, folders_to_exclude=None):
    # get all datasources to be backedup
    all_datasources = get_all_datasources(backup_url, backup_headers)
    all_restore_datasources = get_all_datasources(restore_url, restore_headers)
    if (all_restore_datasources is None) or (all_datasources is None):
        logger.error("ABORTING!! Datasources are not found. Please check the URLs, headers, or api key/service token. Try running with --verbose.")
        return
    (datasources_created_summary, datasources_remapped_summary) = _migrate_datasources(all_datasources, all_restore_datasources, restore_url, restore_headers, dry_run)

    all_folders = get_all_folders(backup_url, backup_headers, folders_to_include=folders_to_include, folders_to_exclude=folders_to_exclude)
    all_restore_folders = get_all_folders(restore_url, restore_headers, folders_to_include=folders_to_include, folders_to_exclude=folders_to_exclude)
    (folders_created_summary, folders_overwrote_summary) = _migrate_folders(all_folders, all_restore_folders, restore_url, restore_headers, dry_run, overwrite)

    valid_folder_uids = set(folder[0]['uid'] for folder in all_folders + all_restore_folders)
    all_dashboards = get_all_dashboards(backup_url, backup_headers, folders_to_include=folders_to_include, folders_to_exclude=folders_to_exclude)
    all_library_panels = get_all_library_panels(backup_url, backup_headers)
    if folders_to_exclude is None or 'General' not in folders_to_exclude:
        # edge case for general folder. The uid is empty string.
        valid_folder_uids.add('')

    all_library_panels_filtered = [panel for panel in all_library_panels if panel['folderUid'] in valid_folder_uids]
    (library_panels_created_summary, library_panels_overwrote_summary, dashboards_created_summary, dashboards_overwrote_summary) = _migrate_library_panels_and_dashboards(all_dashboards, all_library_panels_filtered, restore_url, restore_headers, dry_run, overwrite)

    # get the list of snapshots to backup
    all_snapshots = get_all_snapshots(backup_url, backup_headers)
    snapshots_synced_summary = _migrate_snapshots(all_snapshots, restore_url, restore_headers, dry_run)
   
    # get all the annotations
    all_annotations = get_all_annotations(backup_url, backup_headers)
    annotations_synced_summary = _migrate_annotations(all_annotations, restore_url, restore_headers, dry_run)

    dry_run_status = "to be " if dry_run else ""
    output = [
        (Style.IMPORTANT, f"\n\nDry run: {dry_run if dry_run else False}\n"),
        (Style.IMPORTANT, f"Overwrite dashboards, folders, and library panels: {overwrite if overwrite else False}\n"),
    ]

    if len(datasources_created_summary) > 0:
        output.append((Style.SUCCESS, f"\n\nDatasources {dry_run_status}created:"))
        output.append((Style.IMPORTANT, f"\nDatasources were created, make sure to manually input credentials for those datasources in Grafana (if you have to)."))
        output.append((Style.PRIMARY, "\n    " + "\n    ".join(datasources_created_summary)))
    if len(datasources_remapped_summary) > 0:
        output.append((Style.SUCCESS, f"\n\nDatasources {dry_run_status}remapped:"))
        output.append((Style.PRIMARY, "\n    " + "\n    ".join(datasources_remapped_summary)))

    if len(folders_created_summary) > 0:
        output.append((Style.SUCCESS, f"\n\nFolders {dry_run_status}created:"))
        output.append((Style.PRIMARY, "\n    " + "\n    ".join(folders_created_summary)))

    if len(folders_overwrote_summary) > 0:
        output.append((Style.SUCCESS, f"\n\nFolders {dry_run_status}overwrote:"))
        output.append((Style.PRIMARY, "\n    " + "\n    ".join(folders_overwrote_summary)))

    output.append((Style.SUCCESS, f"\n\nLibrary panels {dry_run_status}created:"))
    for folder, panels in library_panels_created_summary.items():
        output.append((Style.PRIMARY, f"\n    {folder}/\n        "))
        output.append((Style.SECONDARY, "\n        ".join(panels)))

    output.append((Style.SUCCESS, f"\n\nLibrary panels {dry_run_status}overwrote:"))
    for folder, panels in library_panels_overwrote_summary.items():
        output.append((Style.PRIMARY, f"\n    {folder}/\n        "))
        output.append((Style.SECONDARY, "\n        ".join(panels)))

    output.append((Style.SUCCESS, f"\n\nDashboards {dry_run_status}created:"))
    for folder, dashboards in dashboards_created_summary.items():
        output.append((Style.PRIMARY, f"\n    {folder}/\n        "))
        output.append((Style.SECONDARY, "\n        ".join(dashboards)))

    output.append((Style.SUCCESS, f"\n\nDashboards {dry_run_status}overwrote:"))
    for folder, dashboards in dashboards_overwrote_summary.items():
        output.append((Style.PRIMARY, f"\n    {folder}/\n        "))
        output.append((Style.SECONDARY, "\n        ".join(dashboards)))

    # TODO: snapshots don't auto update, it creates a new one.
    output.append((Style.SUCCESS, f"\n\nSnapshots {dry_run_status}updated:"))
    for folder, snapshots in snapshots_synced_summary.items():
        output.append((Style.PRIMARY, f"\n    {folder}/\n        "))
        output.append((Style.SECONDARY, "\n        ".join(snapshots)))

    # TODO: annotations don't auto update, it creates a new one.
    output.append((Style.SUCCESS, f"\n\nAnnotations {dry_run_status}updated (by id):"))
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
    folders_overwrote_summary = []

    restore_folder_uids = {restore_content['uid'] for (restore_content, _) in all_restore_folders}
    restore_folder_uids = set()

    for folder in all_folders:
        content_folder_settings, content_folder_permissions = folder
        # create a folder if it does not exist
        if content_folder_settings['uid'] not in restore_folder_uids:
            # Do this check before creation. 
            exists_before = check_folder_exists(restore_url, content_folder_settings, restore_headers)

            if not dry_run:
                is_successful = create_folder(restore_url, content_folder_settings, restore_headers, overwrite)
            else:
                is_successful = True

            # Make sure that it is successful to add it to the summary properly. dry_run just assume it will work.
            if is_successful:
                if exists_before:
                    folders_overwrote_summary.append(content_folder_settings['title'])
                else:
                    folders_created_summary.append(content_folder_settings['title'])


        else:
            logger.warning("Folder %s already exists, skipping", content_folder_settings['title'])
    return folders_created_summary, folders_overwrote_summary


def _migrate_library_panels_and_dashboards(all_dashboards, all_library_panels_filtered, restore_url, restore_headers, dry_run, overwrite):
    library_panels_created_summary = {}
    library_panels_overwrote_summary = {}
    dashboards_created_summary = {}
    dashboards_overwrote_summary = {}

    # only update the library panels that are not included / excluded.
    for library_panel in all_library_panels_filtered:
        exists_before = check_library_panel_exists(restore_url, library_panel, restore_headers)

        library_panel['id'] = None
        if not dry_run:
            # in create_library_panel, it does the patch if the library panel already exists.
            is_successful = create_library_panel(restore_url, library_panel, restore_headers, overwrite)
        else:
            is_successful = True

        if is_successful:
            panel_folder_name = library_panel['meta']['folderName']
            if exists_before:
                if panel_folder_name not in library_panels_overwrote_summary:
                    library_panels_overwrote_summary[panel_folder_name] = set()
                library_panels_overwrote_summary[panel_folder_name].add(library_panel['name'])
            else:
                if panel_folder_name not in library_panels_created_summary:
                    library_panels_created_summary[panel_folder_name] = set()
                library_panels_created_summary[panel_folder_name].add(library_panel['name'])
        

    # we don't backup provisioned dashboards, so we don't need to restore them
    for dashboard in all_dashboards:
        exists_before = check_dashboard_exists(restore_url, dashboard, restore_headers)

        # Skipping making/updating dashboard if the library panel it relies on is not being updated.

        dashboard['dashboard']['id'] = None
        # Overwrite takes care of delete & create.
        if not dry_run:
            # there is a weird edge case where if the version is the same, it will overwrite even if false.
            # so if the uid are the same, then without overwrite, it will overwrite if the version is the same.
            # this logic doesn't apply to library panel since it is handled via PATCH.
            if exists_before and not overwrite:
                dashboard_title = dashboard['dashboard'].get('title', '')
                print_styled_text([
                    (Style.WARNING, f'Create dashboard {dashboard_title}: '),
                    (Style.ERROR, 'FAILURE (dashboard already exists. Enable --overwrite)')
                ])
                is_successful = False
            else:
                is_successful = create_dashboard(restore_url, dashboard, restore_headers, overwrite)
        else:
            is_successful = True

        if is_successful:
            folder_title = dashboard['meta']['folderTitle']
            if exists_before:
                if folder_title not in dashboards_overwrote_summary:
                    dashboards_overwrote_summary[folder_title] = []
                dashboards_overwrote_summary[folder_title].append(dashboard['dashboard']['title'])
            else:
                if folder_title not in dashboards_created_summary:
                    dashboards_created_summary[folder_title] = []
                dashboards_created_summary[folder_title].append(dashboard['dashboard']['title'])

    return (library_panels_created_summary, library_panels_overwrote_summary, dashboards_created_summary, dashboards_overwrote_summary)


def _get_all_library_panels_uids_from_dashboards(all_dashboards):
    library_panels_uids_to_update = set()
    for dashboard in all_dashboards:
        if ('dashboard' not in dashboard) or ('panels' not in dashboard['dashboard']):
            continue

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
