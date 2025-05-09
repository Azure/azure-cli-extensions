# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import copy
import json
import shutil
import subprocess
import tempfile
import warnings
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import genson
import ruamel.yaml
import yaml
from knack.log import get_logger
from ruamel.yaml.error import ReusedAnchorWarning

from azext_aosm.common.exceptions import (
    DefaultValuesNotFoundError,
    MissingChartDependencyError,
    SchemaGetOrGenerateError,
    TemplateValidationError,
)
from azext_aosm.common.utils import check_tool_installed, extract_tarfile
# from azext_aosm.common.constants import CNF_VALUES_SCHEMA_FILENAME
from azext_aosm.inputs.base_input import BaseInput

logger = get_logger(__name__)
yaml_processor = ruamel.yaml.YAML(typ="safe", pure=True)
warnings.simplefilter("ignore", ReusedAnchorWarning)


@dataclass
class HelmChartMetadata:
    """
    Represents the metadata of a Helm chart.

    :param name: The name of the Helm chart.
    :type name: str
    :param version: The version of the Helm chart.
    :type version: str
    :param dependencies: The dependencies of the Helm chart.
    :type dependencies: List[str]
    """

    name: str
    version: str
    dependencies: List[str]


@dataclass
class HelmChartTemplate:
    """
    Represents a template in a Helm chart.

    :param name: The name of the template.
    :type name: str
    :param data: The data of the template.
    :type data: List[str]
    """

    name: str
    data: List[str]


class HelmChartInput(BaseInput):
    """
    A utility class for working with Helm chart inputs.

    :param artifact_name: The name of the artifact.
    :type artifact_name: str
    :param artifact_version: The version of the artifact.
    :type artifact_version: str
    :param chart_path: The path to the Helm chart.
    :type chart_path: Path
    :param default_config: The default configuration.
    :type default_config: Optional[Dict[str, Any]]
    :param default_config_path: The path to the default configuration.
    :type default_config_path: Optional[str]
    """

    def __init__(
        self,
        artifact_name: str,
        artifact_version: str,
        chart_path: Path,
        default_config: Optional[Dict[str, Any]] = None,
        default_config_path: Optional[str] = None,
    ):
        super().__init__(artifact_name, artifact_version, default_config)
        self.chart_path = chart_path
        self._temp_dir_path = Path(tempfile.mkdtemp())
        if chart_path.is_dir():
            self._chart_dir = chart_path
        else:
            self._chart_dir = extract_tarfile(chart_path, self._temp_dir_path)
        self._validate()
        self.metadata = self._get_metadata()
        self.helm_template: Optional[str] = None
        self.default_config_path = default_config_path

    @staticmethod
    def from_chart_path(
        chart_path: Path,
        default_config: Optional[Dict[str, Any]] = None,
        default_config_path: Optional[str] = None,
    ) -> "HelmChartInput":
        """
        Creates a HelmChartInput object from a path to a Helm chart.

        :param chart_path: The path to the Helm chart. This should either be a path to a folder or a tar file.
        :type chart_path: Path
        :param default_config: The default configuration.
        :type default_config: Optional[Dict[str, Any]]
        :param default_config_path: The path to the default configuration.
        :type default_config_path: Optional[str]
        :return: A HelmChartInput object.
        :rtype: HelmChartInput
        """
        logger.debug("Creating Helm chart input from chart path '%s'", chart_path)
        temp_dir = Path(tempfile.mkdtemp())
        if not chart_path.exists():
            raise FileNotFoundError(
                f"ERROR: The Helm chart '{chart_path}' does not exist."
            )
        logger.debug("Unpacking Helm chart to %s", temp_dir)
        if chart_path.is_dir():
            unpacked_chart_path = Path(chart_path)
        else:
            unpacked_chart_path = extract_tarfile(chart_path, temp_dir)

        name, version = HelmChartInput._get_name_and_version(unpacked_chart_path)

        shutil.rmtree(temp_dir)

        logger.debug("Deleted temporary directory %s", temp_dir)

        return HelmChartInput(
            artifact_name=name,
            artifact_version=version,
            chart_path=chart_path,
            default_config=default_config,
            default_config_path=default_config_path,
        )

    def validate_template(self) -> None:
        """
        Perform validation on the Helm chart template by running `helm template` command.

        :return: Error message if the `helm template` command fails.
        """
        logger.debug("Performing validation on Helm chart %s.", self.artifact_name)

        check_tool_installed("helm")

        if self.default_config_path:
            cmd: List[Union[str, PathLike]] = [
                "helm",
                "template",
                self.artifact_name,
                self.chart_path,
                "--values",
                self.default_config_path,
            ]
        else:
            cmd = [
                "helm",
                "template",
                self.artifact_name,
                self.chart_path,
            ]

        try:
            result = subprocess.run(cmd, capture_output=True, check=True)
            helm_template_output = result.stdout
            self.helm_template = helm_template_output.decode()

            logger.debug(
                "Helm template output for Helm chart %s:\n%s",
                self.artifact_name,
                helm_template_output,
            )
        except subprocess.CalledProcessError as error:
            # Return the error message without raising an error.
            # The errors are going to be collected into a file by the caller of this function.
            error_message = error.stderr.decode()

            # Remove part of the message of the error. This is because this message will polute
            # the error file. We are not running the helm command with the --debug flag,
            # because during testing this flag did not produce any useful output
            # (the invalid YAML was not printed out). If at a later date we find that this flag
            # does produce a useful output, we can run the helm command with the --debug flag.
            error_message = error_message.replace(
                "\nUse --debug flag to render out invalid YAML", ""
            )
            raise TemplateValidationError(error_message)

    def validate_values(self) -> None:
        """
        Confirm that the default values are provided or that a values.yaml file exists in the
        Helm chart directory.

        :raises DefaultValuesNotFoundError: If the values.yaml and default values do not exist.
        """
        logger.debug("Getting default values for Helm chart %s", self.artifact_name)

        try:
            self.default_config or self._read_values_yaml_from_chart()
        except FileNotFoundError:
            logger.error("No values found for Helm chart '%s'", self.chart_path)
            raise DefaultValuesNotFoundError(
                "ERROR: No default values found for the Helm chart"
                f" '{self.chart_path}'. Please provide default values"
                " or add a values.yaml file to the Helm chart."
            )

    def get_defaults(self) -> Dict[str, Any]:
        """
        Retrieves the default values for the Helm chart.

        :return: The default values for the Helm chart.
        :rtype: Dict[str, Any]
        """
        default_config = self.default_config or self._read_values_yaml_from_chart()
        logger.debug(
            "Default values for Helm chart input: %s",
            json.dumps(default_config, indent=4),
        )
        return copy.deepcopy(default_config)

    def get_schema(self) -> Dict[str, Any]:
        """
        Retrieves the schema for the Helm chart.

        If the Helm chart contains a values.schema.json file, then that file
        will be used as the schema. Otherwise, a schema will be generated from
        the default values in the values.yaml file.

        :return: The schema for the Helm chart.
        :rtype: Dict[str, Any]
        :raises SchemaGetOrGenerateError: If an error occurred while trying to generate or retrieve the schema.
        """
        logger.info("Getting schema for Helm chart input %s.", self.artifact_name)
        try:
            # The following commented out code was used to get the values.schema.json file from the Helm chart, and
            # only generate the schema from values.yaml as a backup. Unfortunately, the values.schema.json file is too
            # flexible, and handling all the many ways it can be written is too complex (at least for now). Instead,
            # we always generate the schema we use from values.yaml / default values.
            # values.schema.yaml is still used by `helm template`, which we call, so if present in the chart, we will
            # check that values.yaml complies with values.schema.yaml. This is still useful functionality.
            # The code is being left commented out in case we want to revisit this in the future.

            # schema = None
            # # Use the schema provided in the chart if there is one.
            # for file in self._chart_dir.iterdir():
            #     if file.name == CNF_VALUES_SCHEMA_FILENAME:
            #         logger.debug("Using schema from chart %s", file)
            #         with file.open(encoding="UTF-8") as schema_file:
            #             schema = json.load(schema_file)

            # if not schema:
            #     # Otherwise, generate a schema from the default values or values in values.yaml.

            # Note the following code that builds the schema from defaults has been unindented after above comments.

            logger.debug("Generating schema from default values")
            built_schema = genson.Schema()
            built_schema.add_object(self.get_defaults())
            schema = built_schema.to_dict()

            logger.debug(
                "Schema for Helm chart input:\n%s",
                json.dumps(schema, indent=4),
            )

            return schema
        except FileNotFoundError as error:
            logger.error("No schema found for Helm chart '%s'", self.chart_path)
            raise SchemaGetOrGenerateError(
                "ERROR: Encountered an error while trying to generate or"
                f" retrieve the helm chart values schema:\n{error}"
            ) from error

    def get_dependencies(self) -> List["HelmChartInput"]:
        """
        Get the dependency charts for the Helm chart.

        :return: The dependency charts for the Helm chart.
        :rtype: List[HelmChartInput]
        :raises MissingChartDependencyError: If a dependency chart is missing.
        """
        logger.debug(
            "Getting dependency charts for Helm chart input, '%s'", self.artifact_name
        )
        # All dependency charts should be located in the charts directory.
        dependency_chart_dir = Path(self._chart_dir, "charts")

        if not dependency_chart_dir.exists():
            # If there is no charts directory, then there are no dependencies.
            logger.debug("No dependency charts found for Helm chart input")
            assert len(self.metadata.dependencies) == 0
            return []

        # For each chart in the charts directory, create a HelmChartInput object.
        dependency_charts = [
            HelmChartInput.from_chart_path(Path(chart_dir), None)
            for chart_dir in dependency_chart_dir.iterdir()
        ]

        # Check that the charts found in the charts directory match the
        # all the dependency names defined in Chart.yaml.
        for dependency in self.metadata.dependencies:
            if dependency not in [
                dependency_chart.metadata.name for dependency_chart in dependency_charts
            ]:
                logger.error(
                    "Missing dependency chart '%s' for Helm chart '%s'",
                    dependency,
                    self.chart_path,
                )
                raise MissingChartDependencyError(
                    f"ERROR: The Helm chart '{self.metadata.name}' has a"
                    f"dependency on the chart '{dependency}' which is not"
                    "a local dependency."
                )

        return dependency_charts

    def get_templates(self) -> List[HelmChartTemplate]:
        """
        Get the templates for the Helm chart.

        :return: The templates for the Helm chart.
        :rtype: List[HelmChartTemplate]
        """
        logger.debug("Getting templates for Helm chart input %s", self.artifact_name)

        # Template files are located in the templates directory.
        template_dir = Path(self._chart_dir, "templates")
        templates: List[HelmChartTemplate] = []

        if not template_dir.exists():
            logger.debug("No templates found for Helm chart input")
            return templates

        for file in template_dir.iterdir():
            # Template files are only ever YAML files.
            if file.name.endswith(".yaml"):
                with file.open(encoding="UTF-8") as template_file:
                    template_data = template_file.readlines()

                templates.append(HelmChartTemplate(name=file.name, data=template_data))

        return templates

    @staticmethod
    def _get_name_and_version(chart_dir: Path) -> Tuple[str, str]:
        """
        Retrieves the name and version of the Helm chart.

        :param chart_dir: The path to the Helm chart directory.
        :type chart_dir: Path
        :return: The name and version of the Helm chart.
        :rtype: Tuple[str, str]
        """
        logger.debug("Getting name and version for Helm chart")
        chart_yaml_path = Path(chart_dir, "Chart.yaml")

        with chart_yaml_path.open(encoding="UTF-8") as chart_yaml_file:
            chart_yaml = yaml.safe_load(chart_yaml_file)

        chart_name = chart_yaml["name"]
        chart_version = chart_yaml["version"]

        logger.debug("Chart name: %s", chart_name)
        logger.debug("Chart version: %s", chart_version)

        return chart_name, chart_version

    def _validate(self) -> None:
        """
        Validates the Helm chart by checking if the Chart.yaml file exists.

        :raises FileNotFoundError: If the Chart.yaml file does not exist.
        """
        if not Path(self._chart_dir, "Chart.yaml").exists():
            logger.error(
                "Chart.yaml file not found in Helm chart '%s'", self.chart_path
            )
            raise FileNotFoundError(
                f"ERROR: The Helm chart '{self.chart_path}' does not contain"
                "a Chart.yaml file."
            )

    def _get_metadata(self) -> HelmChartMetadata:
        """
        Retrieves the metadata of the Helm chart.

        :return: The metadata of the Helm chart.
        :rtype: HelmChartMetadata
        """
        logger.debug("Getting metadata for Helm chart input")
        # The metadata is stored in the Chart.yaml file.
        chart_yaml_path = Path(self._chart_dir, "Chart.yaml")

        with chart_yaml_path.open(encoding="UTF-8") as chart_yaml_file:
            chart_yaml = yaml.safe_load(chart_yaml_file)

        # We only need the name of the dependency charts.
        dependencies = [
            dependency["name"] for dependency in chart_yaml.get("dependencies", [])
        ]

        return HelmChartMetadata(
            name=chart_yaml["name"],
            version=chart_yaml["version"],
            dependencies=dependencies,
        )

    def _read_values_yaml_from_chart(self) -> Dict[str, Any]:
        """
        Reads the values.yaml file in the Helm chart directory.

        :return: The contents of the values.yaml file.
        :rtype: Dict[str, Any]
        :raises FileNotFoundError: If the values.yaml file does not exist.
        """
        logger.debug("Reading values.yaml file")
        for file in self._chart_dir.iterdir():
            if file.name.endswith(("values.yaml", "values.yml")):
                with file.open(encoding="UTF-8") as f:
                    content = yaml_processor.load(f)
                return content

        logger.error(
            "values.yaml|yml file not found in Helm chart '%s'", self.chart_path
        )
        raise FileNotFoundError(
            f"ERROR: The Helm chart '{self.chart_path}' does not contain"
            "a values.yaml file."
        )

    def __del__(self):
        shutil.rmtree(self._temp_dir_path)
