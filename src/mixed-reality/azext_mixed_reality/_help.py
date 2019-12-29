# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['mixed-reality operation'] = """
    type: group
    short-summary: Commands to manage mixed reality operation.
"""

helps['mixed-reality operation list'] = """
    type: command
    short-summary: Exposing Available Operations
    examples:
      - name: List available operations
        text: |-
               az mixed-reality operation list
"""

helps['mixed-reality location check-name-availability'] = """
    type: group
    short-summary: Commands to manage mixed reality location check name availability.
"""

helps['mixed-reality location check-name-availability check_name_availability_local'] = """
    type: command
    short-summary: Check Name Availability for local uniqueness
    examples:
      - name: CheckLocalNameAvailability
        text: |-
               az mixed-reality location check-name-availability check_name_availability_local \\
               --location "eastus2euap"
"""

helps['mixed-reality remote-rendering-account'] = """
    type: group
    short-summary: Commands to manage mixed reality remote rendering account.
"""

helps['mixed-reality remote-rendering-account create'] = """
    type: command
    short-summary: Creating or Updating a Remote Rendering Account.
    examples:
      - name: Create remote rendering account
        text: |-
               az mixed-reality remote-rendering-account create --resource-group "MyResourceGroup" \\
               --name "MyAccountName" --location "eastus2euap"
"""

helps['mixed-reality remote-rendering-account update'] = """
    type: command
    short-summary: Creating or Updating a Remote Rendering Account.
    examples:
      - name: Update remote rendering account
        text: |-
               az mixed-reality remote-rendering-account update --resource-group "MyResourceGroup" \\
               --name "MyAccount"
"""

helps['mixed-reality remote-rendering-account delete'] = """
    type: command
    short-summary: Delete a Remote Rendering Account.
    examples:
      - name: Delete remote rendering account
        text: |-
               az mixed-reality remote-rendering-account delete --resource-group "MyResourceGroup" \\
               --name "MyAccount"
"""

helps['mixed-reality remote-rendering-account show'] = """
    type: command
    short-summary: Retrieve a Remote Rendering Account.
    examples:
      - name: Get remote rendering account
        text: |-
               az mixed-reality remote-rendering-account show --resource-group "MyResourceGroup" --name \\
               "MyAccount"
"""

helps['mixed-reality remote-rendering-account list'] = """
    type: command
    short-summary: List Resources by Resource Group
    examples:
      - name: List remote rendering accounts by subscription
        text: |-
               az mixed-reality remote-rendering-account list
      - name: List remote rendering accounts by resource group
        text: |-
               az mixed-reality remote-rendering-account list --resource-group "MyResourceGroup"
"""

helps['mixed-reality remote-rendering-account regenerate_keys'] = """
    type: command
    short-summary: Regenerate specified Key of a Remote Rendering Account
    examples:
      - name: Regenerate remote rendering account keys
        text: |-
               az mixed-reality remote-rendering-account regenerate_keys --resource-group \\
               "MyResourceGroup" --name "MyAccount"
"""

helps['mixed-reality remote-rendering-account get_keys'] = """
    type: command
    short-summary: Get Both of the 2 Keys of a Remote Rendering Account
    examples:
      - name: Get remote rendering account key
        text: |-
               az mixed-reality remote-rendering-account get_keys --resource-group "MyResourceGroup" \\
               --name "MyAccount"
"""

helps['mixed-reality spatial-anchors-account'] = """
    type: group
    short-summary: Commands to manage mixed reality spatial anchors account.
"""

helps['mixed-reality spatial-anchors-account create'] = """
    type: command
    short-summary: Creating or Updating a Spatial Anchors Account.
    examples:
      - name: Create spatial anchor account
        text: |-
               az mixed-reality spatial-anchors-account create --resource-group "MyResourceGroup" --name \\
               "MyAccount" --location "eastus2euap"
"""

helps['mixed-reality spatial-anchors-account update'] = """
    type: command
    short-summary: Creating or Updating a Spatial Anchors Account.
    examples:
      - name: Update spatial anchors account
        text: |-
               az mixed-reality spatial-anchors-account update --resource-group "MyResourceGroup" --name \\
               "MyAccount"
"""

helps['mixed-reality spatial-anchors-account delete'] = """
    type: command
    short-summary: Delete a Spatial Anchors Account.
    examples:
      - name: Delete spatial anchors account
        text: |-
               az mixed-reality spatial-anchors-account delete --resource-group "MyResourceGroup" --name \\
               "MyAccount"
"""

helps['mixed-reality spatial-anchors-account show'] = """
    type: command
    short-summary: Retrieve a Spatial Anchors Account.
    examples:
      - name: Get spatial anchor accounts
        text: |-
               az mixed-reality spatial-anchors-account show --resource-group "MyResourceGroup" --name \\
               "MyAccount"
"""

helps['mixed-reality spatial-anchors-account list'] = """
    type: command
    short-summary: List Resources by Resource Group
    examples:
      - name: List spatial anchors accounts by subscription
        text: |-
               az mixed-reality spatial-anchors-account list
      - name: List spatial anchor accounts by resource group
        text: |-
               az mixed-reality spatial-anchors-account list --resource-group "MyResourceGroup"
"""

helps['mixed-reality spatial-anchors-account regenerate_keys'] = """
    type: command
    short-summary: Regenerate specified Key of a Spatial Anchors Account
    examples:
      - name: Regenerate spatial anchors account keys
        text: |-
               az mixed-reality spatial-anchors-account regenerate_keys --resource-group \\
               "MyResourceGroup" --name "MyAccount"
"""

helps['mixed-reality spatial-anchors-account get_keys'] = """
    type: command
    short-summary: Get Both of the 2 Keys of a Spatial Anchors Account
    examples:
      - name: Get spatial anchor account key
        text: |-
               az mixed-reality spatial-anchors-account get_keys --resource-group "MyResourceGroup" \\
               --name "MyAccount"
"""
