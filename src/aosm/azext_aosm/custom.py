# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations

from pathlib import Path
from typing import Optional

from azure.cli.core.azclierror import UnrecognizedArgumentError
from azure.cli.core.commands import AzCliCommand

from azext_aosm.cli_handlers.onboarding_cnf_handler import OnboardingCNFCLIHandler
from azext_aosm.cli_handlers.onboarding_vnf_handler import OnboardingVNFCLIHandler
from azext_aosm.cli_handlers.onboarding_core_vnf_handler import OnboardingCoreVNFCLIHandler
from azext_aosm.cli_handlers.onboarding_nexus_vnf_handler import OnboardingNexusVNFCLIHandler
from azext_aosm.cli_handlers.onboarding_nsd_handler import OnboardingNSDCLIHandler
from azext_aosm.common.command_context import CommandContext
from azext_aosm.common.constants import ALL_PARAMETERS_FILE_NAME, CNF, VNF, VNF_NEXUS


def onboard_nfd_generate_config(definition_type: str, output_file: str | None):
    """Generate config file for onboarding NFs."""
    # Declare types explicitly
    handler: OnboardingCNFCLIHandler | OnboardingVNFCLIHandler | OnboardingNexusVNFCLIHandler
    if definition_type == CNF:
        handler = OnboardingCNFCLIHandler()
    elif definition_type == VNF:
        handler = OnboardingCoreVNFCLIHandler()
    elif definition_type == VNF_NEXUS:
        handler = OnboardingNexusVNFCLIHandler()
    else:
        raise UnrecognizedArgumentError(
            "Invalid definition type, valid values are 'cnf', 'vnf' or 'vnfnexus'")
    handler.generate_config(output_file)


def onboard_nfd_build(
    definition_type: str, config_file: Path, skip: Optional[str] = None
):
    """Build the NF definition."""
    # Declare types explicitly
    handler: OnboardingCNFCLIHandler | OnboardingVNFCLIHandler | OnboardingNexusVNFCLIHandler
    if definition_type == CNF:
        handler = OnboardingCNFCLIHandler(config_file_path=Path(config_file), skip=skip)
    elif definition_type == VNF:
        handler = OnboardingCoreVNFCLIHandler(config_file_path=Path(config_file))
    elif definition_type == VNF_NEXUS:
        handler = OnboardingNexusVNFCLIHandler(config_file_path=Path(config_file))
    else:
        raise UnrecognizedArgumentError(
            "Invalid definition type, valid values are 'cnf', 'vnf' or 'vnfnexus'")
    handler.build()


def onboard_nfd_publish(
    cmd: AzCliCommand,
    definition_type: str,
    build_output_folder: Path,
    no_subscription_permissions: bool = False,
):
    """Publish the NF definition."""
    command_context = CommandContext(
        cli_ctx=cmd.cli_ctx,
        cli_options={
            "no_subscription_permissions": no_subscription_permissions,
            "definition_folder": Path(build_output_folder),
        },
    )
    # Declare types explicitly
    handler: OnboardingCNFCLIHandler | OnboardingVNFCLIHandler
    if definition_type == CNF:
        handler = OnboardingCNFCLIHandler(
            all_deploy_params_file_path=Path(build_output_folder, ALL_PARAMETERS_FILE_NAME))
    elif definition_type == VNF:
        handler = OnboardingCoreVNFCLIHandler(
            all_deploy_params_file_path=Path(build_output_folder, ALL_PARAMETERS_FILE_NAME))
    elif definition_type == VNF_NEXUS:
        handler = OnboardingNexusVNFCLIHandler(
            all_deploy_params_file_path=Path(build_output_folder, ALL_PARAMETERS_FILE_NAME))
    else:
        raise UnrecognizedArgumentError(
            "Invalid definition type, valid values are 'cnf', 'vnf' or 'vnfnexus'")
    handler.publish(command_context=command_context)


# def onboard_nfd_delete(cmd: AzCliCommand, definition_type: str, config_file: str):
#     """Delete the NF definition."""
#     command_context = CommandContext(cmd.cli_ctx)
#     if definition_type == "cnf":
#         handler = OnboardingCNFCLIHandler(config_file)
#         handler.delete(command_context=command_context)
#     elif definition_type == "vnf":
#         handler = OnboardingVNFCLIHandler(config_file)
#         handler.delete(command_context=command_context)
#     else:
#         raise UnrecognizedArgumentError("Invalid definition type")


def onboard_nsd_generate_config(output_file: str | None):
    """Generate config file for onboarding NSD."""
    handler = OnboardingNSDCLIHandler()
    handler.generate_config(output_file)


def onboard_nsd_build(config_file: Path, cmd: AzCliCommand):
    """Build the NSD definition."""
    command_context = CommandContext(cli_ctx=cmd.cli_ctx)
    handler = OnboardingNSDCLIHandler(config_file_path=Path(config_file),
                                      aosm_client=command_context.aosm_client)
    handler.build()


def onboard_nsd_publish(
    cmd: AzCliCommand,
    build_output_folder: Path,
    no_subscription_permissions: bool = False,
):
    """Publish the NF definition."""
    command_context = CommandContext(
        cli_ctx=cmd.cli_ctx,
        cli_options={
            "no_subscription_permissions": no_subscription_permissions,
            "definition_folder": Path(build_output_folder),
        },
    )
    handler = OnboardingNSDCLIHandler(
        all_deploy_params_file_path=Path(build_output_folder, ALL_PARAMETERS_FILE_NAME)
    )
    handler.publish(command_context=command_context)


# def onboard_nsd_delete(cmd: AzCliCommand, config_file: str):
#     """Delete the NSD definition."""
#     command_context = CommandContext(cmd.cli_ctx)
#     handler = OnboardingNSDCLIHandler(config_file)
#     handler.delete(command_context=command_context)
