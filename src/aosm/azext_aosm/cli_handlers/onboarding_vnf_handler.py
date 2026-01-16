# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations
import json

from pathlib import Path
from abc import abstractmethod
from typing import Optional
from .onboarding_nfd_base_handler import OnboardingNFDBaseCLIHandler
from knack.log import get_logger
from azext_aosm.build_processors.arm_processor import BaseArmBuildProcessor
from azext_aosm.build_processors.vhd_processor import VHDProcessor
from azext_aosm.common.utils import render_bicep_contents_from_j2, get_template_path
from azext_aosm.configuration_models.onboarding_vnf_input_config import (
    OnboardingNFDBaseInputConfig)

from azext_aosm.definition_folder.builder.bicep_builder import (
    BicepDefinitionElementBuilder,
)
from azext_aosm.definition_folder.builder.artifact_builder import ArtifactDefinitionElementBuilder
from azext_aosm.definition_folder.builder.json_builder import JSONDefinitionElementBuilder

from azext_aosm.common.constants import (
    ARTIFACT_LIST_FILENAME,
    NF_DEFINITION_FOLDER_NAME,
    VNF_DEFINITION_TEMPLATE_FILENAME,
    VNF_INPUT_FILENAME,
    VNF_OUTPUT_FOLDER_FILENAME,
    VNF_TEMPLATE_FOLDER_NAME,
    MANIFEST_FOLDER_NAME,
    VNF_MANIFEST_TEMPLATE_FILENAME,
    BASE_FOLDER_NAME
)

logger = get_logger(__name__)


class OnboardingVNFCLIHandler(OnboardingNFDBaseCLIHandler):
    """CLI handler for publishing NFDs."""

    config: OnboardingNFDBaseInputConfig
    processors: list[BaseArmBuildProcessor | VHDProcessor]

    @property
    def default_config_file_name(self) -> str:
        """Get the default configuration file name."""
        return VNF_INPUT_FILENAME

    @property
    def output_folder_file_name(self) -> str:
        """Get the output folder file name."""
        return VNF_OUTPUT_FOLDER_FILENAME

    def _get_input_config(
        self, input_config_dict: Optional[dict] = None
    ) -> OnboardingNFDBaseInputConfig:
        """Get the configuration for the command."""
        if input_config_dict is None:
            input_config_dict = {}
        return self.input_config(**input_config_dict)

    def _get_params_config(
        self, config_file: Path
    ) -> OnboardingNFDBaseInputConfig:
        """Get the configuration for the command."""
        with open(config_file, "r", encoding="utf-8") as _file:
            params_dict = json.load(_file)
        if params_dict is None:
            params_dict = {}
        return self.params_config(**params_dict)

    def build_base_bicep(self) -> BicepDefinitionElementBuilder:
        """Build the base bicep file."""
        template_path = get_template_path(
            VNF_TEMPLATE_FOLDER_NAME, self.base_template_filename
        )
        bicep_contents = render_bicep_contents_from_j2(template_path, {})
        bicep_file = BicepDefinitionElementBuilder(
            Path(VNF_OUTPUT_FOLDER_FILENAME, BASE_FOLDER_NAME), bicep_contents
        )
        return bicep_file

    def build_artifact_list(self) -> ArtifactDefinitionElementBuilder:
        """Build the artifact list.

        Gets list of artifacts to be including in the artifacts.json.
        This is used during the publish command, to upload the artifacts correctly.

        """
        logger.info("Creating artifacts list for artifacts.json")
        # assert isinstance(self.config, OnboardingBaseVNFInputConfig)
        artifact_list = []
        # For each arm template, get list of artifacts and combine
        for processor in self.processors:
            (artifacts, _) = processor.get_artifact_details()
            if artifacts not in artifact_list:
                artifact_list.extend(artifacts)
        logger.debug(
            "Created list of artifact details from %s arm template(s) and the image provided: %s",
            len(self.config.arm_templates),
            artifact_list,
        )

        # Generate Artifact Element with artifact list (of arm template and vhd images)
        return ArtifactDefinitionElementBuilder(
            Path(VNF_OUTPUT_FOLDER_FILENAME, ARTIFACT_LIST_FILENAME), artifact_list
        )

    def build_resource_bicep(self) -> BicepDefinitionElementBuilder:
        """Build the resource bicep file.

        Creates nfDefinition.bicep and its supporting files.

        For each processor:
        - Generates NF application for each processor
        - Generates deployParameters (flattened to be one schema overall)
        - Generates supporting parameters files (to avoid stringified JSON in template)

        """
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

            # Generate deployParameters schema properties
            params_schema = processor.generate_schema()
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

        # Create the bicep element
        bicep_file = BicepDefinitionElementBuilder(
            Path(VNF_OUTPUT_FOLDER_FILENAME, NF_DEFINITION_FOLDER_NAME),
            bicep_contents,
        )
        # Add deployParameters, vhdParameters and templateParameters as supporting files
        for supporting_file in supporting_files:
            bicep_file.add_supporting_file(supporting_file)

        # Add the deployParameters schema file
        bicep_file.add_supporting_file(
            self._render_deploy_params_schema(
                schema_properties, VNF_OUTPUT_FOLDER_FILENAME, NF_DEFINITION_FOLDER_NAME
            )
        )
        return bicep_file

    def build_manifest_bicep(self) -> BicepDefinitionElementBuilder:
        """Build the manifest bicep file."""
        acr_artifact_list = []
        sa_artifact_list = []

        logger.info("Creating artifact manifest bicep")

        for processor in self.processors:
            (arm_artifact, sa_artifact) = self._generate_type_specific_artifact_manifest(processor)
            acr_artifact_list.extend(arm_artifact)
            sa_artifact_list.extend(sa_artifact)

        # Build manifest bicep contents, with j2 template
        template_path = get_template_path(
            VNF_TEMPLATE_FOLDER_NAME, VNF_MANIFEST_TEMPLATE_FILENAME
        )
        params = {
            "acr_artifacts": acr_artifact_list,
            "sa_artifacts": sa_artifact_list
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

    def build_all_parameters_json(self) -> JSONDefinitionElementBuilder:
        """Build the all parameters json file."""
        params_content = self.get_params_content()
        base_file = JSONDefinitionElementBuilder(
            Path(VNF_OUTPUT_FOLDER_FILENAME), json.dumps(params_content, indent=4)
        )
        return base_file

    @abstractmethod
    def _get_nfd_template_params(self, arm_nf_application_list, image_nf_application_list):
        return NotImplementedError

    @abstractmethod
    def _generate_type_specific_nf_application(self, processor):
        return NotImplementedError

    @abstractmethod
    def _generate_type_specific_artifact_manifest(self, processor):
        return NotImplementedError

    def _validate_arm_template(self):
        for processor in self.processors:
            if isinstance(processor, BaseArmBuildProcessor):
                processor.input_artifact.validate_resource_types()

    def pre_validate_build(self):
        """Run all validation functions required before building the vnf."""
        logger.debug("Pre-validating build")

        self._validate_arm_template()

    @property
    def input_config(self):
        raise NotImplementedError

    @property
    def params_config(self):
        raise NotImplementedError

    @property
    def base_template_filename(self):
        raise NotImplementedError

    def get_params_content(self):
        raise NotImplementedError
