# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import re
import time
import uuid
from datetime import datetime, timezone
from urllib.parse import parse_qsl, quote, urlencode, urlsplit

from azure.cli.core.azclierror import (
    AzureResponseError,
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
    RequiredArgumentMissingError,
)
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import send_raw_request
from knack.log import get_logger


logger = get_logger(__name__)

API_VERSION = "2026-06-01-preview"

_DEFAULT_POLL_INTERVAL_SECONDS = 30
_TERMINAL_OPERATION_STATES = ("succeeded", "failed", "canceled")


def _system_readiness_url(cmd):
    endpoint = cmd.cli_ctx.cloud.endpoints.resource_manager.rstrip("/")
    subscription_id = get_subscription_id(cmd.cli_ctx)
    return (
        "{}/subscriptions/{}/providers/Microsoft.EdgeOperator/"
        "systemReadiness/default?api-version={}"
    ).format(endpoint, subscription_id, API_VERSION)


def show_system_readiness(cmd):
    response = send_raw_request(cmd.cli_ctx, "GET", _system_readiness_url(cmd))
    return response.json()


def _observability_configuration_url(cmd):
    endpoint = cmd.cli_ctx.cloud.endpoints.resource_manager.rstrip("/")
    subscription_id = get_subscription_id(cmd.cli_ctx)
    return (
        "{}/subscriptions/{}/providers/Microsoft.EdgeOperator/"
        "observabilityConfiguration/default?api-version={}"
    ).format(endpoint, subscription_id, API_VERSION)


def show_observability_configuration(cmd):
    response = send_raw_request(cmd.cli_ctx, "GET", _observability_configuration_url(cmd))
    return response.json()


def _system_configuration_url(cmd):
    endpoint = cmd.cli_ctx.cloud.endpoints.resource_manager.rstrip("/")
    subscription_id = get_subscription_id(cmd.cli_ctx)
    return (
        "{}/subscriptions/{}/providers/Microsoft.EdgeOperator/"
        "systemConfiguration/default?api-version={}"
    ).format(endpoint, subscription_id, API_VERSION)


def show_system_configuration(cmd):
    response = send_raw_request(cmd.cli_ctx, "GET", _system_configuration_url(cmd))
    return response.json()


def create_system_configuration(cmd, dns_forwarder_ip_address=None, connection_intent=None,
                                stamp_id=None, device_resource_id=None):
    properties = {
        key: value for key, value in {
            "dnsForwarderIpAddress": dns_forwarder_ip_address,
            "connectionIntent": connection_intent,
            "stampId": stamp_id,
            "deviceResourceId": device_resource_id,
        }.items() if value is not None
    }
    response = send_raw_request(
        cmd.cli_ctx, "PUT", _system_configuration_url(cmd), body=json.dumps({"properties": properties})
    )
    return response.json()


def _subscription_url(cmd, path, api_version, query=None):
    endpoint = cmd.cli_ctx.cloud.endpoints.resource_manager.rstrip("/")
    subscription_id = get_subscription_id(cmd.cli_ctx)
    url = "{}/subscriptions/{}/providers/Microsoft.EdgeOperator/{}?api-version={}".format(
        endpoint, subscription_id, path, api_version
    )
    for name, value in (query or {}).items():
        url += "&{}={}".format(name, quote(value, safe=""))
    return url


def _list_all_pages(cmd, url):
    items = []
    while url:
        page = send_raw_request(cmd.cli_ctx, "GET", url).json()
        items.extend(page.get("value", []))
        url = page.get("nextLink")
    return items


# ---------------------------------------------------------------------------
# Log collections
# ---------------------------------------------------------------------------

def _parse_utc_datetime(value, option_name):
    text = value.strip()
    if text[-1:] in ("Z", "z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        raise InvalidArgumentValueError(
            "{} must be an ISO 8601 date-time, for example 2026-01-01T00:00:00Z.".format(option_name)
        ) from None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _format_utc_datetime(value):
    return value.isoformat().replace("+00:00", "Z")


def _collection_time_range(from_date, to_date):
    start = _parse_utc_datetime(from_date, "--from-date")
    end = _parse_utc_datetime(to_date, "--to-date")
    if end <= start:
        raise InvalidArgumentValueError("--to-date must be later than --from-date.")
    return {"fromDate": _format_utc_datetime(start), "toDate": _format_utc_datetime(end)}


def _validate_job_id(job_id):
    try:
        uuid.UUID(job_id)
    except ValueError:
        raise InvalidArgumentValueError("--job-id must be a GUID.") from None


def _retry_after_seconds(response):
    try:
        seconds = int(response.headers.get("Retry-After"))
    except (TypeError, ValueError):
        return _DEFAULT_POLL_INTERVAL_SECONDS
    return seconds if seconds > 0 else _DEFAULT_POLL_INTERVAL_SECONDS


def _log_collection_status_url(response):
    # The URL can carry signed parameters; keep it internal and never log it.
    status_url = response.headers.get("Azure-AsyncOperation")
    if not status_url:
        raise AzureResponseError(
            "The service accepted the log collection request but returned no Azure-AsyncOperation header."
        )

    return status_url


def _unsigned_operation_status_url(cmd, status_url):
    parts = urlsplit(status_url)
    if (parts.scheme.lower() != "https" or not parts.netloc or parts.username or parts.password or
            not re.fullmatch(
                r"(?:/subscriptions/[0-9a-fA-F-]+)?/providers/Microsoft\.EdgeOperator/"
                r"locations/[A-Za-z0-9_-]+/operationStatuses/[A-Za-z0-9_*~-]+",
                parts.path, re.IGNORECASE)):
        raise InvalidArgumentValueError("--operation-status-url must be an HTTPS log collection operation-status URL.")
    query = [(key, value) for key, value in parse_qsl(parts.query) if key.lower() == "api-version"]
    if not query:
        query = [("api-version", API_VERSION)]
    # Use the active cloud endpoint, never a caller-supplied host, for authenticated requests.
    endpoint = cmd.cli_ctx.cloud.endpoints.resource_manager.rstrip("/")
    return endpoint + parts.path + "?" + urlencode(query)


def _wait_for_log_collection(cmd, response=None, status_url=None, interval=None, timeout=None):
    if response is not None:
        status_url = _log_collection_status_url(response)
    delay = _retry_after_seconds(response) if response is not None else 0
    deadline = time.monotonic() + timeout if timeout is not None else None
    progress = cmd.cli_ctx.get_progress_controller()
    progress.begin()
    try:
        while True:
            progress.add(message="Running")
            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise AzureResponseError("Log collection wait timed out after {} seconds.".format(timeout))
                if delay >= remaining:
                    time.sleep(remaining)
                    raise AzureResponseError("Log collection wait timed out after {} seconds.".format(timeout))
            if delay:
                time.sleep(delay)
            poll_response = send_raw_request(cmd.cli_ctx, "GET", status_url)
            operation = poll_response.json()
            if not isinstance(operation, dict) or not operation.get("status"):
                raise AzureResponseError("The operation-status response did not contain a status.")
            state = str(operation.get("status") or "")
            if state.lower() in _TERMINAL_OPERATION_STATES:
                break
            delay = interval if interval is not None else _retry_after_seconds(poll_response)
    finally:
        progress.end()

    if state.lower() != "succeeded":
        error = operation.get("error") or {}
        raise AzureResponseError("Log collection finished with status '{}'. {}: {}".format(
            state, error.get("code", "UnknownError"), error.get("message", "No error details were returned.")
        ))

    resource_id = (operation.get("properties") or {}).get("resourceId")
    if not resource_id:
        raise AzureResponseError(
            "The log collection succeeded, but its operation status did not return properties.resourceId."
        )
    return send_raw_request(
        cmd.cli_ctx, "GET", "{}?api-version={}".format(resource_id, API_VERSION)
    ).json()


def _start_log_collection(cmd, action, body, no_wait):
    response = send_raw_request(
        cmd.cli_ctx, "POST", _subscription_url(cmd, action, API_VERSION), body=json.dumps(body)
    )
    if no_wait:
        status_url = _unsigned_operation_status_url(cmd, _log_collection_status_url(response))
        return {"status": "Accepted", "operationStatusUrl": status_url}
    return _wait_for_log_collection(cmd, response)


def collect_logs(cmd, from_date, to_date, filter_roles=None, no_wait=False):
    body = _collection_time_range(from_date, to_date)
    if filter_roles:
        body["filterRoles"] = filter_roles
    return _start_log_collection(cmd, "collectLogs", body, no_wait)


def collect_logs_indirect(cmd, from_date, to_date, save_to_path, username=None, password=None,
                          filter_roles=None, no_wait=False):
    if not save_to_path or not save_to_path.strip():
        raise InvalidArgumentValueError("--save-to-path must not be empty.")
    body = _collection_time_range(from_date, to_date)
    body["saveToPath"] = save_to_path
    if username:
        if password is None:
            from knack.prompting import NoTTYException, prompt_pass
            try:
                password = prompt_pass("Password for the destination path: ")
            except NoTTYException:
                raise RequiredArgumentMissingError(
                    "--password is required with --username when no interactive terminal is available."
                ) from None
        body["userName"] = username
    if password is not None:
        body["userPassword"] = password
    if filter_roles:
        body["filterRoles"] = filter_roles
    return _start_log_collection(cmd, "collectLogsIndirect", body, no_wait)


def show_log_collection(cmd, job_id):
    _validate_job_id(job_id)
    url = _subscription_url(cmd, "logCollections/{}".format(job_id), API_VERSION)
    return send_raw_request(cmd.cli_ctx, "GET", url).json()


def wait_log_collection(cmd, job_id=None, operation_status_url=None, created=False, deleted=False,
                        updated=False, exists=False, custom=None, interval=None, timeout=3600):
    if job_id and operation_status_url:
        raise MutuallyExclusiveArgumentError("Use either --job-id or --operation-status-url, not both.")
    if not job_id and not operation_status_url:
        raise RequiredArgumentMissingError("Specify --job-id or --operation-status-url.")
    if timeout <= 0 or (interval is not None and interval <= 0):
        raise InvalidArgumentValueError("--timeout and --interval must be positive.")
    if operation_status_url:
        if any((created, deleted, updated, exists, custom)):
            raise MutuallyExclusiveArgumentError(
                "--operation-status-url waits for completion; do not combine it with wait-condition flags."
            )
        return _wait_for_log_collection(
            cmd, status_url=_unsigned_operation_status_url(cmd, operation_status_url),
            interval=interval, timeout=timeout,
        )

    from azure.cli.core.commands.command_operation import WaitCommandOperation
    result = WaitCommandOperation.wait({
        "cmd": cmd, "job_id": job_id, "created": created, "deleted": deleted,
        "updated": updated, "exists": exists, "custom": custom,
        "interval": interval if interval is not None else 30, "timeout": timeout,
    }, cli_ctx=cmd.cli_ctx, getter=show_log_collection)
    if isinstance(result, Exception):
        raise result
    return result


def list_log_collections(cmd, from_date):
    query = {"fromDate": _format_utc_datetime(_parse_utc_datetime(from_date, "--from-date"))}
    return _list_all_pages(cmd, _subscription_url(cmd, "logCollections", API_VERSION, query))
