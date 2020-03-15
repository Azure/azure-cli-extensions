# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['custom-providers custom-resource-provider'] = """
    type: group
    short-summary: Commands to manage custom resource provider.
"""

helps['custom-providers custom-resource-provider create'] = """
    type: command
    short-summary: Creates or updates the custom resource provider.
    examples:
      - name: Create or update the custom resource provider
        text: |-
               az custom-providers custom-resource-provider create --resource-group "testRG" --name \\
               "newrp" --location "eastus"
"""

helps['custom-providers custom-resource-provider update'] = """
    type: command
    short-summary: Creates or updates the custom resource provider.
    examples:
      - name: Update a custom resource provider
        text: |-
               az custom-providers custom-resource-provider update --resource-group "testRG" --name \\
               "newrp"
"""

helps['custom-providers custom-resource-provider delete'] = """
    type: command
    short-summary: Deletes the custom resource provider.
    examples:
      - name: Delete a custom resource provider
        text: |-
               az custom-providers custom-resource-provider delete --resource-group "testRG" --name \\
               "newrp"
"""

helps['custom-providers custom-resource-provider show'] = """
    type: command
    short-summary: Gets the custom resource provider manifest.
    examples:
      - name: Get a custom resource provider
        text: |-
               az custom-providers custom-resource-provider show --resource-group "testRG" --name \\
               "newrp"
"""

helps['custom-providers custom-resource-provider list'] = """
    type: command
    short-summary: Gets all the custom resource providers within a resource group.
    examples:
      - name: List all custom resource providers on the resourceGroup
        text: |-
               az custom-providers custom-resource-provider list --resource-group "testRG"
      - name: List all custom resource providers on the subscription
        text: |-
               az custom-providers custom-resource-provider list
"""
