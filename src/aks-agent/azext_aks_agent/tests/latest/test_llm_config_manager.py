# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Unit tests for LLMConfigManager.
"""

import unittest
from unittest.mock import MagicMock, Mock, patch

from azext_aks_agent.agent.llm_config_manager import LLMConfigManager
from azure.cli.core.azclierror import AzCLIError


class TestLLMConfigManager(unittest.TestCase):
    """Test cases for LLMConfigManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = LLMConfigManager()
        self.test_model_config = {
            "provider": "azure",
            "model": "gpt-4",
            "api_key": "test-key",
            "api_base": "https://test.openai.azure.com",
            "api_version": "2023-05-15",
            "DEPLOYMENT_NAME": "gpt-4-deployment",
            "MODEL_NAME": "gpt-4"
        }

    def test_init_empty(self):
        """Test LLMConfigManager initialization with no models."""
        manager = LLMConfigManager()
        self.assertIsNotNone(manager.model_list)
        self.assertEqual(len(manager.model_list), 0)

    def test_init_with_models(self):
        """Test LLMConfigManager initialization with existing models."""
        models = {"azure/gpt-4": self.test_model_config}
        manager = LLMConfigManager(model_list=models)
        self.assertEqual(len(manager.model_list), 1)
        self.assertIn("azure/gpt-4", manager.model_list)

    def test_save_model_config(self):
        """Test saving model configuration."""
        mock_provider = Mock()
        mock_provider.model_name.return_value = "azure/gpt-4"

        params = {
            "model": "gpt-4",
            "api_key": "test-key"
        }

        self.manager.save(mock_provider, params)

        self.assertEqual(len(self.manager.model_list), 1)
        self.assertIn("azure/gpt-4", self.manager.model_list)
        self.assertEqual(self.manager.model_list["azure/gpt-4"]["model"], "azure/gpt-4")

    @patch('azext_aks_agent.agent.llm_config_manager.LLMProvider.to_k8s_secret_data')
    def test_get_llm_model_secret_data(self, mock_to_secret):
        """Test generating Kubernetes secret data."""
        mock_to_secret.return_value = {"API_KEY": "encoded-key"}
        self.manager.model_list = {
            "azure/gpt-4": self.test_model_config
        }

        result = self.manager.get_llm_model_secret_data()

        self.assertIsNotNone(result)
        mock_to_secret.assert_called_once()

    @patch('azext_aks_agent.agent.llm_config_manager.LLMProvider.to_env_vars')
    def test_get_env_vars(self, mock_to_env):
        """Test generating environment variables."""
        mock_to_env.return_value = [{"name": "API_KEY", "valueFrom": {"secretKeyRef": {"name": "test-secret"}}}]
        self.manager.model_list = {
            "azure/gpt-4": self.test_model_config
        }

        result = self.manager.get_env_vars("test-secret")

        self.assertIsNotNone(result)
        mock_to_env.assert_called_once()


if __name__ == '__main__':
    unittest.main()
