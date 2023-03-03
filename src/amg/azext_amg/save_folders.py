import os
from knack.log import get_logger
from .dashboardApi import search_folders, get_folder, get_folder_permissions
from .commons import print_horizontal_line, save_json

logger = get_logger(__name__)


def save_folders(grafana_url, backup_dir, timestamp, http_headers):
    folder_path = '{0}/folders/{1}'.format(backup_dir, timestamp)
    log_file = 'folders_{0}.txt'.format(timestamp)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    folders = get_all_folders_in_grafana(grafana_url, http_get_headers=http_headers, verify_ssl=None, client_cert=None, debug=None)
    print_horizontal_line()
    get_individual_folder_setting_and_save(folders, folder_path, log_file, grafana_url, http_get_headers=http_headers, verify_ssl=None, client_cert=None, debug=None, pretty_print=None, uid_support=True)
    print_horizontal_line()


def get_all_folders_in_grafana(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    status_and_content_of_all_folders = search_folders(grafana_url, http_get_headers, verify_ssl, client_cert, debug)
    status = status_and_content_of_all_folders[0]
    content = status_and_content_of_all_folders[1]
    if status == 200:
        folders = content
        logger.info("There are %s folders:", len(content))
        for folder in folders:
            logger.info("name: %s", folder['title'])
        return folders
    logger.warning("Get folders failed, status: %s, msg: %s", status, content)
    return []


def save_folder_setting(folder_name, file_name, folder_settings, folder_permissions, folder_path, pretty_print):
    file_path = save_json(file_name, folder_settings, folder_path, 'folder', pretty_print)
    logger.warning("Folder:%s are saved to %s", folder_name, file_path)
    # NOTICE: The 'folder_permission' file extension had the 's' removed to work with the magical dict logic in restore.py...
    file_path = save_json(file_name, folder_permissions, folder_path, 'folder_permission', pretty_print)
    logger.warning("Folder permissions:%s are saved to %s", folder_name, file_path)


def get_individual_folder_setting_and_save(folders, folder_path, log_file, grafana_url, http_get_headers, verify_ssl, client_cert, debug, pretty_print, uid_support):
    file_path = folder_path + '/' + log_file
    with open("{0}".format(file_path), 'w+', encoding="utf8") as f:
        for folder in folders:
            if uid_support:
                folder_uri = "uid/{0}".format(folder['uid'])
            else:
                folder_uri = folder['uri']

            (status_folder_settings, content_folder_settings) = get_folder(folder['uid'], grafana_url, http_get_headers, verify_ssl, client_cert, debug)
            (status_folder_permissions, content_folder_permissions) = get_folder_permissions(folder['uid'], grafana_url, http_get_headers, verify_ssl, client_cert, debug)

            if status_folder_settings == 200 and status_folder_permissions == 200:
                save_folder_setting(
                    folder['title'],
                    folder_uri,
                    content_folder_settings,
                    content_folder_permissions,
                    folder_path,
                    pretty_print
                )
                f.write('{0}\t{1}\n'.format(folder_uri, folder['title']))
