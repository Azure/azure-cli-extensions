import json
from knack.log import get_logger
from .dashboardApi import get_folder_id, send_grafana_post

logger = get_logger(__name__)


def create_dashboard(grafana_url, file_path, http_headers):
    with open(file_path, 'r', encoding="utf8") as f:
        data = f.read()

    content = json.loads(data)
    content['dashboard']['id'] = None

    payload = {
        'dashboard': content['dashboard'],
        'folderId': get_folder_id(content, grafana_url, http_post_headers=http_headers),
        'overwrite': True
    }

    result = _create_dashboard(json.dumps(payload), grafana_url, http_post_headers=http_headers)
    dashboard_title = content['dashboard'].get('title', '')
    logger.warning("Create dashboard \"%s\". %s", dashboard_title, "SUCCESS" if result[0] == 200 else "FAILURE")
    logger.info("status: %s, msg: %s", result[0], result[1])


def _create_dashboard(payload, grafana_url, http_post_headers):
    return send_grafana_post('{0}/api/dashboards/db'.format(grafana_url), payload, http_post_headers)
