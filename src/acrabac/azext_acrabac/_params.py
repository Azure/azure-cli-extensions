# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import get_three_state_flag


def load_arguments_preview(self, _):
    with self.argument_context("acr create", arg_group="Permissions and Role Assignment") as c:
        c.argument(
            "abac_permissions_enabled",
            arg_type=get_three_state_flag(),
            is_preview=True,
            help="Create a registry with ABAC-enabled Repository Permissions. This allows granting role assignment permissions at the repository level through role assignment conditions. For more information on this preview feature, see https://aka.ms/acr/abac/repository-permissions. The Default is false.",
        )

    with self.argument_context("acr update", arg_group="Permissions and Role Assignment") as c:
        c.argument(
            "abac_permissions_enabled",
            arg_type=get_three_state_flag(),
            is_preview=True,
            help="Update a registry to enable or disable ABAC-enabled Repository Permissions. This allows granting role assignment permissions at the repository level through role assignment conditions. For more information on this preview feature, see https://aka.ms/acr/abac/repository-permissions. The Default is false.",
        )
