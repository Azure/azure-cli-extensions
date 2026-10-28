# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=import-error,no-name-in-module
"""ARM APIHub managed connector catalog helpers."""

import json
from urllib.parse import quote, urlencode, urlparse, parse_qs

from azure.cli.core.azclierror import HTTPError, InvalidArgumentValueError, ResourceNotFoundError
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import send_raw_request

from ._constants import MANAGED_API_ARM_API_VERSION
from ._paging import operation_kind, slice_items

_MANAGED_APIS_SEGMENT = "/providers/Microsoft.Web/locations/"


def connector_managed_list(cmd, location, search=None, subscription=None, max_items=None, next_token=None, sender=None):
    subscription_id = subscription or get_subscription_id(cmd.cli_ctx)
    url = _managed_apis_url(subscription_id, location)
    payload = _send(cmd, "GET", url, sender=sender)
    items = _items(payload)
    if search:
        items = [item for item in items if _matches_query(item, search)]
    page, continuation = slice_items(items, next_token=next_token, max_items=max_items)
    result = dict(payload or {})
    result["value"] = page
    result["nextContinuationToken"] = continuation
    return result


def connector_managed_show(cmd, connector, location=None, subscription=None, sender=None):
    connector_id = _managed_api_id(cmd, connector, location, subscription)
    return _send(cmd, "GET", _with_api_version(connector_id), sender=sender)


def connector_managed_operation_list(cmd, connector, location=None, kind="all", search=None,
                                     subscription=None, max_items=None, next_token=None, sender=None):
    kind = operation_kind(kind)
    connector_id = _managed_api_id(cmd, connector, location, subscription)
    params = {}
    if search:
        params["$search"] = search
    url = _with_api_version("{}/apiOperations".format(connector_id), params=params)
    payload = _send(cmd, "GET", url, sender=sender)
    items = _filter_operations(_items(payload), kind, search)
    page, continuation = slice_items(items, next_token=next_token, max_items=max_items)
    result = dict(payload or {})
    result["connector"] = connector_id
    result["kind"] = kind
    result["value"] = page
    result["nextContinuationToken"] = continuation
    return result


def connector_managed_operation_show(cmd, connector, operation, location=None, subscription=None, sender=None):
    connector_id = _managed_api_id(cmd, connector, location, subscription)
    operation_name = _terminal_name(operation, "--operation")
    url = _with_api_version("{}/apiOperations/{}".format(connector_id, _quote_segment(operation_name)))
    payload = _send(cmd, "GET", url, sender=sender)
    if isinstance(payload, dict):
        result = dict(payload)
        result["connector"] = connector_id
        result["operation"] = operation_name
        return result
    return payload


def _managed_apis_url(subscription_id, location):
    if not location:
        raise InvalidArgumentValueError("--location is required.")
    return _with_api_version(
        "/subscriptions/{}/providers/Microsoft.Web/locations/{}/managedApis".format(
            subscription_id, _quote_segment(location)))


def _managed_api_id(cmd, connector, location=None, subscription=None):
    value = str(connector or "").strip()
    if not value:
        raise InvalidArgumentValueError("--connector is required.")
    path = value.split("?", 1)[0].rstrip("/")
    lowered = path.lower()
    marker = "/providers/microsoft.web/locations/"
    if path.startswith("/"):
        if marker not in lowered or "/managedapis/" not in lowered:
            raise InvalidArgumentValueError(
                "Connector '{}' is not a managed API name or ARM managedApis id.".format(connector))
        return path
    if "/" in value:
        raise InvalidArgumentValueError(
            "Connector '{}' is not a managed API name or ARM managedApis id.".format(connector))
    subscription_id = subscription or get_subscription_id(cmd.cli_ctx)
    if not location:
        raise InvalidArgumentValueError("--location is required when --connector is a managed API name.")
    return "/subscriptions/{}/providers/Microsoft.Web/locations/{}/managedApis/{}".format(
        subscription_id, _quote_segment(location), _quote_segment(value))


def _terminal_name(value, flag):
    text = str(value or "").strip()
    if not text:
        raise InvalidArgumentValueError("{} is required.".format(flag))
    if "/" in text:
        text = text.split("?", 1)[0].rstrip("/").split("/")[-1]
    return text


def _with_api_version(path, params=None):
    query = {"api-version": MANAGED_API_ARM_API_VERSION}
    if params:
        query.update({key: value for key, value in params.items() if value is not None})
    return "{}?{}".format(path, urlencode(query, doseq=True))


def _send(cmd, method, url, body=None, sender=None):
    send = sender or send_raw_request
    try:
        response = send(
            cmd.cli_ctx,
            method,
            url,
            headers=["Content-Type=application/json"],
            body=json.dumps(body) if body is not None else None)
    except HTTPError as ex:
        raise _mapped_http_error(ex) from ex
    content = getattr(response, "content", None)
    return _json_content(content)


def _mapped_http_error(ex):
    response = getattr(ex, "response", None)
    status_code = getattr(response, "status_code", None)
    payload = _json_content(getattr(response, "content", None))
    error = payload.get("error") if isinstance(payload, dict) else None
    message = None
    code = None
    if isinstance(error, dict):
        code = error.get("code")
        message = error.get("message")
    message = message or str(ex)
    if status_code == 404 or code in ("ApiOperationNotFound", "ResourceNotFound", "NotFound"):
        return ResourceNotFoundError(message)
    return ex


def _json_content(content):
    if not content:
        return {}
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    try:
        return json.loads(content)
    except ValueError:
        return {}


def _items(payload):
    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        value = payload.get("value")
        return value if isinstance(value, list) else []
    return []


def _matches_query(item, search):
    needle = str(search).strip().lower()
    if not needle:
        return True
    props = item.get("properties") if isinstance(item, dict) else {}
    candidates = [item.get("name"), item.get("id")] if isinstance(item, dict) else []
    if isinstance(props, dict):
        candidates.extend([
            props.get("displayName"),
            props.get("description"),
            props.get("summary"),
            props.get("name"),
        ])
    return any(needle in str(candidate).lower() for candidate in candidates if candidate is not None)


def _filter_operations(items, kind, search):
    filtered = items
    if search:
        filtered = [item for item in filtered if _matches_query(item, search)]
    if kind == "all":
        return filtered
    # No fallback to the unfiltered list when nothing classifies: a filter that
    # silently disables itself and returns every operation is worse than an empty
    # page, and it made --kind mean two different things across the two operation
    # list commands.
    return [item for item in filtered if _operation_matches_kind(item, kind)]


def _operation_matches_kind(item, kind):
    if not isinstance(item, dict):
        return False
    props = item.get("properties") if isinstance(item.get("properties"), dict) else {}
    candidates = [item.get("kind"), item.get("type"), props.get("kind"), props.get("operationType"), props.get("apiOperationType")]
    capabilities = props.get("capabilities")
    if isinstance(capabilities, list):
        candidates.extend(capabilities)
    is_trigger = bool(props.get("isNotification") or props.get("isWebhook")) or any(
        "trigger" in str(candidate or "").lower() for candidate in candidates)
    if is_trigger:
        return kind == "trigger"
    for candidate in candidates:
        text = str(candidate or "").lower()
        if kind in text or (kind == "action" and "trigger" not in text and "operation" in text):
            return True
    if kind == "trigger":
        return False
    return True


def _quote_segment(value):
    return quote(str(value), safe="")


def managed_connection_id(cmd, resource_group_name, connection, subscription=None):
    value = str(connection or "").strip()
    if value.startswith("/"):
        return value.split("?", 1)[0].rstrip("/")
    subscription_id = subscription or get_subscription_id(cmd.cli_ctx)
    return "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/connections/{}".format(
        subscription_id, resource_group_name, _quote_segment(value))


def parse_retry_after(headers):
    if not headers:
        return None
    for key, value in dict(headers).items():
        if str(key).lower() == "retry-after":
            return str(value)
    return None


def response_status_from_error(ex):
    return getattr(getattr(ex, "response", None), "status_code", None)


def response_headers_from_error(ex):
    return getattr(getattr(ex, "response", None), "headers", {}) or {}


def query_value(url, name):
    values = parse_qs(urlparse(str(url)).query).get(name)
    return values[0] if values else None
