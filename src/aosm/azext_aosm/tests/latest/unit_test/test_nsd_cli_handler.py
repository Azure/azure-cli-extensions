# from __future__ import annotations
# from unittest import TestCase
# from unittest.mock import patch
# from azext_aosm.cli_handlers.onboarding_nsd_handler import OnboardingNSDCLIHandler
# from azure.cli.core.azclierror import (
#     UnclassifiedUserFault,
# )
# TODO: Fix tests with correct mocking for input()

# @patch("pathlib.Path.exists")
# class TestNsdCliHandler(TestCase):

#     @patch("pathlib.Path.write_text")
#     def test_generate_config(self, mock_exists, mock_write_text):
#         mock_exists.return_value = False
#         # sensible naming
#         file_path = __file__.split('/')[:-1]
#         file_path.append('input_files')
#         file_path.append('nsd-input.jsonc')
#         file_path = '/'.join(file_path)
#         with open(file_path, "r") as f:
#             expected_output = f.read()
#         nsd_cli_handler = OnboardingNSDCLIHandler()
#         nsd_cli_handler.generate_config()

#         mock_write_text.assert_called_with(expected_output)

#     @patch("pathlib.Path.write_text")
#     @patch("builtins.input")
#     def test_generate_config_with_file_to_overwrite(self, mock_input, mock_write_text, mock_exists):
#         mock_exists.return_value = True
#         mock_input.return_value = "y"

#         file_path = __file__.split('/')[:-1]
#         file_path.append('input_files')
#         file_path.append('nsd-input.jsonc')
#         file_path = '/'.join(file_path)
#         with open(file_path, "r") as f:
#             expected_output = f.read()
#         nsd_cli_handler = OnboardingNSDCLIHandler()
#         nsd_cli_handler.generate_config()

#         mock_input.assert_called()
#         mock_write_text.assert_called_with(expected_output)

#     # @patch("builtins.input")
#     def test_generate_config_with_file_not_to_overwrite(self, mock_exists):
            
#             mock_exists.return_value = True
#             assert input() == 'n'
#             # mock_input.return_value = "n"
#             nsd_cli_handler = OnboardingNSDCLIHandler()

#             with self.assertRaises(UnclassifiedUserFault):
#                 nsd_cli_handler.generate_config()
