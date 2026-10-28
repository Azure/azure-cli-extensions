# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=import-error,no-name-in-module
"""Stateful execution controls with bounded, non-retried mutations."""

from collections import OrderedDict
from copy import deepcopy
import re
import time
from urllib.parse import unquote, urlsplit

from azure.cli.core.azclierror import ClientRequestError, InvalidArgumentValueError
from azure.cli.core.util import user_confirmation
from knack.log import get_logger

from ._execution_transport import DeadlineExpired, ExecutionError, ExecutionTransport
from ._runtime_client import (
    trigger_history_path, trigger_history_resubmit_path,
    run_action_path, workflow_path, workflow_run_cancel_path, workflow_run_path,
    workflow_run_resubmit_path, workflow_trigger_path)
from ._json import json_equal
from ._workflow import validate_workflow_name
from ._workflow_discovery import workflow_metadata

logger = get_logger(__name__)
_TERMINAL = ("Succeeded", "Failed", "Cancelled", "TimedOut", "Aborted", "Faulted", "Skipped", "Ignored")
_ACTIVE = ("Running", "Waiting", "Paused", "Suspended")
_KNOWN = {value.casefold(): value for value in _TERMINAL + _ACTIVE}
_PREFLIGHT_TIMEOUT = 60


def _segment(value, flag, upstream=False):
    valid = (isinstance(value, str) and 0 < len(value) <= 256 and value not in (".", "..")
             and value == value.strip() and not re.search(r"[/\\%?#=\x00-\x1f\x7f]", value))
    if not valid:
        if upstream:
            raise ExecutionError("invalidResponse", "Execution endpoint returned an invalid identifier.")
        raise InvalidArgumentValueError("{} must be a non-empty single identifier, not a path or URL.".format(flag))
    return value


def validate_execution_options(workflow, run_id, timeout=None, interval=None):
    if not workflow:
        raise InvalidArgumentValueError("--workflow is required.")
    validate_workflow_name(workflow)
    _segment(run_id, "--run-id")
    for value, flag, maximum in ((timeout, "--timeout", 86400), (interval, "--interval", 300)):
        if value is not None and (isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum):
            raise InvalidArgumentValueError("{} must be a whole number between 1 and {} seconds.".format(flag, maximum))
    if timeout is not None and interval is not None and interval > timeout:
        raise InvalidArgumentValueError("--interval must not exceed --timeout.")


def _field(payload, name):
    if not isinstance(payload, dict):
        return None
    matches = [value for key, value in payload.items() if key.casefold() == name.casefold()]
    if len(matches) > 1:
        raise ExecutionError("invalidResponse", "Execution endpoint returned ambiguous fields.")
    return matches[0] if matches else None


def _resubmit_new_run_id(headers, source_run=None):
    new_id = _field(dict(headers), "x-ms-workflow-run-id")
    if new_id is not None:
        _segment(new_id, "new run", upstream=True)
        if not re.fullmatch(r"[A-Za-z0-9._-]+", new_id) or new_id == source_run:
            raise ExecutionError("invalidResponse", "Resubmission returned a conflicting or invalid new run identity.")
    return new_id


def _object(payload):
    if not isinstance(payload, dict):
        raise ExecutionError("invalidResponse", "Execution endpoint returned an invalid object.")
    return payload


def _properties(payload):
    _object(payload)
    properties = _field(payload, "properties")
    return payload if properties is None else _object(properties)


def _read(transport, path, deadline, params=None):
    receipt = transport.request("GET", path, deadline, params)
    if receipt["statusCode"] != 200:
        raise ExecutionError("invalidResponse", "Execution read did not return HTTP 200.")
    payload = _object(receipt["payload"])
    if _field(payload, "error") is not None:
        raise ExecutionError("invalidResponse", "Execution read returned an error envelope.")
    return payload


def _stateful(transport, workflow, deadline):
    try:
        metadata = workflow_metadata(_read(transport, workflow_path(workflow), deadline), expected_name=workflow)
    except ClientRequestError as ex:
        if isinstance(ex, ExecutionError):
            raise
        raise ExecutionError("invalidResponse", "Execution endpoint returned invalid workflow metadata.") from None
    if metadata["kind"] != "Stateful":
        raise InvalidArgumentValueError(
            "Execution controls require a Stateful workflow. Stateless debug history does not enable resubmission.")


def _run(transport, workflow, run_id, deadline):
    payload = _read(transport, workflow_run_path(workflow, run_id), deadline)
    return _run_state(payload, run_id)


def _run_state(payload, run_id):
    if _field(payload, "name") != run_id:
        raise ExecutionError("invalidResponse", "Execution endpoint returned a different or unidentified run.")
    props = _properties(payload)
    raw_status = _field(props, "status")
    status = _KNOWN.get(raw_status.casefold()) if isinstance(raw_status, str) else None
    if status is None:
        raise ExecutionError("unknownStatus", "Execution endpoint reported a missing or unrecognized run status.")
    return status, props


def _correlation(value):
    if isinstance(value, str) and re.fullmatch(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", value):
        return value
    return None


def _observe(result, status, props):
    result.update(status=status, terminal=status in _TERMINAL,
                  runCorrelationId=_correlation(_field(props, "correlationId")))


def _report(workflow, run_id, operation):
    return {"schemaVersion": "1.0", "workflow": workflow, "workflowKind": None, "runId": run_id,
            "operation": operation, "action": None, "status": None, "terminal": None, "outcome": None,
            "requestAcknowledged": False, "runCorrelationId": None, "requestCorrelationId": None,
            "exitCode": 0, "error": None}


def _unsent_mutation(result, error, attempted):
    if not result["requestAcknowledged"] and (not attempted or error.before_send):
        result["action"] = None
        return True
    return False


def _failure(result, error, mutated=False):
    if mutated and _unsent_mutation(result, error, mutated):
        mutated = False
        result["message"] = (
            "Credential acquisition failed before submission. " if error.kind == "authentication"
            else "Execution request failed before submission. ")
        result["message"] += "No mutation request was sent."
    result.update(outcome="observationFailed" if mutated else "readFailed", exitCode=1,
                  error={"kind": error.kind, "message": str(error)})
    if mutated:
        result["message"] = (
            "The request was acknowledged, but subsequent verification failed. "
            if result["requestAcknowledged"] else "The request may have been accepted. ")
        result["message"] += "No retry was attempted; inspect runs before retrying."
    return result


def _poll(transport, result, deadline, interval, expected="Succeeded"):
    while time.monotonic() < deadline:
        status, props = _run(transport, result["workflow"], result["runId"], deadline)
        _observe(result, status, props)
        if status in _TERMINAL:
            result.update(outcome="completed" if status == expected else "terminalNotExpected",
                          exitCode=0 if status == expected else 4)
            return result
        remaining = deadline - time.monotonic()
        if remaining > 0:
            time.sleep(min(interval, remaining))
    raise DeadlineExpired()


def wait_run(client, workflow, run_id, timeout=300, interval=5):
    validate_execution_options(workflow, run_id, timeout, interval)
    result = _report(workflow, run_id, "wait")
    result["action"] = "observe"
    deadline = time.monotonic() + timeout
    transport = ExecutionTransport(client)
    try:
        _stateful(transport, workflow, deadline)
        result["workflowKind"] = "Stateful"
        return _poll(transport, result, deadline, interval)
    except DeadlineExpired:
        result.update(outcome="waitTimedOut", exitCode=2)
        result["message"] = "The CLI wait deadline expired. No cancellation was requested."
        return result
    except ExecutionError as ex:
        return _failure(result, ex)


def cancel_run(client, workflow, run_id, yes=False, wait=False, timeout=300, interval=5):
    validate_execution_options(workflow, run_id, timeout, interval)
    result = _report(workflow, run_id, "cancel")
    transport = ExecutionTransport(client)
    deadline = time.monotonic() + _PREFLIGHT_TIMEOUT
    submitted = False
    try:
        _stateful(transport, workflow, deadline)
        result["workflowKind"] = "Stateful"
        status, props = _run(transport, workflow, run_id, deadline)
        _observe(result, status, props)
        if status in _TERMINAL:
            result.update(action="alreadyTerminal", outcome="unchanged")
            return result
        user_confirmation(
            "Request cancellation of run '{}' in workflow '{}' at '{}'? Cancellation is asynchronous, "
            "does not roll back side effects, and may not stop in-flight actions.".format(
                run_id, workflow, client.site_resource_id), yes)
        deadline = time.monotonic() + _PREFLIGHT_TIMEOUT
        _stateful(transport, workflow, deadline)
        status, props = _run(transport, workflow, run_id, deadline)
        _observe(result, status, props)
        if status in _TERMINAL:
            result.update(action="alreadyTerminal", outcome="unchanged")
            return result
        result["action"] = "cancelAttempted"
        submitted = True
        receipt = transport.request("POST", workflow_run_cancel_path(workflow, run_id), deadline)
        if receipt["statusCode"] not in (200, 202, 204) or receipt["payload"] is not None:
            raise ExecutionError("invalidResponse", "Cancellation returned an unexpected acknowledgement.")
        result["action"] = "cancelRequested"
        result["requestAcknowledged"] = True
        result["requestCorrelationId"] = _correlation(_field(dict(receipt["headers"]), "x-ms-correlation-id"))
        if wait:
            deadline = time.monotonic() + timeout
            return _poll(transport, result, deadline, interval, expected="Cancelled")
        status, props = _run(transport, workflow, run_id, deadline)
        _observe(result, status, props)
        result["outcome"] = ("cancelled" if status == "Cancelled" else "terminalNotCancelled"
                             if status in _TERMINAL else "pending")
        if result["outcome"] == "terminalNotCancelled":
            result["exitCode"] = 4
        return result
    except DeadlineExpired as ex:
        unsent = _unsent_mutation(result, ex, submitted)
        result.update(outcome="waitTimedOut" if wait and result["requestAcknowledged"]
                      else "requestDeadlineExpired", exitCode=2)
        result["message"] = (
            "Deadline expired before submission. No cancellation request was sent."
            if unsent else "Deadline expired; no request was retried. Cancellation is not verified.")
        return result
    except ExecutionError as ex:
        return _failure(result, ex, submitted)


def validate_history_options(workflow, trigger, history_name):
    if not workflow:
        raise InvalidArgumentValueError("--workflow is required.")
    validate_workflow_name(workflow)
    _segment(trigger, "--trigger")
    _segment(history_name, "--history-name")


def validate_action_resubmit_options(workflow, run_id, action):
    validate_execution_options(workflow, run_id)
    _segment(action, "--action")


def _selected_identity(payload, name, path, client):
    if _field(payload, "name") != name:
        raise ExecutionError("invalidResponse", "Execution endpoint returned a different or unidentified resource.")
    identifier = _field(payload, "id")
    if identifier is None:
        return
    relative = "/" + unquote(path)
    expected = unquote(urlsplit(client._build_url(path)).path)  # pylint: disable=protected-access
    if not isinstance(identifier, str):
        raise ExecutionError("invalidResponse", "Execution endpoint returned an invalid resource identity.")
    identifier = unquote(identifier)
    if (identifier != relative and
            not (identifier.endswith(relative)
                 and identifier[:-len(relative)].casefold() == expected[:-len(relative)].casefold())):
        raise ExecutionError("invalidResponse", "Execution endpoint returned a conflicting resource identity.")


def _stable_execution_snapshot(props):
    snapshot = {name: _field(props, name) for name in (
        "status", "code", "startTime", "endTime", "correlationId", "canResubmit")}
    # Signed content links are regenerated on reads and are not revision evidence.
    for name, fields in (
            ("workflow", ("id", "name", "version")),
            ("trigger", ("name", "status", "code", "startTime", "endTime")),
            ("correlation", ("actionTrackingId", "clientTrackingId", "trackingId"))):
        value = _field(props, name)
        snapshot[name] = None if value is None else {
            field: _field(_object(value), field) for field in fields}
    return snapshot


def _selected_action(transport, client, workflow, run_id, action, deadline):
    source = _read(transport, workflow_run_path(workflow, run_id), deadline)
    _selected_identity(source, run_id, workflow_run_path(workflow, run_id), client)
    status, props = _run_state(source, run_id)
    if status not in _TERMINAL:
        raise ExecutionError("sourceNotCompleted", "Action resubmission requires a completed source run.")
    path = run_action_path(workflow, run_id, action)
    selected = _read(transport, path, deadline)
    _selected_identity(selected, action, path, client)
    selected_props = _properties(selected)
    action_status = _field(selected_props, "status")
    normalized = _KNOWN.get(action_status.casefold()) if isinstance(action_status, str) else None
    if (normalized not in _TERMINAL or normalized in ("Skipped", "Ignored")
            or _field(selected_props, "canResubmit") is not True):
        raise ExecutionError(
            "actionNotEligible", "The runtime did not advertise this executed action as resubmittable. "
            "No feature was enabled and no resubmit was attempted.")
    return status, props, [_stable_execution_snapshot(props), _stable_execution_snapshot(selected_props)]


def resubmit_run_action(client, workflow, run_id, action, yes=False):
    validate_action_resubmit_options(workflow, run_id, action)
    result = _report(workflow, run_id, "actionResubmit")
    result.update(sourceRunId=run_id, actionName=action, newRunId=None, newRunStatus=None)
    transport = ExecutionTransport(client)
    deadline = time.monotonic() + _PREFLIGHT_TIMEOUT
    submitted = False
    try:
        _stateful(transport, workflow, deadline)
        result["workflowKind"] = "Stateful"
        status, props, before = _selected_action(transport, client, workflow, run_id, action, deadline)
        _observe(result, status, props)
        user_confirmation(
            "Resubmit action '{}' from completed run '{}' in workflow '{}' at '{}' as a NEW execution? "
            "The runtime uses retained history and the source workflow version. The selected action "
            "and dependent actions can repeat external effects; current connections/settings still apply. "
            "This is not in-place resume or exactly-once recovery.".format(
                action, run_id, workflow, client.site_resource_id), yes)
        deadline = time.monotonic() + _PREFLIGHT_TIMEOUT
        _stateful(transport, workflow, deadline)
        status, props, after = _selected_action(transport, client, workflow, run_id, action, deadline)
        _observe(result, status, props)
        if not json_equal(before, after):
            raise ExecutionError("changed", "The selected run/action changed during confirmation. No resubmit was attempted.")
        result["action"] = "resubmitAttempted"
        submitted = True
        receipt = transport.request(
            "POST", workflow_run_resubmit_path(workflow, run_id), deadline,
            body={"actionsToResubmit": [{"name": action}]})
        if type(receipt["statusCode"]) is not int or receipt["statusCode"] != 202 or receipt["payload"] is not None:  # pylint: disable=unidiomatic-typecheck
            raise ExecutionError("invalidResponse", "Action resubmission returned an unexpected acknowledgement.")
        result.update(action="resubmitRequested", requestAcknowledged=True)
        result["requestCorrelationId"] = _correlation(_field(dict(receipt["headers"]), "x-ms-correlation-id"))
        new_id = _resubmit_new_run_id(receipt["headers"], run_id)
        result.update(newRunId=new_id, outcome="accepted" if new_id else "acceptedNewRunIdUnknown")
        result["message"] = (
            "A new execution was requested, not observed completed. The source run was not resumed "
            "or overwritten. No request was retried; follow the new identity separately.")
        return result
    except DeadlineExpired as ex:
        unsent = _unsent_mutation(result, ex, submitted)
        result.update(outcome="requestDeadlineExpired", exitCode=2)
        result["message"] = ("Deadline expired before submission. No resubmit was attempted."
                             if unsent else "Deadline expired; the resubmit outcome is uncertain. No retry was attempted.")
        return result
    except ExecutionError as ex:
        return _failure(result, ex, submitted)


def _history_snapshot(payload):
    props = _properties(payload)
    snapshot = _stable_execution_snapshot(props)
    snapshot.update({name: _field(props, name) for name in (
        "fired", "state", "changedTime", "workflowVersion", "version", "etag", "scheduledTime", "waitEndTime")})
    snapshot["identity"] = {name: _field(payload, name) for name in ("id", "name", "type", "etag")}
    run = _field(props, "run")
    snapshot["run"] = None if run is None else {
        name: _field(_object(run), name) for name in ("id", "name", "version")}
    for name in ("inputsLink", "outputsLink"):
        link = _field(props, name)
        snapshot[name] = None if link is None else {
            field: _field(_object(link), field) for field in ("contentHash", "contentVersion", "contentSize")}
    return deepcopy(snapshot)


def _selected_history(transport, client, workflow, trigger, history_name, deadline):
    selected_trigger = _read(transport, workflow_trigger_path(workflow, trigger), deadline)
    _selected_identity(selected_trigger, trigger, workflow_trigger_path(workflow, trigger), client)
    history = _read(transport, trigger_history_path(workflow, trigger, history_name), deadline)
    _selected_identity(history, history_name, trigger_history_path(workflow, trigger, history_name), client)
    if _field(_properties(history), "fired") is not True:
        raise ExecutionError("historyNotFired", "Selected retained history did not fire. No resubmit was attempted.")
    return _history_snapshot(selected_trigger), _history_snapshot(history)


def resubmit_trigger_history(client, workflow, trigger, history_name, yes=False):
    validate_history_options(workflow, trigger, history_name)
    result = _report(workflow, None, "triggerHistoryResubmit")
    result.update(newRunId=None, newRunStatus=None, triggerName=trigger, triggerHistoryId=history_name)
    transport = ExecutionTransport(client)
    deadline = time.monotonic() + _PREFLIGHT_TIMEOUT
    submitted = False
    try:
        _stateful(transport, workflow, deadline)
        result["workflowKind"] = "Stateful"
        before = _selected_history(transport, client, workflow, trigger, history_name, deadline)
        user_confirmation(
            "Resubmit trigger '{}' history '{}' in workflow '{}' at '{}' as a NEW execution? "
            "This can duplicate external side effects. It is not resume, recovery or exactly-once delivery, "
            "and does not modify a source run.".format(
                trigger, history_name, workflow, client.site_resource_id), yes)
        deadline = time.monotonic() + _PREFLIGHT_TIMEOUT
        _stateful(transport, workflow, deadline)
        after = _selected_history(transport, client, workflow, trigger, history_name, deadline)
        if not all(json_equal(previous, current) for previous, current in zip(before, after)):
            raise ExecutionError("changed", "The selected trigger/history changed during confirmation. No resubmit was attempted.")
        result["action"] = "resubmitAttempted"
        submitted = True
        receipt = transport.request("POST", trigger_history_resubmit_path(workflow, trigger, history_name), deadline)
        if type(receipt["statusCode"]) is not int or receipt["statusCode"] != 202 or receipt["payload"] is not None:  # pylint: disable=unidiomatic-typecheck
            raise ExecutionError("invalidResponse", "Resubmission returned an unexpected acknowledgement.")
        result["action"] = "resubmitRequested"
        result["requestAcknowledged"] = True
        result["requestCorrelationId"] = _correlation(_field(dict(receipt["headers"]), "x-ms-correlation-id"))
        new_id = _resubmit_new_run_id(receipt["headers"])
        result.update(newRunId=new_id, outcome="accepted" if new_id else "acceptedNewRunIdUnknown")
        result["message"] = ("A new execution was requested, not observed completed. "
                             "No request was retried; no source run was selected or changed.")
        return result
    except DeadlineExpired as ex:
        unsent = _unsent_mutation(result, ex, submitted)
        result.update(outcome="requestDeadlineExpired", exitCode=2)
        result["message"] = ("Deadline expired; the resubmit outcome is uncertain. No retry was attempted."
                             if not unsent else "Deadline expired before submission. No resubmit was attempted.")
        return result
    except ExecutionError as ex:
        return _failure(result, ex, submitted)


def execution_table_format(result):
    row = OrderedDict((("Workflow", result["workflow"]), ("Run", result["runId"]),
                       ("Operation", result["operation"]), ("Status", result["status"]),
                       ("Outcome", result["outcome"]), ("NewRun", result.get("newRunId")),
                       ("Error", (result.get("error") or {}).get("kind")),
                       ("ExitCode", result["exitCode"])))
    if result["operation"] == "triggerHistoryResubmit":
        row["Trigger"] = result["triggerName"]
        row["History"] = result["triggerHistoryId"]
    elif result["operation"] == "actionResubmit":
        row["Action"] = result["actionName"]
    return [row]


def finish_execution_command(cmd, report):
    if report["exitCode"]:
        from knack.events import EVENT_CLI_POST_EXECUTE, EVENT_CLI_SUCCESSFUL_EXECUTE

        def cleanup(_cli, **_kwargs):
            cmd.cli_ctx.unregister_event(EVENT_CLI_SUCCESSFUL_EXECUTE, finish)
            cmd.cli_ctx.unregister_event(EVENT_CLI_POST_EXECUTE, cleanup)

        def finish(_cli, **_kwargs):
            cleanup(_cli)
            raise SystemExit(report["exitCode"])

        cmd.cli_ctx.register_event(EVENT_CLI_SUCCESSFUL_EXECUTE, finish)
        cmd.cli_ctx.register_event(EVENT_CLI_POST_EXECUTE, cleanup)
        logger.warning("Execution control outcome: %s (exit %s).", report["outcome"], report["exitCode"])
    return report
