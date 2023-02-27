import json
from knack.log import get_logger
from .dashboardApi import send_grafana_post

logger = get_logger(__name__)


def create_annotation(grafana_url, file_path, http_headers):
    with open(file_path, 'r', encoding="utf8") as f:
        data = f.read()

    annotation = json.loads(data)
    result = _create_annotation(json.dumps(annotation), grafana_url, http_post_headers=http_headers, verify_ssl=None, client_cert=None, debug=None)
    logger.info("create annotation: %s, status: %s, msg: %s", annotation['id'], result[0], result[1])


def _create_annotation(annotation, grafana_url, http_post_headers, verify_ssl, client_cert, debug):
    url = '{0}/api/annotations'.format(grafana_url)
    return send_grafana_post(url, annotation, http_post_headers, verify_ssl, client_cert, debug)
