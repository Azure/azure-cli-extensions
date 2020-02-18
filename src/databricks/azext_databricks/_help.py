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
               "westus" --managed-resource-group-id \\
               "/subscriptions/{{ subscription_id }}/resourceGroups/{{ resource_group }}"
      - name: Create or update workspace with custom parameters
        text: |-
               az databricks workspace create --resource-group "rg" --name "myWorkspace" --location \\
               "westus" --managed-resource-group-id \\
               "/subscriptions/{{ subscription_id }}/resourceGroups/{{ resource_group }}"
"""

helps['databricks workspace update'] = """
    type: command
    short-summary: Creates a new workspace.
    examples:
      - name: Update a workspace's tags.
        text: |-
               az databricks workspace update --resource-group "rg" --name "myWorkspace"
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
    short-summary: Gets the workspace.
    examples:
      - name: Get a workspace with custom parameters
        text: |-
               az databricks workspace show --resource-group "rg" --name "myWorkspace"
      - name: Get a workspace
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

helps['databricks operation'] = """
    type: group
    short-summary: Commands to manage databricks operation.
"""

helps['databricks operation list'] = """
    type: command
    short-summary: Lists all of the available RP operations.
    examples:
      - name: Operations
        text: |-
               az databricks operation list
"""
