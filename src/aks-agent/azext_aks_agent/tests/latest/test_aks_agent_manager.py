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
        self.assertEqual(manager.helm_release_name, "aks-agent")
        self.assertIsNotNone(manager.llm_config_manager)
        mock_init_client.assert_called_once()
        mock_load_config.assert_called_once()

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

        manager = AKSAgentManager(
            resource_group_name=self.resource_group,
            cluster_name=self.cluster_name,
            subscription_id=self.subscription_id
        )
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

        manager = AKSAgentManager(
            resource_group_name=self.resource_group,
            cluster_name=self.cluster_name,
            subscription_id=self.subscription_id
        )
        success, result = manager.get_agent_pods()

        self.assertFalse(success)
        self.assertIsInstance(result, str)
        self.assertIn("No pods found", result)

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._init_k8s_client')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_get_llm_config_empty(self, mock_helm_manager, mock_load_config, mock_init_client):
        """Test getting LLM config when secret doesn't exist."""
        manager = AKSAgentManager(
            resource_group_name=self.resource_group,
            cluster_name=self.cluster_name,
            subscription_id=self.subscription_id
        )

        # Mock the core_v1 API to raise ApiException with 404 (secret not found)
        manager.core_v1 = Mock()
        manager.core_v1.read_namespaced_secret.side_effect = ApiException(status=404)

        result = manager.get_llm_config()
        self.assertEqual(result, {})

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._init_k8s_client')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_get_llm_config_with_models(self, mock_helm_manager, mock_load_config, mock_init_client):
        """Test getting LLM config when models exist."""
        manager = AKSAgentManager(
            resource_group_name=self.resource_group,
            cluster_name=self.cluster_name,
            subscription_id=self.subscription_id
        )

        # Set model_list with test data
        test_models = {"model1": {"provider": "openai"}}
        manager.llm_config_manager.model_list = test_models

        # Mock the core_v1 API to return a secret (secret exists)
        mock_secret = Mock()
        manager.core_v1 = Mock()
        manager.core_v1.read_namespaced_secret.return_value = mock_secret

        result = manager.get_llm_config()
        self.assertEqual(result, test_models)

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._run_helm_command')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._init_k8s_client')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_deploy_agent_success(self, mock_helm_manager, mock_load_config, mock_init_client, mock_helm_cmd):
        """Test successful agent deployment."""
        mock_helm_cmd.return_value = (True, "deployed successfully")

        manager = AKSAgentManager(
            resource_group_name=self.resource_group,
            cluster_name=self.cluster_name,
            subscription_id=self.subscription_id
        )
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

        manager = AKSAgentManager(
            resource_group_name=self.resource_group,
            cluster_name=self.cluster_name,
            subscription_id=self.subscription_id
        )
        success, error_msg = manager.deploy_agent()

        self.assertFalse(success)
        self.assertIn("deployment failed", error_msg)

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._run_helm_command')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._init_k8s_client')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_uninstall_agent_success(self, mock_helm_manager, mock_load_config,
                                     mock_init_client, mock_helm_cmd):
        """Test successful agent uninstallation."""
        mock_helm_cmd.return_value = (True, "uninstalled successfully")

        manager = AKSAgentManager(
            resource_group_name=self.resource_group,
            cluster_name=self.cluster_name,
            subscription_id=self.subscription_id
        )

        result = manager.uninstall_agent()

        self.assertTrue(result)

    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._init_k8s_client')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.AKSAgentManager._load_existing_helm_release_config')
    @patch('azext_aks_agent.agent.k8s.aks_agent_manager.HelmManager')
    def test_save_llm_config(self, mock_helm_manager, mock_load_config, mock_init_client):
        """Test saving LLM configuration."""
        from azext_aks_agent.agent.llm_providers import LLMProvider

        manager = AKSAgentManager(
            resource_group_name=self.resource_group,
            cluster_name=self.cluster_name,
            subscription_id=self.subscription_id
        )

        mock_provider = Mock(spec=LLMProvider)
        mock_provider.name = "openai"
        test_params = {"api_key": "test-key", "model": "gpt-4"}

        # Mock the llm_config_manager.save method and create_llm_config_secret
        manager.llm_config_manager.save = Mock()
        manager.create_llm_config_secret = Mock()

        manager.save_llm_config(mock_provider, test_params)

        manager.llm_config_manager.save.assert_called_once_with(mock_provider, test_params)
        manager.create_llm_config_secret.assert_called_once()

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

        manager = AKSAgentManager(
            resource_group_name=self.resource_group,
            cluster_name=self.cluster_name,
            subscription_id=self.subscription_id
        )
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
