# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Contains a class for generating CNF NFDs and associated resources."""
import json
import re
import shutil
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

import yaml
from azure.cli.core.azclierror import FileOperationError, InvalidTemplateError
from jinja2 import StrictUndefined, Template
from knack.log import get_logger

from azext_aosm._configuration import CNFConfiguration, HelmPackageConfig
from azext_aosm.generate_nfd.nfd_generator_base import NFDGenerator
from azext_aosm.util.constants import (
    CNF_DEFINITION_BICEP_TEMPLATE_FILENAME,
    CNF_DEFINITION_JINJA2_SOURCE_TEMPLATE_FILENAME,
    CNF_MANIFEST_BICEP_TEMPLATE_FILENAME,
    CNF_MANIFEST_JINJA2_SOURCE_TEMPLATE_FILENAME,
    CNF_VALUES_SCHEMA_FILENAME,
    CONFIG_MAPPINGS_DIR_NAME,
    DEPLOYMENT_PARAMETER_MAPPING_REGEX,
    DEPLOYMENT_PARAMETERS_FILENAME,
    GENERATED_VALUES_MAPPINGS_DIR_NAME,
    IMAGE_NAME_AND_VERSION_REGEX,
    IMAGE_PATH_REGEX,
    IMAGE_PULL_SECRETS_START_STRING,
    IMAGE_START_STRING,
    SCHEMA_PREFIX,
    SCHEMAS_DIR_NAME,
)
from azext_aosm.util.utils import input_ack

logger = get_logger(__name__)


@dataclass
class Artifact:
    """Information about an artifact."""

    name: str
    version: str


@dataclass
class NFApplicationConfiguration:  # pylint: disable=too-many-instance-attributes
    name: str
    chartName: str
    chartVersion: str
    releaseName: str
    dependsOnProfile: List[str]
    registryValuesPaths: List[str]
    imagePullSecretsValuesPaths: List[str]
    valueMappingsFile: str

    def __post_init__(self):
        """Format the fields based on the NFDV validation rules."""
        self._format_name()
        self._format_release_name()

    def _format_name(self):
        """
        Format the name field.

        The name should start with a alphabetic character, have alphanumeric characters
        or '-' in-between and end with alphanumerc character, and be less than 64
        characters long. See NfdVersionValidationHelper.cs in pez codebase
        """
        # Replace any non (alphanumeric or '-') characters with '-'
        self.name = re.sub("[^0-9a-zA-Z-]+", "-", self.name)
        # Strip leading or trailing -
        self.name = self.name.strip("-")
        self.name = self.name[:64]

        if not self.name:
            raise InvalidTemplateError(
                "The name field of the NF application configuration for helm package "
                f"{self.chartName} is empty after removing invalid characters. "
                "Valid characters are alphanumeric and '-'. Please fix this in the name"
                " field for the helm package in your input config file."
            )

    def _format_release_name(self):
        """
        Format release name.

        It must consist of lower case alphanumeric characters, '-' or '.', and must
        start and end with an alphanumeric character See
        AzureArcKubernetesRuleBuilderExtensions.cs  and
        AzureArcKubernetesNfValidationMessage.cs in pez codebase
        """
        self.releaseName = self.releaseName.lower()
        # Replace any non (alphanumeric or '-' or '.') characters with '-'
        self.releaseName = re.sub("[^0-9a-z-.]+", "-", self.releaseName)
        # Strip leading - or .
        self.releaseName = self.releaseName.strip("-")
        self.releaseName = self.releaseName.strip(".")
        if not self.releaseName:
            raise InvalidTemplateError(
                "The releaseName field of the NF application configuration for helm "
                f"chart {self.chartName} is empty after formatting and removing invalid"
                "characters. Valid characters are alphanumeric, -.' and '-' and the "
                "releaseName must start and end with an alphanumeric character. The "
                "value of this field is taken from Chart.yaml within the helm package. "
                "Please fix up the helm package. Before removing invalid characters"
                f", the releaseName was {self.chartName}."
            )


@dataclass
class ImageInfo:
    parameter: List[str]
    name: str
    version: str


class CnfNfdGenerator(NFDGenerator):  # pylint: disable=too-many-instance-attributes
    """
    CNF NFD Generator.

    This takes a config file, and outputs:
    - A bicep file for the NFDV
    - Parameters files that are used by the NFDV bicep file, these are the
      deployParameters and the mapping profiles of those deploy parameters
    - A bicep file for the Artifact manifests
    """

    def __init__(self, config: CNFConfiguration, interactive: bool = False):
        """
        Create a new CNF NFD Generator.

        Interactive parameter is only used if the user wants to generate the values
        mapping file from the values.yaml in the helm package, and also requires the
        mapping file in config to be blank.
        """
        self.config = config
        self.nfd_jinja2_template_path = (
            Path(__file__).parent
            / "templates"
            / CNF_DEFINITION_JINJA2_SOURCE_TEMPLATE_FILENAME
        )
        self.manifest_jinja2_template_path = (
            Path(__file__).parent
            / "templates"
            / CNF_MANIFEST_JINJA2_SOURCE_TEMPLATE_FILENAME
        )
        self.output_directory: Path = self.config.output_directory_for_build
        self._cnfd_bicep_path = (
            self.output_directory / CNF_DEFINITION_BICEP_TEMPLATE_FILENAME
        )
        self._tmp_dir: Optional[Path] = None

        self.artifacts: List[Artifact] = []
        self.nf_application_configurations: List[NFApplicationConfiguration] = []
        self.deployment_parameter_schema: Dict[str, Any] = SCHEMA_PREFIX
        self.interactive = interactive

    def generate_nfd(self) -> None:
        """Generate a CNF NFD which comprises a group, an Artifact Manifest and an NFDV."""

        # Create temporary directory.
        with tempfile.TemporaryDirectory() as tmpdirname:
            self._tmp_dir = Path(tmpdirname)
            try:
                for helm_package in self.config.helm_packages:
                    # Unpack the chart into the tmp directory
                    assert isinstance(helm_package, HelmPackageConfig)

                    self._extract_chart(Path(helm_package.path_to_chart))

                    # TODO: Validate charts

                    # Create a chart mapping schema if none has been passed in.
                    if not helm_package.path_to_mappings:
                        self._generate_chart_value_mappings(helm_package)

                    # Get schema for each chart
                    # (extract mappings and relevant parts of the schema)
                    # + Add that schema to the big schema.
                    self.deployment_parameter_schema["properties"].update(
                        self._get_chart_mapping_schema(helm_package)
                    )

                    # Get all image line matches for files in the chart.
                    # Do this here so we don't have to do it multiple times.
                    image_line_matches = self._find_image_parameter_from_chart(
                        helm_package
                    )

                    # Creates a flattened list of image registry paths to prevent set error
                    image_registry_paths: List[str] = []
                    for image_info in image_line_matches:
                        image_registry_paths += image_info.parameter

                    # Generate the NF application configuration for the chart
                    # passed to jinja2 renderer to render bicep template
                    self.nf_application_configurations.append(
                        self._generate_nf_application_config(
                            helm_package,
                            image_registry_paths,
                            self._find_image_pull_secrets_parameter_from_chart(
                                helm_package
                            ),
                        )
                    )
                    # Workout the list of artifacts for the chart and
                    # update the list for the NFD with any unique artifacts.
                    chart_artifacts = self._get_artifact_list(
                        helm_package, image_line_matches
                    )
                    self.artifacts += [
                        a for a in chart_artifacts if a not in self.artifacts
                    ]
                self._write_nfd_bicep_file()
                self._write_schema_to_file()
                self._write_manifest_bicep_file()
                self._copy_to_output_directory()
                print(
                    f"Generated NFD bicep template created in {self.output_directory}"
                )
                print(
                    "Please review these templates. When you are happy with them run "
                    "`az aosm nfd publish` with the same arguments."
                )
            except InvalidTemplateError as e:
                raise e

    @property
    def nfd_bicep_path(self) -> Optional[Path]:
        """Returns the path to the bicep file for the NFD if it has been created."""
        if self._cnfd_bicep_path.exists():
            return self._cnfd_bicep_path
        return None

    def _extract_chart(self, path: Path) -> None:
        """
        Extract the chart into the tmp directory.

        :param path: The path to helm package
        """
        assert self._tmp_dir

        logger.debug("Extracting helm package %s", path)

        file_extension = path.suffix
        if file_extension in (".gz", ".tgz"):
            with tarfile.open(path, "r:gz") as tar:
                tar.extractall(path=self._tmp_dir)

        elif file_extension == ".tar":
            with tarfile.open(path, "r:") as tar:
                tar.extractall(path=self._tmp_dir)

        else:
            raise InvalidTemplateError(
                f"ERROR: The helm package '{path}' is not a .tgz, .tar or .tar.gz file."
                " Please fix this and run the command again."
            )

    def _generate_chart_value_mappings(self, helm_package: HelmPackageConfig) -> None:
        """
        Optional function to create a chart value mappings file with every value being a deployParameter.

        Expected use when a helm chart is very simple and user wants every value to be a
        deployment parameter.
        """
        assert self._tmp_dir
        logger.debug(
            "Creating chart value mappings file for %s", helm_package.path_to_chart
        )
        print(f"Creating chart value mappings file for {helm_package.path_to_chart}.")

        # Get all the values files in the chart
        top_level_values_yaml = self._read_top_level_values_yaml(helm_package)

        mapping_to_write = self._replace_values_with_deploy_params(
            top_level_values_yaml, None
        )

        # Write the mapping to a file
        mapping_directory: Path = self._tmp_dir / GENERATED_VALUES_MAPPINGS_DIR_NAME
        mapping_directory.mkdir(exist_ok=True)
        mapping_filepath = (
            mapping_directory / f"{helm_package.name}-generated-mapping.yaml"
        )
        with open(mapping_filepath, "w", encoding="UTF-8") as mapping_file:
            yaml.dump(mapping_to_write, mapping_file)

        # Update the config that points to the mapping file
        helm_package.path_to_mappings = str(mapping_filepath)

    def _read_top_level_values_yaml(
        self, helm_package: HelmPackageConfig
    ) -> Dict[str, Any]:
        """
        Return a dictionary of the values.yaml|yml read from the root of the helm package.

        :param helm_package: The helm package to look in
        :type helm_package: HelmPackageConfig
        :raises FileOperationError: if no values.yaml|yml found
        :return: A dictionary of the yaml read from the file
        :rtype: Dict[str, Any]
        """
        assert self._tmp_dir
        for file in Path(self._tmp_dir / helm_package.name).iterdir():
            if file.name in ("values.yaml", "values.yml"):
                with file.open(encoding="UTF-8") as values_file:
                    values_yaml = yaml.safe_load(values_file)
                return values_yaml

        raise FileOperationError(
            "Cannot find top level values.yaml/.yml file in Helm package."
        )

    def _write_manifest_bicep_file(self) -> None:
        """Write the bicep file for the Artifact Manifest to the temp directory."""
        assert self._tmp_dir

        with open(self.manifest_jinja2_template_path, "r", encoding="UTF-8") as f:
            template: Template = Template(
                f.read(),
                undefined=StrictUndefined,
            )

        bicep_contents: str = template.render(
            artifacts=self.artifacts,
        )

        path = self._tmp_dir / CNF_MANIFEST_BICEP_TEMPLATE_FILENAME
        with open(path, "w", encoding="utf-8") as f:
            f.write(bicep_contents)

        logger.info("Created artifact manifest bicep template: %s", path)

    def _write_nfd_bicep_file(self) -> None:
        """Write the bicep file for the NFD to the temp directory."""
        assert self._tmp_dir
        with open(self.nfd_jinja2_template_path, "r", encoding="UTF-8") as f:
            template: Template = Template(
                f.read(),
                undefined=StrictUndefined,
            )

        bicep_contents: str = template.render(
            nf_application_configurations=self.nf_application_configurations,
        )

        path = self._tmp_dir / CNF_DEFINITION_BICEP_TEMPLATE_FILENAME
        with open(path, "w", encoding="utf-8") as f:
            f.write(bicep_contents)

        logger.info("Created NFD bicep template: %s", path)

    def _write_schema_to_file(self) -> None:
        """Write the schema to file deploymentParameters.json to the temp directory."""
        logger.debug("Create deploymentParameters.json")
        assert self._tmp_dir

        full_schema = self._tmp_dir / DEPLOYMENT_PARAMETERS_FILENAME
        with open(full_schema, "w", encoding="UTF-8") as f:
            json.dump(self.deployment_parameter_schema, f, indent=4)

        logger.debug("%s created", full_schema)

    def _copy_to_output_directory(self) -> None:
        """
        Copy files from the temp directory to the output directory.

        Files are the config mappings, schema and bicep templates (artifact manifest and
        NFDV).
        """
        assert self._tmp_dir

        logger.info("Create NFD bicep %s", self.output_directory)

        Path(self.output_directory / SCHEMAS_DIR_NAME).mkdir(
            parents=True, exist_ok=True
        )

        # Copy the nfd and the manifest bicep files to the output directory
        shutil.copy(
            self._tmp_dir / CNF_DEFINITION_BICEP_TEMPLATE_FILENAME,
            self.output_directory,
        )
        shutil.copy(
            self._tmp_dir / CNF_MANIFEST_BICEP_TEMPLATE_FILENAME, self.output_directory
        )

        # Copy any generated values mappings YAML files to the corresponding directory in
        # the output directory so that the user can edit them and re-run the build if
        # required
        if Path(self._tmp_dir / GENERATED_VALUES_MAPPINGS_DIR_NAME).exists():
            shutil.copytree(
                self._tmp_dir / GENERATED_VALUES_MAPPINGS_DIR_NAME,
                self.output_directory / GENERATED_VALUES_MAPPINGS_DIR_NAME,
            )

        # Copy the JSON config mappings and deploymentParameters schema that are used
        # for the NFD to the output directory
        shutil.copytree(
            self._tmp_dir / CONFIG_MAPPINGS_DIR_NAME,
            self.output_directory / CONFIG_MAPPINGS_DIR_NAME,
            dirs_exist_ok=True,
        )
        shutil.copy(
            self._tmp_dir / DEPLOYMENT_PARAMETERS_FILENAME,
            self.output_directory / SCHEMAS_DIR_NAME / DEPLOYMENT_PARAMETERS_FILENAME,
        )

        logger.info("Copied files to %s", self.output_directory)

    def _generate_nf_application_config(
        self,
        helm_package: HelmPackageConfig,
        image_registry_path: List[str],
        image_pull_secret_line_matches: List[str],
    ) -> NFApplicationConfiguration:
        """Generate NF application config."""
        (name, version) = self._get_chart_name_and_version(helm_package)

        registry_values_paths = set(image_registry_path)
        image_pull_secrets_values_paths = set(image_pull_secret_line_matches)

        return NFApplicationConfiguration(
            name=helm_package.name,
            chartName=name,
            chartVersion=version,
            releaseName=name,
            dependsOnProfile=helm_package.depends_on,
            registryValuesPaths=list(registry_values_paths),
            imagePullSecretsValuesPaths=list(image_pull_secrets_values_paths),
            valueMappingsFile=self._jsonify_value_mappings(helm_package),
        )

    @staticmethod
    def _find_yaml_files(directory: Path) -> Iterator[Path]:
        """
        Find all yaml files recursively in given directory.

        :param directory: The directory to search.
        """
        yield from directory.glob("**/*.yaml")
        yield from directory.glob("**/*.yml")

    def _find_image_parameter_from_chart(
        self, helm_package_config: HelmPackageConfig
    ) -> List[ImageInfo]:
        """
        Find pattern matches in Helm chart for the names of the image parameters.

        :param helm_package: The helm package config.

        Returns list of tuples containing the list of image
        paths and the name and version of the image. e.g. (Values.foo.bar.repoPath, foo,
        1.2.3)
        """
        assert self._tmp_dir
        chart_dir = self._tmp_dir / helm_package_config.name
        matches = []
        path = []

        for file in self._find_yaml_files(chart_dir):
            with open(file, "r", encoding="UTF-8") as f:
                logger.debug("Searching for %s in %s", IMAGE_START_STRING, file)
                for line in f:
                    if IMAGE_START_STRING in line:
                        logger.debug("Found %s in %s", IMAGE_START_STRING, line)
                        path = re.findall(IMAGE_PATH_REGEX, line)

                        # If "image:", search for chart name and version
                        name_and_version = re.search(IMAGE_NAME_AND_VERSION_REGEX, line)
                        logger.debug(
                            "Regex match for name and version is %s",
                            name_and_version,
                        )

                        if name_and_version and len(name_and_version.groups()) == 2:
                            logger.debug(
                                "Found image name and version %s %s",
                                name_and_version.group("name"),
                                name_and_version.group("version"),
                            )
                            matches.append(
                                ImageInfo(
                                    path,
                                    name_and_version.group("name"),
                                    name_and_version.group("version"),
                                )
                            )
                        else:
                            logger.debug("No image name and version found")
        return matches

    def _find_image_pull_secrets_parameter_from_chart(
        self, helm_package_config: HelmPackageConfig
    ) -> List[str]:
        """
        Find pattern matches in Helm chart for the ImagePullSecrets parameter.

        :param helm_package: The helm package config.

        Returns list of lists containing image pull
        secrets paths, e.g. Values.foo.bar.imagePullSecret
        """
        assert self._tmp_dir
        chart_dir = self._tmp_dir / helm_package_config.name
        matches = []
        path = []

        for file in self._find_yaml_files(chart_dir):
            with open(file, "r", encoding="UTF-8") as f:
                logger.debug(
                    "Searching for %s in %s", IMAGE_PULL_SECRETS_START_STRING, file
                )
                for line in f:
                    if IMAGE_PULL_SECRETS_START_STRING in line:
                        logger.debug(
                            "Found %s in %s", IMAGE_PULL_SECRETS_START_STRING, line
                        )
                        path = re.findall(IMAGE_PATH_REGEX, line)
                        matches += path
        return matches

    def _get_artifact_list(
        self,
        helm_package: HelmPackageConfig,
        image_line_matches: List[ImageInfo],
    ) -> List[Artifact]:
        """
        Get the list of artifacts for the chart.

        :param helm_package: The helm package config.
        :param image_line_matches: The list of image line matches.
        """
        artifact_list = []
        (name, version) = self._get_chart_name_and_version(helm_package)
        helm_artifact = Artifact(name, version)

        artifact_list.append(helm_artifact)
        for image_info in image_line_matches:
            artifact_list.append(Artifact(image_info.name, image_info.version))

        return artifact_list

    def _get_chart_mapping_schema(
        self, helm_package: HelmPackageConfig
    ) -> Dict[Any, Any]:
        """
        Get the schema for the non default values (those with {deploymentParameter...}).
        Based on the user provided values schema.

        param helm_package: The helm package config.
        """
        assert self._tmp_dir
        logger.debug("Get chart mapping schema for %s", helm_package.name)

        mappings_path = helm_package.path_to_mappings
        values_schema = self._tmp_dir / helm_package.name / CNF_VALUES_SCHEMA_FILENAME
        if not Path(mappings_path).exists():
            raise InvalidTemplateError(
                f"ERROR: The helm package '{helm_package.name}' does not have a valid values"
                " mappings file. The file at '{helm_package.path_to_mappings}' does not exist."
                "\nPlease fix this and run the command again."
            )
        if not values_schema.exists():
            raise InvalidTemplateError(
                f"ERROR: The helm package '{helm_package.name}' is missing {CNF_VALUES_SCHEMA_FILENAME}."
                "\nPlease fix this and run the command again."
            )

        with open(mappings_path, "r", encoding="utf-8") as stream:
            values_data = yaml.load(stream, Loader=yaml.SafeLoader)

        with open(values_schema, "r", encoding="utf-8") as f:
            schema_data = json.load(f)

        try:
            deploy_params_dict = self.traverse_dict(
                values_data, DEPLOYMENT_PARAMETER_MAPPING_REGEX
            )
            logger.debug("Deploy params dict is %s", deploy_params_dict)
            new_schema = self.search_schema(deploy_params_dict, schema_data)
        except KeyError as e:
            raise InvalidTemplateError(
                "ERROR: There is a problem with your schema or values for the helm"
                f" package '{helm_package.name}'."
                "\nPlease fix this and run the command again."
            ) from e

        logger.debug("Generated chart mapping schema for %s", helm_package.name)
        return new_schema

    @staticmethod
    def traverse_dict(
        dict_to_search: Dict[Any, Any], target_regex: str
    ) -> Dict[str, List[str]]:
        """
        Traverse the dictionary provided and return a dictionary of all the values that match the target regex,
        with the key being the deploy parameter and the value being the path (as a list) to the value.
        e.g. {"foo": ["global", "foo", "bar"]}

        :param d: The dictionary to traverse.
        :param target: The regex to search for.
        """

        #  pylint: disable=too-many-nested-blocks
        @dataclass
        class DictNode:
            # The dictionary under this node
            sub_dict: Dict[Any, Any]

            # The path to this node under the main dictionary
            position_path: List[str]

        # Initialize the stack with the dictionary and an empty path
        stack: List[DictNode] = [DictNode(dict_to_search, [])]
        result = {}  # Initialize empty dictionary to store the results
        while stack:  # While there are still items in the stack
            # Pop the last item from the stack and unpack it into node (the dictionary) and path
            node = stack.pop()

            # For each key-value pair in the popped item
            for key, value in node.sub_dict.items():
                # If the value is a dictionary
                if isinstance(value, dict):
                    # Add the dictionary to the stack with the path
                    stack.append(DictNode(value, node.position_path + [key]))

                # If the value is a string + matches target regex
                elif isinstance(value, str):
                    # Take the match i.e, foo from {deployParameter.foo}
                    match = re.search(target_regex, value)

                    # Add it to the result dictionary with its path as the value
                    if match:
                        result[match.group(1)] = node.position_path + [key]

                elif isinstance(value, list):
                    logger.debug("Found a list %s", value)
                    for item in value:
                        logger.debug("Found an item %s", item)

                        if isinstance(item, str):
                            match = re.search(target_regex, item)

                            if match:
                                result[match.group(1)] = node.position_path + [key]

                        elif isinstance(item, dict):
                            stack.append(DictNode(item, node.position_path + [key]))

                        elif isinstance(item, list):
                            # We should fix this but for now just log a warning and
                            # carry on
                            logger.warning(
                                "Values mapping file contains a list of lists "
                                "at path %s, which this tool cannot parse. "
                                "Please check the output configMappings and schemas "
                                "files and check that they are as required.",
                                node.position_path + [key],
                            )
        return result

    @staticmethod
    def search_schema(
        deployParams_paths: Dict[str, List[str]], full_schema
    ) -> Dict[str, Dict[str, str]]:
        """
        Search through the provided schema for the types of the deployment parameters.
        This assumes that the type of the key will be the type of the deployment parameter.
        e.g. if foo: {deployParameter.bar} and foo is type string, then bar is type string.

        Returns a dictionary of the deployment parameters in the format:
        {"foo": {"type": "string"}, "bar": {"type": "string"}}

        param deployParams_paths: a dictionary of all the deploy parameters to search for,
                      with the key being the deploy parameter and the value being the
                      path to the value.
                      e.g. {"foo": ["global", "foo", "bar"]}
        param full_schema: The schema to search through.
        """
        new_schema = {}
        no_schema_list = []
        for deploy_param, path_list in deployParams_paths.items():
            logger.debug(
                "Searching for %s in schema at path %s", deploy_param, path_list
            )
            node = full_schema
            for path in path_list:
                if "properties" in node.keys():
                    logger.debug(
                        "Searching properties for %s in schema at path %s",
                        deploy_param,
                        path,
                    )
                    node = node["properties"][path]
                else:
                    logger.debug("No schema node found for %s", deploy_param)
                    no_schema_list.append(deploy_param)
                    new_schema.update({deploy_param: {"type": "string"}})
            if deploy_param not in new_schema:
                param_type = node.get("type", None)
                if param_type == "array":
                    # If the type is an array, we need to get the type of the items.
                    # (This currently only supports a single type, not a list of types.
                    #  If a list is provided, we default to string.)
                    array_item_schema = node.get("items", {})
                    if isinstance(array_item_schema, dict):
                        param_type = array_item_schema.get("type", None)
                    else:
                        logger.debug("Array item schema is not a dict (probably a list)")
                        param_type = None
                if not param_type:
                    logger.debug("No type found for %s", deploy_param)
                    no_schema_list.append(deploy_param)
                    param_type = "string"
                new_schema.update({deploy_param: {"type": param_type}})
        if no_schema_list:
            logger.warning(
                "No schema or type found for deployment parameter(s): %s", no_schema_list
            )
            logger.warning(
                "We default these parameters to type string. "
                "Please edit schemas/%s in the output before publishing "
                "if this is wrong",
                DEPLOYMENT_PARAMETERS_FILENAME,
            )
        return new_schema

    def _replace_values_with_deploy_params(
        self,
        values_yaml_dict,
        param_prefix: Optional[str] = None,
    ) -> Dict[Any, Any]:
        """
        Given the yaml dictionary read from values.yaml, replace all the values with {deploymentParameter.keyname}.

        Thus creating a values mapping file if the user has not provided one in config.
        """
        logger.debug("Replacing values with deploy parameters")
        final_values_mapping_dict: Dict[Any, Any] = {}
        for k, v in values_yaml_dict.items():  # pylint: disable=too-many-nested-blocks
            # if value is a string and contains deployParameters.
            logger.debug("Processing key %s", k)
            param_name = k if param_prefix is None else f"{param_prefix}_{k}"
            if isinstance(v, dict):
                final_values_mapping_dict[k] = self._replace_values_with_deploy_params(
                    v, param_name
                )
            elif isinstance(v, list):
                final_values_mapping_dict[k] = []
                for index, item in enumerate(v):
                    param_name = (
                        f"{param_prefix}_{k}_{index}"
                        if param_prefix
                        else f"{k}_{index}"
                    )
                    if isinstance(item, dict):
                        final_values_mapping_dict[k].append(
                            self._replace_values_with_deploy_params(item, param_name)
                        )
                    elif isinstance(item, (str, int, bool)) or not item:
                        if self.interactive:
                            if not input_ack(
                                "y", f"Expose parameter {param_name}? y/n "
                            ):
                                logger.debug("Excluding parameter %s", param_name)
                                final_values_mapping_dict[k].append(item)
                                continue
                        replacement_value = f"{{deployParameters.{param_name}}}"
                        final_values_mapping_dict[k].append(replacement_value)
                    else:
                        raise ValueError(
                            f"Found an unexpected type {type(item)} of key {k} in "
                            "values.yaml, cannot generate values mapping file."
                        )
            elif isinstance(v, (str, int, bool)) or not v:
                # Replace the parameter with {deploymentParameter.keyname}
                # If v is blank we don't know what type it is. Assuming it is an
                # empty string (but do this after checking for dict and list)
                if self.interactive:
                    # Interactive mode. Prompt user to include or exclude parameters
                    # This requires the enter key after the y/n input which isn't ideal
                    if not input_ack("y", f"Expose parameter {param_name}? y/n "):
                        logger.debug("Excluding parameter %s", param_name)
                        final_values_mapping_dict.update({k: v})
                        continue
                replacement_value = f"{{deployParameters.{param_name}}}"

                # add the schema for k (from the big schema) to the (smaller) schema
                final_values_mapping_dict.update({k: replacement_value})
            else:
                raise ValueError(
                    f"Found an unexpected type {type(v)} of key {k} in values.yaml, "
                    "cannot generate values mapping file."
                )

        return final_values_mapping_dict

    def _get_chart_name_and_version(
        self, helm_package: HelmPackageConfig
    ) -> Tuple[str, str]:
        """Get the name and version of the chart."""
        assert self._tmp_dir
        chart_path = self._tmp_dir / helm_package.name / "Chart.yaml"

        if not chart_path.exists():
            raise InvalidTemplateError(
                f"There is no Chart.yaml file in the helm package '{helm_package.name}'. "
                "\nPlease fix this and run the command again."
            )

        with open(chart_path, "r", encoding="utf-8") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            if "name" in data and "version" in data:
                chart_name = data["name"]
                chart_version = data["version"]
            else:
                raise FileOperationError(
                    "A name or version is missing from Chart.yaml in the helm package"
                    f" '{helm_package.name}'."
                    "\nPlease fix this and run the command again."
                )

        return (chart_name, chart_version)

    def _jsonify_value_mappings(self, helm_package: HelmPackageConfig) -> str:
        """Yaml->JSON values mapping file, then return the filename."""
        assert self._tmp_dir
        mappings_yaml_file = helm_package.path_to_mappings
        mappings_dir = self._tmp_dir / CONFIG_MAPPINGS_DIR_NAME
        mappings_output_file = mappings_dir / f"{helm_package.name}-mappings.json"

        mappings_dir.mkdir(exist_ok=True)

        with open(mappings_yaml_file, "r", encoding="utf-8") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        with open(mappings_output_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        logger.debug("Generated parameter mappings for %s", helm_package.name)
        return f"{helm_package.name}-mappings.json"
