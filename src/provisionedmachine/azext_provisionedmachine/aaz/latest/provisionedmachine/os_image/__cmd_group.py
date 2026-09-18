# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

from azure.cli.core.aaz import *


@register_command_group(
    "provisionedmachine os-image",
)
class __CMDGroup(AAZCommandGroup):
    """Manage OS images for provisioned machines.
    """
    pass


__all__ = ["__CMDGroup"]
