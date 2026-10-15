# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import json
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.cli.core.mock import DummyCli
from knack.util import CLIError

from azext_applicationinsights._trace import TraceContainerCreate, _container_settings, _workspace_arguments
from azext_applicationinsights.aaz.latest.monitor.account.trace_container import Show, Update


SUBSCRIPTION = "00000000-0000-0000-0000-000000000000"
WORKSPACE = f"/subscriptions/{SUBSCRIPTION}/resourceGroups/observability/providers/Microsoft.Monitor/accounts/myAmw"
CONTAINER = {
    "id": WORKSPACE + "/traceContainers/default",
    "name": "default",
    "type": "Microsoft.Monitor/accounts/traceContainers",
    "properties": {
        "provisioningState": "Succeeded",
        "traceRetentionInDays": 60,
        "traceDurationWindowInSeconds": 300,
        "traceMetricsState": "Disabled",
    },
}


class _Polling:
    def __init__(self, callback):
        self._callback = callback

    def run(self):
        self._callback()

    @staticmethod
    def resource():
        return None


class _ArmClient:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []

    @staticmethod
    def format_url(template, **parameters):
        return "https://management.azure.com" + template.format(**parameters)

    @staticmethod
    def _request(method, url, parameters, headers, content, _form, _stream):
        return SimpleNamespace(method=method, url=url, parameters=parameters, headers=headers, content=content)

    def send_request(self, request, **_kwargs):
        self.requests.append(request)
        status, body = next(self.responses)
        response = Mock(status_code=status, reason="test response", headers={})
        response.text.return_value = json.dumps(body)
        response.json.return_value = body
        return SimpleNamespace(
            http_response=response,
            context={ContentDecodePolicy.CONTEXT_NAME: copy.deepcopy(body)},
        )

    @staticmethod
    def build_lro_polling(_no_wait, session, on_success, _on_error, **_kwargs):
        return _Polling(lambda: on_success(session))


class TraceContainerTests(unittest.TestCase):
    def setUp(self):
        self.cli_ctx = DummyCli(random_config_dir=True)
        self.arguments = {
            "subscription": SUBSCRIPTION,
            "resource_group": "observability",
            "azure_monitor_workspace_name": "myAmw",
        }

    def invoke(self, command, responses, **arguments):
        client = _ArmClient(responses)
        with patch("azure.cli.core.aaz._command_ctx.AAZCommandCtx.get_http_client", return_value=client):
            result = command(cli_ctx=self.cli_ctx)(command_args={**self.arguments, **arguments})
            if result is not None and hasattr(result, "result"):
                result = result.result()
        return result, client.requests

    def test_trace_container_create_defaults(self):
        result, requests = self.invoke(TraceContainerCreate, [(404, {}), (201, CONTAINER)])
        self.assertEqual([request.method for request in requests], ["GET", "PUT"])
        self.assertEqual(requests[1].content, {"properties": {
            "traceRetentionInDays": 30,
            "traceDurationWindowInSeconds": 600,
            "traceMetricsState": "Enabled",
        }})
        self.assertEqual(requests[1].parameters, {"api-version": "2026-09-03-preview"})
        self.assertTrue(requests[1].url.endswith("/accounts/myAmw/traceContainers/default"))
        self.assertEqual(result["id"], CONTAINER["id"])

    def test_trace_container_create_preserves_omitted_settings(self):
        _, requests = self.invoke(
            TraceContainerCreate, [(200, CONTAINER), (200, CONTAINER)], retention_days=90
        )
        self.assertEqual(requests[1].content["properties"], {
            "traceRetentionInDays": 90,
            "traceDurationWindowInSeconds": 300,
            "traceMetricsState": "Disabled",
        })

    def test_trace_container_update_merges_settings(self):
        _, requests = self.invoke(Update, [(200, CONTAINER), (200, CONTAINER)], retention_days=90)
        self.assertEqual([request.method for request in requests], ["GET", "PUT"])
        self.assertEqual(requests[1].content["properties"], {
            "traceRetentionInDays": 90,
            "traceDurationWindowInSeconds": 300,
            "traceMetricsState": "Disabled",
        })
        self.assertNotIn("provisioningState", requests[1].content["properties"])

    def test_trace_container_show(self):
        result, requests = self.invoke(Show, [(200, CONTAINER)])
        self.assertEqual(result["properties"], CONTAINER["properties"])
        self.assertEqual(len(requests), 1)

    def test_trace_container_no_wait(self):
        result, requests = self.invoke(
            TraceContainerCreate, [(404, {}), (201, CONTAINER)], no_wait=True
        )
        self.assertIsNone(result)
        self.assertEqual([request.method for request in requests], ["GET", "PUT"])

    def test_trace_container_read_errors_are_not_missing_containers(self):
        with self.assertRaises(HttpResponseError):
            self.invoke(TraceContainerCreate, [(403, {"error": {"code": "AuthorizationFailed"}})])

    def test_trace_container_invalid_settings_fail_before_requests(self):
        for arguments in ({"retention_days": 3}, {"retention_days": 731},
                          {"trace_duration_window": 119}, {"trace_duration_window": 601},
                          {"trace_metrics": "invalid"}):
            with self.subTest(arguments=arguments):
                client = _ArmClient([])
                with patch("azure.cli.core.aaz._command_ctx.AAZCommandCtx.get_http_client", return_value=client):
                    with self.assertRaises(CLIError):
                        TraceContainerCreate(cli_ctx=self.cli_ctx)(
                            command_args={**self.arguments, **arguments}
                        ).result()
                self.assertEqual(client.requests, [])

    def test_trace_container_missing_settings_fail_loudly(self):
        with self.assertRaisesRegex(CLIError, "missing required settings"):
            _container_settings({"properties": {"traceRetentionInDays": 30}})

    def test_trace_workspace_arguments_use_the_workspace_subscription(self):
        other_subscription = "11111111-1111-1111-1111-111111111111"
        arguments = _workspace_arguments(WORKSPACE.replace(SUBSCRIPTION, other_subscription))
        self.assertEqual(arguments["subscription"], other_subscription)
        self.assertEqual(arguments["resource_group"], "observability")

    def test_trace_workspace_rejects_other_resource_types(self):
        for workspace in ("myAmw", WORKSPACE + "/traceContainers/default",
                          WORKSPACE.replace("Microsoft.Monitor/accounts", "Microsoft.Storage/storageAccounts")):
            with self.subTest(workspace=workspace):
                with self.assertRaises(CLIError):
                    _workspace_arguments(workspace)
