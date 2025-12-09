# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Unit tests for AKSAgentManager.
"""

import unittest
from unittest.mock import MagicMock, Mock, PropertyMock, patch

from azext_aks_agent.agent.k8s.aks_agent_manager import AKSAgentManager
from kubernetes.client.rest import ApiException


class TestAKSAgentManager(unittest.TestCase):
    """Test cases for AKSAgentManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.namespace = "aks-agent"
        self.resource_group = "test-rg"
        self.cluster_name = "test-cluster"
        self.subscription_id = "test-sub-id"
        self.kubeconfig_path = "/mock/kubeconfig"

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._init_k8s_client')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_init_default_values(self, mock_helm_manager, mock_load_config, mock_init_client):
        """Test AKSAgentManager initialization with default values."""
        manager = AKSAgentManager()

        self.assertEqual(manager.namespace, "kube-system")
        self.assertEqual(manager.helm_release_name, "aks-agent")
        self.assertIsNotNone(manager.llm_config_manager)
        mock_init_client.assert_called_once()
        mock_load_config.assert_called_once()

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._init_k8s_client')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_init_custom_values(self, mock_helm_manager, mock_load_config, mock_init_client):
        """Test AKSAgentManager initialization with custom values."""
        manager = AKSAgentManager(
            namespace=self.namespace,
            kubeconfig_path=self.kubeconfig_path,
            resource_group_name=self.resource_group,
            cluster_name=self.cluster_name,
            subscription_id=self.subscription_id
        )

        self.assertEqual(manager.namespace, self.namespace)
        self.assertEqual(manager.kubeconfig_path, self.kubeconfig_path)
        self.assertEqual(manager.resource_group_name, self.resource_group)
        self.assertEqual(manager.cluster_name, self.cluster_name)
        self.assertEqual(manager.subscription_id, self.subscription_id)

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._init_k8s_client')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_set_aks_context(self, mock_helm_manager, mock_load_config, mock_init_client):
        """Test setting AKS context."""
        manager = AKSAgentManager()

        manager.set_aks_context(
            resource_group_name=self.resource_group,
            cluster_name=self.cluster_name,
            subscription_id=self.subscription_id
        )

        self.assertEqual(manager.resource_group_name, self.resource_group)
        self.assertEqual(manager.cluster_name, self.cluster_name)
        self.assertEqual(manager.subscription_id, self.subscription_id)

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.client.CoreV1Api')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.config.load_kube_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_get_agent_pods_success(self, mock_helm_manager, mock_load_config, mock_load_kube, mock_core_api):
        """Test getting agent pods successfully."""
        # Setup mock pods with Running status
        mock_aks_agent_pod = Mock()
        mock_aks_agent_pod.metadata.name = "aks-agent-pod-1"
        mock_aks_agent_pod.status.phase = "Running"

        mock_aks_mcp_pod = Mock()
        mock_aks_mcp_pod.metadata.name = "aks-mcp-pod-1"
        mock_aks_mcp_pod.status.phase = "Running"

        # Mock pod lists for each label selector
        mock_agent_pod_list = Mock()
        mock_agent_pod_list.items = [mock_aks_agent_pod]

        mock_mcp_pod_list = Mock()
        mock_mcp_pod_list.items = [mock_aks_mcp_pod]

        mock_api_instance = Mock()
        # Return different pod lists for each call (agent pods, then mcp pods)
        mock_api_instance.list_namespaced_pod.side_effect = [mock_agent_pod_list, mock_mcp_pod_list]
        mock_core_api.return_value = mock_api_instance

        manager = AKSAgentManager()
        success, result = manager.get_agent_pods()

        self.assertTrue(success)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn("aks-agent-pod-1", result)
        self.assertIn("aks-mcp-pod-1", result)

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.client.CoreV1Api')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.config.load_kube_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_get_agent_pods_no_pods(self, mock_helm_manager, mock_load_config, mock_load_kube, mock_core_api):
        """Test getting agent pods when no pods exist."""
        mock_pod_list = Mock()
        mock_pod_list.items = []

        mock_api_instance = Mock()
        mock_api_instance.list_namespaced_pod.return_value = mock_pod_list
        mock_core_api.return_value = mock_api_instance

        manager = AKSAgentManager()
        success, result = manager.get_agent_pods()

        self.assertFalse(success)
        self.assertIsInstance(result, str)
        self.assertIn("No pods found", result)

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._init_k8s_client')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_check_llm_config_exists_true(self, mock_helm_manager, mock_load_config, mock_init_client):
        """Test checking if LLM config exists - returns True when both secret and model_list exist."""
        manager = AKSAgentManager()

        # Mock the core_v1 API
        mock_secret = Mock()
        manager.core_v1 = Mock()
        manager.core_v1.read_namespaced_secret.return_value = mock_secret

        # Set model_list to non-empty dict
        manager.llm_config_manager.model_list = {"model1": {"provider": "openai"}}

        result = manager.check_llm_config_exists()
        self.assertTrue(result)

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._init_k8s_client')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_check_llm_config_exists_false_empty_model_list(self, mock_helm_manager, mock_load_config, mock_init_client):
        """Test checking if LLM config exists - returns False when secret exists but model_list is empty."""
        manager = AKSAgentManager()

        # Mock the core_v1 API
        mock_secret = Mock()
        manager.core_v1 = Mock()
        manager.core_v1.read_namespaced_secret.return_value = mock_secret

        # Set model_list to empty dict
        manager.llm_config_manager.model_list = {}

        result = manager.check_llm_config_exists()
        self.assertFalse(result)

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._init_k8s_client')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_check_llm_config_exists_false_404(self, mock_helm_manager, mock_load_config, mock_init_client):
        """Test checking if LLM config exists - returns False for 404."""
        manager = AKSAgentManager()

        # Mock the core_v1 API to raise ApiException with 404
        manager.core_v1 = Mock()
        manager.core_v1.read_namespaced_secret.side_effect = ApiException(status=404)

        result = manager.check_llm_config_exists()
        self.assertFalse(result)

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._init_k8s_client')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_check_llm_config_exists_raises_azcli_error(self, mock_helm_manager, mock_load_config, mock_init_client):
        """Test checking if LLM config exists - raises AzCLIError for unexpected errors."""
        from azure.cli.core.azclierror import AzCLIError

        manager = AKSAgentManager()

        # Mock the core_v1 API to raise a generic exception
        manager.core_v1 = Mock()
        manager.core_v1.read_namespaced_secret.side_effect = ValueError("Unexpected error")

        with self.assertRaises(AzCLIError) as context:
            manager.check_llm_config_exists()

        self.assertIn("Failed to check LLM config existence", str(context.exception))

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._run_helm_command')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._init_k8s_client')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_deploy_agent_success(self, mock_helm_manager, mock_load_config, mock_init_client, mock_helm_cmd):
        """Test successful agent deployment."""
        mock_helm_cmd.return_value = (True, "deployed successfully")

        manager = AKSAgentManager()
        success, error_msg = manager.deploy_agent()

        self.assertTrue(success)
        self.assertEqual(error_msg, "")
        mock_helm_cmd.assert_called()

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._run_helm_command')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._init_k8s_client')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_deploy_agent_failure(self, mock_helm_manager, mock_load_config, mock_init_client, mock_helm_cmd):
        """Test agent deployment failure returns False and error message."""
        mock_helm_cmd.return_value = (False, "deployment failed")

        manager = AKSAgentManager()
        success, error_msg = manager.deploy_agent()

        self.assertFalse(success)
        self.assertIn("deployment failed", error_msg)

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._run_helm_command')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._init_k8s_client')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_uninstall_agent_success_with_secret_deletion(self, mock_helm_manager, mock_load_config,
                                                          mock_init_client, mock_helm_cmd):
        """Test successful agent uninstallation with secret deletion."""
        mock_helm_cmd.return_value = (True, "uninstalled successfully")

        manager = AKSAgentManager()
        manager.delete_llm_config_secret = Mock()

        result = manager.uninstall_agent(delete_secret=True)

        self.assertTrue(result)
        manager.delete_llm_config_secret.assert_called_once()

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._run_helm_command')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._init_k8s_client')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_uninstall_agent_success_without_secret_deletion(self, mock_helm_manager, mock_load_config,
                                                             mock_init_client, mock_helm_cmd):
        """Test successful agent uninstallation without secret deletion."""
        mock_helm_cmd.return_value = (True, "uninstalled successfully")

        manager = AKSAgentManager()
        manager.delete_llm_config_secret = Mock()

        result = manager.uninstall_agent(delete_secret=False)

        self.assertTrue(result)
        manager.delete_llm_config_secret.assert_not_called()

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._init_k8s_client')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_create_llm_config_secret(self, mock_helm_manager, mock_load_config, mock_init_client):
        """Test creating LLM config secret."""
        manager = AKSAgentManager()
        manager.core_v1 = Mock()
        manager.llm_config_manager = Mock()
        manager.llm_config_manager.get_llm_model_secret_data.return_value = {"API_KEY": "encoded"}
        manager.llm_config_manager.get_env_vars.return_value = []

        # Mock existing secret check
        manager.core_v1.read_namespaced_secret.side_effect = ApiException(status=404)
        manager.core_v1.create_namespaced_secret.return_value = Mock()

        manager.create_llm_config_secret()

        manager.core_v1.create_namespaced_secret.assert_called_once()

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._init_k8s_client')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_delete_llm_config_secret(self, mock_helm_manager, mock_load_config, mock_init_client):
        """Test deleting LLM config secret."""
        manager = AKSAgentManager()
        manager.core_v1 = Mock()
        manager.core_v1.delete_namespaced_secret.return_value = Mock()

        manager.delete_llm_config_secret()

        manager.core_v1.delete_namespaced_secret.assert_called_once()

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._init_k8s_client')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_get_default_cluster_role(self, mock_helm_manager, mock_load_config, mock_init_client):
        """Test getting default cluster role."""
        manager = AKSAgentManager()

        cluster_role = manager.get_default_cluster_role()

        self.assertIsNotNone(cluster_role)
        self.assertEqual(cluster_role.metadata.name, "aks-agent-aks-mcp")
        self.assertIsNotNone(cluster_role.rules)
        self.assertGreater(len(cluster_role.rules), 0)

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._run_helm_command')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._init_k8s_client')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_get_agent_status(self, mock_helm_manager, mock_load_config, mock_init_client, mock_helm_cmd):
        """Test getting agent status."""
        import json

        # Mock helm commands
        mock_helm_cmd.side_effect = [
            (True, json.dumps([{"name": "aks-agent", "status": "deployed"}])),
            (True, json.dumps({"info": {"status": "deployed"}}))
        ]

        manager = AKSAgentManager()
        manager.core_v1 = Mock()
        manager.apps_v1 = Mock()

        # Helper to create mock deployment
        def create_deployment(name):
            mock_dep = Mock()
            mock_dep.metadata.name = name
            mock_dep.status.replicas = mock_dep.status.ready_replicas = 1
            mock_dep.status.updated_replicas = mock_dep.status.available_replicas = 1
            return mock_dep

        # Helper to create mock pod
        def create_pod(name):
            mock_pod = Mock()
            mock_pod.metadata.name = name
            mock_pod.status.phase = "Running"
            mock_pod.status.conditions = [Mock(type="Ready", status="True")]
            return mock_pod

        # Mock deployments and pods
        manager.apps_v1.list_namespaced_deployment.side_effect = [
            Mock(items=[create_deployment("aks-agent-deployment")]),
            Mock(items=[create_deployment("aks-mcp-deployment")])
        ]
        manager.core_v1.list_namespaced_pod.side_effect = [
            Mock(items=[create_pod("aks-agent-pod-1")]),
            Mock(items=[create_pod("aks-mcp-pod-1")])
        ]

        status = manager.get_agent_status()

        self.assertIsNotNone(status)
        self.assertIn("helm_status", status)
        self.assertEqual(len(status["deployments"]), 2)
        self.assertEqual(len(status["pods"]), 2)


if __name__ == '__main__':
    unittest.main()
