# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from dataclasses import asdict
from knack.log import get_logger

from azext_aosm.generate_nfd.cnf_nfd_generator import CnfNfdGenerator
from azext_aosm.generate_nfd.nfd_generator_base import NFDGenerator
from azext_aosm.generate_nfd.vnf_bicep_nfd_generator import VnfBicepNfdGenerator
from azext_aosm.deploy.deploy_with_arm import DeployerViaArm
from azext_aosm._constants import VNF, CNF, NSD
from azext_aosm.util.management_clients import ApiClientsAndCaches
from .vendored_sdks import HybridNetworkManagementClient
from ._client_factory import cf_resources
from ._configuration import (
    get_configuration,
    validate_configuration,
)


logger = get_logger(__name__)


def build_definition(
    cmd,
    client: HybridNetworkManagementClient,
    definition_type,
    config_file,
    publish=False,
):
    """Build and optionally publish a definition

    :param cmd: _description_
    :type cmd: _type_
    :param client: _description_
    :type client: HybridNetworkManagementClient
    :param definition_type: _description_
    :type definition_type: _type_
    :param config_file: _description_
    :type config_file: _type_
    :param publish: _description_, defaults to False
    :type publish: bool, optional
    """
    with open(config_file, "r", encoding="utf-8") as f:
        config_as_dict = json.loads(f.read())

    apiClientsAndCaches = ApiClientsAndCaches(
        aosm_client=client, resource_client=cf_resources(cmd.cli_ctx)
    )

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
            deployer = DeployerViaArm(apiClientsAndCaches, config=config)
            deployer.deploy_vnfd_from_bicep()
        else:
            print("TODO - cannot publish CNF or NSD yet.")


def generate_definition_config(definition_type, output_file="input.json"):
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
    """
    _summary_

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
    clean=False,
):
    with open(config_file, "r", encoding="utf-8") as f:
        config_as_dict = json.loads(f.read())
    config = get_configuration(definition_type, config_as_dict)
    validate_configuration(config)

    api_clients = ApiClientsAndCaches(
        aosm_client=client, resource_client=cf_resources(cmd.cli_ctx)
    )
    from azext_aosm.delete.delete import ResourceDeleter

    delly = ResourceDeleter(api_clients, config)
    if definition_type == VNF:
        delly.delete_vnf(all=clean)


def show_publisher():
    pass
