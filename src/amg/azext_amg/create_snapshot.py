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

    (status, content) = _create_snapshot(json.dumps(snapshot), grafana_url, http_post_headers=http_headers, verify_ssl=None, client_cert=None, debug=None)
    if status == 200:
        logger.info("create snapshot: %s, status: %s, msg: %s", snapshot['name'], status, content)
    else:
        logger.info("creating snapshot %s failed with status %s", snapshot['name'], status)


def _create_snapshot(payload, grafana_url, http_post_headers, verify_ssl, client_cert, debug):
    return send_grafana_post('{0}/api/snapshots'.format(grafana_url), payload, http_post_headers, verify_ssl,
                             client_cert, debug)
