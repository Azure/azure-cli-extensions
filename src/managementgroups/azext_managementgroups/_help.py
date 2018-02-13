# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

# pylint: disable=line-too-long, too-many-lines

helps['account management-group'] = """
    type: group
    short-summary: Manage Azure Management Groups.
"""

helps['account management-group subscription'] = """
    type: group
    short-summary: Subscription operations for Management Groups.
"""

helps['account management-group list'] = """
    type: command
    short-summary: List all management groups.
    long-summary: List of all management groups in the current tenant.
    examples:
        - name: List all management groups
          text: >
             az managementgroups group list
"""

helps['account management-group show'] = """
    type: command
    short-summary: Get a specific management group.
    long-summary: Get the details of the management group.
    parameters:
        - name: --group-name --name -n
          type: string
          short-summary: Name of the management group.
        - name: --expand -e
          type: bool
          short-summary: If given or true, lists the children in the first level of hierarchy.
        - name: --recurse -r
          type: bool
          short-summary: If given or true, lists the children in all levels of hierarchy.
    examples:
        - name: Get a management group.
          text: >
             az managementgroups group get --group-name GroupName
        - name: Get a management group with children in the first level of hierarchy.
          text: >
             az managementgroups group get --group-name GroupName -e
        - name: Get a management group with children in all levels of hierarchy.
          text: >
             az managementgroups group get --group-name GroupName -e -r
"""

helps['account management-group create'] = """
    type: command
    short-summary: Add a new management group.
    long-summary: Add a new management group.
    parameters:
        - name: --group-name --name -n
          type: string
          short-summary: Name of the management group.
        - name: --display-name -d
          type: string
          short-summary: Sets the display name of the management group. If null, the group name is set as the display name.
        - name: --parent-id -p
          type: string
          short-summary: Sets the parent of the management group. A fully qualified id is required. If null, the root tenant group is set as the parent.
    examples:
        - name: Add a new management group.
          text: >
             az managementgroups group new --group-name GroupName
        - name: Add a new management group with a specific display name.
          text: >
             az managementgroups group new --group-name GroupName --display-name DisplayName
        - name: Add a new management group with a specific parent id.
          text: >
             az managementgroups group new --group-name GroupName --parent-id ParentId
        - name: Add a new management group with a specific display name and parent id.
          text: >
             az managementgroups group new --group-name GroupName --display-name DisplayName --parent-id ParentId
"""

helps['account management-group update'] = """
    type: command
    short-summary: Update an existing management group.
    long-summary: Update an existing management group.
    parameters:
        - name: --group-name --name -n
          type: string
          short-summary: Name of the management group.
        - name: --display-name -d
          type: string
          short-summary: Updates the display name of the management group. If null, no change is made.
        - name: --parent-id -p
          type: string
          short-summary: Update the parent of the management group. A fully qualified id is required. If null, no change is made.
    examples:
        - name: Update an existing management group with a specific display name.
          text: >
             az managementgroups group update --group-name GroupName --display-name DisplayName
        - name: Update an existing management group with a specific parent id.
          text: >
             az managementgroups group update --group-name GroupName --parent-id ParentId
        - name: Update an existing management group with a specific display name and parent id.
          text: >
             az managementgroups group update --group-name GroupName --display-name DisplayName --parent-id ParentId
"""

helps['account management-group delete'] = """
    type: command
    short-summary: Remove an existing management group.
    long-summary: Remove an existing management group.
    parameters:
        - name: --group-name --name -n
          type: string
          short-summary: Name of the management group.
    examples:
        - name: Remove an existing management group
          text: >
             az managementgroups group remove --group-name GroupName
"""

helps['account management-group subscription add'] = """
    type: command
    short-summary: Add a subscription to a management group.
    long-summary: Add a subscription to a management group.
    parameters:
        - name: --group-name --name -n
          type: string
          short-summary: Name of the management group.
        - name: --subscription
          type: string
          short-summary: Subscription Id or Name
    examples:
        - name: Add a subscription to a management group.
          text: >
             az managementgroups group new --group-name GroupName --subscription Subscription
"""

helps['account management-group subscription remove'] = """
    type: command
    short-summary: Remove an existing subscription from a management group.
    long-summary: Remove an existing subscription from a management group.
    parameters:
        - name: --group-name --name -n
          type: string
          short-summary: Name of the management group.
        - name: --subscription
          type: string
          short-summary: Subscription Id or Name
    examples:
        - name: Remove an existing subscription from a management group.
          text: >
             az managementgroups group remove --group-name GroupName --subscription Subscription
"""
