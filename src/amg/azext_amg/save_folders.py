import os
from knack.log import get_logger
from .dashboardApi import search_folders, get_folder, get_folder_permissions
from .commons import print_horizontal_line, save_json

logger = get_logger(__name__)


def save_folders(grafana_url, backup_dir, timestamp, http_headers, **kwargs):
    folder_path = '{0}/folders/{1}'.format(backup_dir, timestamp)
    log_file = 'folders_{0}.txt'.format(timestamp)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    folders = get_all_folders_in_grafana(grafana_url, http_get_headers=http_headers)

    # only include what users want
    folders_to_include = kwargs.get('folders_to_include')
    folders_to_exclude = kwargs.get('folders_to_exclude')
    if folders_to_include:
        folders_to_include = [f.lower() for f in folders_to_include]
        folders = [f for f in folders if f.get('title', '').lower() in folders_to_include]
    if folders_to_exclude:
        folders_to_exclude = [f.lower() for f in folders_to_exclude]
        folders = [f for f in folders if f.get('title', '').lower() not in folders_to_exclude]

    print_horizontal_line()
    get_individual_folder_setting_and_save(folders, folder_path, log_file, grafana_url, http_get_headers=http_headers)
    print_horizontal_line()


def get_all_folders_in_grafana(grafana_url, http_get_headers):
    status_and_content_of_all_folders = search_folders(grafana_url, http_get_headers)
    status = status_and_content_of_all_folders[0]
    content = status_and_content_of_all_folders[1]
    if status == 200:
        folders = content
        logger.info("There are %s folders:", len(content))
        for folder in folders:
            logger.info("name: %s", folder['title'])
        return folders
    logger.warning("Get folders FAILED, status: %s, msg: %s", status, content)
    return []


def save_folder_setting(folder_name, file_name, folder_settings, folder_permissions, folder_path):
    file_path = save_json(file_name, folder_settings, folder_path, 'folder')
    logger.warning("Folder: \"%s\" is saved", folder_name)
    logger.info("    -> %s", file_path)
    # NOTICE: The 'folder_permission' file extension had the 's' removed to work with the magical dict logic in restore.py...
    file_path = save_json(file_name, folder_permissions, folder_path, 'folder_permission')
    logger.warning("Folder permissions: %s are saved", folder_name)
    logger.info("    -> %s", file_path)


def get_individual_folder_setting_and_save(folders, folder_path, log_file, grafana_url, http_get_headers):
    file_path = folder_path + '/' + log_file
    with open("{0}".format(file_path), 'w+', encoding="utf8") as f:
        for folder in folders:
            folder_uri = "uid/{0}".format(folder['uid'])

            (status_folder_settings, content_folder_settings) = get_folder(folder['uid'], grafana_url, http_get_headers)
            (status_folder_permissions, content_folder_permissions) = get_folder_permissions(folder['uid'], grafana_url, http_get_headers)

            if status_folder_settings == 200 and status_folder_permissions == 200:
                save_folder_setting(
                    folder['title'],
                    folder_uri,
                    content_folder_settings,
                    content_folder_permissions,
                    folder_path)
                f.write('{0}\t{1}\n'.format(folder_uri, folder['title']))
