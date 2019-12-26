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
      - name: OperationPage
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
               --location "Global"
"""

helps['mixed-reality remote-rendering-account'] = """
    type: group
    short-summary: Commands to manage mixed reality remote rendering account.
"""

helps['mixed-reality remote-rendering-account create'] = """
    type: command
    short-summary: Creating or Updating a Remote Rendering Account.
    examples:
      - name: ResourceCreate
        text: |-
               az mixed-reality remote-rendering-account create --resource-group "mrsecf" --name "alpha" \\
               --location "EastUs2"
"""

helps['mixed-reality remote-rendering-account update'] = """
    type: command
    short-summary: Creating or Updating a Remote Rendering Account.
    examples:
      - name: ResourceCreateOrUpdate
        text: |-
               az mixed-reality remote-rendering-account update --resource-group "mrsecf" --name "alpha"
"""

helps['mixed-reality remote-rendering-account delete'] = """
    type: command
    short-summary: Delete a Remote Rendering Account.
    examples:
      - name: ResourceDelete
        text: |-
               az mixed-reality remote-rendering-account delete --resource-group "mrsecf" --name "alpha"
"""

helps['mixed-reality remote-rendering-account show'] = """
    type: command
    short-summary: Retrieve a Remote Rendering Account.
    examples:
      - name: ResourceGet
        text: |-
               az mixed-reality remote-rendering-account show --resource-group "mrsecf" --name "alpha"
"""

helps['mixed-reality remote-rendering-account list'] = """
    type: command
    short-summary: List Resources by Resource Group
    examples:
      - name: RemoteRenderingAccountPageBySubscription
        text: |-
               az mixed-reality remote-rendering-account list
      - name: ResourceGet
        text: |-
               az mixed-reality remote-rendering-account list --resource-group "mrsecf"
"""

helps['mixed-reality remote-rendering-account regenerate_keys'] = """
    type: command
    short-summary: Regenerate specified Key of a Remote Rendering Account
    examples:
      - name: ResourceRegenerateKey
        text: |-
               az mixed-reality remote-rendering-account regenerate_keys --resource-group "mrsecf" \\
               --name "alpha"
"""

helps['mixed-reality remote-rendering-account get_keys'] = """
    type: command
    short-summary: Get Both of the 2 Keys of a Remote Rendering Account
    examples:
      - name: ResourceGetKey
        text: |-
               az mixed-reality remote-rendering-account get_keys --resource-group "mrsecf" --name \\
               "alpha"
"""

helps['mixed-reality spatial-anchors-account'] = """
    type: group
    short-summary: Commands to manage mixed reality spatial anchors account.
"""

helps['mixed-reality spatial-anchors-account create'] = """
    type: command
    short-summary: Creating or Updating a Spatial Anchors Account.
    examples:
      - name: ResourceCreate
        text: |-
               az mixed-reality spatial-anchors-account create --resource-group "mrsecf" --name "alpha" \\
               --location "EastUs2"
"""

helps['mixed-reality spatial-anchors-account update'] = """
    type: command
    short-summary: Creating or Updating a Spatial Anchors Account.
    examples:
      - name: ResourceCreateOrUpdate
        text: |-
               az mixed-reality spatial-anchors-account update --resource-group "mrsecf" --name "alpha"
"""

helps['mixed-reality spatial-anchors-account delete'] = """
    type: command
    short-summary: Delete a Spatial Anchors Account.
    examples:
      - name: ResourceDelete
        text: |-
               az mixed-reality spatial-anchors-account delete --resource-group "mrsecf" --name "alpha"
"""

helps['mixed-reality spatial-anchors-account show'] = """
    type: command
    short-summary: Retrieve a Spatial Anchors Account.
    examples:
      - name: ResourceGet
        text: |-
               az mixed-reality spatial-anchors-account show --resource-group "mrsecf" --name "alpha"
"""

helps['mixed-reality spatial-anchors-account list'] = """
    type: command
    short-summary: List Resources by Resource Group
    examples:
      - name: SpatialAnchorsAccountPageBySubscription
        text: |-
               az mixed-reality spatial-anchors-account list
      - name: ResourceGet
        text: |-
               az mixed-reality spatial-anchors-account list --resource-group "mrsecf"
"""

helps['mixed-reality spatial-anchors-account regenerate_keys'] = """
    type: command
    short-summary: Regenerate specified Key of a Spatial Anchors Account
    examples:
      - name: ResourceRegenerateKey
        text: |-
               az mixed-reality spatial-anchors-account regenerate_keys --resource-group "mrsecf" --name \\
               "alpha"
"""

helps['mixed-reality spatial-anchors-account get_keys'] = """
    type: command
    short-summary: Get Both of the 2 Keys of a Spatial Anchors Account
    examples:
      - name: ResourceGetKey
        text: |-
               az mixed-reality spatial-anchors-account get_keys --resource-group "mrsecf" --name \\
               "alpha"
"""
