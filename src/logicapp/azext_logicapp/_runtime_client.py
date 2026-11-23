# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long,import-error,no-name-in-module
"""Site-runtime client for Logic Apps Standard workflow run commands."""

import json
import re
from io import BytesIO
from urllib.parse import quote, urlencode

from azure.cli.core.azclierror import (
    ClientRequestError, HTTPError, InvalidArgumentValueError, ResourceNotFoundError, UnauthorizedError,
    ValidationError)
from azure.cli.core.util import send_raw_request
from requests.exceptions import ConnectionError as RequestsConnectionError

from ._paging import slice_items
from ._json import strict_json_loads

DEFAULT_SITE_RUNTIME_API_VERSION = "2018-11-01"
_MANAGEMENT_PREFIX = "hostruntime/runtime/webhooks/workflow/api/management"
_RUNTIME_PREFIX = "hostruntime/runtime/webhooks/workflow"
_VFS_PREFIX = "hostruntime/admin/vfs"


def validate_file_etag(value, argument=False, description="workflow file"):
    error = InvalidArgumentValueError if argument else ClientRequestError
    if not isinstance(value, str) or not value or value.startswith("W/"):
        raise error("A usable strong {} ETag is required; weak or missing ETags are not supported.".format(description))
    if argument and re.fullmatch(r"[A-Za-z0-9._:-]+", value):
        value = '"{}"'.format(value)
    if not re.fullmatch(r'"[\x21\x23-\x2b\x2d-\x7e]+"', value) or value == '"*"':
        raise error("Use one exact {} ETag, not a wildcard, list, or weak ETag.".format(description))
    return value


def _quote_segment(value):
    return quote(str(value), safe="")


def _operation_segment(operation):
    """Normalize an operation reference to the single route segment the runtime expects.

    ``connector operation list`` reports each operation with an ``id`` that carries the
    connector and an ``operations`` segment ahead of the name. Quoting that whole string
    would percent-encode the separators into one unresolvable segment -- the same defect
    that made connector ids unusable before, so the same rule applies here: accept the id
    form and the bare name alike.
    """
    text = str(operation).strip().strip("/")
    if "/" in text:
        text = text.rsplit("/", 1)[-1]
    return _quote_segment(text)


def _operation_group_segment(connector):
    """Normalize a connector reference to the single route segment the runtime expects.

    ``connector list`` reports each connector with an ``id`` like
    ``/serviceProviders/serviceBus`` and a ``name`` like ``serviceBus``. Quoting the id
    form with ``safe=""`` produced ``%2FserviceProviders%2FserviceBus``, which the runtime
    rejected with ``ApiNotFound`` -- so the output of one command could not be fed into
    another. Accept the id form, the unrooted form, and the bare name alike.
    """
    text = str(connector).strip().strip("/")
    lowered = text.lower()
    prefix = "serviceproviders/"
    if lowered.startswith(prefix):
        text = text[len(prefix):]
    return _quote_segment(text)


def workflows_path():
    return "workflows"


def vfs_workflow_dir_path(workflow):
    return _quote_segment(workflow)


def vfs_workflow_file_path(workflow):
    return "{}/workflow.json".format(vfs_workflow_dir_path(workflow))


def vfs_maps_dir_path():
    return "Artifacts/Maps"


def vfs_map_path(map_name):
    return "{}/{}".format(vfs_maps_dir_path(), _quote_segment(map_name))


def workflow_path(workflow):
    return "{}/{}".format(workflows_path(), _quote_segment(workflow))


def workflow_validate_path(workflow):
    return "{}/validate".format(workflow_path(workflow))


def workflow_runs_path(workflow):
    return "{}/runs".format(workflow_path(workflow))


def workflow_triggers_path(workflow):
    return "workflows/{}/triggers".format(_quote_segment(workflow))


def workflow_versions_path(workflow):
    return "workflows/{}/versions".format(_quote_segment(workflow))


def workflow_version_path(workflow, version):
    return "{}/{}".format(workflow_versions_path(workflow), _quote_segment(version))


def workflow_trigger_path(workflow, trigger):
    return "{}/{}".format(workflow_triggers_path(workflow), _quote_segment(trigger))


def trigger_run_path(workflow, trigger):
    return "{}/run".format(workflow_trigger_path(workflow, trigger))


def trigger_callback_url_path(workflow, trigger):
    return "{}/listCallbackUrl".format(workflow_trigger_path(workflow, trigger))


def trigger_schema_path(workflow, trigger):
    return "{}/schemas/json".format(workflow_trigger_path(workflow, trigger))


def trigger_histories_path(workflow, trigger):
    return "{}/histories".format(workflow_trigger_path(workflow, trigger))


def trigger_history_path(workflow, trigger, history):
    return "{}/{}".format(trigger_histories_path(workflow, trigger), _quote_segment(history))


def trigger_history_resubmit_path(workflow, trigger, history):
    return "{}/resubmit".format(trigger_history_path(workflow, trigger, history))


def mockable_operations_path(http_only=False):
    return "listMockableHttpOperations" if http_only else "listMockableOperations"


def operation_groups_path():
    """Connector catalog route: all operation groups visible to the site."""
    return "operationGroups"


def operation_group_path(connector):
    """Singleton connector (operation group) route."""
    return "{}/{}".format(operation_groups_path(), _operation_group_segment(connector))


def operation_group_operations_path(connector):
    """Operations exposed by one connector."""
    return "{}/operations".format(operation_group_path(connector))


def operation_group_operation_path(connector, operation):
    """Singleton operation on one connector."""
    return "{}/{}".format(operation_group_operations_path(connector), _operation_segment(operation))


def page_items(items, next_token=None, max_items=None):
    """Page a list the caller has already filtered.

    ``list`` pages what it fetches, which is wrong when a filter has to be applied
    first -- pages would be cut from the unfiltered set. This exposes the same slicing
    so filtered commands hand back continuation tokens of the same shape.
    """
    return slice_items(items, next_token=next_token, max_items=max_items)


def generate_unit_test_path(workflow, run_id):
    return "{}/generateUnitTest".format(workflow_run_path(workflow, run_id))


def workflow_run_path(workflow, run_id):
    return "{}/{}".format(workflow_runs_path(workflow), _quote_segment(run_id))


def workflow_run_cancel_path(workflow, run_id):
    return "{}/cancel".format(workflow_run_path(workflow, run_id))


def workflow_run_resubmit_path(workflow, run_id):
    return "{}/resubmit".format(workflow_run_path(workflow, run_id))


def run_actions_path(workflow, run_id):
    return "{}/actions".format(workflow_run_path(workflow, run_id))


def run_action_path(workflow, run_id, action):
    return "{}/{}".format(run_actions_path(workflow, run_id), _quote_segment(action))


def action_repetitions_path(workflow, run_id, action, scope=False):
    segment = "scopeRepetitions" if scope else "repetitions"
    return "{}/{}".format(run_action_path(workflow, run_id, action), segment)


def action_request_histories_path(workflow, run_id, action, repetition=None):
    base = run_action_path(workflow, run_id, action)
    if repetition is not None:
        base = "{}/repetitions/{}".format(base, _quote_segment(repetition))
    return "{}/requestHistories".format(base)


class SiteRuntimeClient:
    """Thin ARM-hostruntime proxy client shared by the workflow run and action commands.

    Public seam for command agents:
    - ``SiteRuntimeClient(cmd, site_resource_id, api_version=DEFAULT_SITE_RUNTIME_API_VERSION)``
    - ``get(relative_path, params=None)`` / ``post(relative_path, body=None, params=None)``
    - ``post_with_receipt(relative_path, body=None, params=None)`` for HTTP completion checks
    - ``get_raw_url(url, max_bytes=None)`` for service-provided contentLink URIs
    - ``list(relative_path, params=None, next_token=None, max_items=None)``
    - route helpers above for workflow run/action paths.
    """

    def __init__(self, cmd, site_resource_id, api_version=DEFAULT_SITE_RUNTIME_API_VERSION, sender=None, not_found_as_resource=True, host_key=None):
        self.cmd = cmd
        self.site_resource_id, self.is_local = _normalize_target(site_resource_id)
        self.api_version = api_version
        self.host_key = host_key
        self._sender = sender or send_raw_request
        self._not_found_as_resource = not_found_as_resource

    def get(self, relative_path, params=None):
        return self.request("GET", relative_path, params=params)

    def vfs_client(self):
        return SiteVfsClient(self.cmd, self.site_resource_id, api_version=self.api_version,
                             sender=self._sender, host_key=self.host_key,
                             not_found_as_resource=self._not_found_as_resource)

    def post(self, relative_path, body=None, params=None):
        return self.request("POST", relative_path, body=body, params=params)

    def post_with_headers(self, relative_path, body=None, params=None):
        return self.request_with_headers("POST", relative_path, body=body, params=params)

    def post_with_receipt(self, relative_path, body=None, params=None):
        """POST with the HTTP status, decoded payload and headers for completion checks."""
        return self._request_with_receipt("POST", relative_path, body=body, params=params)

    def post_raw(self, relative_path, body=None, params=None):
        """POST returning the raw response body.

        Routed through the same sender as every other request so a 404 is
        translated to ``ResourceNotFoundError``; callers that reach the sender
        directly bypass that translation and surface a not-found as exit 1.
        """
        response = self._send("POST", self._build_url(relative_path, params=params), body=body)
        return getattr(response, "content", b"") or b""

    def get_raw_url(self, url, max_bytes=None):
        headers = ["Content-Type=application/json"]
        if max_bytes is not None:
            headers.append("Range=bytes=0-{}".format(int(max_bytes) - 1))
        response = self._sender(self.cmd.cli_ctx, "GET", url, headers=headers, skip_authorization_header=True)
        return {"content": getattr(response, "content", b""), "headers": getattr(response, "headers", {})}

    def list(self, relative_path, params=None, next_token=None, max_items=None):
        payload = self.get(relative_path, params=params)
        items = _extract_items(payload)
        page, next_token = slice_items(items, next_token=next_token, max_items=max_items)
        if isinstance(payload, list):
            return {"value": page, "nextContinuationToken": next_token}
        result = dict(payload or {})
        result["value"] = page
        result["nextContinuationToken"] = next_token
        return result

    def request(self, method, relative_path, body=None, params=None):
        return self.request_with_headers(method, relative_path, body=body, params=params)["payload"]

    def get_runtime(self, relative_path, params=None):
        return self.request_runtime("GET", relative_path, params=params)

    def request_runtime(self, method, relative_path, body=None, params=None):
        return self.request_with_headers(method, relative_path, body=body, params=params, prefix=_RUNTIME_PREFIX)["payload"]

    def request_with_headers(self, method, relative_path, body=None, params=None, prefix=_MANAGEMENT_PREFIX):
        receipt = self._request_with_receipt(method, relative_path, body=body, params=params, prefix=prefix)
        return {"payload": receipt["payload"], "headers": receipt["headers"]}

    def _request_with_receipt(self, method, relative_path, body=None, params=None, prefix=_MANAGEMENT_PREFIX):
        url = self._build_url(relative_path, params=params, prefix=prefix)
        response = self._send(method, url, body=body)
        try:
            content = getattr(response, "content", None)
            payload = strict_json_loads(content) if content else None
        except (ValueError, TypeError, RecursionError):
            raise ClientRequestError("The site runtime returned invalid JSON.") from None
        return {"payload": payload, "headers": getattr(response, "headers", {}) or {},
                "statusCode": getattr(response, "status_code", None)}

    def _send(self, method, url, body=None):
        serialized = json.dumps(body) if body is not None else None
        headers = ["Content-Type=application/json"]
        return self._send_request(method, url, serialized, headers)

    def _send_request(self, method, url, body, headers):
        extra = {}
        if self.is_local:
            # A local runtime is plain localhost HTTP with no Azure identity behind it.
            # ``send_raw_request`` already declines to attach a bearer token to a
            # non-https URL, but say so explicitly so an https local host cannot
            # silently trigger a sign-in the user never asked for.
            extra["skip_authorization_header"] = True
            if self.host_key:
                # Sent as a header rather than a ``code`` query parameter so the
                # secret does not land in URLs, history, or error messages.
                headers.append("x-functions-key={}".format(self.host_key))
        try:
            return self._sender(
                self.cmd.cli_ctx,
                method,
                url,
                headers=headers,
                body=body,
                **extra
            )
        except RequestsConnectionError as ex:
            if not self.is_local:
                raise
            # Nothing is listening on that port. The raw urllib3 traceback names
            # the port but buries it in a stack the user cannot act on, so say
            # plainly what is wrong and what to check.
            raise ClientRequestError(
                "Could not reach a Logic Apps runtime at {}.".format(self.site_resource_id),
                recommendation="Check the runtime is running and that --port matches the port "
                               "it is listening on (default {}).".format(DEFAULT_LOCAL_PORT)
            ) from ex
        except HTTPError as ex:
            status_code = getattr(getattr(ex, "response", None), "status_code", None)
            if status_code == 404 and self._not_found_as_resource:
                raise ResourceNotFoundError(str(ex)) from ex
            if status_code in (401, 403) and self.is_local:
                raise UnauthorizedError(
                    "The local runtime at {} rejected the request.".format(self.site_resource_id),
                    recommendation="Some local hosts require a key. Pass --host-key with the host's "
                                   "master key, or start the runtime so it allows anonymous access."
                ) from ex
            raise

    def _build_url(self, relative_path, params=None, prefix=_MANAGEMENT_PREFIX):
        path = str(relative_path).strip("/")
        query = {"api-version": self.api_version}
        if params:
            query.update({key: value for key, value in params.items() if value is not None})
        return "{}/{}/{}?{}".format(
            self.site_resource_id.rstrip("/"),
            _local_prefix(prefix) if self.is_local else prefix,
            path,
            urlencode(query, doseq=True),
        )


class SiteVfsClient(SiteRuntimeClient):
    """ARM-proxied VFS client rooted at ``wwwroot`` for Logic Apps file-plane reads."""

    def get(self, relative_path, params=None):
        merged = {"relativePath": 1}
        if params:
            merged.update(params)
        return self.request_with_headers("GET", relative_path, params=merged, prefix=_VFS_PREFIX)["payload"]

    def get_raw(self, relative_path, params=None):
        merged = {"relativePath": 1}
        if params:
            merged.update(params)
        response = self._send_vfs("GET", self._build_url(relative_path, params=merged), content_type=None)
        return {"content": getattr(response, "content", b"") or b"", "headers": getattr(response, "headers", {}) or {},
                "statusCode": getattr(response, "status_code", None)}

    def put_raw(self, relative_path, content, params=None, if_match="*"):
        merged = {"relativePath": 1}
        if params:
            merged.update(params)
        # The CLI sender reparses JSON strings/bytes even with an octet-stream
        # content type. A stream preserves exact bytes for readback and recovery.
        with BytesIO(content) as body:
            response = self._send_vfs(
                "PUT",
                self._build_url(relative_path, params=merged),
                body=body,
                content_type="application/octet-stream",
                if_match=if_match)
        return {"content": getattr(response, "content", b"") or b"", "headers": getattr(response, "headers", {}) or {},
                "statusCode": getattr(response, "status_code", None)}

    def delete(self, relative_path, params=None, if_match="*"):
        merged = {"relativePath": 1}
        if params:
            merged.update(params)
        response = self._send_vfs(
            "DELETE",
            self._build_url(relative_path, params=merged),
            content_type=None,
            if_match=if_match)
        return {"content": getattr(response, "content", b"") or b"", "headers": getattr(response, "headers", {}) or {},
                "statusCode": getattr(response, "status_code", None)}

    def _build_url(self, relative_path, params=None, prefix=_VFS_PREFIX):
        return super()._build_url(relative_path, params=params, prefix=prefix)

    def _send_vfs(self, method, url, body=None, content_type=None, if_match=None):
        headers = []
        if content_type:
            headers.append("Content-Type={}".format(content_type))
        if if_match:
            if not isinstance(if_match, str) or any(character in if_match for character in ("\r", "\n")):
                raise InvalidArgumentValueError("If-Match must be a single ETag without newline characters.")
            headers.append("If-Match={}".format(if_match))
        return self._send_request(method, url, body, headers)


def _normalize_site_resource_id(site_resource_id):
    from ._context import _cloud_coordinate

    value = str(site_resource_id or "").strip().rstrip("/")
    parts = value.split("/")
    message = ("site_resource_id must be a canonical Microsoft.Web/sites ARM resource id, "
               "not a slot or nested resource, query or escaped coordinate")
    if (len(parts) != 9 or parts[0]
            or [parts[index].casefold() for index in (1, 3, 5, 6, 7)] != [
                "subscriptions", "resourcegroups", "providers", "microsoft.web", "sites"]):
        raise InvalidArgumentValueError(message)
    try:
        for index in (2, 4, 8):
            _cloud_coordinate(parts[index])
    except ValidationError as ex:
        raise InvalidArgumentValueError(message) from ex
    return value


def local_base_url(port, host=None):
    """Base address for a Logic Apps runtime running on this machine."""
    return "http://{}:{}".format(host or "localhost", int(port))


def _normalize_target(target):
    """Resolve a client target to ``(base, is_local)``.

    A target is either a ``Microsoft.Web/sites`` ARM resource id, which is
    proxied through Resource Manager, or an absolute local base URL such as
    ``http://localhost:7071``, which is reached directly.
    """
    value = str(target or "").strip()
    if "://" in value:
        scheme = value.split("://", 1)[0].lower()
        if scheme not in ("http", "https"):
            raise InvalidArgumentValueError("local runtime address must use http or https")
        return value.rstrip("/"), True
    return _normalize_site_resource_id(value), False


def _local_prefix(prefix):
    """Strip the Resource Manager proxy hop from a route prefix.

    ``hostruntime/`` is the segment ARM uses to forward into the site's own
    host. A runtime reached directly serves the same routes without it.
    """
    marker = "hostruntime/"
    return prefix[len(marker):] if prefix.startswith(marker) else prefix


_SITE_PROVIDER = "/providers/Microsoft.Web/sites/"
DEFAULT_LOCAL_PORT = 7071


def _site_resource_id(cmd, resource_group_name, name):
    """Build the ``Microsoft.Web/sites`` id for a deployed logic app."""
    from azure.cli.core.commands.client_factory import get_subscription_id
    from ._context import _cloud_coordinate

    resource_group_name = _cloud_coordinate(resource_group_name)
    name = _cloud_coordinate(name)
    return "/subscriptions/{}/resourceGroups/{}{}{}".format(
        get_subscription_id(cmd.cli_ctx), resource_group_name, _SITE_PROVIDER, name)


def _validated_port(port):
    """Return the port to use locally, rejecting values that cannot be listened on.

    ``--port 0`` is falsy, so treating it as "not supplied" would silently send
    the request to the default port instead of telling the user their input was
    unusable.
    """
    if port is None:
        return DEFAULT_LOCAL_PORT
    try:
        parsed = int(port)
    except (TypeError, ValueError):
        parsed = None
    if parsed is None or not 1 <= parsed <= 65535:
        raise InvalidArgumentValueError(
            "--port must be a whole number between 1 and 65535; got '{}'.".format(port),
            recommendation="Use the port your local runtime is listening on, or omit "
                           "--port to use {}.".format(DEFAULT_LOCAL_PORT))
    return parsed


def build_runtime_client(cmd, resource_group_name=None, name=None, local=None, port=None,
                         host_key=None, client_class=None, **kwargs):
    """Create a runtime client for either a deployed logic app or a local one.

    Deployed apps are addressed by resource group and name and reached through
    Resource Manager. A local runtime is addressed by port alone: no
    subscription is resolved and no sign-in happens, because nothing in the
    request path talks to Azure.

    The two addressing modes are mutually exclusive, and mixing them is
    rejected here rather than further down, so the user is told what is wrong
    instead of watching a request go somewhere unintended.
    """
    from azure.cli.core.azclierror import (
        MutuallyExclusiveArgumentError, RequiredArgumentMissingError)

    client_class = client_class or SiteRuntimeClient
    if local:
        conflicting = [flag for flag, value in
                       (("--resource-group", resource_group_name), ("--name", name)) if value]
        if conflicting:
            raise MutuallyExclusiveArgumentError(
                "{} cannot be used with --local.".format(" and ".join(conflicting)),
                recommendation="--local targets a runtime on this machine, which has no "
                               "resource group or app name. Drop one or the other.")
        return client_class(cmd, local_base_url(_validated_port(port)), host_key=host_key, **kwargs)

    stray = [flag for flag, value in (("--port", port), ("--host-key", host_key)) if value is not None]
    if stray:
        joined = " and ".join(stray)
        raise RequiredArgumentMissingError(
            "{} {} only to a local runtime.".format(
                joined, "applies" if len(stray) == 1 else "apply"),
            recommendation="Add --local to target a runtime on this machine, or drop "
                           "{} to target a deployed app.".format(joined))

    missing = [flag for flag, value in
               (("--resource-group", resource_group_name), ("--name", name)) if not value]
    if missing:
        raise RequiredArgumentMissingError(
            "{} {} required.".format(" and ".join(missing), "is" if len(missing) == 1 else "are"),
            recommendation="Supply --resource-group and --name to target a deployed logic app, "
                           "or use --local to target a runtime on this machine.")

    return client_class(cmd, _site_resource_id(cmd, resource_group_name, name), **kwargs)


def _extract_items(payload):
    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        value = payload.get("value")
        if isinstance(value, list):
            return value
    raise ClientRequestError("site-runtime list response must be an array or an object with a value array")
