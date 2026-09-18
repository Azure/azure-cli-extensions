# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest
from unittest.mock import MagicMock, patch, call

from azure.core.exceptions import HttpResponseError


class TestDatafactoryTriggerStartRetry(unittest.TestCase):
    """Unit tests for the datafactory_trigger_start retry logic."""

    def _get_provisioning_error(self):
        """Create an HttpResponseError that resembles the provisioning error."""
        error = HttpResponseError()
        error.error = MagicMock()
        error.error.message = "Resource cannot be updated during provisioning"
        return error

    def _get_other_error(self):
        """Create an HttpResponseError for a non-provisioning error."""
        error = HttpResponseError()
        error.error = MagicMock()
        error.error.message = "Some other error"
        return error

    def _load_datafactory_trigger_start(self):
        """Load datafactory_trigger_start from manual/custom.py."""
        import ast
        import os

        custom_py = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "custom.py",
        )
        with open(custom_py, "r") as f:
            source = f.read()
        # Parse and find the datafactory_trigger_start function
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "datafactory_trigger_start":
                func_source = ast.get_source_segment(source, node)
                return func_source
        return None

    def test_start_succeeds_on_first_attempt(self):
        """When start succeeds immediately, it should return without retrying."""
        from azext_datafactory.manual.custom import datafactory_trigger_start

        mock_client = MagicMock()
        mock_client.begin_start.return_value = MagicMock()

        with patch("azext_datafactory.manual.custom.sdk_no_wait") as mock_sdk_no_wait:
            mock_sdk_no_wait.return_value = "poller"
            result = datafactory_trigger_start(
                mock_client, "rg", "factory", "trigger"
            )

        self.assertEqual(result, "poller")
        mock_sdk_no_wait.assert_called_once_with(
            False,
            mock_client.begin_start,
            resource_group_name="rg",
            factory_name="factory",
            trigger_name="trigger",
        )

    def test_start_retries_on_provisioning_error(self):
        """When start fails with a provisioning error, it should retry."""
        from azext_datafactory.manual.custom import (
            datafactory_trigger_start,
            _TRIGGER_START_RETRY_DELAY,
        )

        provisioning_error = self._get_provisioning_error()

        with patch("azext_datafactory.manual.custom.sdk_no_wait") as mock_sdk_no_wait, \
             patch("azext_datafactory.manual.custom.time.sleep") as mock_sleep:
            # Fail twice with provisioning error, then succeed
            mock_sdk_no_wait.side_effect = [
                provisioning_error,
                provisioning_error,
                "poller",
            ]

            result = datafactory_trigger_start(
                MagicMock(), "rg", "factory", "trigger"
            )

        self.assertEqual(result, "poller")
        self.assertEqual(mock_sdk_no_wait.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_called_with(_TRIGGER_START_RETRY_DELAY)

    def test_start_raises_cli_error_after_max_retries(self):
        """When provisioning error persists after max retries, raises CLIError."""
        from azext_datafactory.manual.custom import (
            datafactory_trigger_start,
            _TRIGGER_START_MAX_RETRIES,
        )
        from knack.util import CLIError

        provisioning_error = self._get_provisioning_error()

        with patch("azext_datafactory.manual.custom.sdk_no_wait") as mock_sdk_no_wait, \
             patch("azext_datafactory.manual.custom.time.sleep"):
            # Always fail with provisioning error
            mock_sdk_no_wait.side_effect = provisioning_error

            with self.assertRaises(CLIError) as ctx:
                datafactory_trigger_start(
                    MagicMock(), "rg", "factory", "my-trigger"
                )

        self.assertIn("my-trigger", str(ctx.exception))
        self.assertIn("provisioned", str(ctx.exception).lower())
        # Should have tried _TRIGGER_START_MAX_RETRIES + 1 times total
        self.assertEqual(mock_sdk_no_wait.call_count, _TRIGGER_START_MAX_RETRIES + 1)

    def test_start_raises_original_error_for_non_provisioning_errors(self):
        """Non-provisioning errors are re-raised immediately without retry."""
        from azext_datafactory.manual.custom import datafactory_trigger_start

        other_error = self._get_other_error()

        with patch("azext_datafactory.manual.custom.sdk_no_wait") as mock_sdk_no_wait, \
             patch("azext_datafactory.manual.custom.time.sleep") as mock_sleep:
            mock_sdk_no_wait.side_effect = other_error

            with self.assertRaises(HttpResponseError):
                datafactory_trigger_start(
                    MagicMock(), "rg", "factory", "trigger"
                )

        # Should have been called exactly once (no retries)
        mock_sdk_no_wait.assert_called_once()
        mock_sleep.assert_not_called()

    def test_start_with_no_wait_flag(self):
        """The no_wait flag is passed through to sdk_no_wait."""
        from azext_datafactory.manual.custom import datafactory_trigger_start

        mock_client = MagicMock()

        with patch("azext_datafactory.manual.custom.sdk_no_wait") as mock_sdk_no_wait:
            mock_sdk_no_wait.return_value = "poller"
            datafactory_trigger_start(
                mock_client, "rg", "factory", "trigger", no_wait=True
            )

        mock_sdk_no_wait.assert_called_once_with(
            True,
            mock_client.begin_start,
            resource_group_name="rg",
            factory_name="factory",
            trigger_name="trigger",
        )


if __name__ == "__main__":
    unittest.main()
