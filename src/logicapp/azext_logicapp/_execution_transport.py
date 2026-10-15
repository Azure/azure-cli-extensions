# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=import-error,no-name-in-module
"""Bounded, non-retrying transport used only by execution controls."""

import logging
import re
import time
from contextlib import contextmanager
from urllib.parse import urlsplit

from azure.cli.core._profile import Profile
from azure.cli.core.azclierror import ClientRequestError, InvalidArgumentValueError
from knack.util import CLIError
import requests
from requests.adapters import HTTPAdapter
from urllib3 import PoolManager
from urllib3.util import Timeout
from urllib3.exceptions import ReadTimeoutError

from ._runtime_client import SiteRuntimeClient
from ._json import strict_json_loads
from ._http_deadline import DeadlineSocket, remaining_timeout

EXECUTION_API_VERSION = "2024-11-01"
MAX_RESPONSE_BYTES = 1024 * 1024
RESPONSE_CHUNK_BYTES = 64 * 1024
REQUEST_TIMEOUT = 5


class ExecutionError(ClientRequestError):
    def __init__(self, kind, message, before_send=False):
        super().__init__(message)
        self.kind = kind
        self.before_send = before_send


class DeadlineExpired(Exception):
    def __init__(self, before_send=False):
        super().__init__()
        self.before_send = before_send


class _PreserveTargetAuthentication(requests.auth.AuthBase):  # pylint: disable=too-few-public-methods
    def __call__(self, request):
        return request


class _SuppressHttpDetails(logging.Filter):  # pylint: disable=too-few-public-methods
    def filter(self, _record):
        return False


@contextmanager
def _private_transport_logs():
    # Continuation tokens are service-provided opaque data, not debug evidence.
    logger = logging.getLogger("urllib3.connectionpool")
    suppress = _SuppressHttpDetails()
    logger.addFilter(suppress)
    try:
        yield
    finally:
        logger.removeFilter(suppress)


def _check_deadline(deadline, request_deadline, before_send=False):
    now = time.monotonic()
    if now >= deadline:
        raise DeadlineExpired(before_send=before_send)
    if now >= request_deadline:
        raise ExecutionError("requestTimeout", "Execution request exceeded its network timeout.",
                             before_send=before_send)


def _deadline_adapter(deadline):
    def wrap(sock):
        try:
            sock.settimeout(remaining_timeout(deadline, sock.gettimeout()))
            return DeadlineSocket(sock, deadline)
        except TimeoutError:
            sock.close()
            raise

    class BudgetConnectionMixin:  # pylint: disable=too-few-public-methods
        def _new_conn(self):
            return wrap(super()._new_conn())

        def connect(self):
            super().connect()
            self.sock = wrap(self.sock)

        def _tunnel(self):
            self.sock = wrap(self.sock)
            return super()._tunnel()

    def pools_for(manager):
        def budget_pool(base):
            class BudgetConnection(BudgetConnectionMixin, base.ConnectionCls):  # pylint: disable=too-few-public-methods
                pass

            class BudgetPool(base):  # pylint: disable=too-few-public-methods
                ConnectionCls = BudgetConnection

            return BudgetPool

        return {scheme: budget_pool(pool) for scheme, pool in manager.pool_classes_by_scheme.items()}

    class BudgetAdapter(HTTPAdapter):
        def init_poolmanager(self, connections, maxsize, block=False, **kwargs):
            self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize, block=block, **kwargs)
            self.poolmanager.pool_classes_by_scheme = pools_for(self.poolmanager)

        def proxy_manager_for(self, proxy, **kwargs):
            manager = super().proxy_manager_for(proxy, **kwargs)
            if not getattr(manager, "_logicapp_budget_pools", False):
                manager.pool_classes_by_scheme = pools_for(manager)
                manager._logicapp_budget_pools = True
            return manager

    return BudgetAdapter(max_retries=0)


class ExecutionTransport:  # pylint: disable=too-few-public-methods
    def __init__(self, client):
        self.client = client
        target = client.site_resource_id
        if client.is_local:
            parsed = urlsplit(target)
            if (parsed.scheme != "http" or parsed.hostname != "localhost" or not parsed.port
                    or parsed.path or parsed.query or parsed.fragment or parsed.username or parsed.password):
                raise InvalidArgumentValueError("Execution controls require the selected localhost runtime port.")
        elif not re.fullmatch(
                r"/subscriptions/[A-Za-z0-9-]+/resourceGroups/[\w.()-]+"
                r"/providers/Microsoft\.Web/sites/[A-Za-z0-9-]+", target, flags=re.IGNORECASE):
            raise InvalidArgumentValueError("Execution controls require a Standard site, not a slot or nested target.")
        self.runtime = SiteRuntimeClient(client.cmd, target, api_version=EXECUTION_API_VERSION,
                                         host_key=client.host_key)

    def request(self, method, path, deadline, params=None, body=None):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise DeadlineExpired(before_send=True)
        url = self.runtime._build_url(path, params=params)  # pylint: disable=protected-access
        headers = {"Content-Type": "application/json", "Accept": "application/json",
                   "Accept-Encoding": "identity"}
        if self.client.is_local:
            if self.client.host_key:
                headers["x-functions-key"] = self.client.host_key
        else:
            endpoints = self.client.cmd.cli_ctx.cloud.endpoints
            url = endpoints.resource_manager.rstrip("/") + url
            # Let the selected CLI profile cache/refresh credentials on every poll.
            try:
                token, _, _ = Profile(cli_ctx=self.client.cmd.cli_ctx).get_raw_token(
                    endpoints.active_directory_resource_id,
                    subscription=self.client.site_resource_id.split("/")[2])
                headers["Authorization"] = "{} {}".format(token[0], token[1])
            except (CLIError, requests.RequestException):
                raise ExecutionError("authentication", "Could not obtain the selected Azure CLI credential.",
                                     before_send=True) from None
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise DeadlineExpired(before_send=True)
        budget = min(REQUEST_TIMEOUT, remaining)
        request_deadline = min(deadline, time.monotonic() + budget)
        # The CLI REST helper has no timeout and follows redirects. A separate
        # session confines these controls without changing other runtime commands.
        with _private_transport_logs(), requests.Session() as session:
            # Explicit auth prevents netrc substitution without disabling cloud proxies or CA bundles.
            session.auth = _PreserveTargetAuthentication()
            adapter = _deadline_adapter(request_deadline)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            if self.client.is_local:
                session.trust_env = False
            try:
                _check_deadline(deadline, request_deadline, before_send=True)
                with session.request(method, url, headers=headers, allow_redirects=False, stream=True,
                                     timeout=Timeout(total=budget, connect=budget, read=budget),
                                     **({"json": body} if body is not None else {})) as response:
                    _check_deadline(deadline, request_deadline)
                    status = response.status_code
                    if not 200 <= status < 300:
                        kind = {401: "unauthorized", 403: "unauthorized", 404: "notFound",
                                409: "conflict"}.get(status, "redirect" if 300 <= status < 400 else "service")
                        raise ExecutionError(kind, "Execution endpoint returned HTTP {}. "
                                             "Provider details were not exposed.".format(status))
                    encoding = response.headers.get("Content-Encoding", "")
                    if not isinstance(encoding, str) or encoding.strip().lower() not in ("", "identity"):
                        raise ExecutionError(
                            "invalidResponse", "Execution endpoint returned unsupported content encoding; "
                            "no response body was consumed.")
                    content = bytearray()
                    for chunk in response.iter_content(chunk_size=RESPONSE_CHUNK_BYTES):
                        _check_deadline(deadline, request_deadline)
                        if len(chunk) > MAX_RESPONSE_BYTES - len(content):
                            raise ExecutionError("invalidResponse", "Execution response exceeded the size limit.")
                        content.extend(chunk)
                    _check_deadline(deadline, request_deadline)
                    if method.upper() == "POST" and content:
                        raise ExecutionError(
                            "invalidResponse", "Execution mutation returned a nonempty response body; "
                            "an empty acknowledgement was required.")
                    try:
                        payload = strict_json_loads(content) if content else None
                    except (ValueError, RecursionError):
                        raise ExecutionError("invalidResponse", "Execution endpoint returned invalid JSON.") from None
                    _check_deadline(deadline, request_deadline)
                    return {"statusCode": status, "payload": payload, "headers": response.headers}
            except requests.Timeout:
                if time.monotonic() >= deadline:
                    raise DeadlineExpired() from None
                raise ExecutionError("requestTimeout", "Execution request exceeded its network timeout.") from None
            except requests.RequestException as ex:
                _check_deadline(deadline, request_deadline)
                if ex.args and isinstance(ex.args[0], ReadTimeoutError):
                    if time.monotonic() >= deadline:
                        raise DeadlineExpired() from None
                    raise ExecutionError("requestTimeout", "Execution request exceeded its network timeout.") from None
                raise ExecutionError("unavailable", "Could not reach the selected execution endpoint.") from None
