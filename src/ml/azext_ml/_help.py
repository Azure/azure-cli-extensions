# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['ml'] = """
    type: group
    short-summary: Commands to manage ml.
"""

helps['ml list'] = """
    type: command
    short-summary: Lists all the available REST API operations.
"""

helps['ml'] = """
    type: group
    short-summary: Commands to manage ml.
"""

helps['ml create'] = """
    type: command
    short-summary: Creates or updates a workspace with the specified parameters.
    examples:
      - name: WorkspaceCreate
        text: |-
               az ml create --resource-group "myResourceGroup" --name "testworkspace" --location \\
               "West Europe"
"""

helps['ml update'] = """
    type: command
    short-summary: Creates or updates a workspace with the specified parameters.
    examples:
      - name: WorkspaceUpdate
        text: |-
               az ml update --resource-group "myResourceGroup" --name "testworkspace" \\
               --key-vault-identifier-id "kvidnew"
"""

helps['ml delete'] = """
    type: command
    short-summary: Deletes a machine learning workspace.
    examples:
      - name: WorkspaceDelete
        text: |-
               az ml delete --resource-group "myResourceGroup" --name "testworkspace"
"""

helps['ml show'] = """
    type: command
    short-summary: Gets the properties of the specified machine learning workspace.
    examples:
      - name: WorkspaceGet
        text: |-
               az ml show --resource-group "myResourceGroup" --name "testworkspace"
"""

helps['ml list'] = """
    type: command
    short-summary: Lists all the available machine learning workspaces under the specified resource group.
    examples:
      - name: WorkspaceListResourceGroup
        text: |-
               az ml list --resource-group "myResourceGroup"
      - name: WorkspaceGetBySubscription
        text: |-
               az ml list
"""

helps['ml resync_storage_keys'] = """
    type: command
    short-summary: Resync storage keys associated with this workspace.
    examples:
      - name: ResyncStorageKeys
        text: |-
               az ml resync_storage_keys --resource-group "myResourceGroup" --name "testworkspace"
"""

helps['ml list_workspace_keys'] = """
    type: command
    short-summary: List the authorization keys associated with this workspace.
    examples:
      - name: ListWorkspaceKeys
        text: |-
               az ml list_workspace_keys --resource-group "myResourceGroup" --name "testworkspace"
"""
