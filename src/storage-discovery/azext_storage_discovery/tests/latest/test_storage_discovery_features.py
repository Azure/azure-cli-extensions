# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
from copy import deepcopy
import json
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from azure.cli.core.aaz._command_ctx import AAZCommandCtx
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.pipeline.transport import RequestsTransportResponse
from requests import Response

from azext_storage_discovery.aaz.latest.storage_discovery.workspace import Create, List, Query, Show
from azext_storage_discovery.aaz.latest.storage_discovery.workspace.report import (
    GenerateReport,
    List as ReportList,
    Show as ReportShow,
)


class StorageDiscoveryFeaturesTest(unittest.TestCase):
    subscription = "00000000-0000-0000-0000-000000000000"

    def setUp(self):
        self.client = Mock()
        self.client.format_url.side_effect = lambda template, **kwargs: template.format(**kwargs)
        self.capabilities = {
            "azureBlobStorage": {
                "capacityDetails": {"status": "Enabled"},
                "prefixConfigurations": [{
                    "storageAccountName": "accountone",
                    "containerName": "containerone",
                    "prefix": "logs/",
                }],
            },
        }
        self.workspace = {
            "name": "testworkspace",
            "location": "francecentral",
            "properties": {
                "capabilities": deepcopy(self.capabilities),
                "sku": "Standard",
                "workspaceRoots": [f"/subscriptions/{self.subscription}"],
                "scopes": [{
                    "displayName": "testscope",
                    "resourceTypes": ["Microsoft.Storage/storageAccounts"],
                }],
            },
        }
        self.report = {
            "name": "testreport",
            "type": "Microsoft.StorageDiscovery/storageDiscoveryWorkspaces/reports",
            "properties": {"provisioningState": "Succeeded"},
        }
        self.query_payload = {"queries": [{"name": "capacity", "query": "CapacityHourly | take 1"}]}
        self.encoded_query = base64.b64encode(json.dumps(self.query_payload).encode("utf-8")).decode("ascii")
        self.results = {
            "results": [
                {
                    "columns": [{"name": "account", "type": "string"}],
                    "rows": [["accountone"]],
                },
                {"errorCode": "Failed: Bad Query"},
            ],
        }

    def command(self, command_type, **arguments):
        with patch("azure.cli.core.aaz._command_ctx.Profile"):
            ctx = AAZCommandCtx(
                cli_ctx=Mock(),
                schema=command_type.get_arguments_schema(),
                command_args={"subscription": self.subscription, **arguments},
                no_wait_arg="no_wait" if command_type.AZ_SUPPORT_NO_WAIT else None,
            )
        ctx.format_args()
        ctx.get_http_client = Mock(return_value=self.client)
        command = command_type.__new__(command_type)
        command.ctx = ctx
        command.callbacks = {}
        return command

    @staticmethod
    def session(body, status=200):
        return SimpleNamespace(
            http_response=SimpleNamespace(status_code=status),
            context={ContentDecodePolicy.CONTEXT_NAME: deepcopy(body)},
        )

    def assert_request(self, method, path, content=None):
        arguments = self.client._request.call_args.args
        self.assertEqual(arguments[0], method)
        self.assertEqual(arguments[1], path)
        self.assertEqual(arguments[2], {"api-version": "2026-10-01-preview"})
        self.assertEqual(arguments[4], content)

    @property
    def workspace_path(self):
        return (
            f"/subscriptions/{self.subscription}/resourceGroups/testrg/providers/"
            "Microsoft.StorageDiscovery/storageDiscoveryWorkspaces/testworkspace"
        )

    def test_create_serializes_capabilities_and_returns_them(self):
        command = self.command(
            Create,
            resource_group="testrg",
            storage_discovery_workspace_name="testworkspace",
            location="francecentral",
            sku="Standard",
            workspace_roots=[f"/subscriptions/{self.subscription}"],
            scopes=[{
                "display_name": "testscope",
                "resource_types": ["Microsoft.Storage/storageAccounts"],
            }],
            capabilities={
                "azure_blob_storage": {
                    "capacity_details": {"status": "Enabled"},
                    "prefix_configurations": [{
                        "storage_account_name": "accountone",
                        "container_name": "containerone",
                        "prefix": "logs/",
                    }],
                },
            },
        )
        self.client.send_request.return_value = self.session(self.workspace, status=201)
        command._execute_operations()
        expected = deepcopy(self.workspace)
        del expected["name"]
        self.assert_request("PUT", self.workspace_path, expected)
        self.assertEqual(command._output()["properties"]["capabilities"], self.capabilities)

    def test_show_returns_capabilities(self):
        command = self.command(Show, resource_group="testrg", storage_discovery_workspace_name="testworkspace")
        self.client.send_request.return_value = self.session(self.workspace)
        command._execute_operations()
        self.assert_request("GET", self.workspace_path)
        self.assertEqual(command._output()["properties"]["capabilities"], self.capabilities)

    def test_workspace_list_returns_capabilities_at_both_scopes(self):
        for resource_group in (None, "testrg"):
            with self.subTest(resource_group=resource_group):
                arguments = {"resource_group": resource_group} if resource_group else {}
                command = self.command(List, **arguments)
                self.client.send_request.return_value = self.session({"value": [self.workspace]})
                command._execute_operations()
                scope = f"/resourceGroups/{resource_group}" if resource_group else ""
                self.assert_request(
                    "GET",
                    f"/subscriptions/{self.subscription}{scope}/providers/"
                    "Microsoft.StorageDiscovery/storageDiscoveryWorkspaces",
                )
                values, _ = command._output()
                self.assertEqual(values[0]["properties"]["capabilities"], self.capabilities)

    def test_report_list_routes_both_scopes_and_exposes_next_link(self):
        for resource_group in (None, "testrg"):
            with self.subTest(resource_group=resource_group):
                arguments = {"resource_group": resource_group} if resource_group else {}
                command = self.command(
                    ReportList, storage_discovery_workspace_name="testworkspace", **arguments,
                )
                next_link = f"https://management.azure.com{self.workspace_path}/reports?skiptoken=next"
                self.client.send_request.return_value = self.session({
                    "value": [self.report], "nextLink": next_link,
                })
                command._execute_operations()
                scope = f"/resourceGroups/{resource_group}" if resource_group else ""
                self.assert_request(
                    "GET",
                    f"/subscriptions/{self.subscription}{scope}/providers/"
                    "Microsoft.StorageDiscovery/storageDiscoveryWorkspaces/testworkspace/reports",
                )
                values, actual_next_link = command._output()
                self.assertEqual(values, [self.report])
                self.assertEqual(actual_next_link, next_link)

                command.ctx.next_link = next_link
                self.client.send_request.return_value = self.session({"value": []})
                command._execute_operations()
                arguments = self.client._request.call_args.args
                self.assertEqual(arguments[0], "GET")
                self.assertEqual(arguments[1], next_link.split("?")[0])
                self.assertEqual(arguments[2], {"skiptoken": ["next"]})
                self.assertEqual(command._output()[0], [])

    def test_report_show_returns_named_report(self):
        command = self.command(
            ReportShow, resource_group="testrg",
            storage_discovery_workspace_name="testworkspace", discovery_resource_name="testreport",
        )
        self.client.send_request.return_value = self.session(self.report)
        command._execute_operations()
        self.assert_request("GET", self.workspace_path + "/reports/testreport")
        self.assertEqual(command._output(), self.report)

    def test_query_actions_send_encoded_queries_and_return_results(self):
        for command_type, suffix in (
            (Query, "/report"),
            (GenerateReport, "/reports/testreport/generateReport"),
        ):
            for status in (200, 202):
                with self.subTest(command=command_type.__name__, status=status):
                    arguments = {"discovery_resource_name": "testreport"} if command_type is GenerateReport else {}
                    command = self.command(
                        command_type, resource_group="testrg",
                        storage_discovery_workspace_name="testworkspace",
                        queries=[self.encoded_query], no_wait=False, **arguments,
                    )
                    self.client.send_request.return_value = self.session({}, status=status)
                    polling = Mock()

                    def build_polling(no_wait, initial_session, on_success, on_error, **kwargs):
                        self.assertFalse(no_wait)
                        self.assertEqual(initial_session.http_response.status_code, status)
                        self.assertEqual(kwargs["lro_options"], {"final-state-via": "location"})
                        polling.run.side_effect = lambda: on_success(self.session(self.results))
                        return polling

                    self.client.build_lro_polling.side_effect = build_polling
                    poller = command.build_lro_poller(command._execute_operations, command._output)
                    self.assertEqual(poller.result(timeout=5), self.results)
                    polling.run.assert_called_once()
                    self.assert_request("POST", self.workspace_path + suffix, {"queries": [self.encoded_query]})
                    sent_query = self.client._request.call_args.args[4]["queries"][0]
                    self.assertEqual(json.loads(base64.b64decode(sent_query)), self.query_payload)

    def test_query_actions_no_wait_do_not_run_polling(self):
        for command_type in (Query, GenerateReport):
            with self.subTest(command=command_type.__name__):
                arguments = {"discovery_resource_name": "testreport"} if command_type is GenerateReport else {}
                command = self.command(
                    command_type, resource_group="testrg", storage_discovery_workspace_name="testworkspace",
                    queries=[self.encoded_query], no_wait=True, **arguments,
                )
                self.client.send_request.return_value = self.session({}, status=202)
                polling = Mock()
                self.client.build_lro_polling.return_value = polling
                result = command.build_lro_poller(command._execute_operations, command._output)
                self.assertIsNone(result)
                self.assertTrue(self.client.build_lro_polling.call_args.args[0])
                polling.run.assert_not_called()

    def test_query_actions_propagate_http_errors(self):
        for command_type, operation_type in (
            (Query, Query.StorageDiscoveryWorkspacesReport),
            (GenerateReport, GenerateReport.ReportGenerateReport),
        ):
            with self.subTest(command=command_type.__name__):
                arguments = {"discovery_resource_name": "testreport"} if command_type is GenerateReport else {}
                command = self.command(
                    command_type, resource_group="testrg", storage_discovery_workspace_name="testworkspace",
                    queries=[self.encoded_query], **arguments,
                )
                operation = operation_type(command.ctx)
                response = Response()
                response.status_code = 400
                response.reason = "Bad Request"
                response.headers["Content-Type"] = "application/json"
                response._content = json.dumps({
                    "error": {"code": "InvalidQuery", "message": "Invalid query"},
                }).encode("utf-8")
                session = self.session({}, status=400)
                session.http_response = RequestsTransportResponse(None, response)
                self.client.send_request.return_value = session
                with self.assertRaisesRegex(HttpResponseError, "Invalid query"):
                    operation()
