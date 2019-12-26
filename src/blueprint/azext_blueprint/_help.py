# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['blueprint'] = """
    type: group
    short-summary: Commands to manage blueprint.
"""

helps['blueprint create'] = """
    type: command
    short-summary: Create or update a blueprint definition.
    examples:
      - name: SubscriptionBlueprint
        text: |-
               az blueprint create --scope "subscriptions/00000000-0000-0000-0000-000000000000" --name \\
               "simpleBlueprint" --description \\
               "blueprint contains all artifact kinds {'template', 'rbac', 'policy'}" --target-scope \\
               "subscription"
      - name: ResourceGroupWithTags
        text: |-
               az blueprint create --scope \\
               "providers/Microsoft.Management/managementGroups/{ManagementGroupId}" --name \\
               "simpleBlueprint" --description "An example blueprint containing an RG with two tags." \\
               --target-scope "subscription"
      - name: ManagementGroupBlueprint
        text: |-
               az blueprint create --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --name \\
               "simpleBlueprint" --description \\
               "blueprint contains all artifact kinds {'template', 'rbac', 'policy'}" --target-scope \\
               "subscription"
"""

helps['blueprint update'] = """
    type: command
    short-summary: Create or update a blueprint definition.
"""

helps['blueprint delete'] = """
    type: command
    short-summary: Delete a blueprint definition.
    examples:
      - name: ManagementGroupBlueprint
        text: |-
               az blueprint delete --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --name \\
               "simpleBlueprint"
      - name: SubscriptionBlueprint
        text: |-
               az blueprint delete --scope "subscriptions/00000000-0000-0000-0000-000000000000" --name \\
               "simpleBlueprint"
"""

helps['blueprint show'] = """
    type: command
    short-summary: Get a blueprint definition.
    examples:
      - name: ManagementGroupBlueprint
        text: |-
               az blueprint show --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --name \\
               "simpleBlueprint"
      - name: SubscriptionBlueprint
        text: |-
               az blueprint show --scope "subscriptions/00000000-0000-0000-0000-000000000000" --name \\
               "simpleBlueprint"
"""

helps['blueprint list'] = """
    type: command
    short-summary: List blueprint definitions.
    examples:
      - name: ManagementGroupBlueprint
        text: |-
               az blueprint list --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup"
      - name: SubscriptionBlueprint
        text: |-
               az blueprint list --scope "subscriptions/00000000-0000-0000-0000-000000000000"
"""

helps['blueprint artifact'] = """
    type: group
    short-summary: Commands to manage blueprint artifact.
"""

helps['blueprint artifact create'] = """
    type: command
    short-summary: Create or update blueprint artifact.
    examples:
      - name: MG-RoleAssignmentArtifact
        text: |-
               az blueprint artifact create --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --name "ownerAssignment"
      - name: Sub-ARMTemplateArtifact
        text: |-
               az blueprint artifact create --scope "subscriptions/00000000-0000-0000-0000-000000000000" \\
               --blueprint-name "simpleBlueprint" --name "storageTemplate"
      - name: Sub-PolicyAssignmentArtifact
        text: |-
               az blueprint artifact create --scope "subscriptions/00000000-0000-0000-0000-000000000000" \\
               --blueprint-name "simpleBlueprint" --name "costCenterPolicy"
      - name: Sub-RoleAssignmentArtifact
        text: |-
               az blueprint artifact create --scope "subscriptions/00000000-0000-0000-0000-000000000000" \\
               --blueprint-name "simpleBlueprint" --name "ownerAssignment"
      - name: MG-ARMTemplateArtifact
        text: |-
               az blueprint artifact create --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --name "storageTemplate"
      - name: MG-PolicyAssignmentArtifact
        text: |-
               az blueprint artifact create --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --name "costCenterPolicy"
"""

helps['blueprint artifact update'] = """
    type: command
    short-summary: Create or update blueprint artifact.
"""

helps['blueprint artifact delete'] = """
    type: command
    short-summary: Delete a blueprint artifact.
    examples:
      - name: MG-RoleAssignmentArtifact
        text: |-
               az blueprint artifact delete --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --name "ownerAssignment"
      - name: Sub-ARMTemplateArtifact
        text: |-
               az blueprint artifact delete --scope "subscriptions/00000000-0000-0000-0000-000000000000" \\
               --blueprint-name "simpleBlueprint" --name "storageTemplate"
      - name: Sub-PolicyAssignmentArtifact
        text: |-
               az blueprint artifact delete --scope "subscriptions/00000000-0000-0000-0000-000000000000" \\
               --blueprint-name "simpleBlueprint" --name "costCenterPolicy"
      - name: Sub-RoleAssignmentArtifact
        text: |-
               az blueprint artifact delete --scope "subscriptions/00000000-0000-0000-0000-000000000000" \\
               --blueprint-name "simpleBlueprint" --name "ownerAssignment"
      - name: MG-ARMTemplateArtifact
        text: |-
               az blueprint artifact delete --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --name "storageTemplate"
      - name: MG-PolicyAssignmentArtifact
        text: |-
               az blueprint artifact delete --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --name "costCenterPolicy"
"""

helps['blueprint artifact show'] = """
    type: command
    short-summary: Get a blueprint artifact.
    examples:
      - name: Sub-RoleAssignmentArtifact
        text: |-
               az blueprint artifact show --scope "subscriptions/00000000-0000-0000-0000-000000000000" \\
               --blueprint-name "simpleBlueprint" --name "ownerAssignment"
      - name: MG-ARMTemplateArtifact
        text: |-
               az blueprint artifact show --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --name "storageTemplate"
      - name: Sub-ARMTemplateArtifact
        text: |-
               az blueprint artifact show --scope "subscriptions/00000000-0000-0000-0000-000000000000" \\
               --blueprint-name "simpleBlueprint" --name "storageTemplate"
      - name: Sub-PolicyAssignmentArtifact
        text: |-
               az blueprint artifact show --scope "subscriptions/00000000-0000-0000-0000-000000000000" \\
               --blueprint-name "simpleBlueprint" --name "costCenterPolicy"
      - name: MG-PolicyAssignmentArtifact
        text: |-
               az blueprint artifact show --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --name "costCenterPolicy"
      - name: MG-RoleAssignmentArtifact
        text: |-
               az blueprint artifact show --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --name "ownerAssignment"
"""

helps['blueprint artifact list'] = """
    type: command
    short-summary: List artifacts for a given blueprint definition.
    examples:
      - name: MG-ArtifactList
        text: |-
               az blueprint artifact list --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint"
      - name: Sub-ArtifactList
        text: |-
               az blueprint artifact list --scope "subscriptions/00000000-0000-0000-0000-000000000000" \\
               --blueprint-name "simpleBlueprint"
"""

helps['blueprint published'] = """
    type: group
    short-summary: Commands to manage blueprint published.
"""

helps['blueprint published create'] = """
    type: command
    short-summary: Publish a new version of the blueprint definition with the latest artifacts. Published blueprint definitions are immutable.
    examples:
      - name: PublishedManagementGroupBlueprint_Publish
        text: |-
               az blueprint published create --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --name \\
               "simpleBlueprint" --version-id "v2"
      - name: PublishedSubscriptionBlueprint_Publish
        text: |-
               az blueprint published create --scope \\
               "subscriptions/00000000-0000-0000-0000-000000000000" --name "simpleBlueprint" \\
               --version-id "v2"
"""

helps['blueprint published update'] = """
    type: command
    short-summary: Publish a new version of the blueprint definition with the latest artifacts. Published blueprint definitions are immutable.
"""

helps['blueprint published delete'] = """
    type: command
    short-summary: Delete a published version of a blueprint definition.
    examples:
      - name: PublishedSubscriptionBlueprint
        text: |-
               az blueprint published delete --scope \\
               "subscriptions/00000000-0000-0000-0000-000000000000" --name "simpleBlueprint" \\
               --version-id "v2"
      - name: PublishedManagementGroupBlueprint
        text: |-
               az blueprint published delete --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --name \\
               "simpleBlueprint" --version-id "v2"
"""

helps['blueprint published show'] = """
    type: command
    short-summary: Get a published version of a blueprint definition.
    examples:
      - name: PublishedManagementGroupBlueprint
        text: |-
               az blueprint published show --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --name \\
               "simpleBlueprint" --version-id "v2"
      - name: PublishedSubscriptionBlueprint
        text: |-
               az blueprint published show --scope "subscriptions/00000000-0000-0000-0000-000000000000" \\
               --name "simpleBlueprint" --version-id "v2"
"""

helps['blueprint published list'] = """
    type: command
    short-summary: List published versions of given blueprint definition.
    examples:
      - name: PublishedManagementGroupBlueprint
        text: |-
               az blueprint published list --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --name \\
               "simpleBlueprint"
      - name: PublishedSubscriptionBlueprint
        text: |-
               az blueprint published list --scope "subscriptions/00000000-0000-0000-0000-000000000000" \\
               --name "simpleBlueprint"
"""

helps['blueprint published artifact'] = """
    type: group
    short-summary: Commands to manage blueprint published artifact.
"""

helps['blueprint published artifact get'] = """
    type: command
    short-summary: Get an artifact for a published blueprint definition.
    examples:
      - name: Sub-ARMTemplateArtifact
        text: |-
               az blueprint published artifact get --scope \\
               "subscriptions/00000000-0000-0000-0000-000000000000" --blueprint-name "simpleBlueprint" \\
               --version-id "V2" --name "storageTemplate"
      - name: MG-RoleAssignmentArtifact
        text: |-
               az blueprint published artifact get --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --version-id "V2" --name "ownerAssignment"
      - name: Sub-PolicyAssignmentArtifact
        text: |-
               az blueprint published artifact get --scope \\
               "subscriptions/00000000-0000-0000-0000-000000000000" --blueprint-name "simpleBlueprint" \\
               --version-id "V2" --name "costCenterPolicy"
      - name: Sub-RoleAssignmentArtifact
        text: |-
               az blueprint published artifact get --scope \\
               "subscriptions/00000000-0000-0000-0000-000000000000" --blueprint-name "simpleBlueprint" \\
               --version-id "V2" --name "ownerAssignment"
      - name: MG-ARMTemplateArtifact
        text: |-
               az blueprint published artifact get --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --version-id "V2" --name "storageTemplate"
      - name: MG-PolicyAssignmentArtifact
        text: |-
               az blueprint published artifact get --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --version-id "V2" --name "costCenterPolicy"
"""

helps['blueprint published artifact list'] = """
    type: command
    short-summary: List artifacts for a version of a published blueprint definition.
    examples:
      - name: MG-ArtifactList
        text: |-
               az blueprint published artifact list --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --version-id "V2"
      - name: Sub-ArtifactList
        text: |-
               az blueprint published artifact list --scope \\
               "subscriptions/00000000-0000-0000-0000-000000000000" --blueprint-name "simpleBlueprint" \\
               --version-id "V2"
"""

helps['blueprint'] = """
    type: group
    short-summary: Commands to manage blueprint.
"""

helps['blueprint create'] = """
    type: command
    short-summary: Create or update a blueprint assignment.
    examples:
      - name: Assignment with system-assigned managed identity
        text: |-
               az blueprint create --scope "subscriptions/00000000-0000-0000-0000-000000000000" --name \\
               "assignSimpleBlueprint" --location "eastus" --identity-type "SystemAssigned" \\
               --description "enforce pre-defined simpleBlueprint to this XXXXXXXX subscription." \\
               --blueprint-id "/providers/Microsoft.Management/managementGroups/ContosoOnlineGroup/provid
               ers/Microsoft.Blueprint/blueprints/simpleBlueprint"
      - name: Assignment with user-assigned managed identity
        text: |-
               az blueprint create --scope "subscriptions/00000000-0000-0000-0000-000000000000" --name \\
               "assignSimpleBlueprint" --location "eastus" --identity-type "UserAssigned" --description \\
               "enforce pre-defined simpleBlueprint to this XXXXXXXX subscription." --blueprint-id "/prov
               iders/Microsoft.Management/managementGroups/ContosoOnlineGroup/providers/Microsoft.Bluepri
               nt/blueprints/simpleBlueprint"
"""

helps['blueprint update'] = """
    type: command
    short-summary: Create or update a blueprint assignment.
"""

helps['blueprint delete'] = """
    type: command
    short-summary: Delete a blueprint assignment.
    examples:
      - name: Assignment_Delete
        text: |-
               az blueprint delete --scope "subscriptions/00000000-0000-0000-0000-000000000000" --name \\
               "assignSimpleBlueprint"
"""

helps['blueprint show'] = """
    type: command
    short-summary: Get a blueprint assignment.
    examples:
      - name: Assignment
        text: |-
               az blueprint show --scope "subscriptions/00000000-0000-0000-0000-000000000000" --name \\
               "assignSimpleBlueprint"
"""

helps['blueprint list'] = """
    type: command
    short-summary: List blueprint assignments within a subscription.
    examples:
      - name: Assignment
        text: |-
               az blueprint list --scope "subscriptions/00000000-0000-0000-0000-000000000000"
"""

helps['blueprint who_is_blueprint'] = """
    type: command
    short-summary: Get Blueprints service SPN objectId
    examples:
      - name: WhoIsBlueprint_Action
        text: |-
               az blueprint who_is_blueprint --scope \\
               "subscriptions/00000000-0000-0000-0000-000000000000" --name "assignSimpleBlueprint"
"""
