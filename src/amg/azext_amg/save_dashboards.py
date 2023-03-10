import os
from knack.log import get_logger
from .dashboardApi import search_dashboard, get_dashboard
from .commons import print_horizontal_line, save_json

logger = get_logger(__name__)


def save_dashboards(grafana_url, backup_dir, timestamp, http_headers, **kwargs):
    folder_path = '{0}/dashboards/{1}'.format(backup_dir, timestamp)
    log_file = 'dashboards_{0}.txt'.format(timestamp)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    _save_dashboards(folder_path, log_file, grafana_url, http_get_headers=http_headers, **kwargs)


def get_all_dashboards_in_grafana(page, limit, grafana_url, http_get_headers):
    (status, content) = search_dashboard(page,
                                         limit,
                                         grafana_url,
                                         http_get_headers)
    if status == 200:
        dashboards = content
        logger.info("There are %s dashboards:", len(dashboards))
        for board in dashboards:
            logger.info('name: %s', board['title'])
        return dashboards
    logger.warning("Get dashboards FAILED, status: %s, msg: %s", status, content)
    return []


def save_dashboard_setting(dashboard_name, file_name, dashboard_settings, folder_path):
    file_path = save_json(file_name, dashboard_settings, folder_path, 'dashboard')
    logger.warning("Dashboard: \"%s\" is saved", dashboard_name)
    logger.info("    -> %s", file_path)


def get_individual_dashboard_setting_and_save(dashboards, folder_path, log_file, grafana_url, http_get_headers):
    file_path = folder_path + '/' + log_file
    if dashboards:
        with open("{0}".format(file_path), 'w', encoding="utf8") as f:
            for board in dashboards:
                board_uri = "uid/{0}".format(board['uid'])

                (status, content) = get_dashboard(board_uri, grafana_url, http_get_headers)
                if status == 200:
                    save_dashboard_setting(
                        board['title'],
                        board_uri,
                        content,
                        folder_path)
                    f.write('{0}\t{1}\n'.format(board_uri, board['title']))


def _save_dashboards(folder_path, log_file, grafana_url, http_get_headers, **kwargs):
    limit = 5000  # limit is 5000 above V6.2+
    current_page = 1
    while True:
        dashboards = get_all_dashboards_in_grafana(current_page, limit, grafana_url, http_get_headers)

        # only include what users want
        folders_to_include = kwargs.get('folders_to_include')
        folders_to_exclude = kwargs.get('folders_to_exclude')
        if folders_to_include:
            folders_to_include = [f.lower() for f in folders_to_include]
            dashboards = [d for d in dashboards if d.get('folderTitle', '').lower() in folders_to_include]
        if folders_to_exclude:
            folders_to_exclude = [f.lower() for f in folders_to_exclude]
            dashboards = [d for d in dashboards if d.get('folderTitle', '').lower() not in folders_to_exclude]

        print_horizontal_line()
        if len(dashboards) == 0:
            break
        current_page += 1
        get_individual_dashboard_setting_and_save(dashboards, folder_path, log_file, grafana_url, http_get_headers)
        print_horizontal_line()
