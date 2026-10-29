# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=import-error,no-name-in-module
"""Individual Standard workflow state through the documented FlowState setting."""

from contextlib import contextmanager
import logging
import re
from urllib.parse import urlencode

from azure.cli.core.azclierror import (
    ClientRequestError, InvalidArgumentValueError, ResourceNotFoundError, UnauthorizedError)
from azure.cli.core.util import user_confirmation
from knack.log import get_logger
from knack.util import CLIError
from requests.exceptions import RequestException

from ._constants import LOGICAPP_REDACTION_SENTINEL
from ._json import strict_json_loads
from ._runtime_client import workflow_path
from ._workflow import validate_workflow_name
from ._workflow_discovery import workflow_metadata

logger = get_logger(__name__)
_REQUEST_ERRORS = (CLIError, RequestException)
_STATES = ("Enabled", "Disabled")


class _ContractError(ClientRequestError):
    pass


class _SuppressHttpDetails(logging.Filter):  # pylint: disable=too-few-public-methods
    def filter(self, _record):
        return False


@contextmanager
def _private_http_logs():
    # The CLI REST helper logs complete request/response bodies under --debug.
    # App settings contain secrets; neither those bodies nor provider errors
    # belong in the output of these workflow commands.
    http_logger = get_logger("azure.cli.core.util")
    suppress = _SuppressHttpDetails()
    http_logger.addFilter(suppress)
    try:
        yield
    finally:
        http_logger.removeFilter(suppress)


def _failure_kind(error):
    status = getattr(getattr(error, "response", None), "status_code", None)
    if isinstance(error, ResourceNotFoundError) or status == 404:
        return "notFound"
    if isinstance(error, UnauthorizedError) or status in (401, 403):
        return "unauthorized"
    return "unavailable"


def _read_error(error, description):
    if isinstance(error, _ContractError):
        return ClientRequestError(str(error))
    failure = _failure_kind(error)
    if failure == "notFound":
        return ResourceNotFoundError("{} or its app target was not found.".format(description))
    if failure == "unauthorized":
        return UnauthorizedError("Access to {} was denied.".format(description))
    return ClientRequestError(
        "Could not read {}. Provider response details were not exposed.".format(description),
        recommendation="Check Azure CLI sign-in, caller permissions and runtime availability.")


def _metadata_response(client, workflow):
    with _private_http_logs():
        return client._send("GET", client._build_url(workflow_path(workflow)))


def _parse_metadata(response, workflow):
    if getattr(response, "status_code", None) != 200:
        raise _ContractError("The runtime returned an unexpected workflow metadata receipt.")
    try:
        payload = strict_json_loads(getattr(response, "content", None))
        metadata = workflow_metadata(payload, expected_name=workflow)
    except (TypeError, ValueError, RecursionError, ClientRequestError):
        raise _ContractError("The runtime returned malformed or unsupported workflow metadata.") from None
    if metadata["state"] not in _STATES:
        raise _ContractError("The runtime did not report a supported Enabled/Disabled workflow state.")
    return metadata


def _metadata(client, workflow):
    return _parse_metadata(_metadata_response(client, workflow), workflow)


def _settings_url(client, read=False):
    return "{}/config/appsettings{}?{}".format(
        client.site_resource_id, "/list" if read else "", urlencode({"api-version": client.api_version}))


def _settings(client, method="POST", body=None):
    with _private_http_logs():
        response = client._send(method, _settings_url(client, read=method == "POST"), body=body)
    if getattr(response, "status_code", None) != 200:
        raise _ContractError("The app settings service returned an unexpected receipt.")
    try:
        payload = strict_json_loads(getattr(response, "content", None))
    except (TypeError, ValueError, RecursionError):
        raise _ContractError("The app settings service returned invalid JSON.") from None
    if not isinstance(payload, dict) or "error" in payload or not isinstance(payload.get("properties"), dict):
        raise _ContractError("The app settings service returned an invalid settings envelope.")
    resource_id = payload.get("id")
    if resource_id is not None and (not isinstance(resource_id, str)
                                    or resource_id.casefold() != (client.site_resource_id + "/config/appsettings").casefold()):
        raise _ContractError("The app settings service returned a different resource.")
    settings = payload["properties"]
    folded = set()
    for key, value in settings.items():
        if not isinstance(key, str) or not key or not isinstance(value, str):
            raise _ContractError("The app settings service returned an invalid setting.")
        if key.casefold() in folded:
            raise _ContractError("The app settings service returned ambiguous case-duplicate keys.")
        folded.add(key.casefold())
        if value == LOGICAPP_REDACTION_SENTINEL or (len(value) >= 3 and not value.strip("*")):
            raise _ContractError("Masked app settings cannot be safely resent. No masked values were exposed.")
    return dict(settings)


def _state_key(settings, workflow):
    canonical = "Workflows.{}.FlowState".format(workflow)
    return next((key for key in settings if key.casefold() == canonical.casefold()), canonical)


def _configured_state(settings, key):
    state = settings.get(key)
    if state is not None and state not in _STATES:
        raise ClientRequestError("The configured workflow FlowState is not Enabled or Disabled.")
    return state


def _result(workflow, kind, requested, configured, observed, action, observation_error=None):
    convergence = "unknown" if observed is None else ("converged" if observed == requested else "pending")
    if convergence != "converged":
        logger.warning(
            "Workflow FlowState is configured as %s, but runtime convergence is %s. "
            "No request was retried. Inspect workflow show before relying on trigger state.", configured, convergence)
    return {"workflow": workflow, "workflowKind": kind, "action": action,
            "requestedState": requested, "configuredState": configured, "runtimeState": observed,
            "runtimeConvergence": convergence, "runtimeObservationError": observation_error,
            "verification": "appSettingsReadback"}


def _observe_after_configuration(client, workflow, kind):
    try:
        response = _metadata_response(client, workflow)
    except _REQUEST_ERRORS as ex:
        return None, _failure_kind(ex)
    try:
        metadata = _parse_metadata(response, workflow)
    except _ContractError:
        raise ClientRequestError(
            "FlowState was verified in app settings, but runtime metadata was invalid. "
            "Runtime state is unknown; no retry or rollback was attempted.") from None
    if metadata["kind"] != kind:
        raise ClientRequestError(
            "FlowState was verified in app settings, but the workflow kind changed. "
            "Runtime state was not verified; no retry or rollback was attempted.")
    return metadata["state"], None


def set_workflow_state(client, workflow, state, yes=False, allow_non_atomic=False):
    if not workflow:
        raise InvalidArgumentValueError("--workflow is required.")
    validate_workflow_name(workflow)
    if state not in _STATES:
        raise InvalidArgumentValueError("Workflow state must be Enabled or Disabled.")
    if client.is_local:
        raise InvalidArgumentValueError(
            "Individual workflow enable/disable is not supported through the local runtime API.",
            recommendation="For local development, edit the documented Workflows.<name>.FlowState "
                           "value in local.settings.json and restart your own host. "
                           "This command does not edit local files or restart any host.")
    if not re.fullmatch(
            r"/subscriptions/[^/?#%\\]+/resourceGroups/[^/?#%\\]+/providers/Microsoft\.Web/sites/[A-Za-z0-9-]+",
            client.site_resource_id, flags=re.IGNORECASE):
        raise InvalidArgumentValueError(
            "Workflow state commands require a Standard app site target, not a slot or nested resource.")
    if not allow_non_atomic:
        raise InvalidArgumentValueError(
            "Workflow state changes require --allow-non-atomic: App Service replaces the entire app settings map.",
            recommendation="Coordinate with all app-settings writers. Snapshot checks cannot prevent "
                           "a change between the final read and PUT; unrelated settings can be lost.")
    try:
        before = _metadata(client, workflow)
    except _REQUEST_ERRORS as ex:
        raise _read_error(ex, "workflow metadata") from None
    try:
        settings = _settings(client)
    except _REQUEST_ERRORS as ex:
        raise _read_error(ex, "app settings") from None
    key = _state_key(settings, workflow)
    configured = _configured_state(settings, key)
    if configured == state:
        return _result(workflow, before["kind"], state, configured, before["state"], "unchanged")
    user_confirmation(
        "Set workflow '{}' in '{}' to {}? Only its FlowState value changes, but all app settings "
        "are resent and the update is not transactional. Other settings are retained from the "
        "snapshot. Disabling does not cancel runs; enabling may process trigger backlog.".format(
            workflow, client.site_resource_id, state), yes)
    try:
        current = _metadata(client, workflow)
        latest = _settings(client)
    except _REQUEST_ERRORS as ex:
        raise _read_error(ex, "the preflight snapshot") from None
    if current["kind"] != before["kind"] or current["state"] != before["state"] or latest != settings:
        raise ClientRequestError(
            "The workflow or app settings changed during confirmation. No settings update was attempted.",
            recommendation="Review the current workflow and coordinate with other settings writers before retrying.")
    expected = dict(settings)
    expected[key] = state
    try:
        receipt = _settings(client, method="PUT", body={"properties": expected})
    except _REQUEST_ERRORS:
        raise ClientRequestError(
            "The app settings update failed or returned an invalid receipt. Its outcome may be uncertain. "
            "No retry or rollback was attempted; inspect configuration and workflow state before retrying.") from None
    if receipt != expected:
        raise ClientRequestError(
            "The update receipt did not match the expected settings. Configuration may have changed; "
            "no retry or rollback was attempted.")
    try:
        checked = _settings(client)
    except _REQUEST_ERRORS:
        raise ClientRequestError(
            "The settings update was acknowledged, but configuration readback failed. "
            "No success, retry or rollback is claimed; inspect configuration before retrying.") from None
    if checked != expected:
        raise ClientRequestError(
            "App settings changed after the update or readback did not match. "
            "No retry or rollback overwrote potentially newer settings.")
    observed, observation_error = _observe_after_configuration(client, workflow, before["kind"])
    return _result(workflow, before["kind"], state, checked[key], observed, "configured", observation_error)
