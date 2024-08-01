from knack.log import get_logger
from azure.cli.core.style import print_styled_text, Style

from .restore import create_dashboard, create_folder, create_library_panel, create_snapshot, create_annotation, create_datasource, set_uid_mapping, check_folder_exists, check_library_panel_exists, check_dashboard_exists, check_snapshot_exists, check_annotation_exists_and_return_id
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
    snapshots_synced_summary, snapshots_overwrote_summary = _migrate_snapshots(all_snapshots, restore_url, restore_headers, dry_run, overwrite)
   
    # get all the annotations (ONLY up the PAST 13 months)
    all_annotations = get_all_annotations(backup_url, backup_headers)
    annotations_synced_summary, annotations_overwrote_summary = _migrate_annotations(all_annotations, restore_url, restore_headers, dry_run, overwrite)

    dry_run_status = "to be " if dry_run else ""
    output = [
        (Style.IMPORTANT, f"\n\nDry run: {dry_run}\n"),
        (Style.IMPORTANT, f"Overwrite dashboards, folders, and library panels: {overwrite}\n"),
    ]

    append_summary(output, dry_run_status + "created", "Datasources", datasources_created_summary, 
               "\nDatasources were created, make sure to manually input credentials for those datasources in Grafana (if you have to).")
    append_summary(output, dry_run_status + "remapped", "Datasources", datasources_remapped_summary)
    append_summary(output, dry_run_status + "created", "Folders", folders_created_summary)
    append_summary(output, dry_run_status + "overwritten", "Folders", folders_overwrote_summary)

    append_nested_summary(output, dry_run_status + "created", "Library panels", library_panels_created_summary)
    append_nested_summary(output, dry_run_status + "overwritten", "Library panels", library_panels_overwrote_summary)
    append_nested_summary(output, dry_run_status + "created", "Dashboards", dashboards_created_summary)
    append_nested_summary(output, dry_run_status + "overwritten", "Dashboards", dashboards_overwrote_summary)
    append_nested_summary(output, dry_run_status + "created", "Snapshots", snapshots_synced_summary)
    append_nested_summary(output, dry_run_status + "overwritten", "Snapshots", snapshots_overwrote_summary)

    append_annotations_summary(output, dry_run_status + "created", "Annotations", annotations_synced_summary)
    append_annotations_summary(output, dry_run_status + "overwritten", "Annotations", annotations_overwrote_summary)

    print_styled_text(output)


def append_summary(output, status, summary_type, summary_data, important_message=None):
    if len(summary_data) > 0:
        output.append((Style.SUCCESS, f"\n\n{summary_type} {status}:"))
        if important_message:
            output.append((Style.IMPORTANT, important_message))
        output.append((Style.PRIMARY, "\n    " + "\n    ".join(summary_data)))


def append_nested_summary(output, status, summary_type, summary_data):
    output.append((Style.SUCCESS, f"\n\n{summary_type} {status}:"))
    for folder, items in summary_data.items():
        output.append((Style.PRIMARY, f"\n    {folder}/\n        "))
        output.append((Style.SECONDARY, "\n        ".join(items)))


def append_annotations_summary(output, status, summary_type, annotations_summary, max_text_length=50):
    output.append((Style.SUCCESS, f"\n\n{summary_type} {status}:"))
    if len(annotations_summary) > 0:
        postprocessed_summary = [(a, b[:max_text_length] + "...") if len(b) > max_text_length else (a, b) for a, b in annotations_summary]
        output.append((Style.PRIMARY, "\n    " + "\n    ".join([f"id: {a}, text: {b}" for a, b in postprocessed_summary])))


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
            if not dry_run:
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
        content_folder_settings, _ = folder

        if content_folder_settings['uid'] in restore_folder_uids:
            logger.warning("Folder %s already exists, skipping", content_folder_settings['title'])
            continue

        # create a folder if it does not exist
        exists_before = check_folder_exists(restore_url, content_folder_settings, restore_headers)

        is_successful = True
        if not dry_run:
            is_successful = create_folder(restore_url, content_folder_settings, restore_headers, overwrite)

        if not is_successful:
            continue

        # Make sure that it is successful to add it to the summary properly. dry_run just assume it will work.
        if exists_before:
            folders_overwrote_summary.append(content_folder_settings['title'])
        else:
            folders_created_summary.append(content_folder_settings['title'])


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
        is_successful = True
        if not dry_run:
            # in create_library_panel, it does the patch if the library panel already exists.
            is_successful = create_library_panel(restore_url, library_panel, restore_headers, overwrite)

        if not is_successful:
            continue

        panel_folder_name = library_panel['meta']['folderName']
        if exists_before:
            if panel_folder_name not in library_panels_overwrote_summary:
                library_panels_overwrote_summary[panel_folder_name] = []
            library_panels_overwrote_summary[panel_folder_name].append(library_panel['name'])
        else:
            if panel_folder_name not in library_panels_created_summary:
                library_panels_created_summary[panel_folder_name] = []
            library_panels_created_summary[panel_folder_name].append(library_panel['name'])
        

    # we don't backup provisioned dashboards, so we don't need to restore them
    for dashboard in all_dashboards:
        exists_before = check_dashboard_exists(restore_url, dashboard, restore_headers)

        # Skipping making/updating dashboard if the library panel it relies on is not being updated.

        dashboard['dashboard']['id'] = None
        # Overwrite takes care of delete & create.
        is_successful = True
        if not dry_run:
            # there is a weird edge case where if the version is the same, it will overwrite even if false.
            # so if the uid are the same, then without overwrite, it will overwrite if the version is the same.
            # this logic doesn't apply to library panel since it is handled via PATCH.
            if exists_before and not overwrite:
                dashboard_title = dashboard['dashboard'].get('title', '')
                print_styled_text([
                    (Style.WARNING, f'Create dashboard {dashboard_title}: '),
                    (Style.ERROR, 'FAILURE (dashboard already exists. Please enable --overwrite if you want to overwrite the dashboard)')
                ])
                is_successful = False
            else:
                is_successful = create_dashboard(restore_url, dashboard, restore_headers, overwrite)

        if not is_successful:
            continue

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


def _migrate_snapshots(all_snapshots, restore_url, restore_headers, dry_run, overwrite):
    snapshots_synced_summary = {}
    snapshots_overwrote_summary = {}
    for snapshot_key, snapshot in all_snapshots:
        snapshot['key'] = snapshot_key
        exists_before = check_snapshot_exists(restore_url, snapshot['key'], restore_headers)

        try:
            snapshot_name = snapshot['dashboard']['title']
        except KeyError:
            snapshot_name = "Untitled Snapshot"

        is_successful = True
        if not dry_run:
            is_successful = create_snapshot(restore_url, snapshot, restore_headers, overwrite)

        if not is_successful:
            continue

        snapshot_folder_title = snapshot['meta']['folderTitle']
        if exists_before:
            if snapshot_folder_title not in snapshots_overwrote_summary:
                snapshots_overwrote_summary[snapshot_folder_title] = []
            snapshots_overwrote_summary[snapshot_folder_title].append(snapshot_name)
        else:
            if snapshot_folder_title not in snapshots_synced_summary:
                snapshots_synced_summary[snapshot_folder_title] = []
            snapshots_synced_summary[snapshot_folder_title].append(snapshot_name)

    return snapshots_synced_summary, snapshots_overwrote_summary


def _migrate_annotations(all_annotations, restore_url, restore_headers, dry_run, overwrite):
    annotations_synced_summary = []
    annotations_overwrote_summary = []
    for annotation in all_annotations:
        exists_before, _ = check_annotation_exists_and_return_id(restore_url, annotation, restore_headers)

        is_successful = True
        if not dry_run:
            is_successful = create_annotation(restore_url, annotation, restore_headers, overwrite)

        # can do text to get the text, annotations don't have titles.
        # annotations_synced_summary.append(annotation['text'])
        if not is_successful:
            continue

        if exists_before:
            annotations_overwrote_summary.append((str(annotation['id']), annotation['text']))
        else:
            annotations_synced_summary.append((str(annotation['id']), annotation['text']))

    return annotations_synced_summary, annotations_overwrote_summary


def update_summary(exists_before, item, summary_created, summary_overwrote):
    if exists_before:
        summary_overwrote.append(item)
    else:
        summary_created.append(item)

def update_summary_dict(exists_before, key, item, summary_created, summary_overwrote):
    if exists_before:
        if key not in summary_overwrote:
            summary_overwrote[key] = []
        summary_overwrote[key].append(item)
    else:
        if key not in summary_created:
            summary_created[key] = []
        summary_created[key].append(item)
