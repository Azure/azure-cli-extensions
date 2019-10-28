# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['managednetwork'] = """
    type: group
    short-summary: Commands to manage managed network.
"""

helps['managednetwork create'] = """
    type: command
    short-summary: create managed network.
    examples:
      - name: ManagedNetworksPut
        text: |-
               az managednetwork create --resource-group "myResourceGroup" --name "myManagedNetwork" \\
               --location "eastus"
"""

helps['managednetwork update'] = """
    type: command
    short-summary: update managed network.
    examples:
      - name: ManagedNetworksPatch
        text: |-
               az managednetwork update --resource-group "myResourceGroup" --name "myManagedNetwork"
"""

helps['managednetwork delete'] = """
    type: command
    short-summary: delete managed network.
    examples:
      - name: ManagedNetworksDelete
        text: |-
               az managednetwork delete --resource-group "myResourceGroup" --name "myManagedNetwork"
"""

helps['managednetwork list'] = """
    type: command
    short-summary: list managed network.
"""

helps['managednetwork show'] = """
    type: command
    short-summary: show managed network.
"""

helps['managednetwork scope-assignment'] = """
    type: group
    short-summary: Commands to manage scope assignment.
"""

helps['managednetwork scope-assignment create'] = """
    type: command
    short-summary: create scope assignment.
    examples:
      - name: ScopeAssignmentsPut
        text: |-
               az managednetwork scope-assignment create --scope "/subscriptions/{{ subscription_id }}" \\
               --name "subscriptionCAssignment"
"""

helps['managednetwork scope-assignment update'] = """
    type: command
    short-summary: update scope assignment.
"""

helps['managednetwork scope-assignment delete'] = """
    type: command
    short-summary: delete scope assignment.
    examples:
      - name: ScopeAssignmentsDelete
        text: |-
               az managednetwork scope-assignment delete --scope "/subscriptions/{{ subscription_id }}" \\
               --name "subscriptionCAssignment"
"""

helps['managednetwork scope-assignment list'] = """
    type: command
    short-summary: list scope assignment.
"""

helps['managednetwork scope-assignment show'] = """
    type: command
    short-summary: show scope assignment.
"""

helps['managednetwork group'] = """
    type: group
    short-summary: Commands to manage managed network group.
"""

helps['managednetwork group create'] = """
    type: command
    short-summary: create managed network group.
    examples:
      - name: ManagementNetworkGroupsPut
        text: |-
               az managednetwork group create --resource-group "myResourceGroup" \\
               --managed-network-name "myManagedNetwork" --name "myManagedNetworkGroup1"
"""

helps['managednetwork group update'] = """
    type: command
    short-summary: update managed network group.
"""

helps['managednetwork group delete'] = """
    type: command
    short-summary: delete managed network group.
    examples:
      - name: ManagementNetworkGroupsDelete
        text: |-
               az managednetwork group delete --resource-group "myResourceGroup" \\
               --managed-network-name "myManagedNetwork" --name "myManagedNetworkGroup1"
"""

helps['managednetwork group list'] = """
    type: command
    short-summary: list managed network group.
"""

helps['managednetwork group show'] = """
    type: command
    short-summary: show managed network group.
"""

helps['managednetwork peering-policy'] = """
    type: group
    short-summary: Commands to manage managed network peering policy.
"""

helps['managednetwork peering-policy create'] = """
    type: command
    short-summary: create managed network peering policy.
    examples:
      - name: ManagedNetworkPeeringPoliciesPut
        text: |-
               az managednetwork peering-policy create --resource-group \\
               "myResourceGroup" --managed-network-name "myManagedNetwork" --name "myHubAndSpoke" \\
               --type XXX
"""

helps['managednetwork peering-policy update'] = """
    type: command
    short-summary: update managed network peering policy.
"""

helps['managednetwork peering-policy delete'] = """
    type: command
    short-summary: delete managed network peering policy.
    examples:
      - name: ManagedNetworkPeeringPoliciesDelete
        text: |-
               az managednetwork peering-policy delete --resource-group \\
               "myResourceGroup" --managed-network-name "myManagedNetwork" --name "myHubAndSpoke"
"""

helps['managednetwork peering-policy list'] = """
    type: command
    short-summary: list managed network peering policy.
"""

helps['managednetwork peering-policy show'] = """
    type: command
    short-summary: show managed network peering policy.
"""

helps['managednetwork'] = """
    type: group
    short-summary: Commands to manage operation.
"""

helps['managednetwork list'] = """
    type: command
    short-summary: list operation.
"""
