# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# Code generated by aaz-dev-tools
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

from azure.cli.core.aaz import *


@register_command_group(
    "neon",
)
class __CMDGroup(AAZCommandGroup):
    """Manage Neon Postgres databases and related resources within Azure.
    """
    pass


__all__ = ["__CMDGroup"]
