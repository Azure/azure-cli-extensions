# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock, call
from azext_fleet.custom import _convert_kubeconfig_to_azurecli


# Test constants
KUBELOGIN_BINARY = 'kubelogin'
MOCK_KUBELOGIN_PATH = '/usr/local/bin with spaces/kubelogin'
KUBELOGIN_TIMEOUT = 60
KUBELOGIN_CMD_PREFIX = [MOCK_KUBELOGIN_PATH, "convert-kubeconfig", "-l", "azurecli", "--kubeconfig"]
KUBELOGIN_GITHUB_URL = "https://github.com/Azure/kubelogin"
KUBECONFIG_SUFFIX = '.kubeconfig'
STDOUT_PATH = '-'
CUSTOM_CONFIG_PATH = '/custom/path/to/config'


class TestKubeloginConversion(unittest.TestCase):
    """Test cases for kubelogin automatic conversion functionality."""

    def test_ignores_working_directory_executable(self):
        with tempfile.TemporaryDirectory() as directory:
            working = os.path.join(directory, 'working')
            tools = os.path.join(directory, 'installed tools')
            binary = 'kubelogin.exe' if os.name == 'nt' else 'kubelogin'
            for folder in (working, tools):
                os.mkdir(folder)
                executable = os.path.join(folder, binary)
                with open(executable, 'w'):
                    pass
                os.chmod(executable, 0o700)

            old_cwd = os.getcwd()
            try:
                os.chdir(working)
                for prefix in (None, '', '.', working):
                    for installed in (True, False):
                        search_path = [] if prefix is None else [prefix]
                        search_path.append(tools if installed else os.path.join(directory, 'missing'))
                        with (
                            self.subTest(prefix=prefix, installed=installed),
                            patch.dict(os.environ, {
                                'PATH': os.pathsep.join(search_path),
                                'PATHEXT': '.exe',
                                'SystemRoot': os.path.join(directory, 'system'),
                            }),
                            patch('azext_fleet.custom.subprocess.run') as run,
                            patch('azext_fleet.custom.logger') as logger,
                        ):
                            os.environ.pop('NoDefaultCurrentDirectoryInExePath', None)
                            config_path = os.path.join(directory, 'selected config')
                            _convert_kubeconfig_to_azurecli(config_path)

                            if installed:
                                run.assert_called_once_with(
                                    [os.path.join(tools, binary), 'convert-kubeconfig', '-l', 'azurecli',
                                     '--kubeconfig', config_path],
                                    check=True, capture_output=True, text=True, timeout=KUBELOGIN_TIMEOUT,
                                )
                            else:
                                run.assert_not_called()
                                self.assertIn('Please install kubelogin', logger.warning.call_args.args[0])
            finally:
                os.chdir(old_cwd)

    @patch('azext_fleet.custom.get_safe_executable_path')
    @patch('azext_fleet.custom.subprocess.run')
    @patch('azext_fleet.custom.logger')
    def test_convert_with_kubelogin_available(self, mock_logger, mock_subprocess, mock_which):
        """Test conversion when kubelogin is available."""
        mock_which.return_value = MOCK_KUBELOGIN_PATH
        mock_subprocess.return_value = MagicMock()

        with tempfile.NamedTemporaryFile(mode='w', suffix=KUBECONFIG_SUFFIX, delete=False) as f:
            test_path = f.name

        try:
            _convert_kubeconfig_to_azurecli(test_path)

            # Verify kubelogin was called with correct arguments
            mock_subprocess.assert_called_once()
            mock_which.assert_called_once_with(KUBELOGIN_BINARY)
            call_args = mock_subprocess.call_args
            self.assertEqual(call_args[0][0], KUBELOGIN_CMD_PREFIX + [test_path])
            self.assertTrue(call_args[1]['check'])
            self.assertEqual(call_args[1]['timeout'], KUBELOGIN_TIMEOUT)

            # Verify success message was logged
            mock_logger.warning.assert_called_with("Converted kubeconfig to use Azure CLI authentication.")
        finally:
            if os.path.exists(test_path):
                os.remove(test_path)

    @patch('azext_fleet.custom.get_safe_executable_path')
    @patch('azext_fleet.custom.logger')
    def test_convert_with_kubelogin_unavailable(self, mock_logger, mock_which):
        """Test conversion when kubelogin is not available."""
        mock_which.return_value = None

        with tempfile.NamedTemporaryFile(mode='w', suffix=KUBECONFIG_SUFFIX, delete=False) as f:
            test_path = f.name

        try:
            _convert_kubeconfig_to_azurecli(test_path)

            # Verify warning message was logged
            mock_logger.warning.assert_called_once()
            warning_msg = mock_logger.warning.call_args[0][0]
            self.assertIn("kubeconfig requires kubelogin", warning_msg)
            self.assertIn(KUBELOGIN_GITHUB_URL, warning_msg)
        finally:
            if os.path.exists(test_path):
                os.remove(test_path)

    @patch('azext_fleet.custom.get_safe_executable_path')
    @patch('azext_fleet.custom.subprocess.run')
    @patch('azext_fleet.custom.logger')
    def test_convert_handles_subprocess_error(self, mock_logger, mock_subprocess, mock_which):
        """Test that subprocess errors are handled gracefully."""
        mock_which.return_value = MOCK_KUBELOGIN_PATH
        from subprocess import CalledProcessError
        mock_subprocess.side_effect = CalledProcessError(1, KUBELOGIN_BINARY)

        with tempfile.NamedTemporaryFile(mode='w', suffix=KUBECONFIG_SUFFIX, delete=False) as f:
            test_path = f.name

        try:
            _convert_kubeconfig_to_azurecli(test_path)

            # Verify error was logged
            mock_logger.warning.assert_called_once()
            warning_msg = mock_logger.warning.call_args[0][0]
            self.assertIn("Failed to convert kubeconfig with kubelogin", warning_msg)
        finally:
            if os.path.exists(test_path):
                os.remove(test_path)

    @patch('azext_fleet.custom.get_safe_executable_path')
    @patch('azext_fleet.custom.subprocess.run')
    @patch('azext_fleet.custom.logger')
    def test_convert_handles_timeout(self, mock_logger, mock_subprocess, mock_which):
        """Test that timeout errors are handled gracefully."""
        mock_which.return_value = MOCK_KUBELOGIN_PATH
        from subprocess import TimeoutExpired
        mock_subprocess.side_effect = TimeoutExpired(KUBELOGIN_BINARY, KUBELOGIN_TIMEOUT)

        with tempfile.NamedTemporaryFile(mode='w', suffix=KUBECONFIG_SUFFIX, delete=False) as f:
            test_path = f.name

        try:
            _convert_kubeconfig_to_azurecli(test_path)

            # Verify timeout was logged
            mock_logger.warning.assert_called_once()
            warning_msg = mock_logger.warning.call_args[0][0]
            self.assertIn("kubelogin command timed out", warning_msg)
        finally:
            if os.path.exists(test_path):
                os.remove(test_path)

    @patch('azext_fleet.custom.get_safe_executable_path')
    @patch('azext_fleet.custom.subprocess.run')
    @patch('azext_fleet.custom.logger')
    def test_convert_handles_generic_exception(self, mock_logger, mock_subprocess, mock_which):
        """Test that generic exceptions are handled gracefully."""
        mock_which.return_value = MOCK_KUBELOGIN_PATH
        mock_subprocess.side_effect = Exception("Unexpected error")

        with tempfile.NamedTemporaryFile(mode='w', suffix=KUBECONFIG_SUFFIX, delete=False) as f:
            test_path = f.name

        try:
            _convert_kubeconfig_to_azurecli(test_path)

            # Verify error was logged
            mock_logger.warning.assert_called_once()
            warning_msg = mock_logger.warning.call_args[0][0]
            self.assertIn("Error running kubelogin", warning_msg)
        finally:
            if os.path.exists(test_path):
                os.remove(test_path)

    @patch('azext_fleet.custom.get_safe_executable_path')
    @patch('azext_fleet.custom.subprocess.run')
    def test_convert_skips_stdout_path(self, mock_subprocess, mock_which):
        """Test that conversion is skipped when path is stdout."""
        mock_which.return_value = MOCK_KUBELOGIN_PATH

        _convert_kubeconfig_to_azurecli(STDOUT_PATH)

        # Verify subprocess was not called
        mock_subprocess.assert_not_called()
        mock_which.assert_not_called()

    @patch('azext_fleet.custom.get_safe_executable_path')
    @patch('azext_fleet.custom.subprocess.run')
    def test_convert_with_custom_path(self, mock_subprocess, mock_which):
        """Test conversion with custom kubeconfig path."""
        mock_which.return_value = MOCK_KUBELOGIN_PATH
        mock_subprocess.return_value = MagicMock()

        _convert_kubeconfig_to_azurecli(CUSTOM_CONFIG_PATH)

        # Verify kubelogin was called with custom path
        call_args = mock_subprocess.call_args
        self.assertEqual(call_args[0][0], KUBELOGIN_CMD_PREFIX + [CUSTOM_CONFIG_PATH])


if __name__ == '__main__':
    unittest.main()
