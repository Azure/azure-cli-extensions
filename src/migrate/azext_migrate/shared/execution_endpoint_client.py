# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""REST client for development execution endpoints."""

import ipaddress
import uuid
from urllib.parse import quote, urlsplit

import requests
from knack.log import get_logger
from azure.cli.core.azclierror import CLIInternalError, InvalidArgumentValueError

logger = get_logger(__name__)


class ExecutionEndpointClient:
    """Loopback-only development endpoint client; never sends ARM credentials."""

    def __init__(self, endpoint):
        try:
            parsed = urlsplit(endpoint)
            loopback = ipaddress.ip_address(parsed.hostname or '').is_loopback
            port = parsed.port
        except ValueError as ex:
            raise InvalidArgumentValueError('Invalid execution endpoint.') from ex
        if (parsed.scheme != 'http' or not loopback or not port
                or parsed.path not in ('', '/') or parsed.query or parsed.fragment
                or parsed.username or parsed.password):
            raise InvalidArgumentValueError(
                'The execution endpoint must be an HTTP loopback IP and port without a path.')
        self.endpoint = endpoint.rstrip('/')
        logger.warning('Using the configured development execution endpoint.')
        logger.debug('Development execution endpoint: %s', self.endpoint)

    def request(self, method, path, body=None):
        try:
            with requests.Session() as session:
                session.trust_env = False
                response = session.request(
                    method, self.endpoint + path, json=body,
                    timeout=120, allow_redirects=False)
        except requests.RequestException as ex:
            raise CLIInternalError(
                'Execution service request failed. Check that the worker is running; '
                'a lost response does not cancel an execution. Check execution '
                'list/status before issuing another mutation.') from ex
        if not 200 <= response.status_code < 300:
            try:
                payload = response.json()
                detail = payload.get('error', response.reason) if isinstance(payload, dict) else response.reason
            except ValueError:
                detail = response.reason
            raise CLIInternalError(
                'Execution service returned HTTP {}: {}'.format(response.status_code, detail))
        try:
            return response.json()
        except ValueError as ex:
            raise CLIInternalError('Execution service returned invalid JSON.') from ex

    @staticmethod
    def identifier(value):
        try:
            return str(uuid.UUID(value))
        except (ValueError, TypeError, AttributeError) as ex:
            raise InvalidArgumentValueError(
                'Execution IDs must be GUIDs.') from ex

    def status(self, execution_id):
        return self.request('GET', '/local/executions/' + self.identifier(execution_id))

    def action(self, execution_id, action, step_id=None, entities=None, comment=None):
        path = '/local/executions/' + self.identifier(execution_id)
        if step_id:
            path += '/steps/' + quote(step_id, safe='')
        return self.request('POST', path + '/actions', {
            'action': action, 'entities': entities, 'comment': comment,
        })
