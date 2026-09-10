# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from azext_aimanager._format import (
    aimanager_table_format,
    aimanager_list_table_format,
    namespace_table_format,
    namespace_list_table_format,
    modeldeployment_table_format,
    modeldeployment_list_table_format,
)


class TestAIManagerTableFormat(unittest.TestCase):
    """Test cases for AI Manager table output formatting."""

    def _sample(self):
        return {
            "id": (
                "/subscriptions/26fe00f8-0000-0000-0000-bb1d2e00343a"
                "/resourceGroups/yiralirg"
                "/providers/Microsoft.ContainerService/aiManagers/aimbyo"
            ),
            "name": "aimbyo",
            "location": "westus2",
            "eTag": "b918e441-390c-4b01-a922-dea9b42a03df",
            "properties": {"provisioningState": "Succeeded"},
        }

    def test_table_format_columns(self):
        result = aimanager_table_format(self._sample())
        self.assertEqual(
            list(result.keys()),
            ["Name", "ProvisioningState", "ResourceGroup", "Location"],
        )
        self.assertNotIn("ETag", result)

    def test_table_format_values(self):
        result = aimanager_table_format(self._sample())
        self.assertEqual(result["Name"], "aimbyo")
        self.assertEqual(result["ResourceGroup"], "yiralirg")
        self.assertEqual(result["Location"], "westus2")
        self.assertEqual(result["ProvisioningState"], "Succeeded")

    def test_table_format_missing_fields(self):
        result = aimanager_table_format({})
        self.assertEqual(result["Name"], "")
        self.assertEqual(result["ResourceGroup"], "")
        self.assertEqual(result["ProvisioningState"], "")

    def test_table_format_null_properties(self):
        # 'properties' present but null (Optional in the vendored model) must not raise.
        result = aimanager_table_format({"name": "aimbyo", "properties": None})
        self.assertEqual(result["Name"], "aimbyo")
        self.assertEqual(result["ProvisioningState"], "")

    def test_list_table_format(self):
        results = aimanager_list_table_format([self._sample(), self._sample()])
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["Name"], "aimbyo")


class TestNamespaceTableFormat(unittest.TestCase):
    """Test cases for AI Manager namespace table output formatting."""

    def _sample(self):
        return {
            "id": (
                "/subscriptions/26fe00f8-0000-0000-0000-bb1d2e00343a"
                "/resourceGroups/yiralirg"
                "/providers/Microsoft.ContainerService/aiManagers/aimbyo"
                "/namespaces/ns1"
            ),
            "name": "ns1",
            "systemData": {"createdAt": "2020-01-01T00:00:00+00:00"},
            "properties": {
                "provisioningState": "Succeeded",
                "labels": {"team": "payments", "env": "prod"},
            },
        }

    def test_table_format_columns(self):
        result = namespace_table_format(self._sample())
        self.assertEqual(
            list(result.keys()),
            ["Name", "ProvisioningState", "Age", "Labels"],
        )
        self.assertNotIn("ETag", result)

    def test_table_format_values(self):
        result = namespace_table_format(self._sample())
        self.assertEqual(result["Name"], "ns1")
        self.assertEqual(result["ProvisioningState"], "Succeeded")
        self.assertEqual(result["Labels"], "env=prod,team=payments")
        # Age is derived from a fixed 2020 timestamp, so it should be reported in days.
        self.assertIn("d", result["Age"])

    def test_table_format_missing_fields(self):
        result = namespace_table_format({})
        self.assertEqual(result["Name"], "")
        self.assertEqual(result["ProvisioningState"], "")
        self.assertEqual(result["Age"], "")
        self.assertEqual(result["Labels"], "")

    def test_table_format_null_properties(self):
        result = namespace_table_format({"name": "ns1", "properties": None})
        self.assertEqual(result["Name"], "ns1")
        self.assertEqual(result["ProvisioningState"], "")
        self.assertEqual(result["Age"], "")
        self.assertEqual(result["Labels"], "")

    def test_list_table_format(self):
        results = namespace_list_table_format([self._sample(), self._sample()])
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["Name"], "ns1")


class TestModelDeploymentTableFormat(unittest.TestCase):
    """Test cases for model deployment table output formatting."""

    def _sample(self):
        return {
            "id": (
                "/subscriptions/26fe00f8-0000-0000-0000-bb1d2e00343a"
                "/resourceGroups/yiralirg"
                "/providers/Microsoft.ContainerService/aiManagers/aimbyo"
                "/namespaces/ns1/modelDeployments/md1"
            ),
            "name": "md1",
            "modelId": "meta-llama/Llama-3-8B",
            "properties": {
                "provisioningState": "Succeeded",
                "modelResourceId": (
                    "/subscriptions/26fe00f8-0000-0000-0000-bb1d2e00343a"
                    "/providers/Microsoft.ContainerService/locations/westus2"
                    "/aiModels/llama3"
                ),
                "status": {
                    "endpoint": "https://md1.example.com",
                    "currentReplicas": 1,
                    "desiredReplicas": 3,
                },
            },
        }

    def test_table_format_columns(self):
        result = modeldeployment_table_format(self._sample())
        self.assertEqual(
            list(result.keys()),
            ["Name", "ProvisioningState", "ModelId", "Replicas",
             "Endpoint", "Namespace"],
        )

    def test_table_format_values(self):
        result = modeldeployment_table_format(self._sample())
        self.assertEqual(result["Name"], "md1")
        self.assertEqual(result["ProvisioningState"], "Succeeded")
        self.assertEqual(result["ModelId"], "meta-llama/Llama-3-8B")
        self.assertEqual(result["Replicas"], "1/3")
        self.assertEqual(result["Endpoint"], "https://md1.example.com")
        self.assertEqual(result["Namespace"], "ns1")

    def test_model_id_fallback_to_resource_name(self):
        sample = self._sample()
        del sample["modelId"]
        result = modeldeployment_table_format(sample)
        self.assertEqual(result["ModelId"], "llama3")

    def test_replicas_missing_status(self):
        result = modeldeployment_table_format({"name": "md1", "properties": None})
        self.assertEqual(result["Replicas"], "-/-")
        self.assertEqual(result["Endpoint"], "")
        self.assertEqual(result["ModelId"], "")

    def test_list_table_format(self):
        results = modeldeployment_list_table_format([self._sample(), self._sample()])
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["ModelId"], "meta-llama/Llama-3-8B")


if __name__ == "__main__":
    unittest.main()
