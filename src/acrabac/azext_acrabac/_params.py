# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.commands.parameters import get_enum_type
from .vendored_sdks.containerregistry.v2024_01_01_preview.models import RoleAssignmentMode


def load_arguments_preview(self, _):
    with self.argument_context("acr create", arg_group="Permissions and Role Assignment") as c:
        c.argument(
            "role_assignment_mode",
            arg_type=get_enum_type(RoleAssignmentMode),
            is_preview=True,
            help="Role assignment mode of the registry. "
            "For more information on this preview feature, see https://aka.ms/acr/abac/repository-permissions. The Default is LegacyRegistryPermissions.",
        )

    with self.argument_context("acr update", arg_group="Permissions and Role Assignment") as c:
        c.argument(
            "role_assignment_mode",
            arg_type=get_enum_type(RoleAssignmentMode),
            is_preview=True,
            help="Role assignment mode of the registry. "
            "For more information on this preview feature, see https://aka.ms/acr/abac/repository-permissions. The Default is LegacyRegistryPermissions.",
        )
