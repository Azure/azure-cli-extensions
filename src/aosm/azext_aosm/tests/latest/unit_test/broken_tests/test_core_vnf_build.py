# from unittest import TestCase
# from unittest.mock import patch, MagicMock, Mock
# from pathlib import Path
# from typing import List
# from azext_aosm.cli_handlers.onboarding_core_vnf_handler import OnboardingCoreVNFCLIHandler
# from azext_aosm.definition_folder.builder.artifact_builder import ArtifactDefinitionElementBuilder
# from azext_aosm.definition_folder.builder.bicep_builder import BicepDefinitionElementBuilder
# from azext_aosm.definition_folder.builder.local_file_builder import LocalFileBuilder
# from azext_aosm.common.constants import VNF_OUTPUT_FOLDER_FILENAME, ARTIFACT_LIST_FILENAME
# from azext_aosm.build_processors.arm_processor import AzureCoreArmBuildProcessor
# from azext_aosm.build_processors.vhd_processor import VHDProcessor
# from azext_aosm.vendored_sdks.models import (
#     AzureCoreVhdImageDeployMappingRuleProfile, AzureCoreNetworkFunctionVhdApplication,
#     AzureCoreVhdImageArtifactProfile, VhdImageArtifactProfile, VhdImageMappingRuleProfile, ApplicationEnablement
#     )

# class VNFCoreBuildTest(TestCase):

#     def setUp(self):
#         self.vnf_handler = OnboardingCoreVNFCLIHandler()

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
#         self.vnf_handler.processors = MagicMock()
#         artifact_list = self.vnf_handler.build_artifact_list()
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
#         # mocked_input = MagicMock()
#         # arm_processor = AzureCoreArmProcessor(mocked_input)
#         arm_input = MagicMock()
#         vhd_input = MagicMock()
#         arm_processor = AzureCoreArmBuildProcessor("arm_test", arm_input)
#         vhd_processor = VHDProcessor("test_vhd", vhd_input)
#         arm_processor = MagicMock(spec=AzureCoreArmBuildProcessor)
#         vhd_processor = MagicMock(spec=VHDProcessor)
#         # arm_processor = Mock(spec=AzureCoreArmBuildProcessor)
#         # vhd_processor = Mock(spec=VHDProcessor)
#         # assert isinstance(arm_processor, AzureCoreArmBuildProcessor)
#         # # TODO: one of these returns local file build
#         # vhd_processor.generate_nf_application.return_value = AzureCoreNetworkFunctionVhdApplication(name="test",depends_on_profile=None,
#         #                                                                                             artifact_profile=AzureCoreVhdImageArtifactProfile(
#         #                                                                                                 artifact_store=None,
#         #                                                                                                 vhd_artifact_profile=VhdImageArtifactProfile(
#         #                                                                                                     vhd_name="vhd_name",
#         #                                                                                                     vhd_version="1-0-0",
#         #                                                                                                 ),), deploy_parameters_mapping_rule_profile=AzureCoreVhdImageDeployMappingRuleProfile(
#         #                                                                                                     application_enablement=ApplicationEnablement.ENABLED,
#         #                                                                                                     vhd_image_mapping_rule_profile=VhdImageMappingRuleProfile(user_configuration=None)
#         #                                                                                                     )
#         #                                                                                             )
#         arm_processor.generate_params_schema.return_value = {}
#         # arm_processor.generate_parameters_file.return_value = LocalFileBuilder("", {})
#         vhd_processor.generate_params_schema.return_value = {}
#         # We want to test a specific private method so disable the pylint warning
#         # pylint: disable=protected-access
#         vhd_processor._generate_mapping_rule_profile.return_value = AzureCoreVhdImageDeployMappingRuleProfile(application_enablement=None, vhd_image_mapping_rule_profile=None)
#         self.vnf_handler.processors = [arm_processor, vhd_processor]
#         resource_bicep = self.vnf_handler.build_resource_bicep()
#         print(resource_bicep.supporting_files[1].path)
#         # TODO: check that the nexus one contains deploymentParameters, imageParameters and at least one templateParams?
#         # special assert?
#         self.assertIsInstance(resource_bicep.supporting_files, List[LocalFileBuilder])
#         self.assertIsInstance(resource_bicep, BicepDefinitionElementBuilder)

#     # def test_build_all_parameters_json():
#     # def test_build_artifact_manifest(self):
#     #     # self.vnf_handler._generate_type_specific_artifact_manifest
#     #     self.vnf_handler.processors = MagicMock()
#     #     manifest_bicep = self.vnf_handler.build_manifest_bicep()
#     #     # We want to test a specific private method so disable the pylint warning
#     #     # pylint: disable=protected-access
#     #     (arm_list, sa_list) = self.vnf_handler._generate_type_specific_artifact_manifest(self.vnf_handler.processors[0])
#     #     self.assertEqual()
        
