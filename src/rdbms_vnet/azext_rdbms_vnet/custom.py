# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def _custom_vnet_update_get(client, resource_group_name, server_name, virtual_network_rule_name):
    return client.get(resource_group_name, server_name, virtual_network_rule_name)


def _custom_vnet_update_set(client, resource_group_name, server_name, virtual_network_rule_name,
                            virtual_network_subnet_id,
                            ignore_missing_vnet_service_endpoint=None):
    return client.create_or_update(resource_group_name, server_name,
                                   virtual_network_rule_name, virtual_network_subnet_id,
                                   ignore_missing_vnet_service_endpoint)
