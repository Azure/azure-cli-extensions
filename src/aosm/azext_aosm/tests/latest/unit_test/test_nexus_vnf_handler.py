# from unittest import TestCase
# from unittest.mock import patch, MagicMock
# from pathlib import Path
# from typing import List
# from azext_aosm.cli_handlers.onboarding_nexus_vnf_handler import OnboardingNexusVNFCLIHandler
# from azext_aosm.definition_folder.builder.artifact_builder import ArtifactDefinitionElementBuilder
# from azext_aosm.definition_folder.builder.bicep_builder import BicepDefinitionElementBuilder
# from azext_aosm.definition_folder.builder.local_file_builder import LocalFileBuilder
# from azext_aosm.common.constants import VNF_OUTPUT_FOLDER_FILENAME, ARTIFACT_LIST_FILENAME


# class VNFNexusBuildTest(TestCase):

#     def setUp(self):
#         self.nexus_handler = OnboardingNexusVNFCLIHandler()

# #     def test_valid_nexus_config_provided():
# #         # give it nexus specific config
# #         pass

# #     def test_invalid_nexus_config_provided():
# #         # give it nexus specific config with an error
# #         pass

# #     def test_core_config_provided():
# #         # give it core specific config
# #         pass

# #     # def test_build_base_bicep(self):
# #         # with patch("pathlib.Path.write_text") as mock_write_text:
# #         #     self.nexus_vnf_cli_handler.build_base_bicep()
# #         #     mock_write_text.assert_called()

#     def test_build_artifact_list_type(self):
#         """ Testing build artifact list for Nexus VNFs

#         Test if path is as expected, and if list returned is correct type
#         """
#         self.nexus_handler.processors = MagicMock()
#         artifact_list = self.nexus_handler.build_artifact_list()
#         self.assertEqual(artifact_list.path, Path(VNF_OUTPUT_FOLDER_FILENAME, ARTIFACT_LIST_FILENAME))
#         self.assertIsInstance(artifact_list, ArtifactDefinitionElementBuilder)

#     def test_build_resource_bicep_type(self):
#         """Testing build resource bicep for Nexus VNFs

#         We only need to test the type of the bicep and the supporting files,
#         and that they have the correct names.
#         This is because the complicated logic is tested in the processors tests.

#         """
#         # we are testing the rest of the logic in the processors? (are we? we should)
#         # TODO: fix this mocking, it works for deploymentParameters but not for actual processors (duh?)
#         self.nexus_handler.processors = MagicMock()
#         resource_bicep = self.nexus_handler.build_resource_bicep()
#         print(resource_bicep.supporting_files[0].path)
#         # TODO: check that the nexus one contains deploymentParameters, imageParameters and at least one templateParams?
#         self.assertIsInstance(resource_bicep.supporting_files, List[LocalFileBuilder])
#         self.assertIsInstance(resource_bicep, BicepDefinitionElementBuilder)

#     # def test_build_all_parameters_json():
