# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from azext_aimanager._format import (
    aimanager_table_format,
    aimanager_list_table_format,
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


if __name__ == "__main__":
    unittest.main()
