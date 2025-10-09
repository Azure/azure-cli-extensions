# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import patch, MagicMock
from azext_aks_agent.custom import aks_agent_init


class TestAksAgentInit(unittest.TestCase):
    @patch('rich.console.Console')
    @patch('azext_aks_agent.custom.prompt_provider_choice')
    @patch('azext_aks_agent.custom.LLMConfigManager')
    def test_init_successful_save(self, mock_config_manager_cls, mock_prompt_provider_choice, mock_console_cls):
        mock_console = MagicMock()
        mock_console_cls.return_value = mock_console

        mock_provider = MagicMock()
        mock_provider.prompt_params.return_value = {'MODEL_NAME': 'test-model', 'param': 'value'}
        mock_provider.validate_connection.return_value = (True, 'Valid', 'save')
        mock_provider.name = 'openai'
        mock_prompt_provider_choice.return_value = mock_provider

        mock_config_manager = MagicMock()
        mock_config_manager_cls.return_value = mock_config_manager

        aks_agent_init(cmd=None)
        mock_config_manager.save.assert_called_once_with('openai', {'MODEL_NAME': 'test-model', 'param': 'value'})
        mock_console.print.assert_any_call("LLM configuration setup successfully.", style=unittest.mock.ANY)

    @patch('rich.console.Console')
    @patch('azext_aks_agent.custom.prompt_provider_choice')
    @patch('azext_aks_agent.custom.LLMConfigManager')
    def test_init_retry_input(self, mock_config_manager_cls, mock_prompt_provider_choice, mock_console_cls):
        mock_console = MagicMock()
        mock_console_cls.return_value = mock_console

        mock_provider = MagicMock()
        mock_provider.prompt_params.return_value = {'MODEL_NAME': 'test-model'}
        mock_provider.validate_connection.return_value = (False, 'Invalid input', 'retry_input')
        mock_provider.name = 'openai'
        mock_prompt_provider_choice.return_value = mock_provider

        mock_config_manager_cls.return_value = MagicMock()

        with self.assertRaises(SystemExit) as cm:
            aks_agent_init(cmd=None)
        self.assertEqual(cm.exception.code, 1)
        mock_console.print.assert_any_call(
            "Please re-run [bold]`az aks agent-init`[/bold] to correct the input parameters.",
            style=unittest.mock.ANY,
        )

    @patch('rich.console.Console')
    @patch('azext_aks_agent.custom.prompt_provider_choice')
    @patch('azext_aks_agent.custom.LLMConfigManager')
    def test_init_connection_error(self, mock_config_manager_cls, mock_prompt_provider_choice, mock_console_cls):
        mock_console = MagicMock()
        mock_console_cls.return_value = mock_console

        mock_provider = MagicMock()
        mock_provider.prompt_params.return_value = {'MODEL_NAME': 'test-model'}
        mock_provider.validate_connection.return_value = (False, 'Connection failed', 'other')
        mock_provider.name = 'openai'
        mock_prompt_provider_choice.return_value = mock_provider

        mock_config_manager_cls.return_value = MagicMock()

        with self.assertRaises(SystemExit) as cm:
            aks_agent_init(cmd=None)
        self.assertEqual(cm.exception.code, 1)
        mock_console.print.assert_any_call(
            "Please check your deployed model and network connectivity.",
            style=unittest.mock.ANY,
        )


if __name__ == '__main__':
    unittest.main()
