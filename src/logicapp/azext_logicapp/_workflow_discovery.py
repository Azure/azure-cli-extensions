# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=import-error,no-name-in-module
"""Read-only workflow inventory and lossless single-workflow file export."""

import json
import os
import tempfile
from urllib.parse import parse_qs, urlsplit

from azure.cli.core.azclierror import (
    ClientRequestError, FileOperationError, InvalidArgumentValueError, ValidationError)

from ._constants import WORKFLOW_KINDS
from ._paging import slice_items
from ._runtime_client import vfs_workflow_file_path, workflow_path, workflows_path
from ._workflow import abs_path, validate_workflow_name

MAX_SERVICE_PAGES = 100
MAX_INVENTORY_ITEMS = 10000


def _field(payload, name):
    matches = [value for key, value in payload.items() if key.casefold() == name.casefold()]
    if len(matches) > 1:
        raise ClientRequestError("The service returned ambiguous workflow fields.")
    return matches[0] if matches else None


def _object(value, description):
    if not isinstance(value, dict):
        raise ClientRequestError("The service returned an invalid {} object.".format(description))
    return value


def workflow_metadata(payload, expected_name=None):
    payload = _object(payload, "workflow")
    name = _field(payload, "name")
    if not isinstance(name, str) or not name:
        raise ClientRequestError("The service returned a workflow without a name.")
    # ARM envelopes qualify the workflow name with the site name.
    name = name.rsplit("/", 1)[-1]
    if not name:
        raise ClientRequestError("The service returned an invalid workflow name.")
    try:
        validate_workflow_name(name)
    except InvalidArgumentValueError as ex:
        raise ClientRequestError("The service returned an invalid workflow name.") from ex
    if expected_name and name != expected_name:
        raise ClientRequestError("The service returned a different workflow than requested.")
    kind = _field(payload, "kind")
    if kind not in WORKFLOW_KINDS:
        raise ClientRequestError("The service returned an unsupported workflow kind.")
    properties = _field(payload, "properties")
    properties = payload if properties is None else _object(properties, "workflow properties")
    disabled = _field(properties, "isDisabled")
    state = _field(properties, "flowState")
    if disabled is not None:
        if not isinstance(disabled, bool):
            raise ClientRequestError("The service returned an invalid workflow isDisabled value.")
        runtime_state = "Disabled" if disabled else "Enabled"
        if state is not None and state != runtime_state:
            raise ClientRequestError("The service returned conflicting workflow states.")
        state = runtime_state
    if state is not None and not isinstance(state, str):
        raise ClientRequestError("The service returned an invalid workflow state.")
    health = _field(properties, "health")
    if health is not None:
        health = _field(_object(health, "workflow health"), "state")
        if health is not None and not isinstance(health, str):
            raise ClientRequestError("The service returned an invalid workflow health state.")
    return {"name": name, "kind": kind, "state": state, "health": health}


def list_workflows(client, max_items=None, next_token=None):
    # Validate CLI paging input before making a request. CLI tokens are offsets,
    # not service tokens: collect every service page before applying the offset.
    slice_items([], next_token=next_token, max_items=max_items)
    items = []
    seen = set()
    params = None
    pages = 0
    while True:
        if pages >= MAX_SERVICE_PAGES:
            raise ClientRequestError(
                "Workflow inventory exceeded the service page limit. No partial inventory was returned.")
        payload = client.get(workflows_path(), params=params)
        pages += 1
        continuation = None
        if isinstance(payload, list):
            page = payload
        else:
            payload = _object(payload, "workflow collection")
            page = _field(payload, "value")
            link = _field(payload, "nextLink")
            continuation = _field(payload, "nextContinuationToken")
            if continuation is not None and not isinstance(continuation, str):
                raise ClientRequestError("The service returned an invalid workflow continuation.")
            if link is not None and link != "":
                if not isinstance(link, str):
                    raise ClientRequestError("The service returned an invalid workflow nextLink.")
                try:
                    query = parse_qs(urlsplit(link).query, keep_blank_values=True)
                except ValueError:
                    raise ClientRequestError("The service returned a malformed workflow nextLink.") from None
                tokens = [query[key] for key in ("$skiptoken", "skipToken") if key in query]
                if not tokens or any(len(values) != 1 for values in tokens) or not tokens[0][0]:
                    raise ClientRequestError("The service returned an unsupported workflow nextLink.")
                link_token = tokens[0][0]
                if (any(values[0] != link_token for values in tokens)
                        or continuation not in (None, "", link_token)):
                    raise ClientRequestError("The service returned conflicting workflow continuations.")
                continuation = link_token
        if not isinstance(page, list):
            raise ClientRequestError("The service returned a workflow collection without a value array.")
        if len(page) > MAX_INVENTORY_ITEMS - len(items):
            raise ClientRequestError(
                "Workflow inventory exceeded the accumulated item limit. No partial inventory was returned.")
        items.extend(workflow_metadata(item) for item in page)
        if continuation is None or continuation == "":
            break
        if not isinstance(continuation, str) or continuation in seen:
            raise ClientRequestError("The service returned an invalid or repeated workflow continuation.")
        seen.add(continuation)
        # Never follow an upstream URL with a bearer token or local host key.
        params = {"$skiptoken": continuation}
    items.sort(key=lambda item: item["name"])
    names = [item["name"] for item in items]
    if len(set(names)) != len(names):
        raise ClientRequestError("The service returned duplicate workflows in its inventory.")
    page, token = slice_items(items, next_token=next_token, max_items=max_items)
    return {"value": page, "nextContinuationToken": token}


def show_workflow(client, workflow):
    if not workflow:
        raise InvalidArgumentValueError("--workflow is required.")
    validate_workflow_name(workflow)
    metadata = workflow_metadata(client.get(workflow_path(workflow)), expected_name=workflow)
    snapshot = read_workflow_file(client.vfs_client(), workflow)
    document = snapshot["document"]
    if document["kind"] != metadata["kind"]:
        raise ClientRequestError("Workflow metadata and workflow.json kinds differ. Retry after deployment completes.")
    metadata["workflow"] = document
    metadata["etag"] = snapshot["etag"]
    return metadata


def response_etag(response):
    headers = response.get("headers", {})
    return next((value for key, value in headers.items() if key.lower() == "etag"), None)


def read_workflow_file(vfs, workflow):
    from ._json import strict_json_loads

    response = vfs.get_raw(vfs_workflow_file_path(workflow))
    content = response.get("content")
    try:
        document = strict_json_loads(content)
    except (TypeError, ValueError, RecursionError) as ex:
        raise ClientRequestError("The service returned invalid JSON for workflow.json.") from ex
    document = _object(document, "workflow.json")
    kind = document.get("kind")
    if kind not in WORKFLOW_KINDS:
        raise ClientRequestError("workflow.json has a missing or unsupported kind; no default was applied.")
    definition = _object(document.get("definition"), "workflow definition")
    if not isinstance(definition.get("triggers"), dict) or not definition["triggers"]:
        raise ClientRequestError("The workflow definition must contain a non-empty triggers object.")
    if not isinstance(definition.get("actions"), dict):
        raise ClientRequestError("The workflow definition must contain an actions object.")
    try:
        json.dumps(document, allow_nan=False)
    except (TypeError, ValueError) as ex:
        raise ClientRequestError("The service returned a workflow file that is not valid JSON.") from ex
    return {"document": document, "content": content, "etag": response_etag(response)}


def export_destination(output_path, force=False):
    if not isinstance(output_path, str) or not output_path.strip():
        raise InvalidArgumentValueError("--output-path must name a JSON file.")
    path = abs_path(output_path)
    parent = os.path.dirname(path)
    real_parent = os.path.realpath(parent)
    if not path.lower().endswith(".json") or real_parent == os.path.dirname(real_parent):
        raise InvalidArgumentValueError("--output-path must name a .json file outside the filesystem root.")
    if os.path.islink(path) or (os.path.exists(path) and not os.path.isfile(path)):
        raise ValidationError("--output-path must be a regular file, not a directory or symbolic link.")
    if os.path.lexists(path) and not force:
        raise ValidationError("File exists and requires --force: {}".format(path))
    return path


def export_workflow(client, workflow, output_path, force=False):
    path = export_destination(output_path, force)
    shown = show_workflow(client, workflow)
    content = (json.dumps(shown["workflow"], indent=2, ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")
    temporary_path = None
    existed = os.path.lexists(path)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=os.path.dirname(path), prefix=".workflow-export-",
                                         suffix=".tmp", delete=False) as handle:
            temporary_path = handle.name
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        export_destination(path, force)
        if force:
            os.replace(temporary_path, path)
        else:
            # A hard link publishes the complete file atomically without replacing
            # a destination created concurrently (on Windows as well as POSIX).
            os.link(temporary_path, path)
    except FileExistsError as ex:
        raise ValidationError("File exists and requires --force: {}".format(path)) from ex
    except OSError as ex:
        raise FileOperationError("Could not export workflow to: {}".format(path)) from ex
    finally:
        if temporary_path and os.path.exists(temporary_path):
            try:
                os.unlink(temporary_path)
            except OSError as ex:
                raise FileOperationError(
                    "Could not remove export temporary file: {}. The destination may already be published.".format(
                        temporary_path)) from ex
    return {"workflow": workflow, "workflowKind": shown["kind"], "path": path,
            "bytesWritten": len(content), "action": "updated" if existed else "created",
            "etag": shown["etag"]}


def workflow_list_table_format(result):
    return [{"Name": item["name"], "Kind": item["kind"], "State": item["state"],
             "Health": item["health"]} for item in result["value"]]


def workflow_show_table_format(result):
    return [{"Name": result["name"], "Kind": result["kind"], "State": result["state"],
             "Health": result["health"]}]
