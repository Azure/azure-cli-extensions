# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, call, patch

from azext_aks_preview._consts import (CONST_AGENT_CONFIG_PATH_DIR_ENV_KEY,
                                       CONST_AGENT_NAME,
                                       CONST_AGENT_NAME_ENV_KEY)
from azext_aks_preview.agent.agent import aks_agent, init_log
from azure.cli.core.util import CLIError

# Mock the holmes modules before any imports that might trigger holmes imports
sys.modules['holmes'] = Mock()
sys.modules['holmes.config'] = Mock()
sys.modules['holmes.core'] = Mock()
sys.modules['holmes.core.prompt'] = Mock()
sys.modules['holmes.interactive'] = Mock()
sys.modules['holmes.plugins'] = Mock()
sys.modules['holmes.plugins.destinations'] = Mock()
sys.modules['holmes.plugins.interfaces'] = Mock()
sys.modules['holmes.plugins.prompts'] = Mock()
sys.modules['holmes.utils'] = Mock()
sys.modules['holmes.utils.console'] = Mock()
sys.modules['holmes.utils.console.logging'] = Mock()
sys.modules['holmes.utils.console.result'] = Mock()


def setUpModule():
    # Skip all tests in this module for Python versions below 3.10
    if sys.version_info < (3, 10):
        raise unittest.SkipTest("Tests in this module require Python >= 3.10")


class TestInitLog(unittest.TestCase):
    """Test cases for init_log function"""

    @patch('azext_aks_preview.agent.agent.logging.getLogger')
    @patch('holmes.utils.console.logging.init_logging')
    def test_init_log_sets_log_levels_and_calls_init_logging(self, mock_init_logging, mock_get_logger):
        """Test that init_log sets appropriate log levels and calls init_logging"""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_console = Mock()
        mock_init_logging.return_value = mock_console

        # Act
        result = init_log()

        # Assert
        self.assertEqual(result, mock_console)

        # Verify all loggers are set to WARNING level
        expected_logger_calls = [
            call("LiteLLM"),
            call("telemetry.main"),
            call("telemetry.process"),
            call("telemetry.save"),
            call("telemetry.client"),
            call("az_command_data_logger"),
        ]
        mock_get_logger.assert_has_calls(expected_logger_calls, any_order=True)

        # Verify setLevel is called with WARNING for each logger
        expected_setlevel_calls = [call(logging.WARNING)] * 6
        mock_logger.setLevel.assert_has_calls(expected_setlevel_calls)

        # Verify init_logging is called with empty list
        mock_init_logging.assert_called_once_with([])

    @patch('azext_aks_preview.agent.agent.logging.getLogger')
    def test_init_log_logger_level_setting(self, mock_get_logger):
        """Test that specific loggers get WARNING level set"""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        with patch('holmes.utils.console.logging.init_logging') as mock_init_logging:
            mock_init_logging.return_value = Mock()

            # Act
            init_log()

            # Assert that setLevel was called 6 times with WARNING
            self.assertEqual(mock_logger.setLevel.call_count, 6)
            for call_args in mock_logger.setLevel.call_args_list:
                self.assertEqual(call_args[0][0], logging.WARNING)


class TestAksAgent(unittest.TestCase):
    """Test cases for aks_agent function"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_cmd = Mock()
        self.mock_cmd.cli_ctx = Mock()
        # Fix the cli_ctx.data structure to be subscriptable
        self.mock_cmd.cli_ctx.data = {'subscription_id': 'test-subscription-id'}

        # Default parameters for aks_agent function
        self.default_params = {
            'cmd': self.mock_cmd,
            'resource_group_name': 'test-rg',
            'name': 'test-cluster',
            'prompt': 'test prompt',
            'model': 'test-model',
            'api_key': 'test-key',
            'max_steps': 10,
            'config_file': '/path/to/config.yaml',
            'no_interactive': False,
            'no_echo_request': False,
            'show_tool_output': True,
            'refresh_toolsets': False,
        }

    def test_aks_agent_python_version_check(self):
        """Test that aks_agent raises error for Python version < 3.10"""
        with patch.object(sys, 'version_info', (3, 9, 0)):
            with patch('azext_aks_preview.agent.agent.CLITelemetryClient'):
                with self.assertRaises(CLIError) as cm:
                    aks_agent(**self.default_params)

                self.assertIn("Please upgrade the python version to 3.10", str(cm.exception))

    @patch('sys.stdin.isatty')
    @patch('azext_aks_preview.agent.agent.CLITelemetryClient')
    @patch('azext_aks_preview.agent.agent.init_log')
    @patch('azure.cli.core.api.get_config_dir')
    @patch('azure.cli.core.commands.client_factory.get_subscription_id')
    @patch('pathlib.Path')
    def test_aks_agent_no_prompt_no_interactive_raises_error(self, mock_path, mock_get_subscription_id,
                                                             mock_get_config_dir, mock_init_log,
                                                             mock_cli_telemetry, mock_stdin_isatty):
        """Test that aks_agent raises error when no prompt and not interactive mode"""
        # Arrange
        mock_stdin_isatty.return_value = True  # No piped input
        mock_console = Mock()
        mock_init_log.return_value = mock_console
        mock_get_config_dir.return_value = "/home/user/.azure"
        mock_get_subscription_id.return_value = "test-subscription"

        mock_config_path = Mock()
        mock_path.return_value = mock_config_path

        with patch.dict(os.environ, {}, clear=True):
            with patch('holmes.config.Config') as mock_config_class:
                mock_config = Mock()
                mock_config_class.load_from_file.return_value = mock_config
                mock_ai = Mock()
                mock_config.create_console_toolcalling_llm.return_value = mock_ai

                # Act & Assert
                params = self.default_params.copy()
                params['prompt'] = None
                params['no_interactive'] = True  # Not interactive

                with self.assertRaises(CLIError) as cm:
                    aks_agent(**params)

                self.assertIn("Either the 'prompt' argument must be provided", str(cm.exception))

    @patch('sys.stdin.isatty')
    @patch('azext_aks_preview.agent.agent.CLITelemetryClient')
    @patch('azext_aks_preview.agent.agent.init_log')
    @patch('azure.cli.core.api.get_config_dir')
    @patch('azure.cli.core.commands.client_factory.get_subscription_id')
    @patch('pathlib.Path')
    def test_aks_agent_interactive_mode(self, mock_path, mock_get_subscription_id, mock_get_config_dir,
                                        mock_init_log, mock_cli_telemetry, mock_stdin_isatty):
        """Test aks_agent in interactive mode"""
        # Arrange
        mock_stdin_isatty.return_value = True
        mock_console = Mock()
        mock_init_log.return_value = mock_console
        mock_get_config_dir.return_value = "/home/user/.azure"
        mock_get_subscription_id.return_value = "test-subscription"

        mock_config_path = Mock()
        mock_path.return_value = mock_config_path

        with patch.dict(os.environ, {}, clear=True):
            with patch('holmes.config.Config') as mock_config_class:
                mock_config = Mock()
                mock_config_class.load_from_file.return_value = mock_config
                mock_ai = Mock()
                mock_config.create_console_toolcalling_llm.return_value = mock_ai

                with patch('holmes.interactive.run_interactive_loop') as mock_run_interactive:
                    with patch('holmes.plugins.prompts.load_and_render_prompt') as mock_load_prompt:
                        mock_load_prompt.return_value = "AKS context"

                        # Act
                        params = self.default_params.copy()
                        params['no_interactive'] = False  # Interactive mode
                        aks_agent(**params)

                # Assert
                mock_run_interactive.assert_called_once()

                # Verify interactive loop is called with correct parameters
                call_args = mock_run_interactive.call_args
                self.assertEqual(call_args[0][0], mock_ai)  # ai parameter
                self.assertEqual(call_args[0][1], mock_console)  # console parameter
                self.assertEqual(call_args[0][2], 'test prompt')  # prompt parameter
                self.assertEqual(call_args[1]['show_tool_output'], True)
                self.assertEqual(call_args[1]['system_prompt_additions'], "AKS context")

    @patch('sys.stdin.isatty')
    @patch('azext_aks_preview.agent.agent.CLITelemetryClient')
    @patch('azext_aks_preview.agent.agent.init_log')
    @patch('azure.cli.core.api.get_config_dir')
    @patch('azure.cli.core.commands.client_factory.get_subscription_id')
    @patch('pathlib.Path')
    def test_aks_agent_non_interactive_mode(self, mock_path, mock_get_subscription_id, mock_get_config_dir,
                                            mock_init_log, mock_cli_telemetry, mock_stdin_isatty):
        """Test aks_agent in non-interactive mode"""
        # Arrange
        mock_stdin_isatty.return_value = True
        mock_console = Mock()
        mock_init_log.return_value = mock_console
        mock_get_config_dir.return_value = "/home/user/.azure"
        mock_get_subscription_id.return_value = "test-subscription"

        mock_config_path = Mock()
        mock_path.return_value = mock_config_path

        with patch.dict(os.environ, {}, clear=True):
            with patch('holmes.config.Config') as mock_config_class:
                mock_config = Mock()
                mock_config_class.load_from_file.return_value = mock_config
                mock_ai = Mock()
                mock_config.create_console_toolcalling_llm.return_value = mock_ai
                mock_config.get_runbook_catalog.return_value = {}

                with patch('holmes.core.prompt.build_initial_ask_messages') as mock_build_messages:
                    mock_messages = [{'role': 'user', 'content': 'test'}]
                    mock_build_messages.return_value = mock_messages

                    mock_response = Mock()
                    mock_response.messages = mock_messages
                    mock_ai.call.return_value = mock_response

                    with patch('holmes.utils.console.result.handle_result') as mock_handle_result:
                        with patch('holmes.plugins.prompts.load_and_render_prompt') as mock_load_prompt:
                            with patch('holmes.plugins.interfaces.Issue') as mock_issue:
                                with patch('uuid.uuid4') as mock_uuid:
                                    with patch('socket.gethostname') as mock_hostname:
                                        mock_load_prompt.return_value = "AKS context"
                                        mock_uuid.return_value = "test-uuid"
                                        mock_hostname.return_value = "test-host"
                                        mock_issue_instance = Mock()
                                        mock_issue.return_value = mock_issue_instance

                                        # Act
                                        params = self.default_params.copy()
                                        params['no_interactive'] = True  # Non-interactive mode
                                        aks_agent(**params)

                # Assert
                mock_build_messages.assert_called_once()
                mock_ai.call.assert_called_once_with(mock_messages)
                mock_handle_result.assert_called_once()

                # Verify Issue is created with correct parameters
                mock_issue.assert_called_once()
                issue_kwargs = mock_issue.call_args[1]
                self.assertEqual(issue_kwargs['id'], "test-uuid")
                self.assertEqual(issue_kwargs['name'], 'test prompt')
                self.assertEqual(issue_kwargs['source_type'], "holmes-ask")
                self.assertEqual(issue_kwargs['source_instance_id'], "test-host")

    @patch('sys.stdin.isatty')
    @patch('sys.stdin.read')
    @patch('azext_aks_preview.agent.agent.CLITelemetryClient')
    @patch('azext_aks_preview.agent.agent.init_log')
    @patch('azure.cli.core.api.get_config_dir')
    @patch('azure.cli.core.commands.client_factory.get_subscription_id')
    @patch('pathlib.Path')
    def test_aks_agent_piped_input_with_prompt(self, mock_path, mock_get_subscription_id, mock_get_config_dir,
                                               mock_init_log, mock_cli_telemetry, mock_stdin_read, mock_stdin_isatty):
        """Test aks_agent combines piped input with provided prompt"""
        # Arrange
        mock_stdin_isatty.return_value = False
        mock_stdin_read.return_value = "kubectl get pods output"
        mock_console = Mock()
        mock_init_log.return_value = mock_console
        mock_get_config_dir.return_value = "/home/user/.azure"
        mock_get_subscription_id.return_value = "test-subscription"

        mock_config_path = Mock()
        mock_path.return_value = mock_config_path

        with patch.dict(os.environ, {}, clear=True):
            with patch('holmes.config.Config') as mock_config_class:
                mock_config = Mock()
                mock_config_class.load_from_file.return_value = mock_config
                mock_ai = Mock()
                mock_config.create_console_toolcalling_llm.return_value = mock_ai
                mock_config.get_runbook_catalog.return_value = {}

                with patch('holmes.core.prompt.build_initial_ask_messages') as mock_build_messages:
                    mock_messages = [{'role': 'user', 'content': 'test'}]
                    mock_build_messages.return_value = mock_messages

                    mock_response = Mock()
                    mock_response.messages = mock_messages
                    mock_ai.call.return_value = mock_response

                    with patch('holmes.utils.console.result.handle_result'):
                        with patch('holmes.plugins.prompts.load_and_render_prompt') as mock_load_prompt:
                            with patch('holmes.plugins.interfaces.Issue'):
                                with patch('uuid.uuid4'):
                                    with patch('socket.gethostname'):
                                        mock_load_prompt.return_value = "AKS context"

                                        # Act
                                        params = self.default_params.copy()
                                        params['prompt'] = "What's wrong with my pods?"
                                        aks_agent(**params)

                # Assert that build_initial_ask_messages was called with combined prompt
                mock_build_messages.assert_called_once()
                call_args = mock_build_messages.call_args[0]
                combined_prompt = call_args[1]  # prompt parameter

                self.assertIn("kubectl get pods output", combined_prompt)
                self.assertIn("What's wrong with my pods?", combined_prompt)
                self.assertIn("Here's some piped output:", combined_prompt)

    @patch('sys.stdin.isatty')
    @patch('azext_aks_preview.agent.agent.CLITelemetryClient')
    @patch('azext_aks_preview.agent.agent.init_log')
    @patch('azure.cli.core.api.get_config_dir')
    @patch('azure.cli.core.commands.client_factory.get_subscription_id')
    @patch('pathlib.Path')
    def test_aks_agent_echo_request_enabled(self, mock_path, mock_get_subscription_id, mock_get_config_dir,
                                            mock_init_log, mock_cli_telemetry, mock_stdin_isatty):
        """Test aks_agent echoes request when echo is enabled"""
        # Arrange
        mock_stdin_isatty.return_value = True
        mock_console = Mock()
        mock_init_log.return_value = mock_console
        mock_get_config_dir.return_value = "/home/user/.azure"
        mock_get_subscription_id.return_value = "test-subscription"

        mock_config_path = Mock()
        mock_path.return_value = mock_config_path

        with patch.dict(os.environ, {}, clear=True):
            with patch('holmes.config.Config') as mock_config_class:
                mock_config = Mock()
                mock_config_class.load_from_file.return_value = mock_config
                mock_ai = Mock()
                mock_config.create_console_toolcalling_llm.return_value = mock_ai
                mock_config.get_runbook_catalog.return_value = {}

                with patch('holmes.core.prompt.build_initial_ask_messages') as mock_build_messages:
                    mock_messages = [{'role': 'user', 'content': 'test'}]
                    mock_build_messages.return_value = mock_messages

                    mock_response = Mock()
                    mock_response.messages = mock_messages
                    mock_ai.call.return_value = mock_response

                    with patch('holmes.utils.console.result.handle_result'):
                        with patch('holmes.plugins.prompts.load_and_render_prompt') as mock_load_prompt:
                            with patch('holmes.plugins.interfaces.Issue'):
                                with patch('uuid.uuid4'):
                                    with patch('socket.gethostname'):
                                        mock_load_prompt.return_value = "AKS context"

                                        # Act
                                        params = self.default_params.copy()
                                        params['no_interactive'] = True  # Non-interactive
                                        params['no_echo_request'] = False  # Echo enabled
                                        aks_agent(**params)

                # Assert that console.print was called with the user prompt
                mock_console.print.assert_any_call("[bold yellow]User:[/bold yellow] test prompt")

    @patch('azext_aks_preview.agent.agent.CLITelemetryClient')
    def test_aks_agent_telemetry_client_usage(self, mock_cli_telemetry):
        """Test that aks_agent uses CLITelemetryClient context manager"""
        # Arrange
        mock_cli_telemetry.return_value.__enter__ = Mock(return_value=Mock())
        mock_cli_telemetry.return_value.__exit__ = Mock(return_value=None)

        with patch.object(sys, 'version_info', (3, 9, 0)):
            # Act & Assert
            with self.assertRaises(CLIError):
                aks_agent(**self.default_params)

        # Verify CLITelemetryClient was used as context manager
        mock_cli_telemetry.assert_called_once()
        mock_cli_telemetry.return_value.__enter__.assert_called_once()
        mock_cli_telemetry.return_value.__exit__.assert_called_once()

    @patch('sys.stdin.isatty')
    @patch('sys.stdin.read')
    @patch('azext_aks_preview.agent.agent.CLITelemetryClient')
    @patch('azext_aks_preview.agent.agent.init_log')
    @patch('azure.cli.core.api.get_config_dir')
    @patch('azure.cli.core.commands.client_factory.get_subscription_id')
    @patch('pathlib.Path')
    def test_aks_agent_piped_input_no_prompt_default_question(self, mock_path, mock_get_subscription_id,
                                                              mock_get_config_dir, mock_init_log, mock_cli_telemetry,
                                                              mock_stdin_read, mock_stdin_isatty):
        """Test aks_agent with piped input but no prompt uses default question"""
        # Arrange
        mock_stdin_isatty.return_value = False
        mock_stdin_read.return_value = "error logs from pod"
        mock_console = Mock()
        mock_init_log.return_value = mock_console
        mock_get_config_dir.return_value = "/home/user/.azure"
        mock_get_subscription_id.return_value = "test-subscription"

        mock_config_path = Mock()
        mock_path.return_value = mock_config_path

        with patch.dict(os.environ, {}, clear=True):
            with patch('holmes.config.Config') as mock_config_class:
                mock_config = Mock()
                mock_config_class.load_from_file.return_value = mock_config
                mock_ai = Mock()
                mock_config.create_console_toolcalling_llm.return_value = mock_ai
                mock_config.get_runbook_catalog.return_value = {}

                with patch('holmes.core.prompt.build_initial_ask_messages') as mock_build_messages:
                    mock_messages = [{'role': 'user', 'content': 'test'}]
                    mock_build_messages.return_value = mock_messages

                    mock_response = Mock()
                    mock_response.messages = mock_messages
                    mock_ai.call.return_value = mock_response

                    with patch('holmes.utils.console.result.handle_result'):
                        with patch('holmes.plugins.prompts.load_and_render_prompt') as mock_load_prompt:
                            with patch('holmes.plugins.interfaces.Issue'):
                                with patch('uuid.uuid4'):
                                    with patch('socket.gethostname'):
                                        mock_load_prompt.return_value = "AKS context"

                                        # Act
                                        params = self.default_params.copy()
                                        params['prompt'] = None  # No prompt provided
                                        aks_agent(**params)

                # Assert that build_initial_ask_messages was called with default question
                mock_build_messages.assert_called_once()
                call_args = mock_build_messages.call_args[0]
                prompt_with_default = call_args[1]  # prompt parameter

                self.assertIn("error logs from pod", prompt_with_default)
                self.assertIn("What can you tell me about this output?", prompt_with_default)


if __name__ == "__main__":
    unittest.main()
