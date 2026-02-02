# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Unit tests for aks_agent_cleanup function.
"""

import unittest
from unittest.mock import MagicMock, Mock, patch

from azext_aks_agent.custom import aks_agent_cleanup


class TestAksAgentCleanup(unittest.TestCase):
    """Test cases for aks_agent_cleanup function."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_cmd = Mock()
        self.mock_cmd.cli_ctx = Mock()
        self.mock_client = Mock()
        self.resource_group = 'test-rg'
        self.cluster_name = 'test-cluster'
        self.subscription_id = 'test-subscription-id'

    @patch('azext_aks_agent.custom.CLITelemetryClient')
    @patch('azext_aks_agent.custom.get_aks_credentials')
    @patch('azext_aks_agent.custom.AKSAgentManager')
    @patch('azext_aks_agent.custom.AKSAgentManagerClient')
    @patch('azext_aks_agent.custom.get_subscription_id')
    @patch('azext_aks_agent.custom.get_console')
    def test_cleanup_with_various_inputs(self, mock_get_console, mock_get_subscription_id,
                                         mock_aks_manager_client_class, mock_aks_manager_class,
                                         mock_get_aks_creds, mock_telemetry_client):
        """Test cleanup with various user inputs and modes."""
        mock_get_aks_creds.return_value = '/mock/kubeconfig/path'
        mock_get_subscription_id.return_value = self.subscription_id
        mock_telemetry_client.return_value.__enter__ = Mock()
        mock_telemetry_client.return_value.__exit__ = Mock()

        # Test cases: (user_input, should_proceed, mode, namespace, description)
        test_cases = [
            # Cluster mode tests with namespace
            ('y', True, 'cluster', 'test-namespace', 'cluster mode: lowercase y confirms'),
            ('Y', True, 'cluster', 'test-namespace', 'cluster mode: uppercase Y confirms'),
            ('yes', True, 'cluster', 'test-namespace', 'cluster mode: lowercase yes confirms'),
            ('YES', True, 'cluster', 'test-namespace', 'cluster mode: uppercase YES confirms'),
            ('n', False, 'cluster', 'test-namespace', 'cluster mode: lowercase n cancels'),
            ('N', False, 'cluster', 'test-namespace', 'cluster mode: uppercase N cancels'),
            ('', False, 'cluster', 'test-namespace', 'cluster mode: empty input cancels'),
            
            # Client mode tests without namespace
            ('y', True, 'client', None, 'client mode: lowercase y confirms'),
            ('yes', True, 'client', None, 'client mode: yes confirms'),
            ('n', False, 'client', None, 'client mode: n cancels'),
            
            # Client mode tests with namespace (should show warning)
            ('y', True, 'client', 'test-namespace', 'client mode with namespace: y confirms'),
        ]

        for user_input, should_proceed, mode, namespace, description in test_cases:
            with self.subTest(input=user_input, mode=mode, namespace=namespace, description=description):
                # Reset mocks
                mock_console = MagicMock()
                mock_get_console.return_value = mock_console
                mock_console.input.return_value = user_input
                mock_aks_manager_class.reset_mock()
                mock_aks_manager_client_class.reset_mock()
                mock_get_aks_creds.reset_mock()
                mock_telemetry_client.reset_mock()

                mock_agent_manager = MagicMock()
                mock_agent_manager.uninstall_agent.return_value = True
                
                if mode == 'client':
                    mock_aks_manager_client_class.return_value = mock_agent_manager
                else:
                    mock_aks_manager_class.return_value = mock_agent_manager

                # Execute
                aks_agent_cleanup(
                    self.mock_cmd,
                    self.mock_client,
                    self.resource_group,
                    self.cluster_name,
                    namespace,
                    mode
                )

                # Assert
                if should_proceed:
                    mock_get_aks_creds.assert_called_once_with(
                        self.mock_client,
                        self.resource_group,
                        self.cluster_name
                    )
                    
                    if mode == 'client':
                        mock_aks_manager_client_class.assert_called_once_with(
                            resource_group_name=self.resource_group,
                            cluster_name=self.cluster_name,
                            subscription_id=self.subscription_id,
                            kubeconfig_path='/mock/kubeconfig/path'
                        )
                        # Check for warning when namespace is specified in client mode
                        if namespace:
                            warning_calls = [call for call in mock_console.print.call_args_list
                                           if namespace in str(call) and 'Warning' in str(call)]
                            self.assertTrue(len(warning_calls) > 0,
                                          "Warning should be printed when namespace is specified in client mode")
                    else:
                        mock_aks_manager_class.assert_called_once_with(
                            resource_group_name=self.resource_group,
                            cluster_name=self.cluster_name,
                            subscription_id=self.subscription_id,
                            namespace=namespace,
                            kubeconfig_path='/mock/kubeconfig/path'
                        )
                    
                    mock_agent_manager.uninstall_agent.assert_called_once()
                else:
                    mock_agent_manager.uninstall_agent.assert_not_called()

    @patch('azext_aks_agent.custom.CLITelemetryClient')
    @patch('azext_aks_agent.custom.get_aks_credentials')
    @patch('azext_aks_agent.custom.AKSAgentManager')
    @patch('azext_aks_agent.custom.get_subscription_id')
    @patch('azext_aks_agent.custom.get_console')
    def test_cleanup_failed(self, mock_get_console, mock_get_subscription_id, mock_aks_manager_class,
                            mock_get_aks_creds, mock_telemetry_client):
        """Test cleanup failure when uninstall_agent returns False."""
        # Setup mocks
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        mock_console.input.return_value = 'yes'
        mock_get_subscription_id.return_value = self.subscription_id
        mock_get_aks_creds.return_value = '/mock/kubeconfig/path'
        mock_telemetry_client.return_value.__enter__ = Mock()
        mock_telemetry_client.return_value.__exit__ = Mock()

        mock_agent_manager = MagicMock()
        mock_agent_manager.uninstall_agent.return_value = False
        mock_aks_manager_class.return_value = mock_agent_manager

        # Execute
        aks_agent_cleanup(
            self.mock_cmd,
            self.mock_client,
            self.resource_group,
            self.cluster_name,
            'test-namespace',
            'cluster'
        )

        # Assert
        mock_get_aks_creds.assert_called_once()
        mock_aks_manager_class.assert_called_once()
        mock_agent_manager.uninstall_agent.assert_called_once()

        # Assert failure message was printed
        failure_calls = [call for call in mock_console.print.call_args_list
                         if "Cleanup failed" in str(call)]
        self.assertTrue(len(failure_calls) > 0, "Failure message should be printed")

    @patch('azext_aks_agent.custom.CLITelemetryClient')
    @patch('azext_aks_agent.custom.get_aks_credentials')
    @patch('azext_aks_agent.custom.AKSAgentManager')
    @patch('azext_aks_agent.custom.get_subscription_id')
    @patch('azext_aks_agent.custom.get_console')
    def test_cleanup_prints_expected_messages(self, mock_get_console, mock_get_subscription_id,
                                              mock_aks_manager_class, mock_get_aks_creds, mock_telemetry_client):
        """Test that all expected messages are printed during successful cleanup."""
        # Setup mocks
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        mock_console.input.return_value = 'y'
        mock_get_subscription_id.return_value = self.subscription_id
        mock_get_aks_creds.return_value = '/mock/kubeconfig/path'
        mock_telemetry_client.return_value.__enter__ = Mock()
        mock_telemetry_client.return_value.__exit__ = Mock()

        mock_agent_manager = MagicMock()
        mock_agent_manager.uninstall_agent.return_value = True
        mock_aks_manager_class.return_value = mock_agent_manager

        # Execute
        aks_agent_cleanup(
            self.mock_cmd,
            self.mock_client,
            self.resource_group,
            self.cluster_name,
            'test-namespace',
            'cluster'
        )

        # Assert uninstall_agent was called
        mock_agent_manager.uninstall_agent.assert_called_once()

        # Collect all printed messages
        all_prints = [str(call) for call in mock_console.print.call_args_list]
        all_messages = '\n'.join(all_prints)

        # Assert expected messages appear
        self.assertIn("Warning", all_messages, "Warning message should be printed")
        self.assertIn("Starting cleanup", all_messages, "Starting message should be printed")
        self.assertIn("typically takes a few seconds", all_messages, "Time estimate should be printed")
        self.assertIn("Cleanup completed successfully", all_messages, "Success message should be printed")


if __name__ == '__main__':
    unittest.main()
