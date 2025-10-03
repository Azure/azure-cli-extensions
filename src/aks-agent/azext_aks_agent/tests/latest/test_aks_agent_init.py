# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import patch, MagicMock
from azext_aks_agent.custom import aks_agent_init


class TestAksAgentInit(unittest.TestCase):
    @patch('azext_aks_agent.custom.prompt_provider_choice')
    @patch('azext_aks_agent.custom.LLMConfigManager')
    def test_init_successful_save(self, mock_config_manager_cls, mock_prompt_provider_choice):
        # Mock provider and config manager
        mock_provider = MagicMock()
        mock_provider.prompt_params.return_value = {'MODEL_NAME': 'test-model', 'param': 'value'}
        mock_provider.validate_connection.return_value = (True, 'Valid', 'save')
        mock_provider.name = 'openai'
        mock_prompt_provider_choice.return_value = mock_provider
        mock_config_manager = MagicMock()
        mock_config_manager.save.return_value = None
        mock_config_manager_cls.return_value = mock_config_manager

        # Should not raise
        aks_agent_init(cmd=None)
        mock_config_manager.save.assert_called_once_with('openai', {'MODEL_NAME': 'test-model', 'param': 'value'})

    @patch('azext_aks_agent.custom.prompt_provider_choice')
    @patch('azext_aks_agent.custom.LLMConfigManager')
    def test_init_retry_input(self, mock_config_manager_cls, mock_prompt_provider_choice):
        mock_provider = MagicMock()
        mock_provider.prompt_params.return_value = {'MODEL_NAME': 'test-model'}
        mock_provider.validate_connection.return_value = (False, 'Invalid input', 'retry_input')
        mock_provider.name = 'openai'
        mock_prompt_provider_choice.return_value = mock_provider
        mock_config_manager_cls.return_value = MagicMock()

        with self.assertRaises(ValueError) as cm:
            aks_agent_init(cmd=None)
        self.assertIn('Invalid input', str(cm.exception))

    @patch('azext_aks_agent.custom.prompt_provider_choice')
    @patch('azext_aks_agent.custom.LLMConfigManager')
    def test_init_connection_error(self, mock_config_manager_cls, mock_prompt_provider_choice):
        mock_provider = MagicMock()
        mock_provider.prompt_params.return_value = {'MODEL_NAME': 'test-model'}
        mock_provider.validate_connection.return_value = (False, 'Connection failed', 'other')
        mock_provider.name = 'openai'
        mock_prompt_provider_choice.return_value = mock_provider
        mock_config_manager_cls.return_value = MagicMock()

        with self.assertRaises(ConnectionError) as cm:
            aks_agent_init(cmd=None)
        self.assertIn('Connection failed', str(cm.exception))


if __name__ == '__main__':
    unittest.main()
