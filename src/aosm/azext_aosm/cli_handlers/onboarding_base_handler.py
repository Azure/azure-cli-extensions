# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Optional
from azure.cli.core.azclierror import UnclassifiedUserFault
from jinja2 import StrictUndefined, Template
from knack.log import get_logger

from azext_aosm.configuration_models.onboarding_base_input_config import (
    OnboardingBaseInputConfig,
)
from azext_aosm.definition_folder.builder.definition_folder_builder import (
    DefinitionFolderBuilder,
)
from azext_aosm.definition_folder.reader.definition_folder import DefinitionFolder
from azext_aosm.common.command_context import CommandContext
from azext_aosm.configuration_models.common_parameters_config import (
    BaseCommonParametersConfig,
)
from azext_aosm.common.local_file_builder import LocalFileBuilder
from azext_aosm.vendored_sdks import HybridNetworkManagementClient
from azext_aosm.common.constants import DEPLOYMENT_PARAMETERS_FILENAME

logger = get_logger(__name__)


class OnboardingBaseCLIHandler(ABC):
    """Abstract base class for CLI handlers."""

    def __init__(
        self,
        provided_input_path: Optional[Path] = None,
        aosm_client: Optional[HybridNetworkManagementClient] = None,
        skip: str = None,
    ):
        """Initialize the CLI handler."""
        self.aosm_client = aosm_client
        self.skip = skip
        # If config file provided (for build, publish and delete)
        if provided_input_path:
            provided_input_path = Path(provided_input_path)
            # If config file is the input.jsonc for build command
            if provided_input_path.suffix == ".jsonc":
                config_dict = self._read_input_config_from_file(provided_input_path)
                self.config = self._get_input_config(config_dict)
                # Validate config before getting processor list,
                # in case error with input artifacts i.e helm package
                self.config.validate()
                self.processors = self._get_processor_list()
            # If config file is the all parameters json file for publish/delete
            elif provided_input_path.suffix == ".json":
                self.config = self._get_params_config(provided_input_path)
            else:
                raise UnclassifiedUserFault("Invalid input")
                # TODO: Change this to work with publish?
        # If no config file provided (for generate-config)
        else:
            self.config = self._get_input_config()
        self.definition_folder_builder = DefinitionFolderBuilder(
            Path.cwd() / self.output_folder_file_name
        )

    @property
    @abstractmethod
    def default_config_file_name(self) -> str:
        """Get the default configuration file name."""
        raise NotImplementedError

    @property
    @abstractmethod
    def output_folder_file_name(self) -> str:
        """Get the output folder file name."""
        raise NotImplementedError

    def generate_config(self, output_file: str | None = None):
        """Generate the configuration file for the command."""
        if not output_file:
            output_file = self.default_config_file_name

        # Make Path object and ensure it has .jsonc extension
        output_path = Path(output_file).with_suffix(".jsonc")

        self._check_for_overwrite(output_path)
        self._write_config_to_file(output_path)

    def build(self):
        """Build the definition."""
        self.pre_validate_build()
        self.definition_folder_builder.add_element(self.build_base_bicep())
        self.definition_folder_builder.add_element(self.build_manifest_bicep())
        self.definition_folder_builder.add_element(self.build_artifact_list())
        self.definition_folder_builder.add_element(self.build_resource_bicep())
        self.definition_folder_builder.add_element(self.build_all_parameters_json())
        self.definition_folder_builder.write()

    def publish(self, command_context: CommandContext):
        """Publish the definition contained in the specified definition folder."""
        definition_folder = DefinitionFolder(
            command_context.cli_options["definition_folder"]
        )
        definition_folder.deploy(config=self.config, command_context=command_context)

    def delete(self, command_context: CommandContext):
        """Delete the definition."""
        # Takes folder, deletes to Azure
        #  - Read folder/ create folder object
        #  - For each element (reversed):
        #    - Do element.delete()
        # TODO: Implement

    def pre_validate_build(self):
        """Perform all validations that need to be done before running the build command."""
        pass

    @abstractmethod
    def build_base_bicep(self):
        """Build bicep file for underlying resources."""
        raise NotImplementedError

    @abstractmethod
    def build_manifest_bicep(self):
        """Build the manifest bicep file."""
        raise NotImplementedError

    @abstractmethod
    def build_artifact_list(self):
        """Build the artifact list."""
        raise NotImplementedError

    @abstractmethod
    def build_resource_bicep(self):
        """Build the resource bicep file."""
        raise NotImplementedError

    @abstractmethod
    def build_all_parameters_json(self):
        """Build parameters file to be used to create parameters.json for each bicep template."""
        raise NotImplementedError

    @abstractmethod
    def _get_processor_list(self):
        """Get list of processors for use in build."""
        raise NotImplementedError

    @abstractmethod
    def _get_input_config(self, input_config: dict = None) -> OnboardingBaseInputConfig:
        """Get the configuration for the command."""
        raise NotImplementedError

    @abstractmethod
    def _get_params_config(
        self, config_file: Path = None
    ) -> BaseCommonParametersConfig:
        """Get the parameters config for publish/delete."""
        raise NotImplementedError

    def _read_input_config_from_file(self, input_json_path: Path) -> dict:
        """Reads the input JSONC file, removes comments.

        Returns config as dictionary.
        """
        lines = input_json_path.read_text().splitlines()
        lines = [line for line in lines if not line.strip().startswith("//")]
        config_dict = json.loads("".join(lines))

        return config_dict

    def _render_base_bicep_contents(self, template_path):
        """Write the base bicep file from given template."""
        with open(template_path, "r", encoding="UTF-8") as f:
            template: Template = Template(
                f.read(),
                undefined=StrictUndefined,
            )

        bicep_contents: str = template.render()
        return bicep_contents

    def _render_definition_bicep_contents(self, template_path: Path, params):
        """Write the definition bicep file from given template."""
        with open(template_path, "r", encoding="UTF-8") as f:
            template: Template = Template(
                f.read(),
                undefined=StrictUndefined,
            )

        bicep_contents: str = template.render(params)
        return bicep_contents

    def _render_manifest_bicep_contents(
        self,
        template_path: Path,
        acr_artifact_list: list,
        sa_artifact_list: list = None,
    ):
        """Write the manifest bicep file from given template.

        Returns bicep content as string
        """
        with open(template_path, "r", encoding="UTF-8") as f:
            template: Template = Template(
                f.read(),
                undefined=StrictUndefined,
            )

        bicep_contents: str = template.render(
            acr_artifacts=acr_artifact_list, sa_artifacts=sa_artifact_list
        )
        return bicep_contents

    def _get_template_path(self, definition_type: str, template_name: str) -> Path:
        """Get the path to a template."""
        return (
            Path(__file__).parent.parent
            / "common"
            / "templates"
            / definition_type
            / template_name
        )

    def _serialize(self, dataclass, indent_count=1):
        """
        Convert a dataclass instance to a JSONC string.

        This function recursively iterates over the fields of the dataclass and serializes them.

        We expect the dataclass to contain values of type string, list or another dataclass.
        Lists may only contain dataclasses.
        For example,
        {
            "param1": "value1",
            "param2": [
                { ... },
                { ... }
            ],
            "param3": { ... }
        }
        """
        indent = "    " * indent_count
        double_indent = indent * 2
        jsonc_string = []

        for field_info in fields(dataclass):
            # Get the value of the current field.
            field_value = getattr(dataclass, field_info.name)
            # Get comment, if it exists + add it to the result
            comment = field_info.metadata.get("comment", "")
            if comment:
                for line in comment.split("\n"):
                    jsonc_string.append(f"{indent}// {line}")

            if is_dataclass(field_value):
                # Serialize the nested dataclass and add it as a nested JSON object.
                # Checks if it is last field to omit trailing comma
                if field_info == fields(dataclass)[-1]:
                    nested_json = (
                        "{\n"
                        + self._serialize(field_value, indent_count + 1)
                        + "\n"
                        + indent
                        + "}"
                    )
                else:
                    nested_json = (
                        "{\n"
                        + self._serialize(field_value, indent_count + 1)
                        + "\n"
                        + indent
                        + "},"
                    )
                jsonc_string.append(f'{indent}"{field_info.name}": {nested_json}')
            elif isinstance(field_value, list):
                # If the value is a list, iterate over the items.
                jsonc_string.append(f'{indent}"{field_info.name}": [')
                for item in field_value:
                    # Check if the item is a dataclass and serialize it.
                    if is_dataclass(item):
                        inner_dataclass = self._serialize(item, indent_count + 2)
                        if item == field_value[-1]:
                            jsonc_string.append(
                                double_indent
                                + "{\n"
                                + inner_dataclass
                                + "\n"
                                + double_indent
                                + "}"
                            )
                        else:
                            jsonc_string.append(
                                double_indent
                                + "{\n"
                                + inner_dataclass
                                + "\n"
                                + double_indent
                                + "},"
                            )
                    else:
                        jsonc_string.append(json.dumps(item, indent=4) + ",")
                # If the field is the last field, omit the trailing comma.
                if field_info == fields(dataclass)[-1]:
                    jsonc_string.append(indent + "]")
                else:
                    jsonc_string.append(indent + "],")
            else:
                # If the value is a string, serialize it directly.
                if field_info == fields(dataclass)[-1]:
                    jsonc_string.append(
                        f'{indent}"{field_info.name}": {json.dumps(field_value,indent=4)}'
                    )
                else:
                    jsonc_string.append(
                        f'{indent}"{field_info.name}": {json.dumps(field_value,indent=4)},'
                    )
        return "\n".join(jsonc_string)

    def _write_config_to_file(self, output_path: Path):
        """Write the configuration to a file."""
        # Serialize the top-level dataclass instance and wrap it in curly braces to form a valid JSONC string.
        jsonc_str = "{\n" + self._serialize(self.config) + "\n}"
        output_path.write_text(jsonc_str)

        print(f"Empty configuration has been written to {output_path.name}")
        logger.info("Empty  configuration has been written to %s", output_path.name)

    def _check_for_overwrite(self, output_path: Path):
        """Check that the input file exists."""
        if output_path.exists():
            carry_on = input(
                f"The file {output_path.name} already exists in this location - do you want to overwrite it?"
                " (y/n)"
            )
            if carry_on != "y":
                raise UnclassifiedUserFault("User aborted!")

    def _render_deployment_params_schema(
        self, complete_params_schema, output_folder_name, definition_folder_name
    ):
        """Render the schema for deployParameters.json."""
        return LocalFileBuilder(
            Path(
                output_folder_name,
                definition_folder_name,
                DEPLOYMENT_PARAMETERS_FILENAME,
            ),
            json.dumps(
                self._build_deploy_params_schema(complete_params_schema), indent=4
            ),
        )

    def _build_deploy_params_schema(self, schema_properties):
        """Build the schema for deployParameters.json."""
        schema_contents = {
            "$schema": "https://json-schema.org/draft-07/schema#",
            "title": "DeployParametersSchema",
            "type": "object",
            "properties": {},
        }
        schema_contents["properties"] = schema_properties
        return schema_contents
