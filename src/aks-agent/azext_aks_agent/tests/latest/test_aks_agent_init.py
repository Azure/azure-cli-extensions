# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import types
import unittest
from unittest.mock import MagicMock, patch

from azext_aks_agent.custom import aks_agent_init
from azure.cli.core.azclierror import AzCLIError

mock_logging = MagicMock(name="init_logging")
mock_console_mod = types.SimpleNamespace(logging=types.SimpleNamespace(init_logging=mock_logging))

mock_holmes = types.SimpleNamespace(
    interactive=types.SimpleNamespace(
        SlashCommands=MagicMock()
    ),
    utils=types.SimpleNamespace(
        colors=types.SimpleNamespace(
            ERROR_COLOR=MagicMock(),
            HELP_COLOR=MagicMock(),
        ),
        console=mock_console_mod,
    )
)

mock_rich = types.SimpleNamespace(
    console=types.SimpleNamespace(
        Console=MagicMock()
    )
)


class TestAksAgentInit(unittest.TestCase):

    def setUp(self):
        patcher = patch.dict(
            'sys.modules',
            {
                'holmes': mock_holmes,
                'holmes.interactive': mock_holmes.interactive,
                'holmes.utils': mock_holmes.utils,
                'holmes.utils.colors': mock_holmes.utils.colors,
                'holmes.utils.console': mock_holmes.utils.console,
                'holmes.utils.console.logging': mock_holmes.utils.console.logging,
                'rich': mock_rich,
                'rich.console': mock_rich.console,
            }
        )
        self.addCleanup(patcher.stop)
        patcher.start()

    @patch('holmes.interactive.SlashCommands')
    @patch('holmes.utils.colors.ERROR_COLOR')
    @patch('holmes.utils.colors.HELP_COLOR')
    @patch('rich.console.Console')
    @patch('azext_aks_agent.custom.prompt_provider_choice')
    @patch('azext_aks_agent.custom.LLMConfigManager')
    def test_init_successful_save(
        self,
        mock_config_manager_cls,
        mock_prompt_provider_choice,
        mock_console_cls,
        mock_help_color,
        mock_error_color,
        mock_slash_commands
    ):
        mock_console = MagicMock()
        mock_console_cls.return_value = mock_console

        mock_provider = MagicMock()
        mock_provider.prompt_params.return_value = {'MODEL_NAME': 'test-model', 'param': 'value'}
        mock_provider.validate_connection.return_value = (True, 'Valid', 'save')
        mock_provider.name = 'openai'
        mock_provider.model_route = 'openai'
        mock_prompt_provider_choice.return_value = mock_provider

        mock_config_manager = MagicMock()
        mock_config_manager_cls.return_value = mock_config_manager

        mock_help_color.__str__.return_value = "green"
        mock_error_color.__str__.return_value = "red"
        mock_slash_commands.EXIT.command = "exit"

        aks_agent_init(cmd=None)
        mock_config_manager.save.assert_called_once_with('openai', {'MODEL_NAME': 'test-model', 'param': 'value'})

    @patch('holmes.interactive.SlashCommands')
    @patch('holmes.utils.colors.ERROR_COLOR')
    @patch('holmes.utils.colors.HELP_COLOR')
    @patch('rich.console.Console')
    @patch('azext_aks_agent.custom.prompt_provider_choice')
    @patch('azext_aks_agent.custom.LLMConfigManager')
    def test_init_retry_input(
        self,
        mock_config_manager_cls,
        mock_prompt_provider_choice,
        mock_console_cls,
        mock_help_color,
        mock_error_color,
        mock_slash_commands
    ):
        mock_console = MagicMock()
        mock_console_cls.return_value = mock_console

        mock_provider = MagicMock()
        mock_provider.prompt_params.return_value = {'MODEL_NAME': 'test-model'}
        mock_provider.validate_connection.return_value = (False, 'Invalid input', 'retry_input')
        mock_provider.name = 'openai'
        mock_prompt_provider_choice.return_value = mock_provider

        mock_config_manager_cls.return_value = MagicMock()

        mock_help_color.__str__.return_value = "green"
        mock_error_color.__str__.return_value = "red"
        mock_slash_commands.EXIT.command = "exit"

        with self.assertRaises(AzCLIError) as cm:
            aks_agent_init(cmd=None)
        self.assertEqual(str(cm.exception), "Please re-run `az aks agent-init` to correct the input parameters.")

    @patch('holmes.interactive.SlashCommands')
    @patch('holmes.utils.colors.ERROR_COLOR')
    @patch('holmes.utils.colors.HELP_COLOR')
    @patch('rich.console.Console')
    @patch('azext_aks_agent.custom.prompt_provider_choice')
    @patch('azext_aks_agent.custom.LLMConfigManager')
    def test_init_connection_error(
        self,
        mock_config_manager_cls,
        mock_prompt_provider_choice,
        mock_console_cls,
        mock_help_color,
        mock_error_color,
        mock_slash_commands
    ):
        mock_console = MagicMock()
        mock_console_cls.return_value = mock_console

        mock_provider = MagicMock()
        mock_provider.prompt_params.return_value = {'MODEL_NAME': 'test-model'}
        mock_provider.validate_connection.return_value = (False, 'Connection failed', 'other')
        mock_provider.name = 'openai'
        mock_prompt_provider_choice.return_value = mock_provider

        mock_config_manager_cls.return_value = MagicMock()

        mock_help_color.__str__.return_value = "green"
        mock_error_color.__str__.return_value = "red"
        mock_slash_commands.EXIT.command = "exit"

        with self.assertRaises(AzCLIError) as cm:
            aks_agent_init(cmd=None)
        self.assertEqual(str(cm.exception), "Please check your deployed model and network connectivity.")


if __name__ == '__main__':
    unittest.main()
