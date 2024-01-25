# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from typing import List, Tuple

from knack.log import get_logger

from azext_aosm.build_processors.base_processor import BaseInputProcessor
from azext_aosm.common.artifact import (BaseArtifact,
                                        BlobStorageAccountArtifact,
                                        LocalFileStorageAccountArtifact)
from azext_aosm.common.local_file_builder import LocalFileBuilder
from azext_aosm.inputs.nexus_image_input import NexusImageFileInput
from azext_aosm.vendored_sdks.models import (
    AzureOperatorNexusNetworkFunctionImageApplication,
    AzureOperatorNexusImageArtifactProfile,
    AzureOperatorNexusImageDeployMappingRuleProfile,
    ImageArtifactProfile, ImageMappingRuleProfile,
    ApplicationEnablement, ArtifactType,
    DependsOnProfile,
    ManifestArtifactFormat, ReferencedResource, ResourceElementTemplate,
    )

logger = get_logger(__name__)


class NexusImageProcessor(BaseInputProcessor):
    """
    A class for processing VHD inputs.

    :param name: The name of the artifact.
    :type name: str
    :param input_artifact: The input artifact.
    :type input_artifact: VHDFileInput
    """

    def __init__(self, name: str, input_artifact: NexusImageFileInput):
        super().__init__(name, input_artifact)
        self.input_artifact: NexusImageFileInput = input_artifact

    def get_artifact_manifest_list(self) -> List[ManifestArtifactFormat]:
        """
        Get the list of artifacts for the artifact manifest.

        :return: A list of artifacts for the artifact manifest.
        :rtype: List[ManifestArtifactFormat]
        """
        logger.info("Getting artifact manifest list for VHD input.")
        return [
            ManifestArtifactFormat(
                artifact_name=self.input_artifact.artifact_name,
                artifact_type=ArtifactType.IMAGE_FILE.value,
                artifact_version=self.input_artifact.artifact_version,
            )
        ]

    # TODO: figure out what artifact type this can be
    def get_artifact_details(
        self,
    ) -> Tuple[List[BaseArtifact], List[LocalFileBuilder]]:
        """
        Get the artifact details for publishing.

        :return: A tuple containing the list of artifacts and the list of local file builders.
        :rtype: Tuple[List[BaseArtifact], List[LocalFileBuilder]]
        """
        logger.info("Getting artifact details for VHD input.")
        artifacts: List[BaseArtifact] = []
        file_builders: List[LocalFileBuilder] = []

        if self.input_artifact.file_path:
            logger.debug(
                "VHD input has a file path. Adding LocalFileStorageAccountArtifact."
            )
            artifacts.append(
                LocalFileStorageAccountArtifact(
                    artifact_name=self.input_artifact.artifact_name,
                    artifact_type=ArtifactType.IMAGE_FILE.value,
                    artifact_version=self.input_artifact.artifact_version,
                    file_path=self.input_artifact.file_path,
                )
            )
        # elif self.input_artifact.blob_sas_uri:
        #     logger.debug(
        #         "VHD input has a blob SAS URI. Adding BlobStorageAccountArtifact."
        #     )
        #     artifacts.append(
        #         BlobStorageAccountArtifact(
        #             artifact_manifest=artifact_manifest,
        #             blob_sas_uri=self.input_artifact.blob_sas_uri,
        #         )
        #     )
        else:
            # TODO: change error once file input defined
            logger.error("ImageFileInput must have either a file path or a blob SAS URI.")
            raise ValueError(
                "VHDFileInput must have either a file path or a blob SAS URI."
            )

        return artifacts, file_builders

    def generate_nf_application(self) -> AzureOperatorNexusNetworkFunctionImageApplication:
        """
        Generate the NF application.

        :return: The NF application.
        :rtype: AzureCoreNetworkFunctionVhdApplication
        """
        logger.info("Generating NF application for VHD input.")

        return AzureOperatorNexusNetworkFunctionImageApplication(
            name=self.name,
            depends_on_profile=DependsOnProfile(install_depends_on=[],
                                                uninstall_depends_on=[], update_depends_on=[]),
            artifact_profile=self._generate_artifact_profile(),
            deploy_parameters_mapping_rule_profile=self._generate_mapping_rule_profile(),
        )

    def generate_resource_element_template(self) -> ResourceElementTemplate:
        """
        Generate the resource element template.

        :raises NotImplementedError: NSDs do not support deployment of VHDs.
        """
        raise NotImplementedError("NSDs do not support deployment of VHDs.")

    def _generate_artifact_profile(self) -> AzureOperatorNexusImageArtifactProfile:
        """
        Generate the artifact profile.

        :return: The artifact profile.
        :rtype: AzureOperatorNexusImageArtifactProfile
        """
        logger.debug("Generating artifact profile for VHD input.")
        # TODO: JORDAN check what inputs this takes
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
        logger.debug("Generating mapping rule profile for VHD input.")
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
