# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from azure.cli.core.azclierror import (
    CLIInternalError,
    InvalidArgumentValueError,
    UnclassifiedUserFault,
)
from azure.cli.core.commands import AzCliCommand
from azure.core import exceptions as azure_exceptions
from knack.log import get_logger

from azext_aosm._client_factory import cf_features, cf_resources
from azext_aosm._configuration import (
    CNFConfiguration,
    Configuration,
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
from azext_aosm.util.constants import (
    AOSM_FEATURE_NAMESPACE,
    AOSM_REQUIRED_FEATURES,
    CNF,
    NSD,
    VNF,
    DeployableResourceTypes,
    SkipSteps,
)
from azext_aosm.util.management_clients import ApiClients
from azext_aosm.vendored_sdks import HybridNetworkManagementClient

logger = get_logger(__name__)


def build_definition(
    definition_type: str,
    config_file: str,
    order_params: bool = False,
    interactive: bool = False,
    force: bool = False,
):
    """
    Build a definition.

    :param definition_type: VNF or CNF
    :param config_file: path to the file
    :param order_params: VNF definition_type only - ignored for CNF. Order
        deploymentParameters schema and configMappings to have the parameters without
        default values at the top.
    :param interactive: Whether to prompt for input when creating deploy parameters
        mapping files
    :param force: force the build even if the design has already been built
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
        force=force,
    )


def generate_definition_config(definition_type: str, output_file: str = "input.json"):
    """
    Generate an example config file for building a definition.

    :param definition_type: CNF, VNF
    :param output_file: path to output config file, defaults to "input.json"
    """
    config: Configuration
    if definition_type == CNF:
        config = CNFConfiguration.helptext()
    elif definition_type == VNF:
        config = VNFConfiguration.helptext()
    else:
        raise ValueError("definition_type must be CNF or VNF")

    _generate_config(configuration=config, output_file=output_file)


def _get_config_from_file(config_file: str, configuration_type: str) -> Configuration:
    """
    Read input config file JSON and turn it into a Configuration object.

    :param config_file: path to the file
    :param configuration_type: VNF, CNF or NSD
    :returns: The Configuration object
    """

    if not os.path.exists(config_file):
        raise InvalidArgumentValueError(
            f"Config file {config_file} not found. Please specify a valid config file"
            " path."
        )

    config = get_configuration(configuration_type, config_file)
    return config


def _generate_nfd(
    definition_type: str,
    config: NFConfiguration,
    order_params: bool,
    interactive: bool,
    force: bool = False,
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
        if not force:
            carry_on = input(
                f"The {nfd_generator.nfd_bicep_path.parent} directory already exists -"
                " delete it and continue? (y/n)"
            )
            if carry_on != "y":
                raise UnclassifiedUserFault("User aborted!")

        shutil.rmtree(nfd_generator.nfd_bicep_path.parent)
    nfd_generator.generate_nfd()


def _check_features_enabled(cmd: AzCliCommand):
    """
    Check that the required Azure features are enabled on the subscription.

    :param cmd: The AzCLICommand object for the original command that was run, we use
        this to retrieve the CLI context in order to get the features client for access
        to the features API.
    """
    features_client = cf_features(cmd.cli_ctx)
    # Check that the required features are enabled on the subscription
    for feature in AOSM_REQUIRED_FEATURES:
        try:
            feature_result = features_client.features.get(
                resource_provider_namespace=AOSM_FEATURE_NAMESPACE,
                feature_name=feature,
            )
            if (
                not feature_result
                or not feature_result.properties.state == "Registered"
            ):
                # We don't want to log the name of the feature to the user as it is
                # a hidden feature.  We do want to log it to the debug log though.
                logger.debug(
                    "Feature %s is not registered on the subscription.", feature
                )
                raise CLIInternalError(
                    "Your Azure subscription has not been fully onboarded to AOSM. "
                    "Please see the AOSM onboarding documentation for more information."
                )
        except azure_exceptions.ResourceNotFoundError as rerr:
            # If the feature is not found, it is not registered, but also something has
            # gone wrong with the CLI code and onboarding instructions.
            logger.debug(
                "Feature not found error - Azure doesn't recognise the feature %s."
                "This indicates a coding error or error with the AOSM onboarding "
                "instructions.",
                feature,
            )
            logger.debug(rerr)
            raise CLIInternalError(
                "CLI encountered an error checking that your "
                "subscription has been onboarded to AOSM. Please raise an issue against"
                " the CLI."
            ) from rerr


def publish_definition(
    cmd: AzCliCommand,
    client: HybridNetworkManagementClient,
    definition_type,
    config_file,
    definition_file: Optional[str] = None,
    parameters_json_file: Optional[str] = None,
    manifest_file: Optional[str] = None,
    manifest_params_file: Optional[str] = None,
    skip: Optional[SkipSteps] = None,
    no_subscription_permissions: bool = False,
):
    """
    Publish a generated definition.

    :param cmd: The AzCLICommand object for the command that was run, we use this to
                find the CLI context (from which, for example, subscription id and
                credentials can be found, and other clients can be generated.)
    :param client: The AOSM client. This is created in _client_factory.py and passed
                   in by commands.py - we could alternatively just use cf_aosm as
                   we use cf_resources, but other extensions seem to pass a client
                   around like this.
    :type client: HybridNetworkManagementClient
    :param definition_type: VNF or CNF
    :param config_file: Path to the config file for the NFDV
    :param definition_file: Optional path to a bicep template to deploy, in case the
        user wants to edit the built NFDV template. If omitted, the default built NFDV
        template will be used.
    :param parameters_json_file: Optional path to a parameters file for the bicep file,
        in case the user wants to edit the built NFDV template. If omitted, parameters
        from config will be turned into parameters for the bicep file
    :param manifest_file: Optional path to an override bicep template to deploy
        manifests
    :param manifest_params_file: Optional path to an override bicep parameters file for
        manifest parameters
    :param skip: options to skip, either publish bicep or upload artifacts
    :param no_subscription_permissions:
            CNF definition_type publish only - ignored for VNF. Causes the image
            artifact copy from a source ACR to be done via docker pull and push,
            rather than `az acr import`. This is slower but does not require
            Contributor (or importImage action) and AcrPush permissions on the publisher
            subscription. It requires Docker to be installed.
    """
    # Check that the required features are enabled on the subscription
    _check_features_enabled(cmd)

    print("Publishing definition.")
    api_clients = ApiClients(
        aosm_client=client,
        resource_client=cf_resources(cmd.cli_ctx),
    )

    config = _get_config_from_file(
        config_file=config_file, configuration_type=definition_type
    )

    deployer = DeployerViaArm(
        api_clients,
        resource_type=definition_type,
        config=config,
        bicep_path=definition_file,
        parameters_json_file=parameters_json_file,
        manifest_bicep_path=manifest_file,
        manifest_params_file=manifest_params_file,
        skip=skip,
        cli_ctx=cmd.cli_ctx,
        use_manifest_permissions=no_subscription_permissions,
    )
    deployer.deploy_nfd_from_bicep()


def delete_published_definition(
    cmd: AzCliCommand,
    client: HybridNetworkManagementClient,
    definition_type,
    config_file,
    clean=False,
    force=False,
):
    """
    Delete a published definition.

    :param cmd: The AzCLICommand object for the command that was run, we use this to
                find the CLI context (from which, for example, subscription id and
                credentials can be found, and other clients can be generated.)
    :param client: The AOSM client. This is created in _client_factory.py and passed
                   in by commands.py - we could alternatively just use cf_aosm as
                   we use cf_resources, but other extensions seem to pass a client
                   around like this.
    :param definition_type: CNF or VNF
    :param config_file: Path to the config file
    :param clean: if True, will delete the NFDG, artifact stores and publisher too.
        Defaults to False. Only works if no resources have those as a parent.     Use
        with care.
    :param force: if True, will not prompt for confirmation before deleting the resources.
    """
    # Check that the required features are enabled on the subscription
    _check_features_enabled(cmd)

    config = _get_config_from_file(
        config_file=config_file, configuration_type=definition_type
    )

    api_clients = ApiClients(
        aosm_client=client, resource_client=cf_resources(cmd.cli_ctx)
    )

    delly = ResourceDeleter(api_clients, config, cmd.cli_ctx)
    if definition_type == VNF:
        delly.delete_nfd(clean=clean, force=force)
    elif definition_type == CNF:
        delly.delete_nfd(clean=clean, force=force)
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
    _generate_config(NSConfiguration.helptext(), output_file)


def _generate_config(configuration: Configuration, output_file: str = "input.json"):
    """
    Generic generate config function for NFDs and NSDs.

    :param configuration: The Configuration object with helptext filled in for each of
        the fields.
    :param output_file: path to output config file, defaults to "input.json"
    """
    # Config file is a special parameter on the configuration objects.  It is the path
    # to the configuration file, rather than an input parameter.  It therefore shouldn't
    # be included here.
    config = asdict(configuration)
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
        if isinstance(configuration, NSConfiguration):
            prtName = "design"
        else:
            prtName = "definition"
        print(f"Empty {prtName} configuration has been written to {output_file}")
        logger.info(
            "Empty %s configuration has been written to %s", prtName, output_file
        )


def build_design(
    cmd: AzCliCommand,
    client: HybridNetworkManagementClient,
    config_file: str,
    force: bool = False,
):
    """
    Build a Network Service Design.

    :param cmd: The AzCLICommand object for the command that was run, we use this to
                find the CLI context (from which, for example, subscription id and
                credentials can be found, and other clients can be generated.)
    :param client: The AOSM client. This is created in _client_factory.py and passed
                   in by commands.py - we could alternatively just use cf_aosm as
                   we use cf_resources, but other extensions seem to pass a client
                   around like this.
    :type client: HybridNetworkManagementClient
    :param config_file: path to the file
    :param force: force the build, even if the design has already been built
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
        force=force,
    )


def delete_published_design(
    cmd: AzCliCommand,
    client: HybridNetworkManagementClient,
    config_file,
    clean=False,
    force=False,
):
    """
    Delete a published NSD.

    :param cmd: The AzCLICommand object for the command that was run, we use this to
                find the CLI context (from which, for example, subscription id and
                credentials can be found, and other clients can be generated.)
    :param client: The AOSM client. This is created in _client_factory.py and passed
                   in by commands.py - we could alternatively just use cf_aosm as
                   we use cf_resources, but other extensions seem to pass a client
                   around like this.
    :param config_file: Path to the config file
    :param clean: if True, will delete the NSD, artifact stores and publisher too.
                  Defaults to False. Only works if no resources have those as a parent.
                    Use with care.
    :param clean: if True, will delete the NSD on top of the other resources.
    :param force: if True, will not prompt for confirmation before deleting the resources.
    """
    # Check that the required features are enabled on the subscription
    _check_features_enabled(cmd)

    config = _get_config_from_file(config_file=config_file, configuration_type=NSD)

    api_clients = ApiClients(
        aosm_client=client, resource_client=cf_resources(cmd.cli_ctx)
    )

    destroyer = ResourceDeleter(api_clients, config, cmd.cli_ctx)
    destroyer.delete_nsd(clean=clean, force=force)


def publish_design(
    cmd: AzCliCommand,
    client: HybridNetworkManagementClient,
    config_file,
    design_file: Optional[str] = None,
    parameters_json_file: Optional[str] = None,
    manifest_file: Optional[str] = None,
    manifest_params_file: Optional[str] = None,
    skip: Optional[SkipSteps] = None,
):
    """
    Publish a generated design.

    :param cmd: The AzCLICommand object for the command that was run, we use this to
                find the CLI context (from which, for example, subscription id and
                credentials can be found, and other clients can be generated.)
    :param client: The AOSM client. This is created in _client_factory.py and passed
                   in by commands.py - we could alternatively just use cf_aosm as
                   we use cf_resources, but other extensions seem to pass a client
                   around like this.
    :type client: HybridNetworkManagementClient
    :param config_file: Path to the config file for the NSDV
    :param design_file: Optional path to an override bicep template to deploy the NSDV.
    :param parameters_json_file: Optional path to a parameters file for the bicep file,
                      in case the user wants to edit the built NSDV template. If
                      omitted, parameters from config will be turned into parameters
                      for the bicep file
    :param manifest_file: Optional path to an override bicep template to deploy
                        manifests
    :param manifest_params_file: Optional path to an override bicep parameters
                        file for manifest parameters
    :param skip: options to skip, either publish bicep or upload artifacts
    """
    # Check that the required features are enabled on the subscription
    _check_features_enabled(cmd)

    print("Publishing design.")
    api_clients = ApiClients(
        aosm_client=client, resource_client=cf_resources(cmd.cli_ctx)
    )

    config = _get_config_from_file(config_file=config_file, configuration_type=NSD)
    assert isinstance(config, NSConfiguration)
    config.validate()

    deployer = DeployerViaArm(
        api_clients,
        resource_type=DeployableResourceTypes.NSD,
        config=config,
        bicep_path=design_file,
        parameters_json_file=parameters_json_file,
        manifest_bicep_path=manifest_file,
        manifest_params_file=manifest_params_file,
        skip=skip,
        cli_ctx=cmd.cli_ctx,
    )

    deployer.deploy_nsd_from_bicep()


def _generate_nsd(
    config: NSConfiguration, api_clients: ApiClients, force: bool = False
):
    """Generate a Network Service Design for the given config."""
    if config:
        nsd_generator = NSDGenerator(config=config, api_clients=api_clients)
    else:
        raise CLIInternalError("Generate NSD called without a config file")

    if os.path.exists(config.output_directory_for_build):
        if not force:
            carry_on = input(
                f"The folder {config.output_directory_for_build} already exists - delete it"
                " and continue? (y/n)"
            )
            if carry_on != "y":
                raise UnclassifiedUserFault("User aborted! ")

        shutil.rmtree(config.output_directory_for_build)

    nsd_generator.generate_nsd()
