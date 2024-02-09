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
                                         VNF_TEMPLATE_FOLDER_NAME,
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

    # JORDAN: can pull out
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

    def _generate_type_specific_nf_application(self, processor) -> (Any, Any):
        """Generate the type specific nf application."""
        arm_nf = []
        image_nf = []
        nf_application = processor.generate_nf_application()
        print(nf_application)
        if isinstance(processor, NexusArmBuildProcessor):
            arm_nf.append(nf_application)
        elif isinstance(processor, NexusImageProcessor):
            image_nf.append(nf_application)
        else:
            raise TypeError(f"Type: {type(processor)} is not valid")
        logger.debug("Created nf application %s", nf_application.name)
        return (arm_nf, image_nf)

    def _get_nfd_template_params(self, arm_nf_application_list, image_nf_application_list) -> Dict[str, Any]:
        """Get the nfd template params."""
        return {
            "nfvi_type": 'AzureOperatorNexus',
            "acr_nf_applications": arm_nf_application_list,
            "sa_nf_applications": [],
            "nexus_image_nf_applications": image_nf_application_list,
            "deployment_parameters_file": DEPLOYMENT_PARAMETERS_FILENAME,
            "template_parameters_file": TEMPLATE_PARAMETERS_FILENAME,
            "image_parameters_file": NEXUS_IMAGE_PARAMETERS_FILENAME
        }
