# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
    Helpers for requests to Codespaces non-ARM-based APIs
"""

import platform
import requests
from knack.util import CLIError
from knack.log import get_logger
from azure.cli.core import __version__ as az_version

from .version import VERSION

logger = get_logger(__name__)

API_ROOT = "https://online.visualstudio.com/api/v1"


def _get_user_agent_string():
    pv = platform.python_version()
    ps = platform.system()
    pr = platform.release()
    pp = platform.processor()
    pm = platform.machine()
    return f"python/{pv} ({ps}-{pr}-{pm}-{pp}) azure-cli/{az_version} codespaces-extension/{VERSION}"


def assert_status_hook(r, *args, **kwargs):  # pylint: disable=unused-argument
    r.raise_for_status()


def response_logging_hook(response, *args, **kwargs):  # pylint: disable=unused-argument
    logger.debug('Request: %s', response.request.__dict__)
    logger.debug('Response: %s', response.__dict__)


class NoStripAuthSession(requests.Session):
    # Override the default behavior of stripping the Authorization header on redirects
    # see https://github.com/psf/requests/blob/9ed5db8ed28e816b597dafd328b342ec95466afa/requests/sessions.py#L119-L139
    def should_strip_auth(self, old_url, new_url):
        return False


session = NoStripAuthSession()
session.hooks = {
    'response': [response_logging_hook, assert_status_hook],
}
session.headers.update({
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': _get_user_agent_string()
})


def api_response_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
            if response:
                return response.json() if response.content else response
            return None
        except requests.HTTPError as err:
            raise CLIError(str(err))
    return wrapper


@api_response_decorator
def list_locations():
    url = f'{API_ROOT}/locations'
    response = session.get(url)
    return response


@api_response_decorator
def get_location_details(location):
    url = f'{API_ROOT}/locations/{location}'
    response = session.get(url)
    return response


@api_response_decorator
def list_codespaces(access_token, plan_id):
    url = f'{API_ROOT}/environments'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'planId': plan_id}
    response = session.get(url, headers=headers, params=params)
    return response


@api_response_decorator
def get_codespace(access_token, codespace_id):
    url = f'{API_ROOT}/environments/{codespace_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = session.get(url, headers=headers)
    return response


@api_response_decorator
def start_codespace(access_token, codespace_id):
    url = f'{API_ROOT}/environments/{codespace_id}/start'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = session.post(url, headers=headers)
    return response


@api_response_decorator
def shutdown_codespace(access_token, codespace_id):
    url = f'{API_ROOT}/environments/{codespace_id}/shutdown'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = session.post(url, headers=headers)
    return response


@api_response_decorator
def delete_codespace(access_token, codespace_id):
    url = f'{API_ROOT}/environments/{codespace_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = session.delete(url, headers=headers)
    return response


@api_response_decorator
def create_codespace(access_token, data):
    url = f'{API_ROOT}/environments'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = session.post(url, headers=headers, json=data)
    return response
