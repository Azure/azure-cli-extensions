# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Optional

import ruamel.yaml
from azure.cli.core.azclierror import ValidationError
from jinja2 import Template
from knack.log import get_logger
from ruamel.yaml.error import ReusedAnchorWarning

from azext_aosm.build_processors.helm_chart_processor import HelmChartProcessor
from azext_aosm.common.constants import (
    ARTIFACT_LIST_FILENAME,
    BASE_FOLDER_NAME,
    CNF_BASE_TEMPLATE_FILENAME,
    CNF_DEFINITION_TEMPLATE_FILENAME,
    CNF_HELM_VALIDATION_ERRORS_TEMPLATE_FILENAME,
    CNF_INPUT_FILENAME,
    CNF_MANIFEST_TEMPLATE_FILENAME,
    CNF_OUTPUT_FOLDER_FILENAME,
    CNF_TEMPLATE_FOLDER_NAME,
    DEPLOY_PARAMETERS_FILENAME,
    HELM_TEMPLATE,
    MANIFEST_FOLDER_NAME,
    NF_DEFINITION_FOLDER_NAME,
)
from azext_aosm.common.exceptions import TemplateValidationError
from azext_aosm.configuration_models.common_parameters_config import (
    CNFCommonParametersConfig,
)
from azext_aosm.configuration_models.onboarding_cnf_input_config import (
    OnboardingCNFInputConfig,
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
from azext_aosm.inputs.helm_chart_input import HelmChartInput

from .onboarding_nfd_base_handler import OnboardingNFDBaseCLIHandler
from azext_aosm.common.registry import ContainerRegistryHandler
from azext_aosm.common.utils import render_bicep_contents_from_j2, get_template_path

logger = get_logger(__name__)
yaml_processor = ruamel.yaml.YAML(typ="safe", pure=True)
warnings.simplefilter("ignore", ReusedAnchorWarning)


class OnboardingCNFCLIHandler(OnboardingNFDBaseCLIHandler):
    """CLI handler for publishing NFDs."""

    config: OnboardingCNFInputConfig
    processors: list[HelmChartProcessor]

    @property
    def default_config_file_name(self) -> str:
        """Get the default configuration file name."""
        return CNF_INPUT_FILENAME

    @property
    def output_folder_file_name(self) -> str:
        """Get the output folder file name."""
        return CNF_OUTPUT_FOLDER_FILENAME

    def _get_input_config(
        self, input_config: Optional[dict] = None
    ) -> OnboardingCNFInputConfig:
        """Get the configuration for the command."""
        if input_config is None:
            input_config = {}
        return OnboardingCNFInputConfig(**input_config)

    def _get_params_config(self, config_file: Path) -> CNFCommonParametersConfig:
        """Get the configuration for the command."""
        with open(config_file, "r", encoding="utf-8") as _file:
            params_dict = json.load(_file)
        if params_dict is None:
            params_dict = {}
        return CNFCommonParametersConfig(**params_dict)

    def _get_processor_list(self) -> list[HelmChartProcessor]:
        processor_list = []
        assert isinstance(self.config, OnboardingCNFInputConfig)

        registry_handler = ContainerRegistryHandler(self.config.image_sources)

        # for each helm package, instantiate helm processor
        for helm_package in self.config.helm_packages:

            if helm_package.default_values:
                default_config_path = helm_package.default_values
            else:
                default_config_path = None

            helm_input = HelmChartInput.from_chart_path(
                chart_path=Path(helm_package.path_to_chart).absolute(),
                default_config={},
                default_config_path=default_config_path,
            )
            helm_processor = HelmChartProcessor(
                name=helm_package.name,
                input_artifact=helm_input,
                registry_handler=registry_handler,
                expose_all_params=self.config.expose_all_parameters,
            )
            processor_list.append(helm_processor)
        return processor_list

    def _validate_helm_template(self):
        """Validate the helm packages."""
        validation_errors = {}

        for helm_processor in self.processors:
            try:
                helm_processor.input_artifact.validate_template()
            except TemplateValidationError as error:
                validation_errors[helm_processor.input_artifact.artifact_name] = str(
                    error
                )

        if validation_errors:
            # Create an error file using a j2 template
            error_output_template_path = get_template_path(
                CNF_TEMPLATE_FOLDER_NAME, CNF_HELM_VALIDATION_ERRORS_TEMPLATE_FILENAME
            )

            with open(
                error_output_template_path,
                "r",
                encoding="utf-8",
            ) as file:
                error_output_template = Template(file.read())

            rendered_error_output_template = error_output_template.render(
                errors=validation_errors
            )

            logger.info(rendered_error_output_template)

            error_message = (
                "Could not validate all the provided Helm charts. "
                "Use the --verbose flag to see the validation errors."
            )

            raise ValidationError(error_message)

    def pre_validate_build(self):
        """Run all validation functions required before building the cnf."""
        logger.debug("Pre-validating build")

        if self.skip != HELM_TEMPLATE:
            self._validate_helm_template()

    def build_base_bicep(self) -> BicepDefinitionElementBuilder:
        """Build the base bicep file."""
        # Build manifest bicep contents, with j2 template
        template_path = get_template_path(
            CNF_TEMPLATE_FOLDER_NAME, CNF_BASE_TEMPLATE_FILENAME
        )
        params = {"disablePublicNetworkAccess": self.config.disable_public_network_access}
        bicep_contents = render_bicep_contents_from_j2(template_path, params)
        # Create Bicep element with base contents
        bicep_file = BicepDefinitionElementBuilder(
            Path(CNF_OUTPUT_FOLDER_FILENAME, BASE_FOLDER_NAME), bicep_contents
        )
        return bicep_file

    def build_manifest_bicep(self) -> BicepDefinitionElementBuilder:
        """Build the manifest bicep file."""
        artifact_list = []
        logger.info("Creating artifact manifest bicep")
        for processor in self.processors:
            artifacts = processor.get_artifact_manifest_list()

            # Add artifacts to a list of unique artifacts
            if artifacts not in artifact_list:
                artifact_list.extend(artifacts)
        logger.debug(
            "Created list of artifacts from %s helm package(s) provided: %s",
            len(self.config.helm_packages),
            artifact_list,
        )
        # Build manifest bicep contents, with j2 template
        template_path = get_template_path(
            CNF_TEMPLATE_FOLDER_NAME, CNF_MANIFEST_TEMPLATE_FILENAME
        )

        params = {"acr_artifacts": artifact_list, "sa_artifacts": []}
        bicep_contents = render_bicep_contents_from_j2(template_path, params)

        # Create Bicep element with manifest contents
        bicep_file = BicepDefinitionElementBuilder(
            Path(CNF_OUTPUT_FOLDER_FILENAME, MANIFEST_FOLDER_NAME), bicep_contents
        )

        return bicep_file

    def build_artifact_list(self) -> ArtifactDefinitionElementBuilder:
        """Build the artifact list."""
        logger.info("Creating artifacts list for artifacts.json")
        artifact_list = []
        # For each helm package, get list of artifacts and combine
        # For each arm template, get list of artifacts and combine
        for processor in self.processors:
            (artifacts, _) = processor.get_artifact_details()
            if artifacts not in artifact_list:
                artifact_list.extend(artifacts)
        logger.debug(
            "Created list of artifact details from %s helm packages(s) and the vhd image provided: %s",
            len(self.config.helm_packages),
            artifact_list,
        )
        # Generate Artifact Element with artifact list
        return ArtifactDefinitionElementBuilder(
            Path(CNF_OUTPUT_FOLDER_FILENAME, ARTIFACT_LIST_FILENAME), artifact_list
        )

    def build_resource_bicep(self) -> BicepDefinitionElementBuilder:
        """Build the resource bicep file."""
        logger.info("Creating NF definition bicep template")
        nf_application_list = []
        mappings_files = []
        deploy_params_schema = {}
        # For each helm package, generate nf application, params schema and mappings profile
        for processor in self.processors:
            nf_application = processor.generate_nf_application()
            nf_application_list.append(nf_application)

            # The AOSM API models are very permissive with None values. Our code should never set these to None,
            # so we use these asserts to ensure that, and to keep type checking happy.
            assert nf_application.name is not None
            assert nf_application.deploy_parameters_mapping_rule_profile is not None
            assert nf_application.deploy_parameters_mapping_rule_profile.helm_mapping_rule_profile is not None
            assert nf_application.deploy_parameters_mapping_rule_profile.helm_mapping_rule_profile.values is not None

            deploy_params_schema.update(processor.generate_schema())

            # Add supporting file: config mappings
            mapping_rules = (
                nf_application.deploy_parameters_mapping_rule_profile.helm_mapping_rule_profile.values
            )
            mapping_file = LocalFileBuilder(
                Path(
                    CNF_OUTPUT_FOLDER_FILENAME,
                    NF_DEFINITION_FOLDER_NAME,
                    nf_application.name + "-mappings.json",
                ),
                json.dumps(json.loads(mapping_rules), indent=4),
            )
            mappings_files.append(mapping_file)

        # Create bicep contents using cnf defintion j2 template
        template_path = get_template_path(
            CNF_TEMPLATE_FOLDER_NAME, CNF_DEFINITION_TEMPLATE_FILENAME
        )
        params = {
            "acr_nf_applications": nf_application_list,
            "deploy_parameters_file": DEPLOY_PARAMETERS_FILENAME,
        }
        bicep_contents = render_bicep_contents_from_j2(template_path, params)

        # Create a bicep element + add its supporting mapping files
        bicep_element_builder = BicepDefinitionElementBuilder(
            Path(CNF_OUTPUT_FOLDER_FILENAME, NF_DEFINITION_FOLDER_NAME), bicep_contents
        )
        for mappings_file in mappings_files:
            bicep_element_builder.add_supporting_file(mappings_file)

        # Add the deployParameters schema file
        bicep_element_builder.add_supporting_file(
            self._render_deploy_params_schema(
                deploy_params_schema, CNF_OUTPUT_FOLDER_FILENAME, NF_DEFINITION_FOLDER_NAME
            )
        )
        return bicep_element_builder

    def build_all_parameters_json(self) -> JSONDefinitionElementBuilder:
        """Build the all parameters json file."""
        params_content = {
            "location": self.config.location,
            "publisherName": self.config.publisher_name,
            "publisherResourceGroupName": self.config.publisher_resource_group_name,
            "acrArtifactStoreName": self.config.acr_artifact_store_name,
            "acrManifestName": self.config.acr_manifest_name,
            "nfDefinitionGroup": self.config.nf_name,
            "nfDefinitionVersion": self.config.version,
            "disablePublicNetworkAccess": self.config.disable_public_network_access,
            "vnetPrivateEndPoints": self.config.vnet_private_end_points,
            "networkFabricControllerIds": self.config.network_fabric_controller_ids
        }

        base_file = JSONDefinitionElementBuilder(
            Path(CNF_OUTPUT_FOLDER_FILENAME), json.dumps(params_content, indent=4)
        )
        return base_file
