# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from pathlib import Path
from typing import List, Tuple

from knack.log import get_logger

from azext_aosm.build_processors.base_processor import BaseInputProcessor
from azext_aosm.common.artifact import BaseArtifact, RemoteACRArtifact
from azext_aosm.definition_folder.builder.local_file_builder import LocalFileBuilder
from azext_aosm.inputs.nexus_image_input import NexusImageFileInput
from azext_aosm.vendored_sdks.models import (
    AzureOperatorNexusNetworkFunctionImageApplication,
    AzureOperatorNexusImageArtifactProfile,
    AzureOperatorNexusImageDeployMappingRuleProfile,
    ImageArtifactProfile,
    ImageMappingRuleProfile,
    ApplicationEnablement,
    ArtifactType,
    DependsOnProfile,
    ManifestArtifactFormat,
    ReferencedResource,
    ResourceElementTemplate,
)
from azext_aosm.common.registry import AzureContainerRegistry
from azext_aosm.common.constants import (
    VNF_OUTPUT_FOLDER_FILENAME,
    NF_DEFINITION_FOLDER_NAME,
    NEXUS_IMAGE_PARAMETERS_FILENAME,
)

logger = get_logger(__name__)


class NexusImageProcessor(BaseInputProcessor):
    """
    A class for processing Nexus image inputs.

    :param name: The name of the artifact.
    :param input_artifact: The input artifact.
    """
    input_artifact: NexusImageFileInput

    def __init__(self, name: str, input_artifact: NexusImageFileInput, expose_all_params: bool):
        super().__init__(name, input_artifact, expose_all_params)

    def get_artifact_manifest_list(self) -> List[ManifestArtifactFormat]:
        """
        Get the list of artifacts for the artifact manifest.

        :return: A list of artifacts for the artifact manifest.
        :rtype: List[ManifestArtifactFormat]
        """
        logger.info("Getting artifact manifest list for Nexus image input.")
        return [
            ManifestArtifactFormat(
                artifact_name=self.input_artifact.artifact_name,
                artifact_type=ArtifactType.IMAGE_FILE.value,
                artifact_version=self.input_artifact.artifact_version,
            )
        ]

    def get_artifact_details(
        self,
    ) -> Tuple[List[BaseArtifact], List[LocalFileBuilder]]:
        """
        Get the artifact details for publishing.

        :return: A tuple containing the list of artifacts and the list of local file builders.
        :rtype: Tuple[List[BaseArtifact], List[LocalFileBuilder]]
        """
        logger.info("Getting artifact details for Nexus image input.")
        artifacts: List[BaseArtifact] = []
        file_builders: List[LocalFileBuilder] = []

        # We only support remote ACR artifacts for nexus container images
        source_registry = AzureContainerRegistry(
            self.input_artifact.source_acr_registry
        )

        artifacts.append(
            RemoteACRArtifact(
                artifact_name=self.input_artifact.artifact_name,
                artifact_type=ArtifactType.IMAGE_FILE.value,
                artifact_version=self.input_artifact.artifact_version,
                source_registry=source_registry,
                registry_namespace="",
            )
        )
        return artifacts, file_builders

    def generate_nf_application(
        self,
    ) -> AzureOperatorNexusNetworkFunctionImageApplication:
        """
        Generate the NF application.

        :return: The NF application.
        :rtype: AzureOperatorNexusNetworkFunctionImageApplication
        """
        logger.info("Generating NF application for Nexus image input.")

        return AzureOperatorNexusNetworkFunctionImageApplication(
            name=self.name,
            depends_on_profile=DependsOnProfile(
                install_depends_on=[], uninstall_depends_on=[], update_depends_on=[]
            ),
            artifact_profile=self._generate_artifact_profile(),
            deploy_parameters_mapping_rule_profile=self._generate_mapping_rule_profile(),
        )

    def generate_resource_element_template(self) -> ResourceElementTemplate:
        """
        Generate the resource element template.

        :raises NotImplementedError: NSDs do not support deployment of Nexus images.
        """
        raise NotImplementedError(
            "NSDs do not support deployment of Nexus images directly, "
            "they must be provided in the NF."
        )

    def _generate_artifact_profile(self) -> AzureOperatorNexusImageArtifactProfile:
        """
        Generate the artifact profile.

        :return: The artifact profile.
        :rtype: AzureOperatorNexusImageArtifactProfile
        """
        logger.debug("Generating artifact profile for Nexus image input.")
        artifact_profile = ImageArtifactProfile(
            image_name=self.input_artifact.artifact_name,
            image_version=self.input_artifact.artifact_version,
        )

        return AzureOperatorNexusImageArtifactProfile(
            artifact_store=ReferencedResource(id=""),
            image_artifact_profile=artifact_profile,
        )

    def _generate_mapping_rule_profile(
        self,
    ) -> AzureOperatorNexusImageDeployMappingRuleProfile:
        """
        Generate the mapping rule profile.

        :return: The mapping rule profile.
        :rtype: AzureOperatorNexusImageDeployMappingRuleProfile
        """
        logger.debug("Generating mapping rule profile for Nexus image input.")
        user_configuration = self.generate_values_mappings(
            self.input_artifact.get_schema(), self.input_artifact.get_defaults()
        )

        mapping = ImageMappingRuleProfile(
            user_configuration=json.dumps(user_configuration),
        )

        return AzureOperatorNexusImageDeployMappingRuleProfile(
            application_enablement=ApplicationEnablement.ENABLED,
            image_mapping_rule_profile=mapping,
        )

    def generate_parameters_file(self) -> LocalFileBuilder:
        """Generate parameters file."""
        mapping_rule_profile = self._generate_mapping_rule_profile()
        if (
            mapping_rule_profile.image_mapping_rule_profile
            and mapping_rule_profile.image_mapping_rule_profile.user_configuration
        ):
            params = mapping_rule_profile.image_mapping_rule_profile.user_configuration
            logger.info("Created parameters file for Nexus image.")
        # We still want to create an empty params file,
        # otherwise the nf definition bicep will refer to files that don't exist
        else:
            params = "{}"
        return LocalFileBuilder(
            Path(
                VNF_OUTPUT_FOLDER_FILENAME,
                NF_DEFINITION_FOLDER_NAME,
                self.input_artifact.artifact_name
                + "-"
                + NEXUS_IMAGE_PARAMETERS_FILENAME,
            ),
            json.dumps(json.loads(params), indent=4),
        )
