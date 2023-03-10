import json
from knack.log import get_logger
from .dashboardApi import send_grafana_post

logger = get_logger(__name__)


def create_datasource(grafana_url, file_path, http_headers):
    with open(file_path, 'r', encoding="utf8") as f:
        data = f.read()

    datasource = json.loads(data)
    result = _create_datasource(json.dumps(datasource), grafana_url, http_post_headers=http_headers)
    logger.warning("Create datasource \"%s\". %s", datasource['name'], "SUCCESS" if result[0] == 200 else "FAILURE")
    logger.info("status: %s, msg: %s", result[0], result[1])


def _create_datasource(payload, grafana_url, http_post_headers):
    return send_grafana_post('{0}/api/datasources'.format(grafana_url), payload, http_post_headers)
