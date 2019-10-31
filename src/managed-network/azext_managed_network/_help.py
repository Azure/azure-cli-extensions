# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['managed-network'] = """
    type: group
    short-summary: Commands to manage managed network.
"""

helps['managed-network create'] = """
    type: command
    short-summary: create managed network.
    examples:
      - name: ManagedNetworksPut
        text: |-
               az managed-network create --resource-group "myResourceGroup" --name "myManagedNetwork" \\
               --location "eastus"
"""

helps['managed-network update'] = """
    type: command
    short-summary: update managed network.
    examples:
      - name: ManagedNetworksPatch
        text: |-
               az managed-network update --resource-group "myResourceGroup" --name "myManagedNetwork"
"""

helps['managed-network delete'] = """
    type: command
    short-summary: delete managed network.
    examples:
      - name: ManagedNetworksDelete
        text: |-
               az managed-network delete --resource-group "myResourceGroup" --name "myManagedNetwork"
"""

helps['managed-network list'] = """
    type: command
    short-summary: list managed network.
"""

helps['managed-network show'] = """
    type: command
    short-summary: show managed network.
"""

helps['managed-network scope-assignment'] = """
    type: group
    short-summary: Commands to manage scope assignment.
"""

helps['managed-network scope-assignment create'] = """
    type: command
    short-summary: create scope assignment.
    examples:
      - name: ScopeAssignmentsPut
        text: |-
               az managed-network scope-assignment create --scope "subscriptions/subscriptionC" --name \\
               "subscriptionCAssignment"
"""

helps['managed-network scope-assignment update'] = """
    type: command
    short-summary: update scope assignment.
"""

helps['managed-network scope-assignment delete'] = """
    type: command
    short-summary: delete scope assignment.
    examples:
      - name: ScopeAssignmentsDelete
        text: |-
               az managed-network scope-assignment delete --scope "subscriptions/subscriptionC" --name \\
               "subscriptionCAssignment"
"""

helps['managed-network scope-assignment list'] = """
    type: command
    short-summary: list scope assignment.
"""

helps['managed-network scope-assignment show'] = """
    type: command
    short-summary: show scope assignment.
"""

helps['managed-network group'] = """
    type: group
    short-summary: Commands to manage managed network group.
"""

helps['managed-network group create'] = """
    type: command
    short-summary: create managed network group.
    examples:
      - name: ManagementNetworkGroupsPut
        text: |-
               az managed-network group create --resource-group "myResourceGroup" --managed-network-name \\
               "myManagedNetwork" --name "myManagedNetworkGroup1"
"""

helps['managed-network group update'] = """
    type: command
    short-summary: update managed network group.
"""

helps['managed-network group delete'] = """
    type: command
    short-summary: delete managed network group.
    examples:
      - name: ManagementNetworkGroupsDelete
        text: |-
               az managed-network group delete --resource-group "myResourceGroup" --managed-network-name \\
               "myManagedNetwork" --name "myManagedNetworkGroup1"
"""

helps['managed-network group list'] = """
    type: command
    short-summary: list managed network group.
"""

helps['managed-network group show'] = """
    type: command
    short-summary: show managed network group.
"""

helps['managed-network peering-policy'] = """
    type: group
    short-summary: Commands to manage managed network peering policy.
"""

helps['managed-network peering-policy create'] = """
    type: command
    short-summary: create managed network peering policy.
    examples:
      - name: ManagedNetworkPeeringPoliciesPut
        text: |-
               az managed-network peering-policy create --resource-group "myResourceGroup" \\
               --managed-network-name "myManagedNetwork" --name "myHubAndSpoke" \\
               --type XXX
"""

helps['managed-network peering-policy update'] = """
    type: command
    short-summary: update managed network peering policy.
"""

helps['managed-network peering-policy delete'] = """
    type: command
    short-summary: delete managed network peering policy.
    examples:
      - name: ManagedNetworkPeeringPoliciesDelete
        text: |-
               az managed-network peering-policy delete --resource-group "myResourceGroup" \\
               --managed-network-name "myManagedNetwork" --name "myHubAndSpoke"
"""

helps['managed-network peering-policy list'] = """
    type: command
    short-summary: list managed network peering policy.
"""

helps['managed-network peering-policy show'] = """
    type: command
    short-summary: show managed network peering policy.
"""

helps['managed-network'] = """
    type: group
    short-summary: Commands to manage operation.
"""

helps['managed-network list'] = """
    type: command
    short-summary: list operation.
"""
