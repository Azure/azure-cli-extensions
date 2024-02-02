# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import re
from pathlib import Path
from typing import Dict, Any
from knack.log import get_logger

from azext_aosm.build_processors.arm_processor import NexusArmBuildProcessor
from azext_aosm.build_processors.nexus_image_processor import NexusImageProcessor
from azext_aosm.build_processors.base_processor import BaseInputProcessor
from azext_aosm.common.constants import (ARTIFACT_LIST_FILENAME,
                                         BASE_FOLDER_NAME,
                                         MANIFEST_FOLDER_NAME,
                                         NF_DEFINITION_FOLDER_NAME,
                                         VNF_TEMPLATE_FOLDER_NAME,
                                         VNF_DEFINITION_TEMPLATE_FILENAME,
                                         VNF_INPUT_FILENAME,
                                         VNF_MANIFEST_TEMPLATE_FILENAME,
                                         VNF_OUTPUT_FOLDER_FILENAME,
                                         DEPLOYMENT_PARAMETERS_FILENAME,
                                         NEXUS_IMAGE_PARAMETERS_FILENAME,
                                         TEMPLATE_PARAMETERS_FILENAME,
                                         VNF_NEXUS_BASE_TEMPLATE_FILENAME,
                                         SEMVER_REGEX)
from azext_aosm.common.local_file_builder import LocalFileBuilder
from azext_aosm.configuration_models.onboarding_vnf_input_config import (
    OnboardingNexusVNFInputConfig,
)
from azext_aosm.configuration_models.common_parameters_config import (
    NexusVNFCommonParametersConfig,
)
from azext_aosm.definition_folder.builder.artifact_builder import (
    ArtifactDefinitionElementBuilder,
)
from azext_aosm.definition_folder.builder.bicep_builder import (
    BicepDefinitionElementBuilder,
)
from azext_aosm.definition_folder.builder.json_builder import (
    JSONDefinitionElementBuilder,
)
from azext_aosm.inputs.arm_template_input import ArmTemplateInput
from azext_aosm.inputs.nexus_image_input import NexusImageFileInput
from .onboarding_vnf_handler import OnboardingVNFCLIHandler
from azext_aosm.common.utils import render_bicep_contents_from_j2, get_template_path

logger = get_logger(__name__)


class OnboardingNexusVNFCLIHandler(OnboardingVNFCLIHandler):
    """CLI handler for publishing NFDs."""

    @property
    def default_config_file_name(self) -> str:
        """Get the default configuration file name."""
        return VNF_INPUT_FILENAME

    @property
    def output_folder_file_name(self) -> str:
        """Get the output folder file name."""
        return VNF_OUTPUT_FOLDER_FILENAME

    def _get_input_config(
        self, input_config: Dict[str, Any] = None
    ) -> OnboardingNexusVNFInputConfig:
        """Get the configuration for the command."""
        if input_config is None:
            input_config = {}
        return OnboardingNexusVNFInputConfig(**input_config)

    def _get_params_config(
        self, config_file: dict = None
    ) -> NexusVNFCommonParametersConfig:
        """Get the configuration for the command."""
        with open(config_file, "r", encoding="utf-8") as _file:
            params_dict = json.load(_file)
        if params_dict is None:
            params_dict = {}
        return NexusVNFCommonParametersConfig(**params_dict)

    def _get_processor_list(self) -> [BaseInputProcessor]:
        processor_list = []
        # for each arm template, instantiate arm processor
        for arm_template in self.config.arm_templates:
            arm_input = ArmTemplateInput(
                artifact_name=arm_template.artifact_name,
                artifact_version=arm_template.version,
                default_config=None,
                template_path=Path(arm_template.file_path).absolute(),
            )
            processor_list.append(
                NexusArmBuildProcessor(arm_input.artifact_name, arm_input)
            )
        # For each image, instantiate image processor
        for image in self.config.images:
            (source_acr_registry, name, version) = self._split_image_path(image)

            # TEMP FIX FOR INVALID VERSIONS
            version = self._create_semver_compatible_version(version)

            image_input = NexusImageFileInput(
                artifact_name=name,
                artifact_version=version,
                default_config=None,
                source_acr_registry=source_acr_registry,
            )
            processor_list.append(
                NexusImageProcessor(image_input.artifact_name, image_input)
            )

        return processor_list

    def build_base_bicep(self) -> BicepDefinitionElementBuilder:
        """Build the base bicep file."""
        # Build manifest bicep contents, with j2 template
        template_path = get_template_path(
            VNF_TEMPLATE_FOLDER_NAME, VNF_NEXUS_BASE_TEMPLATE_FILENAME
        )
        bicep_contents = render_bicep_contents_from_j2(template_path, {})
        # Create Bicep element with manifest contents
        bicep_file = BicepDefinitionElementBuilder(
            Path(VNF_OUTPUT_FOLDER_FILENAME, BASE_FOLDER_NAME), bicep_contents
        )
        return bicep_file

    def build_manifest_bicep(self) -> BicepDefinitionElementBuilder:
        """Build the manifest bicep file."""
        acr_artifact_list = []

        logger.info("Creating artifact manifest bicep")

        for processor in self.processors:
            acr_artifact_list.extend(processor.get_artifact_manifest_list())
            logger.debug(
                "Created list of artifacts from arm template(s) and image files(s) provided: %s",
                acr_artifact_list,
            )

        # Build manifest bicep contents, with j2 template
        template_path = get_template_path(
            VNF_TEMPLATE_FOLDER_NAME, VNF_MANIFEST_TEMPLATE_FILENAME
        )
        params = {
            "acr_artifacts": acr_artifact_list,
            "sa_artifacts": []
        }
        bicep_contents = render_bicep_contents_from_j2(
            template_path, params
        )

        # Create Bicep element with manifest contents
        bicep_file = BicepDefinitionElementBuilder(
            Path(VNF_OUTPUT_FOLDER_FILENAME, MANIFEST_FOLDER_NAME),
            bicep_contents,
        )

        logger.info("Created artifact manifest bicep element")
        return bicep_file

    def build_artifact_list(self) -> ArtifactDefinitionElementBuilder:
        """Build the artifact list."""
        logger.info("Creating artifacts list for artifacts.json")
        artifact_list = []
        # For each arm template, get list of artifacts and combine
        for processor in self.processors:
            (artifacts, _) = processor.get_artifact_details()
            if artifacts not in artifact_list:
                artifact_list.extend(artifacts)
        logger.debug(
            "Created list of artifact details from arm template(s) and image(s) provided: %s",
            artifact_list,
        )

        # Generate Artifact Element with artifact list (of arm template and vhd images)
        return ArtifactDefinitionElementBuilder(
            Path(VNF_OUTPUT_FOLDER_FILENAME, ARTIFACT_LIST_FILENAME), artifact_list
        )

    def build_resource_bicep(self) -> BicepDefinitionElementBuilder:
        """Build the resource bicep file."""
        logger.info("Creating artifacts list for artifacts.json")
        arm_nf_application_list = []
        image_nf_application_list = []
        supporting_files = []
        schema_properties = {}

        for processor in self.processors:
            # Generate NF Application
            nf_application = processor.generate_nf_application()
            logger.debug("Created nf application %s", nf_application.name)

            # Generate deploymentParameters schema properties
            params_schema = processor.generate_params_schema()
            schema_properties.update(params_schema)

            # For each arm template, generate nf application
            if isinstance(processor, NexusArmBuildProcessor):

                arm_nf_application_list.append(nf_application)
                # Generate local file for template_parameters + add to supporting files list
                params = (
                    nf_application.deploy_parameters_mapping_rule_profile.template_mapping_rule_profile.template_parameters
                )
                template_name = TEMPLATE_PARAMETERS_FILENAME
                logger.info(
                    "Created templatateParameters as supporting file for nfDefinition bicep"
                )
            elif isinstance(processor, NexusImageProcessor):
                image_nf_application_list.append(nf_application)
                # Generate local file for vhd_parameters
                params = (
                    nf_application.deploy_parameters_mapping_rule_profile.image_mapping_rule_profile.user_configuration
                )
                template_name = NEXUS_IMAGE_PARAMETERS_FILENAME
            else:
                raise TypeError(f"Type: {type(processor)} is not valid")

            parameters_file = LocalFileBuilder(
                Path(
                    VNF_OUTPUT_FOLDER_FILENAME,
                    NF_DEFINITION_FOLDER_NAME,
                    template_name,
                ),
                json.dumps(json.loads(params), indent=4),
            )
            supporting_files.append(parameters_file)

        # Create bicep contents using vnf defintion j2 template
        template_path = get_template_path(
            VNF_TEMPLATE_FOLDER_NAME, VNF_DEFINITION_TEMPLATE_FILENAME
        )

        params = {
            "nfvi_type": 'AzureOperatorNexus',
            "acr_nf_applications": arm_nf_application_list,
            "sa_nf_applications": [],
            "nexus_image_nf_applications": image_nf_application_list,
            "deployment_parameters_file": DEPLOYMENT_PARAMETERS_FILENAME,
            "template_parameters_file": TEMPLATE_PARAMETERS_FILENAME,
            "image_parameters_file": NEXUS_IMAGE_PARAMETERS_FILENAME
        }
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

    def build_all_parameters_json(self) -> JSONDefinitionElementBuilder:
        """Build the all parameters json file."""
        params_content = {
            "location": self.config.location,
            "publisherName": self.config.publisher_name,
            "publisherResourceGroupName": self.config.publisher_resource_group_name,
            "acrArtifactStoreName": self.config.acr_artifact_store_name,
            "acrManifestName": self.config.acr_artifact_store_name + "-manifest",
            "nfDefinitionGroup": self.config.nf_name,
            "nfDefinitionVersion": self.config.version
        }
        base_file = JSONDefinitionElementBuilder(
            Path(VNF_OUTPUT_FOLDER_FILENAME), json.dumps(params_content, indent=4)
        )
        return base_file

    def _split_image_path(self, image) -> (str, str, str):
        """Split the image path into source acr registry, name and version."""
        (source_acr_registry, name_and_version) = image.split("/", 2)
        (name, version) = name_and_version.split(":", 2)
        return (source_acr_registry, name, version)

    def _create_semver_compatible_version(self, version) -> str:
        """Create a semver compatible version."""
        if re.search(SEMVER_REGEX, version):
            return version
        else:
            print(f"Invalid version {version}, using 1.0.0 as default")
            return '1.0.0'
