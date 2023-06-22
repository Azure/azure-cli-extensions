# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import shutil
from dataclasses import asdict
from typing import Optional

from azure.cli.core.azclierror import (
    CLIInternalError,
    InvalidArgumentValueError,
    UnclassifiedUserFault,
)
from knack.log import get_logger

from azext_aosm._client_factory import cf_resources
from azext_aosm._configuration import (
    CNFConfiguration,
    NFConfiguration,
    NSConfiguration,
    VNFConfiguration,
    get_configuration,
)
from azext_aosm.delete.delete import ResourceDeleter
from azext_aosm.deploy.deploy_with_arm import DeployerViaArm
from azext_aosm.generate_nfd.cnf_nfd_generator import CnfNfdGenerator
from azext_aosm.generate_nfd.nfd_generator_base import NFDGenerator
from azext_aosm.generate_nfd.vnf_nfd_generator import VnfNfdGenerator
from azext_aosm.generate_nsd.nsd_generator import NSDGenerator
from azext_aosm.util.constants import CNF, NSD, VNF
from azext_aosm.util.management_clients import ApiClients
from azext_aosm.vendored_sdks import HybridNetworkManagementClient

logger = get_logger(__name__)


def build_definition(
    definition_type: str,
    config_file: str,
    order_params: bool = False,
    interactive: bool = False,
):
    """
    Build a definition.

    :param cmd:
    :type cmd: _type_
    :param config_file: path to the file
    :param definition_type: VNF, CNF
    """

    # Read the config from the given file
    config = _get_config_from_file(
        config_file=config_file, configuration_type=definition_type
    )

    # Generate the NFD and the artifact manifest.
    _generate_nfd(
        definition_type=definition_type,
        config=config,
        order_params=order_params,
        interactive=interactive,
    )


def generate_definition_config(definition_type: str, output_file: str = "input.json"):
    """
    Generate an example config file for building a definition.

    :param definition_type: CNF, VNF
    :param output_file: path to output config file, defaults to "input.json"
    :type output_file: str, optional
    """
    _generate_config(configuration_type=definition_type, output_file=output_file)


def _get_config_from_file(
    config_file: str, configuration_type: str
) -> NFConfiguration or NSConfiguration:
    """
    Read input config file JSON and turn it into a Configuration object.

    :param config_file: path to the file
    :param definition_type: VNF, CNF or NSD
    :rtype: Configuration
    """

    if not os.path.exists(config_file):
        raise InvalidArgumentValueError(
            f"Config file {config_file} not found. Please specify a valid config file path."
        )

    with open(config_file, "r", encoding="utf-8") as f:
        config_as_dict = json.loads(f.read())
    config = get_configuration(configuration_type, config_as_dict)
    return config


def _generate_nfd(
    definition_type: str, config: NFConfiguration, order_params: bool, interactive: bool
):
    """Generate a Network Function Definition for the given type and config."""
    nfd_generator: NFDGenerator
    if definition_type == VNF:
        assert isinstance(config, VNFConfiguration)
        nfd_generator = VnfNfdGenerator(config, order_params, interactive)
    elif definition_type == CNF:
        assert isinstance(config, CNFConfiguration)
        nfd_generator = CnfNfdGenerator(config, interactive)
    else:
        raise CLIInternalError(
            "Generate NFD called for unrecognised definition_type. Only VNF and CNF have been implemented."
        )
    if nfd_generator.bicep_path:
        carry_on = input(
            f"The folder {os.path.dirname(nfd_generator.bicep_path)} already exists - delete it and continue? (y/n)"
        )
        if carry_on != "y":
            raise UnclassifiedUserFault("User aborted! ")

        shutil.rmtree(os.path.dirname(nfd_generator.bicep_path))
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
    :param definition_file: Optional path to a bicep template to deploy, in case the
        user wants to edit the built NFDV template.
        If omitted, the default built NFDV template will be used.
    :param parameters_json_file: Optional path to a parameters file for the bicep file,
        in case the user wants to edit the built NFDV template. If omitted,
        parameters from config will be turned into parameters for the bicep file
    :param manifest_file: Optional path to an override bicep template to deploy
        manifests
    :param manifest_parameters_json_file: Optional path to an override bicep parameters
        file for manifest parameters
    """
    print("Publishing definition.")
    api_clients = ApiClients(
        aosm_client=client, resource_client=cf_resources(cmd.cli_ctx)
    )
    config = _get_config_from_file(
        config_file=config_file, configuration_type=definition_type
    )
    if definition_type == VNF:
        deployer = DeployerViaArm(api_clients, config=config)
        deployer.deploy_vnfd_from_bicep(
            bicep_path=definition_file,
            parameters_json_file=parameters_json_file,
            manifest_bicep_path=manifest_file,
            manifest_parameters_json_file=manifest_parameters_json_file,
        )
    else:
        raise NotImplementedError(
            "Publishing of CNF definitions is not yet implemented. \
            You should manually deploy your bicep file and upload charts and images to your artifact store. "
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
        Defaults to False. Only works if no resources have those as a parent.     Use
        with care.
    """
    config = _get_config_from_file(
        config_file=config_file, configuration_type=definition_type
    )

    api_clients = ApiClients(
        aosm_client=client, resource_client=cf_resources(cmd.cli_ctx)
    )

    delly = ResourceDeleter(api_clients, config)
    if definition_type == VNF:
        delly.delete_vnf(clean=clean)
    else:
        raise NotImplementedError(
            "Deleting of published CNF definitions is not yet implemented."
        )


def generate_design_config(output_file: str = "input.json"):
    """
    Generate an example config file for building a NSD.

    :param output_file: path to output config file, defaults to "input.json"
    :type output_file: str, optional
    """
    _generate_config(NSD, output_file)


def _generate_config(configuration_type: str, output_file: str = "input.json"):
    """
    Generic generate config function for NFDs and NSDs.

    :param configuration_type: CNF, VNF or NSD
    :param output_file: path to output config file, defaults to "input.json"
    :type output_file: str, optional
    """
    config = get_configuration(configuration_type)
    config_as_dict = json.dumps(asdict(config), indent=4)

    if os.path.exists(output_file):
        carry_on = input(
            f"The file {output_file} already exists - do you want to overwrite it? (y/n)"
        )
        if carry_on != "y":
            raise UnclassifiedUserFault("User aborted!")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(config_as_dict)
        if configuration_type in (CNF, VNF):
            prtName = "definition"
        else:
            prtName = "design"
        print(f"Empty {prtName} configuration has been written to {output_file}")
        logger.info(f"Empty {prtName} configuration has been written to {output_file}")


def build_design(cmd, client: HybridNetworkManagementClient, config_file: str):
    """
    Build a Network Service Design.

    :param cmd:
    :type cmd: _type_
    :param client:
    :type client: HybridNetworkManagementClient
    :param config_file: path to the file
    """

    api_clients = ApiClients(
        aosm_client=client, resource_client=cf_resources(cmd.cli_ctx)
    )

    # Read the config from the given file
    config = _get_config_from_file(config_file=config_file, configuration_type=NSD)
    assert isinstance(config, NSConfiguration)
    config.validate()

    # Generate the NSD and the artifact manifest.
    # This function should not be taking deploy parameters
    _generate_nsd(
        config=config,
        api_clients=api_clients,
    )


def delete_published_design(
    cmd,
    client: HybridNetworkManagementClient,
    config_file,
):
    """
    Delete a published NSD.

    :param config_file: Path to the config file
    :param clean: if True, will delete the NSDG, artifact stores and publisher too.
                  Defaults to False. Only works if no resources have those as a parent.
                    Use with care.
    """
    config = _get_config_from_file(config_file=config_file, configuration_type=NSD)

    api_clients = ApiClients(
        aosm_client=client, resource_client=cf_resources(cmd.cli_ctx)
    )

    destroyer = ResourceDeleter(api_clients, config)
    destroyer.delete_nsd()


def publish_design(
    cmd,
    client: HybridNetworkManagementClient,
    config_file,
    design_file: Optional[str] = None,
    parameters_json_file: Optional[str] = None,
    manifest_file: Optional[str] = None,
    manifest_parameters_json_file: Optional[str] = None,
):
    """
    Publish a generated design.

    :param cmd:
    :param client:
    :type client: HybridNetworkManagementClient
    :param config_file: Path to the config file for the NSDV
    :param design_file: Optional path to an override bicep template to deploy the NSDV.
    :param parameters_json_file: Optional path to a parameters file for the bicep file,
                      in case the user wants to edit the built NSDV template. If
                      omitted, parameters from config will be turned into parameters
                      for the bicep file
    :param manifest_file: Optional path to an override bicep template to deploy
                        manifests
    :param manifest_parameters_json_file: Optional path to an override bicep parameters
                        file for manifest parameters
    """

    print("Publishing design.")
    api_clients = ApiClients(
        aosm_client=client, resource_client=cf_resources(cmd.cli_ctx)
    )

    config = _get_config_from_file(config_file=config_file, configuration_type=NSD)

    config.validate()

    deployer = DeployerViaArm(api_clients, config=config)

    deployer.deploy_nsd_from_bicep(
        bicep_path=design_file,
        parameters_json_file=parameters_json_file,
        manifest_bicep_path=manifest_file,
        manifest_parameters_json_file=manifest_parameters_json_file,
    )


def _generate_nsd(config: NSConfiguration, api_clients: ApiClients):
    """Generate a Network Service Design for the given config."""
    if os.path.exists(config.build_output_folder_name):
        carry_on = input(
            f"The folder {config.build_output_folder_name} already exists - delete it and continue? (y/n)"
        )
        if carry_on != "y":
            raise UnclassifiedUserFault("User aborted! ")

        shutil.rmtree(config.build_output_folder_name)
    nsd_generator = NSDGenerator(api_clients, config)
    nsd_generator.generate_nsd()
