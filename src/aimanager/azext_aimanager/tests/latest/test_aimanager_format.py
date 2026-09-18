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
    calculate_cost_table_format,
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
            "properties": {"provisioningState": "Succeeded"},
        }

    def test_table_format_columns(self):
        result = aimanager_table_format(self._sample())
        self.assertEqual(
            list(result.keys()),
            ["Name", "ProvisioningState", "ResourceGroup", "Location"],
        )

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

    def test_table_format_columns_namespace(self):
        result = namespace_table_format(self._sample())
        self.assertEqual(
            list(result.keys()),
            ["Name", "ProvisioningState", "Age", "Labels"],
        )

    def test_table_format_values_namespace(self):
        result = namespace_table_format(self._sample())
        self.assertEqual(result["Name"], "ns1")
        self.assertEqual(result["ProvisioningState"], "Succeeded")
        self.assertEqual(result["Labels"], "env=prod,team=payments")
        # Age is derived from a fixed 2020 timestamp, so it should be reported in days.
        self.assertIn("d", result["Age"])

    def test_table_format_missing_fields_namespace(self):
        result = namespace_table_format({})
        self.assertEqual(result["Name"], "")
        self.assertEqual(result["ProvisioningState"], "")
        self.assertEqual(result["Age"], "")
        self.assertEqual(result["Labels"], "")

    def test_table_format_null_properties_namespace(self):
        result = namespace_table_format({"name": "ns1", "properties": None})
        self.assertEqual(result["Name"], "ns1")
        self.assertEqual(result["ProvisioningState"], "")
        self.assertEqual(result["Age"], "")
        self.assertEqual(result["Labels"], "")

    def test_list_table_format_namespace(self):
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
            "systemData": {"createdAt": "2020-01-01T00:00:00+00:00"},
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

    def test_table_format_columns_modeldeployment(self):
        result = modeldeployment_table_format(self._sample())
        self.assertEqual(
            list(result.keys()),
            ["Namespace", "Name", "ProvisioningState", "Replicas",
             "Age", "ModelId", "Endpoint"],
        )

    def test_table_format_values_modeldeployment(self):
        result = modeldeployment_table_format(self._sample())
        self.assertEqual(result["Namespace"], "ns1")
        self.assertEqual(result["Name"], "md1")
        self.assertEqual(result["ProvisioningState"], "Succeeded")
        self.assertEqual(result["Replicas"], "1/3")
        self.assertIn("d", result["Age"])
        self.assertEqual(result["ModelId"], "meta-llama/Llama-3-8B")
        self.assertEqual(result["Endpoint"], "https://md1.example.com")

    def test_model_id_blank_when_unresolved(self):
        # When the human-readable modelId was not injected, the column is blank rather than
        # falling back to the (unreadable) AIModel resource name.
        sample = self._sample()
        del sample["modelId"]
        result = modeldeployment_table_format(sample)
        self.assertEqual(result["ModelId"], "")

    def test_replicas_missing_status(self):
        result = modeldeployment_table_format({"name": "md1", "properties": None})
        self.assertEqual(result["Replicas"], "-/-")
        self.assertEqual(result["Endpoint"], "")
        self.assertEqual(result["ModelId"], "")
        self.assertEqual(result["Age"], "")

    def test_list_table_format_modeldeployment(self):
        results = modeldeployment_list_table_format([self._sample(), self._sample()])
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["ModelId"], "meta-llama/Llama-3-8B")


class TestCalculateCostTableFormat(unittest.TestCase):
    """Test cases for 'az aimanager model calculate-cost' table output formatting."""

    def _feasible_plan(self):
        return {
            "vmSize": "Standard_NC24ads_A100_v4",
            "feasible": True,
            "vmsPerReplica": 1,
            "vmHourlyPrice": 3.673,
            "totalHourlyPrice": 3.673,
            "maxAvailableReplicas": 9,
            "quantization": "fp16",
        }

    def _infeasible_plan(self):
        # The service omits 'feasible', 'totalHourlyPrice' and 'maxAvailableReplicas'
        # for infeasible plans, and adds an infeasibilityReason.
        return {
            "vmSize": "Standard_NC4as_T4_v3",
            "vmsPerReplica": 2,
            "vmHourlyPrice": 0.526,
            "infeasibilityReason": {"code": "InfeasibleCode_InsufficientQuota", "message": "no quota"},
        }

    def test_columns(self):
        rows = calculate_cost_table_format({"plans": [self._feasible_plan()]})
        self.assertEqual(
            list(rows[0].keys()),
            ["VmSize", "Feasible", "VmsPerReplica", "VmHourlyPrice",
             "TotalHourlyPrice", "MaxAvailableReplicas", "Quantization",
             "InfeasibilityReason"],
        )

    def test_feasible_row_values(self):
        rows = calculate_cost_table_format({"plans": [self._feasible_plan()]})
        row = rows[0]
        self.assertIs(row["Feasible"], True)
        self.assertEqual(row["TotalHourlyPrice"], 3.673)
        self.assertEqual(row["InfeasibilityReason"], "")

    def test_infeasible_row_always_shows_feasible_false(self):
        # Regression: even when 'feasible' is absent, the column must be populated as False.
        rows = calculate_cost_table_format({"plans": [self._infeasible_plan()]})
        row = rows[0]
        self.assertIs(row["Feasible"], False)
        self.assertEqual(row["TotalHourlyPrice"], "")
        self.assertEqual(row["MaxAvailableReplicas"], "")
        self.assertEqual(row["InfeasibilityReason"], "InsufficientQuota")

    def test_infeasibility_reason_without_prefix_passthrough(self):
        # Codes not carrying the "InfeasibleCode_" prefix are surfaced unchanged.
        plan = {"vmSize": "sku", "infeasibilityReason": {"code": "RegionUnavailable"}}
        rows = calculate_cost_table_format({"plans": [plan]})
        self.assertEqual(rows[0]["InfeasibilityReason"], "RegionUnavailable")

    def test_all_infeasible_keeps_feasible_column(self):
        rows = calculate_cost_table_format(
            {"plans": [self._infeasible_plan(), self._infeasible_plan()]}
        )
        self.assertEqual(len(rows), 2)
        self.assertTrue(all("Feasible" in r and r["Feasible"] is False for r in rows))

    def test_empty_or_missing_plans(self):
        self.assertEqual(calculate_cost_table_format({}), [])
        self.assertEqual(calculate_cost_table_format({"plans": None}), [])

    def test_feasible_string_values_coerced_strictly(self):
        # Defensive: if 'feasible' ever arrives as a JSON string, "false" must become False
        # (bool("false") is True in Python), and "true" must become True.
        false_row = calculate_cost_table_format(
            {"plans": [{"vmSize": "s", "feasible": "false"}]}
        )[0]
        true_row = calculate_cost_table_format(
            {"plans": [{"vmSize": "s", "feasible": "true"}]}
        )[0]
        self.assertIs(false_row["Feasible"], False)
        self.assertIs(true_row["Feasible"], True)


if __name__ == "__main__":
    unittest.main()
