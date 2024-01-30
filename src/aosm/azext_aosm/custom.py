# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations

from pathlib import Path
from azext_aosm.cli_handlers.onboarding_cnf_handler import OnboardingCNFCLIHandler
from azext_aosm.cli_handlers.onboarding_vnf_handler import OnboardingVNFCLIHandler
from azext_aosm.cli_handlers.onboarding_nsd_handler import OnboardingNSDCLIHandler
from azext_aosm.common.command_context import CommandContext
from azext_aosm.common.constants import ALL_PARAMETERS_FILE_NAME, CNF, VNF
from azure.cli.core.commands import AzCliCommand
from azure.cli.core.azclierror import UnrecognizedArgumentError


def onboard_nfd_generate_config(definition_type: str, output_file: str | None):
    """Generate config file for onboarding NFs."""
    if definition_type == CNF:
        handler = OnboardingCNFCLIHandler()
        handler.generate_config(output_file)
    elif definition_type == VNF:
        handler = OnboardingVNFCLIHandler()
        handler.generate_config(output_file)
    else:
        raise UnrecognizedArgumentError("Invalid definition type")


def onboard_nfd_build(definition_type: str, config_file: Path, skip: str = None):
    """Build the NF definition."""
    if definition_type == CNF:
        handler = OnboardingCNFCLIHandler(Path(config_file), skip=skip)
        handler.build()
    elif definition_type == VNF:
        handler = OnboardingVNFCLIHandler(Path(config_file))
        handler.build()
    else:
        raise UnrecognizedArgumentError("Invalid definition type")


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
    if definition_type == CNF:
        handler = OnboardingCNFCLIHandler(
            Path(build_output_folder, ALL_PARAMETERS_FILE_NAME)
        )
        handler.publish(command_context=command_context)
    elif definition_type == VNF:
        handler = OnboardingVNFCLIHandler(
            Path(build_output_folder, ALL_PARAMETERS_FILE_NAME)
        )
        handler.publish(command_context=command_context)
    else:
        raise UnrecognizedArgumentError("Invalid definition type")


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
    handler = OnboardingNSDCLIHandler(Path(config_file), command_context.aosm_client)
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
        Path(build_output_folder, ALL_PARAMETERS_FILE_NAME)
    )
    handler.publish(command_context=command_context)


# def onboard_nsd_delete(cmd: AzCliCommand, config_file: str):
#     """Delete the NSD definition."""
#     command_context = CommandContext(cmd.cli_ctx)
#     handler = OnboardingNSDCLIHandler(config_file)
#     handler.delete(command_context=command_context)
