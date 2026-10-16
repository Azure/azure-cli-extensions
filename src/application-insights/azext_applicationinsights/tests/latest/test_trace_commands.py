# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import json
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.cli.core.mock import DummyCli
from knack.util import CLIError

from azext_applicationinsights._trace import (
    TraceAssociationCreate, TraceAssociationDelete, TraceAssociationList, TraceAssociationShow,
    TraceContainerCreate, _container_settings, _destinations, _workspace_arguments,
)
from azext_applicationinsights.aaz.latest.monitor.account.trace_container import Show, Update


SUBSCRIPTION = "00000000-0000-0000-0000-000000000000"
WORKSPACE = f"/subscriptions/{SUBSCRIPTION}/resourceGroups/observability/providers/Microsoft.Monitor/accounts/myAmw"
SUBSCRIPTION_SCOPE = f"/subscriptions/{SUBSCRIPTION}"
GROUP_SCOPE = SUBSCRIPTION_SCOPE + "/resourceGroups/apps"
COMPONENT_SCOPE = GROUP_SCOPE + "/providers/Microsoft.Insights/components/myAi"
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

    @staticmethod
    def status():
        return "Succeeded"


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


def _association(scope, workspace=WORKSPACE):
    return {
        "id": scope + "/providers/Microsoft.Monitor/traceAssociations/default",
        "name": "default",
        "type": "Microsoft.Monitor/traceAssociations",
        "properties": {"azureMonitorWorkspaceResourceId": workspace},
    }


class _TraceCommandTests(unittest.TestCase):
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


class TraceContainerTests(_TraceCommandTests):
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

    def test_trace_container_write_does_not_accept_an_empty_response(self):
        with self.assertRaisesRegex(CLIError, "missing required settings"):
            self.invoke(TraceContainerCreate, [(404, {}), (201, {})])

    def test_trace_container_invalid_response_settings_fail_loudly(self):
        for name, value in (("traceRetentionInDays", None), ("traceMetricsState", None),
                            ("traceDurationWindowInSeconds", 0), ("traceRetentionInDays", 731)):
            with self.subTest(name=name, value=value):
                container = copy.deepcopy(CONTAINER)
                container["properties"][name] = value
                with self.assertRaisesRegex(CLIError, "returned invalid settings"):
                    _container_settings(container)

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


class TraceAssociationTests(_TraceCommandTests):
    def setUp(self):
        super().setUp()
        self.arguments = {"resource_uri": COMPONENT_SCOPE}

    def test_trace_association_create_at_each_scope(self):
        for scope in (COMPONENT_SCOPE, GROUP_SCOPE, SUBSCRIPTION_SCOPE):
            with self.subTest(scope=scope):
                result, requests = self.invoke(TraceAssociationCreate, [
                    (200, {"value": []}), (404, {}), (201, CONTAINER), (200, _association(scope)),
                ], resource_uri=scope, azure_monitor_workspace=WORKSPACE)
                self.assertEqual([request.method for request in requests], ["GET", "GET", "PUT", "PUT"])
                self.assertEqual(requests[3].url, "https://management.azure.com" + _association(scope)["id"])
                self.assertEqual(requests[3].content, {
                    "properties": {"azureMonitorWorkspaceResourceId": WORKSPACE},
                })
                self.assertEqual(result, _association(scope))

    def test_trace_association_reuses_shared_container_without_changing_it(self):
        _, requests = self.invoke(TraceAssociationCreate, [
            (200, {"value": [_association(SUBSCRIPTION_SCOPE)]}),
            (200, CONTAINER), (200, _association(COMPONENT_SCOPE)),
        ], azure_monitor_workspace=WORKSPACE)
        self.assertEqual([request.method for request in requests], ["GET", "GET", "PUT"])
        self.assertTrue(requests[2].url.endswith("/traceAssociations/default"))

    def test_trace_association_rejects_conflicting_container_settings(self):
        for arguments in ({"trace_retention_days": 90}, {"trace_metrics": "Enabled"}):
            with self.subTest(arguments=arguments):
                client = _ArmClient([(200, {"value": []}), (200, CONTAINER)])
                with patch("azure.cli.core.aaz._command_ctx.AAZCommandCtx.get_http_client", return_value=client):
                    with self.assertRaisesRegex(CLIError, "does not modify shared settings"):
                        TraceAssociationCreate(cli_ctx=self.cli_ctx)(command_args={
                            **self.arguments, "azure_monitor_workspace": WORKSPACE, **arguments,
                        })
                self.assertEqual([request.method for request in client.requests], ["GET", "GET"])

    def test_trace_association_create_waits_for_an_existing_container(self):
        pending = copy.deepcopy(CONTAINER)
        pending["properties"]["provisioningState"] = "Creating"
        _, requests = self.invoke(TraceAssociationCreate, [
            (200, {"value": []}), (200, pending), (200, CONTAINER), (200, CONTAINER),
            (200, _association(COMPONENT_SCOPE)),
        ], azure_monitor_workspace=WORKSPACE)
        self.assertEqual([request.method for request in requests], ["GET", "GET", "GET", "GET", "PUT"])

    def test_trace_association_container_timeout_is_an_error(self):
        pending = copy.deepcopy(CONTAINER)
        pending["properties"]["provisioningState"] = "Creating"
        with patch("azext_applicationinsights._trace.WaitCommandOperation.wait", return_value=CLIError("timed out")):
            with self.assertRaisesRegex(CLIError, "timed out"):
                self.invoke(TraceAssociationCreate, [(200, {"value": []}), (200, pending)],
                            azure_monitor_workspace=WORKSPACE)

    def test_trace_association_container_permissions_name_the_owner_command(self):
        with self.assertRaisesRegex(CLIError, "Ask the workspace owner to run"):
            self.invoke(TraceAssociationCreate, [
                (200, {"value": []}), (404, {}), (403, {"error": {"code": "AuthorizationFailed"}}),
            ], azure_monitor_workspace=WORKSPACE)

    def test_trace_association_does_not_follow_an_empty_container_response(self):
        with self.assertRaisesRegex(CLIError, "missing required settings"):
            self.invoke(TraceAssociationCreate, [
                (200, {"value": []}), (404, {}), (201, {}),
            ], azure_monitor_workspace=WORKSPACE)

    def test_trace_association_write_failure_reports_partial_state(self):
        with self.assertRaisesRegex(CLIError, "container is ready"):
            self.invoke(TraceAssociationCreate, [
                (200, {"value": []}), (200, CONTAINER), (500, {"error": {"code": "InternalServerError"}}),
            ], azure_monitor_workspace=WORKSPACE)

    def test_trace_association_unsupported_location_explains_the_region_gate(self):
        with self.assertRaisesRegex(CLIError, "backing Log Analytics workspace region"):
            self.invoke(TraceAssociationCreate, [
                (200, {"value": []}), (200, CONTAINER),
                (400, {"error": {"code": "UnsupportedLocation", "message": "Region is not enabled"}}),
            ], azure_monitor_workspace=WORKSPACE)

    def test_trace_association_retarget_names_old_and_new_workspaces(self):
        target = WORKSPACE.replace("myAmw", "otherAmw")
        with patch("azext_applicationinsights._trace.logger") as logs:
            self.invoke(TraceAssociationCreate, [
                (200, {"value": [_association(COMPONENT_SCOPE)]}), (200, CONTAINER),
                (200, _association(COMPONENT_SCOPE, target)),
            ], azure_monitor_workspace=target)
        self.assertIn("Replaced the trace destination", str(logs.warning.call_args_list))
        self.assertIn(WORKSPACE, str(logs.warning.call_args_list))
        self.assertIn(target, str(logs.warning.call_args_list))

    def test_trace_association_delete_is_idempotent_and_reports_inherited_routes(self):
        for status in (200, 204, 404):
            with self.subTest(status=status):
                with patch("azext_applicationinsights._trace.logger") as logs:
                    result, requests = self.invoke(TraceAssociationDelete, [
                        (status, {}), (200, {"value": [_association(SUBSCRIPTION_SCOPE)]}),
                    ])
                self.assertIsNone(result)
                self.assertEqual([request.method for request in requests], ["DELETE", "GET"])
                self.assertTrue(requests[0].url.endswith(_association(COMPONENT_SCOPE)["id"]))
                self.assertIn(SUBSCRIPTION_SCOPE, str(logs.warning.call_args_list))
                self.assertFalse(any("/traceContainers/" in request.url for request in requests))

    def test_trace_association_delete_report_failure_is_not_success(self):
        with self.assertRaisesRegex(CLIError, "is removed, but reading remaining destinations failed"):
            self.invoke(TraceAssociationDelete, [(204, {}), (500, {"error": {"code": "InternalServerError"}})])

    def test_trace_association_show_does_not_substitute_an_inherited_association(self):
        with self.assertRaises(ResourceNotFoundError):
            self.invoke(TraceAssociationShow, [(404, {})])

    def test_trace_association_list_paginates_and_keeps_each_association(self):
        first, second = _association(COMPONENT_SCOPE), _association(SUBSCRIPTION_SCOPE)
        result, requests = self.invoke(TraceAssociationList, [
            (200, {"value": [first], "nextLink": "https://management.azure.com/next?api-version=2026-09-03-preview"}),
            (200, {"value": [second]}),
        ])
        self.assertEqual(result, [first, second])
        self.assertEqual(len(requests), 2)

    def test_trace_association_destinations_deduplicate_workspaces_not_scopes(self):
        result = _destinations([_association(COMPONENT_SCOPE), _association(SUBSCRIPTION_SCOPE)])
        self.assertEqual(result, [{"workspace": WORKSPACE, "scopes": [COMPONENT_SCOPE, SUBSCRIPTION_SCOPE]}])

    def test_trace_association_invalid_scope_fails_before_requests(self):
        for scope in ("/providers/Microsoft.Management/managementGroups/group",
                      COMPONENT_SCOPE + "/children/child",
                      COMPONENT_SCOPE.replace("Microsoft.Insights/components", "Microsoft.Compute/virtualMachines"),
                      "/subscriptions/not-a-subscription-id"):
            with self.subTest(scope=scope):
                with self.assertRaises(CLIError):
                    self.invoke(TraceAssociationCreate, [], resource_uri=scope, azure_monitor_workspace=WORKSPACE)

    def test_trace_association_invalid_workspace_fails_before_requests(self):
        with self.assertRaises(CLIError):
            self.invoke(TraceAssociationCreate, [], azure_monitor_workspace="not-an-arm-id")

    def test_trace_association_helper_commands_are_not_registered(self):
        from azext_applicationinsights import ApplicationInsightsCommandsLoader
        commands = ApplicationInsightsCommandsLoader(cli_ctx=self.cli_ctx).load_command_table([])
        self.assertIsInstance(commands["monitor trace-association create"], TraceAssociationCreate)
        for scope in ("resource", "resource-group", "subscription"):
            self.assertFalse(any(name.startswith("monitor trace-association " + scope) for name in commands))
