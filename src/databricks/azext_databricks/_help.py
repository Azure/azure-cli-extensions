# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['databricks'] = """
    type: group
    short-summary: Manage databricks workspaces.
"""

helps['databricks workspace'] = """
    type: group
    short-summary: Commands to manage databricks workspace.
"""

helps['databricks workspace create'] = """
    type: command
    short-summary: Create a new workspace.
    examples:
      - name: Create a workspace
        text: |-
               az databricks workspace create --resource-group MyResourceGroup --name MyWorkspace --location westus --sku standard
      - name: Create a workspace with managed identity for storage account
        text: |-
               az databricks workspace create --resource-group MyResourceGroup --name MyWorkspace --location eastus2euap --sku premium --prepare-encryption
"""

helps['databricks workspace update'] = """
    type: command
    short-summary: Update the workspace.
    examples:
      - name: Update the workspace's tags.
        text: |-
               az databricks workspace update --resource-group MyResourceGroup --name MyWorkspace --tags key1=value1 key2=value2
      - name: Clean the workspace's tags.
        text: |-
               az databricks workspace update --resource-group MyResourceGroup --name MyWorkspace --tags ""
      - name: Prepare for CMK encryption by assigning identity for storage account.
        text: |-
               az databricks workspace update --resource-group MyResourceGroup --name MyWorkspace --prepare-encryption
      - name: Configure CMK encryption
        text: |-
               az databricks workspace update --resource-group MyResourceGroup --name MyWorkspace --key-source Microsoft.KeyVault \
--key-name MyKey --key-vault https://myKeyVault.vault.azure.net/ --key-version 00000000000000000000000000000000
      - name: Revert encryption to Microsoft Managed Keys
        text: |-
               az databricks workspace update --resource-group MyResourceGroup --name MyWorkspace --key-source Default
"""

helps['databricks workspace delete'] = """
    type: command
    short-summary: Delete the workspace.
    examples:
      - name: Delete the workspace
        text: |-
               az databricks workspace delete --resource-group MyResourceGroup --name MyWorkspace
"""

helps['databricks workspace show'] = """
    type: command
    short-summary: Show the workspace.
    examples:
      - name: Show the workspace
        text: |-
               az databricks workspace show --resource-group MyResourceGroup --name MyWorkspace
"""

helps['databricks workspace list'] = """
    type: command
    short-summary: Get all the workspaces.
    examples:
      - name: List workspaces within a resource group
        text: |-
               az databricks workspace list --resource-group MyResourceGroup
      - name: List workspaces within the default subscription
        text: |-
               az databricks workspace list
"""

helps['databricks workspace wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the Databricks workspace is met.
    examples:
        - name: Pause executing next line of CLI script until the Databricks workspace is successfully provisioned.
          text: az databricks workspace wait --resource-group MyResourceGroup --name MyWorkspace \\
                --created
"""

helps['databricks workspace vnet-peering'] = """
    type: group
    short-summary: Commands to manage databricks workspace vnet peering.
"""

helps['databricks workspace vnet-peering create'] = """
    type: command
    short-summary: Create a vnet peering for a workspace.
    examples:
      - name: Create a vnet peering for a workspace
        text: |-
               az databricks workspace vnet-peering create --resource-group MyResourceGroup --workspace-name MyWorkspace \\
               -n MyPeering --remote-vnet /subscriptions/000000-0000-0000/resourceGroups/MyRG/providers/Microsoft.Network/virtualNetworks/MyVNet
"""

helps['databricks workspace vnet-peering update'] = """
    type: command
    short-summary: Update the vnet peering.
    examples:
      - name: Update the vnet peering (enable gateway transit and disable virtual network access).
        text: |-
               az databricks workspace vnet-peering update --resource-group MyResourceGroup --workspace-name MyWorkspace \\
               -n MyPeering --allow-gateway-transit --allow-virtual-network-access false
"""

helps['databricks workspace vnet-peering list'] = """
    type: command
    short-summary: List vnet peerings under a workspace.
    examples:
      - name: List vnet peerings under a workspace.
        text: |-
               az databricks workspace vnet-peering list --resource-group MyResourceGroup --workspace-name MyWorkspace
"""

helps['databricks workspace vnet-peering delete'] = """
    type: command
    short-summary: Delete the vnet peering.
    examples:
      - name: Delete the vnet peering.
        text: |-
               az databricks workspace vnet-peering delete --resource-group MyResourceGroup --workspace-name MyWorkspace -n MyPeering
"""

helps['databricks workspace vnet-peering show'] = """
    type: command
    short-summary: Show the vnet peering.
    examples:
      - name: Show the vnet peering
        text: |-
               az databricks workspace vnet-peering show --resource-group MyResourceGroup --workspace-name MyWorkspace -n MyPeering
"""

helps['databricks workspace vnet-peering wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the Databricks workspace vnet peering is met.
    examples:
        - name: Pause executing next line of CLI script until the Databricks workspace vnet peering is successfully provisioned.
          text: az databricks workspace vnet-peering wait --resource-group MyResourceGroup --workspace-name MyWorkspace \\
                --name MyPeering --created
"""
