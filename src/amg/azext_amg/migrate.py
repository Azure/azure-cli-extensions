# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from azure.cli.core.style import print_styled_text, Style
from azure.cli.core.azclierror import ArgumentUsageError

from .restore import (create_dashboard, create_folder, create_library_panel, create_snapshot, create_annotation,
                      create_datasource, set_uid_mapping, check_folder_exists, check_library_panel_exists,
                      check_dashboard_exists, check_snapshot_exists, check_annotation_exists_and_return_id)
from .backup_core import (get_all_dashboards, get_all_library_panels, get_all_snapshots, get_all_folders,
                          get_all_annotations, get_all_datasources)

logger = get_logger(__name__)


def migrate(backup_url, backup_headers, restore_url, restore_headers, dry_run,
            overwrite, folders_to_include=None, folders_to_exclude=None):
    # pylint: disable=too-many-locals
    folders_to_include_set = set()
    folders_to_exclude_set = set()

    if folders_to_include:
        folders_to_include_set = set(s.lower() for s in folders_to_include)
    if folders_to_exclude:
        folders_to_exclude_set = set(s.lower() for s in folders_to_exclude)
    if folders_to_include_set.intersection(folders_to_exclude_set):
        raise ArgumentUsageError("Folders to include and exclude cannot have the same folder")

    # get all datasources to be backed up
    all_source_datasources = get_all_datasources(backup_url, backup_headers)
    all_destination_datasources = get_all_datasources(restore_url, restore_headers)
    (datasources_created_summary, datasources_remapped_summary) = _migrate_datasources(
        all_source_datasources, all_destination_datasources, restore_url, restore_headers, dry_run)

    all_source_folders = get_all_folders(backup_url,
                                         backup_headers,
                                         folders_to_include=folders_to_include,
                                         folders_to_exclude=folders_to_exclude)
    all_destination_folders = get_all_folders(restore_url,
                                              restore_headers,
                                              folders_to_include=folders_to_include,
                                              folders_to_exclude=folders_to_exclude)
    (folders_created_summary, folders_overwrote_summary) = _migrate_folders(
        all_source_folders, all_destination_folders, restore_url, restore_headers, dry_run, overwrite)

    valid_folder_uids = set(folder[0]['uid'] for folder in all_source_folders + all_destination_folders)
    all_source_dashboards = get_all_dashboards(backup_url,
                                               backup_headers,
                                               folders_to_include=folders_to_include,
                                               folders_to_exclude=folders_to_exclude)
    all_source_lib_panels = get_all_library_panels(backup_url, backup_headers)

    if 'general' in folders_to_include_set or 'general' not in folders_to_exclude_set:
        valid_folder_uids.add('')

    # needs to be meta since in Grafana 8, the folderUid is in the meta.
    all_lib_panels_filtered = [p for p in all_source_lib_panels if p['meta']['folderUid'] in valid_folder_uids]
    (library_panels_created_summary,
     library_panels_overwrote_summary,
     dashboards_created_summary,
     dashboards_overwrote_summary) = _migrate_library_panels_and_dashboards(all_source_dashboards,
                                                                            all_lib_panels_filtered,
                                                                            restore_url,
                                                                            restore_headers,
                                                                            dry_run,
                                                                            overwrite)

    # get the list of snapshots to backup
    all_source_snapshots = get_all_snapshots(backup_url, backup_headers)
    snapshots_synced_summary, snapshots_overwrote_summary = _migrate_snapshots(
        all_source_snapshots, restore_url, restore_headers, dry_run, overwrite)

    # get all the annotations (ONLY up the PAST 13 months)
    all_source_annotations = get_all_annotations(backup_url, backup_headers)
    annotations_synced_summary, annotations_overwrote_summary = _migrate_annotations(
        all_source_annotations, restore_url, restore_headers, dry_run, overwrite)

    dry_run_status = "to be " if dry_run else ""
    output = [
        (Style.IMPORTANT, f"\n\nDry run: {dry_run}\n"),
        (Style.IMPORTANT, f"Overwrite dashboards, folders, and library panels: {overwrite}\n"),
    ]

    append_summary(output, dry_run_status + "created", "Datasources", datasources_created_summary,
                   "\nDatasources were created, credentials ARE NOT migrated.")
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
        postprocessed_summary = [(a, b[:max_text_length] + "...") if len(b) >
                                 max_text_length else (a, b) for a, b in annotations_summary]
        output.append((Style.PRIMARY, "\n    " +
                       "\n    ".join([f"id: {a}, text: {b}" for a, b in postprocessed_summary])))


def _migrate_datasources(all_source_datasources, all_destination_datasources, restore_url, restore_headers, dry_run):
    datasources_created_summary = []
    datasources_remapped_summary = []

    # since in our remapping, we use the name and type to check if it is the same datasource.
    restore_datasources_names = {(ds['name'], ds['type']) for ds in all_destination_datasources}

    for datasource in all_source_datasources:
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
    set_uid_mapping(all_source_datasources, all_destination_datasources)

    return (datasources_created_summary, datasources_remapped_summary)


def _migrate_folders(all_source_folders, all_destination_folders, restore_url, restore_headers, dry_run, overwrite):
    folders_created_summary = []
    folders_overwrote_summary = []

    restore_folder_uids = {restore_content['uid'] for (restore_content, _) in all_destination_folders}
    restore_folder_uids = set()

    for folder in all_source_folders:
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

        update_summary(exists_before,
                       content_folder_settings['title'],
                       folders_created_summary,
                       folders_overwrote_summary)

    return folders_created_summary, folders_overwrote_summary


def _migrate_library_panels_and_dashboards(all_source_dashboards, all_library_panels_filtered, restore_url,
                                           restore_headers, dry_run, overwrite):
    library_panels_created_summary = {}
    library_panels_overwrote_summary = {}
    dashboards_created_summary = {}
    dashboards_overwrote_summary = {}

    created_library_panels = set()
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

        created_library_panels.add(library_panel['uid'])
        panel_folder_name = library_panel['meta']['folderName']
        update_summary_dict(exists_before,
                            panel_folder_name,
                            library_panel['name'],
                            library_panels_created_summary,
                            library_panels_overwrote_summary)

    # we don't backup provisioned dashboards, so we don't need to restore them
    for dashboard in all_source_dashboards:
        exists_before = check_dashboard_exists(restore_url, dashboard["dashboard"]["uid"], restore_headers)
        dashboard_title = dashboard['dashboard'].get('title', '')

        # Skipping making/updating dashboard if the library panel it relies on is not being updated.
        panel_uids = {p["libraryPanel"]["uid"] for p in dashboard["dashboard"]["panels"] if "libraryPanel" in p}
        if not panel_uids.issubset(created_library_panels):
            # all the panels that are created are in the created_library_panels set, so if the panel is not in the set,
            # then it is not created and we should skip the dashboard.
            print_styled_text([
                (Style.WARNING, f'Create dashboard {dashboard_title}: '),
                (Style.ERROR, 'FAILURE (skipped because library panel is not created)')
            ])
            continue

        dashboard['dashboard']['id'] = None
        # Overwrite takes care of delete & create.
        is_successful = True
        if not dry_run:
            # there is a weird edge case where if the version is the same, it will overwrite even if false.
            # so if the uid are the same, then without overwrite, it will overwrite if the version is the same.
            # this logic doesn't apply to library panel since it is handled via PATCH.
            if exists_before and not overwrite:
                error_msg = '(dashboard already exists. Please enable --overwrite if you want to overwrite dashboard)'
                print_styled_text([
                    (Style.WARNING, f'Create dashboard {dashboard_title}: '),
                    (Style.ERROR, f'FAILURE {error_msg}')
                ])
                is_successful = False
            else:
                is_successful = create_dashboard(restore_url, dashboard, restore_headers, overwrite)

        if not is_successful:
            continue

        folder_title = dashboard['meta']['folderTitle']
        update_summary_dict(exists_before,
                            folder_title,
                            dashboard['dashboard']['title'],
                            dashboards_created_summary,
                            dashboards_overwrote_summary)

    return (library_panels_created_summary, library_panels_overwrote_summary,
            dashboards_created_summary, dashboards_overwrote_summary)


def _migrate_snapshots(all_source_snapshots, restore_url, restore_headers, dry_run, overwrite):
    snapshots_synced_summary = {}
    snapshots_overwrote_summary = {}
    for snapshot_key, snapshot in all_source_snapshots:
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
        update_summary_dict(exists_before,
                            snapshot_folder_title,
                            snapshot_name,
                            snapshots_synced_summary,
                            snapshots_overwrote_summary)

    return snapshots_synced_summary, snapshots_overwrote_summary


def _migrate_annotations(all_source_annotations, restore_url, restore_headers, dry_run, overwrite):
    annotations_synced_summary = []
    annotations_overwrote_summary = []
    for annotation in all_source_annotations:
        exists_before, _ = check_annotation_exists_and_return_id(restore_url, annotation, restore_headers)

        is_successful = True
        if not dry_run:
            is_successful = create_annotation(restore_url, annotation, restore_headers, overwrite)

        if not is_successful:
            continue

        update_summary(exists_before,
                       (str(annotation['id']), annotation['text']),
                       annotations_synced_summary,
                       annotations_overwrote_summary)

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
