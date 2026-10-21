# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Offline HTTP contracts. Synthetic responses are not service recordings."""

import argparse
import base64
from collections import deque
from copy import deepcopy
from importlib import import_module
from inspect import unwrap
from io import BytesIO
import json
import shlex
from types import SimpleNamespace
from unittest.mock import Mock
import zipfile

import pytest
from azure.cli.core.aaz._client import AAZMgmtClient
from azure.cli.core.aaz._command_ctx import AAZCommandCtx
from azure.cli.core.azclierror import FileOperationError, InvalidArgumentValueError, ValidationError
from azure.cli.core.cloud import AZURE_PUBLIC_CLOUD
from azure.cli.core.mock import DummyCli
from azure.cli.core.sdk.policies import SafeNetworkTraceLoggingPolicy
from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.transport import HttpResponse, RequestsTransport
from knack.parser import CLICommandParser
from requests.structures import CaseInsensitiveDict

from azext_edge_action import EdgeActionCommandsLoader
from azext_edge_action.custom import EdgeActionSwapDefaultMgmtClient, ExecutionFilterUpdate, GetVersionCode
from .spec_validation import RecordingValidator, spec

API_VERSION = "2026-10-01"
SUBSCRIPTION = "00000000-0000-0000-0000-000000000000"
RESOURCE_ID = f"/subscriptions/{SUBSCRIPTION}/resourceGroups/rg/providers/Microsoft.Cdn/edgeActions/action"
RESOURCE_URL = "https://management.azure.com" + RESOURCE_ID
HANDLER = base64.b64encode(b"function handler(event) { return event; }").decode("ascii")
GROUPS = ("", "version", "execution_filter")
FILTER_UPDATE_PROPERTIES = {
    "version_id": ("versionId", RESOURCE_ID + "/versions/v2"),
    "execution_filter_identifier_header_name": ("executionFilterIdentifierHeaderName", "x-cli-updated"),
    "execution_filter_identifier_header_value": ("executionFilterIdentifierHeaderValue", "updated"),
}


def command(group, operation):
    suffix = f".{group}" if group else ""
    module = import_module(f"azext_edge_action.aaz.latest.edge_action{suffix}._{operation}")
    return getattr(module, "".join(part.title() for part in operation.split("_")))


def resource(group):
    suffix, resource_type, properties = {
        "": ("", "edgeActions", {"attachments": []}),
        "version": ("/versions/v1", "edgeActions/versions", {
            "deploymentType": "file", "isDefaultVersion": "False", "validationStatus": "Succeeded",
        }),
        "execution_filter": ("/executionFilters/filter", "edgeActions/executionFilters", {
            "versionId": RESOURCE_ID + "/versions/v1",
            "executionFilterIdentifierHeaderName": "x-cli-test",
            "executionFilterIdentifierHeaderValue": "initial",
        }),
    }[group]
    result = {
        "id": RESOURCE_ID + suffix,
        "name": suffix.rsplit("/", 1)[-1] if suffix else "action",
        "type": "Microsoft.Cdn/" + resource_type,
        "location": "global",
        "tags": {"purpose": "initial"},
        "properties": {"provisioningState": "Succeeded", **properties},
    }
    if not group:
        result["sku"] = {"name": "Standard", "tier": "Standard"}
    return result


def arguments(group):
    args = {"resource_group": "rg", "edge_action_name": "action"}
    if group == "version":
        args["version"] = "v1"
    elif group == "execution_filter":
        args["execution_filter"] = "filter"
    return args


def creation_arguments(group):
    args = {**arguments(group), "location": "global", "tags": {"purpose": "initial"}}
    if not group:
        args["sku"] = {"name": "Standard", "tier": "Standard"}
    elif group == "version":
        args.update(deployment_type="file", is_default_version="False")
    else:
        args.update(
            version_id=RESOURCE_ID + "/versions/v1",
            execution_filter_identifier_header_name="x-cli-test",
            execution_filter_identifier_header_value="initial",
        )
    return args


class SyntheticResponse(HttpResponse):
    def __init__(self, request, status, body, headers):
        super().__init__(request, None)
        self.status_code = status
        self.headers = CaseInsensitiveDict({"Content-Type": "application/json", **headers})
        self.reason = "Synthetic response"
        self.content_type = "application/json"
        self._body = json.dumps(body).encode("utf-8") if body is not None else b""

    def body(self):
        return self._body

    def text(self, encoding=None):
        return self._body.decode(encoding or "utf-8")


@pytest.fixture
def api(monkeypatch, tmp_path):
    monkeypatch.setenv("AZURE_CONFIG_DIR", str(tmp_path))
    cloud = deepcopy(AZURE_PUBLIC_CLOUD)
    cloud.profile = "latest"
    monkeypatch.setattr("azure.cli.core.cloud.get_active_cloud", lambda cli_ctx: cloud)
    cli = DummyCli()
    responses = deque()
    requests = []
    validator = RecordingValidator(spec())

    def send(request, **kwargs):
        requests.append(request)
        assert responses, f"Unexpected HTTP request: {request.method} {request.url}"
        status, body, headers = responses.popleft()
        validator.validate(request.method, request.url, request.body, dict(request.headers), status, body, headers)
        return SyntheticResponse(request, status, body, headers)

    monkeypatch.setattr(RequestsTransport, "send", lambda self, request, **kwargs: send(request, **kwargs))
    monkeypatch.setattr(RequestsTransport, "sleep", lambda self, duration: None)
    credential = Mock(spec=["get_token"])
    credential.get_token.return_value = AccessToken("offline-token", 4102444800)
    clients = {}

    def get_http_client(_ctx, client_type):
        if client_type not in clients:
            client_class = {
                "MgmtClient": AAZMgmtClient,
                "EdgeActionSwapDefaultMgmtClient": EdgeActionSwapDefaultMgmtClient,
            }[client_type]
            clients[client_type] = client_class(
                SimpleNamespace(cli_ctx=cli), credential, logging_policy=SafeNetworkTraceLoggingPolicy())
        return clients[client_type]

    monkeypatch.setattr(AAZCommandCtx, "get_http_client", get_http_client)

    def respond(body=None, status=200, headers=None):
        responses.append((status, deepcopy(body), headers or {}))

    def load(group, operation):
        names = ["edge-action"]
        if group:
            names.append(group.replace("_", "-"))
        names.append(operation.replace("_", "-"))
        loader = EdgeActionCommandsLoader(cli_ctx=cli)
        return loader.load_command_table(names)[" ".join(names)]

    def parse(group, operation, argv):
        handler = load(group, operation)
        handler.load_arguments()
        parser = argparse.ArgumentParser(allow_abbrev=False)
        for arg in handler.arguments.values():
            CLICommandParser._add_argument(parser, arg)
        parsed = vars(parser.parse_args(argv))
        ctx = AAZCommandCtx(cli, handler._build_arguments_schema(),
                            {"subscription": SUBSCRIPTION, **parsed})
        ctx.format_args()
        return parsed

    def invoke(group, operation, **kwargs):
        handler = load(group, operation)
        result = handler(command_args={"subscription": SUBSCRIPTION, **kwargs})
        if hasattr(result, "result"):
            result = result.result()
        elif operation == "list":
            result = list(result)
        return result

    try:
        yield SimpleNamespace(respond=respond, invoke=invoke, parse=parse, load=load, requests=requests)
        assert not responses, "Not all expected HTTP responses were consumed"
    finally:
        for client in clients.values():
            client.close()


def assert_resource(actual, expected):
    flattened = {key: value for key, value in expected.items() if key != "properties"}
    flattened.update(expected["properties"])
    assert actual == flattened


@pytest.mark.parametrize("group", GROUPS)
def test_show_stable_api_and_flattened_output(api, group):
    expected = resource(group)
    api.respond(expected)
    assert_resource(api.invoke(group, "show", **arguments(group)), expected)
    assert [(req.method, req.url) for req in api.requests] == [
        ("GET", f"https://management.azure.com{expected['id']}?api-version={API_VERSION}")]


@pytest.mark.parametrize("group", GROUPS)
def test_create_serializes_writable_properties(api, group):
    expected = resource(group)
    api.respond(expected)
    assert_resource(api.invoke(group, "create", **creation_arguments(group)), expected)
    request, = api.requests
    assert request.method == "PUT"
    assert request.url == f"https://management.azure.com{expected['id']}?api-version={API_VERSION}"
    assert request.headers["Content-Type"] == "application/json"
    body = json.loads(request.body)
    assert body["location"] == "global"
    assert body["tags"] == expected["tags"]
    if not group:
        assert body == {"location": "global", "tags": expected["tags"], "sku": expected["sku"]}
    else:
        properties = {key: value for key, value in expected["properties"].items()
                      if key not in ("provisioningState", "validationStatus")}
        assert body == {"location": "global", "tags": expected["tags"], "properties": properties}


@pytest.mark.parametrize("group", GROUPS)
@pytest.mark.parametrize("tags", [{"purpose": "updated"}, {}], ids=["replace", "clear"])
def test_generic_update_preserves_resource_properties(api, group, tags):
    before = resource(group)
    after = deepcopy(before)
    after["tags"] = tags
    api.respond(before)
    api.respond(after)
    assert_resource(api.invoke(group, "update", **arguments(group), tags=tags), after)
    assert [req.method for req in api.requests] == ["GET", "PUT"]
    assert all(req.url == f"https://management.azure.com{before['id']}?api-version={API_VERSION}"
               for req in api.requests)
    body = json.loads(api.requests[-1].body)
    assert body["tags"] == tags
    assert body["location"] == before["location"]
    assert "id" not in body and "type" not in body and "name" not in body
    if not group:
        assert body["sku"] == before["sku"]
    else:
        expected = {key: value for key, value in before["properties"].items()
                    if key not in ("provisioningState", "validationStatus")}
        assert body["properties"] == expected


def test_execution_filter_update_covers_all_supported_fields():
    operation, _ = spec().operation(
        "PATCH", f"{RESOURCE_URL}/executionFilters/filter?api-version={API_VERSION}")
    body = next(spec().resolve(item) for item in operation["parameters"]
                if spec().resolve(item)["in"] == "body")
    schema = spec().resolve(body["schema"])
    assert set(schema["properties"]) == {"tags", "properties"}
    properties = spec().resolve(schema["properties"]["properties"])
    assert set(properties["properties"]) == {name for name, _ in FILTER_UPDATE_PROPERTIES.values()}


@pytest.mark.parametrize("fields", [
    ("tags",), ("clear_tags",), ("version_id",),
    ("execution_filter_identifier_header_name",),
    ("execution_filter_identifier_header_value",),
    ("tags", *FILTER_UPDATE_PROPERTIES),
], ids=["tags", "clear-tags", "version", "header-name", "header-value", "all"])
def test_execution_filter_update_preserves_omitted_fields(api, fields):
    before = resource("execution_filter")
    expected = deepcopy(before)
    argv = ["-g", "rg", "--edge-action-name", "action", "-n", "filter"]
    for field in fields:
        if field in ("tags", "clear_tags"):
            tags = {} if field == "clear_tags" else {"purpose": "updated"}
            expected["tags"] = tags
            argv.extend(["--tags", json.dumps(tags)])
        else:
            name, value = FILTER_UPDATE_PROPERTIES[field]
            expected["properties"][name] = value
            argv.extend(["--" + field.replace("_", "-"), value])
    api.respond(before)
    api.respond(expected)
    parsed = api.parse("execution_filter", "update", argv)
    assert_resource(api.invoke("execution_filter", "update", **parsed), expected)
    assert_filter_update_requests(api, expected)


def assert_filter_update_requests(api, expected):
    assert [request.method for request in api.requests] == ["GET", "PUT"]
    assert all(request.url == f"https://management.azure.com{expected['id']}?api-version={API_VERSION}"
               for request in api.requests)
    assert json.loads(api.requests[-1].body) == {
        "location": expected["location"],
        "tags": expected["tags"],
        "properties": {name: value for name, value in expected["properties"].items()
                       if name != "provisioningState"},
    }


@pytest.mark.parametrize("status", [200, 201])
@pytest.mark.parametrize("use_status", [True, False])
def test_execution_filter_update_polls_and_returns_updated_resource(api, status, use_status):
    expected = resource("execution_filter")
    expected["properties"]["versionId"] = RESOURCE_ID + "/versions/v2"
    pending = deepcopy(expected)
    pending["properties"]["provisioningState"] = "Upgrading"
    resource_url = f"https://management.azure.com{expected['id']}?api-version={API_VERSION}"
    status_url = "https://management.azure.com/operations/filter-status"
    headers = {"Retry-After": "0"}
    urls = [resource_url, resource_url]
    if use_status:
        headers["Azure-AsyncOperation"] = status_url
    api.respond(resource("execution_filter"))
    api.respond(pending, status=status, headers=headers)
    if use_status:
        api.respond({"status": "InProgress"}, headers={"Retry-After": "0"})
        api.respond({"status": "Succeeded"})
        urls.extend([status_url, status_url])
    api.respond(expected)
    urls.append(resource_url)
    assert_resource(api.invoke("execution_filter", "update", **arguments("execution_filter"),
                               version_id=expected["properties"]["versionId"]), expected)
    assert [request.method for request in api.requests] == ["GET", "PUT"] + ["GET"] * (len(urls) - 2)
    assert [request.url for request in api.requests] == urls


def test_execution_filter_update_no_wait_does_not_poll(api):
    before = resource("execution_filter")
    pending = deepcopy(before)
    pending["properties"]["provisioningState"] = "Upgrading"
    pending["tags"] = {"purpose": "updated"}
    api.respond(before)
    api.respond(pending, status=201, headers={
        "Azure-AsyncOperation": "https://management.azure.com/operations/filter-status"})
    assert api.invoke("execution_filter", "update", **arguments("execution_filter"),
                      tags={"purpose": "updated"}, no_wait=True) is None
    assert_filter_update_requests(api, pending)


@pytest.mark.parametrize("status", ["Failed", "Canceled"])
def test_execution_filter_update_polling_failure_is_not_success(api, status):
    pending = resource("execution_filter")
    pending["properties"]["provisioningState"] = "Upgrading"
    api.respond(resource("execution_filter"))
    api.respond(pending, status=201, headers={
        "Azure-AsyncOperation": "https://management.azure.com/operations/filter-status", "Retry-After": "0"})
    api.respond({"status": status, "error": {"code": "OperationFailed", "message": "Filter update failed"}})
    with pytest.raises(HttpResponseError, match="Filter update failed"):
        api.invoke("execution_filter", "update", **arguments("execution_filter"),
                   version_id=RESOURCE_ID + "/versions/v2")
    assert [request.method for request in api.requests] == ["GET", "PUT", "GET"]


@pytest.mark.parametrize("error", ["VersionOutsideParent", "HeaderPairAlreadyExists"])
def test_execution_filter_update_surfaces_service_rejection(api, error):
    api.respond(resource("execution_filter"))
    api.respond({"error": {"code": error, "message": error}}, status=400)
    with pytest.raises(HttpResponseError, match=error):
        api.invoke("execution_filter", "update", **arguments("execution_filter"),
                   **{arg: value for arg, (_, value) in FILTER_UPDATE_PROPERTIES.items()})
    assert [request.method for request in api.requests] == ["GET", "PUT"]


def test_execution_filter_update_registration_preserves_generic_options(api):
    handler = api.load("execution_filter", "update")
    assert isinstance(handler, ExecutionFilterUpdate)
    handler.load_arguments()
    options = {option for arg in handler.arguments.values() for option in arg.options_list}
    assert {"--set", "--add", "--remove", "--force-string", "--no-wait",
            "--tags", "--version-id", "--execution-filter-identifier-header-name",
            "--execution-filter-identifier-header-value"} <= options
    assert api.requests == []


@pytest.mark.parametrize("field", list(FILTER_UPDATE_PROPERTIES))
def test_execution_filter_generic_set_can_update_properties(api, field):
    name, value = FILTER_UPDATE_PROPERTIES[field]
    before = resource("execution_filter")
    expected = deepcopy(before)
    expected["properties"][name] = value
    api.respond(before)
    api.respond(expected)
    parsed = api.parse("execution_filter", "update", [
        "-g", "rg", "--edge-action-name", "action", "-n", "filter",
        "--set", f"{field}={value}",
    ])
    assert_resource(api.invoke("execution_filter", "update", **parsed), expected)
    assert_filter_update_requests(api, expected)


def test_execution_filter_generic_options_apply_after_named_arguments(api):
    before = resource("execution_filter")
    expected = deepcopy(before)
    expected["properties"]["executionFilterIdentifierHeaderValue"] = "true"
    expected["tags"] = {"number": "123"}
    api.respond(before)
    api.respond(expected)
    parsed = api.parse("execution_filter", "update", [
        "-g", "rg", "--edge-action-name", "action", "-n", "filter",
        "--execution-filter-identifier-header-value", "named-value",
        "--set", "execution_filter_identifier_header_value=true", "tags.number=123",
        "--remove", "tags.purpose", "--force-string",
    ])
    assert_resource(api.invoke("execution_filter", "update", **parsed), expected)
    assert_filter_update_requests(api, expected)


def test_execution_filter_generic_remove_clears_a_tag(api):
    before = resource("execution_filter")
    expected = deepcopy(before)
    expected["tags"] = {}
    api.respond(before)
    api.respond(expected)
    parsed = api.parse("execution_filter", "update", [
        "-g", "rg", "--edge-action-name", "action", "-n", "filter", "--remove", "tags.purpose",
    ])
    assert_resource(api.invoke("execution_filter", "update", **parsed), expected)
    assert_filter_update_requests(api, expected)


def test_execution_filter_update_does_not_modify_generated_argument_schema(api):
    handler = api.load("execution_filter", "update")
    handler.load_arguments()
    generated = command("execution_filter", "update")(cli_ctx=handler.cli_ctx)
    generated.load_arguments()
    assert "version_id" not in generated.arguments
    assert "execution_filter_identifier_header_name" not in generated.arguments
    assert "execution_filter_identifier_header_value" not in generated.arguments
    assert api.requests == []


def test_execution_filter_generic_add_retains_list_validation(api):
    api.respond(resource("execution_filter"))
    parsed = api.parse("execution_filter", "update", [
        "-g", "rg", "--edge-action-name", "action", "-n", "filter",
        "--add", "tags", "purpose=updated",
    ])
    with pytest.raises(InvalidArgumentValueError, match="invalid syntax"):
        api.invoke("execution_filter", "update", **parsed)
    assert [request.method for request in api.requests] == ["GET"]


def test_execution_filter_scenario_deletes_default_version_last(api):
    from .test_edge_action import EdgeActionScenarioTest

    versions = {}
    deletions = []
    filter_exists = False

    def run(command_line, checks=None):
        nonlocal filter_exists
        argv = shlex.split(command_line.format())
        group = argv[1].replace("-", "_") if argv[1] in ("version", "execution-filter") else ""
        operation_index = 2 if group else 1
        operation = argv[operation_index].replace("-", "_")
        api.parse(group, operation, argv[operation_index + 1:])
        name = argv[argv.index("-n") + 1] if "-n" in argv else ""
        if group == "version" and operation == "create":
            versions[name] = argv[argv.index("--is-default-version") + 1] == "True"
        elif group == "version" and operation == "delete":
            assert not filter_exists, "Delete the execution filter before its versions"
            assert not versions[name] or len(versions) == 1, "Delete non-default versions first"
            del versions[name]
            deletions.append(name)
        elif group == "execution_filter" and operation in ("create", "delete"):
            filter_exists = operation == "create"
        return SimpleNamespace(get_output_in_json=lambda: {"id": RESOURCE_ID + "/versions/" + name})

    scenario = SimpleNamespace(cmd=run, create_random_name=lambda prefix, length: prefix + "123456")
    unwrap(EdgeActionScenarioTest.test_edge_action_execution_filter_crud)(scenario, "rg")
    assert deletions == ["v2", "v1"]
    assert not versions and not filter_exists
    assert api.requests == []


@pytest.mark.parametrize("group,operation", [
    (group, operation)
    for group in GROUPS
    for operation in ("create", "delete", "list", "show", "update")
] + [("version", operation) for operation in ("deploy_version_code", "get_version_code", "swap_default")])
def test_help_examples_accept_registered_arguments(api, group, operation):
    examples = [line.strip() for line in command(group, operation).__doc__.splitlines()
                if line.strip().startswith("az ")]
    assert examples
    prefix_length = 3 if not group else 4
    for example in examples:
        api.parse(group, operation, shlex.split(example)[prefix_length:])
    assert api.requests == []


@pytest.mark.parametrize("group", GROUPS)
def test_list_follows_next_link(api, group):
    first = resource(group)
    second = deepcopy(first)
    second["name"] = "second"
    second["id"] = first["id"].rsplit("/", 1)[0] + "/second"
    url = f"https://management.azure.com{first['id'].rsplit('/', 1)[0]}?api-version={API_VERSION}"
    next_link = url + "&$skiptoken=opaque"
    api.respond({"value": [first], "nextLink": next_link})
    api.respond({"value": [second]})
    result = api.invoke(group, "list", **arguments(group))
    assert len(result) == 2
    assert_resource(result[0], first)
    assert_resource(result[1], second)
    assert [(req.method, req.url) for req in api.requests] == [("GET", url), ("GET", next_link)]


@pytest.mark.parametrize("group", GROUPS)
def test_list_empty(api, group):
    api.respond({"value": []})
    assert api.invoke(group, "list", **arguments(group)) == []
    assert len(api.requests) == 1


@pytest.mark.parametrize("group", GROUPS)
@pytest.mark.parametrize("status", [200, 204])
def test_delete_no_content(api, group, status):
    api.respond(status=status)
    assert api.invoke(group, "delete", **arguments(group)) is None
    request, = api.requests
    assert request.method == "DELETE"
    assert request.url == f"https://management.azure.com{resource(group)['id']}?api-version={API_VERSION}"


@pytest.mark.parametrize("group", GROUPS)
@pytest.mark.parametrize("status", [200, 201])
def test_create_polls_async_operation_then_fetches_resource(api, group, status):
    expected = resource(group)
    pending = deepcopy(expected)
    pending["properties"]["provisioningState"] = "Creating"
    status_url = "https://management.azure.com/operations/create"
    api.respond(pending, status=status, headers={"Azure-AsyncOperation": status_url, "Retry-After": "0"})
    api.respond({"status": "InProgress"}, headers={"Retry-After": "0"})
    api.respond({"status": "Succeeded"})
    api.respond(expected)
    assert_resource(api.invoke(group, "create", **creation_arguments(group)), expected)
    resource_url = f"https://management.azure.com{expected['id']}?api-version={API_VERSION}"
    assert [(req.method, req.url) for req in api.requests] == [
        ("PUT", resource_url), ("GET", status_url), ("GET", status_url), ("GET", resource_url)]


@pytest.mark.parametrize("group", GROUPS)
def test_delete_polls_and_returns_no_resource(api, group):
    status_url = "https://management.azure.com/operations/delete-status"
    result_url = "https://management.azure.com/operations/delete-result"
    api.respond(status=202, headers={
        "Azure-AsyncOperation": status_url, "Location": result_url, "Retry-After": "0"})
    api.respond({"status": "Succeeded"})
    api.respond(status=204)
    assert api.invoke(group, "delete", **arguments(group)) is None
    assert [(req.method, req.url) for req in api.requests] == [
        ("DELETE", f"https://management.azure.com{resource(group)['id']}?api-version={API_VERSION}"),
        ("GET", status_url), ("GET", result_url)]


@pytest.mark.parametrize("operation", ["deploy_version_code", "get_version_code", "swap_default"])
def test_action_immediate_success_returns_declared_shape(api, operation):
    expected = {
        "deploy_version_code": resource("version"),
        "get_version_code": {"name": "v1", "content": HANDLER},
        "swap_default": None,
    }[operation]
    api.respond(expected, status=204 if expected is None else 200)
    args = arguments("version")
    if operation == "deploy_version_code":
        args.update(name="v1", content=HANDLER)
    result = api.invoke("version", operation, **args)
    if operation == "deploy_version_code":
        assert_resource(result, expected)
    else:
        assert result == expected
    assert len(api.requests) == 1


@pytest.mark.parametrize("operation", ["deploy_version_code", "get_version_code"])
def test_action_lro_uses_final_location(api, operation):
    status_url = "https://management.azure.com/operations/status"
    location = "https://management.azure.com/operations/result"
    expected = {
        "deploy_version_code": resource("version"),
        "get_version_code": {"name": "v1", "content": HANDLER},
    }[operation]
    api.respond(status=202, headers={
        "Azure-AsyncOperation": status_url, "Location": location, "Retry-After": "0"})
    api.respond({"status": "InProgress"}, headers={"Retry-After": "0"})
    api.respond({"status": "Succeeded"})
    api.respond(expected)
    args = arguments("version")
    if operation == "deploy_version_code":
        args.update(name="v1", content=HANDLER)
    result = api.invoke("version", operation, **args)
    if operation == "deploy_version_code":
        assert_resource(result, expected)
        assert json.loads(api.requests[0].body) == {"name": "v1", "content": HANDLER}
    else:
        assert result == expected
        assert not api.requests[0].body
    action = {"deploy_version_code": "deployVersionCode", "get_version_code": "getVersionCode"}[operation]
    assert [(req.method, req.url) for req in api.requests] == [
        ("POST", f"{RESOURCE_URL}/versions/v1/{action}?api-version={API_VERSION}"),
        ("GET", status_url), ("GET", status_url), ("GET", location)]


@pytest.mark.parametrize("option", ["--output-directory", "-d"])
@pytest.mark.parametrize("asynchronous", [False, True])
def test_get_version_code_saves_zip_through_registered_alias(api, tmp_path, option, asynchronous):
    archive = BytesIO()
    with zipfile.ZipFile(archive, "w") as package:
        package.writestr("handler.js", base64.b64decode(HANDLER))
    content = archive.getvalue()
    output_dir = tmp_path / "directory with spaces" / "nested"
    location = "https://management.azure.com/operations/code-result"
    if asynchronous:
        api.respond(status=202, headers={"Location": location, "Retry-After": "0"})
    api.respond({"name": "download", "content": base64.b64encode(content).decode("ascii")})
    parsed = api.parse("version", "get_version_code", [
        "-g", "rg", "--edge-action-name", "action", "--version", "v1", option, str(output_dir),
    ])
    result = api.invoke("version", "get_version_code", **parsed)
    output_file = output_dir / "download.zip"
    assert result == {"message": f"Version code saved to: {output_file}", "file": str(output_file)}
    assert output_file.read_bytes() == content
    expected_requests = [
        ("POST", f"{RESOURCE_URL}/versions/v1/getVersionCode?api-version={API_VERSION}"),
    ]
    if asynchronous:
        expected_requests.append(("GET", location))
    assert [(request.method, request.url) for request in api.requests] == expected_requests
    assert not api.requests[0].body


def test_get_version_code_overwrites_existing_download(api, tmp_path):
    output_file = tmp_path / "v1.zip"
    output_file.write_bytes(b"previous download")
    api.respond({"name": "v1", "content": HANDLER})
    api.invoke("version", "get_version_code", **arguments("version"), output_directory=str(tmp_path))
    assert output_file.read_bytes() == base64.b64decode(HANDLER)


def test_get_version_code_argument_schema_is_cached_and_isolated(api):
    handler = api.load("version", "get_version_code")
    assert isinstance(handler, GetVersionCode)
    schema = handler._build_arguments_schema()
    assert handler._build_arguments_schema() is schema
    generated = command("version", "get_version_code")(cli_ctx=handler.cli_ctx)
    generated.load_arguments()
    assert "output_directory" not in generated.arguments
    handler.load_arguments()
    assert handler.arguments["output_directory"].options_list == ["--output-directory", "-d"]
    assert api.requests == []


def test_get_version_code_no_wait_does_not_save_or_poll(api, tmp_path):
    output_dir = tmp_path / "download"
    api.respond(status=202, headers={"Location": "https://management.azure.com/operations/code-result"})
    assert api.invoke("version", "get_version_code", **arguments("version"),
                      output_directory=str(output_dir), no_wait=True) is None
    assert len(api.requests) == 1
    assert not output_dir.exists()


@pytest.mark.parametrize("content,message", [
    ("", "No content returned"),
    ("not base64!", "Failed to decode base64 content"),
    ("YQ", "Failed to decode base64 content"),
])
def test_get_version_code_rejects_invalid_content_before_writing(api, tmp_path, content, message):
    output_dir = tmp_path / "download"
    api.respond({"name": "v1", "content": content})
    with pytest.raises(ValidationError, match=message):
        api.invoke("version", "get_version_code", **arguments("version"), output_directory=str(output_dir))
    assert not output_dir.exists()


@pytest.mark.parametrize("name", ["../escape", "..\\escape", "C:escape", "bad\0name"])
def test_get_version_code_rejects_paths_in_response_name(api, tmp_path, name):
    output_dir = tmp_path / "download"
    api.respond({"name": name, "content": HANDLER})
    with pytest.raises(ValidationError, match="Invalid version code file name"):
        api.invoke("version", "get_version_code", **arguments("version"), output_directory=str(output_dir))
    assert not output_dir.exists()


@pytest.mark.parametrize("failure", ["directory", "write"])
def test_get_version_code_surfaces_file_errors(api, tmp_path, monkeypatch, failure):
    output_dir = tmp_path / "download"
    if failure == "directory":
        output_dir.write_bytes(b"not a directory")
    else:
        monkeypatch.setattr("azext_edge_action.custom.open",
                            Mock(side_effect=PermissionError("write denied")), raising=False)
    api.respond({"name": "v1", "content": HANDLER})
    with pytest.raises(FileOperationError, match="Failed to save file"):
        api.invoke("version", "get_version_code", **arguments("version"), output_directory=str(output_dir))
    assert not (output_dir / "v1.zip").exists()


def test_get_version_code_polling_failure_does_not_save(api, tmp_path):
    output_dir = tmp_path / "download"
    api.respond(status=202, headers={
        "Azure-AsyncOperation": "https://management.azure.com/operations/status", "Retry-After": "0"})
    api.respond({"status": "Failed", "error": {"code": "OperationFailed", "message": "Download failed"}})
    with pytest.raises(HttpResponseError, match="Download failed"):
        api.invoke("version", "get_version_code", **arguments("version"), output_directory=str(output_dir))
    assert not output_dir.exists()
    assert len(api.requests) == 2


@pytest.mark.parametrize("operation", ["deploy_version_code", "get_version_code", "swap_default"])
def test_action_no_wait_does_not_poll(api, operation):
    api.respond(status=202, headers={"Location": "https://management.azure.com/operations/result"})
    args = arguments("version")
    if operation == "deploy_version_code":
        args.update(name="v1", content=HANDLER)
    assert api.invoke("version", operation, **args, no_wait=True) is None
    assert len(api.requests) == 1


@pytest.mark.parametrize("use_status,use_location", [(True, True), (True, False), (False, True)])
def test_swap_default_discards_successful_polling_body(api, use_status, use_location):
    status_url = "https://management.azure.com/operations/status"
    location = "https://management.azure.com/operations/result"
    headers = {"Retry-After": "0"}
    urls = [f"{RESOURCE_URL}/versions/v1/swapDefault?api-version={API_VERSION}"]
    if use_status:
        headers["Azure-AsyncOperation"] = status_url
    if use_location:
        headers["Location"] = location
    api.respond(status=202, headers=headers)
    if use_status:
        api.respond({"status": "InProgress"}, headers={"Retry-After": "0"})
        api.respond({"status": "Succeeded"})
        urls.extend([status_url, status_url])
    if use_location:
        api.respond({"status": "Succeeded"})
        urls.append(location)
    assert api.invoke("version", "swap_default", **arguments("version")) is None
    assert [request.url for request in api.requests] == urls


def test_swap_default_accepts_empty_successful_location(api):
    status_url = "https://management.azure.com/operations/status"
    location = "https://management.azure.com/operations/result"
    api.respond(status=202, headers={
        "Azure-AsyncOperation": status_url, "Location": location, "Retry-After": "0"})
    api.respond({"status": "Succeeded"})
    api.respond(status=204)
    assert api.invoke("version", "swap_default", **arguments("version")) is None
    assert [request.url for request in api.requests] == [
        f"{RESOURCE_URL}/versions/v1/swapDefault?api-version={API_VERSION}", status_url, location]


@pytest.mark.parametrize("operation", ["deploy_version_code", "swap_default"])
@pytest.mark.parametrize("status", ["Failed", "Canceled"])
def test_failed_lro_surfaces_service_error(api, operation, status):
    api.respond(status=202, headers={
        "Azure-AsyncOperation": "https://management.azure.com/operations/status", "Retry-After": "0"})
    api.respond({"status": status, "error": {"code": "OperationFailed", "message": "Invalid code"}})
    args = arguments("version")
    if operation == "deploy_version_code":
        args.update(name="v1", content=HANDLER)
    with pytest.raises(HttpResponseError, match="Invalid code"):
        api.invoke("version", operation, **args)
    assert len(api.requests) == 2


@pytest.mark.parametrize("group", GROUPS)
def test_not_found_is_not_success(api, group):
    api.respond({"error": {"code": "ResourceNotFound", "message": "Edge Action does not exist"}}, status=404)
    with pytest.raises(HttpResponseError, match="Edge Action does not exist"):
        api.invoke(group, "show", **arguments(group))
    assert len(api.requests) == 1


def test_name_exceeding_maximum_length_rejected_before_http(api):
    with pytest.raises(InvalidArgumentValueError):
        api.invoke("", "create", **{**creation_arguments(""), "edge_action_name": "a" * 51})
    assert api.requests == []


def test_name_at_maximum_length_is_accepted(api):
    expected = resource("")
    expected["name"] = "a" * 50
    expected["id"] = RESOURCE_ID.rsplit("/", 1)[0] + "/" + expected["name"]
    api.respond(expected)
    assert_resource(api.invoke("", "create", **{
        **creation_arguments(""), "edge_action_name": expected["name"],
    }), expected)
    assert api.requests[0].url == f"https://management.azure.com{expected['id']}?api-version={API_VERSION}"
