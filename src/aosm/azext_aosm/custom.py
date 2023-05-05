# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from dataclasses import asdict
from knack.log import get_logger
from typing import Optional

from azext_aosm.generate_nfd.cnf_nfd_generator import CnfNfdGenerator
from azext_aosm.generate_nfd.nfd_generator_base import NFDGenerator
from azext_aosm.generate_nfd.vnf_bicep_nfd_generator import VnfBicepNfdGenerator
from azext_aosm.deploy.deploy_with_arm import DeployerViaArm
from azext_aosm.util.constants import VNF, CNF, NSD
from azext_aosm.util.management_clients import ApiClients
from .vendored_sdks import HybridNetworkManagementClient
from .client_factory import cf_resources
from configuration import get_configuration, validate_configuration, Configuration


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
    api_clients = ApiClients(
        aosm_client=client, resource_client=cf_resources(cmd.cli_ctx)
    )

    config = _get_config_from_file(config_file, definition_type)

    # Generate the NFD/NSD and the artifact manifest.
    _generate_nfd(definition_type=definition_type, config=config)
    # Write the ARM/bicep template if that's what we are doing

    # Publish the definition if publish is true
    if publish:
        if definition_type == VNF:
            deployer = DeployerViaArm(api_clients, config=config)
            deployer.deploy_vnfd_from_bicep()
        else:
            print("TODO - cannot publish CNF or NSD yet.")


def generate_definition_config(definition_type: str, output_file: str = "input.json"):
    config = get_configuration(definition_type)
    config_as_dict = json.dumps(asdict(config), indent=4)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(config_as_dict)
        print(f"Empty definition configuration has been written to {output_file}")
        logger.info(f"Empty definition configuration has been written to {output_file}")


def _get_config_from_file(config_file: str, definition_type: str) -> Configuration:
    """
    Read input config file JSON and turn it into a Configuration object.

    :param config_file: path to the file
    :param definition_type: VNF, CNF or NSD
    :rtype: Configuration
    """
    with open(config_file, "r", encoding="utf-8") as f:
        config_as_dict = json.loads(f.read())

    config = get_configuration(definition_type, config_as_dict)
    validate_configuration(config)
    return config


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


def publish_definition(
    cmd,
    client: HybridNetworkManagementClient,
    definition_type,
    config_file,
    bicep_file: Optional[str] = None,
    parameters_json_file: Optional[str] = None,
):
    """
    _summary_

    :param cmd:
    :param client:
    :type client: HybridNetworkManagementClient
    :param definition_type: VNF or CNF
    :param config_file: Path to the config file for the NFDV
    :param bicep_file: Optional path to a bicep template to deploy, in case the user
                       wants to edit the built NFDV template. If omitted, the default
                       built NFDV template will be used
    :param parameters_json_file: Optional path to a parameters file for the bicep file,
                      in case the user wants to edit the built NFDV template. If
                      omitted, parameters from config will be turned into parameters
                      for the bicep file
    """
    print("Publishing definition.")
    api_clients = ApiClients(
        aosm_client=client, resource_client=cf_resources(cmd.cli_ctx)
    )
    config = _get_config_from_file(config_file, definition_type)
    if definition_type == VNF:
        deployer = DeployerViaArm(api_clients, config=config)
        deployer.deploy_vnfd_from_bicep(
            bicep_path=bicep_file, parameters_json_file=parameters_json_file
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
    from azext_aosm.delete.delete import ResourceDeleter

    delly = ResourceDeleter(api_clients, config)
    if definition_type == VNF:
        delly.delete_vnf(all=clean)


def show_publisher():
    pass
