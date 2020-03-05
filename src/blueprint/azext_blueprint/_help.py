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
      - name: Create a subscription blueprint
        text: |-
               az blueprint create --subscription "00000000-0000-0000-0000-000000000000" --name \\
               "simpleBlueprint" --description \\
               "blueprint contains all artifact" --target-scope \\
               "subscription"
      - name: Create a management group blueprint
        text: |-
               az blueprint create --management-group myManagementGroup --name \\
               "simpleBlueprint" --description \\
               "blueprint contains all artifact" --target-scope \\
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
      - name: Delete a management group blueprint
        text: |-
               az blueprint delete --management-group myManagementGroup --name \\
               "simpleBlueprint"
      - name: Delete a subscription blueprint
        text: |-
               az blueprint delete --subscription "00000000-0000-0000-0000-000000000000" --name \\
               "simpleBlueprint"
"""

helps['blueprint show'] = """
    type: command
    short-summary: Get a blueprint definition.
    examples:
      - name: Show a management group blueprint
        text: |-
               az blueprint show --management-group myManagementGroup --name \\
               "simpleBlueprint"
      - name: Show a subscription blueprint
        text: |-
               az blueprint show --subscription "00000000-0000-0000-0000-000000000000" --name \\
               "simpleBlueprint"
"""

helps['blueprint list'] = """
    type: command
    short-summary: List blueprint definitions.
    examples:
      - name: List blueprints in a management group
        text: |-
               az blueprint list --management-group myManagementGroup
      - name: List blueprints in a subscription
        text: |-
               az blueprint list --subscription "00000000-0000-0000-0000-000000000000"
"""

helps['blueprint import'] = """
    type: command
    short-summary: Import a blueprint definition and artifacts from a directoy of json files.
    examples:
      - name: Import a blueprint definition and artifacts
        text: |-
               az blueprint import --name "simpleBlueprint" \\
               --input-path "/path/to/blueprint/directory"
"""

helps['blueprint resource-group'] = """
    type: group
    short-summary: Commands to manage blueprint resource group artifact.
"""

helps['blueprint resource-group add'] = """
    type: command
    short-summary: Add a resource group artifact to the blueprint.
    examples:
      - name: Add a resource group artifact
        text: |-
               az blueprint resource-group add \\
               --blueprint-name "myBlueprint" --artifact-name "myRG"
"""

helps['blueprint resource-group update'] = """
    type: command
    short-summary: Update blueprint resource group artifact.
    examples:
      - name: Update a resource group artifact
        text: |-
               az blueprint resource-group update \\
               --blueprint-name "myBlueprint" --artifact-name "myRG" --display-name "Updated name"
"""

helps['blueprint resource-group remove'] = """
    type: command
    short-summary: Remove a blueprint resource group artifact.
    examples:
      - name: Remove a resource group artifact
        text: |-
               az blueprint resource-group delete \\
               --blueprint-name "myBlueprint" --artifact-name "myRG"
"""

helps['blueprint resource-group show'] = """
    type: command
    short-summary: Show blueprint resource group artifact.
    examples:
      - name: Show a resource group artifact
        text: |-
               az blueprint resource-group show \\
               --blueprint-name "myBlueprint" --artifact-name "myRG"
"""

helps['blueprint resource-group list'] = """
    type: command
    short-summary: List blueprint resource group artifact.
    examples:
      - name: List resource group artifacts
        text: |-
               az blueprint resource-group list \\
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
      - name: Delete a role assignment artifact
        text: |-
               az blueprint artifact delete --subscription "00000000-0000-0000-0000-000000000000" \\
               --blueprint-name "simpleBlueprint" --name "ownerAssignment"
      - name: Delete an ARM template artifact
        text: |-
               az blueprint artifact delete --management-group myManagementGroup --blueprint-name \\
               "simpleBlueprint" --name "storageTemplate"
"""

helps['blueprint artifact show'] = """
    type: command
    short-summary: Get a blueprint artifact.
    examples:
      - name: Sub-RoleAssignmentArtifact
        text: |-
               az blueprint artifact show --subscription "00000000-0000-0000-0000-000000000000" \\
               --blueprint-name "simpleBlueprint" --name "ownerAssignment"
      - name: MG-ARMTemplateArtifact
        text: |-
               az blueprint artifact show --management-group myManagementGroup --blueprint-name \\
               "simpleBlueprint" --name "storageTemplate"
"""

helps['blueprint artifact list'] = """
    type: command
    short-summary: List artifacts for a given blueprint definition.
    examples:
      - name: MG-ArtifactList
        text: |-
               az blueprint artifact list --management-group myManagementGroup --blueprint-name \\
               "simpleBlueprint"
      - name: Sub-ArtifactList
        text: |-
               az blueprint artifact list --subscription "00000000-0000-0000-0000-000000000000" \\
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
               az blueprint artifact policy create \\
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
               az blueprint artifact policy update \\
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
               az blueprint artifact role create \\
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
               az blueprint artifact role update \\
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
               az blueprint artifact template create \\
               --blueprint-name "myBlueprint" --artifact-name "myTemplate" \\
               --parameters @/path/to/parameter/file --template @/path/to/template
"""

helps['blueprint artifact template update'] = """
    type: command
    short-summary: Update blueprint arm artifact.
    examples:
      - name: Update a arm artifact
        text: |-
               az blueprint artifact template update \\
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
               az blueprint published create --management-group myManagementGroup --name \\
               "simpleBlueprint" --version "v2"
      - name: PublishedSubscriptionBlueprint_Publish
        text: |-
               az blueprint published create --subscription "00000000-0000-0000-0000-000000000000" \\
               --name "simpleBlueprint" \\
               --version "v2"
"""

helps['blueprint published delete'] = """
    type: command
    short-summary: Delete a published version of a blueprint definition.
    examples:
      - name: PublishedSubscriptionBlueprint
        text: |-
               az blueprint published delete --subscription "00000000-0000-0000-0000-000000000000" \\
               --name "simpleBlueprint" \\
               --version "v2"
      - name: PublishedManagementGroupBlueprint
        text: |-
               az blueprint published delete --management-group myManagementGroup --name \\
               "simpleBlueprint" --version "v2"
"""

helps['blueprint published show'] = """
    type: command
    short-summary: Get a published version of a blueprint definition.
    examples:
      - name: PublishedManagementGroupBlueprint
        text: |-
               az blueprint published show --management-group myManagementGroup --name \\
               "simpleBlueprint" --version "v2"
      - name: PublishedSubscriptionBlueprint
        text: |-
               az blueprint published show --subscription "00000000-0000-0000-0000-000000000000" \\
               --name "simpleBlueprint" --version "v2"
"""

helps['blueprint published list'] = """
    type: command
    short-summary: List published versions of given blueprint definition.
    examples:
      - name: PublishedManagementGroupBlueprint
        text: |-
               az blueprint published list --management-group myManagementGroup --blueprint-name \\
               "simpleBlueprint"
      - name: PublishedSubscriptionBlueprint
        text: |-
               az blueprint published list --subscription "00000000-0000-0000-0000-000000000000" \\
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
      - name: Sub-RoleAssignmentArtifact
        text: |-
               az blueprint published artifact show --subscription "00000000-0000-0000-0000-000000000000" \\
               --blueprint-name "simpleBlueprint" \\
               --version "V2" --artifact-name "ownerAssignment"
      - name: MG-ARMTemplateArtifact
        text: |-
               az blueprint published artifact show --management-group myManagementGroup --blueprint-name \\
               "simpleBlueprint" --version "V2" --artifact-name "storageTemplate"
"""

helps['blueprint published artifact list'] = """
    type: command
    short-summary: List artifacts for a version of a published blueprint definition.
    examples:
      - name: MG-ArtifactList
        text: |-
               az blueprint published artifact list --management-group myManagementGroup --blueprint-name \\
               "simpleBlueprint" --version "V2"
      - name: Sub-ArtifactList
        text: |-
               az blueprint published artifact list --subscription "00000000-0000-0000-0000-000000000000" \\
               --blueprint-name "simpleBlueprint" \\
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
               az blueprint assignment create --subscription "00000000-0000-0000-0000-000000000000" --name \\
               "assignSimpleBlueprint" --location "eastus" --identity-type "SystemAssigned" \\
               --description "enforce pre-defined simpleBlueprint to this XXXXXXXX subscription." \\
               --blueprint-id "/providers/Microsoft.Management/managementGroups/ContosoOnlineGroup/provid \\
               ers/Microsoft.Blueprint/blueprints/simpleBlueprint/versions/1.0" \\
               --resource-groups "@path/to/resource-group/file" \\
               --parameters "@path/to/parameter/file" \\
      - name: Assignment with user-assigned managed identity
        text: |-
               az blueprint assignment create --subscription "00000000-0000-0000-0000-000000000000" --name \\
               "assignSimpleBlueprint" --location "eastus" --identity-type "UserAssigned" \\
               --description "enforce pre-defined simpleBlueprint to this XXXXXXXX subscription." \\
               --blueprint-id "/providers/Microsoft.Management/managementGroups/ContosoOnlineGroup \\
               /providers/Microsoft.Blueprint/blueprints/simpleBlueprint/versions/1.0" \\
               --resource-groups "@path/to/resource-group/file" \\
               --parameters "@path/to/parameter/file" \\
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
               az blueprint assignment delete --subscription "00000000-0000-0000-0000-000000000000" --name \\
               "assignSimpleBlueprint"
"""

helps['blueprint assignment show'] = """
    type: command
    short-summary: Get a blueprint assignment.
    examples:
      - name: Assignment
        text: |-
               az blueprint assignment show --subscription "00000000-0000-0000-0000-000000000000" --name \\
               "assignSimpleBlueprint"
"""

helps['blueprint assignment list'] = """
    type: command
    short-summary: List blueprint assignments within a subscription.
    examples:
      - name: Assignment
        text: |-
               az blueprint assignment list --subscription "00000000-0000-0000-0000-000000000000"
"""

helps['blueprint assignment wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the Blueprint Assignment is met.
    examples:
        - name: Pause executing next line of CLI script until the Blueprint Assignment is successfully provisioned.
          text: az blueprint assignment wait --subscription "00000000-0000-0000-0000-000000000000" \\
                --assignment-name "assignSimpleBlueprint" \\
                --created
"""

helps['blueprint assignment who-is-blueprint'] = """
    type: command
    short-summary: Get Blueprints service SPN objectId
    examples:
      - name: WhoIsBlueprint_Action
        text: |-
               az blueprint assignment who-is-blueprint --subscription "00000000-0000-0000-0000-000000000000" \\
               --name "assignSimpleBlueprint"
"""
