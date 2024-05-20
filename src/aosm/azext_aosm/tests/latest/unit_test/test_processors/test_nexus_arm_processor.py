# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import logging
import sys
import json
from unittest import TestCase
from unittest.mock import MagicMock
from azext_aosm.build_processors.arm_processor import NexusArmBuildProcessor
from azext_aosm.inputs.arm_template_input import ArmTemplateInput
from azext_aosm.vendored_sdks.models import (
    AzureOperatorNexusNetworkFunctionArmTemplateApplication,
    ApplicationEnablement, ArmResourceDefinitionResourceElementTemplate,
    ArmResourceDefinitionResourceElementTemplateDetails,
    ArmTemplateArtifactProfile,
    ArmTemplateMappingRuleProfile,
    NSDArtifactProfile,
    TemplateType,
    AzureOperatorNexusArmTemplateDeployMappingRuleProfile,
    AzureOperatorNexusArmTemplateArtifactProfile,
    DependsOnProfile,
    ManifestArtifactFormat,
    ReferencedResource,
)
from azext_aosm.definition_folder.builder.local_file_builder import LocalFileBuilder
from azext_aosm.common.artifact import LocalFileACRArtifact
from azext_aosm.common.constants import TEMPLATE_PARAMETERS_FILENAME

code_directory = os.path.dirname(__file__)
parent_directory = os.path.abspath(os.path.join(code_directory, "../.."))
mock_vnf_directory = os.path.join(parent_directory, "mock_nexus_vnf")


class NexusArmProcessorTest(TestCase):
    """Class to test Nexus ARM Processor functionality"""
    def setUp(self):
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        mock_arm_template_path = os.path.join(mock_vnf_directory, "ubuntu-template.json")
        self.nexus_arm_input = ArmTemplateInput(
            artifact_name="test-artifact-name",
            artifact_version="1.1.1",
            template_path=mock_arm_template_path,
            default_config=None
        )
        self.processor = NexusArmBuildProcessor("test-name", self.nexus_arm_input, expose_all_params=False)

    def test_get_artifact_manifest_list(self):
        """Test get artifact manifest list for nexus arm processor."""
        manifest_list = self.processor.get_artifact_manifest_list()
        mock_manifest_artifact_format = ManifestArtifactFormat(
            artifact_name="test-artifact-name",
            artifact_type="ArmTemplate",
            artifact_version="1.1.1",
        )
        self.assertEqual(len(manifest_list), 1)
        self.assertIsInstance(manifest_list[0], ManifestArtifactFormat)
        self.assertEqual(manifest_list[0], mock_manifest_artifact_format)
        assert True

    def test_artifact_details(self):
        """Test get artifact details for nexus arm processor."""
        artifact_details = self.processor.get_artifact_details()
        mock_arm_template_path = os.path.join(mock_vnf_directory, "ubuntu-template.json")
        mock_artifact = [LocalFileACRArtifact(
            artifact_name="test-artifact-name",
            artifact_type="ArmTemplate",
            artifact_version="1.1.1",
            file_path=mock_arm_template_path,
        )]

        # Ensure no list of LocalFileBuilders is returned, as this is only for NSDs
        self.assertEqual(artifact_details[0][0].artifact_name, mock_artifact[0].artifact_name)
        self.assertEqual(artifact_details[0][0].artifact_version, mock_artifact[0].artifact_version)
        self.assertEqual(artifact_details[0][0].artifact_type, mock_artifact[0].artifact_type)
        self.assertEqual(artifact_details[0][0].file_path, mock_artifact[0].file_path)
        self.assertEqual(artifact_details[1], [])
        assert True

    def test_generate_nf_application(self):
        """Test generate nf application for nexus arm processor."""
        # Check type is correct, other functionality is tested in appropriate functions
        # (such as test_generate_artifact_profile)
        nf_application = self.processor.generate_nf_application()
        self.assertIsInstance(nf_application,
                              AzureOperatorNexusNetworkFunctionArmTemplateApplication)

    def test_generate_resource_element_template(self):
        """Test generate RET for Nexus ARM Processor"""
        result = self.processor.generate_resource_element_template()

        # Assert the expected output
        expected_template = ArmResourceDefinitionResourceElementTemplateDetails(
            name="test-name",
            depends_on_profile=DependsOnProfile(
                install_depends_on=[], uninstall_depends_on=[], update_depends_on=[]
            ),
            configuration=ArmResourceDefinitionResourceElementTemplate(
                template_type=TemplateType.ARM_TEMPLATE.value,
                parameter_values=json.dumps({}),
                artifact_profile=NSDArtifactProfile(
                    artifact_store_reference=ReferencedResource(id=""),
                    artifact_name=self.processor.input_artifact.artifact_name,
                    artifact_version=self.processor.input_artifact.artifact_version,
                ),
            ),
        )
        # Assert each parameter equal
        self.assertEqual(result.name, expected_template.name)
        self.assertEqual(result.depends_on_profile, expected_template.depends_on_profile)
        self.assertEqual(result.configuration.artifact_profile,
                         expected_template.configuration.artifact_profile)

    def test_generate_parameters_file(self):
        """ Test generate parameters file for Nexus ARM Processor"""

        # Mock private function
        # (generate mapping rule profile is tested elsewhere)
        mapping_rule_profile = MagicMock()
        mock_params = '{"param1": "value1", "param2": "value2"}'
        mapping_rule_profile.template_mapping_rule_profile.template_parameters = mock_params
        self.processor._generate_mapping_rule_profile = MagicMock(return_value=mapping_rule_profile)

        parameters_file = self.processor.generate_parameters_file()

        # Assert the expected behaviour
        expected_params = {
            "param1": "value1",
            "param2": "value2"
        }
        expected_json = json.dumps(expected_params, indent=4)

        # Assert the contents
        self.assertEqual(parameters_file.file_content, expected_json)
        # Assert name of the file includes templateParameters
        # (We want to know that in the instance of Nexus ARM Templates,
        # we are creating template parameters)
        assert TEMPLATE_PARAMETERS_FILENAME in str(parameters_file.path)
        # Assert the type is LocalFileBuilder
        self.assertIsInstance(parameters_file, LocalFileBuilder)
        # Assert that the necessary methods were called
        self.processor._generate_mapping_rule_profile.assert_called_once()

    def test_generate_mapping_rule_profile(self):
        """ Test generate artifact profile returned correctly with generate_nf_application."""
        nf_application = self.processor.generate_nf_application()
        mock_template_params = json.dumps({
            "subnetName": "{deployParameters.test-name.subnetName}",
            "virtualNetworkId": "{deployParameters.test-name.virtualNetworkId}",
            "sshPublicKeyAdmin": "{deployParameters.test-name.sshPublicKeyAdmin}",
            "imageName": "{deployParameters.test-name.imageName}"
        })
        expected_arm_mapping_profile = ArmTemplateMappingRuleProfile(
            template_parameters=mock_template_params)
        expected_nexus_arm_mapping_profile = AzureOperatorNexusArmTemplateDeployMappingRuleProfile(
            application_enablement=ApplicationEnablement.ENABLED,
            template_mapping_rule_profile=expected_arm_mapping_profile,
        )
        self.assertEqual(nf_application.deploy_parameters_mapping_rule_profile,
                         expected_nexus_arm_mapping_profile)
        self.assertIsInstance(nf_application.deploy_parameters_mapping_rule_profile,
                              AzureOperatorNexusArmTemplateDeployMappingRuleProfile)

    def test_generate_artifact_profile(self):
        """ Test generate artifact profile returned correctly with generate_nf_application."""

        nf_application = self.processor.generate_nf_application()
        expected_arm_artifact_profile = ArmTemplateArtifactProfile(
            template_name="test-artifact-name", template_version="1.1.1")
        expected_nexus_arm_artifact_profile = AzureOperatorNexusArmTemplateArtifactProfile(
            artifact_store=ReferencedResource(id=""),
            template_artifact_profile=expected_arm_artifact_profile
        )
        self.assertEqual(nf_application.artifact_profile, expected_nexus_arm_artifact_profile)
        self.assertIsInstance(nf_application.artifact_profile,
                              AzureOperatorNexusArmTemplateArtifactProfile)
