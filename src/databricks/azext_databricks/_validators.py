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
    if not namespace.managed_resource_group:
        namespace.managed_resource_group = resource_id(
            subscription=get_subscription_id(cmd.cli_ctx),
            resource_group='databricks-rg-' + namespace.workspace_name + '-' + random_id)
    elif not is_valid_resource_id(namespace.managed_resource_group):
        namespace.managed_resource_group = resource_id(
            subscription=get_subscription_id(cmd.cli_ctx),
            resource_group=namespace.managed_resource_group)

    # set default values similar to portal
    if not namespace.relay_namespace_name:
        namespace.relay_namespace_name = 'dbrelay{}'.format(random_id)
    if not namespace.storage_account_name:
        namespace.storage_account_name = 'dbstorage{}'.format(random_id)
    if not namespace.storage_account_sku_name:
        namespace.storage_account_sku_name = 'Standard_GRS'
    if not namespace.vnet_address_prefix:
        namespace.vnet_address_prefix = '10.139'
