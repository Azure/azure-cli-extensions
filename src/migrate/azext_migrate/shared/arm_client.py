# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Single cross-feature ARM REST surface built on send_raw_request."""

import json as _json
import re as _re
import time as _time

from knack.log import get_logger

from azure.cli.core.util import send_raw_request

from azext_migrate.shared import arm_ids, errors
from azext_migrate.shared.constants import (
    RUNBOOKS_API_VERSION,
    WAVE_OPERATIONS_API_VERSION,
)

logger = get_logger(__name__)

# Async status polling tuning.
_DEFAULT_POLL_DELAY = 5
_MAX_POLL_DELAY = 60
_TERMINAL_SUCCESS = 'succeeded'
_TERMINAL_FAILURE = ('failed', 'canceled', 'cancelled')


def _poll_delay(response):
    """Seconds to wait before the next poll, honoring Retry-After."""
    retry_after = response.headers.get('Retry-After')
    if retry_after and retry_after.isdigit():
        return min(int(retry_after), _MAX_POLL_DELAY)
    return _DEFAULT_POLL_DELAY


def _rewrite_poll_api_version(url):
    """Point an async-operation status URL at the wave-operations API era.

    Runbook create/delete are served by RUNBOOKS_API_VERSION, but the
    Azure-AsyncOperation/Location status endpoint (migrateProjects/
    waveOperations) is only registered at WAVE_OPERATIONS_API_VERSION and
    returns NoRegisteredProviderFound otherwise. The header echoes the
    request's api-version, so swap only that value, preserving the signed
    token that follows.
    """
    if 'api-version=' not in url.lower():
        return url + ('&' if '?' in url else '?') + \
            'api-version=' + WAVE_OPERATIONS_API_VERSION
    return _re.sub(
        r'([?&]api-version=)[^&]+',
        r'\g<1>' + WAVE_OPERATIONS_API_VERSION,
        url, count=1)


class ArmClient:
    """Thin, generic wrapper over send_raw_request for ARM resources.

    Every migrate feature package routes its REST calls through this one
    surface so authentication, endpoint selection, serialization, paging
    and error mapping live in exactly one place.
    """

    def __init__(self, cmd, api_version=RUNBOOKS_API_VERSION):
        self.cmd = cmd
        self.api_version = api_version

    def _url(self, resource_id):
        endpoint = self.cmd.cli_ctx.cloud.endpoints.resource_manager
        return endpoint.rstrip('/') + arm_ids.with_api_version(
            resource_id, self.api_version)

    def _send(self, method, resource_id, body=None):
        kwargs = {}
        if body is not None:
            kwargs['body'] = _json.dumps(body)
        response = send_raw_request(
            self.cmd.cli_ctx, method, self._url(resource_id), **kwargs)
        if response.status_code >= 400:
            errors.raise_for_arm_error(response)
        return response

    @staticmethod
    def _json_or_none(response):
        if not getattr(response, 'content', None):
            return None
        try:
            return response.json()
        except ValueError:
            return None

    def _poll_until_done(self, response, method, resource_id):
        """Follow an Azure LRO to completion, returning the initial body.

        Create/delete on runbooks are long-running: they return 201/202
        with an Azure-AsyncOperation (or Location) header. Poll that URL
        until the operation reaches a terminal state, then return the
        original response body (the caller already has the resource repr).
        """
        header_name = ('Azure-AsyncOperation'
                       if response.headers.get('Azure-AsyncOperation')
                       else 'Location')
        poll_url = response.headers.get(header_name)
        result = self._json_or_none(response)
        if response.status_code not in (201, 202) or not poll_url:
            logger.info(
                "%s '%s' completed synchronously (HTTP %s).",
                method, resource_id, response.status_code)
            return result
        poll_url = _rewrite_poll_api_version(poll_url)
        op_ref = poll_url.split('?', 1)[0]
        delay = _poll_delay(response)
        logger.warning(
            "%s '%s' is a long-running operation (HTTP %s). Tracking via "
            "'%s' header: %s. First status check in %ss "
            "(use --no-wait to skip).",
            method, resource_id, response.status_code, header_name,
            op_ref, delay)
        logger.info("Full async-operation poll URL: %s", poll_url)
        start = _time.monotonic()
        attempt = 0
        while True:
            _time.sleep(delay)
            attempt += 1
            poll = send_raw_request(self.cmd.cli_ctx, 'GET', poll_url)
            if poll.status_code >= 400:
                errors.raise_for_arm_error(poll)
            body = self._json_or_none(poll) or {}
            status = body.get('status') or ''
            elapsed = int(_time.monotonic() - start)
            norm = status.lower()
            if poll.status_code in (200, 204) and not status:
                logger.warning(
                    "%s '%s' completed (elapsed %ss, %s poll(s)).",
                    method, resource_id, elapsed, attempt)
                return result
            if norm == _TERMINAL_SUCCESS:
                logger.warning(
                    "%s '%s' succeeded (elapsed %ss, %s poll(s)).",
                    method, resource_id, elapsed, attempt)
                return result
            if norm in _TERMINAL_FAILURE:
                errors.raise_for_async_operation(body)
            delay = _poll_delay(poll)
            logger.warning(
                "%s '%s' still running: status=%s (elapsed %ss, "
                "poll #%s, next check in %ss).",
                method, resource_id, status or '(none)', elapsed,
                attempt, delay)

    def _begin(self, method, resource_id, body=None, no_wait=False):
        response = self._send(method, resource_id, body)
        if no_wait:
            logger.warning(
                "%s '%s' accepted; --no-wait set, not polling for "
                "completion.", method, resource_id)
            return self._json_or_none(response)
        return self._poll_until_done(response, method, resource_id)

    def get(self, resource_id):
        """GET a resource and return its JSON body."""
        return self._send('GET', resource_id).json()

    def get_or_none(self, resource_id):
        """GET a resource, returning None on 404 (existence check)."""
        from azure.cli.core.azclierror import HTTPError
        try:
            response = send_raw_request(
                self.cmd.cli_ctx, 'GET', self._url(resource_id))
        except HTTPError as ex:
            if getattr(ex.response, 'status_code', None) == 404:
                return None
            raise
        if response.status_code >= 400:
            errors.raise_for_arm_error(response)
        return response.json()

    def list(self, collection_id):
        """GET a collection, following nextLink pagination."""
        items = []
        url = self._url(collection_id)
        while url:
            response = send_raw_request(self.cmd.cli_ctx, 'GET', url)
            if response.status_code >= 400:
                errors.raise_for_arm_error(response)
            body = response.json()
            items.extend(body.get('value', []))
            url = body.get('nextLink')
        return items

    def put(self, resource_id, body=None, no_wait=False):
        """PUT (create/generate/start) a resource, awaiting any LRO."""
        return self._begin('PUT', resource_id, body, no_wait)

    def patch(self, resource_id, body=None):
        """PATCH (update) a resource."""
        return self._json_or_none(self._send('PATCH', resource_id, body))

    def delete(self, resource_id, no_wait=False):
        """DELETE a resource, awaiting any LRO."""
        return self._begin('DELETE', resource_id, no_wait=no_wait)

    def post_action(self, resource_id, action_name, body=None,
                    no_wait=False):
        """POST {resourceId}/{action_name} with an optional JSON body.

        This is the workhorse for every action endpoint (AddStep,
        PerformAction, ProvideApproval, GenerateDownloadUrl, ...).
        """
        action_id = f"{resource_id}/{action_name}"
        return self._begin('POST', action_id, body, no_wait)
