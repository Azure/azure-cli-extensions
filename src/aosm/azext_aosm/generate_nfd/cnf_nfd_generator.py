# --------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT
# License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------
"""Contains a class for generating VNF NFDs and associated resources."""
import os
from typing import Dict, List, Any, Tuple
from azext_aosm.generate_nfd.nfd_generator_base import NFDGenerator
from knack.log import get_logger
from azext_aosm._configuration import CNFConfiguration
from azext_aosm.vendored_sdks.models import AzureArcKubernetesHelmApplication
from azext_aosm._constants import CNF_DEFINITION_BICEP_SOURCE_TEMPLATE
logger = get_logger(__name__)


class CnfNfdGenerator(NFDGenerator):
    """
    _summary_

    :param NFDGenerator: _description_
    :type NFDGenerator: _type_
    """

    def __init__(self, config: CNFConfiguration):
        super(NFDGenerator, self).__init__(
            config=config,
        )
        self.config = config
        self.bicep_template_name = CNF_DEFINITION_BICEP_SOURCE_TEMPLATE

    def generate_nfd(self):
        pass

    def write(self):
        pass

    def _create_nfd_folder(self):
        pass

    def generate_nf_applications(
        self, helm_packages_config: List[Any]
    ) -> List[Dict[str, Any]]:
        # This will mostly call the functions below.
        nf_applications = []

        for helm_package in helm_packages_config:
            nf_applications.append(self.generate_nf_application(helm_package))
        return nf_applications

    def generate_nf_application(
        self, helm_package: Dict[Any, Any]
    ) -> Dict[str, Any]:
        (name, version) = self.get_chart_name_and_version(helm_package)
        return {
            "artifactType": "HelmPackage",
            "name": helm_package["name"],
            "dependsOnProfile": helm_package["dependsOnProfile"],
            "artifactProfile": {
                "artifactStore": {"id": "acrArtifactStore.id"},
                "helmArtifactProfile": {
                    "helmPackageName": name,
                    "helmPackageVersionRange": version,
                    "registryValuesPaths": [
                        "'global.registry.docker.repoPath'"
                    ],
                    "imagePullSecretsValuesPaths": [
                        "'global.registry.docker.imagePullSecrets'"
                    ],
                },
            },
            "deployParametersMappingRuleProfile": {
                "applicationEnablement": "'Enabled'",
                "helmMappingRuleProfile": {
                    "releaseNamespace": "'PACKAGE_NAME'",
                    "releaseName": "'PACKAGE_NAME'",
                    "helmPackageVersion": "'PACKAGE_VERSION'",
                    "values": self.generate_parmeter_mappings(),
                },
            },
        }

    def generate_deployment_parameters_schema(self):
        # We need to take the parameters requested by the mapping file (values.nondef.yaml)
        # and generate the deployment parameters schema based on values.schema.json.
        # Basically take the bits of the schema that are relevant to the parameters requested.
        pass

    def get_chart_name_and_version(self, helm_package: Dict[Any, Any]) -> Tuple[str, str]:
        # We need to get the chart name and version from the Chart.yaml file.
        return ("chart_name", "chart_version")

    def some_fun_to_check_ragistry_and_image_secret_path(self):
        # Need to work out what we are doing here???
        pass

    def generate_parmeter_mappings(self) -> str:
        # Basically copy the values.nondef.yaml file to the right place.
        pass
