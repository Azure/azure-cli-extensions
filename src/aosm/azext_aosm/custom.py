# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from dataclasses import asdict
from typing import Optional, Tuple
from azext_aosm.generate_nfd.cnf_nfd_generator import CnfNfdGenerator
from azext_aosm.generate_nfd.nfd_generator_base import NFDGenerator
from azext_aosm.generate_nfd.vnf_nfd_generator import VnfNfdGenerator
from knack.log import get_logger
from azure.cli.core.azclierror import AzCLIError
from azure.mgmt.resource import ResourceManagementClient
from .vendored_sdks import HybridNetworkManagementClient
from .vendored_sdks.models import Publisher, NetworkFunctionDefinitionVersion
from ._client_factory import cf_resources
from ._configuration import Configuration, VNFConfiguration, get_configuration
from ._constants import VNF, CNF, NSD


logger = get_logger(__name__)

PUBLISHER_RESOURCE_TYPE = "Microsoft.HybridNetwork/publishers"
ARTIFACT_STORE_RESOURCE_TYPE = "Microsoft.HybridNetwork/publishers/artifactstores"
NFDG_RESOURCE_TYPE = "Microsoft.HybridNetwork/publishers/networkfunctiondefinitiongroups"
NSDG_RESOURCE_TYPE = "Microsoft.HybridNetwork/publishers/networkservicedesigngroups"

def _required_resources_exist(
    cli_ctx, definition_type: str, config: Configuration
) -> bool:
    resource_client = cf_resources(cli_ctx)

    if resource_client.check_existence(
        config.publisher_resource_group_name,
        PUBLISHER_RESOURCE_TYPE,
        config.publisher_name,
    ):
        if not resource_client.check_existence(
            config.publisher_resource_group_name,
            "Microsoft.HybridNetwork/publishers/artifactstores",
            config.acr_artifact_store_name,
        ):
            return False
        if definition_type == VNF:
            if not resource_client.check_existence(
                config.publisher_resource_group_name,
                NFDG_RESOURCE_TYPE,
                config.name,
            ):
                return False
        elif definition_type == NSD:
            if not resource_client.check_existence(
                config.publisher_resource_group_name,
                NSDG_RESOURCE_TYPE,
                config.name,
            ):
                return False
        elif definition_type == CNF:
            if not resource_client.check_existence(
                config.publisher_resource_group_name,
                NFDG_RESOURCE_TYPE,
                config.name,
            ):
                return False
        else:
            raise AzCLIError(
                "Invalid definition type. Valid values are vnf, nsd and cnf."
            )
    else:
        return False

def _create_required_resources(definition_type, config):
    pass

def build_definition(
    cmd,
    client: HybridNetworkManagementClient,
    definition_type,
    config_file,
    publish=False,
):
    with open(config_file, "r", encoding="utf-8") as f:
        config_as_dict = json.loads(f)

    config = get_configuration(definition_type, config_as_dict)

    # Generate the NFD/NSD and the artifact manifest.


    # Write the ARM/bicep template if that's what we are doing

    # Publish the definition if publish is true
    if publish:
        if not _required_resources_exist(cmd.cli_ctx, definition_type, config):
            _create_required_resources(definition_type, config)


def generate_definition_config(cmd, definition_type, output_file="input.json"):
    config = get_configuration(definition_type)
    config_as_dict = json.dumps(asdict(config), indent=4)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(config_as_dict)
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
        nfd_generator = VnfNfdGenerator(config)
    elif definition_type == CNF:
        nfd_generator = CnfNfdGenerator(config)
        
    nfd_generator.generate_nfd()
