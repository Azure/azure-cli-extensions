# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
from pathlib import Path
from typing import Any, Dict, List

from knack.log import get_logger
from azure.mgmt.resource.resources.models import ResourceGroup
from azext_aosm.common.command_context import CommandContext
from azext_aosm.configuration_models.common_parameters_config import (
    BaseCommonParametersConfig,
)
from azext_aosm.definition_folder.reader.artifact_definition import (
    ArtifactDefinitionElement,
)
from azext_aosm.definition_folder.reader.base_definition import BaseDefinitionElement
from azext_aosm.definition_folder.reader.bicep_definition import BicepDefinitionElement

logger = get_logger(__name__)


class DefinitionFolder:
    """Represents a definition folder for an NFD or NSD."""

    def __init__(self, path: Path):
        self.path = path
        try:
            index = self._parse_index_file((path / "index.json").read_text())
        except Exception as e:
            raise ValueError(f"Error parsing index file - {e}")
        self.elements: List[BaseDefinitionElement] = []
        for element in index:
            if element["type"] == "bicep":
                self.elements.append(
                    BicepDefinitionElement(
                        element["path"], element["only_delete_on_clean"]
                    )
                )
            elif element["type"] == "artifact":
                self.elements.append(
                    ArtifactDefinitionElement(
                        element["path"], element["only_delete_on_clean"]
                    )
                )

    def _parse_index_file(self, file_content: str) -> List[Dict[str, Any]]:
        """Read the index file. Return a list of dicts containing path, type, only_delete_on_clean"""
        json_content = json.loads(file_content)
        parsed_elements = []
        for element in json_content:
            if "name" not in element:
                raise ValueError("Index file element is missing name")
            if "type" not in element:
                raise ValueError(
                    f"Index file element {element['name']} is missing type"
                )
            if "only_delete_on_clean" not in element:
                element["only_delete_on_clean"] = False
            elif not isinstance(element["only_delete_on_clean"], bool):
                raise ValueError(
                    f"Index file element {element['name']} only_delete_on_clean should be a boolean"
                )
            parsed_elements.append(
                {
                    "path": self.path / element["name"],
                    "type": element["type"],
                    "only_delete_on_clean": element["only_delete_on_clean"],
                }
            )
        return parsed_elements

    def _create_or_confirm_existence_of_resource_group(self, config, command_context):
        """Ensure resource group exists before deploying of elements begins.

        Using ResourceManagementClient:
        - Check for existence of resource group specified in allDeployParameters.json.
        - Create resource group if doesn't exist.
        """
        resources_client = command_context.resources_client
        if not resources_client.resource_groups.check_existence(config.publisherResourceGroupName):
            rg_params = ResourceGroup(location=config.location)
            resources_client.resource_groups.create_or_update(
                resource_group_name=config.publisherResourceGroupName,
                parameters=rg_params
            )

    def deploy(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ):
        """Deploy the resources defined in the folder."""
        self._create_or_confirm_existence_of_resource_group(config, command_context)
        for element in self.elements:
            logger.info(
                "Deploying definition element %s of type %s",
                element.path,
                type(element),
            )
            element.deploy(config=config, command_context=command_context)

    def delete(
        self,
        config: BaseCommonParametersConfig,
        command_context: CommandContext,
        clean: bool = False,
    ):
        """Delete the definition folder."""
        for element in reversed(self.elements):
            if clean or not element.only_delete_on_clean:
                element.delete(config=config, command_context=command_context)
