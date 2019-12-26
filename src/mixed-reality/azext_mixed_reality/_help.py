# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['mixed-reality'] = """
    type: group
    short-summary: Commands to manage mixed reality.
"""

helps['mixed-reality list'] = """
    type: command
    short-summary: Exposing Available Operations
    examples:
      - name: OperationList
        text: |-
               az mixed-reality list
"""

helps['mixed-reality check-name-availability'] = """
    type: group
    short-summary: Commands to manage mixed reality check name availability.
"""

helps['mixed-reality check-name-availability check_name_availability_local'] = """
    type: command
    short-summary: Check Name Availability for global uniqueness
    examples:
      - name: CheckLocalNameAvailability
        text: |-
               az mixed-reality check-name-availability check_name_availability_local --location \\
               "Global"
"""

helps['mixed-reality'] = """
    type: group
    short-summary: Commands to manage mixed reality.
"""

helps['mixed-reality create'] = """
    type: command
    short-summary: Creating or Updating a Spatial Anchors Account.
    examples:
      - name: ResourceCreate
        text: |-
               az mixed-reality create --resource-group "mrsecf" --name "alpha" --location "Global"
"""

helps['mixed-reality update'] = """
    type: command
    short-summary: Creating or Updating a Spatial Anchors Account.
    examples:
      - name: ResourceCreateOrUpdate
        text: |-
               az mixed-reality update --resource-group "mrsecf" --name "alpha"
"""

helps['mixed-reality delete'] = """
    type: command
    short-summary: Delete a Spatial Anchors Account.
    examples:
      - name: ResourceDelete
        text: |-
               az mixed-reality delete --resource-group "mrsecf" --name "alpha"
"""

helps['mixed-reality show'] = """
    type: command
    short-summary: Retrieve a Spatial Anchors Account.
    examples:
      - name: ResourceGet
        text: |-
               az mixed-reality show --resource-group "mrsecf" --name "alpha"
"""

helps['mixed-reality list'] = """
    type: command
    short-summary: List Resources by Resource Group
    examples:
      - name: SpatialAnchorsAccountListBySubscription
        text: |-
               az mixed-reality list
      - name: ResourceGet
        text: |-
               az mixed-reality list --resource-group "mrsecf"
"""

helps['mixed-reality regenerate_keys'] = """
    type: command
    short-summary: Regenerate 1 Key of a Spatial Anchors Account
    examples:
      - name: ResourceRegenerateKey
        text: |-
               az mixed-reality regenerate_keys --resource-group "mrsecf" --name "alpha"
"""

helps['mixed-reality get_keys'] = """
    type: command
    short-summary: Get Both of the 2 Keys of a Spatial Anchors Account
    examples:
      - name: ResourceRegenerateKey
        text: |-
               az mixed-reality get_keys --resource-group "mrsecf" --name "alpha"
"""
