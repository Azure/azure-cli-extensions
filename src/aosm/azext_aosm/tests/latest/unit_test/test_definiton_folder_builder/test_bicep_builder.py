# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from azext_aosm.definition_folder.builder.bicep_builder import (
    BicepDefinitionElementBuilder,
)


class TestBicepDefinitionElementBuilder(TestCase):
    """Test the Bicep definition element builder."""

    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.mkdir")
    def test_write(self, mock_mkdir, mock_write_text):
        """Test writing the definition element to disk."""

        # Create a Bicep definition element builder.
        bicep_definition_element_builder = BicepDefinitionElementBuilder(
            Path("/some/folder"), "some bicep content"
        )

        # Write the definition element to disk.
        bicep_definition_element_builder.write()

        # Check that the definition element was written to disk.
        mock_mkdir.assert_called_once()
        mock_write_text.assert_called_once_with("some bicep content")

    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.mkdir")
    def test_write_supporting_files(self, mock_mkdir, mock_write_text):
        """Test writing the definition element to disk with supporting files."""

        # Create a Bicep definition element builder.
        bicep_definition_element_builder = BicepDefinitionElementBuilder(
            Path("/some/folder"), "some bicep content"
        )

        # Create some mocks to act as supporting files.
        supporting_file_1 = MagicMock()
        supporting_file_2 = MagicMock()

        # Add the supporting files to the definition element builder.
        bicep_definition_element_builder.add_supporting_file(supporting_file_1)
        bicep_definition_element_builder.add_supporting_file(supporting_file_2)

        # Write the definition element to disk.
        bicep_definition_element_builder.write()

        # Check that the definition element was written to disk.
        mock_mkdir.assert_called_once()
        mock_write_text.assert_called_once_with("some bicep content")

        # Check that the supporting files were written to disk.
        supporting_file_1.write.assert_called_once()
        supporting_file_2.write.assert_called_once()
