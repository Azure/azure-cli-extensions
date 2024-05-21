# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from azext_aosm.definition_folder.builder.artifact_builder import (
    ArtifactDefinitionElementBuilder,
)


class TestArtifactDefinitionElementBuilder(TestCase):
    """Test the artifact definition element builder."""

    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.mkdir")
    def test_write(self, mock_mkdir, mock_write_text):
        """Test writing the definition element to disk."""

        # Create some mocks to act as artifacts.
        artifact_1 = MagicMock()
        artifact_1.to_dict.return_value = {"abc": "def"}
        artifact_2 = MagicMock()
        artifact_2.to_dict.return_value = {"ghi": "jkl"}

        # Create a Artifact definition element builder.
        artifact_definition_element_builder = ArtifactDefinitionElementBuilder(
            Path("/some/folder"), [artifact_1, artifact_2]
        )

        # Write the definition element to disk.
        artifact_definition_element_builder.write()

        # Check that the definition element was written to disk.
        mock_mkdir.assert_called_once()
        artifact_1.to_dict.assert_called_once()
        artifact_2.to_dict.assert_called_once()
        expected_params = [{"abc": "def"}, {"ghi": "jkl"}]
        mock_write_text.assert_called_once_with(json.dumps(expected_params, indent=4))
