# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

#  pylint: disable=line-too-long


def add_helps(command_group, server_type):
    helps['{} server vnet-rule'.format(command_group)] = """
                type: group
                short-summary: Manage a server's virtual network rules.
                """
    helps['{} server vnet-rule update'.format(command_group)] = """
                type: command
                short-summary: Update a virtual network rule.
                """
    helps['{} server vnet-rule create'.format(command_group)] = """
                type: command
                short-summary: Create a virtual network rule to allows access to a {} server.
                examples:
                    - name: Create a virtual network rule by providing the subnet id.
                      text: az {} server vnet-rule create -g testgroup -s testsvr -n vnetRuleName --subnet /subscriptions/{{SubID}}/resourceGroups/{{ResourceGroup}}/providers/Microsoft.Network/virtualNetworks/vnetName/subnets/subnetName
                    - name: Create a vnet rule by providing the vnet and subnet name. The subnet id is created by taking the resource group name and subscription id of the server.
                      text: az {} server vnet-rule create -g testgroup -s testsvr -n vnetRuleName --subnet subnetName --vnet-name vnetName
                """.format(server_type, command_group, command_group)


add_helps("mysql", "MySQL")
add_helps("postgres", "PostgreSQL")
