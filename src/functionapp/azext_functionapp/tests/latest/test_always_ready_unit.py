# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import unittest
from unittest.mock import MagicMock, patch


def _build_functionapp_response(always_ready_entries):
    """Build a fake ARM API response for a Flex Consumption function app."""
    return {
        "id": "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Web/sites/app",
        "location": "eastus",
        "properties": {
            "serverFarmId": "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Web/serverfarms/plan",
            "sku": "FlexConsumption",
            "functionAppConfig": {
                "scaleAndConcurrency": {
                    "alwaysReady": always_ready_entries
                }
            }
        }
    }


class TestDeleteAlwaysReadySettings(unittest.TestCase):

    def _call_delete(self, always_ready_entries, setting_names_to_delete):
        """
        Call delete_always_ready_settings with mocked HTTP requests.

        Returns the alwaysReady list sent in the PUT body.
        """
        from azext_functionapp.custom import delete_always_ready_settings

        initial_app = _build_functionapp_response(always_ready_entries)
        put_body_captured = {}

        def fake_send_raw_request(cli_ctx, method, url, body=None):
            mock_resp = MagicMock()
            if method == "GET":
                mock_resp.json.return_value = initial_app
            else:  # PUT
                put_body_captured['body'] = json.loads(body)
                # Return updated app reflecting the PUT body
                mock_resp.json.return_value = put_body_captured['body']
            return mock_resp

        mock_cmd = MagicMock()
        mock_cmd.cli_ctx.cloud.endpoints.resource_manager = "https://management.azure.com/"

        with patch('azure.cli.core.util.send_raw_request', side_effect=fake_send_raw_request), \
             patch('azure.cli.core.commands.client_factory.get_subscription_id', return_value='sub'):
            delete_always_ready_settings(
                cmd=mock_cmd,
                resource_group_name='rg',
                name='app',
                setting_names=setting_names_to_delete
            )

        return (put_body_captured['body']
                .get('properties', {})
                .get('functionAppConfig', {})
                .get('scaleAndConcurrency', {})
                .get('alwaysReady', []))

    def test_delete_http_setting(self):
        """Deleting 'http' should remove only that entry."""
        entries = [
            {"name": "http", "instanceCount": 2},
            {"name": "function:Function1", "instanceCount": 1},
        ]
        result = self._call_delete(entries, ["http"])
        names = [x["name"] for x in result]
        self.assertNotIn("http", names)
        self.assertIn("function:Function1", names)

    def test_delete_function_setting_exact_case(self):
        """Deleting 'function:Function1' with exact case should remove the entry."""
        entries = [
            {"name": "http", "instanceCount": 2},
            {"name": "function:Function1", "instanceCount": 1},
        ]
        result = self._call_delete(entries, ["function:Function1"])
        names = [x["name"] for x in result]
        self.assertIn("http", names)
        self.assertNotIn("function:Function1", names)

    def test_delete_function_setting_case_insensitive(self):
        """Deletion should be case-insensitive to handle ARM API name normalization.

        Regression test for: when the ARM API normalizes function names to lowercase
        (e.g. stores 'function:function1' even though the user set 'function:Function1'),
        the delete command should still successfully match and remove the entry regardless
        of the casing used in --setting-names.
        """
        # Simulate ARM returning lowercase name even if user set mixed-case
        entries = [
            {"name": "http", "instanceCount": 2},
            {"name": "function:function1", "instanceCount": 1},  # lowercase from ARM
        ]
        # User passes the original mixed-case name
        result = self._call_delete(entries, ["function:Function1"])
        names = [x["name"] for x in result]
        self.assertIn("http", names)
        self.assertNotIn("function:function1", names)

    def test_delete_all_settings(self):
        """Deleting all setting names should result in an empty alwaysReady list."""
        entries = [
            {"name": "http", "instanceCount": 2},
            {"name": "function:Function1", "instanceCount": 1},
        ]
        result = self._call_delete(entries, ["http", "function:Function1"])
        self.assertEqual(result, [])

    def test_delete_nonexistent_setting(self):
        """Deleting a setting that doesn't exist should leave the list unchanged."""
        entries = [
            {"name": "http", "instanceCount": 2},
        ]
        result = self._call_delete(entries, ["nonexistent"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "http")

    def test_delete_from_empty_list(self):
        """Deleting from an empty alwaysReady list should not raise an error."""
        result = self._call_delete([], ["http"])
        self.assertEqual(result, [])

    def test_delete_multiple_settings(self):
        """Deleting multiple settings at once should remove all specified entries."""
        entries = [
            {"name": "http", "instanceCount": 2},
            {"name": "function:Function1", "instanceCount": 1},
            {"name": "function:Function2", "instanceCount": 3},
        ]
        result = self._call_delete(entries, ["function:Function1", "function:Function2"])
        names = [x["name"] for x in result]
        self.assertEqual(names, ["http"])


if __name__ == '__main__':
    unittest.main()
