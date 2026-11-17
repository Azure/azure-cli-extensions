# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# flake8: noqa

import os
import time
import unittest
from unittest import mock

from azext_networkcloud.operations.custom_properties import (
    CustomActionProperties,
    _get_az_command,
    _safe_remove_file,
)
from azure.cli.core.aaz._base import AAZUndefined
from azure.cli.core.azclierror import AzureInternalError


class TestCustomProperties(unittest.TestCase):
    """Test CustomProperties methods"""

    def test_resulturl_output(self):
        self._check_output_download("resultUrl")

    def test_resultref_output(self):
        self._check_output_download("resultRef")

    def _check_output_download(self, property_name):
        cmd = mock.Mock()
        args = cmd.ctx.args
        properties = cmd.ctx.vars.instance.properties
        properties.output_head = AAZUndefined
        properties.resultUrl = AAZUndefined
        properties.resultRef = AAZUndefined
        args.output = AAZUndefined
        target = "azext_networkcloud.operations.custom_properties._download_and_extract"
        with mock.patch(target) as download:
            CustomActionProperties._output(cmd)
            download.assert_not_called()
            cmd.deserialize_output.assert_called_once_with(
                cmd.ctx.vars.instance, client_flatten=True
            )
            url = "https://results.blob.core.windows.net/results/output.tar.gz"
            value = mock.Mock()
            value.to_serialized_data.return_value = url
            setattr(properties, property_name, value)
            CustomActionProperties._output(cmd)
            download.assert_not_called()

            args.output = "/path/to/output"
            args.expected_storage_host.to_serialized_data.return_value = (
                "results.blob.core.windows.net"
            )
            args.expected_sha256.to_serialized_data.return_value = "a" * 64
            CustomActionProperties._output(cmd)
            auth = {"cli_ctx": cmd.cli_ctx} if property_name == "resultRef" else {}
            download.assert_called_once_with(
                url, args.output, "results.blob.core.windows.net", "a" * 64, **auth
            )
            download.reset_mock()
            args.expected_sha256 = AAZUndefined
            CustomActionProperties._output(cmd)
            download.assert_called_once_with(
                url, args.output, "results.blob.core.windows.net", None, **auth
            )
            download.side_effect = ValueError("checksum mismatch")
            with self.assertRaisesRegex(AzureInternalError, "checksum mismatch"):
                CustomActionProperties._output(cmd)

    def test_safe_remove_file_success(self):
        """Test _safe_remove_file successfully removes a file"""
        test_file_path = "/path/to/test/file.txt"
        with mock.patch("os.path.exists", return_value=True), mock.patch(
            "os.remove"
        ) as mock_remove, mock.patch(
            "azext_networkcloud.operations.custom_properties.logger"
        ) as mock_logger:
            _safe_remove_file(test_file_path)
            mock_remove.assert_called_once_with(test_file_path)
            mock_logger.info.assert_called_once_with(
                "Successfully removed temporary file: %s", test_file_path
            )

    def test_safe_remove_file_not_exists(self):
        """Test _safe_remove_file when file doesn't exist"""
        test_file_path = "/path/to/nonexistent/file.txt"
        with mock.patch("os.path.exists", return_value=False), mock.patch(
            "os.remove"
        ) as mock_remove:
            _safe_remove_file(test_file_path)

            mock_remove.assert_not_called()

    def test_safe_remove_file_permission_error_retry_success(self):
        """Test _safe_remove_file retries on PermissionError and eventually succeeds"""
        test_file_path = "/path/to/test/file.txt"
        with mock.patch("os.path.exists", return_value=True), mock.patch(
            "os.remove", side_effect=[PermissionError("Access denied"), None]
        ) as mock_remove, mock.patch("time.sleep") as mock_sleep, mock.patch(
            "azext_networkcloud.operations.custom_properties.logger"
        ) as mock_logger:
            _safe_remove_file(test_file_path, max_retries=3, delay=0.1)
            self.assertEqual(mock_remove.call_count, 2)
            mock_sleep.assert_called_once_with(0.1)
            mock_logger.warning.assert_called_once()
            mock_logger.info.assert_called_once_with(
                "Successfully removed temporary file: %s", test_file_path
            )

    def test_safe_remove_file_permission_error_max_retries(self):
        """Test _safe_remove_file fails after max retries with PermissionError"""
        test_file_path = "/path/to/test/file.txt"
        permission_error = PermissionError("Access denied")
        with mock.patch("os.path.exists", return_value=True), mock.patch(
            "os.remove", side_effect=permission_error
        ) as mock_remove, mock.patch("time.sleep") as mock_sleep, mock.patch(
            "azext_networkcloud.operations.custom_properties.logger"
        ) as mock_logger:
            _safe_remove_file(test_file_path, max_retries=2, delay=0.1)
            self.assertEqual(mock_remove.call_count, 3)  # Initial attempt + 2 retries
            self.assertEqual(mock_sleep.call_count, 2)
            # Check that warning was called for each retry attempt
            self.assertEqual(mock_logger.warning.call_count, 2)
            # Check that error was called after max retries
            mock_logger.error.assert_called_once()

    def test_safe_remove_file_os_error(self):
        """Test _safe_remove_file handles OSError and logs error"""
        test_file_path = "/path/to/test/file.txt"
        os_error = OSError("Unexpected error")
        with mock.patch("os.path.exists", return_value=True), mock.patch(
            "os.remove", side_effect=os_error
        ) as mock_remove, mock.patch(
            "azext_networkcloud.operations.custom_properties.logger"
        ) as mock_logger:
            _safe_remove_file(test_file_path)
            mock_remove.assert_called_once_with(test_file_path)
            mock_logger.error.assert_called_once_with(
                "Unexpected error removing file %s: %s", test_file_path, str(os_error)
            )

    def test_safe_remove_file_exponential_backoff(self):
        """Test _safe_remove_file uses exponential backoff for delays"""
        test_file_path = "/path/to/test/file.txt"
        permission_error = PermissionError("Access denied")
        with mock.patch("os.path.exists", return_value=True), mock.patch(
            "os.remove", side_effect=permission_error
        ), mock.patch("time.sleep") as mock_sleep, mock.patch(
            "azext_networkcloud.operations.custom_properties.logger"
        ) as mock_logger:
            _safe_remove_file(test_file_path, max_retries=2, delay=0.1)
            # Check exponential backoff: first delay 0.1, second delay 0.2
            expected_calls = [mock.call(0.1), mock.call(0.2)]
            mock_sleep.assert_has_calls(expected_calls)

    def test_get_az_command_windows_found_cmd(self):
        """Test _get_az_command returns correct path for Windows when az.cmd is found"""
        expected_path = r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
        with mock.patch("os.name", "nt"), mock.patch(
            "os.path.exists", side_effect=lambda path: path == expected_path
        ):
            result = _get_az_command()
            self.assertEqual(result, expected_path)

    def test_get_az_command_windows_found_exe(self):
        """Test _get_az_command returns correct path for Windows when az.exe is found"""
        expected_path = r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.exe"

        def mock_exists(path):
            # Simulate az.cmd not existing but az.exe existing
            if "az.cmd" in path:
                return False
            elif path == expected_path:
                return True
            return False

        with mock.patch("os.name", "nt"), mock.patch(
            "os.path.exists", side_effect=mock_exists
        ):
            result = _get_az_command()
            self.assertEqual(result, expected_path)

    def test_get_az_command_windows_program_files_cmd(self):
        """Test _get_az_command returns Program Files path for Windows when az.cmd is found"""
        expected_path = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"

        def mock_exists(path):
            # Simulate Program Files (x86) not existing but Program Files existing
            if "Program Files (x86)" in path:
                return False
            elif path == expected_path:
                return True
            return False

        with mock.patch("os.name", "nt"), mock.patch(
            "os.path.exists", side_effect=mock_exists
        ):
            result = _get_az_command()
            self.assertEqual(result, expected_path)

    def test_get_az_command_windows_program_files_exe(self):
        """Test _get_az_command returns Program Files path for Windows when az.exe is found"""
        expected_path = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.exe"

        def mock_exists(path):
            # Simulate only the Program Files az.exe existing
            if "az.cmd" in path or "Program Files (x86)" in path:
                return False
            elif path == expected_path:
                return True
            return False

        with mock.patch("os.name", "nt"), mock.patch(
            "os.path.exists", side_effect=mock_exists
        ):
            result = _get_az_command()
            self.assertEqual(result, expected_path)

    def test_get_az_command_windows_not_found(self):
        """Test _get_az_command returns default 'az' when no Windows paths are found"""
        with mock.patch("os.name", "nt"), mock.patch(
            "os.path.exists", return_value=False
        ):
            result = _get_az_command()
            self.assertEqual(result, "az")

    def test_get_az_command_non_windows(self):
        """Test _get_az_command returns default 'az' for non-Windows platforms"""
        with mock.patch("os.name", "posix"):
            result = _get_az_command()
            self.assertEqual(result, "az")

    def test_get_az_command_linux(self):
        """Test _get_az_command returns default 'az' for Linux"""
        with mock.patch("os.name", "posix"):
            result = _get_az_command()
            self.assertEqual(result, "az")

    def test_get_az_command_mac(self):
        """Test _get_az_command returns default 'az' for Mac (Darwin)"""
        with mock.patch("os.name", "darwin"):
            result = _get_az_command()
            self.assertEqual(result, "az")

    def test_get_az_command_windows_path_priority(self):
        """Test _get_az_command follows correct priority order for Windows paths"""
        # Test that Program Files (x86) az.cmd takes precedence
        first_priority_path = (
            r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
        )

        def mock_exists_first_found(path):
            return path == first_priority_path

        with mock.patch("os.name", "nt"), mock.patch(
            "os.path.exists", side_effect=mock_exists_first_found
        ):
            result = _get_az_command()
            self.assertEqual(result, first_priority_path)
