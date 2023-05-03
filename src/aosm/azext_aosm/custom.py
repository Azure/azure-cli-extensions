# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from dataclasses import asdict
from typing import Optional, Tuple
from knack.log import get_logger
from azure.cli.core.azclierror import AzCLIError
from azure.mgmt.resource import ResourceManagementClient

from azext_aosm.generate_nfd.cnf_nfd_generator import CnfNfdGenerator
from azext_aosm.generate_nfd.nfd_generator_base import NFDGenerator
from azext_aosm.generate_nfd.vnf_bicep_nfd_generator import VnfBicepNfdGenerator

from .vendored_sdks import HybridNetworkManagementClient
from .vendored_sdks.models import Publisher, NetworkFunctionDefinitionVersion
from ._client_factory import cf_resources
from ._configuration import (
    Configuration,
    VNFConfiguration,
    get_configuration,
    validate_configuration,
)
from azext_aosm.deploy.deploy_with_arm import DeployerViaArm
from azext_aosm._constants import VNF, CNF, NSD
from azext_aosm.util.management_clients import ApiClientsAndCaches



logger = get_logger(__name__)

PUBLISHER_RESOURCE_TYPE = "Microsoft.HybridNetwork/publishers"
ARTIFACT_STORE_RESOURCE_TYPE = "Microsoft.HybridNetwork/publishers/artifactstores"
NFDG_RESOURCE_TYPE = (
    "Microsoft.HybridNetwork/publishers/networkfunctiondefinitiongroups"
)
NSDG_RESOURCE_TYPE = "Microsoft.HybridNetwork/publishers/networkservicedesigngroups"


def build_definition(
    cmd,
    client: HybridNetworkManagementClient,
    definition_type,
    config_file,
    publish=False,
):
    with open(config_file, "r", encoding="utf-8") as f:
        config_as_dict = json.loads(f.read())

    apiClientsAndCaches = ApiClientsAndCaches(aosm_client=client,
                                              resource_client=cf_resources(cmd.cli_ctx))

    # TODO - this isn't deserializing the config properly - any sub-objects are left
    # as a dictionary instead of being converted to the object (e.g. ArtifactConfig)
    # se we have to reference them as dictionary values
    config = get_configuration(definition_type, config_as_dict)
    validate_configuration(config)
    # Generate the NFD/NSD and the artifact manifest.
    _generate_nfd(definition_type=definition_type, config=config)
    # Write the ARM/bicep template if that's what we are doing

    # Publish the definition if publish is true
    if publish:
        if definition_type == VNF:
            deployer = DeployerViaArm(apiClientsAndCaches,
                                      config=config)
            output = deployer.deploy_vnfd_from_bicep()
        else:
            print("TODO - cannot publish CNF or NSD yet.")


def generate_definition_config(cmd, definition_type, output_file="input.json"):
    config = get_configuration(definition_type)
    config_as_dict = json.dumps(asdict(config), indent=4)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(config_as_dict)
        print(
            "Empty definition configuration has been written to %s",
            output_file,
        )
        logger.info(
            "Empty definition configuration has been written to %s",
            output_file,
        )


def _generate_nfd(definition_type, config):
    """_summary_

    :param definition_type: _description_
    :type definition_type: _type_
    """
    nfd_generator: NFDGenerator
    if definition_type == VNF:
        nfd_generator = VnfBicepNfdGenerator(config)
    elif definition_type == CNF:
        nfd_generator = CnfNfdGenerator(config)
    else:
        from azure.cli.core.azclierror import CLIInternalError

        raise CLIInternalError(
            "Generate NFD called for unrecognised definition_type. Only VNF and CNF have been implemented."
        )

    nfd_generator.generate_nfd()
    
def delete_published_definition(
    cmd,
    client: HybridNetworkManagementClient,
    definition_type,
    config_file,
    all=False,
):
    with open(config_file, "r", encoding="utf-8") as f:
        config_as_dict = json.loads(f.read())
    config = get_configuration(definition_type, config_as_dict)
    validate_configuration(config)

    api_clients = ApiClientsAndCaches(aosm_client=client,
                                              resource_client=cf_resources(cmd.cli_ctx))
    from azext_aosm.delete.delete import ResourceDeleter
    delly = ResourceDeleter(api_clients, config)
    if definition_type == VNF:
        delly.delete_vnf(all)

def show_publisher():
    pass
