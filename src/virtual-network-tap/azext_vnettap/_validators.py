# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_subscription_id


def validate_vnet_tap(cmd, namespace):
    if namespace.vnet_tap:
        from msrestazure.tools import is_valid_resource_id, resource_id
        if not is_valid_resource_id(namespace.vnet_tap):
            namespace.vnet_tap = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace='Microsoft.Network', type='virtualNetworkTaps',
                name=namespace.vnet_tap
            )
