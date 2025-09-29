# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from pathlib import Path
from unittest import TestCase
from unittest.mock import call, MagicMock, patch

from azext_aosm.definition_folder.reader.definition_folder import DefinitionFolder

from azext_aosm.configuration_models.common_parameters_config import (
    BaseCommonParametersConfig,
)


class MockCommandContext:
    def __init__(self) -> None:
        self.cli_ctx = None
        self.resources_client = MagicMock()


mocked_command_context = MockCommandContext()


class TestDefinitionFolderBuilder(TestCase):
    """Test the definition folder object."""

    @patch(
        "azext_aosm.definition_folder.reader.definition_folder.BicepDefinitionElement"
    )
    @patch(
        "azext_aosm.definition_folder.reader.definition_folder.ArtifactDefinitionElement"
    )
    @patch("pathlib.Path.read_text")
    def test_deploy(self, mock_read_text, mock_artifact_element, mock_bicep_element):
        """Test creating and deploying a definition folder."""

        # Example index.json
        mock_read_text.return_value = """
        [
            {
                "name": "biceptemplate",
                "type": "bicep"
            },
            {
                "name": "artifactlist",
                "type": "artifact",
                "only_delete_on_clean": true
            }
        ]
        """

        # Create a parent mock to check correct call order.
        mock_elements = MagicMock()
        mock_elements.attach_mock(mock_bicep_element, "bicep_element")
        mock_elements.attach_mock(mock_artifact_element, "artifact_element")

        mocked_config = MagicMock()

        # Create a definition folder
        folder_path = Path("/definition/folder/path")
        definition_folder = DefinitionFolder(folder_path)

        # Deploy the definition folder
        definition_folder.deploy(
            config=mocked_config, command_context=mocked_command_context
        )

        # Check that the elements w bere created and deployed in the expected order.
        mock_elements.assert_has_calls(
            [
                call.bicep_element(folder_path / "biceptemplate", False),
                call.artifact_element(folder_path / "artifactlist", True),
                call.bicep_element().deploy(
                    config=mocked_config, command_context=mocked_command_context
                ),
                call.artifact_element().deploy(
                    config=mocked_config, command_context=mocked_command_context
                ),
            ]
        )

    @patch("pathlib.Path.read_text")
    def test_bad_index_file(self, mock_read_text):
        """Test that a bad index file raises an error."""

        # Example index.json
        mock_read_text.return_value = """
        unicode_snowman.jpeg
        """

        # Attempt to create a definition folder, check an exception is raised.
        folder_path = Path("/definition/folder/path")
        with self.assertRaises(ValueError):
            DefinitionFolder(folder_path)

    @patch("pathlib.Path.read_text")
    def test_index_missing_name(self, mock_read_text):
        """Test that an index file with a missing name raises an error."""

        # Example index.json
        mock_read_text.return_value = """
        [
            {
                "type": "bicep"
            }
        ]
        """

        # Attempt to create a definition folder, check an exception is raised.
        folder_path = Path("/definition/folder/path")
        with self.assertRaises(ValueError):
            DefinitionFolder(folder_path)

    @patch("pathlib.Path.read_text")
    def test_index_missing_type(self, mock_read_text):
        """Test that an index file with a missing type raises an error."""

        # Example index.json
        mock_read_text.return_value = """
        [
            {
                "name": "biceptemplate"
            }
        ]
        """

        # Attempt to create a definition folder, check an exception is raised.
        folder_path = Path("/definition/folder/path")
        with self.assertRaises(ValueError):
            DefinitionFolder(folder_path)

    # The Delete code does not do anything at the moment, which is why we cannot test it.
    # @patch(
    #     "azext_aosm.definition_folder.reader.definition_folder.BicepDefinitionElement"
    # )
    # @patch(
    #     "azext_aosm.definition_folder.reader.definition_folder.ArtifactDefinitionElement"
    # )
    # @patch("pathlib.Path.read_text")
    # def test_delete(self, mock_read_text, mock_artifact_element, mock_bicep_element):
    #     """Test creating and deploying a definition folder."""

    #     # Example index.json
    #     mock_read_text.return_value = """
    #     [
    #         {
    #             "name": "infratemplate",
    #             "type": "bicep",
    #             "only_delete_on_clean": true
    #         },
    #         {
    #             "name": "biceptemplate",
    #             "type": "bicep"
    #         },
    #         {
    #             "name": "artifactlist",
    #             "type": "artifact",
    #             "only_delete_on_clean": false
    #         }
    #     ]
    #     """

    #     # Set up mocks.
    #     mock_bicep_element().only_delete_on_clean.__bool__.side_effect = [False, True]
    #     mock_artifact_element().only_delete_on_clean.__bool__.return_value = False

    #     # Create a parent mock to check correct call order.
    #     mock_elements = MagicMock()
    #     mock_elements.attach_mock(mock_bicep_element, "bicep_element")
    #     mock_elements.attach_mock(mock_artifact_element, "artifact_element")

    #     # Create a definition folder
    #     folder_path = Path("/definition/folder/path")
    #     definition_folder = DefinitionFolder(folder_path)

    #     # Call delete for the definition folder
    #     definition_folder.delete()

    #     # Check that the elements were created and deleted in the expected order.
    #     # Delete should be in reverse order, and only_delete_on_clean should be respected.
    #     mock_elements.assert_has_calls(
    #         [
    #             call.bicep_element(folder_path / "infratemplate", True),
    #             call.bicep_element(folder_path / "biceptemplate", False),
    #             call.artifact_element(folder_path / "artifactlist", False),
    #             call.artifact_element().only_delete_on_clean.__bool__(),
    #             call.artifact_element().delete(),
    #             call.bicep_element().only_delete_on_clean.__bool__(),
    #             call.bicep_element().delete(),
    #             call.bicep_element().only_delete_on_clean.__bool__(),
    #         ]
    #     )
    #     self.assertEqual(mock_bicep_element().delete.call_count, 1)
    #     self.assertEqual(mock_artifact_element().delete.call_count, 1)

    # @patch(
    #     "azext_aosm.definition_folder.reader.definition_folder.BicepDefinitionElement"
    # )
    # @patch(
    #     "azext_aosm.definition_folder.reader.definition_folder.ArtifactDefinitionElement"
    # )
    # @patch("pathlib.Path.read_text")
    # def test_delete_clean(
    #     self, mock_read_text, mock_artifact_element, mock_bicep_element
    # ):
    #     """Test creating and deploying a definition folder."""

    #     # Example index.json
    #     mock_read_text.return_value = """
    #     [
    #         {
    #             "name": "infratemplate",
    #             "type": "bicep",
    #             "only_delete_on_clean": true
    #         },
    #         {
    #             "name": "biceptemplate",
    #             "type": "bicep"
    #         },
    #         {
    #             "name": "artifactlist",
    #             "type": "artifact",
    #             "only_delete_on_clean": false
    #         }
    #     ]
    #     """

    #     # Create a parent mock to check correct call order.
    #     mock_elements = MagicMock()
    #     mock_elements.attach_mock(mock_bicep_element, "bicep_element")
    #     mock_elements.attach_mock(mock_artifact_element, "artifact_element")

    #     # Create a definition folder
    #     folder_path = Path("/definition/folder/path")
    #     definition_folder = DefinitionFolder(folder_path)

    #     # Call delete for the definition folder
    #     definition_folder.delete(clean=True)

    #     # Check that the elements were created and deleted in the expected order.
    #     # Delete should be in reverse order, and only_delete_on_clean should be respected.
    #     mock_elements.assert_has_calls(
    #         [
    #             call.bicep_element(folder_path / "infratemplate", True),
    #             call.bicep_element(folder_path / "biceptemplate", False),
    #             call.artifact_element(folder_path / "artifactlist", False),
    #             call.artifact_element().delete(),
    #             call.bicep_element().delete(),
    #         ]
    #     )
    #     self.assertEqual(mock_bicep_element().delete.call_count, 2)
    #     self.assertEqual(mock_artifact_element().delete.call_count, 1)
