# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.core import MatchConditions

from azext_aimanager import custom
from azext_aimanager._params import load_arguments
from azext_aimanager.vendored_sdks.v2026_05_02_preview import models


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
        self.assertEqual(2, client.list_by_ai_manager_namespace.call_count)

    @patch.object(custom, "_annotate_model_ids", side_effect=lambda _cmd, d: d)
    @patch("azext_aimanager._client_factory.cf_ai_manager_namespaces")
    def test_list_without_namespace_skips_forbidden_namespaces(
            self, cf_namespaces, _annotate):
        from azure.core.exceptions import HttpResponseError

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
        from azure.core.exceptions import HttpResponseError

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
        from azure.core.exceptions import HttpResponseError
        from azure.cli.core.azclierror import UnauthorizedError

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
        from azure.core.exceptions import HttpResponseError
        from azure.cli.core.azclierror import UnauthorizedError

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

    @patch.object(custom, "sdk_no_wait")
    @patch.object(custom, "_construct_modeldeployment")
    def test_update_preserves_omitted_properties_and_uses_etag(
            self, construct_modeldeployment, sdk_no_wait):
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
            etag='"etag-value"',
            match_condition=MatchConditions.IfNotModified,
        )

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


if __name__ == '__main__':
    unittest.main()
