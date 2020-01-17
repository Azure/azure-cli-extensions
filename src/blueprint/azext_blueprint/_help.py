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
    short-summary: Create a blueprint definition.
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
    short-summary: Update a blueprint definition.
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

helps['blueprint resource-group'] = """
    type: group
    short-summary: Commands to manage blueprint resource group artifact.
"""

helps['blueprint resource-group create'] = """
    type: command
    short-summary: Create blueprint resource group artifact.
    examples:
      - name: Create a resource group artifact
        text: |-
               az blueprint resource-group create --scope "subscriptions/{subscriptionId}" \\
               --blueprint-name "myBlueprint" --artifact-name "myRG"
"""

helps['blueprint resource-group update'] = """
    type: command
    short-summary: Update blueprint resource group artifact.
    examples:
      - name: Update a resource group artifact
        text: |-
               az blueprint resource-group update --scope "subscriptions/{subscriptionId}" \\
               --blueprint-name "myBlueprint" --artifact-name "myRG" --display-name "Updated name"
"""

helps['blueprint resource-group delete'] = """
    type: command
    short-summary: Delete blueprint resource group artifact.
    examples:
      - name: Delete a resource group artifact
        text: |-
               az blueprint resource-group delete --scope "subscriptions/{subscriptionId}" \\
               --blueprint-name "myBlueprint" --artifact-name "myRG"
"""

helps['blueprint resource-group show'] = """
    type: command
    short-summary: Show blueprint resource group artifact.
    examples:
      - name: Show a resource group artifact
        text: |-
               az blueprint resource-group show --scope "subscriptions/{subscriptionId}" \\
               --blueprint-name "myBlueprint" --artifact-name "myRG"
"""

helps['blueprint resource-group list'] = """
    type: command
    short-summary: List blueprint resource group artifact.
    examples:
      - name: List resource group artifacts
        text: |-
               az blueprint resource-group list --scope "subscriptions/{subscriptionId}" \\
               --blueprint-name "myBlueprint"
"""

helps['blueprint artifact'] = """
    type: group
    short-summary: Commands to manage blueprint artifact.
"""

helps['blueprint artifact delete'] = """
    type: command
    short-summary: Delete a blueprint artifact.
    examples:
      - name: MG-RoleAssignmentArtifact
        text: |-
               az blueprint artifact delete --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --artifact-name "ownerAssignment"
      - name: Sub-ARMTemplateArtifact
        text: |-
               az blueprint artifact delete --scope "subscriptions/00000000-0000-0000-0000-000000000000" \\
               --blueprint-name "simpleBlueprint" --artifact-name "storageTemplate"
      - name: Sub-PolicyAssignmentArtifact
        text: |-
               az blueprint artifact delete --scope "subscriptions/00000000-0000-0000-0000-000000000000" \\
               --blueprint-name "simpleBlueprint" --artifact-name "costCenterPolicy"
      - name: Sub-RoleAssignmentArtifact
        text: |-
               az blueprint artifact delete --scope "subscriptions/00000000-0000-0000-0000-000000000000" \\
               --blueprint-name "simpleBlueprint" --artifact-name "ownerAssignment"
      - name: MG-ARMTemplateArtifact
        text: |-
               az blueprint artifact delete --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --artifact-name "storageTemplate"
      - name: MG-PolicyAssignmentArtifact
        text: |-
               az blueprint artifact delete --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --artifact-name "costCenterPolicy"
"""

helps['blueprint artifact show'] = """
    type: command
    short-summary: Get a blueprint artifact.
    examples:
      - name: Sub-RoleAssignmentArtifact
        text: |-
               az blueprint artifact show --scope "subscriptions/00000000-0000-0000-0000-000000000000" \\
               --blueprint-name "simpleBlueprint" --artifact-name "ownerAssignment"
      - name: MG-ARMTemplateArtifact
        text: |-
               az blueprint artifact show --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --artifact-name "storageTemplate"
      - name: Sub-ARMTemplateArtifact
        text: |-
               az blueprint artifact show --scope "subscriptions/00000000-0000-0000-0000-000000000000" \\
               --blueprint-name "simpleBlueprint" --artifact-name "storageTemplate"
      - name: Sub-PolicyAssignmentArtifact
        text: |-
               az blueprint artifact show --scope "subscriptions/00000000-0000-0000-0000-000000000000" \\
               --blueprint-name "simpleBlueprint" --artifact-name "costCenterPolicy"
      - name: MG-PolicyAssignmentArtifact
        text: |-
               az blueprint artifact show --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --artifact-name "costCenterPolicy"
      - name: MG-RoleAssignmentArtifact
        text: |-
               az blueprint artifact show --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --artifact-name "ownerAssignment"
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

helps['blueprint artifact policy'] = """
    type: group
    short-summary: Commands to manage blueprint policy assignment artifact.
"""

helps['blueprint artifact policy create'] = """
    type: command
    short-summary: Create blueprint policy artifact.
    examples:
      - name: Create a policy artifact
        text: |-
               az blueprint artifact policy create --scope "subscriptions/{subscriptionId}" \\
               --blueprint-name "myBlueprint" --artifact-name "myPolicy" --policy-definition-id \\
               "/providers/Microsoft.Authorization/policyDefinitions/{policyId}" \\
               --parameters @/path/to/file --display-name "Policy to do sth"
"""

helps['blueprint artifact policy update'] = """
    type: command
    short-summary: Update blueprint policy artifact.
    examples:
      - name: Update a policy artifact
        text: |-
               az blueprint artifact policy update --scope "subscriptions/{subscriptionId}" \\
               --blueprint-name "myBlueprint" --artifact-name "myPolicy" --display-name "Updated Name"
"""

helps['blueprint artifact role'] = """
    type: group
    short-summary: Commands to manage blueprint role assignment artifact.
"""

helps['blueprint artifact role create'] = """
    type: command
    short-summary: Create blueprint role artifact.
    examples:
      - name: Create a role artifact
        text: |-
               az blueprint artifact role create --scope "subscriptions/{subscriptionId}" \\
               --blueprint-name "myBlueprint" --artifact-name "myRole" --role-definition-id \\
               "/providers/Microsoft.Authorization/roleDefinitions/{roleId}" \\
               --parameters @/path/to/file --principal-ids "pId"
"""

helps['blueprint artifact role update'] = """
    type: command
    short-summary: Update blueprint role artifact.
    examples:
      - name: Update a role artifact
        text: |-
               az blueprint artifact role update --scope "subscriptions/{subscriptionId}" \\
               --blueprint-name "myBlueprint" --artifact-name "myRole" --display-name "Updated Name"
"""

helps['blueprint artifact template'] = """
    type: group
    short-summary: Commands to manage blueprint ARM template artifact.
"""

helps['blueprint artifact template create'] = """
    type: command
    short-summary: Create blueprint arm artifact.
    examples:
      - name: Create an arm artifact
        text: |-
               az blueprint artifact template create --scope "subscriptions/{subscriptionId}" \\
               --blueprint-name "myBlueprint" --artifact-name "myTemplate" \\
               --parameters @/path/to/file --template @/path/to/template
"""

helps['blueprint artifact template update'] = """
    type: command
    short-summary: Update blueprint arm artifact.
    examples:
      - name: Update a arm artifact
        text: |-
               az blueprint artifact template update --scope "subscriptions/{subscriptionId}" \\
               --blueprint-name "myBlueprint" --artifact-name "myTemplate" --display-name "Updated Name"
"""

helps['blueprint published'] = """
    type: group
    short-summary: Commands to manage published blueprint.
"""

helps['blueprint published create'] = """
    type: command
    short-summary: Publish a new version of the blueprint definition with the latest artifacts. Published blueprint definitions are immutable.
    examples:
      - name: PublishedManagementGroupBlueprint_Publish
        text: |-
               az blueprint published create --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --name \\
               "simpleBlueprint" --version "v2"
      - name: PublishedSubscriptionBlueprint_Publish
        text: |-
               az blueprint published create --scope \\
               "subscriptions/00000000-0000-0000-0000-000000000000" --name "simpleBlueprint" \\
               --version "v2"
"""

helps['blueprint published delete'] = """
    type: command
    short-summary: Delete a published version of a blueprint definition.
    examples:
      - name: PublishedSubscriptionBlueprint
        text: |-
               az blueprint published delete --scope \\
               "subscriptions/00000000-0000-0000-0000-000000000000" --name "simpleBlueprint" \\
               --version "v2"
      - name: PublishedManagementGroupBlueprint
        text: |-
               az blueprint published delete --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --name \\
               "simpleBlueprint" --version "v2"
"""

helps['blueprint published show'] = """
    type: command
    short-summary: Get a published version of a blueprint definition.
    examples:
      - name: PublishedManagementGroupBlueprint
        text: |-
               az blueprint published show --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --name \\
               "simpleBlueprint" --version "v2"
      - name: PublishedSubscriptionBlueprint
        text: |-
               az blueprint published show --scope "subscriptions/00000000-0000-0000-0000-000000000000" \\
               --name "simpleBlueprint" --version "v2"
"""

helps['blueprint published list'] = """
    type: command
    short-summary: List published versions of given blueprint definition.
    examples:
      - name: PublishedManagementGroupBlueprint
        text: |-
               az blueprint published list --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint"
      - name: PublishedSubscriptionBlueprint
        text: |-
               az blueprint published list --scope "subscriptions/00000000-0000-0000-0000-000000000000" \\
               --blueprint-name "simpleBlueprint"
"""

helps['blueprint published artifact'] = """
    type: group
    short-summary: Commands to manage blueprint published artifact.
"""

helps['blueprint published artifact show'] = """
    type: command
    short-summary: Show an artifact for a published blueprint definition.
    examples:
      - name: Sub-ARMTemplateArtifact
        text: |-
               az blueprint published artifact show --scope \\
               "subscriptions/00000000-0000-0000-0000-000000000000" --blueprint-name "simpleBlueprint" \\
               --version "V2" --artifact-name "storageTemplate"
      - name: MG-RoleAssignmentArtifact
        text: |-
               az blueprint published artifact show --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --version "V2" --artifact-name "ownerAssignment"
      - name: Sub-PolicyAssignmentArtifact
        text: |-
               az blueprint published artifact show --scope \\
               "subscriptions/00000000-0000-0000-0000-000000000000" --blueprint-name "simpleBlueprint" \\
               --version "V2" --artifact-name "costCenterPolicy"
      - name: Sub-RoleAssignmentArtifact
        text: |-
               az blueprint published artifact show --scope \\
               "subscriptions/00000000-0000-0000-0000-000000000000" --blueprint-name "simpleBlueprint" \\
               --version "V2" --artifact-name "ownerAssignment"
      - name: MG-ARMTemplateArtifact
        text: |-
               az blueprint published artifact show --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --version "V2" --artifact-name "storageTemplate"
      - name: MG-PolicyAssignmentArtifact
        text: |-
               az blueprint published artifact show --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --version "V2" --artifact-name "costCenterPolicy"
"""

helps['blueprint published artifact list'] = """
    type: command
    short-summary: List artifacts for a version of a published blueprint definition.
    examples:
      - name: MG-ArtifactList
        text: |-
               az blueprint published artifact list --scope \\
               "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" --blueprint-name \\
               "simpleBlueprint" --version "V2"
      - name: Sub-ArtifactList
        text: |-
               az blueprint published artifact list --scope \\
               "subscriptions/00000000-0000-0000-0000-000000000000" --blueprint-name "simpleBlueprint" \\
               --version "V2"
"""

helps['blueprint assignment'] = """
    type: group
    short-summary: Commands to manage blueprint assignment.
"""

helps['blueprint assignment create'] = """
    type: command
    short-summary: Create a blueprint assignment.
    examples:
      - name: Assignment with system-assigned managed identity
        text: |-
               az blueprint assignment create --scope "subscriptions/00000000-0000-0000-0000-000000000000" --name \\
               "assignSimpleBlueprint" --location "eastus" --identity-type "SystemAssigned" \\
               --description "enforce pre-defined simpleBlueprint to this XXXXXXXX subscription." \\
               --blueprint-id "/providers/Microsoft.Management/managementGroups/ContosoOnlineGroup/provid \\
               ers/Microsoft.Blueprint/blueprints/simpleBlueprint"
      - name: Assignment with user-assigned managed identity
        text: |-
               az blueprint assignment create --scope "subscriptions/00000000-0000-0000-0000-000000000000" --name \\
               "assignSimpleBlueprint" --location "eastus" --identity-type "UserAssigned" --description \\
               "enforce pre-defined simpleBlueprint to this XXXXXXXX subscription." --blueprint-id "/prov \\
               iders/Microsoft.Management/managementGroups/ContosoOnlineGroup/providers/Microsoft.Bluepri \\
               nt/blueprints/simpleBlueprint"
"""

helps['blueprint assignment update'] = """
    type: command
    short-summary: Update a blueprint assignment.
"""

helps['blueprint assignment delete'] = """
    type: command
    short-summary: Delete a blueprint assignment.
    examples:
      - name: Assignment_Delete
        text: |-
               az blueprint assignment delete --scope "subscriptions/00000000-0000-0000-0000-000000000000" --name \\
               "assignSimpleBlueprint"
"""

helps['blueprint assignment show'] = """
    type: command
    short-summary: Get a blueprint assignment.
    examples:
      - name: Assignment
        text: |-
               az blueprint assignment show --scope "subscriptions/00000000-0000-0000-0000-000000000000" --name \\
               "assignSimpleBlueprint"
"""

helps['blueprint assignment list'] = """
    type: command
    short-summary: List blueprint assignments within a subscription.
    examples:
      - name: Assignment
        text: |-
               az blueprint assignment list --scope "subscriptions/00000000-0000-0000-0000-000000000000"
"""

helps['blueprint assignment who-is-blueprint'] = """
    type: command
    short-summary: Get Blueprints service SPN objectId
    examples:
      - name: WhoIsBlueprint_Action
        text: |-
               az blueprint assignment who-is-blueprint --scope \\
               "subscriptions/00000000-0000-0000-0000-000000000000" --name "assignSimpleBlueprint"
"""
