# --------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT
# License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------
"""Contains a class for generating VNF NFDs and associated resources."""
import json
import os
import re
import shutil
import tarfile
from typing import Dict, List, Any, Tuple, Optional, Iterator

import yaml
from azext_aosm.generate_nfd.nfd_generator_base import NFDGenerator
from jinja2 import Template, StrictUndefined
from knack.log import get_logger
from azext_aosm._configuration import CNFConfiguration, HelmPackageConfig
from azext_aosm.util.constants import (
    CNF_DEFINITION_BICEP_TEMPLATE,
    CNF_DEFINITION_JINJA2_SOURCE_TEMPLATE,
    CNF_MANIFEST_BICEP_TEMPLATE,
    CNF_MANIFEST_JINJA2_SOURCE_TEMPLATE,
    IMAGE_LINE_REGEX,
    IMAGE_PULL_SECRET_LINE_REGEX,
)

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
        self.nfd_jinja2_template_path = os.path.join(os.path.dirname(__file__), "templates", CNF_DEFINITION_JINJA2_SOURCE_TEMPLATE)
        self.manifest_jinja2_template_path = os.path.join(os.path.dirname(__file__), "templates", CNF_MANIFEST_JINJA2_SOURCE_TEMPLATE)
        self.output_folder_name = self.config.build_output_folder_name
        self.tmp_folder_name = "tmp"

        self.artifacts = []
        self.nf_application_configurations = []
        # JORDAN: need to add the bit to schema before properties?
        self.deployment_parameter_schema = {}

        self._bicep_path = os.path.join(
            self.output_folder_name, CNF_DEFINITION_BICEP_TEMPLATE
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
                # Why are we having to do this???
                helm_package = HelmPackageConfig(**helm_package)
                # Unpack the chart into the tmp folder
                self._extract_chart(helm_package.path_to_chart)
                # Validate chartz

                # Get schema for each chart (extract mappings and take the schema bits we need from values.schema.json)
                # + Add that schema to the big schema.
                # self.deployment_parameter_schema[
                #     "properties"
                # ] = self.get_chart_mapping_schema(helm_package)

                # Get all image line matches for files in the chart.
                image_line_matches = self.find_pattern_matches_in_chart(
                    helm_package, IMAGE_LINE_REGEX
                )
                # Get all imagePullSecrets line matches for files in the chart.
                image_pull_secret_line_matches = (
                    self.find_pattern_matches_in_chart(
                        helm_package, IMAGE_PULL_SECRET_LINE_REGEX
                    )
                )

                # generate the NF application for the chart
                self.nf_application_configurations.append(
                    self.generate_nf_application_config(
                        helm_package,
                        image_line_matches,
                        image_pull_secret_line_matches,
                    )
                )
                # Workout the list of artifacts for the chart and
                # update the list for the NFD
                self.artifacts += self.get_artifact_list(
                    helm_package, set(image_line_matches)
                )

            # Write NFD bicep
            self.write_nfd_bicep_file()
            # Write schema to schema/deploymentParameterSchema.json
            # Write Artifact Mainfest bicep
            self.write__manifest_bicep_file()

            # Copy contents of tmp folder to output folder.

        # Delete tmp folder
        #shutil.rmtree(self.tmp_folder_name)

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
        print("fname", fname)
        if fname.endswith("tar.gz") or fname.endswith("tgz"):
            tar = tarfile.open(fname, "r:gz")
            tar.extractall(path=self.tmp_folder_name)
            tar.close()
        elif fname.endswith("tar"):
            tar = tarfile.open(fname, "r:")
            tar.extractall(path=self.tmp_folder_name)
            tar.close()
        # JORDAN: avoiding tar extract errors, fix and remove later
        else:
            shutil.copytree(fname, self.tmp_folder_name, dirs_exist_ok=True)

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

    def write__manifest_bicep_file(self):
        # This will write the bicep file for the Artifact Manifest.
        with open(self.manifest_jinja2_template_path, 'r', encoding='UTF-8') as f:
            template: Template = Template(
                f.read(),
                undefined=StrictUndefined,
            )

        bicep_contents: str = template.render(
            artifacts=self.artifacts,
        )

        path = os.path.join(self.tmp_folder_name, CNF_MANIFEST_BICEP_TEMPLATE)
        with open(path, "w", encoding="utf-8") as f:
            f.write(bicep_contents)

    def write_nfd_bicep_file(self):
        # This will write the bicep file for the NFD.
        with open(self.nfd_jinja2_template_path, 'r', encoding='UTF-8') as f:
            template: Template = Template(
                f.read(),
                undefined=StrictUndefined,
            )

        bicep_contents: str = template.render(
            deployParametersPath="schema/deploymentParameterSchema.json",
            nf_application_configurations=self.nf_application_configurations,
        )

        path = os.path.join(self.tmp_folder_name, CNF_DEFINITION_BICEP_TEMPLATE)
        with open(path, "w", encoding="utf-8") as f:
            f.write(bicep_contents)

    def generate_nf_application_config(
        self,
        helm_package: HelmPackageConfig,
        image_line_matches: List[Tuple[str, ...]],
        image_pull_secret_line_matches: List[Tuple[str, ...]],
    ) -> Dict[str, Any]:
        (name, version) = self.get_chart_name_and_version(helm_package)
        registryValuesPaths = set([m[0] for m in image_line_matches])
        imagePullSecretsValuesPaths = set(image_pull_secret_line_matches)

        return {
            "name": helm_package.name,
            "chartName": name,
            "chartVersion": version,
            "dependsOnProfile": helm_package.depends_on,
            "registryValuesPaths": list(registryValuesPaths),
            "imagePullSecretsValuesPaths": list(imagePullSecretsValuesPaths),
            # "valueMappingsPath": self.generate_parmeter_mappings(helm_package),
            "valueMappingsPath": "",
        }

    def _find_yaml_files(self, directory) -> Iterator[str]:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".yaml") or file.endswith(".yml"):
                    yield os.path.join(root, file)

    def find_pattern_matches_in_chart(
        self, helm_package: HelmPackageConfig, pattern: str
    ) -> List[Tuple[str, ...]]:
        chart_dir = os.path.join(self.tmp_folder_name, helm_package.name)
        matches = []

        for file in self._find_yaml_files(chart_dir):
            with open(file, "r", encoding="UTF-8") as f:
                contents = f.read()
                matches += re.findall(pattern, contents)

        return matches

    def get_artifact_list(
        self,
        helm_package: HelmPackageConfig,
        image_line_matches: List[Tuple[str, ...]],
    ) -> List[Any]:
        artifact_list = []
        (chart_name, chart_version) = self.get_chart_name_and_version(
            helm_package
        )
        helm_artifact = {
            "name": chart_name,
            "version": chart_version,
        }
        artifact_list.append(helm_artifact)

        for match in image_line_matches:
            artifact_list.append(
                {
                    "name": match[1],
                    "version": match[2],
                }
            )

        return artifact_list

    ## JORDAN: this is done cheating by not actually looking at the schema
    def get_chart_mapping_schema(
        self, helm_package: HelmPackageConfig
    ) -> Dict[Any, Any]:
        # We need to take the mappings from the values.nondef.yaml file and generate the schema
        # from the values.schema.json file.
        # Basically take the bits of the schema that are relevant to the parameters requested.

        non_def_values = os.path.join(
            self.tmp_folder_name, helm_package.name, "values.nondef.yaml"
        )

        with open(non_def_values, "r") as stream:
            data = yaml.load(stream, Loader=yaml.SafeLoader)
            deploy_params_list = []
            params_for_schema = self.find_deploy_params(
                data, deploy_params_list
            )

        schema_dict = {}
        for i in params_for_schema:
            schema_dict[i] = {"type": "string", "description": "no descr"}

        return schema_dict

    ## JORDAN: change this to save the key and value that has deployParam in it so we can check the schema for the key
    def find_deploy_params(self, nested_dict, deploy_params_list):
        for k, v in nested_dict.items():
            if isinstance(v, str) and "deployParameters" in v:
                # only add the parameter name (not deployParam. or anything after)
                param = v.split(".", 1)[1]
                param = param.split("}", 1)[0]
                deploy_params_list.append(param)
                print(deploy_params_list)
            elif hasattr(v, "items"):  # v is a dict
                self.find_deploy_params(v, deploy_params_list)

        return deploy_params_list

    def get_chart_name_and_version(
        self, helm_package: HelmPackageConfig
    ) -> Tuple[str, str]:
        chart = os.path.join(
            self.tmp_folder_name, helm_package.name, "Chart.yaml"
        )

        with open(chart) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            chart_name = data["name"]
            chart_version = data["version"]

        return (chart_name, chart_version)

    ## JORDAN: change this to return string(loadJson).. with the file in output
    def generate_parmeter_mappings(
        self, helm_package: HelmPackageConfig
    ) -> str:
        # Basically copy the values.nondef.yaml file to the right place.
        values = os.path.join(
            self.tmp_folder_name, helm_package.name, "values.nondef.yaml"
        )

        mappings_folder_path = os.path.join(
            self.tmp_folder_name, "configMappings"
        )
        mappings_filename = f"{helm_package.name}-mappings.json"
        if not os.path.exists(mappings_folder_path):
            os.mkdir(mappings_folder_path)

        mapping_file_path = os.path.join(
            mappings_folder_path, mappings_filename
        )

        with open(values) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        with open(mapping_file_path, "w") as file:
            json.dump(data, file)

        return os.path.join("configMappings", mappings_filename)
