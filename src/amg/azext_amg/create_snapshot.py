import json
from knack.log import get_logger
from .dashboardApi import send_grafana_post

logger = get_logger(__name__)


def create_snapshot(grafana_url, file_path, http_headers):
    with open(file_path, 'r', encoding="utf8") as f:
        data = f.read()

    snapshot = json.loads(data)
    try:
        snapshot['name'] = snapshot['dashboard']['title']
    except KeyError:
        snapshot['name'] = "Untitled Snapshot"

    (status, content) = _create_snapshot(json.dumps(snapshot), grafana_url, http_post_headers=http_headers)
    logger.warning("Create snapshot \"%s\". %s", snapshot['name'], "SUCCESS" if status == 200 else "FAILURE")
    logger.info("status: %s, msg: %s", status, content)


def _create_snapshot(payload, grafana_url, http_post_headers):
    return send_grafana_post('{0}/api/snapshots'.format(grafana_url), payload, http_post_headers)
