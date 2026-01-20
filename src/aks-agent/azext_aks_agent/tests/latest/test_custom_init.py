# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Unit tests for aks_agent_init function.
"""

import unittest
from unittest.mock import MagicMock, Mock, call, patch

from azext_aks_agent.custom import aks_agent_init
from azure.cli.core.azclierror import AzCLIError


class TestAksAgentInit(unittest.TestCase):
    """Test cases for aks_agent_init function."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_cmd = Mock()
        self.mock_cmd.cli_ctx = Mock()
        self.mock_client = Mock()
        self.resource_group = 'test-rg'
        self.cluster_name = 'test-cluster'
        self.subscription_id = 'test-subscription-id'
        self.kubeconfig_path = '/mock/kubeconfig/path'

    @patch('azext_aks_agent.custom.CLITelemetryClient')
    @patch('azext_aks_agent.custom._setup_helm_deployment')
    @patch('azext_aks_agent.custom._setup_llm_configuration')
    @patch('azext_aks_agent.custom.get_aks_credentials')
    @patch('azext_aks_agent.custom.AKSAgentManager')
    @patch('azext_aks_agent.custom.get_subscription_id')
    @patch('azext_aks_agent.custom.get_console')
    def test_init_cluster_mode_new_deployment(
            self, mock_get_console, mock_get_subscription_id, mock_aks_manager_class,
            mock_get_aks_creds, mock_setup_llm, mock_setup_helm, mock_telemetry_client):
        """Test initialization with cluster mode and new deployment."""
        # Setup mocks
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        mock_console.input.side_effect = ['1', 'test-namespace']  # Mode 1 = cluster, namespace
        mock_get_subscription_id.return_value = self.subscription_id
        mock_get_aks_creds.return_value = self.kubeconfig_path
        mock_telemetry_client.return_value.__enter__ = Mock()
        mock_telemetry_client.return_value.__exit__ = Mock()

        mock_agent_manager = MagicMock()
        mock_aks_manager_class.return_value = mock_agent_manager

        # Execute
        aks_agent_init(self.mock_cmd, self.mock_client, self.resource_group, self.cluster_name)

        # Assert
        mock_get_aks_creds.assert_called_once_with(
            self.mock_client,
            self.resource_group,
            self.cluster_name
        )
        mock_aks_manager_class.assert_called_once_with(
            resource_group_name=self.resource_group,
            cluster_name=self.cluster_name,
            namespace='test-namespace',
            subscription_id=self.subscription_id,
            kubeconfig_path=self.kubeconfig_path
        )
        mock_setup_llm.assert_called_once_with(mock_console, mock_agent_manager)
        mock_setup_helm.assert_called_once_with(mock_console, mock_agent_manager)

    @patch('azext_aks_agent.custom.CLITelemetryClient')
    @patch('azext_aks_agent.custom._setup_llm_configuration')
    @patch('azext_aks_agent.custom.get_aks_credentials')
    @patch('azext_aks_agent.custom.AKSAgentManagerClient')
    @patch('azext_aks_agent.custom.get_subscription_id')
    @patch('azext_aks_agent.custom.get_console')
    def test_init_client_mode(
            self, mock_get_console, mock_get_subscription_id, mock_aks_manager_client_class,
            mock_get_aks_creds, mock_setup_llm, mock_telemetry_client):
        """Test initialization with client mode."""
        # Setup mocks
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        mock_console.input.side_effect = ['2']  # Mode 2 = client
        mock_get_subscription_id.return_value = self.subscription_id
        mock_get_aks_creds.return_value = self.kubeconfig_path
        mock_telemetry_client.return_value.__enter__ = Mock()
        mock_telemetry_client.return_value.__exit__ = Mock()

        mock_agent_manager = MagicMock()
        mock_aks_manager_client_class.return_value = mock_agent_manager

        # Execute
        aks_agent_init(self.mock_cmd, self.mock_client, self.resource_group, self.cluster_name)

        # Assert
        mock_get_aks_creds.assert_called_once_with(
            self.mock_client,
            self.resource_group,
            self.cluster_name
        )
        mock_aks_manager_client_class.assert_called_once_with(
            resource_group_name=self.resource_group,
            cluster_name=self.cluster_name,
            subscription_id=self.subscription_id,
            kubeconfig_path=self.kubeconfig_path
        )
        mock_setup_llm.assert_called_once_with(mock_console, mock_agent_manager)

    @patch('azext_aks_agent.custom.CLITelemetryClient')
    @patch('azext_aks_agent.custom._setup_llm_configuration')
    @patch('azext_aks_agent.custom.get_aks_credentials')
    @patch('azext_aks_agent.custom.AKSAgentManager')
    @patch('azext_aks_agent.custom.get_subscription_id')
    @patch('azext_aks_agent.custom.get_console')
    def test_init_invalid_mode_choice_retry(
            self, mock_get_console, mock_get_subscription_id, mock_aks_manager_class,
            mock_get_aks_creds, mock_setup_llm, mock_telemetry_client):
        """Test initialization with invalid mode choice, then valid choice."""
        # Setup mocks
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        mock_console.input.side_effect = ['3', 'invalid', '1', 'test-namespace']  # Invalid, then mode 1
        mock_get_subscription_id.return_value = self.subscription_id
        mock_get_aks_creds.return_value = self.kubeconfig_path
        mock_telemetry_client.return_value.__enter__ = Mock()
        mock_telemetry_client.return_value.__exit__ = Mock()

        mock_agent_manager = MagicMock()
        mock_aks_manager_class.return_value = mock_agent_manager

        # Execute
        aks_agent_init(self.mock_cmd, self.mock_client, self.resource_group, self.cluster_name)

        # Assert - should have prompted multiple times for mode
        mode_prompts = [call for call in mock_console.input.call_args_list
                        if 'Enter your choice (1 or 2)' in str(call)]
        self.assertTrue(len(mode_prompts) >= 2, "Should prompt multiple times for invalid input")

    @patch('azext_aks_agent.custom.CLITelemetryClient')
    @patch('azext_aks_agent.custom._setup_helm_deployment')
    @patch('azext_aks_agent.custom._setup_llm_configuration')
    @patch('azext_aks_agent.custom.get_aks_credentials')
    @patch('azext_aks_agent.custom.AKSAgentManager')
    @patch('azext_aks_agent.custom.get_subscription_id')
    @patch('azext_aks_agent.custom.get_console')
    def test_init_empty_namespace_retry(
            self, mock_get_console, mock_get_subscription_id, mock_aks_manager_class,
            mock_get_aks_creds, mock_setup_llm, mock_setup_helm, mock_telemetry_client):
        """Test initialization with empty namespace, then valid namespace."""
        # Setup mocks
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        mock_console.input.side_effect = ['1', '', '  ', 'test-namespace']  # Mode 1, empty inputs, then valid
        mock_get_subscription_id.return_value = self.subscription_id
        mock_get_aks_creds.return_value = self.kubeconfig_path
        mock_telemetry_client.return_value.__enter__ = Mock()
        mock_telemetry_client.return_value.__exit__ = Mock()

        mock_agent_manager = MagicMock()
        mock_aks_manager_class.return_value = mock_agent_manager

        # Execute
        aks_agent_init(self.mock_cmd, self.mock_client, self.resource_group, self.cluster_name)

        # Assert - should have prompted multiple times for namespace
        namespace_prompts = [call for call in mock_console.input.call_args_list
                             if 'Enter namespace' in str(call)]
        self.assertTrue(len(namespace_prompts) >= 2, "Should prompt multiple times for empty namespace")

    @patch('azext_aks_agent.custom.CLITelemetryClient')
    @patch('azext_aks_agent.custom._setup_llm_configuration')
    @patch('azext_aks_agent.custom.get_aks_credentials')
    @patch('azext_aks_agent.custom.AKSAgentManager')
    @patch('azext_aks_agent.custom.get_subscription_id')
    @patch('azext_aks_agent.custom.get_console')
    def test_init_setup_llm_configuration_error(
            self, mock_get_console, mock_get_subscription_id, mock_aks_manager_class,
            mock_get_aks_creds, mock_setup_llm, mock_telemetry_client):
        """Test initialization raises error when LLM configuration setup fails."""
        # Setup mocks
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        mock_console.input.side_effect = ['1', 'test-namespace']
        mock_get_subscription_id.return_value = self.subscription_id
        mock_get_aks_creds.return_value = self.kubeconfig_path

        # Properly mock the context manager - __exit__ must return None to allow exceptions to propagate
        mock_telemetry_instance = MagicMock()
        mock_telemetry_client.return_value = mock_telemetry_instance
        mock_telemetry_instance.__enter__ = Mock(return_value=mock_telemetry_instance)
        mock_telemetry_instance.__exit__ = Mock(return_value=None)

        mock_agent_manager = MagicMock()
        mock_aks_manager_class.return_value = mock_agent_manager

        # Make setup_llm raise an error
        mock_setup_llm.side_effect = AzCLIError("Failed to configure LLM")

        # Execute - should raise AzCLIError wrapped with "Agent initialization failed"
        with self.assertRaises(AzCLIError) as cm:
            aks_agent_init(self.mock_cmd, self.mock_client, self.resource_group, self.cluster_name)

        # The error should be wrapped with "Agent initialization failed:"
        exception_str = str(cm.exception)
        self.assertIn("Agent initialization failed", exception_str)
        self.assertIn("Failed to configure LLM", exception_str)

    @patch('azext_aks_agent.custom.CLITelemetryClient')
    @patch('azext_aks_agent.custom._setup_llm_configuration')
    @patch('azext_aks_agent.custom.get_aks_credentials')
    @patch('azext_aks_agent.custom.get_subscription_id')
    @patch('azext_aks_agent.custom.get_console')
    def test_init_telemetry_tracking(
            self, mock_get_console, mock_get_subscription_id,
            mock_get_aks_creds, mock_setup_llm, mock_telemetry_client):
        """Test that telemetry tracks mode correctly."""
        # Setup mocks
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        mock_console.input.side_effect = ['2']  # Client mode
        mock_get_subscription_id.return_value = self.subscription_id
        mock_get_aks_creds.return_value = self.kubeconfig_path

        mock_telemetry_instance = MagicMock()
        mock_telemetry_client.return_value = mock_telemetry_instance
        mock_telemetry_instance.__enter__ = Mock(return_value=mock_telemetry_instance)
        mock_telemetry_instance.__exit__ = Mock()

        # Execute
        with patch('azext_aks_agent.custom.AKSAgentManagerClient'):
            aks_agent_init(self.mock_cmd, self.mock_client, self.resource_group, self.cluster_name)

        # Assert telemetry mode was set
        self.assertEqual(mock_telemetry_instance.mode, 'client')


if __name__ == '__main__':
    unittest.main()
