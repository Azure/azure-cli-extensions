# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from pathlib import Path
import json
from typing import List, Tuple

from knack.log import get_logger

from azext_aosm.build_processors.base_processor import BaseInputProcessor
from azext_aosm.common.artifact import (
    BaseArtifact,
    BlobStorageAccountArtifact,
    LocalFileStorageAccountArtifact
)
from azext_aosm.definition_folder.builder.local_file_builder import LocalFileBuilder
from azext_aosm.inputs.vhd_file_input import VHDFileInput
from azext_aosm.vendored_sdks.models import (
    ApplicationEnablement,
    ArtifactType,
    AzureCoreNetworkFunctionVhdApplication,
    AzureCoreVhdImageArtifactProfile,
    AzureCoreVhdImageDeployMappingRuleProfile,
    DependsOnProfile,
    ManifestArtifactFormat,
    ReferencedResource,
    ResourceElementTemplate,
    VhdImageArtifactProfile,
    VhdImageMappingRuleProfile,
)
from azext_aosm.common.constants import (
    VNF_OUTPUT_FOLDER_FILENAME,
    NF_DEFINITION_FOLDER_NAME,
    VHD_PARAMETERS_FILENAME)

logger = get_logger(__name__)


class VHDProcessor(BaseInputProcessor):
    """
    A class for processing VHD inputs.

    :param name: The name of the artifact.
    :param input_artifact: The input artifact.
    """
    input_artifact: VHDFileInput

    def __init__(self, name: str, input_artifact: VHDFileInput, expose_all_params: bool):
        super().__init__(name, input_artifact, expose_all_params)

    def get_artifact_manifest_list(self) -> List[ManifestArtifactFormat]:
        """
        Get the list of artifacts for the artifact manifest.

        :return: A list of artifacts for the artifact manifest.
        :rtype: List[ManifestArtifactFormat]
        """
        logger.debug("Getting artifact manifest list for VHD input %s.", self.name)
        return [
            ManifestArtifactFormat(
                artifact_name=self.input_artifact.artifact_name,
                artifact_type=ArtifactType.VHD_IMAGE_FILE.value,
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
                    artifact_type=ArtifactType.VHD_IMAGE_FILE.value,
                    artifact_version=self.input_artifact.artifact_version,
                    file_path=self.input_artifact.file_path,
                )
            )
        elif self.input_artifact.blob_sas_uri:
            logger.debug(
                "VHD input has a blob SAS URI. Adding BlobStorageAccountArtifact."
            )
            artifacts.append(
                BlobStorageAccountArtifact(
                    artifact_name=self.input_artifact.artifact_name,
                    artifact_type=ArtifactType.VHD_IMAGE_FILE.value,
                    artifact_version=self.input_artifact.artifact_version,
                    blob_sas_uri=self.input_artifact.blob_sas_uri,
                )
            )
        else:
            logger.error("VHDFileInput must have either a file path or a blob SAS URI.")
            raise ValueError(
                "VHDFileInput must have either a file path or a blob SAS URI."
            )

        return artifacts, file_builders

    def generate_nf_application(self) -> AzureCoreNetworkFunctionVhdApplication:
        """
        Generate the NF application.

        :return: The NF application.
        :rtype: AzureCoreNetworkFunctionVhdApplication
        """
        logger.info("Generating NF application for VHD input.")

        return AzureCoreNetworkFunctionVhdApplication(
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

        :raises NotImplementedError: NSDs do not support deployment of VHDs.
        """
        raise NotImplementedError("NSDs do not support deployment of VHDs directly, "
                                  "they must be provided in the NF.")

    def _generate_artifact_profile(self) -> AzureCoreVhdImageArtifactProfile:
        """
        Generate the artifact profile.

        :return: The artifact profile.
        :rtype: AzureCoreVhdImageArtifactProfile
        """
        logger.debug("Generating artifact profile for VHD input.")
        artifact_profile = VhdImageArtifactProfile(
            vhd_name=self.input_artifact.artifact_name,
            vhd_version=self.input_artifact.artifact_version,
        )

        return AzureCoreVhdImageArtifactProfile(
            artifact_store=ReferencedResource(id=""),
            vhd_artifact_profile=artifact_profile,
        )

    def _generate_mapping_rule_profile(
        self,
    ) -> AzureCoreVhdImageDeployMappingRuleProfile:
        """
        Generate the mapping rule profile.

        :return: The mapping rule profile.
        :rtype: AzureCoreVhdImageDeployMappingRuleProfile
        """
        logger.debug("Generating mapping rule profile for VHD input.")
        user_configuration = self.generate_values_mappings(
            self.input_artifact.get_schema(), self.input_artifact.get_defaults()
        )

        mapping = VhdImageMappingRuleProfile(
            user_configuration=json.dumps(user_configuration),
        )

        return AzureCoreVhdImageDeployMappingRuleProfile(
            application_enablement=ApplicationEnablement.ENABLED,
            vhd_image_mapping_rule_profile=mapping,
        )

    def generate_parameters_file(self) -> LocalFileBuilder:
        """ Generate parameters file. """
        mapping_rule_profile = self._generate_mapping_rule_profile()
        if (mapping_rule_profile.vhd_image_mapping_rule_profile
           and mapping_rule_profile.vhd_image_mapping_rule_profile.user_configuration):
            params = (
                mapping_rule_profile.vhd_image_mapping_rule_profile.user_configuration
            )
        # We still want to create an empty params file,
        # otherwise the nf definition bicep will refer to files that don't exist
        else:
            params = '{}'
        logger.info(
            "Created parameters file for VHD image."
        )
        return LocalFileBuilder(
            Path(
                VNF_OUTPUT_FOLDER_FILENAME,
                NF_DEFINITION_FOLDER_NAME,
                VHD_PARAMETERS_FILENAME,
            ),
            json.dumps(json.loads(params), indent=4),
        )
