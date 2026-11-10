# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import time
import uuid
from datetime import datetime, timezone
from urllib.parse import quote

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
# The billing commands use the newer preview, which adds deployment-manifest licenses and signatures.
BILLING_API_VERSION = "2026-09-01-preview"

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


def _wait_for_log_collection(cmd, response):
    # The Azure-AsyncOperation URL carries signed query parameters; never log or display it.
    status_url = response.headers.get("Azure-AsyncOperation")
    if not status_url:
        raise AzureResponseError(
            "The service accepted the log collection request but returned no Azure-AsyncOperation header."
        )

    delay = _retry_after_seconds(response)
    progress = cmd.cli_ctx.get_progress_controller()
    progress.begin()
    try:
        while True:
            progress.add(message="Running")
            time.sleep(delay)
            poll_response = send_raw_request(cmd.cli_ctx, "GET", status_url)
            operation = poll_response.json()
            state = str(operation.get("status") or "")
            if state.lower() in _TERMINAL_OPERATION_STATES:
                break
            delay = _retry_after_seconds(poll_response)
    finally:
        progress.end()

    if state.lower() != "succeeded":
        error = operation.get("error") or {}
        raise AzureResponseError("Log collection finished with status '{}'. {}: {}".format(
            state, error.get("code", "UnknownError"), error.get("message", "No error details were returned.")
        ))

    resource_id = (operation.get("properties") or {}).get("resourceId")
    if not resource_id:
        logger.warning("The log collection succeeded, but the service did not return the job's resource ID.")
        return operation
    return send_raw_request(
        cmd.cli_ctx, "GET", "{}?api-version={}".format(resource_id, API_VERSION)
    ).json()


def _start_log_collection(cmd, action, body, no_wait):
    response = send_raw_request(
        cmd.cli_ctx, "POST", _subscription_url(cmd, action, API_VERSION), body=json.dumps(body)
    )
    if no_wait:
        logger.warning(
            "Log collection was accepted. Use 'az aldo log-collection list --from-date <date-time>' "
            "to find the job, then 'az aldo log-collection wait' to wait for it."
        )
        return None
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


def list_log_collections(cmd, from_date):
    query = {"fromDate": _format_utc_datetime(_parse_utc_datetime(from_date, "--from-date"))}
    return _list_all_pages(cmd, _subscription_url(cmd, "logCollections", API_VERSION, query))


# ---------------------------------------------------------------------------
# Billing configurations
# ---------------------------------------------------------------------------

def _billing_configuration_url(cmd, path=""):
    return _subscription_url(cmd, "billingConfigurations/default" + path, BILLING_API_VERSION)


def _read_manifest_properties(manifest):
    from azure.cli.core.util import get_file_json
    try:
        content = get_file_json(manifest, preserve_order=True)
    except OSError as ex:
        raise InvalidArgumentValueError("Unable to read --manifest '{}': {}".format(manifest, ex)) from None
    if not isinstance(content, dict):
        raise InvalidArgumentValueError("--manifest must contain a JSON object.")
    # Accept a full request body ({"properties": {...}}) or the bare properties object. Values are
    # forwarded unchanged because the service validates the Azure-issued manifest signature.
    properties = content.get("properties", content)
    if not isinstance(properties, dict):
        raise InvalidArgumentValueError("The 'properties' value in --manifest must be a JSON object.")
    return properties


def _billing_period(cores, pricing_model, start_date, end_date):
    period = {"cores": cores, "pricingModel": pricing_model, "startDate": start_date}
    if end_date is not None:
        period["endDate"] = end_date
    return period


def _build_billing_properties(values):
    required = {
        "--disconnected-operation": values["disconnected_operation"],
        "--stamp-id": values["stamp_id"],
        "--location": values["location"],
        "--billing-model": values["billing_model"],
        "--connection-intent": values["connection_intent"],
        "--auto-renew": values["auto_renew"],
        "--billing-status": values["billing_status"],
        "--cores": values["cores"],
        "--pricing-model": values["pricing_model"],
        "--start-date": values["start_date"],
    }
    missing = [option for option, value in required.items() if value is None]
    if missing:
        raise RequiredArgumentMissingError(
            "Provide --manifest, or all of these arguments: {}.".format(", ".join(missing))
        )

    upcoming = {
        "--upcoming-cores": values["upcoming_cores"],
        "--upcoming-pricing-model": values["upcoming_pricing_model"],
        "--upcoming-start-date": values["upcoming_start_date"],
    }
    if any(value is not None for value in list(upcoming.values()) + [values["upcoming_end_date"]]):
        missing = [option for option, value in upcoming.items() if value is None]
        if missing:
            raise RequiredArgumentMissingError(
                "An upcoming billing period also requires: {}.".format(", ".join(missing))
            )

    from azure.mgmt.core.tools import is_valid_resource_id, parse_resource_id
    if not is_valid_resource_id(values["disconnected_operation"]):
        raise InvalidArgumentValueError("--disconnected-operation must be an Azure resource ID.")

    billing_configuration = {
        "autoRenew": values["auto_renew"],
        "billingStatus": values["billing_status"],
        "current": _billing_period(
            values["cores"], values["pricing_model"], values["start_date"], values["end_date"]
        ),
    }
    if values["upcoming_cores"] is not None:
        billing_configuration["upcoming"] = _billing_period(
            values["upcoming_cores"], values["upcoming_pricing_model"],
            values["upcoming_start_date"], values["upcoming_end_date"]
        )

    properties = {
        "resourceId": values["disconnected_operation"],
        "resourceName": parse_resource_id(values["disconnected_operation"])["name"],
        "stampId": values["stamp_id"],
        "location": values["location"],
        "billingModel": values["billing_model"],
        "connectionIntent": values["connection_intent"],
    }
    if values["cloud"] is not None:
        properties["cloud"] = values["cloud"]
    properties["billingConfiguration"] = billing_configuration

    benefit_plans = {
        key: value for key, value in {
            "azureHybridWindowsServerBenefit": values["azure_hybrid_benefit"],
            "windowsServerVmCount": values["windows_server_vm_count"],
        }.items() if value is not None
    }
    if benefit_plans:
        properties["benefitPlans"] = benefit_plans
    return properties


def show_billing_configuration(cmd):
    return send_raw_request(cmd.cli_ctx, "GET", _billing_configuration_url(cmd)).json()


def create_billing_configuration(cmd, manifest=None, disconnected_operation=None, stamp_id=None,  # pylint: disable=too-many-locals
                                 location=None, billing_model=None, connection_intent=None, cloud=None,
                                 auto_renew=None, billing_status=None, cores=None, pricing_model=None,
                                 start_date=None, end_date=None, upcoming_cores=None, upcoming_pricing_model=None,
                                 upcoming_start_date=None, upcoming_end_date=None, azure_hybrid_benefit=None,
                                 windows_server_vm_count=None, if_match=None, if_none_match=None):
    values = {
        "disconnected_operation": disconnected_operation,
        "stamp_id": stamp_id,
        "location": location,
        "billing_model": billing_model,
        "connection_intent": connection_intent,
        "cloud": cloud,
        "auto_renew": auto_renew,
        "billing_status": billing_status,
        "cores": cores,
        "pricing_model": pricing_model,
        "start_date": start_date,
        "end_date": end_date,
        "upcoming_cores": upcoming_cores,
        "upcoming_pricing_model": upcoming_pricing_model,
        "upcoming_start_date": upcoming_start_date,
        "upcoming_end_date": upcoming_end_date,
        "azure_hybrid_benefit": azure_hybrid_benefit,
        "windows_server_vm_count": windows_server_vm_count,
    }
    if manifest is not None:
        if any(value is not None for value in values.values()):
            raise MutuallyExclusiveArgumentError(
                "--manifest cannot be combined with individual billing configuration arguments."
            )
        properties = _read_manifest_properties(manifest)
    else:
        properties = _build_billing_properties(values)

    headers = {
        key: value for key, value in {"If-Match": if_match, "If-None-Match": if_none_match}.items()
        if value is not None
    }
    response = send_raw_request(
        cmd.cli_ctx, "PUT", _billing_configuration_url(cmd), body=json.dumps({"properties": properties}),
        headers=[json.dumps(headers)] if headers else None
    )
    return response.json()


def show_billing_configuration_snapshot(cmd, snapshot_name):
    url = _billing_configuration_url(cmd, "/snapshots/{}".format(quote(snapshot_name, safe="")))
    return send_raw_request(cmd.cli_ctx, "GET", url).json()


def list_billing_configuration_snapshots(cmd):
    return _list_all_pages(cmd, _billing_configuration_url(cmd, "/snapshots"))
