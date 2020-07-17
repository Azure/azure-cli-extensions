# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
    Helpers for requests to Codespaces non-ARM-based APIs
"""

import platform
from enum import Enum

import requests

from knack.util import CLIError
from knack.log import get_logger
from azure.cli.core import __version__ as az_version
from .version import VERSION
from ._config import get_service_domain

logger = get_logger(__name__)

API_ROUTE = "/api/v1"


# The current secret scopes available on the service
class SecretScope(Enum):
    PLAN = 1
    USER = 2


# The current secret types available on the service
class SecretType(Enum):
    ENVIRONMENT_VARIABLE = 1


def _get_user_agent_string():
    pv = platform.python_version()
    ps = platform.system()
    pr = platform.release()
    pp = platform.processor()
    pm = platform.machine()
    return f"python/{pv} ({ps}-{pr}-{pm}-{pp}) azure-cli/{az_version} codespaces-extension/{VERSION}"


def assert_status_hook(r, *_, **__):
    r.raise_for_status()


def response_logging_hook(response, *_, **__):
    for k in response.request.__dict__:
        if k and not k.startswith('_'):
            logger.debug('codespaces-api.request : %s : %s', k, response.request.__dict__[k])
    for k in response.__dict__:
        if k and not k.startswith('_'):
            logger.debug('codespaces-api.response : %s : %s', k, response.__dict__[k])
    if response.content:
        logger.debug('codespaces-api.response : %s : %s', 'content', response.content)


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
            raise CLIError(f"{err}.  Use --debug for details.")
    return wrapper


def custom_api_root_decorator(func):
    def wrapper(*args, **kwargs):
        cli_ctx = kwargs.pop('cli_ctx')
        domain = get_service_domain(cli_ctx)
        api_root = f"https://{domain}{API_ROUTE}"
        kwargs['api_root'] = api_root
        return func(*args, **kwargs)
    return wrapper


@custom_api_root_decorator
@api_response_decorator
def list_locations(api_root=None, **_):
    url = f'{api_root}/locations'
    response = session.get(url)
    return response


@custom_api_root_decorator
@api_response_decorator
def get_location_details(location, api_root=None, **_):
    url = f'{api_root}/locations/{location}'
    response = session.get(url)
    return response


@custom_api_root_decorator
@api_response_decorator
def list_codespaces(access_token, plan_id, api_root=None, **_):
    url = f'{api_root}/environments'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'planId': plan_id}
    response = session.get(url, headers=headers, params=params)
    return response


@custom_api_root_decorator
@api_response_decorator
def get_codespace(access_token, codespace_id, api_root=None, **_):
    url = f'{api_root}/environments/{codespace_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = session.get(url, headers=headers)
    return response


@custom_api_root_decorator
@api_response_decorator
def start_codespace(access_token, codespace_id, api_root=None, **_):
    url = f'{api_root}/environments/{codespace_id}/start'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = session.post(url, headers=headers)
    return response


@custom_api_root_decorator
@api_response_decorator
def shutdown_codespace(access_token, codespace_id, api_root=None, **_):
    url = f'{api_root}/environments/{codespace_id}/shutdown'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = session.post(url, headers=headers)
    return response


@custom_api_root_decorator
@api_response_decorator
def delete_codespace(access_token, codespace_id, api_root=None, **_):
    url = f'{api_root}/environments/{codespace_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = session.delete(url, headers=headers)
    return response


@custom_api_root_decorator
@api_response_decorator
def create_codespace(access_token, data, api_root=None, **_):
    url = f'{api_root}/environments'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = session.post(url, headers=headers, json=data)
    return response


@custom_api_root_decorator
@api_response_decorator
def update_codespace(access_token, codespace_id, data, api_root=None, **_):
    url = f'{api_root}/environments/{codespace_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = session.patch(url, headers=headers, json=data)
    return response


@custom_api_root_decorator
@api_response_decorator
def list_secrets(access_token, plan_id, api_root=None, **_):
    url = f'{api_root}/secrets'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'planId': plan_id}
    response = session.get(url, headers=headers, params=params)
    return response


@custom_api_root_decorator
@api_response_decorator
def create_secret(access_token, plan_id, data, api_root=None, **_):
    url = f'{api_root}/secrets'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'planId': plan_id}
    response = session.post(url, headers=headers, json=data, params=params)
    return response


@custom_api_root_decorator
@api_response_decorator
def update_secret(access_token, plan_id, secret_id, data, api_root=None, **_):
    url = f'{api_root}/secrets/{secret_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'planId': plan_id}
    response = session.put(url, headers=headers, json=data, params=params)
    return response


@custom_api_root_decorator
@api_response_decorator
def delete_secret(access_token, plan_id, secret_id, scope, api_root=None, **_):
    url = f'{api_root}/secrets/{secret_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'planId': plan_id, 'scope': scope}
    response = session.delete(url, headers=headers, params=params)
    return response
