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
            param_name = prop if not param_prefix else f"{param_prefix}_{prop}"

            # Note: We don't recurse into arrays. For arrays we just dump all the `details` as is.
            # This is because arrays are 'tricky'. This approach may need to be revisited at some point.

            # We have three types of parameter to handle in the following if statements:
            # 1. Required parameters (in 'required' array and no default given).
            if (
                prop not in default_values
                and "required" in source_schema
                and prop in source_schema["required"]
            ):
                # Note: we only recurse into objects, not arrays. For now, this is sufficient.
                if "properties" in details:
                    self._generate_schema(
                        deploy_params_schema,
                        details,
                        default_values={},  # In this branch property_key is not in defaults, so pass empty dict.
                        param_prefix=param_name,
                    )
                else:
                    deploy_params_schema["required"].append(param_name)
                    deploy_params_schema["properties"][param_name] = details
            # 2. Optional parameters that have child properties. These aren't added to the schema here (default
            # behaviour), but we check their children.
            elif prop in default_values and "properties" in details:
                self._generate_schema(
                    deploy_params_schema, details, default_values[prop], param_name
                )
            # 3. Other optional parameters. By default these are excluded from the schema to minimise the number of
            # parameters the user needs to deal with in the schemas, but expose_all_params means we include them.
            elif self.expose_all_params:
                if "properties" in details:
                    # default_values is an empty dict. If there were defaults, elif #2 would have caught them
                    self._generate_schema(
                        deploy_params_schema,
                        details,
                        default_values={},
                        param_prefix=param_name,
                    )
                else:
                    if prop in default_values:
                        # AOSM wants null as a string
                        # TODO: Flag with RP that this is a bug?
                        if default_values[prop] is None:
                            default_values[prop] = "null"
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
        mapping: Dict[str, Any],
        is_ret: bool = False,
        param_prefix: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generates a mapping from user-provided values to the parameters of an ARM template.

        The mapping also allows for values to be "hardcoded", i.e., the value is provided in the dictionary, not as
        a reference to a deployParameter / CGV.

        This method iterates over the properties in the provided schema. For each property, it checks if it's a
        required parameter or optional, and if it has child properties. Based on these checks, it generates a
        mapping for the parameter:

            - If a parameter is required and not present in the initial mappings, it adds a mapping for it.
              The user must provide this value.
            - If optional, the existing hardcoded value will be left in place (but see next point about
              expose_all_params) and the user can't set this value.
            - If expose_all_params is set, it generates mappings for all optional parameters. If the user doesn't
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
        if "properties" not in schema.keys():
            return mapping
        for prop, prop_schema in schema["properties"].items():
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
            # We have three types of parameter to handle in the following if statements (analagous to
            # generate_schema()):
            # 1. Required parameters (in 'required' array and no default given).
            if (
                "required" in schema
                and prop in schema["required"]
                and prop not in mapping
            ):
                if "properties" in prop_schema:
                    mapping[prop] = self.generate_values_mappings(
                        prop_schema, {}, is_ret, param_name
                    )
                else:
                    mapping[prop] = (
                        f"{{configurationparameters('{CGS_NAME}').{self.name}.{param_name}}}"
                        if is_ret
                        else f"{{deployParameters.{self.name}.{param_name}}}"
                    )
            # 2. Optional parameters (i.e. they have a default in the mapping dict) that have child properties.
            #    These aren't added to the mapping here, but we check their children.
            elif prop in mapping and "properties" in prop_schema:
                # Python evaluates {} as False, so we need to explicitly set to {}
                prop_mapping = mapping[prop] or {}
                mapping[prop] = self.generate_values_mappings(
                    prop_schema, prop_mapping, is_ret, param_name
                )
            # 3. Other optional parameters. By default these are hardcoded in the mapping to minimise the number of
            #    parameters the user needs to deal with, but expose_all_params means we map them from the user
            #    provided values.
            elif self.expose_all_params:
                if "properties" in prop_schema:
                    # Mapping is an empty dict.
                    # If there were defaults in the mapping dict, the elif above would have caught them
                    mapping[prop] = self.generate_values_mappings(
                        prop_schema, {}, is_ret, param_name
                    )
                else:
                    mapping[prop] = (
                        f"{{configurationparameters('{CGS_NAME}').{self.name}.{param_name}}}"
                        if is_ret
                        else f"{{deployParameters.{self.name}.{param_name}}}"
                    )

        logger.debug(
            "Output of generate_values_mappings for %s:\n%s",
            self.name,
            json.dumps(mapping, indent=4),
        )

        return mapping
