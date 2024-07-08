# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from azext_aosm.definition_folder.builder.definition_folder_builder import DefinitionFolderBuilder


class TestDefinitionFolderBuilder(TestCase):
    """Test the definition folder builder."""

    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.mkdir")
    def test_add_elements_and_write(self, mock_mkdir, mock_write_text):
        """Test adding elements and writing the definition folder."""

        # Create some mocks to act as definition elements.
        element_1 = MagicMock()
        element_1.path = Path("/some/folder/element_1")
        element_1.only_delete_on_clean = False
        element_2 = MagicMock()
        element_2.path = Path("/some/folder/element_2")
        element_2.only_delete_on_clean = True

        # Create a definition folder builder.
        definition_folder_builder = DefinitionFolderBuilder(Path("/some/folder"))

        # Add the elements to the definition folder builder.
        definition_folder_builder.add_element(element_1)
        definition_folder_builder.add_element(element_2)

        # Write the definition folder.
        definition_folder_builder.write()

        # Check that the elements were written to disk.
        mock_mkdir.assert_called_once()
        element_1.write.assert_called_once()
        element_2.write.assert_called_once()

        # Check that the index.json file was written to disk.
        expected_params = [{"name": "element_1",
                            "type": "artifact",
                            "only_delete_on_clean": False },
                            {"name": "element_2",
                             "type": "artifact",
                             "only_delete_on_clean": True}]
        mock_write_text.assert_called_once_with(json.dumps(expected_params, indent=4))

