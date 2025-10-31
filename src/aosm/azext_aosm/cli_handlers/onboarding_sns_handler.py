# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional
from knack.log import get_logger
from azext_aosm.cli_handlers.onboarding_nfd_base_handler import OnboardingBaseCLIHandler
from azext_aosm.common.command_context import CommandContext
from azext_aosm.common.constants import (
    SNS_OUTPUT_FOLDER_FILENAME,
    SNS_INPUT_FILENAME,
    SNS_DEFINITION_FOLDER_NAME,
    SNS_TEMPLATE_FOLDER_NAME,
    SNS_DEFINITION_TEMPLATE_FILENAME,
)
from azext_aosm.common.utils import render_bicep_contents_from_j2, get_template_path, generate_data_for_given_schema
from azext_aosm.configuration_models.onboarding_sns_input_config import (
    OnboardingSNSInputConfig,
)
from azext_aosm.configuration_models.sns_parameters_config import SNSCommonParametersConfig
from azext_aosm.definition_folder.builder.bicep_builder import BicepDefinitionElementBuilder
from azext_aosm.definition_folder.builder.sns_deploy_input_builder import SNSDeploymentInputDefinitionElementBuilder
from azext_aosm.definition_folder.builder.json_builder import (
    JSONDefinitionElementBuilder,
)
from azext_aosm.definition_folder.builder.local_file_builder import LocalFileBuilder
from azext_aosm.definition_folder.reader.definition_folder import DefinitionFolder
from azext_aosm.vendored_sdks import HybridNetworkManagementClient
from azext_aosm.vendored_sdks.models import (
    NetworkServiceDesignVersion
)


class OnboardingSNSCLIHandler(OnboardingBaseCLIHandler):
    """CLI handler for deploying SNSs."""

    config: OnboardingSNSInputConfig | SNSCommonParametersConfig
    logger = get_logger(__name__)
    schema_to_cgv_map = []
    nsdv = None

    @property
    def default_config_file_name(self) -> str:
        """Get the default configuration file name."""
        return SNS_INPUT_FILENAME

    @property
    def output_folder_file_name(self) -> str:
        """Get the output folder file name."""
        return SNS_OUTPUT_FOLDER_FILENAME

    def build(self):
        """Build the definition."""
        self.definition_folder_builder.add_element(self.build_all_parameters_json())
        self.definition_folder_builder.add_element(self.build_deploy_input())
        self.definition_folder_builder.add_element(self.build_resource_bicep())
        for cgv_entry in self.schema_to_cgv_map:
            self.definition_folder_builder.add_element(
                self.build_cgv_data_for_schema(
                    cgv_entry["cgs_schema_definition"],
                    cgv_entry["cgv_definition_builder_path"]
                ))
        self.definition_folder_builder.write()

    def _get_processor_list(self) -> list:
        return []

    def _get_input_config(self, input_config: Optional[dict] = None) -> OnboardingSNSInputConfig:
        """Get the configuration for the command."""
        if input_config is None:
            input_config = {}
        return OnboardingSNSInputConfig(**input_config)

    def _get_params_config(self, config_file: Path) -> SNSCommonParametersConfig:
        """Get the configuration for the command."""
        with open(config_file, "r", encoding="utf-8") as _file:
            params_dict = json.load(_file)
        if params_dict is None:
            params_dict = {}
        return SNSCommonParametersConfig(**params_dict)

    def build_deploy_input(self) -> SNSDeploymentInputDefinitionElementBuilder:
        """Generate deploy input file which is created post build and used for deploy."""
        self.nsdv = self._get_nsdv()
        self._generate_cgv_filenames()
        deployment_input_file = SNSDeploymentInputDefinitionElementBuilder(
            Path(SNS_OUTPUT_FOLDER_FILENAME), self.nsdv.properties.nfvis_from_site, self.schema_to_cgv_map
        )
        return deployment_input_file

    def _generate_cgv_filenames(self):
        for schema_reference in self.nsdv.properties.configuration_group_schema_references:
            file_name = os.path.join(SNS_OUTPUT_FOLDER_FILENAME, f"{schema_reference}-CGV.json")
            schema_object = self._get_cgSchema(schema_reference)
            cgv_entry = {
                "cgs_name": schema_reference,
                "cgs_id": schema_object.id,
                "cgv_name": "cgv_" + schema_reference,
                "cgv_configuration_type": "Open",
                "cgv_file_path": "../../" + f"{file_name}",
                "cgv_definition_builder_path": file_name,
                "cgs_schema_definition": schema_object.properties.schema_definition
            }
            self.schema_to_cgv_map.append(cgv_entry)

    def _get_cgSchema(self, cg_name):
        """Get the existing CGSchema resource object."""

        assert isinstance(self.aosm_client, HybridNetworkManagementClient)

        cg_schema_object = self.aosm_client.configuration_group_schemas.get(
            resource_group_name=self.config.nsd_reference.publisher_resource_group_name,
            publisher_name=self.config.nsd_reference.publisher_name,
            configuration_group_schema_name=cg_name
        )
        return cg_schema_object

    def _get_nsdv(self) -> NetworkServiceDesignVersion:
        """Get the existing NSDV resource object."""
        self.logger.debug(
            "Reading existing NSDV resource object %s from group %s",
            self.config.nsd_reference.nsd_version,
            self.config.nsd_reference.nsd_name
        )
        assert isinstance(self.aosm_client, HybridNetworkManagementClient)
        nsdv_object = self.aosm_client.network_service_design_versions.get(
            resource_group_name=self.config.nsd_reference.publisher_resource_group_name,
            publisher_name=self.config.nsd_reference.publisher_name,
            network_service_design_group_name=self.config.nsd_reference.nsd_name,
            network_service_design_version_name=self.config.nsd_reference.nsd_version,
        )
        return nsdv_object

    def build_resource_bicep(self) -> BicepDefinitionElementBuilder:
        """Build the resource bicep file."""
        template_path = get_template_path(
            SNS_TEMPLATE_FOLDER_NAME, SNS_DEFINITION_TEMPLATE_FILENAME
        )
        params = {
            "cgvs": self.schema_to_cgv_map,
            "nsdvId": self.nsdv.id
        }

        bicep_contents = render_bicep_contents_from_j2(
            template_path, params
        )
        # Generate the sns bicep file
        bicep_file = BicepDefinitionElementBuilder(
            Path(SNS_OUTPUT_FOLDER_FILENAME, SNS_DEFINITION_FOLDER_NAME), bicep_contents
        )
        return bicep_file

    def deploy(self, command_context: CommandContext):
        """Publish the definition contained in the specified definition folder."""
        definition_folder = DefinitionFolder(
            command_context.cli_options["definition_folder"]
        )
        assert isinstance(self.config, SNSCommonParametersConfig)
        definition_folder.deploy(config=self.config, command_context=command_context)

    def build_all_parameters_json(self) -> JSONDefinitionElementBuilder:
        """Build all parameters json."""
        params_content = {
            "location": self.config.location,
            "operatorResourceGroupName": self.config.operator_resource_group_name,
            "siteName": self.config.site_name,
            "snsName": self.config.sns_name,
            "userIdentity": self.config.user_identity_resourceid
        }
        base_file = JSONDefinitionElementBuilder(
            Path(SNS_OUTPUT_FOLDER_FILENAME), json.dumps(params_content, indent=4)
        )
        return base_file

    def build_cgv_data_for_schema(self, schema_definition, path_to_write) -> LocalFileBuilder:
        """Build CGV Data JSON."""
        value_json = generate_data_for_given_schema(schema_definition)
        cgv_data_file = LocalFileBuilder(
            Path(path_to_write), json.dumps(value_json, indent=4)
        )
        return cgv_data_file

    def build_base_bicep(self):
        raise NotImplementedError

    def build_artifact_list(self):
        raise NotImplementedError

    def build_manifest_bicep(self) -> BicepDefinitionElementBuilder:
        raise NotImplementedError
