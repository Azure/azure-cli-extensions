# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal, Optional

from knack.log import get_logger
from azext_aosm.build_processors.nfd_processor import NFDProcessor
from azext_aosm.build_processors.arm_processor import AzureCoreArmBuildProcessor
from azext_aosm.cli_handlers.onboarding_nfd_base_handler import OnboardingBaseCLIHandler
from azext_aosm.common.constants import (  # NSD_DEFINITION_TEMPLATE_FILENAME,
    ARTIFACT_LIST_FILENAME,
    BASE_FOLDER_NAME,
    CGS_FILENAME,
    CGS_NAME,
    DEPLOY_PARAMETERS_FILENAME,
    MANIFEST_FOLDER_NAME,
    NSD_BASE_TEMPLATE_FILENAME,
    NSD_DEFINITION_FOLDER_NAME,
    NSD_DEFINITION_TEMPLATE_FILENAME,
    NSD_INPUT_FILENAME,
    NSD_MANIFEST_TEMPLATE_FILENAME,
    NSD_OUTPUT_FOLDER_FILENAME,
    NSD_TEMPLATE_FOLDER_NAME,
    TEMPLATE_PARAMETERS_FILENAME,
)
from azext_aosm.configuration_models.common_parameters_config import (
    NSDCommonParametersConfig,
)
from azext_aosm.configuration_models.onboarding_nsd_input_config import (
    OnboardingNSDInputConfig,
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
from azext_aosm.definition_folder.builder.local_file_builder import LocalFileBuilder
from azext_aosm.inputs.arm_template_input import ArmTemplateInput
from azext_aosm.inputs.nfd_input import NFDInput
from azext_aosm.vendored_sdks.models import NetworkFunctionDefinitionVersion
from azext_aosm.common.utils import render_bicep_contents_from_j2, get_template_path
from azext_aosm.vendored_sdks import HybridNetworkManagementClient
from azext_aosm.configuration_models.common_input import ArmTemplatePropertiesConfig
from azext_aosm.configuration_models.onboarding_nsd_input_config import NetworkFunctionPropertiesConfig
logger = get_logger(__name__)


class OnboardingNSDCLIHandler(OnboardingBaseCLIHandler):
    """CLI handler for publishing NFDs."""

    config: OnboardingNSDInputConfig
    processors: list[AzureCoreArmBuildProcessor | NFDProcessor]
    nfvi_types: list[Literal["AzureArcKubernetes"] | Literal["AzureOperatorNexus"] |
                     Literal["AzureCore"] | Literal["Unknown"]] = []

    @property
    def default_config_file_name(self) -> str:
        """Get the default configuration file name."""
        return NSD_INPUT_FILENAME

    @property
    def output_folder_file_name(self) -> str:
        """Get the output folder file name."""
        return NSD_OUTPUT_FOLDER_FILENAME

    @property
    def nfvi_site_name(self) -> str:
        """Return the name of the NFVI used for the NSDV."""
        assert isinstance(self.config, OnboardingNSDInputConfig)
        return f"{self.config.nsd_name}_NFVI"

    def _get_input_config(self, input_config: Optional[dict] = None) -> OnboardingNSDInputConfig:
        """Get the configuration for the command."""
        if input_config is None:
            input_config = {}
        return OnboardingNSDInputConfig(**input_config)

    def _get_params_config(self, config_file: Path) -> NSDCommonParametersConfig:
        """Get the configuration for the command."""
        with open(config_file, "r", encoding="utf-8") as _file:
            params_dict = json.load(_file)
        if params_dict is None:
            params_dict = {}
        return NSDCommonParametersConfig(**params_dict)

    def _get_processor_list(self) -> list:
        processor_list: list[AzureCoreArmBuildProcessor | NFDProcessor] = []
        # for each resource element template, instantiate processor
        for resource_element in self.config.resource_element_templates:
            if resource_element.resource_element_type == "ArmTemplate":
                assert isinstance(resource_element.properties, ArmTemplatePropertiesConfig)
                arm_input = ArmTemplateInput(
                    artifact_name=resource_element.properties.artifact_name,
                    artifact_version=resource_element.properties.version,
                    default_config=None,
                    template_path=Path(
                        resource_element.properties.file_path
                    ).absolute(),
                )
                # TODO: generalise for nexus in nexus ready stories
                # For NSDs, we don't have the option to expose ARM template parameters. This could be supported by
                # adding an 'expose_all_parameters' option to NSD input.jsonc file, as we have for NFD input files.
                # For now, we prefer this simpler interface for NSDs, but we might need to revisit in the future.
                processor_list.append(
                    AzureCoreArmBuildProcessor(arm_input.artifact_name, arm_input, expose_all_params=False)
                )
            elif resource_element.resource_element_type == "NF":
                assert isinstance(resource_element.properties, NetworkFunctionPropertiesConfig)
                # TODO: change artifact name and version to the nfd name and version or justify why it was this
                #       in the first place
                # AC4 note: I couldn't find a reference in the old code, but this
                # does ring a bell. Was it so the artifact manifest didn't get broken with changes to NF versions?
                # I.e., you could make an NF version change in CGV, and the artifact manifest, which is immutable,
                # would still be valid?
                # I am concerned that if we have multiple NFs we will have clashing artifact names.
                # I'm not changing the behaviour right now as it's too high risk, but we should look again here.
                nfdv_object = self._get_nfdv(resource_element.properties)

                # Add nfvi_type to list for creating nfvisFromSite later
                # There is a 1:1 mapping between NF RET and nfvisFromSite object,
                # as we shouldn't build NSDVs that deploy different RETs against the same custom location
                self.nfvi_types.append(nfdv_object.properties.network_function_template.nfvi_type)

                nfd_input = NFDInput(
                    # This would be the alternative if we swap from nsd name/version to nfd.
                    # artifact_name=resource_element.properties.name,
                    # artifact_version=resource_element.properties.version,
                    artifact_name=self.config.nsd_name,
                    artifact_version=self.config.nsd_version,
                    default_config={"location": self.config.location},
                    network_function_definition=nfdv_object,
                    arm_template_output_path=Path(
                        NSD_OUTPUT_FOLDER_FILENAME,
                        ARTIFACT_LIST_FILENAME,
                        resource_element.properties.name + ".bicep",
                    ),
                )
                nfd_processor = NFDProcessor(
                    name=self.config.nsd_name, input_artifact=nfd_input
                )
                processor_list.append(nfd_processor)
            else:
                # TODO: raise more specific error
                raise ValueError(
                    f"Invalid resource element type: {resource_element.resource_element_type}"
                )
        return processor_list

    def build_base_bicep(self) -> BicepDefinitionElementBuilder:
        """Build the base bicep file."""
        # Build base bicep contents, with bicep template
        template_path = get_template_path(
            NSD_TEMPLATE_FOLDER_NAME, NSD_BASE_TEMPLATE_FILENAME
        )
        bicep_contents = render_bicep_contents_from_j2(template_path, {})
        # Create Bicep element with manifest contents
        bicep_file = BicepDefinitionElementBuilder(
            Path(NSD_OUTPUT_FOLDER_FILENAME, BASE_FOLDER_NAME), bicep_contents
        )
        return bicep_file

    def build_manifest_bicep(self) -> BicepDefinitionElementBuilder:
        """Build the manifest bicep file."""
        artifact_list = []
        for processor in self.processors:
            artifact_list.extend(processor.get_artifact_manifest_list())
        logger.debug(
            "Created list of artifacts from resource element(s) provided: %s",
            artifact_list,
        )
        template_path = get_template_path(
            NSD_TEMPLATE_FOLDER_NAME, NSD_MANIFEST_TEMPLATE_FILENAME
        )
        params = {
            "acr_artifacts": artifact_list,
            "sa_artifacts": []
        }
        bicep_contents = render_bicep_contents_from_j2(template_path, params)

        bicep_file = BicepDefinitionElementBuilder(
            Path(NSD_OUTPUT_FOLDER_FILENAME, MANIFEST_FOLDER_NAME), bicep_contents
        )
        return bicep_file

    def build_artifact_list(self) -> ArtifactDefinitionElementBuilder:
        """Build the artifact list."""
        # Build artifact list for ArmTemplates
        artifact_list = []
        nf_files = []
        for processor in self.processors:
            (artifacts, files) = processor.get_artifact_details()
            if artifacts not in artifact_list:
                artifact_list.extend(artifacts)
            # If NF, file is local file builder, if ARM, file is empty
            nf_files.extend(files)

        artifact_file = ArtifactDefinitionElementBuilder(
            Path(NSD_OUTPUT_FOLDER_FILENAME, ARTIFACT_LIST_FILENAME), artifact_list
        )
        for nf_arm_template in nf_files:
            artifact_file.add_supporting_file(nf_arm_template)

        return artifact_file

    def build_resource_bicep(self) -> BicepDefinitionElementBuilder:
        """Build the resource bicep file."""
        schema_properties = {}
        nf_names = []
        ret_list = []
        supporting_files = []

        # For each RET (arm template or NF), generate RET
        for processor in self.processors:
            nf_ret = processor.generate_resource_element_template()
            ret_list.append(nf_ret)

            # Add supporting file: config mappings
            deploy_values = nf_ret.configuration.parameter_values
            mapping_file = LocalFileBuilder(
                Path(
                    NSD_OUTPUT_FOLDER_FILENAME,
                    NSD_DEFINITION_FOLDER_NAME,
                    processor.name + "-mappings.json",
                ),
                json.dumps(json.loads(deploy_values), indent=4),
            )
            supporting_files.append(mapping_file)

            # Generate deployParameters schema properties
            params_schema = processor.generate_schema()
            schema_properties.update(params_schema)

            # List of NF RET names, for adding to required part of CGS
            nf_names.append(processor.name)

        # If all NF RETs nfvi_types are AzureCore, only make one nfviFromSite object
        # This is a design decision, for simplification of nfvisFromSite and also
        # so that users are discouraged from deploying NFs across multiple locations
        # within a single SNS
        if all(nfvi_type == "AzureCore" for nfvi_type in self.nfvi_types):
            self.nfvi_types = ["AzureCore"]

        template_path = get_template_path(
            NSD_TEMPLATE_FOLDER_NAME, NSD_DEFINITION_TEMPLATE_FILENAME
        )

        params = {
            "nsdv_description": self.config.nsdv_description,
            "nfvi_types": self.nfvi_types,
            "cgs_name": CGS_NAME,
            "nfvi_site_name": self.nfvi_site_name,
            "nf_rets": ret_list,
            "cgs_file": CGS_FILENAME,
            "deploy_parameters_file": DEPLOY_PARAMETERS_FILENAME,
            "template_parameters_file": TEMPLATE_PARAMETERS_FILENAME,
        }

        bicep_contents = render_bicep_contents_from_j2(
            template_path, params
        )
        # Generate the nsd bicep file
        bicep_file = BicepDefinitionElementBuilder(
            Path(NSD_OUTPUT_FOLDER_FILENAME, NSD_DEFINITION_FOLDER_NAME), bicep_contents
        )

        # Add the config mappings for each nf
        for mappings_file in supporting_files:
            bicep_file.add_supporting_file(mappings_file)

        # Add the accompanying cgs
        bicep_file.add_supporting_file(
            self._render_config_group_schema_contents(schema_properties, nf_names)
        )

        return bicep_file

    def build_all_parameters_json(self) -> JSONDefinitionElementBuilder:
        """Build all parameters json."""
        params_content = {
            "location": self.config.location,
            "publisherName": self.config.publisher_name,
            "publisherResourceGroupName": self.config.publisher_resource_group_name,
            "acrArtifactStoreName": self.config.acr_artifact_store_name,
            "acrManifestName": self.config.acr_manifest_name,
            "nsDesignGroup": self.config.nsd_name,
            "nsDesignVersion": self.config.nsd_version,
            "nfviSiteName": self.nfvi_site_name,
        }
        base_file = JSONDefinitionElementBuilder(
            Path(NSD_OUTPUT_FOLDER_FILENAME), json.dumps(params_content, indent=4)
        )
        return base_file

    @staticmethod
    def _render_config_group_schema_contents(complete_schema, nf_names):
        params_content = {
            "$schema": "https://json-schema.org/draft-07/schema#",
            "title": CGS_NAME,
            "type": "object",
            "properties": complete_schema,
            "required": nf_names,
        }
        return LocalFileBuilder(
            Path(
                NSD_OUTPUT_FOLDER_FILENAME,
                NSD_DEFINITION_FOLDER_NAME,
                CGS_FILENAME,
            ),
            json.dumps(params_content, indent=4),
        )

    def _get_nfdv(self, nf_properties) -> NetworkFunctionDefinitionVersion:
        """Get the existing NFDV resource object."""
        print(
            f"Reading existing NFDV resource object {nf_properties.version} from group {nf_properties.name}"
        )
        assert isinstance(self.aosm_client, HybridNetworkManagementClient)
        nfdv_object = self.aosm_client.network_function_definition_versions.get(
            resource_group_name=nf_properties.publisher_resource_group,
            publisher_name=nf_properties.publisher,
            network_function_definition_group_name=nf_properties.name,
            network_function_definition_version_name=nf_properties.version,
        )
        return nfdv_object
