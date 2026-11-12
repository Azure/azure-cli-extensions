# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.cli.core.azclierror import ClientRequestError, InvalidArgumentValueError, UnauthorizedError
from azure.cli.core.util import todict

from azext_aimanager import custom
from azext_aimanager._params import load_arguments
from azext_aimanager.vendored_sdks.v2026_09_02_preview import models


class MockCmd:
    def get_models(self, name, **_):
        return getattr(models, name)


class TestModelDeployment(unittest.TestCase):

    def setUp(self):
        self.cmd = MockCmd()

    def test_manual_scaling(self):
        scale = custom._construct_scaling_profile(self.cmd, replicas=0, required=True)

        self.assertEqual(scale.manual.replicas, 0)
        self.assertIsNone(scale.autoscale)

    def test_scaling_modes_are_mutually_exclusive(self):
        with self.assertRaises(InvalidArgumentValueError):
            custom._construct_scaling_profile(
                self.cmd, replicas=1, min_replicas=1, required=True)

    def test_autoscale_requires_minimum_when_not_already_enabled(self):
        with self.assertRaises(InvalidArgumentValueError):
            custom._construct_scaling_profile(
                self.cmd, max_replicas=3, required=True)

    def test_scaling_rejects_invalid_values(self):
        cases = [
            ({"replicas": -1}, "--replicas must be zero or greater"),
            ({"min_replicas": 0}, "--min-replicas must be at least 1"),
            ({"min_replicas": 3, "max_replicas": 2},
             "--max-replicas must be greater than or equal to --min-replicas"),
            ({"required": True}, "Specify either --replicas or --min-replicas"),
            ({"replicas": 1, "max_replicas": 3}, "--replicas cannot be combined"),
        ]
        for kwargs, message in cases:
            with self.subTest(**kwargs):
                with self.assertRaisesRegex(InvalidArgumentValueError, message):
                    custom._construct_scaling_profile(self.cmd, **kwargs)

    def test_scaling_is_optional_when_not_required(self):
        self.assertIsNone(custom._construct_scaling_profile(self.cmd))

    def test_partial_autoscale_updates_preserve_omitted_bound(self):
        existing = models.ScalingProfile(
            autoscale=models.AutoscaleProfile(min_replicas=2, max_replicas=5))
        for kwargs, expected in [
                ({"max_replicas": 8}, (2, 8)),
                ({"min_replicas": 3}, (3, 5))]:
            with self.subTest(**kwargs):
                scale = custom._construct_scaling_profile(
                    self.cmd, existing_scale=existing, **kwargs)
                self.assertIsNone(scale.manual)
                self.assertEqual(
                    (scale.autoscale.min_replicas, scale.autoscale.max_replicas), expected)
                self.assertEqual(
                    (existing.autoscale.min_replicas, existing.autoscale.max_replicas), (2, 5))

    def test_autoscale_rejects_minimum_above_preserved_maximum(self):
        existing = models.ScalingProfile(
            autoscale=models.AutoscaleProfile(min_replicas=2, max_replicas=5))
        with self.assertRaisesRegex(
                InvalidArgumentValueError, "--max-replicas must be greater"):
            custom._construct_scaling_profile(
                self.cmd, min_replicas=6, existing_scale=existing)

    def test_scaling_switches_between_manual_and_autoscale(self):
        manual = models.ScalingProfile(manual=models.ManualScalingProfile(replicas=2))
        autoscale = custom._construct_scaling_profile(
            self.cmd, min_replicas=1, max_replicas=4, existing_scale=manual)
        self.assertIsNone(autoscale.manual)
        self.assertEqual(autoscale.autoscale.min_replicas, 1)
        self.assertEqual(autoscale.autoscale.max_replicas, 4)

        manual = custom._construct_scaling_profile(
            self.cmd, replicas=0, existing_scale=autoscale)
        self.assertIsNone(manual.autoscale)
        self.assertEqual(manual.manual.replicas, 0)

    def test_namespace_name_options_list(self):
        class ArgumentContext:
            def __init__(self, loader, command):
                self.loader = loader
                self.command = command

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def argument(self, name, *args, **kwargs):
                self.loader.arguments.setdefault(self.command, {})[name] = kwargs

            def extra(self, name, *args, **kwargs):
                self.argument(name, *args, **kwargs)

            def ignore(self, *_):
                pass

        class Loader:
            def __init__(self):
                self.arguments = {}
                self.cli_ctx = MagicMock()

            def argument_context(self, command, **kwargs):
                return ArgumentContext(self, command)

        loader = Loader()
        load_arguments(loader, None)

        namespace_argument = loader.arguments[
            "aimanager namespace modeldeployment"]["namespace_name"]
        self.assertEqual(
            ["--namespace", "--ns"], namespace_argument["options_list"])

    @patch.object(custom, "_annotate_model_ids", side_effect=lambda _cmd, d: d)
    def test_list_single_namespace(self, _annotate):
        client = MagicMock()
        client.list_by_ai_manager_namespace.return_value = ["d1"]

        result = custom.list_modeldeployment(
            self.cmd, client, "rg", "mgr", namespace_name="ns1")

        self.assertEqual(["d1"], result)
        client.list_by_ai_manager_namespace.assert_called_once_with("rg", "mgr", "ns1")

    @patch.object(custom, "_annotate_model_ids", side_effect=lambda _cmd, d: d)
    @patch("azext_aimanager._client_factory.cf_ai_manager_namespaces")
    def test_list_without_namespace_aggregates_across_namespaces(
            self, cf_namespaces, _annotate):
        namespaces_client = MagicMock()
        namespaces_client.list_by_ai_manager.return_value = [
            SimpleNamespace(name="ns1"), SimpleNamespace(name="ns2")]
        cf_namespaces.return_value = namespaces_client
        self.cmd.cli_ctx = MagicMock()

        client = MagicMock()
        client.list_by_ai_manager_namespace.side_effect = [["d1"], ["d2", "d3"]]

        result = custom.list_modeldeployment(self.cmd, client, "rg", "mgr")

        self.assertEqual(["d1", "d2", "d3"], result)
        namespaces_client.list_by_ai_manager.assert_called_once_with("rg", "mgr")
        self.assertEqual(
            [call("rg", "mgr", "ns1"), call("rg", "mgr", "ns2")],
            client.list_by_ai_manager_namespace.call_args_list)
        _annotate.assert_called_once_with(self.cmd, ["d1", "d2", "d3"])

    @patch.object(custom, "_annotate_model_ids", side_effect=lambda _cmd, d: d)
    @patch("azext_aimanager._client_factory.cf_ai_manager_namespaces")
    def test_list_without_namespace_skips_forbidden_namespaces(
            self, cf_namespaces, _annotate):
        namespaces_client = MagicMock()
        namespaces_client.list_by_ai_manager.return_value = [
            SimpleNamespace(name="ns1"), SimpleNamespace(name="ns2")]
        cf_namespaces.return_value = namespaces_client
        self.cmd.cli_ctx = MagicMock()

        forbidden = HttpResponseError(message="Forbidden")
        forbidden.status_code = 403

        client = MagicMock()
        client.list_by_ai_manager_namespace.side_effect = [forbidden, ["d2"]]

        with self.assertLogs(custom.logger, level="WARNING") as logs:
            result = custom.list_modeldeployment(self.cmd, client, "rg", "mgr")

        self.assertEqual(["d2"], result)
        # The full warning names the skipped namespace and the reason.
        self.assertTrue(any(
            "Skipping namespace 'ns1': not authorized to read its model deployments." in line
            for line in logs.output))
        self.assertEqual(2, client.list_by_ai_manager_namespace.call_count)

    @patch.object(custom, "_annotate_model_ids", side_effect=lambda _cmd, d: d)
    @patch("azext_aimanager._client_factory.cf_ai_manager_namespaces")
    def test_list_without_namespace_reraises_non_auth_errors(
            self, cf_namespaces, _annotate):
        namespaces_client = MagicMock()
        namespaces_client.list_by_ai_manager.return_value = [SimpleNamespace(name="ns1")]
        cf_namespaces.return_value = namespaces_client
        self.cmd.cli_ctx = MagicMock()

        server_error = HttpResponseError(message="Boom")
        server_error.status_code = 500

        client = MagicMock()
        client.list_by_ai_manager_namespace.side_effect = server_error

        with self.assertRaises(HttpResponseError):
            custom.list_modeldeployment(self.cmd, client, "rg", "mgr")

    @patch.object(custom, "_annotate_model_ids", side_effect=lambda _cmd, d: d)
    @patch("azext_aimanager._client_factory.cf_ai_manager_namespaces")
    def test_list_without_namespace_propagates_namespace_list_unauthorized(
            self, cf_namespaces, _annotate):
        unauthorized = HttpResponseError(message="Forbidden")
        unauthorized.status_code = 403

        namespaces_client = MagicMock()
        namespaces_client.list_by_ai_manager.side_effect = unauthorized
        cf_namespaces.return_value = namespaces_client
        self.cmd.cli_ctx = MagicMock()

        client = MagicMock()

        # The caller cannot enumerate namespaces (permission layer 1): the error names the
        # namespace-read requirement on the AI Manager and points at --namespace/--ns.
        with self.assertRaises(UnauthorizedError) as ctx:
            custom.list_modeldeployment(self.cmd, client, "rg", "mgr")
        recs = " ".join(ctx.exception.recommendations)
        self.assertEqual(
            "Listing model deployments without --namespace/--ns first lists namespaces, which "
            "requires namespace read permission on AI Manager 'mgr'. Grant that permission, or "
            "specify --namespace/--ns to list model deployments for a single namespace.",
            recs)
        client.list_by_ai_manager_namespace.assert_not_called()

    @patch.object(custom, "_annotate_model_ids", side_effect=lambda _cmd, d: d)
    @patch("azext_aimanager._client_factory.cf_ai_manager_namespaces")
    def test_list_without_namespace_all_forbidden_raises(
            self, cf_namespaces, _annotate):
        namespaces_client = MagicMock()
        namespaces_client.list_by_ai_manager.return_value = [
            SimpleNamespace(name="ns1"), SimpleNamespace(name="ns2")]
        cf_namespaces.return_value = namespaces_client
        self.cmd.cli_ctx = MagicMock()

        forbidden = HttpResponseError(message="Forbidden")
        forbidden.status_code = 403

        client = MagicMock()
        client.list_by_ai_manager_namespace.side_effect = [forbidden, forbidden]

        # Namespaces list fine, but the caller lacks model deployment read on every one
        # (permission layer 2): the error names the per-namespace model-deployment-read
        # requirement. It must NOT suggest --namespace/--ns, since scoping to one namespace
        # would fail too.
        with self.assertRaises(UnauthorizedError) as ctx:
            custom.list_modeldeployment(self.cmd, client, "rg", "mgr")
        recs = " ".join(ctx.exception.recommendations)
        self.assertEqual(
            "Not authorized to read model deployments in any namespace of AI Manager 'mgr'. "
            "Ask for model deployment read access on a namespace of this AI Manager, or on the "
            "AI Manager resource itself to cover all its namespaces.",
            recs)
        self.assertNotIn("--namespace", recs)
        self.assertEqual(2, client.list_by_ai_manager_namespace.call_count)

    @patch.object(custom, "_annotate_model_ids", side_effect=lambda _cmd, d: d)
    @patch("azext_aimanager._client_factory.cf_ai_manager_namespaces")
    def test_list_without_namespaces_returns_empty(self, cf_namespaces, annotate):
        self.cmd.cli_ctx = MagicMock()
        cf_namespaces.return_value.list_by_ai_manager.return_value = []
        client = MagicMock()

        self.assertEqual([], custom.list_modeldeployment(self.cmd, client, "rg", "mgr"))

        client.list_by_ai_manager_namespace.assert_not_called()
        annotate.assert_called_once_with(self.cmd, [])

    @patch.object(custom, "_annotate_model_ids", side_effect=lambda _cmd, d: d)
    @patch("azext_aimanager._client_factory.cf_ai_manager_namespaces")
    def test_list_readable_empty_namespace_and_forbidden_returns_empty(
            self, cf_namespaces, annotate):
        self.cmd.cli_ctx = MagicMock()
        cf_namespaces.return_value.list_by_ai_manager.return_value = [
            SimpleNamespace(name="ns1"), SimpleNamespace(name="ns2")]
        for status in (401, 403):
            for forbidden_first in (True, False):
                with self.subTest(status=status, forbidden_first=forbidden_first):
                    error = HttpResponseError(message="Denied")
                    error.status_code = status
                    client = MagicMock()
                    client.list_by_ai_manager_namespace.side_effect = (
                        [error, []] if forbidden_first else [[], error])
                    with self.assertLogs(custom.logger, level="WARNING"):
                        result = custom.list_modeldeployment(self.cmd, client, "rg", "mgr")
                    self.assertEqual([], result)
                    self.assertEqual(
                        [call("rg", "mgr", "ns1"), call("rg", "mgr", "ns2")],
                        client.list_by_ai_manager_namespace.call_args_list)
                    annotate.assert_called_with(self.cmd, [])

    @patch.object(custom, "_annotate_model_ids")
    @patch("azext_aimanager._client_factory.cf_ai_manager_namespaces")
    def test_list_namespace_enumeration_errors(self, cf_namespaces, annotate):
        self.cmd.cli_ctx = MagicMock()
        client = MagicMock()
        for status in (401, 500):
            with self.subTest(status=status):
                error = HttpResponseError(message="Enumeration failed")
                error.status_code = status
                cf_namespaces.return_value.list_by_ai_manager.side_effect = error
                expected_error = UnauthorizedError if status == 401 else HttpResponseError
                with self.assertRaises(expected_error) as ctx:
                    custom.list_modeldeployment(self.cmd, client, "rg", "mgr")
                if status == 401:
                    self.assertIn(
                        "requires namespace read permission",
                        " ".join(ctx.exception.recommendations))
                else:
                    self.assertIs(ctx.exception, error)
        client.list_by_ai_manager_namespace.assert_not_called()
        annotate.assert_not_called()

    @patch.object(custom, "_annotate_model_ids")
    def test_list_single_namespace_propagates_auth_errors(self, annotate):
        for status in (401, 403):
            with self.subTest(status=status):
                error = HttpResponseError(message="Denied")
                error.status_code = status
                client = MagicMock()
                client.list_by_ai_manager_namespace.side_effect = error
                with self.assertRaises(HttpResponseError) as ctx:
                    custom.list_modeldeployment(
                        self.cmd, client, "rg", "mgr", namespace_name="ns1")
                self.assertIs(ctx.exception, error)
                client.list_by_ai_manager_namespace.assert_called_once_with("rg", "mgr", "ns1")
        annotate.assert_not_called()

    @patch("azext_aimanager._client_factory.cf_ai_manager_namespaces")
    def test_list_all_namespaces_unauthorized_raises(self, cf_namespaces):
        self.cmd.cli_ctx = MagicMock()
        cf_namespaces.return_value.list_by_ai_manager.return_value = [
            SimpleNamespace(name="ns1")]
        error = HttpResponseError(message="Unauthorized")
        error.status_code = 401
        client = MagicMock()
        client.list_by_ai_manager_namespace.side_effect = error
        with self.assertLogs(custom.logger, level="WARNING"):
            with self.assertRaises(UnauthorizedError) as ctx:
                custom.list_modeldeployment(self.cmd, client, "rg", "mgr")
        self.assertIn(
            "model deployment read access", " ".join(ctx.exception.recommendations))

    @patch.object(custom, "_annotate_model_id_on_completion", side_effect=lambda _cmd, p, _nw: p)
    @patch.object(custom, "sdk_no_wait")
    @patch.object(custom, "_construct_modeldeployment")
    def test_update_preserves_omitted_properties_without_etag_precondition(
            self, construct_modeldeployment, sdk_no_wait, _annotate):
        existing_scale = models.ScalingProfile(
            manual=models.ManualScalingProfile(replicas=2))
        existing_overrides = models.ModelDeploymentOverrides(
            values_property={"engine": "vllm"})
        existing = SimpleNamespace(
            e_tag='"etag-value"',
            properties=SimpleNamespace(
                model_resource_id="/models/model-a",
                model_source_resource_id="/sources/source-a",
                performance_mode="Latency",
                vm_size="Standard_NC24ads_A100_v4",
                scale=existing_scale,
                overrides=existing_overrides,
            ),
        )
        client = MagicMock()
        client.get.return_value = existing
        deployment = object()
        construct_modeldeployment.return_value = deployment
        sdk_no_wait.return_value = "result"

        result = custom.update_modeldeployment(
            self.cmd, client, "rg", "manager", "namespace", "deployment")

        self.assertEqual(result, "result")
        _annotate.assert_called_once_with(self.cmd, "result", False)
        construct_modeldeployment.assert_called_once_with(
            self.cmd,
            "/models/model-a",
            "Standard_NC24ads_A100_v4",
            "/sources/source-a",
            "Latency",
            existing_scale,
            {"engine": "vllm"},
        )
        sdk_no_wait.assert_called_once_with(
            False,
            client.begin_create_or_update,
            "rg",
            "manager",
            "namespace",
            "deployment",
            deployment,
            headers={},
        )

    @patch.object(custom, "_annotate_model_id_on_completion", return_value="annotated")
    @patch.object(custom, "sdk_no_wait", return_value="poller")
    def test_update_applies_explicit_changes_and_preserves_omitted_properties(
            self, sdk_no_wait, annotate):
        for changes in (
                {"performance_mode": "Throughput"},
                {"replicas": 0},
                {"overrides": ["engine=new", "setting=a=b"]},
                {"performance_mode": "Throughput", "replicas": 0,
                 "overrides": ["engine=new", "setting=a=b"]}):
            with self.subTest(changes=changes):
                client = MagicMock()
                existing_scale = models.ScalingProfile(
                    manual=models.ManualScalingProfile(replicas=2))
                client.get.return_value = SimpleNamespace(properties=SimpleNamespace(
                    model_resource_id="/models/model-a",
                    model_source_resource_id="/sources/source-a",
                    vm_size="Standard_NC24ads_A100_v4",
                    performance_mode="Latency",
                    scale=existing_scale,
                    overrides=models.ModelDeploymentOverrides(
                        values_property={"engine": "old"}),
                ))

                result = custom.update_modeldeployment(
                    self.cmd, client, "rg", "manager", "namespace", "deployment", **changes)

                self.assertEqual(result, "annotated")
                client.get.assert_called_once_with("rg", "manager", "namespace", "deployment")
                properties = sdk_no_wait.call_args.args[-1].properties
                self.assertEqual(properties.model_resource_id, "/models/model-a")
                self.assertEqual(properties.model_source_resource_id, "/sources/source-a")
                self.assertEqual(properties.vm_size, "Standard_NC24ads_A100_v4")
                self.assertEqual(
                    properties.performance_mode, changes.get("performance_mode", "Latency"))
                self.assertEqual(properties.scale.manual.replicas, changes.get("replicas", 2))
                self.assertEqual(
                    properties.overrides.values_property,
                    {"engine": "new", "setting": "a=b"} if "overrides" in changes
                    else {"engine": "old"})
                annotate.assert_called_with(self.cmd, "poller", False)

    @patch.object(custom, "_annotate_model_id_on_completion", return_value="annotated")
    @patch.object(custom, "sdk_no_wait", return_value="poller")
    def test_update_forwards_explicit_if_match_instead_of_fetched_etag(
            self, sdk_no_wait, _annotate):
        client = MagicMock()
        client.get.return_value = SimpleNamespace(
            e_tag='"fetched-etag"',
            properties=SimpleNamespace(
                model_resource_id="/models/model-a", vm_size="Standard_NC24ads_A100_v4",
                model_source_resource_id=None, performance_mode=None, scale=None,
                overrides=None))

        custom.update_modeldeployment(
            self.cmd, client, "rg", "manager", "namespace", "deployment",
            custom_headers='If-Match="caller-etag"')

        deployment = sdk_no_wait.call_args.args[-1]
        self.assertIsNone(deployment.properties.overrides)
        sdk_no_wait.assert_called_once_with(
            False, client.begin_create_or_update, "rg", "manager", "namespace",
            "deployment", deployment, headers={"If-Match": '"caller-etag"'})

    @patch.object(custom, "sdk_no_wait")
    def test_update_missing_deployment_raises_without_writing(self, sdk_no_wait):
        client = MagicMock()
        client.get.side_effect = ResourceNotFoundError(message="Not found")

        with self.assertRaises(ClientRequestError) as ctx:
            custom.update_modeldeployment(
                self.cmd, client, "rg", "manager", "namespace", "deployment")

        self.assertIn("Model deployment 'deployment' doesn't exist.", str(ctx.exception))
        self.assertIn("az aimanager namespace modeldeployment list", str(ctx.exception))
        sdk_no_wait.assert_not_called()
        client.begin_create_or_update.assert_not_called()

    @patch.object(custom, "_annotate_model_id_on_completion", return_value="poller")
    @patch.object(custom, "sdk_no_wait", return_value="poller")
    def test_create_and_update_forward_no_wait(self, sdk_no_wait, annotate):
        for operation in ("create", "update"):
            with self.subTest(operation=operation):
                sdk_no_wait.reset_mock()
                annotate.reset_mock()
                client = MagicMock()
                client.get.return_value = SimpleNamespace(properties=SimpleNamespace(
                    model_resource_id="/models/model-a", vm_size="Standard_NC24ads_A100_v4",
                    model_source_resource_id=None, performance_mode=None,
                    scale=models.ScalingProfile(manual=models.ManualScalingProfile(replicas=1)),
                    overrides=None))
                if operation == "create":
                    result = custom.create_modeldeployment(
                        self.cmd, client, "rg", "manager", "namespace", "deployment",
                        "/models/model-a", "Standard_NC24ads_A100_v4",
                        replicas=1, no_wait=True)
                else:
                    result = custom.update_modeldeployment(
                        self.cmd, client, "rg", "manager", "namespace", "deployment",
                        no_wait=True)

                self.assertEqual(result, "poller")
                deployment = sdk_no_wait.call_args.args[-1]
                sdk_no_wait.assert_called_once_with(
                    True, client.begin_create_or_update, "rg", "manager", "namespace",
                    "deployment", deployment, headers={})
                annotate.assert_called_once_with(self.cmd, "poller", True)

    @patch.object(custom, "_annotate_model_id_on_completion", return_value="annotated")
    @patch.object(custom, "sdk_no_wait", return_value="poller")
    def test_create_builds_payload_and_forwards_headers(self, sdk_no_wait, annotate):
        client = MagicMock()

        result = custom.create_modeldeployment(
            self.cmd, client, "rg", "manager", "namespace", "deployment",
            "/models/model-a", "Standard_NC24ads_A100_v4",
            model_source_resource_id="/sources/source-a", performance_mode="Latency",
            min_replicas=2, max_replicas=5, overrides=["engine=vllm", "setting=a=b"],
            custom_headers="x-custom=value")

        self.assertEqual(result, "annotated")
        deployment = sdk_no_wait.call_args.args[-1]
        self.assertIsInstance(deployment, models.ModelDeployment)
        properties = deployment.properties
        self.assertEqual(properties.model_resource_id, "/models/model-a")
        self.assertEqual(properties.model_source_resource_id, "/sources/source-a")
        self.assertEqual(properties.vm_size, "Standard_NC24ads_A100_v4")
        self.assertEqual(properties.performance_mode, "Latency")
        self.assertIsNone(properties.scale.manual)
        self.assertEqual(properties.scale.autoscale.min_replicas, 2)
        self.assertEqual(properties.scale.autoscale.max_replicas, 5)
        self.assertEqual(properties.overrides.values_property, {"engine": "vllm", "setting": "a=b"})
        sdk_no_wait.assert_called_once_with(
            False, client.begin_create_or_update, "rg", "manager", "namespace",
            "deployment", deployment, headers={"x-custom": "value"})
        annotate.assert_called_once_with(self.cmd, "poller", False)

    @patch.object(custom, "_annotate_model_id_on_completion", return_value="annotated")
    @patch.object(custom, "sdk_no_wait", return_value="poller")
    @patch.object(custom, "_construct_modeldeployment")
    def test_create_routes_result_through_model_id_annotation(
            self, _construct, _sdk_no_wait, annotate):
        result = custom.create_modeldeployment(
            self.cmd, MagicMock(), "rg", "manager", "namespace", "deployment",
            "/models/model-a", "Standard_NC24ads_A100_v4", replicas=1)

        self.assertEqual(result, "annotated")
        annotate.assert_called_once_with(self.cmd, "poller", False)

    @patch.object(custom, "_annotate_model_ids")
    @patch.object(custom, "LongRunningOperation")
    def test_annotate_model_id_on_completion_waits_and_annotates(self, lro, annotate):
        lro.return_value.return_value = "deployment"
        annotate.return_value = [{"name": "md1", "modelId": "meta-llama/Llama-3-8B"}]
        cmd = SimpleNamespace(cli_ctx=object())

        result = custom._annotate_model_id_on_completion(cmd, "poller", False)

        lro.return_value.assert_called_once_with("poller")
        annotate.assert_called_once_with(cmd, ["deployment"])
        self.assertEqual(result["modelId"], "meta-llama/Llama-3-8B")

    @patch.object(custom, "_annotate_model_ids")
    @patch.object(custom, "LongRunningOperation")
    def test_annotate_model_id_on_completion_no_wait_returns_poller(self, lro, annotate):
        result = custom._annotate_model_id_on_completion(SimpleNamespace(), "poller", True)

        self.assertEqual(result, "poller")
        lro.assert_not_called()
        annotate.assert_not_called()

    @patch("azext_aimanager._client_factory.cf_ai_models")
    def test_annotate_model_ids_returns_plain_dicts_with_model_id(self, cf_ai_models):
        # The AIModel GET resolves the human-readable modelId.
        model = models.AIModel({"properties": {"modelId": "meta-llama/Llama-3-8B"}})
        cf_ai_models.return_value.get.return_value = model

        deployment = models.ModelDeployment({
            "name": "md1",
            "properties": {
                "modelResourceId": (
                    "/subscriptions/s/providers/Microsoft.ContainerService"
                    "/locations/westus2/aiModels/llama3"
                ),
            },
        })
        cmd = SimpleNamespace(cli_ctx=object())

        results = custom._annotate_model_ids(cmd, [deployment])

        # Must be a plain dict (not the SDK model) so the injected modelId — which is not a
        # declared ModelDeployment field — survives azure-cli 2.76+ output conversion.
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], dict)
        self.assertEqual(results[0]["modelId"], "meta-llama/Llama-3-8B")
        # A single distinct model is fetched once.
        cf_ai_models.return_value.get.assert_called_once_with("westus2", "llama3")

    @patch("azext_aimanager._client_factory.cf_ai_models")
    def test_annotate_model_ids_memoizes_repeated_models(self, cf_ai_models):
        model = models.AIModel({"properties": {"modelId": "meta-llama/Llama-3-8B"}})
        cf_ai_models.return_value.get.return_value = model

        def make(name):
            return models.ModelDeployment({
                "name": name,
                "properties": {
                    "modelResourceId": (
                        "/subscriptions/s/providers/Microsoft.ContainerService"
                        "/locations/westus2/aiModels/llama3"
                    ),
                },
            })

        cmd = SimpleNamespace(cli_ctx=object())
        results = custom._annotate_model_ids(cmd, [make("md1"), make("md2")])

        self.assertEqual([r["modelId"] for r in results],
                         ["meta-llama/Llama-3-8B", "meta-llama/Llama-3-8B"])
        # Two deployments, same model -> one GET.
        cf_ai_models.return_value.get.assert_called_once()

    @patch("azext_aimanager._client_factory.cf_ai_models")
    def test_annotate_model_ids_blank_on_resolution_failure(self, cf_ai_models):
        cf_ai_models.return_value.get.side_effect = Exception("not found")

        deployment = models.ModelDeployment({
            "name": "md1",
            "properties": {
                "modelResourceId": (
                    "/subscriptions/s/providers/Microsoft.ContainerService"
                    "/locations/westus2/aiModels/llama3"
                ),
            },
        })
        cmd = SimpleNamespace(cli_ctx=object())

        results = custom._annotate_model_ids(cmd, [deployment])

        # No modelId injected; formatter will render a blank column.
        self.assertIsInstance(results[0], dict)
        self.assertNotIn("modelId", results[0])
        self.assertEqual(results, [todict(deployment)])

    @patch("azext_aimanager._client_factory.cf_ai_models")
    def test_annotate_model_ids_skips_missing_or_malformed_resource_ids(self, cf_ai_models):
        for properties in (
                None, {}, {"modelResourceId": ""},
                {"modelResourceId": "not-a-resource-id"},
                {"modelResourceId": "/subscriptions/s/resourceGroups/rg"}):
            with self.subTest(properties=properties):
                deployment = {"name": "md1", "properties": properties}
                results = custom._annotate_model_ids(
                    SimpleNamespace(cli_ctx=object()), [deployment])
                self.assertEqual(results, [deployment])
        cf_ai_models.assert_not_called()

    @patch("azext_aimanager._client_factory.cf_ai_models")
    def test_annotate_model_ids_leaves_deployment_unchanged_without_resolved_id(
            self, cf_ai_models):
        deployment = models.ModelDeployment({
            "name": "md1",
            "properties": {"modelResourceId": (
                "/subscriptions/s/providers/Microsoft.ContainerService"
                "/locations/westus2/aiModels/llama3")},
        })
        for properties in (None, {}, {"modelId": ""}):
            with self.subTest(properties=properties):
                cf_ai_models.return_value.get.return_value = {"properties": properties}
                results = custom._annotate_model_ids(
                    SimpleNamespace(cli_ctx=object()), [deployment])
                self.assertEqual(results, [todict(deployment)])

    @patch("azext_aimanager._client_factory.cf_ai_models")
    def test_annotate_model_ids_resolves_distinct_models(self, cf_ai_models):
        cf_ai_models.return_value.get.side_effect = [
            {"properties": {"modelId": "model-a"}},
            {"properties": {"modelId": "model-b"}},
            {"properties": {"modelId": "model-c"}},
        ]
        deployments = [
            {"name": name, "properties": {"modelResourceId": (
                "/subscriptions/s/providers/Microsoft.ContainerService"
                f"/locations/{location}/aiModels/{model}")}}
            for name, location, model in (
                ("md1", "westus2", "llama3"), ("md2", "eastus", "llama3"),
                ("md3", "westus2", "other"), ("md4", "westus2", "llama3"))
        ]
        cmd = SimpleNamespace(cli_ctx=object())

        results = custom._annotate_model_ids(cmd, deployments)

        self.assertEqual(
            [r["modelId"] for r in results], ["model-a", "model-b", "model-c", "model-a"])
        cf_ai_models.assert_called_once_with(cmd.cli_ctx)
        self.assertEqual(
            [call("westus2", "llama3"), call("eastus", "llama3"), call("westus2", "other")],
            cf_ai_models.return_value.get.call_args_list)

    @patch("azext_aimanager._client_factory.cf_ai_models")
    def test_annotate_model_ids_continues_after_one_lookup_fails(self, cf_ai_models):
        cf_ai_models.return_value.get.side_effect = [
            HttpResponseError(message="Lookup failed"),
            {"properties": {"modelId": "model-b"}},
        ]
        deployments = [
            {"name": name, "properties": {"modelResourceId": (
                "/subscriptions/s/providers/Microsoft.ContainerService"
                f"/locations/westus2/aiModels/{model}")}}
            for name, model in (("md1", "model-a"), ("md2", "model-b"))
        ]

        with self.assertLogs(custom.logger, level="DEBUG") as logs:
            results = custom._annotate_model_ids(
                SimpleNamespace(cli_ctx=object()), deployments)

        self.assertEqual(results[0], deployments[0])
        self.assertEqual(results[1], {**deployments[1], "modelId": "model-b"})
        self.assertTrue(any("Failed to resolve human-readable modelId" in line
                            for line in logs.output))
        self.assertEqual(
            [call("westus2", "model-a"), call("westus2", "model-b")],
            cf_ai_models.return_value.get.call_args_list)


if __name__ == '__main__':
    unittest.main()
