# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=import-error,no-name-in-module
"""ARM APIHub managed connector catalog helpers."""

import json
from urllib.parse import quote, urlencode, urlparse, parse_qs

from azure.cli.core.azclierror import HTTPError, InvalidArgumentValueError, ResourceNotFoundError, ValidationError
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import send_raw_request

from ._constants import MANAGED_API_ARM_API_VERSION
from ._json import strict_json_loads
from ._paging import operation_kind, slice_items

_MANAGED_APIS_SEGMENT = "/providers/Microsoft.Web/locations/"
_SWAGGER_METHODS = frozenset(("get", "put", "post", "delete", "options", "head", "patch"))


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


def connector_managed_operation_show(cmd, connector, operation, location=None, subscription=None, sender=None,
                                     include_input_schema=False):
    connector_id = _managed_api_id(cmd, connector, location, subscription)
    operation_name = _terminal_name(operation, "--operation")
    url = _with_api_version("{}/apiOperations/{}".format(connector_id, _quote_segment(operation_name)))
    payload = _send(
        cmd, "GET", url, sender=sender,
        json_object_name="Managed connector APIHub operation metadata" if include_input_schema else None)
    if isinstance(payload, dict):
        result = dict(payload)
        result["connector"] = connector_id
        result["operation"] = operation_name
        if include_input_schema:
            operation_id = _swagger_operation_id(payload)
            swagger_url = _with_api_version(connector_id, params={"export": "true"})
            swagger = _send(
                cmd, "GET", swagger_url, sender=sender,
                json_object_name="Managed connector OpenAPI export")
            result["inputSchema"] = _managed_operation_input_schema(swagger, operation_id)
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


def _send(cmd, method, url, body=None, sender=None, json_object_name=None):
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
    if json_object_name:
        return _json_object_content(content, json_object_name)
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


def _json_object_content(content, description):
    if not content:
        raise ValidationError("{} returned an empty response.".format(description))
    if isinstance(content, bytes):
        try:
            content = content.decode("utf-8")
        except UnicodeDecodeError as ex:
            raise ValidationError("{} was not valid UTF-8.".format(description)) from ex
    try:
        payload = strict_json_loads(content)
    except (TypeError, ValueError) as ex:
        raise ValidationError(
            "{} must contain unambiguous finite JSON.".format(description)) from ex
    if not isinstance(payload, dict):
        raise ValidationError("{} must be a JSON object.".format(description))
    return payload


def _swagger_operation_id(operation):
    properties = operation.get("properties")
    if isinstance(properties, dict) and "swaggerOperationId" in properties:
        value = properties["swaggerOperationId"]
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("Managed connector operation has an invalid swaggerOperationId.")
        return value
    value = operation.get("name")
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(
            "Managed connector APIHub operation metadata has no operation name or "
            "swaggerOperationId.")
    return value


def _managed_operation_input_schema(swagger, operation_id):
    if swagger.get("swagger") != "2.0":
        raise ValidationError("Managed connector OpenAPI export must use Swagger 2.0.")

    if not isinstance(swagger.get("paths"), dict):
        raise ValidationError("Managed connector OpenAPI export must include a paths object.")
    definitions = swagger.get("definitions", {})
    reusable_parameters = swagger.get("parameters", {})
    if not isinstance(definitions, dict) or not isinstance(reusable_parameters, dict):
        raise ValidationError("Managed connector OpenAPI definitions and parameters must be JSON objects.")

    matches = []
    unresolved_path_references = []
    for paths_key in ("paths", "x-ms-paths"):
        paths = swagger.get(paths_key, {})
        if not isinstance(paths, dict):
            raise ValidationError("Managed connector OpenAPI '{}' must be a JSON object.".format(paths_key))
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                raise ValidationError("Managed connector OpenAPI path items must be JSON objects.")
            if "$ref" in path_item:
                unresolved_path_references.append(path_item["$ref"])
            for method, operation in path_item.items():
                if method.lower() not in _SWAGGER_METHODS:
                    continue
                if not isinstance(operation, dict):
                    raise ValidationError("Managed connector OpenAPI operations must be JSON objects.")
                candidate_id = operation.get("operationId")
                if isinstance(candidate_id, str) and candidate_id == operation_id:
                    matches.append((path, method.lower(), path_item, operation))

    if not matches:
        if unresolved_path_references:
            raise ValidationError(
                "Could not locate operation ID '{}' without following unresolved "
                "path-item references.".format(operation_id))
        raise ResourceNotFoundError(
            "Operation ID '{}' was not found in the managed connector OpenAPI export.".format(operation_id))
    if len(matches) > 1:
        raise InvalidArgumentValueError(
            "Operation ID '{}' is ambiguous in the managed connector OpenAPI export.".format(operation_id))

    path, method, path_item, operation = matches[0]
    if "$ref" in path_item:
        raise ValidationError(
            "The selected path item contains an unresolved $ref; inherited input parameters "
            "cannot be discovered without following it.")
    path_parameters = path_item.get("parameters", [])
    operation_parameters = operation.get("parameters", [])
    if not isinstance(path_parameters, list) or not isinstance(operation_parameters, list):
        raise ValidationError("Managed connector OpenAPI operation parameters must be JSON arrays.")
    if any(not isinstance(parameter, dict) for parameter in path_parameters + operation_parameters):
        raise ValidationError("Managed connector OpenAPI parameter entries must be JSON objects.")

    schema_source = {
        "pathParameters": path_parameters,
        "operationParameters": operation_parameters,
        "definitions": definitions,
        "parameterDefinitions": reusable_parameters,
    }
    return {
        "swagger": "2.0",
        "operationId": operation_id,
        "path": path,
        "method": method,
        "pathParameters": path_parameters,
        "operationParameters": operation_parameters,
        "definitions": definitions,
        "parameterDefinitions": reusable_parameters,
        "dynamicMetadata": {
            "resolved": False,
            "extensions": _collect_extension_metadata(schema_source),
        },
        "references": {
            "resolved": False,
            "external": _collect_external_references(schema_source),
        },
    }


def _collect_extension_metadata(value, path="$"):
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = "{}/{}".format(path, str(key).replace("~", "~0").replace("/", "~1"))
            if isinstance(key, str) and key.startswith("x-ms-dynamic-"):
                found.append({"path": child_path, "name": key, "value": child})
            found.extend(_collect_extension_metadata(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_collect_extension_metadata(child, "{}/{}".format(path, index)))
    return found


def _collect_external_references(value):
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "$ref" and isinstance(child, str) and not child.startswith("#"):
                found.append(child)
            found.extend(_collect_external_references(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(_collect_external_references(child))
    return sorted(set(found))


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
