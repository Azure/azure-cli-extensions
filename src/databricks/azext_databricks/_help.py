# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['databricks workspace'] = """
    type: group
    short-summary: Commands to manage databricks workspace.
"""

helps['databricks workspace create'] = """
    type: command
    short-summary: Creates a new workspace.
    examples:
      - name: Create or update workspace
        text: |-
               az databricks workspace create --resource-group "rg" --name "myWorkspace" --location \\
               "westus" --managed-resource-group "myResourceGroup" --sku standard
      - name: Create or update workspace with custom parameters
        text: |-
               az databricks workspace create --resource-group "rg" --name "myWorkspace" --location \\
               "westus" --managed-resource-group \\
               "/subscriptions/subscription_id/resourceGroups/rg" --sku premium
"""

helps['databricks workspace update'] = """
    type: command
    short-summary: Update workspace.
    examples:
      - name: Update a workspace's tags.
        text: |-
               az databricks workspace update --resource-group "rg" --name "myWorkspace" --tags key1=value1 key2=value2
      - name: Clean a workspace's tags.
        text: |-
               az databricks workspace update --resource-group "rg" --name "myWorkspace" --tags ""
"""

helps['databricks workspace delete'] = """
    type: command
    short-summary: Deletes the workspace.
    examples:
      - name: Delete a workspace
        text: |-
               az databricks workspace delete --resource-group "rg" --name "myWorkspace"
"""

helps['databricks workspace show'] = """
    type: command
    short-summary: Show the workspace.
    examples:
      - name: Show a workspace with custom parameters
        text: |-
               az databricks workspace show --resource-group "rg" --name "myWorkspace"
      - name: Show a workspace
        text: |-
               az databricks workspace show --resource-group "rg" --name "myWorkspace"
"""

helps['databricks workspace list'] = """
    type: command
    short-summary: Gets all the workspaces within a resource group.
    examples:
      - name: Lists workspaces
        text: |-
               az databricks workspace list --resource-group "rg"
      - name: Lists workspaces
        text: |-
               az databricks workspace list
"""

helps['databricks workspace wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the Databricks workspace is met.
    examples:
        - name: Pause executing next line of CLI script until the Databricks workspace is successfully provisioned.
          text: az databricks workspace wait --resource-group "rg" --name "myWorkspace" \\
                --created
"""
