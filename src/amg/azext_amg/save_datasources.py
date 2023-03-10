import os
from knack.log import get_logger
from .dashboardApi import search_datasource
from .commons import print_horizontal_line, save_json

logger = get_logger(__name__)


def save_datasources(grafana_url, backup_dir, timestamp, http_headers, **kwargs):
    folder_path = '{0}/datasources/{1}'.format(backup_dir, timestamp)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    get_all_datasources_and_save(folder_path, grafana_url, http_get_headers=http_headers)
    print_horizontal_line()


def save_datasource(file_name, datasource_setting, folder_path):
    file_path = save_json(file_name, datasource_setting, folder_path, 'datasource')
    logger.warning("Datasource: \"%s\" is saved", datasource_setting['name'])
    logger.info("    -> %s", file_path)


def get_all_datasources_and_save(folder_path, grafana_url, http_get_headers):
    status_code_and_content = search_datasource(grafana_url, http_get_headers)
    if status_code_and_content[0] == 200:
        datasources = status_code_and_content[1]
        logger.info("There are %s datasources:", len(datasources))
        for datasource in datasources:
            logger.info(datasource)
            datasource_name = datasource['uid']
            save_datasource(datasource_name, datasource, folder_path)
    else:
        logger.info("Query datasource FAILED, status: %s, msg: %s", status_code_and_content[0],
                    status_code_and_content[1])
