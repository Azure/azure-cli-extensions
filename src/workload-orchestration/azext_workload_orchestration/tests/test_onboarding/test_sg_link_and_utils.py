# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Unit tests for service group link helper."""

import json
import unittest
from unittest.mock import patch, MagicMock, call

from azure.cli.core.azclierror import CLIInternalError


class TestServiceGroupLink(unittest.TestCase):
    """Test target-to-service-group linking."""

    def _get_mock_cmd(self):
        cmd = MagicMock()
        cmd.cli_ctx = MagicMock()
        return cmd

    @patch('azext_workload_orchestration.onboarding.target_sg_link.invoke_cli_command')
    def test_link_creates_member_and_refreshes_target(self, mock_invoke):
        from azext_workload_orchestration.onboarding.target_sg_link import (
            link_target_to_service_group
        )
        cmd = self._get_mock_cmd()

        # GET target returns existing data
        mock_invoke.side_effect = [
            None,  # SGMember PUT
            {  # GET target
                "location": "eastus",
                "properties": {"displayName": "t1"},
                "extendedLocation": {"name": "cl1", "type": "CustomLocation"},
            },
            None,  # PUT target (refresh)
        ]

        link_target_to_service_group(cmd, '/sub/rg/targets/t1', 'my-factory')

        # Should have 3 calls: SGMember PUT, GET target, PUT target
        self.assertEqual(mock_invoke.call_count, 3)

        # Verify SGMember PUT URL contains service group name
        sg_call_args = mock_invoke.call_args_list[0][0][1]
        self.assertTrue(any('serviceGroupMember/my-factory' in a for a in sg_call_args))

    @patch('azext_workload_orchestration.onboarding.target_sg_link.invoke_cli_command')
    def test_link_failure_raises_cli_error(self, mock_invoke):
        from azext_workload_orchestration.onboarding.target_sg_link import (
            link_target_to_service_group
        )
        cmd = self._get_mock_cmd()

        mock_invoke.side_effect = CLIInternalError("SG not found")

        with self.assertRaises(CLIInternalError) as ctx:
            link_target_to_service_group(cmd, '/sub/rg/targets/t1', 'bad-sg')

        self.assertIn('bad-sg', str(ctx.exception))


class TestUtils(unittest.TestCase):
    """Test shared utilities."""

    def test_print_step_with_status(self):
        from azext_workload_orchestration.onboarding.utils import print_step
        # Should not raise
        print_step(1, 4, "Installing cert-manager", "✓")

    def test_print_step_without_status(self):
        from azext_workload_orchestration.onboarding.utils import print_step
        print_step(2, 4, "Installing trust-manager")

    def test_print_success(self):
        from azext_workload_orchestration.onboarding.utils import print_success
        print_success("All done")

    def test_consts_values(self):
        from azext_workload_orchestration.onboarding.consts import (
            MAX_HIERARCHY_NAME_LENGTH,
            LRO_TIMEOUT_SECONDS,
            DEFAULT_CERT_MANAGER_VERSION,
            DEFAULT_EXTENSION_TYPE,
        )
        self.assertEqual(MAX_HIERARCHY_NAME_LENGTH, 24)
        self.assertEqual(LRO_TIMEOUT_SECONDS, 600)
        self.assertEqual(DEFAULT_CERT_MANAGER_VERSION, 'v1.15.3')
        self.assertEqual(DEFAULT_EXTENSION_TYPE, 'Microsoft.workloadorchestration')


if __name__ == '__main__':
    unittest.main()
