# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Handles the creation of a resource element template for a network function."""

import json

from typing import Dict, Any, List, Union
from knack.log import get_logger

from azext_aosm._configuration import NFDRETConfiguration
from azext_aosm.util.constants import CNF, VNF
from azext_aosm.util.management_clients import ApiClients
from azext_aosm.vendored_sdks.models import NetworkFunctionDefinitionVersion, NFVIType


logger = get_logger(__name__)


class NFRETGenerator:
    """Represents a single network function resource element template within an NSD."""

    def __init__(
        self, api_clients: ApiClients, config: NFDRETConfiguration, cg_schema_name: str
    ) -> None:
        self.config = config
        self.cg_schema_name = cg_schema_name
        nfdv = self._get_nfdv(config, api_clients)
        print(
            f"Finding the deploy parameters for {self.config.name}:{self.config.version}"
        )

        if not nfdv.properties.deploy_parameters:
            raise NotImplementedError(
                f"NFDV {self.config.name} has no deploy parameters, cannot generate NSD."
            )
        self.deploy_parameters: Dict[str, Any] = json.loads(
            nfdv.properties.deploy_parameters
        )

        self.nfd_group_name = self.config.name.replace("-", "_")
        self.nfdv_parameter_name = f"{self.nfd_group_name}_nfd_version"
        self.config_mapping_filename = f"{self.config.name}_config_mapping.json"

    @staticmethod
    def _get_nfdv(
        config: NFDRETConfiguration, api_clients: ApiClients
    ) -> NetworkFunctionDefinitionVersion:
        """Get the existing NFDV resource object."""
        print(
            f"Reading existing NFDV resource object {config.version} from group {config.name}"
        )
        nfdv_object = api_clients.aosm_client.network_function_definition_versions.get(
            resource_group_name=config.publisher_resource_group,
            publisher_name=config.publisher,
            network_function_definition_group_name=config.name,
            network_function_definition_version_name=config.version,
        )
        return nfdv_object

    @property
    def config_mappings(self) -> Dict[str, Any]:
        """
        Return the contents of the config mapping file for this RET.

                Output will look something like:
        {
            "deploymentParametersObject": {
                "deploymentParameters": [
                    "{configurationparameters('foo_ConfigGroupSchema').bar.deploymentParameters}"
                ]
            },
            "nginx_nfdg_nfd_version": "{configurationparameters('foo_ConfigGroupSchema').bar.bar_nfd_version}",
            "managedIdentity": "{configurationparameters('foo_ConfigGroupSchema').managedIdentity}",
            "customLocationId": "{configurationparameters('foo_ConfigGroupSchema').bar.customLocationId}"
        }
        """
        nf = self.config.name

        logger.debug("Create %s", self.config_mapping_filename)

        deployment_parameters: Union[
            str, List[str]
        ] = f"{{configurationparameters('{self.cg_schema_name}').{nf}.deploymentParameters}}"

        if not self.config.multiple_instances:
            assert isinstance(deployment_parameters, str)
            deployment_parameters = [deployment_parameters]

        deployment_parameters_object = {"deploymentParameters": deployment_parameters}

        version_parameter = (
            f"{{configurationparameters('{self.cg_schema_name}')."
            f"{nf}.{self.nfdv_parameter_name}}}"
        )

        config_mappings = {
            "deploymentParametersObject": deployment_parameters_object,
            self.nfdv_parameter_name: version_parameter,
            "managedIdentity": f"{{configurationparameters('{self.cg_schema_name}').managedIdentity}}",
        }

        if self.config.type == CNF:
            config_mappings[
                "customLocationId"
            ] = f"{{configurationparameters('{self.cg_schema_name}').{nf}.customLocationId}}"

        return config_mappings

    @property
    def nf_bicep_substitutions(self) -> Dict[str, Any]:
        """Returns the jinja2 parameters for the NF bicep template template."""
        return {
            "network_function_name": self.config.name,
            "publisher_name": self.config.publisher,
            "publisher_resource_group": self.config.publisher_resource_group,
            "network_function_definition_group_name": (self.config.name),
            "network_function_definition_version_parameter": (self.nfdv_parameter_name),
            "network_function_definition_offering_location": (
                self.config.publisher_offering_location
            ),
            # Ideally we would use the network_function_type from reading the actual
            # NF, as we do for deployParameters, but the SDK currently doesn't
            # support this and needs to be rebuilt to do so.
            "nfvi_type": (
                NFVIType.AZURE_CORE.value  # type: ignore[attr-defined] # pylint: disable=no-member
                if self.config.type == VNF
                else NFVIType.AZURE_ARC_KUBERNETES.value  # type: ignore[attr-defined] # pylint: disable=no-member
            ),
            "CNF": self.config.type == CNF,
        }

    @property
    def config_schema_snippet(self) -> Dict[str, Any]:
        """Return the CGS snippet for this NF."""
        nfdv_version_description_string = (
            f"The version of the {self.config.name} "
            "NFD to use.  This version must be compatible with (have the same "
            "parameters exposed as) "
            f"{self.config.name}."
        )

        if self.config.multiple_instances:
            deploy_parameters = {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": self.deploy_parameters["properties"],
                },
            }
        else:
            deploy_parameters = {
                "type": "object",
                "properties": self.deploy_parameters["properties"],
            }

        nf_schema: Dict[str, Any] = {
            "type": "object",
            "properties": {
                "deploymentParameters": deploy_parameters,
                self.nfdv_parameter_name: {
                    "type": "string",
                    "description": nfdv_version_description_string,
                },
            },
            "required": ["deploymentParameters", self.nfdv_parameter_name],
        }

        if self.config.type == CNF:
            custom_location_description_string = (
                "The custom location ID of the ARC-Enabled AKS Cluster to deploy the CNF "
                "to. Should be of the form "
                "'/subscriptions/{subscriptionId}/resourcegroups"
                "/{resourceGroupName}/providers/microsoft.extendedlocation/"
                "customlocations/{customLocationName}'"
            )

            nf_schema["properties"]["customLocationId"] = {
                "type": "string",
                "description": custom_location_description_string,
            }
            nf_schema["required"].append("customLocationId")

        return nf_schema
