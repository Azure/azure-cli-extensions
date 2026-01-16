# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations
from unittest import TestCase
from unittest.mock import patch, Mock
from azext_aosm.cli_handlers.onboarding_nsd_handler import OnboardingNSDCLIHandler
from azure.cli.core.azclierror import (
    UnclassifiedUserFault,
)
import logging

unit_test_folder_path = __file__.split("/")[:-2]
input_files_path = unit_test_folder_path + ["input_files"]
nsd_input_file = input_files_path + ["nsd-input.jsonc"]
nsd_input_file = "/".join(nsd_input_file)


@patch("pathlib.Path.exists")
class TestNsdCliHandler(TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.INFO)

    def test_generate_config(self, mock_exists):
        mock_exists.return_value = False

        with open(nsd_input_file, "r") as f:
            expected_config = f.read()

        nsd_cli_handler = OnboardingNSDCLIHandler()
        mocked_write_text = Mock()
        with patch(
            "pathlib.Path.write_text",
            mocked_write_text,
        ):
            nsd_cli_handler.generate_config()            
            mocked_write_text.assert_called_with(expected_config)

    @patch("builtins.input")
    def test_generate_config_with_file_to_overwrite(self, mock_input, mock_exists):
        mock_exists.return_value = True
        mock_input.return_value = "y"

        with open(nsd_input_file, "r") as f:
            expected_output = f.read()

        nsd_cli_handler = OnboardingNSDCLIHandler()
        mocked_write_text = Mock()

        with patch(
            "pathlib.Path.write_text",
            mocked_write_text,
        ):
            nsd_cli_handler.generate_config()
            mock_input.assert_called()
            mocked_write_text.assert_called_with(expected_output)

    @patch("builtins.input")
    def test_generate_config_with_file_not_to_overwrite(self, mock_input, mock_exists):
        mock_exists.return_value = True
        mock_input.return_value = "n"

        nsd_cli_handler = OnboardingNSDCLIHandler()

        with self.assertRaises(UnclassifiedUserFault):
            nsd_cli_handler.generate_config()
