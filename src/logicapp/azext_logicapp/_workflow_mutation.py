# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=import-error,no-name-in-module
"""Revision-guarded mutations with explicit non-transactional VFS boundaries."""

import json

from azure.cli.core.azclierror import (
    ClientRequestError, FileOperationError, HTTPError, InvalidArgumentValueError,
    ResourceNotFoundError, UnauthorizedError, ValidationError)
from azure.cli.core.util import user_confirmation
from requests.exceptions import ConnectionError as RequestsConnectionError, Timeout as RequestsTimeout

from ._json import json_equal, strict_json_loads
from ._runtime_client import validate_file_etag, vfs_workflow_file_path, workflow_path
from ._workflow_validation import validate_runtime_workflow
from ._workflow import abs_path, validate_workflow_document, validate_workflow_name
from ._workflow_discovery import read_workflow_file, response_etag, workflow_metadata

_REQUEST_ERRORS = (HTTPError, ClientRequestError, ResourceNotFoundError, UnauthorizedError,
                   RequestsConnectionError, RequestsTimeout)


def _require_acknowledgement(allow_non_atomic):
    if not allow_non_atomic:
        raise InvalidArgumentValueError(
            "Workflow file mutations require --allow-non-atomic. The runtime's VFS API is not "
            "transactional: ETag checks do not prevent every race or partial write.",
            recommendation="Export the current workflow first and coordinate with other writers. "
                           "--allow-non-atomic acknowledges this limitation; it does not bypass ETag checks.")


def _etag(value, argument=False):
    return validate_file_etag(value, argument=argument)


def _expected_etag(if_match):
    return _etag(if_match, argument=True) if if_match is not None else None


def _unchanged_revision(actual, expected):
    if expected is not None and actual != expected:
        raise ClientRequestError(
            "The workflow revision changed. No mutation was attempted.",
            recommendation="Read/export the current workflow and review the changes before retrying.")


def _same_snapshot(before, current):
    _unchanged_revision(current["etag"], before["etag"])
    if current["content"] != before["content"]:
        raise ClientRequestError("The workflow file changed without a new ETag. No mutation was attempted.")


def _status(error):
    response = getattr(error, "response", None)
    if response is None:
        response = getattr(getattr(error, "__cause__", None), "response", None)
    return getattr(response, "status_code", None)


def load_update_file(file, workflow):
    if not file:
        raise InvalidArgumentValueError("--file is required.")
    path = abs_path(file)
    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            document = strict_json_loads(handle.read())
    except (ValueError, UnicodeError, RecursionError) as ex:
        raise InvalidArgumentValueError("--file must contain valid JSON.") from ex
    except OSError as ex:
        raise FileOperationError("Could not read workflow input file: {}".format(path)) from ex
    findings = []
    validate_workflow_document(document, workflow, path, findings)
    errors = [finding for finding in findings if finding["severity"] == "error"]
    if errors:
        raise ValidationError(json.dumps({"valid": False, "findings": errors}))
    # A complete authored workflow file is required; never infer a kind or merge
    # in old configuration behind the user's back.
    if not isinstance(document["definition"].get("actions"), dict):
        raise InvalidArgumentValueError("--file must contain a complete workflow.json with an actions object.")
    if "runtimeConfiguration" in document and not isinstance(document["runtimeConfiguration"], dict):
        raise InvalidArgumentValueError("--file runtimeConfiguration must be an object.")
    try:
        json.dumps(document, allow_nan=False)
    except (TypeError, ValueError) as ex:
        raise InvalidArgumentValueError("--file contains a value that is not valid JSON.") from ex
    return document


def _current_workflow(client, workflow, expected):
    metadata = workflow_metadata(client.get(workflow_path(workflow)), expected_name=workflow)
    vfs = client.vfs_client()
    snapshot = read_workflow_file(vfs, workflow)
    snapshot["etag"] = _etag(snapshot["etag"])
    _unchanged_revision(snapshot["etag"], expected)
    if snapshot["document"]["kind"] != metadata["kind"]:
        raise ClientRequestError("Workflow metadata and file kinds differ. No mutation was attempted.")
    return vfs, snapshot


def _mutation_error(operation, error):
    if _status(error) == 412:
        return ClientRequestError(
            "The workflow changed before {}. The runtime rejected the ETag; no retry or bypass was attempted.".format(
                operation),
            recommendation="Read/export the latest workflow before retrying.")
    return ClientRequestError(
        "{} failed. The request outcome may be uncertain; no unconditional retry or rollback was attempted.".format(
            operation.capitalize()),
        recommendation="Inspect/export the workflow before retrying. Non-atomic VFS writes can leave changed or partial content.")


def _restore_owned_revision(vfs, path, before, written_etag):
    try:
        current = vfs.get_raw(path)
        if _etag(response_etag(current)) != written_etag:
            return "A newer revision exists; it was not overwritten and no rollback was attempted."
        restored = vfs.put_raw(path, before["content"], if_match=written_etag)
        if restored.get("statusCode") != 204:
            return "Conditional restoration did not return an update receipt; state requires manual verification."
        restored_etag = _etag(response_etag(restored))
        checked = vfs.get_raw(path)
        if checked.get("content") == before["content"] and response_etag(checked) == restored_etag:
            return "The previous workflow file was conditionally restored and its bytes verified."
        return "Restoration could not be verified; inspect the current workflow before retrying."
    except ResourceNotFoundError:
        return "The file disappeared; no rollback recreated it."
    except _REQUEST_ERRORS:
        return "Conditional restoration failed; the workflow may contain changed or partial content."


def set_workflow(client, workflow, file, if_match=None, yes=False, allow_non_atomic=False):
    _require_acknowledgement(allow_non_atomic)
    if not workflow:
        raise InvalidArgumentValueError("--workflow is required.")
    validate_workflow_name(workflow)
    expected = _expected_etag(if_match)
    document = load_update_file(file, workflow)
    vfs, before = _current_workflow(client, workflow, expected)
    if document["kind"] != before["document"]["kind"]:
        raise InvalidArgumentValueError("workflow set does not convert Stateful/Stateless kind. No mutation was attempted.")
    try:
        validate_runtime_workflow(
            client, workflow,
            {"properties": {"definition": document["definition"], "kind": document["kind"]}})
    except _REQUEST_ERRORS as ex:
        raise ValidationError(
            "The target runtime rejected or could not validate the incoming definition. "
            "The existing workflow was not written.",
            recommendation="Validate the input using workflow validate --with-runtime and check target access.") from ex
    if json_equal(document, before["document"]):
        # Recheck after validation so a concurrent edit cannot be called a no-op.
        current = read_workflow_file(vfs, workflow)
        _same_snapshot(before, current)
        return {"workflow": workflow, "workflowKind": document["kind"], "action": "unchanged",
                "etag": before["etag"], "verification": "fileReadback"}
    user_confirmation(
        "Replace workflow '{}' at '{}'? Only workflow.json is written. VFS writes are not atomic; "
        "coordinate with other writers and retain an export for recovery.".format(
            workflow, client.site_resource_id), yes)
    path = vfs_workflow_file_path(workflow)
    # Recheck after a potentially long confirmation prompt; the conditional
    # write still carries the original revision, never '*'.
    current = read_workflow_file(vfs, workflow)
    _same_snapshot(before, current)
    content = (json.dumps(document, indent=2, ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")
    try:
        response = vfs.put_raw(path, content, if_match=before["etag"])
    except _REQUEST_ERRORS as ex:
        raise _mutation_error("update", ex) from ex
    if response.get("statusCode") != 204:
        raise ClientRequestError(
            "The runtime did not return an update receipt. It may have recreated a concurrently deleted file. "
            "No automatic deletion or rollback was attempted; inspect/export the workflow.")
    try:
        written_etag = _etag(response_etag(response))
    except ClientRequestError as ex:
        raise ClientRequestError(
            "The update was acknowledged without a usable write ETag. Ownership and rollback cannot be "
            "verified; inspect/export the workflow before retrying.") from ex
    try:
        after = vfs.get_raw(path)
    except _REQUEST_ERRORS as ex:
        raise ClientRequestError(
            "The update was acknowledged, but readback failed. No rollback was attempted without a current "
            "revision; inspect/export the workflow before retrying.") from ex
    if response_etag(after) != written_etag:
        raise ClientRequestError(
            "The workflow changed after the update. Verification failed; a newer revision was not overwritten.")
    if after.get("content") != content:
        outcome = _restore_owned_revision(vfs, path, before, written_etag)
        raise ClientRequestError("Update readback did not match the input. {}".format(outcome))
    return {"workflow": workflow, "workflowKind": document["kind"], "action": "updated",
            "etag": written_etag, "verification": "fileReadback"}


def delete_workflow(client, workflow, if_match=None, yes=False, allow_non_atomic=False):
    _require_acknowledgement(allow_non_atomic)
    if not workflow:
        raise InvalidArgumentValueError("--workflow is required.")
    validate_workflow_name(workflow)
    expected = _expected_etag(if_match)
    vfs, before = _current_workflow(client, workflow, expected)
    user_confirmation(
        "Delete workflow '{}' at '{}'? Only its workflow.json is removed; sibling files, app settings, "
        "connections and other workflows remain. This does not cancel runs or purge run history. "
        "VFS mutations are not transactional.".format(workflow, client.site_resource_id), yes)
    current = read_workflow_file(vfs, workflow)
    _same_snapshot(before, current)
    path = vfs_workflow_file_path(workflow)
    try:
        response = vfs.delete(path, if_match=before["etag"])
    except _REQUEST_ERRORS as ex:
        raise _mutation_error("delete", ex) from ex
    if response.get("statusCode") not in (200, 204):
        raise ClientRequestError("The runtime did not return a delete receipt. Inspect the workflow before retrying.")
    try:
        vfs.get_raw(path)
    except ResourceNotFoundError:
        return {"workflow": workflow, "workflowKind": before["document"]["kind"], "action": "deleted",
                "etag": None, "verification": "fileNotFound"}
    except _REQUEST_ERRORS as ex:
        raise ClientRequestError(
            "Deletion was acknowledged, but file absence could not be verified. Inspect the workflow before retrying.") from ex
    raise ClientRequestError(
        "Deletion was acknowledged, but workflow.json still exists or was recreated. No second deletion was attempted.")
