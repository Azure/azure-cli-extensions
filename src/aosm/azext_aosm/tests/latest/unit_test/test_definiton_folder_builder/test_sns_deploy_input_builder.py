# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch, mock_open, Mock
from io import TextIOWrapper
from pathlib import PosixPath

from azext_aosm.definition_folder.builder.sns_deploy_input_builder import (
    SNSDeploymentInputDefinitionElementBuilder,
)
from azext_aosm.vendored_sdks.models import NfviDetails


class TestDeploymentInputDefinitionElementBuilder(TestCase):
    """Test the DeploymentInputDefinitionElementBuilder."""

    
    @patch("builtins.open", new_callable=mock_open)
    def test_write(self, mock_open):
        """Test writing the definition element to disk."""

        # Create some mocks to act as nfvis.
        nfvi_1 = NfviDetails(name="nfvi1", type="type1")
        nfvi_2 = NfviDetails(name="nfvi2", type="type2")
        nfvis = {"nfvi1": nfvi_1, "nfvi2": nfvi_2}

        schema_to_cgv_map = [
            {"cgv_name": "cgv1", "cgv_configuration_type": "Open", "cgv_file_path": "/path/to/cgv1"},
            {"cgv_name": "cgv2", "cgv_configuration_type": "Open", "cgv_file_path": "/path/to/cgv2"},
        ]

        # Create a DeploymentInputDefinitionElementBuilder.
        deployment_input_definition_element_builder = (
            SNSDeploymentInputDefinitionElementBuilder(
                Path("/some/folder"), nfvis, schema_to_cgv_map
            )
        )
        mock_mkdir = Mock()        
        with patch(
            "pathlib.Path.mkdir",
            mock_mkdir,
        ):
            # Write the definition element to disk.
            deployment_input_definition_element_builder.write()
            mock_mkdir.assert_called_once_with(exist_ok=True)
        mock_open.assert_called_once_with(Path("/some/folder/deploy_input.jsonc"), "w")

        expected_data = json.dumps(
            {
                "nfvis_list": [
                    {
                        "name": "nfvi1",
                        "nfviType": "type1",
                        "customLocationReference": {"id": ""},
                    },
                    {
                        "name": "nfvi2",
                        "nfviType": "type2",
                        "customLocationReference": {"id": ""},
                    },
                ],
                "cgv_list": [
                    {"cgv_name": "cgv1", "cgv_configuration_type": "Open", "cgv_file_path": "/path/to/cgv1"},
                    {"cgv_name": "cgv2", "cgv_configuration_type": "Open", "cgv_file_path": "/path/to/cgv2"},
                ],
            },
            indent=4,
        )

        # Get the mock file object that open returned
        mock_file = mock_open()

        # Assert that write was called with the correct data
        mock_file.write.assert_called_once_with(expected_data)