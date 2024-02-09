# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from pathlib import Path
from abc import ABC, abstractmethod
from azext_aosm.common.constants import VNF_INPUT_FILENAME, VNF_OUTPUT_FOLDER_FILENAME
from .onboarding_nfd_base_handler import OnboardingNFDBaseCLIHandler
from knack.log import get_logger
from azext_aosm.common.constants import (
                                         NF_DEFINITION_FOLDER_NAME,
                                         VNF_TEMPLATE_FOLDER_NAME,
                                         VNF_DEFINITION_TEMPLATE_FILENAME,
                                         VNF_INPUT_FILENAME)
from azext_aosm.common.utils import render_bicep_contents_from_j2, get_template_path
from azext_aosm.definition_folder.builder.bicep_builder import (
    BicepDefinitionElementBuilder,
)
logger = get_logger(__name__)

class OnboardingVNFCLIHandler(OnboardingNFDBaseCLIHandler):
    """CLI handler for publishing NFDs."""

    @property
    def default_config_file_name(self) -> str:
        """Get the default configuration file name."""
        return VNF_INPUT_FILENAME

    @property
    def output_folder_file_name(self) -> str:
        """Get the output folder file name."""
        return VNF_OUTPUT_FOLDER_FILENAME

    def build_resource_bicep(self) -> BicepDefinitionElementBuilder:
        """Build the resource bicep file."""
        logger.info("Creating artifacts list for artifacts.json")
        arm_nf_application_list = []
        image_nf_application_list = []
        supporting_files = []
        schema_properties = {}

        for processor in self.processors:
            # Generate NF Application + add to correct list for nfd template
            (arm_nf_application, image_nf_application) = self._generate_type_specific_nf_application(processor)
            arm_nf_application_list.extend(arm_nf_application)
            image_nf_application_list.extend(image_nf_application)

            # Generate deploymentParameters schema properties
            params_schema = processor.generate_params_schema()
            schema_properties.update(params_schema)

            # Generate local file for parameters, i.e imageParameters
            parameters_file = processor.generate_parameters_file()
            supporting_files.append(parameters_file)

        # Create bicep contents using vnf defintion j2 template
        template_path = get_template_path(
            VNF_TEMPLATE_FOLDER_NAME, VNF_DEFINITION_TEMPLATE_FILENAME
        )

        params = self._get_nfd_template_params(arm_nf_application_list, image_nf_application_list)
        bicep_contents = render_bicep_contents_from_j2(
            template_path, params
        )

        # Create a bicep element
        # + add its supporting files (deploymentParameters, vhdParameters and templateParameters)
        bicep_file = BicepDefinitionElementBuilder(
            Path(VNF_OUTPUT_FOLDER_FILENAME, NF_DEFINITION_FOLDER_NAME),
            bicep_contents,
        )
        for supporting_file in supporting_files:
            bicep_file.add_supporting_file(supporting_file)

        # Add the deploymentParameters schema file
        bicep_file.add_supporting_file(
            self._render_deployment_params_schema(
                schema_properties, VNF_OUTPUT_FOLDER_FILENAME, NF_DEFINITION_FOLDER_NAME
            )
        )
        return bicep_file

    @abstractmethod
    def _get_nfd_template_params(self, arm_nf_application_list, image_nf_application_list):
        return NotImplementedError

    @abstractmethod
    def _generate_type_specific_nf_application(self, processor):
        return NotImplementedError
