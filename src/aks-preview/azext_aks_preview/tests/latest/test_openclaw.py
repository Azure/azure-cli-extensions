# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import unittest
from unittest.mock import MagicMock, patch

from knack.util import CLIError

from azext_aks_preview.openclaw._consts import (
    CONST_OPENCLAW_DEFAULT_MODEL,
    CONST_OPENCLAW_DEFAULT_NAMESPACE,
    CONST_OPENCLAW_STORAGE_CLASS_NAME,
)
from azext_aks_preview.openclaw._helpers import (
    generate_deployment_name,
    generate_foundry_name,
    generate_helm_values,
)
from azext_aks_preview.openclaw.deploy import (
    _resolve_byo_endpoint,
    resolve_or_provision_ai_foundry,
)


class TestGenerateFoundryName(unittest.TestCase):
    def test_basic_name(self):
        name = generate_foundry_name("mycluster")
        self.assertTrue(name.startswith("openclaw-mycluster-"))
        self.assertLessEqual(len(name), 64)

    def test_long_cluster_name(self):
        name = generate_foundry_name("a" * 100)
        self.assertLessEqual(len(name), 64)
        self.assertFalse(name.endswith("-"))

    def test_deterministic(self):
        name1 = generate_foundry_name("test")
        name2 = generate_foundry_name("test")
        self.assertEqual(name1, name2)

    def test_different_clusters_different_names(self):
        name1 = generate_foundry_name("cluster1")
        name2 = generate_foundry_name("cluster2")
        self.assertNotEqual(name1, name2)


class TestGenerateDeploymentName(unittest.TestCase):
    def test_removes_dots_and_hyphens(self):
        self.assertEqual(generate_deployment_name("gpt-5.1-chat"), "gpt51chat")

    def test_plain_name(self):
        self.assertEqual(generate_deployment_name("gpt4o"), "gpt4o")


class TestGenerateHelmValues(unittest.TestCase):
    def test_basic_values(self):
        values, master_key = generate_helm_values(
            endpoint="https://eastus.api.cognitive.microsoft.com/openai/deployments/gpt51chat",
            api_key="test-key",
            deployment_name="gpt51chat",
            model_name="gpt-5.1-chat",
            gateway_token="fixed-token",
        )

        self.assertTrue(len(master_key) > 0)
        self.assertEqual(values["secrets"]["openclawGatewayToken"], "fixed-token")
        self.assertEqual(values["litellm"]["model"], "gpt-5.1-chat")
        self.assertEqual(
            values["persistence"]["storageClass"],
            CONST_OPENCLAW_STORAGE_CLASS_NAME,
        )

        # configOverride is a YAML string
        config_override = values["litellm"]["configOverride"]
        self.assertIsInstance(config_override, str)
        self.assertIn("azure/gpt51chat", config_override)
        self.assertIn("gpt-5.1-chat", config_override)

        env_vars = values["litellm"]["extraEnv"]
        api_key_env = next(e for e in env_vars if e["name"] == "AZURE_API_KEY")
        self.assertEqual(api_key_env["value"], "test-key")

    def test_generates_token_if_not_provided(self):
        values, _ = generate_helm_values(
            endpoint="https://test.com",
            api_key="key",
            deployment_name="dep",
            model_name="model",
        )
        self.assertTrue(len(values["secrets"]["openclawGatewayToken"]) > 0)


class TestResolveBYOEndpoint(unittest.TestCase):
    def test_requires_deployment_name(self):
        with self.assertRaises(CLIError):
            _resolve_byo_endpoint("https://test.com", "key", None)

    def test_appends_deployment_path(self):
        endpoint, key, dep = _resolve_byo_endpoint(
            "https://eastus.api.cognitive.microsoft.com",
            "mykey",
            "gpt51chat",
        )
        self.assertIn("/openai/deployments/gpt51chat", endpoint)
        self.assertEqual(key, "mykey")
        self.assertEqual(dep, "gpt51chat")

    def test_preserves_existing_deployment_path(self):
        endpoint, _, _ = _resolve_byo_endpoint(
            "https://eastus.api.cognitive.microsoft.com/openai/deployments/existing",
            "mykey",
            "gpt51chat",
        )
        self.assertIn("/openai/deployments/existing", endpoint)
        self.assertNotIn("gpt51chat", endpoint)


class TestResolveOrProvisionMutualExclusivity(unittest.TestCase):
    def test_rejects_both_byo_flags(self):
        cmd = MagicMock()
        with self.assertRaises(CLIError) as ctx:
            resolve_or_provision_ai_foundry(
                cmd,
                resource_group_name="rg",
                ai_foundry_resource_id="/subscriptions/sub/resourceGroups/rg/providers/Microsoft.CognitiveServices/accounts/acc",
                ai_foundry_endpoint="https://test.com",
                ai_foundry_api_key="key",
            )
        self.assertIn("Only one of", str(ctx.exception))

    def test_endpoint_requires_api_key(self):
        cmd = MagicMock()
        with self.assertRaises(CLIError) as ctx:
            resolve_or_provision_ai_foundry(
                cmd,
                resource_group_name="rg",
                ai_foundry_endpoint="https://test.com",
            )
        self.assertIn("--ai-foundry-api-key is required", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
