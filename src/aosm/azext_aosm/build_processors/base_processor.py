# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

from knack.log import get_logger
from azure.cli.core.azclierror import InvalidArgumentValueError
from azext_aosm.common.artifact import BaseArtifact
from azext_aosm.common.constants import CGS_NAME
from azext_aosm.definition_folder.builder.local_file_builder import LocalFileBuilder
from azext_aosm.inputs.base_input import BaseInput
from azext_aosm.vendored_sdks.models import (
    ManifestArtifactFormat,
    NetworkFunctionApplication,
    ResourceElementTemplate,
)

logger = get_logger(__name__)


class BaseInputProcessor(ABC):
    """
    A base class for input processors.

    :param name: The name of the artifact.
    :type name: str
    :param input_artifact: The input artifact.
    :type input_artifact: BaseInput
    """

    def __init__(self, name: str, input_artifact: BaseInput):
        self.name = name
        self.input_artifact = input_artifact

    @abstractmethod
    def get_artifact_manifest_list(self) -> List[ManifestArtifactFormat]:
        """
        Get the list of artifacts for the artifact manifest.

        :return: A list of artifacts for the artifact manifest.
        :rtype: List[ManifestArtifactFormat]
        """
        raise NotImplementedError

    @abstractmethod
    def get_artifact_details(self) -> Tuple[List[BaseArtifact], List[LocalFileBuilder]]:
        """
        Get the artifact details for publishing.

        :return: A tuple containing the list of artifacts and the list of local file builders.
        :rtype: Tuple[List[BaseArtifact], List[LocalFileBuilder]]
        """
        raise NotImplementedError

    @abstractmethod
    def generate_nf_application(self) -> NetworkFunctionApplication:
        """
        Generate the network function application from the input.

        :return: The network function application.
        :rtype: NetworkFunctionApplication
        """
        raise NotImplementedError

    @abstractmethod
    def generate_resource_element_template(self) -> ResourceElementTemplate:
        """
        Generate the resource element template from the input.

        :return: The resource element template.
        :rtype: ResourceElementTemplate
        """
        raise NotImplementedError

    def generate_params_schema(self) -> Dict[str, Any]:
        """
        Generate the parameter schema for configuring the input.

        :return: A dictionary containing the parameter schema.
        :rtype: Dict[str, Any]
        """
        logger.info("Generating parameter schema for %s", self.name)

        base_params_schema = """
        {
            "%s": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
        """ % (
            self.name
        )

        params_schema = json.loads(base_params_schema)

        self._generate_schema(
            params_schema[self.name],
            self.input_artifact.get_schema(),
            self.input_artifact.get_defaults(),
        )

        # If there are no properties, return an empty dict as we don't need
        # a schema for this input artifact.
        if not bool(params_schema[self.name]["properties"]):
            params_schema = {}

        logger.debug(
            "Parameter schema for %s: %s",
            self.name,
            json.dumps(params_schema, indent=4),
        )

        return params_schema

    def _generate_schema(
        self,
        schema: Dict[str, Any],
        source_schema: Dict[str, Any],
        values: Dict[str, Any],
    ) -> None:
        """
        Generate the parameter schema

        This function recursively generates the parameter schema for the input artifact by updating
        the schema parameter.

        :param schema: The schema to generate.
        :type schema: Dict[str, Any]
        :param source_schema: The source schema.
        :type source_schema: Dict[str, Any]
        :param values: The values to generate the schema from.
        :type values: Dict[str, Any]
        """
        if "properties" not in source_schema.keys():
            return

        # Loop through each property in the schema.
        for k, v in source_schema["properties"].items():
            # If the property is not in the values, and is required, add it to the values.
            if (
                "required" in source_schema
                and k not in values
                and k in source_schema["required"]
            ):
                if v["type"] == "object":
                    print(f"Resolving object {k} for schema")
                    self._generate_schema(schema, v, {})
                else:
                    schema["required"].append(k)
                    schema["properties"][k] = v
            # If the property is in the values, and is an object, generate the values mappings
            # for the subschema.
            if k in values and v["type"] == "object" and values[k]:
                self._generate_schema(schema, v, values[k])

    def generate_values_mappings(
        self,
        schema: Dict[str, Any],
        values: Dict[str, Any],
        is_ret: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate the values mappings for the input artifact.

        This function recursively generates the values mappings for the input artifact by updating
        the values parameter.

        :param schema: The schema to generate the values mappings from.
        :type schema: Dict[str, Any]
        :param values: The values to generate the values mappings from.
        :type values: Dict[str, Any]
        :param is_ret: Whether or not the input artifact is being used to generate a resource element template.
        :type is_ret: bool
        """
        # If there are no properties in the schema for the object, return the values.
        if "properties" not in schema.keys():
            return values

        # Loop through each property in the schema.
        for subschema_name, subschema in schema["properties"].items():

            if "type" not in subschema:
                if ["oneOf", "anyOf"] in subschema:
                    raise InvalidArgumentValueError(
                        f"The subschema '{subschema_name}' does not contain a type.\n"
                        "It contains 'anyOf' or 'oneOf' logic, which is not valid for AOSM.\n"
                        "Please remove this from your values.schema.json and provide a concrete type "
                        "or remove the schema and the CLI will generate a generic schema."
                    )
                raise InvalidArgumentValueError(
                    f"The subschema {subschema_name} does not contain a type. This is a required field.\n"
                    "Please fix your values.schema.json or remove the schema and the CLI will generate a "
                    "generic schema."
                )
            # If the property is not in the values, and is required, add it to the values.
            if (
                "required" in schema
                and subschema_name not in values
                and subschema_name in schema["required"]
            ):
                print(f"Adding {subschema_name} to values")
                if subschema["type"] == "object":
                    values[subschema_name] = self.generate_values_mappings(
                        subschema, {}, is_ret
                    )
                else:
                    values[subschema_name] = (
                        f"{{configurationparameters('{CGS_NAME}').{self.name}.{subschema_name}}}"
                        if is_ret
                        else f"{{deployParameters.{self.name}.{subschema_name}}}"
                    )
            # If the property is in the values, and is an object, generate the values mappings
            # for the subschema.
            if subschema_name in values and subschema["type"] == "object":
                # Python evaluates {} as False, so we need to explicitly set to {}
                default_subschema_values = values[subschema_name] or {}
                values[subschema_name] = self.generate_values_mappings(
                    subschema, default_subschema_values, is_ret
                )

        logger.debug(
            "Output of generate_values_mappings for %s: %s",
            self.name,
            json.dumps(values, indent=4),
        )

        return values
