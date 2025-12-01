# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

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
    :param input_artifact: The input artifact.
    """

    def __init__(self, name: str, input_artifact: BaseInput, expose_all_params: bool):
        self.name = name
        self.input_artifact = input_artifact
        self.expose_all_params = expose_all_params

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

    def generate_schema(self) -> Dict[str, Any]:
        """
        Generate the schema for values the user must provide.

        :return: A dictionary containing the schema.
        :rtype: Dict[str, Any]
        """
        logger.info(
            "Generating parameter schema for %s with expose_all_params set to %s",
            self.name,
            self.expose_all_params,
        )

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

    # pylint:disable=unused-argument
    def _set_expose_boolean(self, **kwargs) -> bool:
        return self.expose_all_params

    def _generate_schema(
        self,
        deploy_params_schema: Dict[str, Any],
        source_schema: Dict[str, Any],
        default_values: Dict[str, Any],
        param_prefix: Optional[str] = None,
    ) -> None:
        """
        Generate the JSON schema for deployParameters. The NFDProcessor overrides this method to generate CGS for NSDs.

        This method recursively generates the deployParameters schema for the input artifact by updating
        the schema parameter.

        Note there is no return value. The schema is passed by reference and modified in place.

        Parameters:
            deploy_params_schema:
                The schema to be modified. On first call of this method,
                it should contain any base nodes for the schema.
                This schema is passed by reference and modified in place.
                This property is defined by the CLI in the base processor.
            source_schema:
                The source schema from which the deploy parameters schema is generated.
                E.g., for a Helm chart this may be the schema generated from the values.yaml file.
                For an ARM template this will be the schema generated from the template's parameters
            default_values:
                The default values used to determine whether a parameter should be hardcoded or provided by the user.
                Defined by the input artifact classes from the config provided by the user.
                E.g. for helm charts this can be the default values file or the values.yaml file in the chart.
            param_prefix:
                The prefix to be added to the parameter name.
                This is used for namespacing nested properties in the schema.
                On first call to this method this should be None.
        """
        if "properties" not in source_schema.keys():
            return

        # Abbreviated 'prop' because 'property' is built in.
        for prop, details in source_schema["properties"].items():

            # Abbreviated 'prop' because 'property' is built in.
            param_name = prop if not param_prefix else f"{param_prefix}_{prop}"

            # Set EXPOSE conditions
            expose_boolean = self._set_expose_boolean(prop=prop, defaults=default_values)

            # 1. Required parameters (in 'required' array and no default given).
            # Add parameter to properties and required in schema
            if (
                (prop not in default_values or default_values[prop] is None)
                and "required" in source_schema
                and prop in source_schema["required"]
            ):
                deploy_params_schema["required"].append(param_name)
                deploy_params_schema["properties"][param_name] = details

            # 2. Parameters that have child properties, check their children
            elif "properties" in details:
                self._generate_schema(
                    deploy_params_schema,
                    details,
                    default_values=default_values[prop],
                    param_prefix=param_name,
                )
            # 3. All other parameters (including arrays)
            # Note: We don't recurse into arrays for simplicity
            # This means we don't get defaults for items and nested arrays don't have properties
            else:
                if expose_boolean:
                    # AOSM RP wants null as a string, bug raised
                    if prop in default_values and default_values[prop] is None:
                        default_values[prop] = "null"
                        # Add value to default in schema
                    if prop in default_values:
                        details["default"] = default_values[prop]
                    # If there is a default of '[resourceGroup().location]'
                    # which is not allowed to be passed into CGVs
                    if "default" in details and details["default"] == '[resourceGroup().location]':
                        # Remove the default
                        del details["default"]
                        # Make the parameter required (to expose in CGVS without a default)
                        deploy_params_schema["required"].append(param_name)
                    deploy_params_schema["properties"][param_name] = details

    def generate_values_mappings(
        self,
        schema: Dict[str, Any],
        defaults: Dict[str, Any],
        is_ret: bool = False,
        param_prefix: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generates a mapping from user-provided values to the parameters of the input artifact.

        The mapping also allows for values to be "hardcoded", i.e., the value is provided in the dictionary, not as
        a reference to a deployParameter / CGV.

        This method iterates over the properties in the provided schema. For each property, it checks if it's a
        required parameter or optional, and if it has child properties. Based on these checks, it generates a
        mapping for the parameter:

            - If a parameter is required and not present in the initial mappings, it adds a mapping for it.
              The user must provide this value.
            - If optional, the existing hardcoded value will be left in place (but see next point about
              expose_boolean) and the user can't set this value.
            - If expose_boolean is set, it generates mappings for all optional parameters. If the user doesn't
              provide this value, AOSM will use the default value from the corresponding deployParameters schema.
            - If the parameter has child properties, it recursively generates mappings (if necessary) for them.

        The mapping is returned as a dictionary where the keys are the parameter names and the values are either
        hardcoded values or references to user-provided values.

        Parameters:
            schema:  The schema defining the user inputs from which the mapping will be generated.
            mapping: Initially a dictionary of hardcoded default values. Any parameters required by the schema that are
                     not present in the mapping dictionary will be added (recursively) as a mapping to the user input.
            is_ret:  Whether the mapping is for a resource element template (RET).
        """
        mappings: Dict[str, Any] = {}

        if "properties" not in schema.keys():
            return mappings
        for prop, prop_schema in schema["properties"].items():

            # Error handling for oneOf, anyOf which AOSM doesn't allow
            if isinstance(prop_schema, dict) and "type" not in prop_schema:
                if "oneOf" in prop_schema or "anyOf" in prop_schema:
                    raise InvalidArgumentValueError(
                        f"The subschema '{prop}' does not contain a type.\n"
                        "It contains 'anyOf' or 'oneOf' logic, which is not supported by AOSM.\n"
                        "Please remove this from your values.schema.json and provide a concrete type "
                        "or remove the schema and the CLI will generate a schema from your values.yaml file."
                    )
                raise InvalidArgumentValueError(
                    f"The subschema {prop} does not contain a type. This is a required field.\n"
                    "Please fix your values.schema.json or remove the schema and the CLI will generate a "
                    "schema from your values.yaml file."
                )

            param_name = prop if param_prefix is None else f"{param_prefix}_{prop}"

            # Set EXPOSE conditions
            expose_boolean = self._set_expose_boolean(prop=prop, defaults=defaults)

            # 1. Parameters that have child properties, check their children
            if "properties" in prop_schema:
                mappings[prop] = self.generate_values_mappings(
                    prop_schema, defaults[prop], is_ret, param_name
                )
            # 2. Required parameters (in 'required' array and no default given).
            # These will have no values so must be exposed
            # We ignore any comments about hard-coding because there are no values
            elif (
                (prop not in defaults or defaults[prop] is None)
                and "required" in schema
                and prop in schema["required"]
            ):
                mappings[prop] = self._generate_mapping_string(param_name, is_ret)
            # 3. All other parameters (including arrays)
            else:
                if expose_boolean:
                    mappings[prop] = self._generate_mapping_string(param_name, is_ret)
                # Note: need this condition to ignore optional parameters that have no defaults
                elif prop in defaults:
                    mappings[prop] = defaults[prop]

        logger.debug(
            "Output of generate_values_mappings for %s:\n%s",
            self.name,
            json.dumps(mappings, indent=4),
        )

        return mappings

    def _generate_mapping_string(self, param_name: str, is_ret: bool) -> str:
        """
        Generate the mapping string based on the parameter name and the is_ret flag.

        Args:
            param_name (str): The name of the parameter.
            is_ret (bool): A flag indicating whether to use the return format.

        Returns:
            str: The generated mapping string.
        """
        return (
            f"{{configurationparameters('{CGS_NAME}').{self.name}.{param_name}}}"
            if is_ret
            else f"{{deployParameters.{self.name}.{param_name}}}"
        )
