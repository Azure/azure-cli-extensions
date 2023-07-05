# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Optional, Union

from azure.cli.core.azclierror import (
    CLIInternalError,
    InvalidArgumentValueError,
    UnclassifiedUserFault,
)
from knack.log import get_logger

from azext_aosm._client_factory import cf_acr_registries, cf_resources
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
    assert isinstance(config, NFConfiguration)

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
) -> Union[NFConfiguration, NSConfiguration]:
    """
    Read input config file JSON and turn it into a Configuration object.

    :param config_file: path to the file
    :param definition_type: VNF, CNF or NSD
    :rtype: Configuration
    """

    if not os.path.exists(config_file):
        raise InvalidArgumentValueError(
            f"Config file {config_file} not found. Please specify a valid config file"
            " path."
        )

    config = get_configuration(configuration_type, config_file)
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
            "Generate NFD called for unrecognised definition_type. Only VNF and CNF"
            " have been implemented."
        )
    if nfd_generator.nfd_bicep_path:
        carry_on = input(
            f"The {nfd_generator.nfd_bicep_path.parent} directory already exists -"
            " delete it and continue? (y/n)"
        )
        if carry_on != "y":
            raise UnclassifiedUserFault("User aborted!")

        shutil.rmtree(nfd_generator.nfd_bicep_path.parent)
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
    skip: Optional[str] = None,
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
    :param skip: options to skip, either publish bicep or upload artifacts
    """
    print("Publishing definition.")
    api_clients = ApiClients(
        aosm_client=client,
        resource_client=cf_resources(cmd.cli_ctx),
        container_registry_client=cf_acr_registries(cmd.cli_ctx),
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
            skip=skip,
        )
    elif definition_type == CNF:
        deployer = DeployerViaArm(api_clients, config=config)
        deployer.deploy_cnfd_from_bicep(
            cli_ctx=cmd.cli_ctx,
            bicep_path=definition_file,
            parameters_json_file=parameters_json_file,
            manifest_bicep_path=manifest_file,
            manifest_parameters_json_file=manifest_parameters_json_file,
            skip=skip,
        )
    else:
        raise ValueError(
            "Definition type must be either 'vnf' or 'cnf'. Definition type"
            f" {definition_type} is not recognised."
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
        delly.delete_nfd(clean=clean)
    elif definition_type == CNF:
        delly.delete_nfd(clean=clean)
    else:
        raise ValueError(
            "Definition type must be either 'vnf' or 'cnf'. Definition type"
            f" {definition_type} is not recognised."
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
    # Config file is a special parameter on the configuration objects.  It is the path
    # to the configuration file, rather than an input parameter.  It therefore shouldn't
    # be included here.
    config = asdict(get_configuration(configuration_type))
    config.pop("config_file")

    config_as_dict = json.dumps(config, indent=4)

    if Path(output_file).exists():
        carry_on = input(
            f"The file {output_file} already exists - do you want to overwrite it?"
            " (y/n)"
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
        logger.info(
            "Empty %s configuration has been written to %s", prtName, output_file
        )


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
    skip: Optional[str] = None,
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
    :param skip: options to skip, either publish bicep or upload artifacts
    """

    print("Publishing design.")
    api_clients = ApiClients(
        aosm_client=client, resource_client=cf_resources(cmd.cli_ctx)
    )

    config = _get_config_from_file(config_file=config_file, configuration_type=NSD)
    assert isinstance(config, NSConfiguration)
    config.validate()

    deployer = DeployerViaArm(api_clients, config=config)

    deployer.deploy_nsd_from_bicep(
        bicep_path=design_file,
        parameters_json_file=parameters_json_file,
        manifest_bicep_path=manifest_file,
        manifest_parameters_json_file=manifest_parameters_json_file,
        skip=skip,
    )


def _generate_nsd(config: NSConfiguration, api_clients: ApiClients):
    """Generate a Network Service Design for the given config."""
    if os.path.exists(config.output_directory_for_build):
        carry_on = input(
            f"The folder {config.output_directory_for_build} already exists - delete it"
            " and continue? (y/n)"
        )
        if carry_on != "y":
            raise UnclassifiedUserFault("User aborted! ")

        shutil.rmtree(config.output_directory_for_build)
    nsd_generator = NSDGenerator(api_clients, config)
    nsd_generator.generate_nsd()
