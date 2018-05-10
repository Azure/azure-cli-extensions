# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument

from azure.cli.core.commands.client_factory import get_subscription_id
from msrestazure.tools import resource_id, is_valid_resource_id, parse_resource_id  # pylint: disable=import-error
from azext_rdbms.mysql.operations.servers_operations import ServersOperations
from ._client_factory import get_mysql_management_client, get_postgresql_management_client



def _custom_vnet_update_get(client, resource_group_name, server_name, virtual_network_rule_name):
    return client.get(resource_group_name, server_name, virtual_network_rule_name)

def _custom_vnet_update_set(client, resource_group_name, server_name, virtual_network_rule_name, virtual_network_subnet_id, ignore_missing_vnet_service_endpoint=None, parameters=None):
    return client.create_or_update(resource_group_name, server_name, virtual_network_rule_name, virtual_network_subnet_id, ignore_missing_vnet_service_endpoint)
