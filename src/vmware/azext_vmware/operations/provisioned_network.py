# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from ..aaz.latest.vmware.private_cloud.provisioned_network import List, Show
from azure.cli.core.aaz import register_command_group, register_command, AAZCommandGroup


@register_command_group(
    "vmware provisioned-network",
)
class __CMDGroup(AAZCommandGroup):  # pylint: disable=too-few-public-methods
    """Commands to list and show provisioned network resources.
    """


__all__ = ["__CMDGroup"]


@register_command(
    "vmware provisioned-network list",
)
class ProvisionedNetworkList(List):
    """List ProvisionedNetwork resources by PrivateCloud.

    :example: List ProvisionedNetwork resources.
        az vmware provisioned-network list --resource-group group1 --private-cloud-name cloud1
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return args_schema


@register_command(
    "vmware provisioned-network show",
)
class ProvisionedNetworkShow(Show):
    """ Get a provisioned network by name in a private cloud.

    :example: Get a provisioned network by name.
        az vmware provisioned-network show --resource-group group1 --private-cloud-name cloud1 --provisioned-network-name network1
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return args_schema
