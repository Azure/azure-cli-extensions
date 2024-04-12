# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import re
from typing import Any, Dict, List, Set, Tuple

from knack.log import get_logger

from azext_aosm.build_processors.base_processor import BaseInputProcessor
from azext_aosm.common.artifact import (
    BaseArtifact,
    LocalFileACRArtifact,
    RemoteACRArtifact,
)
from azext_aosm.definition_folder.builder.local_file_builder import LocalFileBuilder
from azext_aosm.inputs.helm_chart_input import HelmChartInput
from azext_aosm.common.registry import ContainerRegistryHandler
from azext_aosm.vendored_sdks.models import (
    ApplicationEnablement,
    ArtifactType,
    AzureArcKubernetesArtifactProfile,
    AzureArcKubernetesDeployMappingRuleProfile,
    AzureArcKubernetesHelmApplication,
    DependsOnProfile,
    HelmArtifactProfile,
    HelmMappingRuleProfile,
    ManifestArtifactFormat,
    ReferencedResource,
    ResourceElementTemplate,
)

logger = get_logger(__name__)

VALUE_PATH_REGEX = (
    r".Values\.([^\s})]*)"  # Regex to find values paths in Helm chart templates
)
IMAGE_NAME_AND_VERSION_REGEX = r"\/(?P<name>[^\s]*):(?P<tag>[^\s)\"}]*)"


class HelmChartProcessor(BaseInputProcessor):
    """
    A class for processing Helm Chart inputs.

    :param name: The name of the artifact.
    :param input_artifact: The input artifact.
    """
    input_artifact: HelmChartInput

    def __init__(
        self,
        name: str,
        input_artifact: HelmChartInput,
        expose_all_params: bool,
        registry_handler: ContainerRegistryHandler,
    ):
        super().__init__(name, input_artifact, expose_all_params)
        self.registry_handler = registry_handler
        self.input_artifact: HelmChartInput = input_artifact

    def get_artifact_manifest_list(self) -> List[ManifestArtifactFormat]:
        """
        Get the list of artifacts for the artifact manifest.

        :return: A list of artifacts for the artifact manifest.
        :rtype: List[ManifestArtifactFormat]
        """
        logger.debug(
            "Getting artifact manifest list for Helm chart input %s.", self.name
        )
        artifact_manifest_list = []
        artifact_manifest_list.append(
            ManifestArtifactFormat(
                artifact_name=self.input_artifact.artifact_name,
                artifact_type=ArtifactType.OCI_ARTIFACT.value,
                artifact_version=self.input_artifact.artifact_version,
            )
        )

        # Add an artifact for each image used by the Helm chart
        for image_name, image_version in self._find_chart_images():
            artifact_manifest_list.append(
                ManifestArtifactFormat(
                    artifact_name=image_name,
                    artifact_type=ArtifactType.OCI_ARTIFACT.value,
                    artifact_version=image_version,
                )
            )

        return artifact_manifest_list

    def get_artifact_details(
        self,
    ) -> Tuple[List[BaseArtifact], List[LocalFileBuilder]]:
        """
        Get the artifact details for publishing.

        :return: A tuple containing the list of artifacts and the list of local file builders.
        :rtype: Tuple[List[BaseACRArtifact], List[LocalFileBuilder]]
        """
        logger.debug("Getting artifact details for Helm chart input %s.", self.name)
        artifact_details: List[BaseArtifact] = []

        # Helm charts can only be local file artifacts
        helm_chart_details = LocalFileACRArtifact(
            artifact_name=self.input_artifact.artifact_name,
            artifact_type=ArtifactType.OCI_ARTIFACT.value,
            artifact_version=self.input_artifact.artifact_version,
            file_path=self.input_artifact.chart_path,
        )
        artifact_details.append(helm_chart_details)
        for image_name, image_version in self._find_chart_images():
            # Container images can only be remote ACR artifacts
            registry, namespace = self.registry_handler.find_registry_for_image(
                image_name, image_version
            )
            if registry is None or namespace is None:
                continue

            artifact_details.append(
                RemoteACRArtifact(
                    artifact_name=image_name,
                    artifact_type=ArtifactType.OCI_ARTIFACT.value,
                    artifact_version=image_version,
                    source_registry=registry,
                    registry_namespace=namespace,
                )
            )

        # We do not need to return any local file builders as no artifacts are being built
        # by the CLI for Helm charts
        return artifact_details, []

    def generate_resource_element_template(self) -> ResourceElementTemplate:
        """
        Generate the resource element template from the input.

        :raises NotImplementedError: Helm charts do not support resource element templates.
        """
        raise NotImplementedError("NSDs do not support deployment of Helm charts.")

    def generate_nf_application(self) -> AzureArcKubernetesHelmApplication:
        """
        Generates an Azure Arc Kubernetes Helm application for the given Helm chart.

        :return: The generated Azure Arc Kubernetes Helm application.
        :rtype: AzureArcKubernetesHelmApplication
        """
        logger.debug("Generating NF application for Helm chart input %s.", self.name)
        artifact_profile = self._generate_artifact_profile()
        assert artifact_profile.helm_artifact_profile is not None

        # Remove the registry values paths and image pull secrets values paths from the values mappings
        # as these values are supplied by NFM when it installs the chart.
        registry_values_paths = (
            artifact_profile.helm_artifact_profile.registry_values_paths or []
        )
        image_pull_secrets_values_paths = (
            artifact_profile.helm_artifact_profile.image_pull_secrets_values_paths
            or []
        )
        mapping_rule_profile = self._generate_mapping_rule_profile(
            values_to_remove=registry_values_paths + image_pull_secrets_values_paths
        )

        return AzureArcKubernetesHelmApplication(
            name=self.name,
            # Current implementation is set all depends on profiles to empty lists
            depends_on_profile=DependsOnProfile(
                install_depends_on=[], uninstall_depends_on=[], update_depends_on=[]
            ),
            artifact_profile=artifact_profile,
            deploy_parameters_mapping_rule_profile=mapping_rule_profile,
        )

    def _find_chart_images(self) -> Set[Tuple[str, str]]:
        """
        Find the images used by the Helm chart.

        :return: A list of tuples containing the image name and version.
        :rtype: Set[Tuple[str, str]]
        """
        logger.debug("Finding images used by Helm chart %s", self.name)
        image_lines: Set[str] = set()
        self._find_image_lines(self.input_artifact, image_lines)

        images: Set[Tuple[str, str]] = set()
        for line in image_lines:
            name_and_tag = re.search(IMAGE_NAME_AND_VERSION_REGEX, line)
            if name_and_tag and len(name_and_tag.groups()) == 2:
                image_name = name_and_tag.group("name")
                image_tag = name_and_tag.group("tag")
                logger.debug(
                    "Found image %s:%s in Helm chart %s",
                    image_name,
                    image_tag,
                    self.name,
                )
                images.add((image_name, image_tag))
            else:
                logger.warning(
                    "Could not parse image name and tag in line %s in Helm chart %s",
                    line,
                    self.name,
                )

        return images

    @staticmethod
    def _find_image_lines(chart: HelmChartInput, image_lines: Set[str]) -> None:
        """
        Finds the lines containing image references in the given Helm chart and its dependencies.

        :param image_lines: A set of image lines found so far.
        :type image_lines: Set[str]
        """
        logger.debug("Finding image lines in Helm chart %s", chart.artifact_name)
        # Find the image lines in the current chart

        template_lines = []

        if chart.helm_template is not None:
            template_lines = chart.helm_template.split("\n")

        for line in template_lines:
            if "image:" in line:
                logger.debug(
                    "Found image line %s in Helm chart %s",
                    line,
                    chart.artifact_name,
                )
                image_lines.add(line.replace("image:", "").strip())

    def _generate_artifact_profile(self) -> AzureArcKubernetesArtifactProfile:
        """
        Generates an Azure Arc Kubernetes artifact profile for the given artifact store and Helm chart.

        :return: The generated Azure Arc Kubernetes artifact profile.
        :rtype: AzureArcKubernetesArtifactProfile
        """
        logger.debug("Generating artifact profile for Helm chart input.")
        image_pull_secrets_values_paths: Set[str] = set()
        # self._find_image_pull_secrets_values_paths(
        #     self.input_artifact, image_pull_secrets_values_paths
        # )

        registry_values_paths = self._find_registry_values_paths()

        helm_artifact_profile = HelmArtifactProfile(
            helm_package_name=self.input_artifact.artifact_name,
            helm_package_version_range=self.input_artifact.artifact_version,
            registry_values_paths=list(registry_values_paths),
            image_pull_secrets_values_paths=list(image_pull_secrets_values_paths),
        )

        # We set the artifact store ID as an empty string as the builder will
        # set the artifact store ID when it writes the bicep template for the NFD.
        return AzureArcKubernetesArtifactProfile(
            artifact_store=ReferencedResource(id=""),
            helm_artifact_profile=helm_artifact_profile,
        )

    def _find_image_pull_secrets_values_paths(
        self, chart: HelmChartInput, matches: Set[str]
    ) -> None:
        """
        Find image pull secrets values paths in the Helm chart templates.

        Recursively searches the dependency charts for image pull secrets values paths and adds them to the matches set.

        :param chart: The Helm chart to search.
        :type chart: HelmChartInput
        :param matches: A set of image pull secrets values paths found so far.
        :type matches: Set[str]
        """
        logger.debug(
            "Finding image pull secrets values paths in Helm chart %s",
            chart.artifact_name,
        )
        for template in chart.get_templates():
            # Loop through each line in the template.
            for index in range(len(template.data)):
                count = 0
                # If the line contains 'imagePullSecrets:' we check if there is a
                # value path matching the regex. If there is, we add it to the
                # matches set and break the loop. If there is not, we check the
                # next line. We do this until we find a line that contains a match.
                # NFM provides the image pull secrets parameter as a list. If we find
                # a line that contains 'name:' we know that the image pull secrets
                # parameter value path is for a string and not a list, and
                # so we can break from the loop.
                while ("imagePullSecrets:" in template.data[index]) and (
                    "name:" not in template.data[index + count]
                ):
                    new_matches = re.findall(
                        VALUE_PATH_REGEX, template.data[index + count]
                    )
                    if len(new_matches) != 0:
                        logger.debug(
                            "Found image pull secrets values path %s in Helm chart %s",
                            new_matches,
                            chart.artifact_name,
                        )
                        # Add the new matches to the matches set
                        matches.update(new_matches)
                        break

                    count += 1

        # Recursively search the dependency charts for image pull secrets parameters
        for dep in chart.get_dependencies():
            self._find_image_pull_secrets_values_paths(dep, matches)

    def _find_registry_values_paths(self) -> Set[str]:
        """
        Find registry values paths in the Helm chart templates.

        :return: A set of registry values paths found in the Helm chart templates.
        :rtype: Set[str]
        """
        logger.debug("Finding registry values paths in Helm chart %s", self.name)
        matches: Set[str] = set()

        image_lines: Set[str] = set()
        self._find_image_lines(self.input_artifact, image_lines)

        for line in image_lines:
            # Images are expected to be specified in the format <registry>/<image>:<tag>
            # so we split the line on '/' and then find the value path
            # in the first element of the resulting list, which corresponds to the <registry>
            # part of the line.
            new_matches = re.findall(VALUE_PATH_REGEX, line.split("/")[0])
            if len(new_matches) != 0:
                logger.debug(
                    "Found registry values path %s in Helm chart %s",
                    new_matches,
                    self.name,
                )
                # Add the new matches to the matches set
                matches.update(new_matches)

        return matches

    def _generate_mapping_rule_profile(
        self, values_to_remove: List[str]
    ) -> AzureArcKubernetesDeployMappingRuleProfile:
        """
        Generate the mappings for a Helm chart.

        :param values_to_remove: The values to remove from the generated values mappings.
        :type values_to_remove: Set[str]
        :return: The generated mapping rule profile.
        :rtype: AzureArcKubernetesDeployMappingRuleProfile
        """
        # Generate the values mappings for the Helm chart.
        values_mappings = self.generate_values_mappings(
            self.input_artifact.get_schema(),
            self.input_artifact.get_defaults(),
        )

        # Remove the values from the values mappings.
        # We want to remove the image registry and image pull secrets values paths from the values mappings
        # as these values are supplied by NFM when it installs the chart.
        for value_to_remove in values_to_remove:
            self._remove_key_from_dict(values_mappings, value_to_remove)

        mapping_rule_profile = HelmMappingRuleProfile(
            release_name=self.name,
            release_namespace=self.name,
            helm_package_version=self.input_artifact.artifact_version,
            values=json.dumps(values_mappings),
        )

        return AzureArcKubernetesDeployMappingRuleProfile(
            application_enablement=ApplicationEnablement.ENABLED,
            helm_mapping_rule_profile=mapping_rule_profile,
        )

    def _remove_key_from_dict(self, dictionary: Dict[str, Any], path: str) -> None:
        """
        Remove a key from a nested dictionary based on the given path.

        The path is in dot notation, e.g. "a.b.c" will remove the key "c" from the dictionary

        :param dictionary: The dictionary to remove the key from.
        :type dictionary: Dict[str, Any]
        :param path: The path to the key to remove.
        :type path: str
        """
        # Split the path by the dot character
        keys = path.split(".")
        # Check if the path is valid
        if len(keys) == 0 or keys[0] not in dictionary:
            return None  # Invalid path
        # If the path has only one key, remove it from the dictionary
        if len(keys) == 1:
            del dictionary[keys[0]]
            return None  # Key removed
        # Otherwise, recursively call the function on the sub-dictionary
        return self._remove_key_from_dict(dictionary[keys[0]], ".".join(keys[1:]))
