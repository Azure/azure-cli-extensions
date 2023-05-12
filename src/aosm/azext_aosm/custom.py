# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from dataclasses import asdict
from typing import Optional
from knack.log import get_logger

from azext_aosm.generate_nfd.cnf_nfd_generator import CnfNfdGenerator
from azext_aosm.generate_nfd.nfd_generator_base import NFDGenerator
from azext_aosm.generate_nfd.vnf_bicep_nfd_generator import VnfBicepNfdGenerator
from azext_aosm.delete.delete import ResourceDeleter
from azext_aosm.deploy.deploy_with_arm import DeployerViaArm
from azext_aosm.util.constants import VNF, CNF  # , NSD
from azext_aosm.util.management_clients import ApiClients
from azext_aosm.vendored_sdks import HybridNetworkManagementClient
from azext_aosm._client_factory import cf_resources
from azext_aosm._configuration import (
    get_configuration,
    NFConfiguration,
)


logger = get_logger(__name__)


def build_definition(
    cmd,
    client: HybridNetworkManagementClient,
    definition_type: str,
    config_file: str,
    publish=False,
):
    """
    Build and optionally publish a definition.

    :param cmd:
    :type cmd: _type_
    :param client:
    :type client: HybridNetworkManagementClient
    :param config_file: path to the file
    :param definition_type: VNF, CNF or NSD
    :param publish: _description_, defaults to False
    :type publish: bool, optional
    """
    api_clients = ApiClients(
        aosm_client=client, resource_client=cf_resources(cmd.cli_ctx)
    )

    # Read the config from the given file
    config = _get_config_from_file(config_file, definition_type)

    # Generate the NFD/NSD and the artifact manifest.
    _generate_nfd(definition_type=definition_type, config=config)

    # Publish the definition if publish is true
    if publish:
        if definition_type == VNF:
            deployer = DeployerViaArm(api_clients, config=config)
            deployer.deploy_vnfd_from_bicep()
        else:
            print("TODO - cannot publish CNF or NSD yet.")


def generate_definition_config(definition_type: str, output_file: str = "input.json"):
    """
    Generate an example config file for building a definition.

    :param definition_type: CNF, VNF or NSD
    :param output_file: path to output config file, defaults to "input.json"
    :type output_file: str, optional
    """
    config = get_configuration(definition_type)
    config_as_dict = json.dumps(asdict(config), indent=4)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(config_as_dict)
        print(f"Empty definition configuration has been written to {output_file}")
        logger.info(f"Empty definition configuration has been written to {output_file}")


def _get_config_from_file(config_file: str, definition_type: str) -> NFConfiguration:
    """
    Read input config file JSON and turn it into a Configuration object.

    :param config_file: path to the file
    :param definition_type: VNF, CNF or NSD
    :rtype: Configuration
    """
    with open(config_file, "r", encoding="utf-8") as f:
        config_as_dict = json.loads(f.read())

    config = get_configuration(definition_type, config_as_dict)
    return config


def _generate_nfd(definition_type, config):
    """Generate a Network Function Definition for the given type and config."""
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


def publish_definition(
    cmd,
    client: HybridNetworkManagementClient,
    definition_type,
    config_file,
    definition_file: Optional[str] = None,
    parameters_json_file: Optional[str] = None,
    manifest_file: Optional[str] = None,
    manifest_parameters_json_file: Optional[str] = None,
):
    """
    Publish a generated definition.

    :param cmd:
    :param client:
    :type client: HybridNetworkManagementClient
    :param definition_type: VNF or CNF
    :param config_file: Path to the config file for the NFDV
    :param definition_file: Optional path to a bicep template to deploy, in case the user
                       wants to edit the built NFDV template. If omitted, the default
                       built NFDV template will be used.
    :param parameters_json_file: Optional path to a parameters file for the bicep file,
                      in case the user wants to edit the built NFDV template. If
                      omitted, parameters from config will be turned into parameters
                      for the bicep file
    :param manifest_file: Optional path to an override bicep template to deploy
                          manifests
    :param manifest_parameters_json_file: Optional path to an override bicep parameters
                                          file for manifest parameters
    """
    print("Publishing definition.")
    api_clients = ApiClients(
        aosm_client=client, resource_client=cf_resources(cmd.cli_ctx)
    )
    config = _get_config_from_file(config_file, definition_type)
    if definition_type == VNF:
        deployer = DeployerViaArm(api_clients, config=config)
        deployer.deploy_vnfd_from_bicep(
            bicep_path=definition_file,
            parameters_json_file=parameters_json_file,
            manifest_bicep_path=manifest_file,
            manifest_parameters_json_file=manifest_parameters_json_file,
        )


def delete_published_definition(
    cmd,
    client: HybridNetworkManagementClient,
    definition_type,
    config_file,
    clean=False,
):
    """
    Delete a published definition.

    :param definition_type: CNF or VNF
    :param config_file: Path to the config file
    :param clean: if True, will delete the NFDG, artifact stores and publisher too.
                  Defaults to False. Only works if no resources have those as a parent.
                    Use with care.
    """
    config = _get_config_from_file(config_file, definition_type)

    api_clients = ApiClients(
        aosm_client=client, resource_client=cf_resources(cmd.cli_ctx)
    )

    delly = ResourceDeleter(api_clients, config)
    if definition_type == VNF:
        delly.delete_vnf(clean=clean)


def show_publisher():
    pass
