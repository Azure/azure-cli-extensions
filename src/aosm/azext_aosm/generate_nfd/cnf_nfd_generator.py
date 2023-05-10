# --------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT
# License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------
"""Contains a class for generating VNF NFDs and associated resources."""
import json
import os
import shutil
import subprocess
import tarfile
from typing import Dict, List, Any, Tuple, Optional
from azext_aosm.generate_nfd.nfd_generator_base import NFDGenerator
from knack.log import get_logger
from azext_aosm._configuration import CNFConfiguration, HelmPackageConfig
from azext_aosm.util.constants import CNF_DEFINITION_BICEP_SOURCE_TEMPLATE

logger = get_logger(__name__)


class CnfNfdGenerator(NFDGenerator):
    """
    _summary_

    :param NFDGenerator: _description_
    :type NFDGenerator: _type_
    """

    def __init__(self, config: CNFConfiguration):
        super(NFDGenerator, self).__init__()
        self.config = config
        self.bicep_template_name = CNF_DEFINITION_BICEP_SOURCE_TEMPLATE
        self.output_folder_name = self.config.build_output_folder_name
        self.tmp_folder_name = "tmp"

        self.artifacts = []
        self.nf_applications = []
        self.deployment_parameter_schema = {}

        self._bicep_path = os.path.join(
            self.output_folder_name, self.bicep_template_name
        )

    def generate_nfd(self):
        """Generate a VNF NFD which comprises an group, an Artifact Manifest and a NFDV."""
        # Create tmp folder.
        os.mkdir(self.tmp_folder_name)

        if self.bicep_path:
            print(f"Using the existing NFD bicep template {self.bicep_path}.")
            print(
                f"To generate a new NFD, delete the folder {os.path.dirname(self.bicep_path)} and re-run this command."
            )
        else:
            for helm_package in self.config.helm_packages:
                # Unpack the chart into the tmp folder
                self._extract_chart(helm_package)
                # Validate chart
                # Get schema for each chart (extract mappings and take the schema bits we need from values.schema.json)
                self.deployment_parameter_schema["properties"].update(self.get_chart_mapping_schema(helm_package.name))
                # Add that schema to the big schema.
                # generate the NF application for the chart
                self.generate_nf_application(helm_package)
                # Workout the list of artifacts for the chart
                self.artifacts.append(self.get_artifact_list(helm_package.name))
            # Write NFD bicep
            self.write_nfd_bicep_file()
            # Write schema to schema/deploymentParameterSchema.json
            # Write Artifact Mainfest bicep

            # Copy contents of tmp folder to output folder.

        # Delete tmp folder
        shutil.rmtree(self.tmp_folder_name)

    @property
    def bicep_path(self) -> Optional[str]:
        """Returns the path to the bicep file for the NFD if it has been created."""
        if os.path.exists(self._bicep_path):
            return self._bicep_path

        return None

    def _extract_chart(self, fname: str) -> None:
        """
        Extract the chart into the tmp folder.

        :param helm_package: The helm package to extract.
        :type helm_package: HelmPackageConfig
        """
        if fname.endswith("tar.gz") or fname.endswith("tgz"):
            tar = tarfile.open(fname, "r:gz")
            tar.extractall(path=self.tmp_folder_name)
            tar.close()
        elif fname.endswith("tar"):
            tar = tarfile.open(fname, "r:")
            tar.extractall(path=self.tmp_folder_name)
            tar.close()

    def _create_nfd_folder(self) -> None:
        """
        Create the folder for the NFD bicep files.

        :raises RuntimeError: If the user aborts.
        """
        if os.path.exists(self.output_folder_name):
            carry_on = input(
                f"The folder {self.output_folder_name} already exists - delete it and continue? (y/n)"
            )
            if carry_on != "y":
                raise RuntimeError("User aborted!")

            shutil.rmtree(self.output_folder_name)

        logger.info("Create NFD bicep %s", self.output_folder_name)
        os.mkdir(self.output_folder_name)

    def write_nfd_bicep_file(self):
        # This will write the bicep file for the NFD.
        code_dir = os.path.dirname(__file__)
        arm_template_path = os.path.join(code_dir, "templates/cnfdefinition.json")

        with open(arm_template_path, "r", encoding="UTF-8") as f:
            cnf_arm_template_dict = json.load(f)

        cnf_arm_template_dict["resources"][0]["properties"][
            "networkFunctionTemplate"
        ]["networkFunctionApplications"] = self.nf_applications

        self.write_arm_to_bicep(cnf_arm_template_dict, f"{self.tmp_folder_name}/{self.config.nf_name}-nfdv.json")

    def write_arm_to_bicep(self, arm_template_dict: Dict[Any, Any], arm_file: str):
        with open(arm_file, 'w', encoding="UTF-8") as f:
            print("Writing ARM template to json file.")
            json.dump(arm_template_dict, f, indent=4)
        try:
            cmd = f"az bicep decompile --file {os.path.abspath(arm_file)} --only-show-errors"
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            raise e
        finally:
            os.remove(arm_file)

    def generate_nf_application(
        self, helm_package: HelmPackageConfig
    ) -> Dict[str, Any]:
        (name, version) = self.get_chart_name_and_version(helm_package.path_to_chart)
        return {
            "artifactType": "HelmPackage",
            "name": helm_package.name,
            "dependsOnProfile": helm_package.depends_on,
            "artifactProfile": {
                "artifactStore": {
                    "id": "[resourceId('Microsoft.HybridNetwork/publishers/artifactStores', parameters('publisherName'), parameters('acrArtifactStoreName'))]"
                },
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
                    "releaseNamespace": name,
                    "releaseName": name,
                    "helmPackageVersion": version,
                    "values": self.generate_parmeter_mappings(),
                },
            },
        }

    def get_artifact_list(self, helm_package: HelmPackageConfig) -> List[Any]:
        pass

    def get_chart_mapping_schema(self, helm_package: HelmPackageConfig) -> Dict[Any, Any]:
        # We need to take the mappings from the values.nondef.yaml file and generate the schema
        # from the values.schema.json file.
        # Basically take the bits of the schema that are relevant to the parameters requested.
        pass

    def get_chart_name_and_version(
        self, helm_package: Dict[Any, Any]
    ) -> Tuple[str, str]:
        # We need to get the chart name and version from the Chart.yaml file.
        return ("chart_name", "chart_version")

    def some_fun_to_check_ragistry_and_image_secret_path(self):
        # Need to work out what we are doing here???
        pass

    def generate_parmeter_mappings(self) -> str:
        # Basically copy the values.nondef.yaml file to the right place.
        pass
