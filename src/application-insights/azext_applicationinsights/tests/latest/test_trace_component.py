# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch, sentinel

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.cli.core.mock import DummyCli
from knack.util import CLIError

from azext_applicationinsights.custom import create_or_update_component, update_component
from azext_applicationinsights._trace_component import _resolve_default_workspace
from azext_applicationinsights.vendored_sdks.mgmt_applicationinsights.v2020_02_02_preview.models import (
    ApplicationInsightsComponent,
)
from .test_trace_commands import (
    _ArmClient, _association, COMPONENT_SCOPE, CONTAINER, GROUP_SCOPE, SUBSCRIPTION, SUBSCRIPTION_SCOPE, WORKSPACE,
)


def _not_found():
    error = ResourceNotFoundError("not found")
    error.status_code = 404
    return error


class TraceComponentTests(unittest.TestCase):
    def setUp(self):
        self.cli_ctx = DummyCli(random_config_dir=True)
        self.cmd = SimpleNamespace(cli_ctx=self.cli_ctx)
        self.component = ApplicationInsightsComponent(location="eastus", kind="web", application_type="web")
        self.component.id = COMPONENT_SCOPE
        self.client = Mock()
        self.client.get.return_value = self.component
        self.client.create_or_update.return_value = self.component
        factory = patch(
            "azext_applicationinsights._client_factory.applicationinsights_mgmt_plane_client",
            return_value=Mock(components=self.client),
        )
        self.factory = factory.start()
        self.addCleanup(factory.stop)
        subscription = patch(
            "azext_applicationinsights._trace_component.get_subscription_id", return_value=SUBSCRIPTION,
        )
        subscription.start()
        self.addCleanup(subscription.stop)
        resources = patch("azext_applicationinsights._trace_component.get_mgmt_service_client")
        self.resources_factory = resources.start()
        self.addCleanup(resources.stop)
        self.resources = self.resources_factory.return_value
        self.resources.providers.get.return_value = SimpleNamespace(resource_types=[
            SimpleNamespace(resource_type="accounts", locations=["East US", "West US 2"]),
        ])
        self.resources.resource_groups.check_existence.return_value = True

    def invoke(self, responses, creating=False, **arguments):
        self.arm = _ArmClient(responses)
        with patch("azure.cli.core.aaz._command_ctx.AAZCommandCtx.get_http_client", return_value=self.arm):
            if creating:
                result = create_or_update_component(
                    self.cmd, self.client, "myAi", "apps", "eastus", **arguments,
                )
            else:
                result = update_component(self.cmd, self.client, "myAi", "apps", **arguments)
        return result, self.arm.requests

    def test_trace_component_explicit_onboarding_does_not_put_the_component(self):
        result, requests = self.invoke([
            (200, {"value": []}), (404, {}), (201, CONTAINER), (200, _association(COMPONENT_SCOPE)),
        ], enable_traces=True, trace_workspace=WORKSPACE)
        self.assertIs(result, self.component)
        self.client.create_or_update.assert_not_called()
        self.assertEqual([request.method for request in requests], ["GET", "GET", "PUT", "PUT"])
        self.factory.assert_called_once_with(self.cli_ctx, api_version="2020-02-02-preview")

    def test_trace_component_creates_container_before_creating_component(self):
        self.client.get.side_effect = _not_found()

        def create_component(*_args):
            self.assertEqual([request.method for request in self.arm.requests], ["GET", "GET", "PUT"])
            return self.component

        self.client.create_or_update.side_effect = create_component
        result, requests = self.invoke([
            (200, {"value": []}), (404, {}), (201, CONTAINER), (200, _association(COMPONENT_SCOPE)),
        ], creating=True, enable_traces=True, trace_workspace=WORKSPACE)
        self.assertIs(result, self.component)
        self.assertEqual(requests[0].url, "https://management.azure.com" + GROUP_SCOPE
                         + "/providers/Microsoft.Monitor/traceAssociations")
        self.assertTrue(requests[-1].url.endswith(_association(COMPONENT_SCOPE)["id"]))
        self.client.create_or_update.assert_called_once()

    def test_trace_component_combines_component_changes_with_onboarding(self):
        _, requests = self.invoke([
            (200, {"value": []}), (200, CONTAINER), (200, _association(COMPONENT_SCOPE)),
        ], enable_traces=True, trace_workspace=WORKSPACE, kind="other")
        self.client.create_or_update.assert_called_once()
        self.assertEqual(self.client.create_or_update.call_args.args[2].kind, "other")
        self.assertEqual([request.method for request in requests], ["GET", "GET", "PUT"])

    def test_trace_component_workspace_name_resolves_in_component_scope(self):
        _, requests = self.invoke([
            (200, {"value": []}), (200, CONTAINER),
            (200, _association(COMPONENT_SCOPE, WORKSPACE.replace("observability", "apps"))),
        ], enable_traces=True, trace_workspace="myAmw")
        self.assertIn("/resourceGroups/apps/providers/Microsoft.Monitor/accounts/myAmw/", requests[1].url)

    def test_trace_component_cross_subscription_workspace_does_not_change_source_scope(self):
        target = WORKSPACE.replace(SUBSCRIPTION, "11111111-1111-1111-1111-111111111111")
        _, requests = self.invoke([
            (200, {"value": []}), (200, CONTAINER), (200, _association(COMPONENT_SCOPE, target)),
        ], enable_traces=True, trace_workspace=target)
        self.assertIn("/subscriptions/11111111-1111-1111-1111-111111111111/", requests[1].url)
        self.assertIn("/subscriptions/" + SUBSCRIPTION + "/", requests[2].url)
        self.assertEqual(requests[2].content["properties"]["azureMonitorWorkspaceResourceId"], target)

    def test_trace_component_retarget_without_enable_flag(self):
        target = WORKSPACE.replace("myAmw", "otherAmw")
        _, requests = self.invoke([
            (200, {"value": [_association(COMPONENT_SCOPE), _association(SUBSCRIPTION_SCOPE)]}),
            (200, CONTAINER), (200, _association(COMPONENT_SCOPE, target)),
        ], trace_workspace=target)
        self.assertEqual([request.method for request in requests], ["GET", "GET", "PUT"])
        self.assertTrue(requests[-1].url.endswith(_association(COMPONENT_SCOPE)["id"]))
        self.client.create_or_update.assert_not_called()

    def test_trace_component_existing_own_association_is_not_retargeted(self):
        _, requests = self.invoke([
            (200, {"value": [_association(COMPONENT_SCOPE)]}), (200, CONTAINER),
        ], enable_traces=True)
        self.assertEqual([request.method for request in requests], ["GET", "GET"])
        self.client.create_or_update.assert_not_called()
        self.resources_factory.assert_not_called()

    def test_trace_component_create_retry_keeps_its_existing_workspace(self):
        _, requests = self.invoke([
            (200, {"value": [_association(COMPONENT_SCOPE)]}), (200, CONTAINER),
        ], creating=True, enable_traces=True)
        self.assertEqual([request.method for request in requests], ["GET", "GET"])
        self.assertIn("/Microsoft.Insights/components/myAi/", requests[0].url)
        self.client.create_or_update.assert_called_once()
        self.resources_factory.assert_not_called()

    def test_trace_component_inherited_routes_are_not_duplicated_or_provisioned(self):
        with patch("azext_applicationinsights._trace_component.logger") as logs:
            _, requests = self.invoke([
                (200, {"value": [_association(GROUP_SCOPE), _association(SUBSCRIPTION_SCOPE)]}), (404, {}),
            ], enable_traces=True)
        self.assertEqual([request.method for request in requests], ["GET", "GET"])
        self.assertIn("nothing is being stored", str(logs.warning.call_args_list))
        self.assertIn("trace-container create", str(logs.warning.call_args_list))
        self.resources_factory.assert_not_called()
        self.client.create_or_update.assert_not_called()

    def test_trace_component_new_app_inherits_without_creating_an_association(self):
        self.client.get.side_effect = _not_found()
        _, requests = self.invoke([
            (200, {"value": [_association(GROUP_SCOPE)]}), (200, CONTAINER),
        ], creating=True, enable_traces=True)
        self.assertEqual([request.method for request in requests], ["GET", "GET"])
        self.client.create_or_update.assert_called_once()
        self.resources_factory.assert_not_called()

    def test_trace_component_inherited_settings_need_an_explicit_workspace(self):
        with self.assertRaisesRegex(CLIError, "inherits its trace workspaces"):
            self.invoke([(200, {"value": [_association(SUBSCRIPTION_SCOPE)]})],
                        enable_traces=True, trace_retention_days=90)
        self.client.create_or_update.assert_not_called()

    def test_trace_component_default_workspace_is_created_and_awaited(self):
        self.resources.resource_groups.check_existence.return_value = False
        self.resources.resources.get_by_id.side_effect = _not_found()
        target = (f"/subscriptions/{SUBSCRIPTION}/resourceGroups/DefaultResourceGroup-eastus"
                  "/providers/Microsoft.Monitor/accounts/DefaultAzureMonitorWorkspace-eastus")
        _, requests = self.invoke([
            (200, {"value": []}), (404, {}), (201, CONTAINER), (200, _association(COMPONENT_SCOPE, target)),
        ], enable_traces=True)
        self.resources.resource_groups.create_or_update.assert_called_once_with(
            "DefaultResourceGroup-eastus", {"location": "eastus"},
        )
        self.resources.resources.begin_create_or_update_by_id.assert_called_once_with(
            target, "2023-04-03", {"location": "eastus", "properties": {}},
        )
        self.resources.resources.begin_create_or_update_by_id.return_value.result.assert_called_once()
        self.assertEqual(requests[-1].content["properties"]["azureMonitorWorkspaceResourceId"], target)

    def test_trace_component_existing_default_workspace_is_not_rewritten(self):
        target = (f"/subscriptions/{SUBSCRIPTION}/resourceGroups/DefaultResourceGroup-eastus"
                  "/providers/Microsoft.Monitor/accounts/DefaultAzureMonitorWorkspace-eastus")
        self.invoke([
            (200, {"value": []}), (200, CONTAINER), (200, _association(COMPONENT_SCOPE, target)),
        ], enable_traces=True)
        self.resources.resource_groups.create_or_update.assert_not_called()
        self.resources.resources.begin_create_or_update_by_id.assert_not_called()

    def test_trace_component_default_workspace_region_policy(self):
        for source, locations, expected in (
            ("centraluseuap", ["East US"], "eastus2euap"),
            ("West US 2", ["East US", "West US 2"], "westus2"),
            ("australiaeast", ["West Europe", "East US"], "westeurope"),
            ("australiaeast", [], "eastus"),
        ):
            with self.subTest(source=source, locations=locations):
                self.resources.providers.get.return_value.resource_types[0].locations = locations
                workspace = _resolve_default_workspace(self.cli_ctx, COMPONENT_SCOPE, source)
                self.assertTrue(workspace.endswith("/DefaultAzureMonitorWorkspace-" + expected))

    def test_trace_component_offboarding_keeps_inherited_routing(self):
        result, requests = self.invoke([
            (404, {}), (200, {"value": [_association(SUBSCRIPTION_SCOPE)]}),
        ], disable_traces=True)
        self.assertIs(result, self.component)
        self.assertEqual([request.method for request in requests], ["DELETE", "GET"])
        self.client.create_or_update.assert_not_called()

    def test_trace_component_flags_validate_before_any_requests(self):
        for arguments in (
            {"enable_traces": True, "disable_traces": True},
            {"disable_traces": True, "trace_workspace": WORKSPACE},
            {"trace_retention_days": 30}, {"trace_metrics": "Enabled"},
            {"enable_traces": True, "trace_retention_days": 3},
            {"enable_traces": True, "trace_metrics": "invalid"},
            {"trace_workspace": ""},
        ):
            with self.subTest(arguments=arguments):
                with self.assertRaises(CLIError):
                    self.invoke([], **arguments)
        self.factory.assert_not_called()
        self.client.create_or_update.assert_not_called()

    def test_trace_component_create_failure_keeps_reusable_container(self):
        self.client.get.side_effect = _not_found()
        self.client.create_or_update.side_effect = CLIError("component rejected")
        with self.assertRaisesRegex(CLIError, "container is reusable"):
            self.invoke([(200, {"value": []}), (404, {}), (201, CONTAINER)],
                        creating=True, enable_traces=True, trace_workspace=WORKSPACE)
        self.assertEqual([request.method for request in self.arm.requests], ["GET", "GET", "PUT"])

    def test_trace_component_association_failure_reports_created_component(self):
        self.client.get.side_effect = _not_found()
        with self.assertRaisesRegex(CLIError, "was created, but enabling traces failed"):
            self.invoke([
                (200, {"value": []}), (200, CONTAINER),
                (500, {"error": {"code": "InternalServerError"}}),
            ], creating=True, enable_traces=True, trace_workspace=WORKSPACE)
        self.client.create_or_update.assert_called_once()
        self.assertFalse(any(request.method == "DELETE" for request in self.arm.requests))

    def test_trace_component_update_requires_an_existing_component(self):
        self.client.get.side_effect = _not_found()
        with self.assertRaises(ResourceNotFoundError):
            self.invoke([], enable_traces=True, trace_workspace=WORKSPACE)

    def test_trace_component_without_trace_flags_uses_legacy_create_unchanged(self):
        with patch("azext_applicationinsights.custom._create_or_update_component", return_value=sentinel.component) as write:
            result, requests = self.invoke([], creating=True, kind="other", tags={"tag": "value"})
        self.assertIs(result, sentinel.component)
        self.assertEqual(requests, [])
        self.assertEqual(write.call_args.kwargs["tags"], {"tag": "value"})
        self.assertEqual(write.call_args.kwargs["kind"], "other")
        self.factory.assert_not_called()

    def test_trace_component_without_trace_flags_uses_legacy_update_unchanged(self):
        with patch("azext_applicationinsights.custom._update_component", return_value=sentinel.component) as write:
            result, requests = self.invoke([], kind="other")
        self.assertIs(result, sentinel.component)
        self.assertEqual(requests, [])
        self.assertEqual(write.call_args.kwargs["kind"], "other")
        self.factory.assert_not_called()
