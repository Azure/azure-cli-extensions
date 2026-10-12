# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=import-error,no-name-in-module
"""Stateful run waiting, cancellation and verified trigger-history resubmission."""

from collections import OrderedDict
import re
import time
from urllib.parse import parse_qs, urlsplit

from azure.cli.core.azclierror import ClientRequestError, InvalidArgumentValueError
from azure.cli.core.util import user_confirmation
from knack.log import get_logger

from ._execution_transport import DeadlineExpired, ExecutionError, ExecutionTransport
from ._runtime_client import (
    _MANAGEMENT_PREFIX, trigger_histories_path, trigger_history_path, trigger_history_resubmit_path,
    workflow_path, workflow_run_cancel_path, workflow_run_path)
from ._workflow import validate_workflow_name
from ._workflow_discovery import workflow_metadata

logger = get_logger(__name__)
_TERMINAL = ("Succeeded", "Failed", "Cancelled", "TimedOut", "Aborted", "Faulted", "Skipped", "Ignored")
_ACTIVE = ("Running", "Waiting", "Paused", "Suspended")
_KNOWN = {value.casefold(): value for value in _TERMINAL + _ACTIVE}
_PREFLIGHT_TIMEOUT = 60
_HISTORY_PAGES = 10


def _segment(value, flag, upstream=False):
    valid = (isinstance(value, str) and 0 < len(value) <= 256 and value not in (".", "..")
             and value == value.strip() and not re.search(r"[/\\%?#=\x00-\x1f\x7f]", value))
    if not valid:
        if upstream:
            raise ExecutionError("invalidResponse", "Execution endpoint returned an invalid identifier.")
        raise InvalidArgumentValueError("{} must be a non-empty single identifier, not a path or URL.".format(flag))
    return value


def validate_execution_options(workflow, run_id, timeout=None, interval=None, trigger_history_id=None):
    if not workflow:
        raise InvalidArgumentValueError("--workflow is required.")
    validate_workflow_name(workflow)
    _segment(run_id, "--run-id")
    if trigger_history_id is not None:
        _segment(trigger_history_id, "--trigger-history-id")
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


def _run_reference(reference, workflow, run_id, site_resource_id=None):
    reference = _object(reference)
    name = _field(reference, "name")
    identifier = _field(reference, "id")
    if name is not None and _segment(name, "run reference", upstream=True) != run_id:
        return False
    if identifier is None:
        return name == run_id
    if not isinstance(identifier, str):
        raise ExecutionError("invalidResponse", "Trigger history returned an invalid run reference.")
    # Match an exact runtime resource reference; never navigate to its URL.
    expected = {"/workflows/{}/runs/{}".format(workflow, run_id),
                "/" + workflow_run_path(workflow, run_id)}
    if identifier in expected:
        return True
    if site_resource_id is None:
        return False
    prefix = site_resource_id.rstrip("/") + "/" + _MANAGEMENT_PREFIX
    return any(identifier.endswith(path) and identifier[:-len(path)].casefold() == prefix.casefold()
               for path in expected)


def _matching_history(payload, workflow, run_id, expected=None, site_resource_id=None):
    name = _segment(_field(payload, "name"), "history", upstream=True)
    if expected is not None and name != expected:
        raise ExecutionError("invalidResponse", "Execution endpoint returned a different trigger history.")
    props = _properties(payload)
    if _field(props, "fired") is not True:
        return None
    reference = _field(props, "run")
    if reference is not None and _run_reference(reference, workflow, run_id, site_resource_id):
        return name
    return None


def _history(transport, workflow, trigger, run_id, deadline, history_id, site_resource_id=None):
    if history_id:
        payload = _read(transport, trigger_history_path(workflow, trigger, history_id), deadline)
        if _matching_history(payload, workflow, run_id, history_id, site_resource_id) is None:
            raise ExecutionError("historyMismatch", "Selected trigger history is not associated with the selected run.")
        return history_id
    params = {"$top": 100}
    seen = set()
    for _ in range(_HISTORY_PAGES):
        payload = _read(transport, trigger_histories_path(workflow, trigger), deadline, params)
        items = _field(payload, "value")
        if not isinstance(items, list) or len(items) > 100:
            raise ExecutionError("invalidResponse", "Trigger history returned an invalid or oversized page.")
        matches = [_matching_history(item, workflow, run_id, site_resource_id=site_resource_id) for item in items]
        matches = [name for name in matches if name is not None]
        if len(matches) > 1:
            raise ExecutionError("invalidResponse", "More than one trigger history identifies the selected run.")
        if matches:
            return matches[0]
        link = _field(payload, "nextLink")
        if not link:
            break
        if not isinstance(link, str):
            raise ExecutionError("invalidResponse", "Trigger history returned an invalid continuation.")
        try:
            tokens = parse_qs(urlsplit(link).query).get("$skiptoken")
        except ValueError:
            raise ExecutionError("invalidResponse", "Trigger history returned a malformed continuation URL.") from None
        if (not tokens or len(tokens) != 1 or tokens[0] in seen or len(tokens[0]) > 4096
                or any(ord(character) < 32 for character in tokens[0])):
            raise ExecutionError("invalidResponse", "Trigger history returned an unsupported or repeated continuation.")
        seen.add(tokens[0])
        params = {"$top": 100, "$skiptoken": tokens[0]}
    raise ExecutionError("historyNotFound", "No associated retained trigger history was found in the bounded lookup. "
                         "Use --trigger-history-id to verify a known retained history, or check retention.")


def resubmit_run(client, workflow, run_id, yes=False, trigger_history_id=None):
    validate_execution_options(workflow, run_id, trigger_history_id=trigger_history_id)
    result = _report(workflow, run_id, "resubmit")
    result.update(sourceRunId=run_id, newRunId=None, newRunStatus=None, triggerName=None, triggerHistoryId=None)
    transport = ExecutionTransport(client)
    site_resource_id = None if client.is_local else client.site_resource_id
    deadline = time.monotonic() + _PREFLIGHT_TIMEOUT
    submitted = False
    try:
        _stateful(transport, workflow, deadline)
        result["workflowKind"] = "Stateful"
        status, props = _run(transport, workflow, run_id, deadline)
        _observe(result, status, props)
        trigger = _segment(_field(_field(props, "trigger"), "name"), "trigger", upstream=True)
        history_id = _history(transport, workflow, trigger, run_id, deadline, trigger_history_id, site_resource_id)
        result.update(triggerName=trigger, triggerHistoryId=history_id)
        user_confirmation(
            "Resubmit run '{}' in workflow '{}' at '{}' as a NEW execution using retained trigger history '{}'? "
            "This can duplicate external side effects. It is not resume, recovery or exactly-once delivery, "
            "and does not modify the original run.".format(
                run_id, workflow, client.site_resource_id, history_id), yes)
        deadline = time.monotonic() + _PREFLIGHT_TIMEOUT
        _stateful(transport, workflow, deadline)
        current_status, current = _run(transport, workflow, run_id, deadline)
        _observe(result, current_status, current)
        if _field(_field(current, "trigger"), "name") != trigger:
            raise ExecutionError("changed", "The run trigger changed during confirmation. No resubmit was attempted.")
        _history(transport, workflow, trigger, run_id, deadline, history_id, site_resource_id)
        result["action"] = "resubmitAttempted"
        submitted = True
        receipt = transport.request("POST", trigger_history_resubmit_path(workflow, trigger, history_id), deadline)
        if receipt["statusCode"] != 202 or receipt["payload"] is not None:
            raise ExecutionError("invalidResponse", "Resubmission returned an unexpected acknowledgement.")
        result["action"] = "resubmitRequested"
        result["requestAcknowledged"] = True
        result["requestCorrelationId"] = _correlation(_field(dict(receipt["headers"]), "x-ms-correlation-id"))
        new_id = next((value for key, value in receipt["headers"].items()
                       if key.casefold() == "x-ms-workflow-run-id"), None)
        if new_id is not None:
            _segment(new_id, "new run", upstream=True)
            if new_id == run_id:
                raise ExecutionError("invalidResponse", "Resubmission did not identify a distinct new run.")
        result.update(newRunId=new_id, outcome="accepted" if new_id else "acceptedNewRunIdUnknown")
        result["message"] = ("A new execution was requested, not observed completed. "
                             "No request was retried; the original run was not changed.")
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
    return [OrderedDict((("Workflow", result["workflow"]), ("Run", result["runId"]),
                         ("Operation", result["operation"]), ("Status", result["status"]),
                         ("Outcome", result["outcome"]), ("NewRun", result.get("newRunId")),
                         ("Error", (result.get("error") or {}).get("kind")),
                         ("ExitCode", result["exitCode"])))]


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
