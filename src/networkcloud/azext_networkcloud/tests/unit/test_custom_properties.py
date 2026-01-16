# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# flake8: noqa

import os
import subprocess
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
        self.cmd = mock.Mock()

        # Mock args
        args = mock.Mock()
        self.cmd.ctx = mock.Mock()
        self.cmd.ctx.args = args

        # Mock deserialize method
        self.cmd.deserialize_output.return_value = mock.Mock()

        # Mock vars
        self.cmd.ctx.vars = mock.Mock()
        self.cmd.ctx.vars.instance = mock.Mock()

        # Mock output head
        self.cmd.ctx.vars.instance.properties = mock.Mock()
        self.cmd.ctx.vars.instance.properties.output_head = mock.Mock()
        self.cmd.ctx.vars.instance.properties.output_head.to_serialized_data = (
            mock.Mock(side_effect="HEADER")
        )

        # Validate URL download skipped when result URL not provided
        with mock.patch("urllib.request.urlopen") as mock_urlopen:
            # Set output dir to undefined
            self.cmd.ctx.args.output = AAZUndefined

            # Set result url to undefined
            self.cmd.ctx.vars.instance.properties.resultUrl = AAZUndefined
            self.cmd.ctx.vars.instance.properties.resultRef = AAZUndefined

            CustomActionProperties()._output(self.cmd, args)
            mock_urlopen.assert_not_called()

        # Mock result URL
        test_url = "https://aka.ms/fakeurl"
        self.cmd.ctx.vars.instance.properties.resultUrl = mock.Mock()
        self.cmd.ctx.vars.instance.properties.resultUrl.to_serialized_data = mock.Mock(
            side_effect=test_url
        )

        # Validate results not downloaded when no output dir provided
        with mock.patch("urllib.request.urlopen") as mock_urlopen:
            # Set output dir to undefined
            self.cmd.ctx.args.output = AAZUndefined

            CustomActionProperties()._output(self.cmd, args)
            mock_urlopen.assert_not_called()

        # Validate exceptions handled
        with mock.patch("urllib.request.urlopen") as mock_urlopen:
            test_output_dir = "/path/to/test/output/dir"
            self.cmd.ctx.args.output = mock.Mock()
            self.cmd.ctx.args.output.to_serialized_data.return_value = test_output_dir

            # Raise exception when calling tar lib
            with mock.patch("tarfile.open") as tar_open:
                tar_open.side_effect = Exception
                with self.assertRaises(Exception):
                    CustomActionProperties()._output(self.cmd, args)

            # Raise exception when calling URL
            mock_urlopen.side_effect = Exception
            with self.assertRaises(Exception):
                CustomActionProperties()._output(self.cmd, args)

    def test_resultref_output(self):
        self.cmd = mock.Mock()

        # Mock args
        args = mock.Mock()
        self.cmd.ctx = mock.Mock()
        self.cmd.ctx.args = args

        # Validate URL download skipped when resultRef not provided
        with mock.patch("subprocess.run") as mock_subprocess_run:
            # Set output dir to undefined
            self.cmd.ctx.args.output = AAZUndefined

            # Set result url to undefined
            self.cmd.ctx.vars.instance.properties.resultRef = AAZUndefined

            CustomActionProperties()._output(self.cmd, args)
            mock_subprocess_run.assert_not_called()

        # Mock result URL
        test_url = "https://aka.ms/fakeurl"
        self.cmd.ctx.vars.instance.properties.resultRef = mock.Mock()
        self.cmd.ctx.vars.instance.properties.resultRef.to_serialized_data = mock.Mock(
            side_effect=test_url
        )

        # Validate results not downloaded when no output dir provided
        with mock.patch("subprocess.run") as mock_subprocess_run:
            # Set output dir to undefined
            self.cmd.ctx.args.output = AAZUndefined

            CustomActionProperties()._output(self.cmd, args)
            mock_subprocess_run.assert_not_called()

        # Validate exceptions handled
        with mock.patch("subprocess.run") as mock_subprocess_run:
            test_output_dir = "/path/to/test/output/dir"
            self.cmd.ctx.args.output = test_output_dir

            # Simulate subprocess.run raising an error
            mock_subprocess_run.side_effect = subprocess.CalledProcessError(
                returncode=1, cmd="az storage blob download", stderr="Simulated error"
            )

            # Raise exception when downloading blob
            mock_subprocess_run.side_effect = Exception
            with self.assertRaises(AzureInternalError) as cm:
                CustomActionProperties()._output(self.cmd, args)

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
