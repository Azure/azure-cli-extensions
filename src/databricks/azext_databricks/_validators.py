# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import random
import string


def id_generator(size=13, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def validate_workspace_values(cmd, namespace):
    """Parse managed resource_group which can be either resource group name or id"""
    from msrestazure.tools import is_valid_resource_id, resource_id
    from azure.cli.core.commands.client_factory import get_subscription_id

    random_id = id_generator()
    subscription_id = get_subscription_id(cmd.cli_ctx)
    if not namespace.managed_resource_group:
        namespace.managed_resource_group = resource_id(
            subscription=subscription_id,
            resource_group='databricks-rg-' + namespace.workspace_name + '-' +
            random_id)
    elif not is_valid_resource_id(namespace.managed_resource_group):
        namespace.managed_resource_group = resource_id(
            subscription=subscription_id,
            resource_group=namespace.managed_resource_group)

    # name to resource id for virtual-network
    if namespace.custom_virtual_network_id is not None \
       and not is_valid_resource_id(namespace.custom_virtual_network_id):
        namespace.custom_virtual_network_id = resource_id(
            subscription=subscription_id,
            resource_group=namespace.resource_group_name,
            namespace='Microsoft.Network',
            type='virtualNetworks',
            name=namespace.custom_virtual_network_id)
