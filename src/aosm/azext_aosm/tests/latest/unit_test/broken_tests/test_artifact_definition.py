# # --------------------------------------------------------------------------------------------
# # Copyright (c) Microsoft Corporation. All rights reserved.
# # Licensed under the MIT License. See License.txt in the project root for license information.
# # --------------------------------------------------------------------------------------------

# from pathlib import Path
# from unittest import TestCase
# from unittest.mock import call, MagicMock, patch, create_autospec

# from azext_aosm.definition_folder.reader.artifact_definition import ArtifactDefinitionElement
# from azext_aosm.common.artifact import LocalFileACRArtifact

# class TestArtifactDefinitionElement(TestCase):
#     """Test the Artifact definition element."""


#     @patch("pathlib.Path.read_text")
#     def test_deploy(self, mock_read_text):
#         """Test deploying an Artifact definition element."""

#         # Example artifacts.json
#         # Fields other than type are ignored as Artifact classes are mocked.
#         mock_read_text.return_value = """
#         [
#             {
#                 "artifact_type": "ArmTemplate",
#                 "artifact_name": "abc",
#                 "artifact_version": "1.0.0",
#                 "type": "MockType1",
#                 "file_path": "def"
#             },
#             {
#                 "artifact_type": "ArmTemplate",
#                 "artifact_name": "ghi",
#                 "artifact_version": "2.1.1",
#                 "type": "MockType2",
#                 "file_path": "jkl"
#             }
#         ]
#         """

#         # Create artifact type mocks.
#         mock_type_1 = LocalFileACRArtifact
#         mock_type_2 = LocalFileACRArtifact
#         mock_artifact_type_to_class = {
#             "MockType1": mock_type_1,
#             "MockType2": mock_type_2,
#         }

#         with patch.dict(
#             "azext_aosm.definition_folder.reader.artifact_definition.ARTIFACT_TYPE_TO_CLASS",
#             mock_artifact_type_to_class
#         ):
#             # Create an Artifact definition element.
#             element_path = Path("/element/path")
#             definition_element = ArtifactDefinitionElement(element_path, False)

#         # Deploy the element.
#         mock_config = MagicMock()
#         mock_context = MagicMock()
#         definition_element.deploy(config=mock_config, command_context=mock_context)

#         # Check results.
#         mock_type_1.assert_has_calls(
#             [
#                 call.upload(),
#             ]
#         )
#         mock_type_2.assert_has_calls(
#             [
#                 call.upload(),
#             ]
#         )

#     @patch("pathlib.Path.read_text")
#     def test_delete(self, mock_read_text):
#         """Test deleting an Artifact definition element."""

#         # Example artifacts.json
#         # Fields other than type are ignored as Artifact classes are mocked.
#         mock_read_text.return_value = """
#         [
#             {
#                 "type": "MockType1",
#                 "artifact_manifest": "def",
#                 "file_path": "def"
#             },
#             {
#                 "type": "MockType2",
#                 "artifact_manifest": "jkl",
#                 "file_path": "jkl"
#             }
#         ]
#         """

#         # Create artifact type mocks.
#         mock_type_1 = LocalFileACRArtifact
#         mock_type_2 = LocalFileACRArtifact
#         mock_artifact_type_to_class = {
#             "MockType1": mock_type_1,
#             "MockType2": mock_type_2,
#         }

#         with patch.dict(
#             "azext_aosm.definition_folder.reader.artifact_definition.ARTIFACT_TYPE_TO_CLASS",
#             mock_artifact_type_to_class
#         ):
#             # Create an Artifact definition element.
#             # only_delete_on_clean is True, but this is not checked in the delete method.
#             # It is expected to be checked in the owning DefinitionFolder before calling delete.
#             element_path = Path("/element/path")
#             definition_element = ArtifactDefinitionElement(element_path, True)

#         # Delete the element.
#         # TODO: Implement? Currently no-op.
#         definition_element.delete()

#         # Check results.
#         # TODO: Implement.
