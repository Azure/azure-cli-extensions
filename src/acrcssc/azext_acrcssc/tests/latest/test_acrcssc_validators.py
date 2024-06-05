# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile
import unittest
from unittest import mock
from datetime import (
        datetime,
        timezone
    )
from ..._validators import (
    validate_and_convert_timespan_to_cron,
    check_continuoustask_exists,
    validate_continuouspatch_config_v1
)

from azure.cli.core.azclierror import AzCLIError
from azure.cli.core.mock import DummyCli
from unittest.mock import patch


class AcrCsscCommandsTests(unittest.TestCase):

    def test_validate_and_convert_timespan_to_cron(self):
        test_cases = [
            ('1d', '2 12 */1 * *', datetime(2022, 1, 1, 12, 0, 0, tzinfo=timezone.utc), False),
            ('5d', '2 12 */5 * *', datetime(2022, 1, 1, 12, 0, 0, tzinfo=timezone.utc), False),
            ('1d', '2 12 */1 * *', datetime(2022, 1, 1, 12, 0, 0, tzinfo=timezone.utc), False),
            ('1d', '58 11 */1 * *', datetime(2022, 1, 1, 12, 0, 0, tzinfo=timezone.utc), True),
            ('1d', '1 13 */1 * *', datetime(2022, 1, 1, 12, 59, 0, tzinfo=timezone.utc), False),
            ('1d', '57 12 */1 * *', datetime(2022, 1, 1, 12, 59, 0, tzinfo=timezone.utc), True)
        ]

        for timespan, expected_cron, date_time, do_not_run_immediately in test_cases:
            with self.subTest(timespan=timespan):
                if date_time:
                    result = validate_and_convert_timespan_to_cron(timespan, date_time, do_not_run_immediately)
                self.assertEqual(result, expected_cron)
    
    @patch('azext_acrcssc._validators.cf_acr_tasks')
    def test_check_continuoustask_exists(self, mock_cf_acr_tasks):
        cmd = self._setup_cmd()
        registry = mock.MagicMock()
        registry.id = "/subscriptions/11111111-0000-0000-0000-0000000000006/resourceGroups/test-rg/providers/Microsoft.ContainerRegistry/registries/testregistry"
        cf_acr_tasks_mock = mock.MagicMock()

        mock_cf_acr_tasks.return_value = cf_acr_tasks_mock
        cf_acr_tasks_mock.get.return_value = {"name": "my_task"}
        # use the client factory to use ACR's client to query for this task
        exists = check_continuoustask_exists(cmd, registry)
        self.assertTrue(exists)

    @patch('azext_acrcssc._validators.cf_acr_tasks')
    def test_task_does_not_exist(self, mock_cf_acr_tasks):
        cmd = self._setup_cmd()
        registry = mock.MagicMock()
        registry.id = "/subscriptions/11111111-0000-0000-0000-0000000000006/resourceGroups/test-rg/providers/Microsoft.ContainerRegistry/registries/testregistry"
        cf_acr_tasks_mock = mock.MagicMock()

        mock_cf_acr_tasks.return_value = cf_acr_tasks_mock
        cf_acr_tasks_mock.get.return_value = None

        exists = check_continuoustask_exists(cmd, registry)
        self.assertFalse(exists)
    
    def test_validate_continuouspatch_file(self):
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name

       # Test when the file does not exist
        with patch('os.path.exists', return_value=False):
            self.assertRaises(AzCLIError, validate_continuouspatch_config_v1, temp_file_path)

        # Test when the path is not a file
        with patch('os.path.exists', return_value=True), \
             patch('os.path.isfile', return_value=False):
            self.assertRaises(AzCLIError, validate_continuouspatch_config_v1, temp_file_path)

        # Test when the file size exceeds the limit
        with patch('os.path.exists', return_value=True), \
             patch('os.path.isfile', return_value=True), \
             patch('os.path.getsize', return_value=10485761):
            self.assertRaises(AzCLIError, validate_continuouspatch_config_v1, temp_file_path)

        # Test when the file is empty
        with patch('os.path.exists', return_value=True), \
             patch('os.path.isfile', return_value=True), \
             patch('os.path.getsize', return_value=0):
            self.assertRaises(AzCLIError, validate_continuouspatch_config_v1, temp_file_path)

        # Test when the file is not readable
        with patch('os.path.exists', return_value=True), \
             patch('os.path.isfile', return_value=True), \
             patch('os.path.getsize', return_value=100), \
             patch('os.access', return_value=False):
            self.assertRaises(AzCLIError, validate_continuouspatch_config_v1, temp_file_path)

        # Clean up the temporary file
        os.remove(temp_file_path)

    @patch('azext_acrcssc._validators.json.load')
    def test_validate_continuouspatch_json_valid_json_should_parse(self, mock_load):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name

        mock_config = {
            "repositories": [
                {
                    "repository": "docker-local",
                    "tags": ["v1"],
                    "enabled": True
                }],
            "version": "1"
            }
        mock_load.return_value = mock_config

        with patch('os.path.exists', return_value=True), \
             patch('os.path.isfile', return_value=True), \
             patch('os.path.getsize', return_value=100), \
             patch('os.access', return_value=True):
             validate_continuouspatch_config_v1(temp_file_path)
             mock_load.assert_called_once_with(mock.ANY)
    
    @patch('azext_acrcssc._validators.json.load')
    def test_validate_continuouspatch_json_invalid_json_should_fail(self, mock_load):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name

        mock_invalid_config = {
            "repositories": [
                {
                    "repository": "docker-local",
                    "tags": ["v1"],
                }],
            }
        mock_load.return_value = mock_invalid_config

        with patch('os.path.exists', return_value=True), \
             patch('os.path.isfile', return_value=True), \
             patch('os.path.getsize', return_value=100), \
             patch('os.access', return_value=True):
             self.assertRaises(AzCLIError, validate_continuouspatch_config_v1, temp_file_path)
    
    def _setup_cmd(self):
        cmd = mock.MagicMock()
        cmd.cli_ctx = DummyCli()
        return cmd