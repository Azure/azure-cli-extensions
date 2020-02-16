# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['powerbi embedded-capacity'] = """
    type: group
    short-summary: Manage powerbi embedded capacity.
"""

helps['powerbi embedded-capacity create'] = """
    type: command
    short-summary: Provision the specified Dedicated capacity based on the configuration specified in the request.
    examples:
      - name: Create capacity
        text: |-
               az powerbi embedded-capacity create --resource-group "TestRG" --name "azsdktest" \\
               --sku-name "A1" --sku-tier "PBIE_Azure" --administration-members \\
               "azsdktest@microsoft.com,azsdktest2@microsoft.com"
"""

helps['powerbi embedded-capacity update'] = """
    type: command
    short-summary: Provisions the specified Dedicated capacity based on the configuration specified in the request.
    examples:
      - name: Update capacity parameters
        text: |-
               az powerbi embedded-capacity update --resource-group "TestRG" --name "azsdktest" \\
               --sku-name "A1" --sku-tier "PBIE_Azure" --administration-members \\
               "azsdktest@microsoft.com,azsdktest2@microsoft.com"
"""

helps['powerbi embedded-capacity delete'] = """
    type: command
    short-summary: Delete the specified Dedicated capacity.
    examples:
      - name: Delete a capacity in specified resource group
        text: |-
               az powerbi embedded-capacity delete --resource-group "TestRG" --name "azsdktest"
"""

helps['powerbi embedded-capacity show'] = """
    type: command
    short-summary: Get details about the specified dedicated capacity.
    examples:
      - name: Get details of a capacity
        text: |-
               az powerbi embedded-capacity show --resource-group "TestRG" --name "azsdktest"
"""

helps['powerbi embedded-capacity list'] = """
    type: command
    short-summary: Get all the Dedicated capacities for the given resource group.
    examples:
      - name: List capacities in resource group
        text: |-
               az powerbi embedded-capacity list --resource-group "TestRG"
      - name: List all capacities in default subscription.
        text: |-
               az powerbi embedded-capacity list
"""

helps['-'] = """
    type: group
    short-summary: Commands to manage .
"""
