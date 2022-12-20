import re
import json
import requests
from knack.log import get_logger
from .commons import log_response

logger = get_logger(__name__)


def search_dashboard(page, limit, grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    url = '{0}/api/search/?type=dash-db&limit={1}&page={2}'.format(grafana_url, limit, page)
    logger.info("search dashboard in grafana: %s", url)
    return send_grafana_get(url, http_get_headers, verify_ssl, client_cert, debug)


def get_dashboard(board_uri, grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    url = '{0}/api/dashboards/{1}'.format(grafana_url, board_uri)
    logger.info("query dashboard uri: %s", url)
    (status_code, content) = send_grafana_get(url, http_get_headers, verify_ssl, client_cert, debug)
    return (status_code, content)


def search_annotations(grafana_url, ts_from, ts_to, http_get_headers, verify_ssl, client_cert, debug):
    # there is two types of annotations
    # annotation: are user created, custom ones and can be managed via the api
    # alert: are created by Grafana itself, can NOT be managed by the api
    url = '{0}/api/annotations?type=annotation&limit=5000&from={1}&to={2}'.format(grafana_url, ts_from, ts_to)
    (status_code, content) = send_grafana_get(url, http_get_headers, verify_ssl, client_cert, debug)
    return (status_code, content)


def search_alert_channels(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    url = '{0}/api/alert-notifications'.format(grafana_url)
    logger.info("search alert channels in grafana: %s", url)
    return send_grafana_get(url, http_get_headers, verify_ssl, client_cert, debug)


def create_alert_channel(payload, grafana_url, http_post_headers, verify_ssl, client_cert, debug):
    return send_grafana_post('{0}/api/alert-notifications'.format(grafana_url), payload, http_post_headers, verify_ssl,
                             client_cert, debug)


def delete_alert_channel_by_uid(uid, grafana_url, http_post_headers):
    r = requests.delete('{0}/api/alert-notifications/uid/{1}'.format(grafana_url, uid), headers=http_post_headers)
    return int(r.status_code)


def delete_alert_channel_by_id(id_, grafana_url, http_post_headers):
    r = requests.delete('{0}/api/alert-notifications/{1}'.format(grafana_url, id_), headers=http_post_headers)
    return int(r.status_code)


def search_alerts(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    url = '{0}/api/alerts'.format(grafana_url)
    (status_code, content) = send_grafana_get(url, http_get_headers, verify_ssl, client_cert, debug)
    return (status_code, content)


def pause_alert(id_, grafana_url, http_post_headers, verify_ssl, client_cert, debug):
    url = '{0}/api/alerts/{1}/pause'.format(grafana_url, id_)
    payload = '{ "paused": true }'
    (status_code, content) = send_grafana_post(url, payload, http_post_headers, verify_ssl, client_cert, debug)
    return (status_code, content)


def unpause_alert(id_, grafana_url, http_post_headers, verify_ssl, client_cert, debug):
    url = '{0}/api/alerts/{1}/pause'.format(grafana_url, id_)
    payload = '{ "paused": false }'
    (status_code, content) = send_grafana_post(url, payload, http_post_headers, verify_ssl, client_cert, debug)
    return (status_code, content)


def delete_folder(uid, grafana_url, http_post_headers):
    r = requests.delete('{0}/api/folders/{1}'.format(grafana_url, uid), headers=http_post_headers)
    return int(r.status_code)


def delete_snapshot(key, grafana_url, http_post_headers):
    r = requests.delete('{0}/api/snapshots/{1}'.format(grafana_url, key), headers=http_post_headers)
    return int(r.status_code)


def delete_dashboard_by_uid(uid, grafana_url, http_post_headers):
    r = requests.delete('{0}/api/dashboards/uid/{1}'.format(grafana_url, uid), headers=http_post_headers)
    return int(r.status_code)


def delete_dashboard_by_slug(slug, grafana_url, http_post_headers):
    r = requests.delete('{0}/api/dashboards/db/{1}'.format(grafana_url, slug), headers=http_post_headers)
    return int(r.status_code)


def search_datasource(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    logger.info("search datasources in grafana:")
    return send_grafana_get('{0}/api/datasources'.format(grafana_url), http_get_headers, verify_ssl, client_cert, debug)


def search_snapshot(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    logger.info("search snapshots in grafana:")
    return send_grafana_get('{0}/api/dashboard/snapshots'.format(grafana_url), http_get_headers, verify_ssl, client_cert, debug)


def get_snapshot(key, grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    url = '{0}/api/snapshots/{1}'.format(grafana_url, key)
    (status_code, content) = send_grafana_get(url, http_get_headers, verify_ssl, client_cert, debug)
    return (status_code, content)


def search_folders(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    logger.info("search folder in grafana:")
    return send_grafana_get('{0}/api/search/?type=dash-folder'.format(grafana_url), http_get_headers, verify_ssl,
                            client_cert, debug)


def get_folder(uid, grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    (status_code, content) = send_grafana_get('{0}/api/folders/{1}'.format(grafana_url, uid), http_get_headers,
                                              verify_ssl, client_cert, debug)
    logger.info("query folder:%s, status:%s", uid, status_code)
    return (status_code, content)


def get_folder_permissions(uid, grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    (status_code, content) = send_grafana_get('{0}/api/folders/{1}/permissions'.format(grafana_url, uid), http_get_headers,
                                              verify_ssl, client_cert, debug)
    logger.info("query folder permissions:%s, status:%s", uid, status_code)
    return (status_code, content)


def update_folder_permissions(payload, grafana_url, http_post_headers, verify_ssl, client_cert, debug):
    items = json.dumps({'items': payload})
    return send_grafana_post('{0}/api/folders/{1}/permissions'.format(grafana_url, payload[0]['uid']), items, http_post_headers, verify_ssl, client_cert,
                             debug)


def get_folder_id(dashboard, grafana_url, http_post_headers, verify_ssl, client_cert, debug):
    folder_uid = ""
    try:
        folder_uid = dashboard['meta']['folderUid']
    except KeyError:
        matches = re.search('dashboards/f/(.*)/.*', dashboard['meta']['folderUrl'])
        if matches is not None:
            folder_uid = matches.group(1)
        else:
            folder_uid = '0'

    if folder_uid != "":
        logger.debug("debug: quering with uid %s", folder_uid)
        response = get_folder(folder_uid, grafana_url, http_post_headers, verify_ssl, client_cert, debug)
        if isinstance(response[1], dict):
            folder_data = response[1]
        else:
            folder_data = json.loads(response[1])

        try:
            return folder_data['id']
        except KeyError:
            return 0
    else:
        return 0


def get_dashboard_versions(dashboard_id, grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    (status_code, content) = send_grafana_get('{0}/api/dashboards/id/{1}/versions'.format(grafana_url, dashboard_id), http_get_headers,
                                              verify_ssl, client_cert, debug)
    logger.info("query dashboard versions: %s, status: %s", dashboard_id, status_code)
    return (status_code, content)


def get_version(dashboard_id, version_number, grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    (status_code, content) = send_grafana_get('{0}/api/dashboards/id/{1}/versions/{2}'.format(grafana_url, dashboard_id, version_number), http_get_headers,
                                              verify_ssl, client_cert, debug)
    logger.info("query dashboard %s version %s, status: %s", dashboard_id, version_number, status_code)
    return (status_code, content)


def send_grafana_get(url, http_get_headers, verify_ssl, client_cert, debug):

    r = requests.get(url, headers=http_get_headers, verify=verify_ssl, cert=client_cert)
    if debug:
        log_response(r)
    return (r.status_code, r.json())


def send_grafana_post(url, json_payload, http_post_headers, verify_ssl=False, client_cert=None, debug=True):
    r = requests.post(url, headers=http_post_headers, data=json_payload, verify=verify_ssl, cert=client_cert)
    if debug:
        log_response(r)
    try:
        return (r.status_code, r.json())
    except ValueError:
        return (r.status_code, r.text)


def send_grafana_put(url, json_payload, http_post_headers, verify_ssl=False, client_cert=None, debug=True):
    r = requests.put(url, headers=http_post_headers, data=json_payload, verify=verify_ssl, cert=client_cert)
    if debug:
        log_response(r)
    return (r.status_code, r.json())
