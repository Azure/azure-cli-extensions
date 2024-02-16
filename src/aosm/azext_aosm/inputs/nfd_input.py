# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import copy
import json
from pathlib import Path
from typing import Any, Dict, Optional

from knack.log import get_logger

from azext_aosm.common.constants import BASE_SCHEMA
from azext_aosm.inputs.base_input import BaseInput
from azext_aosm.vendored_sdks.models import NetworkFunctionDefinitionVersion

logger = get_logger(__name__)


class NFDInput(BaseInput):
    """
    A utility class for working with Network Function Definition inputs.

    :param artifact_name: The name of the artifact.
    :type artifact_name: str
    :param artifact_version: The version of the artifact.
    :type artifact_version: str
    :param network_function_definition: The network function definition.
    :type network_function_definition: NetworkFunctionDefinitionVersion
    :param arm_template_output_path: The path to the ARM template output.
    :type arm_template_output_path: Path
    :param default_config: The default configuration.
    :type default_config: Optional[Dict[str, Any]]
    """

    def __init__(
        self,
        artifact_name: str,
        artifact_version: str,
        network_function_definition: NetworkFunctionDefinitionVersion,
        arm_template_output_path: Path,
        default_config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(artifact_name, artifact_version, default_config)
        self.network_function_definition = network_function_definition
        self.arm_template_output_path = arm_template_output_path

    def get_defaults(self) -> Dict[str, Any]:
        """
        Gets the default values for configuring the input.

        :return: A dictionary containing the default values.
        :rtype: Dict[str, Any]
        """
        if self.network_function_definition.id:
            logger.debug(
                "network_function_definition.id for NFD input: %s",
                self.network_function_definition.id,
            )
            split_id = self.network_function_definition.id.split("/")
            publisher_name: str = split_id[8]
            nfdg_name: str = split_id[10]
            publisher_resource_group: str = split_id[4]

        logger.info("Getting default values for NFD Input")

        base_defaults = {
            "configObject": {
                "location": self.default_config["location"],
                "publisherName": publisher_name,
                "nfdgName": nfdg_name,
                "publisherResourceGroup": publisher_resource_group,
            }
        }

        if self.network_function_definition.properties and (
          self.network_function_definition.properties.network_function_template.nfvi_type
          not in ("AzureArcKubernetes","AzureOperatorNexus")
        ):
            base_defaults["configObject"]["customLocationId"] = ""

        logger.debug(
            "Default values for NFD Input: %s", json.dumps(base_defaults, indent=4)
        )

        return copy.deepcopy(base_defaults)

    def get_schema(self) -> Dict[str, Any]:
        """
        Gets the parameter schema for configuring the input.

        :return: A dictionary containing the schema.
        :rtype: Dict[str, Any]
        :raises ValueError: If no deployment parameters schema is found on the network function definition version.
        """
        logger.debug("Getting schema for NFD Input %s.", self.artifact_name)
        schema_properties = {
            "configObject": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "publisherName": {"type": "string"},
                    "nfdgName": {"type": "string"},
                    "nfdvName": {"type": "string"},
                    "publisherResourceGroup": {"type": "string"},
                    "deploymentParameters": {
                        "type": "array",
                        "items": {"type": "object"},
                    },
                    "customLocationId": {"type": "string"},
                    "managedIdentityId": {"type": "string"},
                },
                "required": [
                    "location",
                    "publisherName",
                    "nfdgName",
                    "nfdvName",
                    "publisherResourceGroup",
                    "deploymentParameters",
                    "customLocationId",
                    "managedIdentityId",
                ],
            }
        }

        schema_required_properties = ["configObject"]

        schema = copy.deepcopy(BASE_SCHEMA)
        schema["properties"] = schema_properties
        schema["required"] = schema_required_properties

        nfdv_properties = self.network_function_definition.properties

        if nfdv_properties and nfdv_properties.deploy_parameters:
            schema["properties"]["configObject"]["properties"]["deploymentParameters"][
                "items"
            ] = json.loads(nfdv_properties.deploy_parameters)

            logger.debug("Schema for NFD Input: %s", json.dumps(schema, indent=4))

            return copy.deepcopy(schema)

        logger.error(
            "No deployment parameters schema found on the network function definition version."
        )
        raise ValueError(
            "No deployment parameters schema found on the network function definition version."
        )
