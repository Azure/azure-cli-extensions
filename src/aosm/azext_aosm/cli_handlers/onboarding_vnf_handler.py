# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
from pathlib import Path
from typing import Dict, Any
from knack.log import get_logger

from azext_aosm.build_processors.arm_processor import (
    AzureCoreArmBuildProcessor, BaseArmBuildProcessor)
from azext_aosm.build_processors.vhd_processor import VHDProcessor
from azext_aosm.common.constants import (ARTIFACT_LIST_FILENAME,
                                         BASE_FOLDER_NAME,
                                         MANIFEST_FOLDER_NAME,
                                         NF_DEFINITION_FOLDER_NAME,
                                         VNF_BASE_TEMPLATE_FILENAME,
                                         VNF_TEMPLATE_FOLDER_NAME,
                                         VNF_DEFINITION_TEMPLATE_FILENAME,
                                         VNF_INPUT_FILENAME,
                                         VNF_MANIFEST_TEMPLATE_FILENAME,
                                         VNF_OUTPUT_FOLDER_FILENAME,
                                         DEPLOYMENT_PARAMETERS_FILENAME,
                                         VHD_PARAMETERS_FILENAME,
                                         TEMPLATE_PARAMETERS_FILENAME)
from azext_aosm.common.local_file_builder import LocalFileBuilder
from azext_aosm.configuration_models.onboarding_vnf_input_config import (
    OnboardingVNFInputConfig,
)
from azext_aosm.configuration_models.common_parameters_config import (
    VNFCommonParametersConfig,
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
from azext_aosm.inputs.vhd_file_input import VHDFileInput

from .onboarding_nfd_base_handler import OnboardingNFDBaseCLIHandler

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

    def _get_input_config(self, input_config: Dict[str, Any] = None) -> OnboardingVNFInputConfig:
        """Get the configuration for the command."""
        if input_config is None:
            input_config = {}
        return OnboardingVNFInputConfig(**input_config)

    def _get_params_config(
        self, config_file: dict = None
    ) -> VNFCommonParametersConfig:
        """Get the configuration for the command."""
        with open(config_file, "r", encoding="utf-8") as _file:
            params_dict = json.load(_file)
        if params_dict is None:
            params_dict = {}
        return VNFCommonParametersConfig(**params_dict)

    def _get_processor_list(self):
        processor_list = []
        # for each arm template, instantiate arm processor
        for arm_template in self.config.arm_templates:
            arm_input = ArmTemplateInput(
                artifact_name=arm_template.artifact_name,
                artifact_version=arm_template.version,
                default_config=None,
                template_path=Path(arm_template.file_path).absolute(),
            )
            # TODO: generalise for nexus in nexus ready stories
            processor_list.append(
                AzureCoreArmBuildProcessor(arm_input.artifact_name, arm_input)
            )

        # Instantiate vhd processor
        if not self.config.vhd.artifact_name:
            self.config.vhd.artifact_name = self.config.nf_name + "-vhd"
        vhd_processor = VHDProcessor(
            name=self.config.vhd.artifact_name,
            input_artifact=VHDFileInput(
                artifact_name=self.config.vhd.artifact_name,
                artifact_version=self.config.vhd.version,
                default_config=self._get_default_config(self.config.vhd),
                file_path=Path(self.config.vhd.file_path).absolute(),
                blob_sas_uri=self.config.vhd.blob_sas_url,
            ),
        )
        processor_list.append(vhd_processor)
        return processor_list

    def build_base_bicep(self):
        """Build the base bicep file."""
        # Build manifest bicep contents, with j2 template
        template_path = self._get_template_path(
            VNF_TEMPLATE_FOLDER_NAME, VNF_BASE_TEMPLATE_FILENAME
        )
        bicep_contents = self._render_base_bicep_contents(template_path)
        # Create Bicep element with manifest contents
        bicep_file = BicepDefinitionElementBuilder(
            Path(VNF_OUTPUT_FOLDER_FILENAME, BASE_FOLDER_NAME), bicep_contents
        )
        return bicep_file

    def build_manifest_bicep(self):
        """Build the manifest bicep file."""
        acr_artifact_list = []

        logger.info("Creating artifact manifest bicep")

        for processor in self.processors:
            if isinstance(processor, BaseArmBuildProcessor):
                acr_artifact_list.extend(processor.get_artifact_manifest_list())
                logger.debug(
                    "Created list of artifacts from %s arm template(s) provided: %s",
                    len(self.config.arm_templates),
                    acr_artifact_list,
                )
            elif isinstance(processor, VHDProcessor):
                sa_artifact_list = processor.get_artifact_manifest_list()
                logger.debug(
                    "Created list of artifacts from vhd image provided: %s",
                    sa_artifact_list,
                )

        # Build manifest bicep contents, with j2 template
        template_path = self._get_template_path(
            VNF_TEMPLATE_FOLDER_NAME, VNF_MANIFEST_TEMPLATE_FILENAME
        )
        bicep_contents = self._render_manifest_bicep_contents(
            template_path, acr_artifact_list, sa_artifact_list
        )
        # Create Bicep element with manifest contents
        bicep_file = BicepDefinitionElementBuilder(
            Path(VNF_OUTPUT_FOLDER_FILENAME, MANIFEST_FOLDER_NAME),
            bicep_contents,
        )

        logger.info("Created artifact manifest bicep element")
        return bicep_file

    def build_artifact_list(self):
        """Build the artifact list."""
        logger.info("Creating artifacts list for artifacts.json")
        artifact_list = []
        # For each arm template, get list of artifacts and combine
        for processor in self.processors:
            (artifacts, _) = processor.get_artifact_details()
            if artifacts not in artifact_list:
                artifact_list.extend(artifacts)
        logger.debug(
            "Created list of artifact details from %s arm template(s) and the vhd image provided: %s",
            len(self.config.arm_templates),
            artifact_list,
        )

        # Generate Artifact Element with artifact list (of arm template and vhd images)
        return ArtifactDefinitionElementBuilder(
            Path(VNF_OUTPUT_FOLDER_FILENAME, ARTIFACT_LIST_FILENAME), artifact_list
        )

    def build_resource_bicep(self):
        """Build the resource bicep file."""
        logger.info("Creating artifacts list for artifacts.json")
        acr_nf_application_list = []
        sa_nf_application_list = []
        supporting_files = []
        schema_properties = {}

        for processor in self.processors:
            nf_application = processor.generate_nf_application()
            logger.debug("Created nf application %s", nf_application.name)

            # Generate deploymentParameters schema properties
            params_schema = processor.generate_params_schema()
            schema_properties.update(params_schema)

            # For each arm template, generate nf application
            if isinstance(processor, BaseArmBuildProcessor):

                acr_nf_application_list.append(nf_application)

                # Generate local file for template_parameters + add to supporting files list
                params = (
                    nf_application.deploy_parameters_mapping_rule_profile.template_mapping_rule_profile.template_parameters
                )
                template_name = TEMPLATE_PARAMETERS_FILENAME
                logger.info(
                    "Created templatateParameters as supporting file for nfDefinition bicep"
                )
            elif isinstance(processor, VHDProcessor):
                # Generate NF Application
                # nf_application = processor.generate_nf_application()
                sa_nf_application_list.append(nf_application)
                # Generate local file for vhd_parameters
                params = (
                    nf_application.deploy_parameters_mapping_rule_profile.vhd_image_mapping_rule_profile.user_configuration
                )
                template_name = VHD_PARAMETERS_FILENAME
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
        template_path = self._get_template_path(
            VNF_TEMPLATE_FOLDER_NAME, VNF_DEFINITION_TEMPLATE_FILENAME
        )

        params = {
            "acr_nf_applications": acr_nf_application_list,
            "sa_nf_application": sa_nf_application_list[0],
            "deployment_parameters_file": DEPLOYMENT_PARAMETERS_FILENAME,
            "vhd_parameters_file": VHD_PARAMETERS_FILENAME,
            "template_parameters_file": TEMPLATE_PARAMETERS_FILENAME
        }
        bicep_contents = self._render_definition_bicep_contents(
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

    def build_all_parameters_json(self):
        params_content = {
            "location": self.config.location,
            "publisherName": self.config.publisher_name,
            "publisherResourceGroupName": self.config.publisher_resource_group_name,
            "acrArtifactStoreName": self.config.acr_artifact_store_name,
            "saArtifactStoreName": self.config.blob_artifact_store_name,
            "acrManifestName":  self.config.acr_artifact_store_name + "-manifest",
            "saManifestName": self.config.blob_artifact_store_name + "-manifest",
            "nfDefinitionGroup": self.config.nf_name,
            "nfDefinitionVersion": self.config.version
        }
        base_file = JSONDefinitionElementBuilder(
            Path(VNF_OUTPUT_FOLDER_FILENAME), json.dumps(params_content, indent=4)
        )
        return base_file

    def _get_default_config(self, vhd):
        default_config = {}
        if vhd.image_disk_size_GB:
            default_config.update({"image_disk_size_GB": vhd.image_disk_size_GB})
        if vhd.image_hyper_v_generation:
            default_config.update(
                {"image_hyper_v_generation": vhd.image_hyper_v_generation}
            )
        else:
            # Default to V1 if not specified
            default_config.update({"image_hyper_v_generation": "V1"})
        if vhd.image_api_version:
            default_config.update({"image_api_version": vhd.image_api_version})
        return default_config
