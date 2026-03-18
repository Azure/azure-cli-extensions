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
from azext_aosm.common.constants import (
    VALID_VNF_TEMPLATE_RESOURCE_TYPES
)
from azure.cli.core.azclierror import InvalidTemplateError

logger = get_logger(__name__)


class ArmTemplateInput(BaseInput):
    """
    A utility class for working with ARM template inputs.

    :param artifact_name: The name of the artifact.
    :type artifact_name: str
    :param artifact_version: The version of the artifact.
    :type artifact_version: str
    :param template_path: The path to the ARM template file.
    :type template_path: Path
    :param default_config: The default configuration.
    :type default_config: Optional[Dict[str, Any]]
    """

    def __init__(
        self,
        artifact_name: str,
        artifact_version: str,
        template_path: Path,
        default_config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(artifact_name, artifact_version, default_config)
        self.template_path = template_path

    def get_defaults(self) -> Dict[str, Any]:
        """
        Gets the default values for configuring the input.

        :return: A dictionary containing the default values.
        :rtype: Dict[str, Any]
        """
        logger.info("Getting default values for ARM template input")
        default_config = {}
        with open(self.template_path, "r", encoding="utf-8") as _file:
            data = json.load(_file)

        if "parameters" in data:
            default_config = self._generate_defaults_from_arm_params(data["parameters"])
        else:
            logger.warning(
                "No parameters found in the template provided. "
                "Your NFD will have no deployParameters"
            )

        # Add any default config to the defaults dictionary
        default_config.update(self.default_config)
        logger.debug(
            "Default values for ARM template input: %s",
            json.dumps(default_config, indent=4),
        )
        return copy.deepcopy(default_config)

    def get_schema(self) -> Dict[str, Any]:
        """
        Gets the schema for the ARM template input.

        :return: A dictionary containing the schema.
        :rtype: Dict[str, Any]
        """
        logger.debug("Getting schema for ARM template input %s.", self.artifact_name)
        arm_template_schema = copy.deepcopy(BASE_SCHEMA)
        with open(self.template_path, "r", encoding="utf-8") as _file:
            data = json.load(_file)

        if "parameters" in data:
            self._generate_schema_from_arm_params(arm_template_schema, data["parameters"])
        else:
            logger.warning(
                "No parameters found in the template provided. "
                "Your NFD will have no deployParameters"
            )
        logger.debug(
            "Schema for ARM template input: %s",
            json.dumps(arm_template_schema, indent=4),
        )

        return copy.deepcopy(arm_template_schema)

    def _generate_schema_from_arm_params(
        self, schema: Dict[str, Any], parameters: Dict[str, Any]
    ) -> None:
        """
        Generates the schema from the parameters.

        :param schema: The schema to generate.
        :type schema: Dict[str, Any]
        :param parameters: The parameters to generate the schema from.
        :type parameters: Dict[str, Any]
        """
        logger.debug("Generating schema from parameters")
        for key, value in parameters.items():
            if "defaultValue" not in value:
                schema["required"].append(key)
            if value["type"] in ("object", "secureObject"):
                schema["properties"][key] = {
                    "type": "object",
                    "properties": {},
                    "required": [],
                }
                if "properties" in value:
                    self._generate_schema_from_arm_params(
                        schema["properties"][key], value["properties"]
                    )
            else:
                schema["properties"][key] = {"type": value["type"]}
                if "defaultValue" in value:
                    schema["properties"][key]["default"] = value["defaultValue"]

    def _generate_defaults_from_arm_params(self, parameters):
        defaults_dict = {}
        for param_name, param_details in parameters.items():
            default_value = param_details.get('defaultValue')
            if default_value is not None:
                defaults_dict[param_name] = default_value

        return defaults_dict

    def validate_resource_types(self):
        with open(Path(self.template_path).absolute()) as f:
            data = json.load(f)
            arm_resource_types = [resource['type'] for resource in data['resources']]
            for resource_type in arm_resource_types:
                resource_type_prefix = resource_type.split('/')[0] if '/' in resource_type else resource_type
                if resource_type_prefix not in VALID_VNF_TEMPLATE_RESOURCE_TYPES:
                    raise InvalidTemplateError(
                        f"ERROR: The resource type '{resource_type_prefix}' "
                        " used in the ARM template is not valid. "
                        f" Valid types are: {', '.join(VALID_VNF_TEMPLATE_RESOURCE_TYPES)}")
