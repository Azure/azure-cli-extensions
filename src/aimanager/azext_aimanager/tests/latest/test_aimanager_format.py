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
    modelsource_table_format,
    modelsource_list_table_format,
    modeldeployment_table_format,
    modeldeployment_list_table_format,
    aimodel_table_format,
    aimodel_list_table_format,
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


class TestModelSourceTableFormat(unittest.TestCase):
    """Test cases for model source table output formatting."""

    def _sample(self):
        return {
            "id": (
                "/subscriptions/26fe00f8-0000-0000-0000-bb1d2e00343a"
                "/resourceGroups/yiralirg"
                "/providers/Microsoft.ContainerService/aiManagers/aimbyo"
                "/modelSources/hf1"
            ),
            "name": "hf1",
            "eTag": "ff459bfb-b983-436f-b55b-afe701d1c896",
            "properties": {
                "provisioningState": "Succeeded",
                "sourceType": "HuggingFace",
                "description": "gated models",
            },
        }

    def test_table_format_columns_modelsource(self):
        result = modelsource_table_format(self._sample())
        self.assertEqual(
            list(result.keys()),
            ["Name", "ProvisioningState", "SourceType", "Description"],
        )

    def test_table_format_values_modelsource(self):
        result = modelsource_table_format(self._sample())
        self.assertEqual(result["Name"], "hf1")
        self.assertEqual(result["ProvisioningState"], "Succeeded")
        self.assertEqual(result["SourceType"], "HuggingFace")
        self.assertEqual(result["Description"], "gated models")

    def test_table_format_null_properties_modelsource(self):
        result = modelsource_table_format({"name": "hf1", "properties": None})
        self.assertEqual(result["Name"], "hf1")
        self.assertEqual(result["ProvisioningState"], "")
        self.assertEqual(result["SourceType"], "")
        self.assertEqual(result["Description"], "")

    def test_table_format_null_description_modelsource(self):
        # A null description must still render as a (blank) column: knack drops None cells.
        sample = self._sample()
        sample["properties"]["description"] = None
        self.assertEqual(modelsource_table_format(sample)["Description"], "")

    def test_list_table_format_modelsource(self):
        results = modelsource_list_table_format([self._sample(), self._sample()])
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["Name"], "hf1")


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


class TestAIModelTableFormat(unittest.TestCase):
    """Test cases for AI model table output formatting."""

    def _sample(self):
        return {
            "id": (
                "/subscriptions/26fe00f8-0000-0000-0000-bb1d2e00343a"
                "/providers/Microsoft.ContainerService/locations/westus2"
                "/aiModels/9806f0c862fdd920"
            ),
            "name": "9806f0c862fdd920",
            "properties": {
                "modelId": "microsoft/Phi-4-mini-instruct",
                "description": "Phi-4 mini",
                "spec": {"parameterCount": "3.8B"},
            },
        }

    def test_table_format_columns_aimodel(self):
        result = aimodel_table_format(self._sample())
        self.assertEqual(list(result.keys()), ["Name", "ModelId", "Description"])

    def test_table_format_values_aimodel(self):
        result = aimodel_table_format(self._sample())
        self.assertEqual(result["Name"], "9806f0c862fdd920")
        self.assertEqual(result["ModelId"], "microsoft/Phi-4-mini-instruct")
        self.assertEqual(result["Description"], "Phi-4 mini")

    def test_table_format_null_properties_aimodel(self):
        result = aimodel_table_format({"name": "m1", "properties": None})
        self.assertEqual(result["Name"], "m1")
        self.assertEqual(result["ModelId"], "")
        self.assertEqual(result["Description"], "")

    def test_table_format_null_description_aimodel(self):
        # A null description must still render as a (blank) column: knack drops None cells.
        sample = self._sample()
        sample["properties"]["description"] = None
        self.assertEqual(aimodel_table_format(sample)["Description"], "")

    def test_list_table_format_aimodel(self):
        results = aimodel_list_table_format([self._sample(), self._sample()])
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["ModelId"], "microsoft/Phi-4-mini-instruct")


class TestCommandTableTransformers(unittest.TestCase):
    """Every create/update/show/list command must render "-o table" with a formatter, since
    azure-cli's default table drops nested fields such as properties.provisioningState."""

    def _load(self):
        from azext_aimanager.commands import load_command_table

        transformers = {}

        class Group:
            def __init__(self, name):
                self.name = name

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def _record(self, verb, *_, **kwargs):
                transformers["{} {}".format(self.name, verb)] = kwargs.get("table_transformer")

            custom_command = custom_show_command = _record

            def wait_command(self, *_, **__):
                pass

            custom_wait_command = wait_command

        class Loader:
            def command_group(self, name, *_, **__):
                return Group(name)

        load_command_table(Loader(), None)
        return transformers

    def test_create_update_show_list_have_table_transformers(self):
        transformers = self._load()
        expected = {
            "aimanager": (aimanager_table_format, aimanager_list_table_format),
            "aimanager namespace": (namespace_table_format, namespace_list_table_format),
            "aimanager modelsource": (modelsource_table_format, modelsource_list_table_format),
            "aimanager namespace modeldeployment": (
                modeldeployment_table_format, modeldeployment_list_table_format),
        }
        for group, (single, many) in expected.items():
            for verb in ("create", "update", "show"):
                self.assertIs(transformers["{} {}".format(group, verb)], single, (group, verb))
            self.assertIs(transformers["{} list".format(group)], many, group)

    def test_aimodel_commands_have_table_transformers(self):
        transformers = self._load()
        self.assertIs(transformers["aimanager model show"], aimodel_table_format)
        self.assertIs(transformers["aimanager model list"], aimodel_list_table_format)
        self.assertIs(transformers["aimanager model calculate-cost"], calculate_cost_table_format)

    def test_every_resource_command_has_callable_table_transformer(self):
        # Guards against a newly added create/update/show/list command shipping without a
        # formatter (or with a JMESPath string instead of a _format.py callable).
        transformers = self._load()
        for command, transformer in transformers.items():
            if command.rsplit(" ", 1)[1] in ("create", "update", "show", "list"):
                self.assertTrue(callable(transformer), command)


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
