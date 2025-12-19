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

    @patch('azext_aks_agent.custom._setup_and_create_llm_config')
    @patch('azext_aks_agent.custom._prompt_managed_identity_configuration')
    @patch('azext_aks_agent.custom._prompt_cluster_role_configuration')
    @patch('azext_aks_agent.custom.get_aks_credentials')
    @patch('azext_aks_agent.custom.AKSAgentManager')
    @patch('azext_aks_agent.custom.get_subscription_id')
    @patch('azext_aks_agent.custom.get_console')
    def test_init_new_deployment_no_llm_config(
            self, mock_get_console, mock_get_subscription_id, mock_aks_manager_class,
            mock_get_aks_creds, mock_prompt_cluster_role, mock_prompt_managed_identity,
            mock_setup_llm):
        """Test initialization with new deployment and no existing LLM config."""
        # Setup mocks
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        mock_get_subscription_id.return_value = self.subscription_id
        mock_get_aks_creds.return_value = self.kubeconfig_path

        mock_agent_manager = MagicMock()
        mock_agent_manager.check_llm_config_exists.return_value = False
        mock_agent_manager.get_agent_status.return_value = {
            "helm_status": "not_found",
            "ready": True
        }
        mock_agent_manager.deploy_agent.return_value = (True, "")
        mock_aks_manager_class.return_value = mock_agent_manager

        mock_prompt_cluster_role.return_value = ""
        mock_prompt_managed_identity.return_value = ""

        # Execute
        aks_agent_init(self.mock_cmd, self.mock_client, self.resource_group, self.cluster_name)

        # Assert
        mock_get_aks_creds.assert_called_once_with(
            self.mock_client,
            self.resource_group,
            self.cluster_name
        )
        mock_aks_manager_class.assert_called_once()
        mock_agent_manager.check_llm_config_exists.assert_called_once()
        mock_setup_llm.assert_called_once_with(mock_console, mock_agent_manager)
        mock_prompt_cluster_role.assert_called_once()
        mock_prompt_managed_identity.assert_called_once()
        mock_agent_manager.deploy_agent.assert_called_once()

    @patch('azext_aks_agent.custom._get_existing_cluster_role')
    @patch('azext_aks_agent.custom._setup_and_create_llm_config')
    @patch('azext_aks_agent.custom.get_aks_credentials')
    @patch('azext_aks_agent.custom.AKSAgentManager')
    @patch('azext_aks_agent.custom.get_subscription_id')
    @patch('azext_aks_agent.custom.get_console')
    def test_init_existing_llm_config_user_skips_update(
            self, mock_get_console, mock_get_subscription_id, mock_aks_manager_class,
            mock_get_aks_creds, mock_setup_llm, mock_get_cluster_role):
        """Test initialization raises AzCLIError when LLM config exists, user skips update, but cluster role not found."""
        # Setup mocks
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        mock_console.input.side_effect = ['n']  # User skips LLM config update
        mock_get_subscription_id.return_value = self.subscription_id
        mock_get_aks_creds.return_value = self.kubeconfig_path

        mock_agent_manager = MagicMock()
        mock_agent_manager.check_llm_config_exists.return_value = True
        mock_agent_manager.get_agent_status.return_value = {
            "helm_status": "deployed",
            "ready": True
        }
        mock_agent_manager.managed_identity_client_id = ""
        mock_aks_manager_class.return_value = mock_agent_manager

        mock_get_cluster_role.return_value = None  # Cannot find cluster role

        # Execute - should raise AzCLIError with wrapped message
        with self.assertRaises(AzCLIError) as cm:
            aks_agent_init(self.mock_cmd, self.mock_client, self.resource_group, self.cluster_name)

        # Assert
        mock_agent_manager.check_llm_config_exists.assert_called_once()
        mock_setup_llm.assert_not_called()
        # Verify the error message contains the wrapped format
        self.assertIn("Agent initialization failed:", str(cm.exception))
        self.assertIn("Could not determine existing cluster role", str(cm.exception))

    @patch('azext_aks_agent.custom._get_existing_cluster_role')
    @patch('azext_aks_agent.custom._setup_and_create_llm_config')
    @patch('azext_aks_agent.custom.get_aks_credentials')
    @patch('azext_aks_agent.custom.AKSAgentManager')
    @patch('azext_aks_agent.custom.get_subscription_id')
    @patch('azext_aks_agent.custom.get_console')
    def test_init_existing_llm_config_user_updates(
            self, mock_get_console, mock_get_subscription_id, mock_aks_manager_class,
            mock_get_aks_creds, mock_setup_llm, mock_get_cluster_role):
        """Test initialization raises AzCLIError when LLM config exists, user updates, but cluster role not found."""
        # Setup mocks
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        mock_console.input.side_effect = ['yes']  # User updates LLM config
        mock_get_subscription_id.return_value = self.subscription_id
        mock_get_aks_creds.return_value = self.kubeconfig_path

        mock_agent_manager = MagicMock()
        mock_agent_manager.check_llm_config_exists.return_value = True
        mock_agent_manager.get_agent_status.return_value = {
            "helm_status": "deployed",
            "ready": True
        }
        mock_agent_manager.managed_identity_client_id = ""
        mock_aks_manager_class.return_value = mock_agent_manager

        mock_get_cluster_role.return_value = None  # Cannot find cluster role

        # Execute - should raise AzCLIError with wrapped message
        with self.assertRaises(AzCLIError) as cm:
            aks_agent_init(self.mock_cmd, self.mock_client, self.resource_group, self.cluster_name)

        # Assert
        mock_agent_manager.check_llm_config_exists.assert_called_once()
        mock_setup_llm.assert_called_once_with(mock_console, mock_agent_manager)
        # Verify the error message contains the wrapped format
        self.assertIn("Agent initialization failed:", str(cm.exception))
        self.assertIn("Could not determine existing cluster role", str(cm.exception))

    @patch('azext_aks_agent.custom._get_existing_cluster_role')
    @patch('azext_aks_agent.custom._display_cluster_role_rules')
    @patch('azext_aks_agent.custom._prompt_managed_identity_configuration')
    @patch('azext_aks_agent.custom._setup_and_create_llm_config')
    @patch('azext_aks_agent.custom.get_aks_credentials')
    @patch('azext_aks_agent.custom.AKSAgentManager')
    @patch('azext_aks_agent.custom.get_subscription_id')
    @patch('azext_aks_agent.custom.get_console')
    def test_init_deployed_helm_with_managed_identity_update(
            self, mock_get_console, mock_get_subscription_id, mock_aks_manager_class,
            mock_get_aks_creds, mock_setup_llm, mock_prompt_managed_identity,
            mock_display_rules, mock_get_cluster_role):
        """Test initialization when helm is deployed and user updates managed identity."""
        # Setup mocks
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        mock_console.input.side_effect = ['n', 'yes']  # Skip LLM update, change managed identity
        mock_get_subscription_id.return_value = self.subscription_id
        mock_get_aks_creds.return_value = self.kubeconfig_path

        mock_agent_manager = MagicMock()
        mock_agent_manager.check_llm_config_exists.return_value = True
        mock_agent_manager.get_agent_status.side_effect = [
            {"helm_status": "deployed", "ready": False},
            {"helm_status": "deployed", "ready": True}
        ]
        mock_agent_manager.managed_identity_client_id = "existing-client-id"
        mock_agent_manager.deploy_agent.return_value = (True, "")
        mock_aks_manager_class.return_value = mock_agent_manager

        mock_get_cluster_role.return_value = "test-cluster-role"
        mock_cluster_role = Mock()
        mock_agent_manager.rbac_v1.read_cluster_role.return_value = mock_cluster_role
        mock_prompt_managed_identity.return_value = "new-client-id"

        # Execute
        aks_agent_init(self.mock_cmd, self.mock_client, self.resource_group, self.cluster_name)

        # Assert
        mock_prompt_managed_identity.assert_called_once()
        self.assertEqual(mock_agent_manager.managed_identity_client_id, "new-client-id")
        mock_agent_manager.deploy_agent.assert_called_once()

    @patch('azext_aks_agent.custom._prompt_managed_identity_configuration')
    @patch('azext_aks_agent.custom._prompt_cluster_role_configuration')
    @patch('azext_aks_agent.custom._setup_and_create_llm_config')
    @patch('azext_aks_agent.custom.get_aks_credentials')
    @patch('azext_aks_agent.custom.AKSAgentManager')
    @patch('azext_aks_agent.custom.get_subscription_id')
    @patch('azext_aks_agent.custom.get_console')
    def test_init_with_custom_cluster_role(
            self, mock_get_console, mock_get_subscription_id, mock_aks_manager_class,
            mock_get_aks_creds, mock_setup_llm, mock_prompt_cluster_role,
            mock_prompt_managed_identity):
        """Test initialization with custom cluster role."""
        # Setup mocks
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        mock_get_subscription_id.return_value = self.subscription_id
        mock_get_aks_creds.return_value = self.kubeconfig_path

        mock_agent_manager = MagicMock()
        mock_agent_manager.check_llm_config_exists.return_value = False
        mock_agent_manager.get_agent_status.return_value = {
            "helm_status": "not_found",
            "ready": True
        }
        mock_agent_manager.deploy_agent.return_value = (True, "")
        mock_aks_manager_class.return_value = mock_agent_manager

        mock_prompt_cluster_role.return_value = "custom-cluster-role"
        mock_prompt_managed_identity.return_value = "test-client-id"

        # Execute
        aks_agent_init(self.mock_cmd, self.mock_client, self.resource_group, self.cluster_name)

        # Assert
        self.assertEqual(mock_agent_manager.customized_cluster_role_name, "custom-cluster-role")
        self.assertEqual(mock_agent_manager.managed_identity_client_id, "test-client-id")
        mock_agent_manager.deploy_agent.assert_called_once()

    @patch('azext_aks_agent.custom._setup_and_create_llm_config')
    @patch('azext_aks_agent.custom.get_aks_credentials')
    @patch('azext_aks_agent.custom.AKSAgentManager')
    @patch('azext_aks_agent.custom.get_subscription_id')
    @patch('azext_aks_agent.custom.get_console')
    def test_init_deployment_failure_logs_error(
            self, mock_get_console, mock_get_subscription_id, mock_aks_manager_class,
            mock_get_aks_creds, mock_setup_llm):
        """Test initialization raises AzCLIError when deployment fails."""
        # Setup mocks
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        mock_get_subscription_id.return_value = self.subscription_id
        mock_get_aks_creds.return_value = self.kubeconfig_path

        mock_agent_manager = MagicMock()
        mock_agent_manager.check_llm_config_exists.return_value = False
        mock_agent_manager.get_agent_status.return_value = {"helm_status": "not_found"}
        mock_agent_manager.deploy_agent.return_value = (False, "Deployment failed")
        mock_aks_manager_class.return_value = mock_agent_manager

        # Execute - should raise AzCLIError with wrapped message
        with self.assertRaises(AzCLIError) as cm:
            aks_agent_init(self.mock_cmd, self.mock_client, self.resource_group, self.cluster_name)

        # Verify the error message contains the wrapped format
        self.assertIn("Agent initialization failed:", str(cm.exception))
        self.assertIn("Failed to deploy agent", str(cm.exception))

    @patch('azext_aks_agent.custom._get_existing_cluster_role')
    @patch('azext_aks_agent.custom._setup_and_create_llm_config')
    @patch('azext_aks_agent.custom.get_aks_credentials')
    @patch('azext_aks_agent.custom.AKSAgentManager')
    @patch('azext_aks_agent.custom.get_subscription_id')
    @patch('azext_aks_agent.custom.get_console')
    def test_init_deployed_no_cluster_role_logs_error(
            self, mock_get_console, mock_get_subscription_id, mock_aks_manager_class,
            mock_get_aks_creds, mock_setup_llm, mock_get_cluster_role):
        """Test initialization raises AzCLIError when deployed but cannot determine cluster role."""
        # Setup mocks
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        mock_console.input.return_value = 'n'
        mock_get_subscription_id.return_value = self.subscription_id
        mock_get_aks_creds.return_value = self.kubeconfig_path

        mock_agent_manager = MagicMock()
        mock_agent_manager.check_llm_config_exists.return_value = True
        mock_agent_manager.get_agent_status.return_value = {"helm_status": "deployed"}
        mock_aks_manager_class.return_value = mock_agent_manager

        mock_get_cluster_role.return_value = None  # Cannot find cluster role

        # Execute - should raise AzCLIError with wrapped message
        with self.assertRaises(AzCLIError) as cm:
            aks_agent_init(self.mock_cmd, self.mock_client, self.resource_group, self.cluster_name)

        # Verify the error message contains the wrapped format
        self.assertIn("Agent initialization failed:", str(cm.exception))
        self.assertIn("Could not determine existing cluster role", str(cm.exception))

    @patch('azext_aks_agent.custom._prompt_managed_identity_configuration')
    @patch('azext_aks_agent.custom._prompt_cluster_role_configuration')
    @patch('azext_aks_agent.custom._setup_and_create_llm_config')
    @patch('azext_aks_agent.custom.get_aks_credentials')
    @patch('azext_aks_agent.custom.AKSAgentManager')
    @patch('azext_aks_agent.custom.get_subscription_id')
    @patch('azext_aks_agent.custom.get_console')
    def test_init_deployment_not_ready_shows_warning(
            self, mock_get_console, mock_get_subscription_id, mock_aks_manager_class,
            mock_get_aks_creds, mock_setup_llm, mock_prompt_cluster_role,
            mock_prompt_managed_identity):
        """Test initialization shows warning when deployment not ready."""
        # Setup mocks
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        mock_get_subscription_id.return_value = self.subscription_id
        mock_get_aks_creds.return_value = self.kubeconfig_path

        mock_agent_manager = MagicMock()
        mock_agent_manager.check_llm_config_exists.return_value = False
        mock_agent_manager.get_agent_status.side_effect = [
            {"helm_status": "not_found"},
            {"helm_status": "deployed", "ready": False}
        ]
        mock_agent_manager.deploy_agent.return_value = (True, "")
        mock_aks_manager_class.return_value = mock_agent_manager

        mock_prompt_cluster_role.return_value = ""
        mock_prompt_managed_identity.return_value = ""

        # Execute
        aks_agent_init(self.mock_cmd, self.mock_client, self.resource_group, self.cluster_name)

        # Assert - check that console.print was called with warning message
        warning_calls = [call for call in mock_console.print.call_args_list
                         if "not yet ready" in str(call)]
        self.assertTrue(len(warning_calls) > 0, "Expected warning message about agent not ready")

    @patch('azext_aks_agent.custom._prompt_managed_identity_configuration')
    @patch('azext_aks_agent.custom._prompt_cluster_role_configuration')
    @patch('azext_aks_agent.custom._setup_and_create_llm_config')
    @patch('azext_aks_agent.custom.get_aks_credentials')
    @patch('azext_aks_agent.custom.AKSAgentManager')
    @patch('azext_aks_agent.custom.get_subscription_id')
    @patch('azext_aks_agent.custom.get_console')
    def test_init_with_azureopenai_model_and_workload_identity(
            self, mock_get_console, mock_get_subscription_id, mock_aks_manager_class,
            mock_get_aks_creds, mock_setup_llm, mock_prompt_cluster_role,
            mock_prompt_managed_identity):
        """Test initialization with Azure OpenAI model and workload identity client ID."""
        # Setup mocks
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        mock_get_subscription_id.return_value = self.subscription_id
        mock_get_aks_creds.return_value = self.kubeconfig_path

        mock_agent_manager = MagicMock()
        mock_agent_manager.check_llm_config_exists.return_value = False
        mock_agent_manager.get_agent_status.return_value = {
            "helm_status": "not_found",
            "ready": True
        }
        mock_agent_manager.deploy_agent.return_value = (True, "")
        mock_aks_manager_class.return_value = mock_agent_manager

        # Setup LLM config manager with Azure OpenAI model
        mock_llm_config_manager = MagicMock()
        mock_llm_config_manager.model_list = {
            "azure/gpt-4": {
                "model": "azure/gpt-4",
                "api_base": "https://test-openai.openai.azure.com",
                "api_version": "2024-02-15-preview"
            }
        }
        mock_agent_manager.llm_config_manager = mock_llm_config_manager

        # Mock _setup_and_create_llm_config to set the model_list
        def setup_llm_side_effect(console, agent_manager):
            agent_manager.llm_config_manager.model_list = {
                "azure/gpt-4": {
                    "model": "azure/gpt-4",
                    "api_base": "https://test-openai.openai.azure.com",
                    "api_version": "2024-02-15-preview"
                }
            }
        mock_setup_llm.side_effect = setup_llm_side_effect

        mock_prompt_cluster_role.return_value = "custom-role"
        mock_prompt_managed_identity.return_value = "test-workload-client-id-12345"

        # Execute
        aks_agent_init(self.mock_cmd, self.mock_client, self.resource_group, self.cluster_name)

        # Assert
        mock_setup_llm.assert_called_once_with(mock_console, mock_agent_manager)
        mock_prompt_managed_identity.assert_called_once()

        # Verify that managed identity client ID was set
        self.assertEqual(mock_agent_manager.managed_identity_client_id, "test-workload-client-id-12345")

        # Verify that customized cluster role name was set
        self.assertEqual(mock_agent_manager.customized_cluster_role_name, "custom-role")

        # Verify deploy_agent was called
        mock_agent_manager.deploy_agent.assert_called_once()


if __name__ == '__main__':
    unittest.main()
