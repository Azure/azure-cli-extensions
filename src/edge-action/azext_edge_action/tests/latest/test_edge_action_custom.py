# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import base64
from contextlib import ExitStack, contextmanager
from copy import deepcopy
from io import BytesIO
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import zipfile

from azure.cli.core.aaz._command_ctx import AAZCommandCtx
from azure.cli.core.aaz._client import AAZMgmtClient
from azure.cli.core.azclierror import FileOperationError, InvalidArgumentValueError, ValidationError
from azure.cli.core.cloud import AZURE_PUBLIC_CLOUD
from azure.cli.core.commands import ExtensionCommandSource
from azure.cli.core.mock import DummyCli
from azure.cli.core.sdk.policies import SafeNetworkTraceLoggingPolicy
from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.transport import HttpResponse, RequestsTransport
from knack.parser import CLICommandParser
from knack.util import CLIError
from requests.structures import CaseInsensitiveDict

from azext_edge_action import EdgeActionCommandsLoader
from azext_edge_action.aaz.latest.edge_action.execution_filter import Update as GeneratedFilterUpdate
from azext_edge_action.aaz.latest.edge_action.version import GetVersionCode as GeneratedGetVersionCode
from azext_edge_action.custom import (
    EdgeActionSwapDefaultMgmtClient, ExecutionFilterUpdate, GetVersionCode, deploy_edge_action_version,
)

HANDLER = b"function handler(event) { return event; }"
SUBSCRIPTION = "00000000-0000-0000-0000-000000000000"
RESOURCE_ID = f"/subscriptions/{SUBSCRIPTION}/resourceGroups/rg/providers/Microsoft.Cdn/edgeActions/action"
STATUS_URL = "https://management.azure.com/operations/status"
RESULT_URL = "https://management.azure.com/operations/result"
FILTER_FIELDS = (
    "version_id", "execution_filter_identifier_header_name", "execution_filter_identifier_header_value",
)


class MockResponse(HttpResponse):
    def __init__(self, request, status, body, headers):
        super().__init__(request, None)
        self.status_code = status
        self.headers = CaseInsensitiveDict({"Content-Type": "application/json", **headers})
        self.content_type = "application/json"
        self.reason = "Unit test response"
        self._body = json.dumps(body).encode("utf-8") if body is not None else b""

    def body(self):
        return self._body

    def text(self, encoding=None):
        return self._body.decode(encoding or "utf-8")


class EdgeActionCustomTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        environment = patch.dict(os.environ, {"AZURE_CONFIG_DIR": str(self.directory)})
        environment.start()
        self.addCleanup(environment.stop)
        self.cli = DummyCli()

    def load_command(self, name):
        loader = EdgeActionCommandsLoader(cli_ctx=self.cli)
        command = loader.load_command_table(name.split())[name]
        command.load_arguments()
        return command

    @contextmanager
    def http_responses(self, responses):
        """Mock transport only; execute the registered command and real AAZ polling."""
        requests, clients = [], {}
        credential = Mock(spec=["get_token"])
        credential.get_token.return_value = AccessToken("unit-test-token", 4102444800)
        cloud = deepcopy(AZURE_PUBLIC_CLOUD)
        cloud.profile = "latest"

        def send(request, **_kwargs):
            self.assertLess(len(requests), len(responses), "Unexpected HTTP request")
            status, body, headers = responses[len(requests)]
            requests.append(request)
            return MockResponse(request, status, body, headers)

        def get_client(_ctx, client_type):
            if client_type not in clients:
                cls = {"MgmtClient": AAZMgmtClient,
                       "EdgeActionSwapDefaultMgmtClient": EdgeActionSwapDefaultMgmtClient}[client_type]
                clients[client_type] = cls(
                    SimpleNamespace(cli_ctx=self.cli), credential, logging_policy=SafeNetworkTraceLoggingPolicy())
            return clients[client_type]

        with ExitStack() as stack:
            stack.enter_context(patch("azure.cli.core.cloud.get_active_cloud", return_value=cloud))
            stack.enter_context(patch.object(RequestsTransport, "send", side_effect=send))
            stack.enter_context(patch.object(RequestsTransport, "sleep", return_value=None))
            stack.enter_context(patch.object(AAZCommandCtx, "get_http_client", get_client))
            try:
                yield requests
                self.assertEqual(len(requests), len(responses), "Not all expected requests were made")
            finally:
                for client in clients.values():
                    client.close()

    def invoke(self, name, **arguments):
        command = self.load_command(name)
        result = command(command_args={
            "subscription": SUBSCRIPTION, "resource_group": "rg", "edge_action_name": "action", **arguments,
        })
        return result.result() if hasattr(result, "result") else result

    @staticmethod
    def filter_resource():
        return {
            "id": RESOURCE_ID + "/executionFilters/filter", "name": "filter", "location": "global",
            "tags": {"purpose": "initial"}, "properties": {
                "provisioningState": "Succeeded", "versionId": RESOURCE_ID + "/versions/v1",
                "executionFilterIdentifierHeaderName": "x-test",
                "executionFilterIdentifierHeaderValue": "initial",
            },
        }

    def download(self, result, output_directory):
        command = GetVersionCode(cli_ctx=self.cli)
        command.ctx = AAZCommandCtx(self.cli, command.get_arguments_schema(), {
            "output_directory": output_directory,
        })
        with patch.object(GeneratedGetVersionCode, "_output", return_value=result):
            return command._output()

    def test_edge_action_download_aliases_and_no_wait_remain_registered(self):
        command = self.load_command("edge-action version get-version-code")
        self.assertIsInstance(command, GetVersionCode)
        self.assertTrue(command.supports_no_wait)
        self.assertEqual(command.arguments["output_directory"].options_list, ["--output-directory", "-d"])
        parser = argparse.ArgumentParser(allow_abbrev=False)
        for argument in command.arguments.values():
            CLICommandParser._add_argument(parser, argument)
        for option in ("--output-directory", "-d"):
            with self.subTest(option=option):
                parsed = parser.parse_args([
                    "-g", "rg", "--edge-action-name", "action", "--version", "v1",
                    option, str(self.directory / "with spaces"), "--no-wait",
                ])
                context = AAZCommandCtx(self.cli, command.get_arguments_schema(), {
                    "subscription": "00000000-0000-0000-0000-000000000000", **vars(parsed),
                })
                context.format_args()
                self.assertEqual(
                    context.args.output_directory.to_serialized_data(), str(self.directory / "with spaces"))
                self.assertTrue(context.args.no_wait.to_serialized_data())

    def test_edge_action_download_preserves_result_without_directory(self):
        result = {"name": "v1", "content": base64.b64encode(HANDLER).decode("ascii")}
        for directory in (None, ""):
            with self.subTest(directory=directory):
                self.assertIs(self.download(result, directory), result)

    def test_edge_action_download_saves_zip_and_overwrites(self):
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("index.js", HANDLER)
        content = buffer.getvalue()
        directory = self.directory / "with spaces" / "nested"
        output = directory / "download.zip"
        result = {"name": "download", "content": base64.b64encode(content).decode("ascii")}
        expected = {"file": str(output), "message": f"Version code saved to: {output}"}
        self.assertEqual(self.download(result, str(directory)), expected)
        self.assertEqual(output.read_bytes(), content)
        output.write_bytes(b"old download")
        self.assertEqual(self.download(result, str(directory)), expected)
        self.assertEqual(output.read_bytes(), content)

    def test_edge_action_download_rejects_invalid_content(self):
        output = self.directory / "download"
        for content, message in (
                (None, "No content returned"), ("", "No content returned"), ("not base64!", "Failed to decode"),
                ("YQ", "Failed to decode")):
            with self.subTest(content=content), self.assertRaisesRegex(ValidationError, message):
                self.download({"name": "v1", "content": content}, str(output))
            self.assertFalse(output.exists())

    def test_edge_action_download_rejects_unsafe_names(self):
        output = self.directory / "download"
        for name in ("", ".", "..", "../escape", "..\\escape", "C:escape", "bad\0name"):
            with self.subTest(name=name), self.assertRaisesRegex(ValidationError, "Invalid version code file name"):
                self.download({"name": name, "content": base64.b64encode(HANDLER).decode("ascii")}, str(output))
            self.assertFalse(output.exists())

    def test_edge_action_download_reports_filesystem_errors(self):
        result = {"name": "v1", "content": base64.b64encode(HANDLER).decode("ascii")}
        output = self.directory / "not a directory"
        output.write_bytes(b"file")
        with self.assertRaisesRegex(FileOperationError, "Failed to save file"):
            self.download(result, str(output))
        with patch("azext_edge_action.custom.open", side_effect=PermissionError("denied"), create=True):
            with self.assertRaisesRegex(FileOperationError, "Failed to save file"):
                self.download(result, str(self.directory / "download"))

    def test_edge_action_download_registered_polling_saves_final_content(self):
        output = self.directory / "download"
        responses = [
            (202, None, {"Azure-AsyncOperation": STATUS_URL, "Location": RESULT_URL}),
            (200, {"status": "Succeeded"}, {}),
            (200, {"name": "v1", "content": base64.b64encode(HANDLER).decode("ascii")}, {}),
        ]
        with self.http_responses(responses) as requests:
            result = self.invoke("edge-action version get-version-code", version="v1", output_directory=str(output))
            self.assertEqual([request.method for request in requests], ["POST", "GET", "GET"])
            self.assertEqual(requests[-1].url, RESULT_URL)
        self.assertEqual(Path(result["file"]).read_bytes(), HANDLER)

    def test_edge_action_download_no_wait_and_polling_errors_do_not_write(self):
        for status in (None, "Failed", "Canceled"):
            with self.subTest(status=status):
                output = self.directory / str(status)
                responses = [(202, None, {"Azure-AsyncOperation": STATUS_URL})]
                if status:
                    responses.append((200, {
                        "status": status, "error": {"code": "DownloadFailed", "message": "Download rejected"},
                    }, {}))
                with self.http_responses(responses):
                    args = {"version": "v1", "output_directory": str(output), "no_wait": status is None}
                    if status:
                        with self.assertRaisesRegex(HttpResponseError, "Download rejected"):
                            self.invoke("edge-action version get-version-code", **args)
                    else:
                        self.assertIsNone(self.invoke("edge-action version get-version-code", **args))
                self.assertFalse(output.exists())

    def test_edge_action_custom_command_name_boundaries(self):
        for field in ("edge_action_name", "version"):
            for length in (1, 50, 51):
                with self.subTest(field=field, length=length):
                    args = {"version": "v1", field: "a" * length, "no_wait": True}
                    responses = [(202, None, {"Location": RESULT_URL})] if length <= 50 else []
                    with self.http_responses(responses):
                        if length <= 50:
                            self.assertIsNone(self.invoke("edge-action version get-version-code", **args))
                        else:
                            with self.assertRaises(InvalidArgumentValueError):
                                self.invoke("edge-action version get-version-code", **args)

    def test_edge_action_list_pagination_and_local_limit_arguments(self):
        root = {
            "id": RESOURCE_ID, "name": "action", "location": "global",
            "sku": {"name": "Standard", "tier": "Standard"},
            "properties": {"provisioningState": "Succeeded", "attachments": []},
        }
        version = {
            "id": RESOURCE_ID + "/versions/v1", "name": "v1", "location": "global",
            "properties": {"provisioningState": "Succeeded", "deploymentType": "file",
                           "isDefaultVersion": "False", "validationStatus": "Succeeded"},
        }
        cases = (
            ("", root, None),
            ("", root, "rg"),
            ("version", version, "rg"),
            ("execution-filter", self.filter_resource(), "rg"),
        )
        for group, first, resource_group in cases:
            with self.subTest(group=group, resource_group=resource_group):
                name = " ".join(part for part in ("edge-action", group, "list") if part)
                args = ["-g", resource_group] if resource_group else []
                if group:
                    args.extend(["--edge-action-name", "action"])
                path = f"/subscriptions/{SUBSCRIPTION}"
                if resource_group:
                    path += f"/resourceGroups/{resource_group}"
                path += "/providers/Microsoft.Cdn/edgeActions"
                if group:
                    path += "/action/" + {"version": "versions", "execution-filter": "executionFilters"}[group]
                url = "https://management.azure.com" + path + "?api-version=2026-10-01"
                second = deepcopy(first)
                second.update(id=first["id"] + "2", name=first["name"] + "2")

                def items(*options):
                    command = self.load_command(name)
                    parser = argparse.ArgumentParser(allow_abbrev=False)
                    for argument in command.arguments.values():
                        CLICommandParser._add_argument(parser, argument)
                    parsed = vars(parser.parse_args([*args, *options]))
                    return list(command(command_args={"subscription": SUBSCRIPTION, **parsed}))

                next_link = url + "&$skiptoken=next-page"
                responses = [
                    (200, {"value": [first], "nextLink": next_link}, {}),
                    (200, {"value": [second]}, {}),
                ]
                with self.http_responses(responses) as requests:
                    result = items()
                    self.assertEqual([item["name"] for item in result], [first["name"], second["name"]])
                    self.assertEqual([item["id"] for item in result], [first["id"], second["id"]])
                    if not group:
                        for item in result:
                            self.assertEqual(item["location"], "global")
                            self.assertEqual(item["sku"], {"name": "Standard", "tier": "Standard"})
                            self.assertEqual(item["provisioningState"], "Succeeded")
                            self.assertEqual(item["attachments"], [])
                    self.assertEqual(requests[0].method, "GET")
                    self.assertEqual(requests[0].url, url)
                    self.assertEqual(len(requests), 2)
                    self.assertEqual(requests[-1].method, "GET")
                    self.assertEqual(requests[-1].url, next_link)
                with self.http_responses([(200, {"value": []}, {})]) as requests:
                    self.assertEqual(items(), [])
                    self.assertEqual(len(requests), 1)
                    self.assertEqual(requests[0].url, url)
                with self.http_responses([]), self.assertRaises(InvalidArgumentValueError):
                    items("--max-items", "0")
                for limit in (1, 2):
                    with self.subTest(limit=limit), self.http_responses([(200, {"value": [first, second]}, {})]):
                        self.assertEqual(len(items("--max-items", str(limit))), limit)
                token = base64.b64encode(json.dumps({"next_link": None, "offset": 1}).encode("utf-8")).decode("ascii")
                with self.http_responses([(200, {"value": [first, second]}, {})]):
                    page = items("--max-items", "1", "--next-token", token)
                    self.assertEqual([item["name"] for item in page], [second["name"]])

    def test_edge_action_list_subscription_override(self):
        self.assert_list_subscription_override(resource_group=None)

    def test_edge_action_list_resource_group_subscription_override(self):
        self.assert_list_subscription_override(resource_group="rg1")

    def assert_list_subscription_override(self, resource_group):
        class TestCommandsLoader(EdgeActionCommandsLoader):
            def load_command_table(self, args):
                table = super().load_command_table(args)
                for command in table.values():
                    command.command_source = ExtensionCommandSource(extension_name="edge-action")
                return table

            def load_arguments(self, command):
                self.command_table[command].load_arguments()
                super().load_arguments(command)

        subscription = "11111111-1111-1111-1111-111111111111"
        self.cli = DummyCli(commands_loader_cls=TestCommandsLoader)
        self.addCleanup(self.cli.logging.end_cmd_metadata_logging, 0)
        self.cli.data["subscription_id"] = SUBSCRIPTION
        subscriptions = [
            {"id": SUBSCRIPTION, "name": "default", "isDefault": True},
            {"id": subscription, "name": "alternate", "isDefault": False},
        ]
        args = ["edge-action", "list", "--subscription", subscription]
        path = f"/subscriptions/{subscription}"
        if resource_group:
            args.extend(["--resource-group", resource_group])
            path += f"/resourceGroups/{resource_group}"
        path += "/providers/Microsoft.Cdn/edgeActions"
        resource_id = (
            f"/subscriptions/{subscription}/resourceGroups/rg1/providers/Microsoft.Cdn/edgeActions/action"
        )
        resource = {
            "id": resource_id, "name": "action", "location": "global",
            "sku": {"name": "Standard", "tier": "Standard"},
            "properties": {"provisioningState": "Succeeded", "attachments": []},
        }

        # Exercise the CLI's subscription action and override, not direct command_args injection.
        self.cli.invocation = self.cli.invocation_cls(
            cli_ctx=self.cli, parser_cls=self.cli.parser_cls,
            commands_loader_cls=TestCommandsLoader, help_cls=self.cli.help_cls,
        )
        with patch("azure.cli.core._profile.Profile.load_cached_subscriptions",
                   return_value=subscriptions) as cached_subscriptions, \
                patch("azure.cli.core._profile.Profile.get_subscription_id", return_value=SUBSCRIPTION), \
                self.http_responses([(200, {"value": [resource]}, {})]) as requests:
            result = self.cli.invocation.execute(args)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual([item["id"] for item in result.result], [resource_id])
            self.assertEqual(result.result[0]["name"], "action")
            self.assertEqual(result.result[0]["provisioningState"], "Succeeded")
            cached_subscriptions.assert_called()
            self.assertEqual(len(requests), 1)
            self.assertEqual(requests[0].method, "GET")
            self.assertEqual(
                requests[0].url, "https://management.azure.com" + path + "?api-version=2026-10-01")
            self.assertNotIn(SUBSCRIPTION, requests[0].url)
        self.assertEqual(self.cli.data["subscription_id"], SUBSCRIPTION)

    def test_edge_action_custom_argument_caches_are_isolated_in_both_load_orders(self):
        cases = (
            ("edge-action version get-version-code", GeneratedGetVersionCode, GetVersionCode,
             {"output_directory": ["--output-directory", "-d"]}),
            ("edge-action execution-filter update", GeneratedFilterUpdate, ExecutionFilterUpdate,
             {field: ["--" + field.replace("_", "-")] for field in FILTER_FIELDS}),
        )
        for name, generated_class, custom_class, options in cases:
            for generated_first in (True, False):
                with self.subTest(command=name, generated_first=generated_first), ExitStack() as stack:
                    for cls in (generated_class, custom_class):
                        for attribute in ("_args_schema", "_arguments_schema"):
                            # Do not create ownership of an inherited cache while testing it.
                            if attribute in vars(cls):
                                stack.enter_context(patch.object(cls, attribute, None))
                    loader = EdgeActionCommandsLoader(cli_ctx=self.cli)
                    custom = loader.load_command_table(name.split())[name]
                    self.assertIsInstance(custom, custom_class)
                    generated = generated_class(cli_ctx=self.cli)
                    for command in ((generated, custom) if generated_first else (custom, generated)):
                        command.load_arguments()
                    schema = custom.get_arguments_schema()
                    self.assertIs(custom.get_arguments_schema(), schema)
                    self.assertIs(custom._build_arguments_schema(), schema)
                    self.assertIsNot(generated.get_arguments_schema(), schema)
                    for field, aliases in options.items():
                        self.assertNotIn(field, generated.arguments)
                        self.assertEqual(custom.arguments[field].options_list, aliases)

    def test_edge_action_filter_update_keeps_generic_arguments(self):
        command = self.load_command("edge-action execution-filter update")
        self.assertIsInstance(command, ExecutionFilterUpdate)
        options = {option for argument in command.arguments.values() for option in argument.options_list}
        self.assertTrue({
            "--set", "--add", "--remove", "--force-string", "--tags", "--no-wait",
            "--version-id", "--execution-filter-identifier-header-name",
            "--execution-filter-identifier-header-value",
        } <= options)

    def test_edge_action_filter_update_preserves_omitted_fields_and_applies_empty_strings(self):
        before = dict(zip(FILTER_FIELDS, ("old-version", "old-header", "old-value")))
        cases = [{}] + [{field: value} for field in FILTER_FIELDS for value in ("new-value", "", None)]
        cases.append(dict(zip(FILTER_FIELDS, ("new-version", "new-header", "new-value"))))
        for supplied in cases:
            with self.subTest(supplied=supplied):
                command = ExecutionFilterUpdate(cli_ctx=self.cli)
                command.ctx = AAZCommandCtx(self.cli, command.get_arguments_schema(), supplied)
                instance = SimpleNamespace(properties=SimpleNamespace(**before))
                command.pre_instance_update(instance)
                changed = {field: value for field, value in supplied.items() if value is not None}
                for field, value in {**before, **changed}.items():
                    actual = getattr(instance.properties, field)
                    if field in changed:
                        actual = actual.to_serialized_data()
                    self.assertEqual(actual, value)

    def test_edge_action_filter_generic_precedence_and_add_validation(self):
        before = self.filter_resource()
        name = "edge-action execution-filter update"
        for add in (False, True):
            with self.subTest(add=add):
                command = self.load_command(name)
                parser = argparse.ArgumentParser(allow_abbrev=False)
                for argument in command.arguments.values():
                    CLICommandParser._add_argument(parser, argument)
                options = ["--add", "tags", "purpose=updated"] if add else [
                    "--execution-filter-identifier-header-value", "named-value",
                    "--set", "execution_filter_identifier_header_value=true", "tags.number=123",
                    "--remove", "tags.purpose", "--force-string",
                ]
                parsed = vars(parser.parse_args([
                    "-g", "rg", "--edge-action-name", "action", "-n", "filter", *options,
                ]))
                expected = deepcopy(before)
                expected["tags"] = {"number": "123"}
                expected["properties"]["executionFilterIdentifierHeaderValue"] = "true"
                responses = [(200, before, {})] + ([] if add else [(200, expected, {})])
                with self.http_responses(responses) as requests:
                    if add:
                        with self.assertRaisesRegex(InvalidArgumentValueError, "invalid syntax"):
                            self.invoke(name, **parsed)
                    else:
                        result = self.invoke(name, **parsed)
                        self.assertEqual(result["executionFilterIdentifierHeaderValue"], "true")
                        body = json.loads(requests[-1].body)
                        self.assertEqual(body["tags"], expected["tags"])
                        for field in ("versionId", "executionFilterIdentifierHeaderName",
                                      "executionFilterIdentifierHeaderValue"):
                            self.assertEqual(body["properties"][field], expected["properties"][field])
                    self.assertEqual([request.method for request in requests], ["GET"] if add else ["GET", "PUT"])

    def test_edge_action_filter_update_no_wait_and_errors_preserve_request_fields(self):
        for error in (None, "VersionOutsideParent", "HeaderPairAlreadyExists", "Failed", "Canceled"):
            with self.subTest(error=error):
                before = self.filter_resource()
                updating = deepcopy(before)
                updating["properties"].update(versionId=RESOURCE_ID + "/versions/v2", provisioningState="Updating")
                responses = [(200, before, {})]
                if error in ("VersionOutsideParent", "HeaderPairAlreadyExists"):
                    responses.append((400, {"error": {"code": error, "message": error}}, {}))
                else:
                    responses.append((201, updating, {"Azure-AsyncOperation": STATUS_URL}))
                    if error:
                        responses.append((200, {
                            "status": error, "error": {"code": error, "message": error},
                        }, {}))
                with self.http_responses(responses) as requests:
                    args = {
                        "execution_filter": "filter", "version_id": RESOURCE_ID + "/versions/v2",
                        "no_wait": error is None,
                    }
                    if error:
                        with self.assertRaisesRegex(HttpResponseError, error):
                            self.invoke("edge-action execution-filter update", **args)
                    else:
                        self.assertIsNone(self.invoke("edge-action execution-filter update", **args))
                    self.assertEqual([request.method for request in requests[:2]], ["GET", "PUT"])
                    body = json.loads(requests[1].body)
                    self.assertEqual(body["properties"]["versionId"], args["version_id"])
                    for field in ("executionFilterIdentifierHeaderName", "executionFilterIdentifierHeaderValue"):
                        self.assertEqual(body["properties"][field], before["properties"][field])
                    self.assertEqual(body["tags"], before["tags"])

    def test_edge_action_deployment_encodes_files_and_forwards_arguments(self):
        path = self.directory / "file with spaces.js"
        path.write_bytes(HANDLER)
        for deployment_type in (None, "file"):
            with self.subTest(deployment_type=deployment_type), patch(
                    "azext_edge_action.aaz.latest.edge_action.version._deploy_version_code.DeployVersionCode") as generated:
                result = deploy_edge_action_version(
                    SimpleNamespace(cli_ctx=self.cli), "rg", "action", "v1", str(path), deployment_type)
                generated.assert_called_once_with(cli_ctx=self.cli)
                generated.return_value.assert_called_once_with(command_args={
                    "resource_group": "rg", "edge_action_name": "action", "version": "v1",
                    "content": base64.b64encode(HANDLER).decode("ascii"), "name": "v1", "no_wait": False,
                })
                self.assertIs(result, generated.return_value.return_value)

    def test_edge_action_deployment_preserves_zip_and_no_wait(self):
        path = self.directory / "package.zip"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("index.js", HANDLER)
        for deployment_type in (None, "zip"):
            with self.subTest(deployment_type=deployment_type), patch(
                    "azext_edge_action.aaz.latest.edge_action.version._deploy_version_code.DeployVersionCode") as generated:
                deploy_edge_action_version(
                    SimpleNamespace(cli_ctx=self.cli), "rg", "action", "v1", str(path), deployment_type, no_wait=True)
                args = generated.return_value.call_args.kwargs["command_args"]
                self.assertEqual(base64.b64decode(args["content"], validate=True), path.read_bytes())
                self.assertTrue(args["no_wait"])

    def test_edge_action_deployment_auto_zips_javascript(self):
        path = self.directory / "index.js"
        path.write_bytes(HANDLER)
        with patch("azext_edge_action.aaz.latest.edge_action.version._deploy_version_code.DeployVersionCode") as generated:
            deploy_edge_action_version(SimpleNamespace(cli_ctx=self.cli), "rg", "action", "v1", str(path), "zip")
        args = generated.return_value.call_args.kwargs["command_args"]
        with zipfile.ZipFile(BytesIO(base64.b64decode(args["content"], validate=True))) as archive:
            self.assertEqual(archive.namelist(), ["index.js"])
            self.assertEqual(archive.read("index.js"), HANDLER)

    def test_edge_action_deployment_rejects_invalid_files(self):
        cases = (
            ("missing.js", None, "File not found"),
            ("handler.txt", None, "Cannot determine deployment type"),
            ("handler.zip", "file", "requires a JavaScript"),
            ("handler.txt", "zip", "requires a JavaScript"),
            ("handler.js", "invalid", "Invalid deployment type"),
        )
        for filename, deployment_type, message in cases:
            with self.subTest(filename=filename, deployment_type=deployment_type), patch(
                    "azext_edge_action.aaz.latest.edge_action.version._deploy_version_code.DeployVersionCode") as generated:
                path = self.directory / filename
                if filename != "missing.js":
                    path.write_bytes(HANDLER)
                with self.assertRaisesRegex(CLIError, message):
                    deploy_edge_action_version(
                        SimpleNamespace(cli_ctx=self.cli), "rg", "action", "v1", str(path), deployment_type)
                generated.assert_not_called()

    def test_edge_action_deployment_propagates_generated_command_failure(self):
        path = self.directory / "index.js"
        path.write_bytes(HANDLER)
        with patch("azext_edge_action.aaz.latest.edge_action.version._deploy_version_code.DeployVersionCode") as generated:
            generated.return_value.side_effect = CLIError("Deployment rejected")
            with self.assertRaisesRegex(CLIError, "Deployment rejected"):
                deploy_edge_action_version(SimpleNamespace(cli_ctx=self.cli), "rg", "action", "v1", str(path))

    def test_edge_action_swap_default_preserves_polling_arguments_and_existing_callbacks(self):
        for no_wait in (True, False):
            for has_deserializer in (True, False):
                with self.subTest(no_wait=no_wait, has_deserializer=has_deserializer), patch(
                        "azure.cli.core.aaz._client.AAZMgmtClient.build_lro_polling") as build_polling:
                    client = object.__new__(EdgeActionSwapDefaultMgmtClient)
                    session, error_callback = Mock(), Mock()
                    deserialize = Mock() if has_deserializer else None
                    options = {"final-state-via": "location"}
                    paths = {"version": "v1"}
                    result = client.build_lro_polling(
                        no_wait, session, deserialize, error_callback,
                        lro_options=options, path_format_arguments=paths)
                    self.assertIs(result, build_polling.return_value)
                    actual_wait, actual_session, actual_deserialize, actual_error = build_polling.call_args.args
                    self.assertIs(actual_wait, no_wait)
                    self.assertIs(actual_session, session)
                    self.assertIs(actual_error, error_callback)
                    self.assertEqual(build_polling.call_args.kwargs, {
                        "lro_options": options, "path_format_arguments": paths,
                    })
                    if has_deserializer:
                        self.assertIs(actual_deserialize, deserialize)
                        deserialize.assert_not_called()
                    else:
                        response = Mock()
                        self.assertIsNone(actual_deserialize(response))
                        self.assertEqual(response.mock_calls, [])

    def test_edge_action_swap_default_registered_polling_paths(self):
        for use_status, use_location in ((True, True), (True, False), (False, True)):
            for final_status in ((200, 204) if use_location else (200,)):
                with self.subTest(status=use_status, location=use_location, final_status=final_status):
                    headers, responses = {}, []
                    urls = [f"https://management.azure.com{RESOURCE_ID}/versions/v1/swapDefault"
                            "?api-version=2026-10-01"]
                    if use_status:
                        headers["Azure-AsyncOperation"] = STATUS_URL
                        responses.extend([(200, {"status": "InProgress"}, {}), (200, {"status": "Succeeded"}, {})])
                        urls.extend([STATUS_URL, STATUS_URL])
                    if use_location:
                        headers["Location"] = RESULT_URL
                        responses.append((final_status, {"status": "Succeeded"} if final_status == 200 else None, {}))
                        urls.append(RESULT_URL)
                    with self.http_responses([(202, None, headers), *responses]) as requests:
                        self.assertIsNone(self.invoke("edge-action version swap-default", version="v1"))
                        self.assertEqual([request.url for request in requests], urls)

    def test_edge_action_swap_default_no_wait_and_immediate_success(self):
        for status, no_wait in ((204, False), (202, True)):
            with self.subTest(status=status, no_wait=no_wait):
                with self.http_responses([(status, None, {"Location": RESULT_URL} if no_wait else {})]):
                    self.assertIsNone(self.invoke("edge-action version swap-default", version="v1", no_wait=no_wait))

    def test_edge_action_swap_default_polling_errors_are_not_success(self):
        for status in ("Failed", "Canceled"):
            with self.subTest(status=status):
                responses = [
                    (202, None, {"Azure-AsyncOperation": STATUS_URL}),
                    (200, {"status": status, "error": {"code": "SwapFailed", "message": "Swap rejected"}}, {}),
                ]
                with self.http_responses(responses), self.assertRaisesRegex(HttpResponseError, "Swap rejected"):
                    self.invoke("edge-action version swap-default", version="v1")
