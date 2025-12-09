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

    @patch('azext_aks_agent.custom.get_aks_credentials')
    @patch('azext_aks_agent.custom.AKSAgentManager')
    @patch('azext_aks_agent.custom.get_subscription_id')
    @patch('azext_aks_agent.custom.get_console')
    def test_cleanup_with_various_inputs(self, mock_get_console, mock_get_subscription_id, mock_aks_manager_class,
                                         mock_get_aks_creds):
        """Test cleanup with various user inputs including confirmation, cancellation, and invalid inputs."""
        mock_get_aks_creds.return_value = '/mock/kubeconfig/path'

        test_cases = [
            # (input, should_proceed, test_description)
            ('y', True, 'lowercase y confirms'),
            ('Y', True, 'uppercase Y confirms'),
            ('yes', True, 'lowercase yes confirms'),
            ('YES', True, 'uppercase YES confirms'),
            ('n', False, 'lowercase n cancels'),
            ('N', False, 'uppercase N cancels'),
            ('no', False, 'lowercase no cancels'),
            ('NO', False, 'uppercase NO cancels'),
            ('', False, 'empty input (default) cancels'),
            ('maybe', False, 'invalid input cancels'),
            ('sure', False, 'invalid input cancels'),
            ('1', False, 'invalid input cancels'),
            ('true', False, 'invalid input cancels'),
            ('ok', False, 'invalid input cancels'),
        ]

        for user_input, should_proceed, description in test_cases:
            with self.subTest(input=user_input, description=description):
                # Reset mocks
                mock_console = MagicMock()
                mock_get_console.return_value = mock_console
                mock_console.input.return_value = user_input
                mock_get_subscription_id.return_value = self.subscription_id
                mock_aks_manager_class.reset_mock()
                mock_get_aks_creds.reset_mock()

                mock_agent_manager = MagicMock()
                mock_agent_manager.uninstall_agent.return_value = True
                mock_aks_manager_class.return_value = mock_agent_manager

                # Execute
                aks_agent_cleanup(self.mock_cmd, self.mock_client, self.resource_group, self.cluster_name)

                # Assert
                if should_proceed:
                    mock_get_aks_creds.assert_called_once_with(
                        self.mock_client,
                        self.resource_group,
                        self.cluster_name
                    )
                    mock_aks_manager_class.assert_called_once_with(
                        resource_group_name=self.resource_group,
                        cluster_name=self.cluster_name,
                        subscription_id=self.subscription_id,
                        kubeconfig_path='/mock/kubeconfig/path'
                    )
                    mock_agent_manager.uninstall_agent.assert_called_once()
                else:
                    mock_get_aks_creds.assert_not_called()
                    mock_aks_manager_class.assert_not_called()

    @patch('azext_aks_agent.custom.get_aks_credentials')
    @patch('azext_aks_agent.custom.AKSAgentManager')
    @patch('azext_aks_agent.custom.get_subscription_id')
    @patch('azext_aks_agent.custom.get_console')
    def test_cleanup_failed(self, mock_get_console, mock_get_subscription_id, mock_aks_manager_class,
                            mock_get_aks_creds):
        """Test cleanup failure when uninstall_agent returns False."""
        # Setup mocks
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        mock_console.input.return_value = 'yes'
        mock_get_subscription_id.return_value = self.subscription_id
        mock_get_aks_creds.return_value = '/mock/kubeconfig/path'

        mock_agent_manager = MagicMock()
        mock_agent_manager.uninstall_agent.return_value = False
        mock_aks_manager_class.return_value = mock_agent_manager

        # Execute
        aks_agent_cleanup(self.mock_cmd, self.mock_client, self.resource_group, self.cluster_name)

        # Assert
        mock_get_aks_creds.assert_called_once()
        mock_aks_manager_class.assert_called_once()
        mock_agent_manager.uninstall_agent.assert_called_once()

        # Assert failure message was printed
        failure_calls = [call for call in mock_console.print.call_args_list
                         if "Cleanup failed" in str(call)]
        self.assertTrue(len(failure_calls) > 0, "Failure message should be printed")

    @patch('azext_aks_agent.custom.get_aks_credentials')
    @patch('azext_aks_agent.custom.AKSAgentManager')
    @patch('azext_aks_agent.custom.get_subscription_id')
    @patch('azext_aks_agent.custom.get_console')
    def test_cleanup_prints_expected_messages(self, mock_get_console, mock_get_subscription_id,
                                              mock_aks_manager_class, mock_get_aks_creds):
        """Test that all expected messages are printed during successful cleanup."""
        # Setup mocks
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        mock_console.input.return_value = 'y'
        mock_get_subscription_id.return_value = self.subscription_id
        mock_get_aks_creds.return_value = '/mock/kubeconfig/path'

        mock_agent_manager = MagicMock()
        mock_agent_manager.uninstall_agent.return_value = True
        mock_aks_manager_class.return_value = mock_agent_manager

        # Execute
        aks_agent_cleanup(self.mock_cmd, self.mock_client, self.resource_group, self.cluster_name)

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
