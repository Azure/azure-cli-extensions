# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from ..aaz.latest.vmware.private_cloud.pure_storage_policy import List, Show, Create, Delete
from azure.cli.core.aaz import register_command_group, register_command, AAZCommandGroup


@register_command_group(
    "vmware pure-storage-policy",
)
class __CMDGroup(AAZCommandGroup):  # pylint: disable=too-few-public-methods
    """Commands to manage Pure Storage policy resources.
    """


__all__ = ["__CMDGroup"]


@register_command(
    "vmware pure-storage-policy list",
)
class PureStoragePolicyList(List):
    """List Pure Storage policy resources by PrivateCloud.

    :example: List ProvisionedNetwork resources.
        az vmware pure-storage-policy list --resource-group group1 --private-cloud-name cloud1
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return args_schema


@register_command(
    "vmware pure-storage-policy show",
)
class PureStoragePolicyShow(Show):
    """Show details of a Pure Storage policy for a private cloud.

    :example: Show details of a Pure Storage policy.
        az vmware pure-storage-policy show --resource-group group1 --private-cloud-name cloud1 --storage-policy-name storagePolicy1
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return args_schema


@register_command(
    "vmware pure-storage-policy create",
)
class PureStoragePolicyCreate(Create):
    """Create a Pure Storage policy for a private cloud.

    :example: Create a Pure Storage policy.
        az vmware pure-storage-policy create --resource-group group1 --private-cloud-name cloud1 --storage-policy-name storagePolicy1 --storage-policy-definition storagePolicyDefinition1 --storage-pool-id /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/group1/providers/PureStorage.Block/storagePools/storagePool1
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        setattr(args_schema.no_wait, '_registered', False)
        return args_schema


@register_command(
    "vmware pure-storage-policy delete",
    confirmation="This will delete the Pure Storage policy. Are you sure?",
)
class PureStoragePolicyDelete(Delete):
    """Delete a Pure Storage policy for a private cloud.

    :example: Delete a Pure Storage policy.
        az vmware pure-storage-policy delete --resource-group group1 --private-cloud-name cloud1 --storage-policy-name storagePolicy1
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return args_schema
