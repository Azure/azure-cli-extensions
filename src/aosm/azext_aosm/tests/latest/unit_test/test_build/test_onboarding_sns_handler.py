# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from azext_aosm.cli_handlers.onboarding_sns_handler import OnboardingSNSCLIHandler
from azext_aosm.configuration_models.sns_parameters_config import SNSCommonParametersConfig
from azext_aosm.vendored_sdks import HybridNetworkManagementClient
from azext_aosm.vendored_sdks.models import (
    NetworkServiceDesignVersion,
)
from azext_aosm.common.constants import (
    SNS_OUTPUT_FOLDER_FILENAME,
)

class TestOnboardingSNSCLIHandler(unittest.TestCase):
    @patch('azext_aosm.cli_handlers.onboarding_sns_handler.get_template_path')
    @patch('azext_aosm.cli_handlers.onboarding_sns_handler.render_bicep_contents_from_j2')
    @patch('azext_aosm.cli_handlers.onboarding_sns_handler.BicepDefinitionElementBuilder')
    def test_build_resource_bicep(self, mock_bicep_builder, mock_render_bicep, mock_get_template_path):
        # Arrange
        mock_get_template_path.return_value = 'template_path'
        mock_render_bicep.return_value = 'bicep_contents'
        mock_bicep_builder.return_value = 'bicep_file'
        handler = OnboardingSNSCLIHandler()
        handler.nsdv = MagicMock()
        handler.nsdv.id = 'nsdv_id'
        # Act
        result = handler.build_resource_bicep()
        
        # Assert
        mock_get_template_path.assert_called_once_with('sns', 'snsdefinition.bicep.j2')
        mock_render_bicep.assert_called_once_with('template_path', {'cgvs': [],'nsdvId': 'nsdv_id'})
        mock_bicep_builder.assert_called_once_with(Path('sns-cli-output', 'snsDefinition'), 'bicep_contents')
        self.assertEqual(result, 'bicep_file')
    
    @patch('azext_aosm.cli_handlers.onboarding_sns_handler.CommandContext')
    @patch('azext_aosm.cli_handlers.onboarding_sns_handler.DefinitionFolder')
    def test_deploy(self, mock_definition_folder, mock_command_context):
        # Arrange
        mock_definition_folder_instance = mock_definition_folder.return_value
        mock_command_context_instance = mock_command_context.return_value
        handler = OnboardingSNSCLIHandler()
        handler.config = SNSCommonParametersConfig('location', 'operatorResourceGroupName', 'siteName' , 'snsName', 'userIdentityResourceId')

        # Act
        handler.deploy(mock_command_context_instance)

        # Assert
        mock_definition_folder.assert_called_once_with(mock_command_context_instance.cli_options["definition_folder"])
        mock_definition_folder_instance.deploy.assert_called_once_with(config=handler.config, command_context=mock_command_context_instance)

    @patch('azext_aosm.cli_handlers.onboarding_sns_handler.SNSDeploymentInputDefinitionElementBuilder')
    @patch('azext_aosm.cli_handlers.onboarding_sns_handler.OnboardingSNSCLIHandler._get_nsdv')
    def test_build_deploy_input(self, mock_get_nsdv, mock_deployment_input_builder):
        # Arrange
        mock_get_nsdv.return_value = NetworkServiceDesignVersion(location='location', properties=MagicMock(nfvis_from_site='nfvis_from_site'))
        handler = OnboardingSNSCLIHandler()

        # Act
        result = handler.build_deploy_input()

        # Assert
        mock_get_nsdv.assert_called_once()
        mock_deployment_input_builder.assert_called_once_with(Path(SNS_OUTPUT_FOLDER_FILENAME), 'nfvis_from_site', [])
        self.assertEqual(result, mock_deployment_input_builder.return_value)

    @patch('azext_aosm.cli_handlers.onboarding_sns_handler.OnboardingSNSCLIHandler._get_cgSchema')
    def test_generate_cgv_filenames(self, mock_get_cgSchema):
        # Setup
        handler = OnboardingSNSCLIHandler()
        nsdv_mock = MagicMock()
        nsdv_mock.properties.configuration_group_schema_references = ['schema1']
        handler.nsdv = nsdv_mock
        mock_get_cgSchema.return_value = MagicMock(id='id1', properties=MagicMock(schema_definition='{}'))
        # Act
        handler._generate_cgv_filenames()
        # Assert
        self.assertEqual(len(handler.schema_to_cgv_map), 1)
        self.assertIn('schema1', handler.schema_to_cgv_map[0]['cgs_name'])
    