# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# Code generated by aaz-dev-tools
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands import AzCliCommand

from .custom_commands.load_balancer import enable_load_balancer, disable_load_balancer


def enable_load_balancer_cmd(cmd: AzCliCommand, resource_uri: str):
    """
    Enable load balancer service in a connected cluster


    :param resource_uri: The resource uri of the connected cluster
    """

    return enable_load_balancer(cmd, resource_uri)


def disable_load_balancer_cmd(cmd: AzCliCommand, resource_uri: str):
    """
    Disable load_balancer service in a connected cluster


    :param resource_uri: The resource uri of the connected cluster
    """

    return disable_load_balancer(cmd, resource_uri)
