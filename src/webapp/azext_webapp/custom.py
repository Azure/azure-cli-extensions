# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function
from knack.log import get_logger
from knack.util import CLIError
from azure.cli.command_modules.appservice.custom import (
    show_webapp,
    _get_site_credential,
    _get_scm_url)
logger = get_logger(__name__)


def start_scan(cmd, resource_group_name, name, timeout="", slot=None):
    webapp = show_webapp(cmd, resource_group_name, name, slot)
    is_linux = webapp.reserved
    if not is_linux:
        raise CLIError("Only Linux App Service Plans supported, Found a Windows App Service Plan")

    import requests
    user_name, password = _get_site_credential(cmd.cli_ctx, resource_group_name, name, slot)
    scm_url = _get_scm_url(cmd, resource_group_name, name, slot)
    start_scan_url = scm_url + '/api/scan/start?timeout=' + timeout

    import urllib3
    authorization = urllib3.util.make_headers(basic_auth='{0}:{1}'.format(user_name, password))
    headers = authorization
    headers['content-type'] = 'application/octet-stream'

    response = requests.get(start_scan_url, headers=authorization)
    return response.json()


def get_scan_result(cmd, resource_group_name, name, scan_id, slot=None):
    webapp = show_webapp(cmd, resource_group_name, name, slot)
    is_linux = webapp.reserved
    if not is_linux:
        raise CLIError("Only Linux App Service Plans supported, Found a Windows App Service Plan")

    import requests
    user_name, password = _get_site_credential(cmd.cli_ctx, resource_group_name, name, slot)
    scm_url = _get_scm_url(cmd, resource_group_name, name, slot)
    scan_result_url = scm_url + '/api/scan/' + scan_id + '/result'

    import urllib3
    authorization = urllib3.util.make_headers(basic_auth='{0}:{1}'.format(user_name, password))
    headers = authorization
    headers['content-type'] = 'application/octet-stream'

    response = requests.get(scan_result_url, headers=authorization)

    return response.json()


def track_scan(cmd, resource_group_name, name, scan_id, slot=None):
    webapp = show_webapp(cmd, resource_group_name, name, slot)
    is_linux = webapp.reserved
    if not is_linux:
        raise CLIError("Only Linux App Service Plans supported, Found a Windows App Service Plan")

    import requests
    user_name, password = _get_site_credential(cmd.cli_ctx, resource_group_name, name, slot)
    scm_url = _get_scm_url(cmd, resource_group_name, name, slot)
    scan_result_url = scm_url + '/api/scan/' + scan_id + '/track'

    import urllib3
    authorization = urllib3.util.make_headers(basic_auth='{0}:{1}'.format(user_name, password))
    headers = authorization
    headers['content-type'] = 'application/octet-stream'

    response = requests.get(scan_result_url, headers=authorization)

    return response.json()


def get_all_scan_result(cmd, resource_group_name, name, slot=None):
    webapp = show_webapp(cmd, resource_group_name, name, slot)
    is_linux = webapp.reserved
    if not is_linux:
        raise CLIError("Only Linux App Service Plans supported, Found a Windows App Service Plan")

    import requests
    user_name, password = _get_site_credential(cmd.cli_ctx, resource_group_name, name, slot)
    scm_url = _get_scm_url(cmd, resource_group_name, name, slot)
    scan_result_url = scm_url + '/api/scan/results'

    import urllib3
    authorization = urllib3.util.make_headers(basic_auth='{0}:{1}'.format(user_name, password))
    headers = authorization
    headers['content-type'] = 'application/octet-stream'

    response = requests.get(scan_result_url, headers=authorization)

    return response.json()


def stop_scan(cmd, resource_group_name, name, slot=None):
    webapp = show_webapp(cmd, resource_group_name, name, slot)
    is_linux = webapp.reserved
    if not is_linux:
        raise CLIError("Only Linux App Service Plans supported, Found a Windows App Service Plan")

    import requests
    user_name, password = _get_site_credential(cmd.cli_ctx, resource_group_name, name, slot)
    scm_url = _get_scm_url(cmd, resource_group_name, name, slot)
    stop_scan_url = scm_url + '/api/scan/stop'

    import urllib3
    authorization = urllib3.util.make_headers(basic_auth='{0}:{1}'.format(user_name, password))
    headers = authorization
    headers['content-type'] = 'application/octet-stream'

    requests.delete(stop_scan_url, headers=authorization)
