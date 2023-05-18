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
    DEPLOYMENT_PARAMETER_MAPPING_REGEX,
    IMAGE_LINE_REGEX,
    IMAGE_PULL_SECRET_LINE_REGEX,
)
from azure.cli.core.azclierror import InvalidTemplateError

logger = get_logger(__name__)


class CnfNfdGenerator(NFDGenerator):
    """
    _summary_

    :param NFDGenerator: _description_
    :type NFDGenerator: _type_
    """

    def __init__(self, config: CNFConfiguration):
        """Create a new VNF NFD Generator."""
        super(NFDGenerator, self).__init__()
        self.config = config
        self.nfd_jinja2_template_path = os.path.join(
            os.path.dirname(__file__),
            "templates",
            CNF_DEFINITION_JINJA2_SOURCE_TEMPLATE,
        )
        self.manifest_jinja2_template_path = os.path.join(
            os.path.dirname(__file__),
            "templates",
            CNF_MANIFEST_JINJA2_SOURCE_TEMPLATE,
        )
        self.output_folder_name = self.config.build_output_folder_name
        self.tmp_folder_name = "tmp"

        self.artifacts = []
        self.nf_application_configurations = []
        self.deployment_parameter_schema = {
            "$schema": "https://json-schema.org/draft-07/schema#",
            "title": "DeployParametersSchema",
            "type": "object",
            "properties": {}}

        self._bicep_path = os.path.join(
            self.output_folder_name, CNF_DEFINITION_BICEP_TEMPLATE
        )

    def generate_nfd(self) -> None:
        """Generate a VNF NFD which comprises an group, an Artifact Manifest and a NFDV."""
        # Create tmp folder.
        os.mkdir(self.tmp_folder_name)

        if self.bicep_path:
            shutil.rmtree(self.tmp_folder_name)
            raise InvalidTemplateError(
                f"ERROR: Using the existing NFD bicep template {self.bicep_path}.\nPlease fix this and run the command again."
            )
        else:
            for helm_package in self.config.helm_packages:
                # TO FIGURE OUT: Why are we having to do this???
                helm_package = HelmPackageConfig(**helm_package)
                # Unpack the chart into the tmp folder
                self._extract_chart(helm_package.path_to_chart)

                # TODO: Validate charts

                # Get schema for each chart (extract mappings and take the schema bits we need from values.schema.json)
                # + Add that schema to the big schema.
                self.deployment_parameter_schema[
                    "properties"
                ].update(self.get_chart_mapping_schema(helm_package))
                
                # Get all image line matches for files in the chart.
                # Do this here so we don't have to do it multiple times.
                image_line_matches = self.find_pattern_matches_in_chart(
                    helm_package, IMAGE_LINE_REGEX
                )
                
                # Generate the NF application configuration for the chart
                self.nf_application_configurations.append(
                    self.generate_nf_application_config(
                        helm_package,
                        image_line_matches,
                        self.find_pattern_matches_in_chart(
                            helm_package, IMAGE_PULL_SECRET_LINE_REGEX
                        ),
                    )
                )
                # Workout the list of artifacts for the chart and
                # update the list for the NFD with any unique artifacts.
                chart_artifacts = self.get_artifact_list(
                    helm_package, set(image_line_matches)
                )
                self.artifacts += [
                    a for a in chart_artifacts if a not in self.artifacts
                ]

            self.write_nfd_bicep_file()
            self.write_schema_to_file()
            self.write_manifest_bicep_file()
            self.copy_to_output_folder()
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
        else:
            # Throw error here
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

    def write_manifest_bicep_file(self) -> None:
        # This will write the bicep file for the Artifact Manifest.
        with open(
            self.manifest_jinja2_template_path, "r", encoding="UTF-8"
        ) as f:
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

    def write_nfd_bicep_file(self) -> None:
        # This will write the bicep file for the NFD.
        with open(self.nfd_jinja2_template_path, "r", encoding="UTF-8") as f:
            template: Template = Template(
                f.read(),
                undefined=StrictUndefined,
            )

        bicep_contents: str = template.render(
            deployParametersPath="schemas/deploymentParameters.json",
            nf_application_configurations=self.nf_application_configurations,
        )

        path = os.path.join(
            self.tmp_folder_name, CNF_DEFINITION_BICEP_TEMPLATE
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(bicep_contents)

    def write_schema_to_file(self) -> None:
        full_schema = os.path.join(
            self.tmp_folder_name, "deploymentParameters.json"
        )
        with open(full_schema, "w", encoding="UTF-8") as f:
            json.dump(self.deployment_parameter_schema, f, indent=4)
        
    def copy_to_output_folder(self) -> None:
        if not os.path.exists(self.output_folder_name):
            os.mkdir(self.output_folder_name)
            os.mkdir(self.output_folder_name + "/schemas")

        nfd_bicep_path = os.path.join(
            self.tmp_folder_name, CNF_DEFINITION_BICEP_TEMPLATE
        )
        shutil.copy(nfd_bicep_path, self.output_folder_name)

        manifest_bicep_path = os.path.join(
            self.tmp_folder_name, CNF_MANIFEST_BICEP_TEMPLATE
        )
        shutil.copy(manifest_bicep_path, self.output_folder_name)

        config_mappings_path = os.path.join(
            self.tmp_folder_name, "configMappings"
        )
        shutil.copytree(
            config_mappings_path,
            self.output_folder_name + "/configMappings",
            dirs_exist_ok=True,
        )

        full_schema = os.path.join(
            self.tmp_folder_name, "deploymentParameters.json"
        )
        shutil.copy(
            full_schema,
            self.output_folder_name
            + "/schemas"
            + "/deploymentParameters.json",
        )

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
            "valueMappingsPath": self.generate_parmeter_mappings(helm_package),
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

    def get_chart_mapping_schema(
        self, helm_package: HelmPackageConfig
    ) -> Dict[Any, Any]:
        non_def_values = os.path.join(
            self.tmp_folder_name, helm_package.name, "values.mappings.yaml"
        )
        values_schema = os.path.join(
            self.tmp_folder_name, helm_package.name, "values.schema.json"
        )

        with open(non_def_values, "r", encoding="utf-8") as stream:
            values_data = yaml.load(stream, Loader=yaml.SafeLoader)

        with open(values_schema, "r", encoding="utf-8") as f:
            data = json.load(f)
            schema_data = data["properties"]

        try:
            final_schema = self.find_deploy_params(
                values_data, schema_data, {}
            )
        except KeyError as e:
            raise InvalidTemplateError(
                f"ERROR: Your schema and values for the helm package '{helm_package.name}' do not match. Please fix this and run the command again."
            ) from e

        return final_schema

    def find_deploy_params(
        self, nested_dict, schema_nested_dict, final_schema
    ) -> Dict[Any, Any]:
        original_schema_nested_dict = schema_nested_dict
        for k, v in nested_dict.items():
            # if value is a string and contains deployParameters.
            if isinstance(v, str) and re.search(DEPLOYMENT_PARAMETER_MAPPING_REGEX, v):
                
                # only add the parameter name (e.g. from {deployParameter.zone} only param = zone)
                param = v.split(".", 1)[1]
                param = param.split("}", 1)[0]

                # add the schema for k (from the big schema) to the (smaller) schema
                final_schema.update({param: { "type" : schema_nested_dict["properties"][k]["type"]}})

            # else if value is a (non-empty) dictionary (i.e another layer of nesting)
            elif hasattr(v, "items") and v.items():
                # handling schema having properties which doesn't map directly to the values file nesting
                if "properties" in schema_nested_dict.keys():
                    schema_nested_dict = schema_nested_dict["properties"][k]
                else:
                    schema_nested_dict = schema_nested_dict[k]
                # recursively call function with values (i.e the nested dictionary)
                self.find_deploy_params(v, schema_nested_dict, final_schema)
                # reset the schema dict to its original value (once finished with that level of recursion)
                schema_nested_dict = original_schema_nested_dict

        return final_schema

    def get_chart_name_and_version(
        self, helm_package: HelmPackageConfig
    ) -> Tuple[str, str]:
        chart = os.path.join(
            self.tmp_folder_name, helm_package.name, "Chart.yaml"
        )

        with open(chart, "r", encoding="utf-8") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            chart_name = data["name"]
            chart_version = data["version"]

        return (chart_name, chart_version)

    def generate_parmeter_mappings(
        self, helm_package: HelmPackageConfig
    ) -> str:
        # Basically copy the values.mappings.yaml file to the right place.
        values = os.path.join(
            self.tmp_folder_name, helm_package.name, "values.mappings.yaml"
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

        with open(values, "r", encoding="utf-8") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        with open(mapping_file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        return os.path.join("configMappings", mappings_filename)
