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
MOCK_KUBELOGIN_PATH = '/usr/bin/kubelogin'
KUBELOGIN_TIMEOUT = 60
KUBELOGIN_CMD_PREFIX = [KUBELOGIN_BINARY, "convert-kubeconfig", "-l", "azurecli", "--kubeconfig"]
KUBELOGIN_GITHUB_URL = "https://github.com/Azure/kubelogin"
KUBECONFIG_SUFFIX = '.kubeconfig'
STDOUT_PATH = '-'
CUSTOM_CONFIG_PATH = '/custom/path/to/config'


class TestKubeloginConversion(unittest.TestCase):
    """Test cases for kubelogin automatic conversion functionality."""

    @patch('azext_fleet.custom.shutil.which')
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
            call_args = mock_subprocess.call_args
            self.assertEqual(call_args[0][0], KUBELOGIN_CMD_PREFIX + [test_path])
            self.assertTrue(call_args[1]['check'])
            self.assertEqual(call_args[1]['timeout'], KUBELOGIN_TIMEOUT)

            # Verify success message was logged
            mock_logger.warning.assert_called_with("Converted kubeconfig to use Azure CLI authentication.")
        finally:
            if os.path.exists(test_path):
                os.remove(test_path)

    @patch('azext_fleet.custom.shutil.which')
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

    @patch('azext_fleet.custom.shutil.which')
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

    @patch('azext_fleet.custom.shutil.which')
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

    @patch('azext_fleet.custom.shutil.which')
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

    @patch('azext_fleet.custom.shutil.which')
    @patch('azext_fleet.custom.subprocess.run')
    def test_convert_skips_stdout_path(self, mock_subprocess, mock_which):
        """Test that conversion is skipped when path is stdout."""
        mock_which.return_value = MOCK_KUBELOGIN_PATH

        _convert_kubeconfig_to_azurecli(STDOUT_PATH)

        # Verify subprocess was not called
        mock_subprocess.assert_not_called()

    @patch('azext_fleet.custom.shutil.which')
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
