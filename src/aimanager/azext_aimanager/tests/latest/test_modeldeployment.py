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

    def test_list_scope_requires_namespace_or_all_namespaces(self):
        from azext_aimanager._validators import validate_modeldeployment_list_scope
        with self.assertRaises(InvalidArgumentValueError):
            validate_modeldeployment_list_scope(
                SimpleNamespace(namespace_name=None, all_namespaces=False))

    def test_list_scope_rejects_both_namespace_and_all_namespaces(self):
        from azext_aimanager._validators import validate_modeldeployment_list_scope
        with self.assertRaises(InvalidArgumentValueError):
            validate_modeldeployment_list_scope(
                SimpleNamespace(namespace_name="ns1", all_namespaces=True))

    def test_list_scope_accepts_single_namespace(self):
        from azext_aimanager._validators import validate_modeldeployment_list_scope
        validate_modeldeployment_list_scope(
            SimpleNamespace(namespace_name="ns1", all_namespaces=False))

    def test_list_scope_accepts_all_namespaces(self):
        from azext_aimanager._validators import validate_modeldeployment_list_scope
        validate_modeldeployment_list_scope(
            SimpleNamespace(namespace_name=None, all_namespaces=True))

    @patch.object(custom, "_annotate_model_ids", side_effect=lambda _cmd, d: d)
    @patch("azext_aimanager._client_factory.cf_ai_manager_namespaces")
    def test_list_all_namespaces_aggregates_across_namespaces(
            self, cf_namespaces, _annotate):
        namespaces_client = MagicMock()
        namespaces_client.list_by_ai_manager.return_value = [
            SimpleNamespace(name="ns1"), SimpleNamespace(name="ns2")]
        cf_namespaces.return_value = namespaces_client
        self.cmd.cli_ctx = MagicMock()

        client = MagicMock()
        client.list_by_ai_manager_namespace.side_effect = [["d1"], ["d2", "d3"]]

        result = custom.list_modeldeployment(
            self.cmd, client, "rg", "mgr", all_namespaces=True)

        self.assertEqual(["d1", "d2", "d3"], result)
        namespaces_client.list_by_ai_manager.assert_called_once_with("rg", "mgr")
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
