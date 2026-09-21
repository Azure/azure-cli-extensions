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

    def __init__(self, cmd, api_version=RUNBOOKS_API_VERSION,
                 rewrite_poll_api_version=True):
        self.cmd = cmd
        self.api_version = api_version
        # Runbook create/delete LROs are polled via the waveOperations type
        # at a different api-version; artifact LROs are polled at their own
        # async-operation URI as-is, so callers can opt out of the rewrite.
        self.rewrite_poll_api_version = rewrite_poll_api_version

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

    def _finalize(self, result, final_get_id):
        """Return the settled resource state after a successful LRO.

        Standard Azure CLI behaviour is for create/update commands to
        render the *final* resource (a GET issued once the operation
        completes), not the initial 201/202 accepted body -- which still
        shows ``provisioningState: InProgress``. ``final_get_id`` is the
        resource to re-read; it is ``None`` for operations with nothing to
        fetch (e.g. delete), in which case the initial body is returned
        unchanged. If the follow-up GET 404s (resource gone), the initial
        body is kept as a safe fallback.
        """
        if not final_get_id:
            return result
        refreshed = self.get_or_none(final_get_id)
        return refreshed if refreshed is not None else result

    def _poll_until_done(self, response, method, resource_id,
                         final_get_id=None, return_final_poll=False):
        """Follow an Azure LRO to completion and return the final state.

        Create/delete on runbooks are long-running: they return 201/202
        with an Azure-AsyncOperation (or Location) header. Poll that URL
        until the operation reaches a terminal state. On success, when
        ``final_get_id`` is set, re-read that resource so the caller sees
        the settled representation (see :meth:`_finalize`); otherwise the
        original response body is returned. When ``return_final_poll`` is
        set (and no ``final_get_id``), the terminal operation-status body
        is returned instead -- used by actions whose result (e.g. a SAS
        URL) is carried in the async operation status rather than the
        initial accepted body.
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
            return self._finalize(result, final_get_id)
        if self.rewrite_poll_api_version:
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
                if return_final_poll and not final_get_id:
                    return body
                return self._finalize(result, final_get_id)
            if norm == _TERMINAL_SUCCESS:
                logger.warning(
                    "%s '%s' succeeded (elapsed %ss, %s poll(s)).",
                    method, resource_id, elapsed, attempt)
                if return_final_poll and not final_get_id:
                    return body
                return self._finalize(result, final_get_id)
            if norm in _TERMINAL_FAILURE:
                errors.raise_for_async_operation(body)
            delay = _poll_delay(poll)
            logger.warning(
                "%s '%s' still running: status=%s (elapsed %ss, "
                "poll #%s, next check in %ss).",
                method, resource_id, status or '(none)', elapsed,
                attempt, delay)

    def _begin(self, method, resource_id, body=None, no_wait=False,
               final_get_id=None, return_final_poll=False):
        response = self._send(method, resource_id, body)
        if no_wait:
            logger.warning(
                "%s '%s' accepted; --no-wait set, not polling for "
                "completion.", method, resource_id)
            return self._json_or_none(response)
        return self._poll_until_done(
            response, method, resource_id, final_get_id, return_final_poll)

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
        """PUT (create/generate/start) a resource, awaiting any LRO.

        On success the settled resource is re-read (a final GET on the same
        id) so callers render the final state (e.g. ``provisioningState:
        Succeeded``) rather than the initial accepted body.
        """
        return self._begin(
            'PUT', resource_id, body, no_wait, final_get_id=resource_id)

    def patch(self, resource_id, body=None):
        """PATCH (update) a resource."""
        return self._json_or_none(self._send('PATCH', resource_id, body))

    def delete(self, resource_id, no_wait=False):
        """DELETE a resource, awaiting any LRO.

        Returns None: a completed delete has no resource to render (the
        initial 202 accepted body still shows the resource as InProgress,
        which is misleading), matching standard Azure CLI delete behaviour.
        """
        self._begin('DELETE', resource_id, no_wait=no_wait)

    def post_action(self, resource_id, action_name, body=None,
                    no_wait=False, final_get=False,
                    return_final_poll=False):
        """POST {resourceId}/{action_name} with an optional JSON body.

        This is the workhorse for every action endpoint (AddStep,
        PerformAction, ProvideApproval, GenerateDownloadUrl, ...).

        Set ``final_get=True`` only for actions whose settled state is the
        parent resource itself (e.g. Regenerate), so the LRO result is a
        fresh GET of ``resource_id`` rather than the initial InProgress body.
        Set ``return_final_poll=True`` for actions whose result is carried
        in the async operation status (e.g. an artifact download SAS URL).
        Most actions return their own payload (SAS URL, validation result)
        or mutate state exposed elsewhere, so they leave both False.
        """
        action_id = f"{resource_id}/{action_name}"
        final_get_id = resource_id if final_get else None
        return self._begin(
            'POST', action_id, body, no_wait, final_get_id,
            return_final_poll)
