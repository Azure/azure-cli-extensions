# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Unit tests for target prepare command."""

import unittest
from unittest.mock import patch, MagicMock

from azure.cli.core.azclierror import CLIInternalError, ValidationError


class TestTargetPreparePreFlight(unittest.TestCase):
    """Test pre-flight checks for target prepare."""

    def _get_mock_cmd(self):
        cmd = MagicMock()
        cmd.cli_ctx = MagicMock()
        return cmd

    @patch('azext_workload_orchestration.onboarding.target_prepare.invoke_cli_command')
    def test_cluster_not_arc_connected_raises_error(self, mock_invoke):
        from azext_workload_orchestration.onboarding.target_prepare import _preflight_checks
        cmd = self._get_mock_cmd()

        mock_invoke.side_effect = CLIInternalError("Not found")

        with self.assertRaises(ValidationError) as ctx:
            _preflight_checks(cmd, 'my-cluster', 'my-rg')

        self.assertIn('not Arc-connected', str(ctx.exception))

    @patch('azext_workload_orchestration.onboarding.target_prepare.invoke_cli_command')
    def test_arc_connected_returns_cluster_id(self, mock_invoke):
        from azext_workload_orchestration.onboarding.target_prepare import _preflight_checks
        cmd = self._get_mock_cmd()

        mock_invoke.return_value = {
            "id": "/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.Kubernetes/connectedClusters/my-cluster",
            "name": "my-cluster",
        }

        result = _preflight_checks(cmd, 'my-cluster', 'my-rg')
        self.assertIn('connectedClusters/my-cluster', result)


class TestTargetPrepareCertManager(unittest.TestCase):
    """Test cert-manager + trust-manager AIO extension install."""

    def test_aio_extension_function_exists(self):
        """Verify _ensure_cert_trust_manager_via_aio_extension is importable."""
        from azext_workload_orchestration.onboarding.target_prepare import (
            _ensure_cert_trust_manager_via_aio_extension,
        )
        self.assertTrue(callable(_ensure_cert_trust_manager_via_aio_extension))


class TestTargetPrepareExtension(unittest.TestCase):
    """Test WO extension detection and install."""

    def _get_mock_cmd(self):
        cmd = MagicMock()
        cmd.cli_ctx = MagicMock()
        return cmd

    @patch('azext_workload_orchestration.onboarding.target_prepare.invoke_cli_command')
    @patch('azext_workload_orchestration.onboarding.target_prepare._detect_storage_class',
           return_value='default')
    def test_extension_already_installed_succeeds_skips(self, _, mock_invoke):
        from azext_workload_orchestration.onboarding.target_prepare import _ensure_wo_extension
        cmd = self._get_mock_cmd()

        mock_invoke.return_value = [
            {
                "extensionType": "microsoft.workloadorchestration",
                "id": "/sub/rg/ext/wo-ext",
                "version": "2.1.11",
                "provisioningState": "Succeeded",
            }
        ]

        result = _ensure_wo_extension(
            cmd, 'cluster1', 'rg1', 'wo-ext', None, 'preview', False
        )

        self.assertEqual(result, '/sub/rg/ext/wo-ext')
        # Only list was called, not create
        mock_invoke.assert_called_once()

    @patch('azext_workload_orchestration.onboarding.target_prepare.invoke_cli_command')
    @patch('azext_workload_orchestration.onboarding.target_prepare._detect_storage_class',
           return_value='default')
    def test_failed_extension_gets_deleted_and_reinstalled(self, _, mock_invoke):
        from azext_workload_orchestration.onboarding.target_prepare import _ensure_wo_extension
        cmd = self._get_mock_cmd()

        call_count = [0]
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call: list returns failed extension
                return [{
                    "extensionType": "microsoft.workloadorchestration",
                    "id": "/sub/rg/ext/wo-ext",
                    "name": "wo-ext",
                    "version": "2.1.11",
                    "provisioningState": "Failed",
                }]
            elif call_count[0] == 2:
                # Second call: delete
                return None
            else:
                # Third call: create
                return {"id": "/sub/rg/ext/wo-ext-new"}

        mock_invoke.side_effect = side_effect

        result = _ensure_wo_extension(
            cmd, 'cluster1', 'rg1', 'wo-ext', None, 'preview', False
        )

        # Should have called: list, delete, create
        self.assertEqual(mock_invoke.call_count, 3)


class TestTargetPrepareStorageClass(unittest.TestCase):
    """Test storage class auto-detection."""

    def test_detect_returns_none_without_cluster(self):
        """Without a real cluster, should return None gracefully."""
        from azext_workload_orchestration.onboarding.target_prepare import _detect_storage_class
        result = _detect_storage_class("/nonexistent/kubeconfig", "bad-context")
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
