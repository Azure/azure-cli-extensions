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
               az blueprint create --subscription MySubscription --name \\
               MyBlueprint --description \\
               "blueprint contains all artifacts" --target-scope \\
               subscription
      - name: Create a management group blueprint
        text: |-
               az blueprint create --management-group MyManagementGroup --name \\
               MyBlueprint --description \\
               "blueprint contains all artifact" --target-scope \\
               subscription
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
               az blueprint delete --management-group MyManagementGroup --name \\
               MyBlueprint
      - name: Delete a subscription blueprint
        text: |-
               az blueprint delete --subscription MySubscription --name \\
               MyBlueprint
"""

helps['blueprint show'] = """
    type: command
    short-summary: Get a blueprint definition.
    examples:
      - name: Show a management group blueprint
        text: |-
               az blueprint show --management-group MyManagementGroup --name \\
               MyBlueprint
      - name: Show a subscription blueprint
        text: |-
               az blueprint show --subscription MySubscription --name \\
               MyBlueprint
"""

helps['blueprint list'] = """
    type: command
    short-summary: List blueprint definitions.
    examples:
      - name: List blueprints in a management group
        text: |-
               az blueprint list --management-group MyManagementGroup
      - name: List blueprints in a subscription
        text: |-
               az blueprint list --subscription MySubscription
"""

helps['blueprint import'] = """
    type: command
    short-summary: Import a blueprint definition and artifacts from a directoy of json files.
    examples:
      - name: Import a blueprint definition and artifacts
        text: |-
               az blueprint import --name MyBlueprint \\
               --input-path "path/to/blueprint/directory"
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
               --blueprint-name MyBlueprint --artifact-name MyResourceGroupArt
"""

helps['blueprint resource-group update'] = """
    type: command
    short-summary: Update blueprint resource group artifact.
    examples:
      - name: Update a resource group artifact
        text: |-
               az blueprint resource-group update \\
               --blueprint-name MyBlueprint --artifact-name MyResourceGroupArt --display-name "My Resource Group"
"""

helps['blueprint resource-group remove'] = """
    type: command
    short-summary: Remove a blueprint resource group artifact.
    examples:
      - name: Remove a resource group artifact
        text: |-
               az blueprint resource-group remove \\
               --blueprint-name MyBlueprint --artifact-name MyResourceGroupArt
"""

helps['blueprint resource-group show'] = """
    type: command
    short-summary: Show blueprint resource group artifact.
    examples:
      - name: Show a resource group artifact
        text: |-
               az blueprint resource-group show \\
               --blueprint-name MyBlueprint --artifact-name MyResourceGroupArt
"""

helps['blueprint resource-group list'] = """
    type: command
    short-summary: List blueprint resource group artifact.
    examples:
      - name: List resource group artifacts
        text: |-
               az blueprint resource-group list \\
               --blueprint-name MyBlueprint
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
               az blueprint artifact delete --subscription MySubscription \\
               --blueprint-name MyBlueprint --name OwnerAssignment
      - name: Delete an ARM template artifact
        text: |-
               az blueprint artifact delete --management-group MyManagementGroup --blueprint-name \\
               MyBlueprint --name StorageTemplate
"""

helps['blueprint artifact show'] = """
    type: command
    short-summary: Get a blueprint artifact.
    examples:
      - name: Show an artifact of a subscription blueprint
        text: |-
               az blueprint artifact show --subscription MySubscription \\
               --blueprint-name MyBlueprint --name OwnerAssignment
      - name: Show an artifact of a management group blueprint
        text: |-
               az blueprint artifact show --management-group MyManagementGroup --blueprint-name \\
               MyBlueprint --name StorageTemplate
"""

helps['blueprint artifact list'] = """
    type: command
    short-summary: List artifacts for a given blueprint definition.
    examples:
      - name: List artifcats for a management group blueprint
        text: |-
               az blueprint artifact list --management-group MyManagementGroup --blueprint-name \\
               MyBlueprint
      - name: List artifcats for a subscription blueprint
        text: |-
               az blueprint artifact list --subscription MySubscription \\
               --blueprint-name MyBlueprint
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
               --blueprint-name MyBlueprint --artifact-name MyPolicy --policy-definition-id \\
               "/providers/Microsoft.Authorization/policyDefinitions/00000000-0000-0000-0000-000000000000" \\
               --parameters path/to/file --display-name "Policy to do sth"
"""

helps['blueprint artifact policy update'] = """
    type: command
    short-summary: Update blueprint policy artifact.
    examples:
      - name: Update a policy artifact
        text: |-
               az blueprint artifact policy update \\
               --blueprint-name MyBlueprint --artifact-name MyPolicy --display-name "My Policy"
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
               --blueprint-name MyBlueprint --artifact-name MyRole --role-definition-id \\
               "/providers/Microsoft.Authorization/roleDefinitions/00000000-0000-0000-0000-000000000000" \\
               --principal-ids "[parameters('[Usergrouporapplicationname]:MyRoleAssignmentName')]"
"""

helps['blueprint artifact role update'] = """
    type: command
    short-summary: Update blueprint role artifact.
    examples:
      - name: Update a role artifact
        text: |-
               az blueprint artifact role update \\
               --blueprint-name MyBlueprint --artifact-name MyRole --display-name "My Big Role"
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
               --blueprint-name MyBlueprint --artifact-name MyTemplate \\
               --parameters path/to/parameter/file --template path/to/template
"""

helps['blueprint artifact template update'] = """
    type: command
    short-summary: Update blueprint arm artifact.
    examples:
      - name: Update a arm artifact
        text: |-
               az blueprint artifact template update \\
               --blueprint-name MyBlueprint --artifact-name MyTemplate --display-name "My Template"
"""

helps['blueprint version'] = """
    type: group
    short-summary: Commands to manage published blueprint versions.
"""

helps['blueprint publish'] = """
    type: command
    short-summary: Publish a new version of the blueprint definition with the latest artifacts. Published blueprint definitions are immutable.
    examples:
      - name: Publish a management group blueprint
        text: |-
               az blueprint publish --management-group MyManagementGroup --blueprint-name \\
               MyBlueprint --version v2
      - name: Publish a subscription blueprint
        text: |-
               az blueprint publish --subscription MySubscription \\
               --blueprint-name MyBlueprint \\
               --version v2
"""

helps['blueprint version delete'] = """
    type: command
    short-summary: Delete a published version of a blueprint.
    examples:
      - name: Delete a published subscription blueprint
        text: |-
               az blueprint version delete --subscription MySubscription \\
               --blueprint-name MyBlueprint \\
               --version v2
      - name: Delete a published management group blueprint
        text: |-
               az blueprint version delete --management-group MyManagementGroup --blueprint-name \\
               MyBlueprint --version v2
"""

helps['blueprint version show'] = """
    type: command
    short-summary: Get a published version of a blueprint.
    examples:
      - name: Get a published management group blueprint
        text: |-
               az blueprint version show --management-group MyManagementGroup --blueprint-name \\
               MyBlueprint --version v2
      - name: Get a published subscription blueprint
        text: |-
               az blueprint version show --subscription MySubscription \\
               --blueprint-name MyBlueprint --version v2
"""

helps['blueprint version list'] = """
    type: command
    short-summary: List published versions of given blueprint definition.
    examples:
      - name: List published blueprints of a management group
        text: |-
               az blueprint version list --management-group MyManagementGroup --blueprint-name \\
               MyBlueprint
      - name: List published blueprints of a subscription
        text: |-
               az blueprint version list --subscription MySubscription \\
               --blueprint-name MyBlueprint
"""

helps['blueprint version artifact'] = """
    type: group
    short-summary: Commands to manage published blueprint artifacts.
"""

helps['blueprint version artifact show'] = """
    type: command
    short-summary: Show an artifact for a published blueprint.
    examples:
      - name: Show a role assignment artifact
        text: |-
               az blueprint version artifact show --subscription MySubscription \\
               --blueprint-name MyBlueprint \\
               --version v2 --artifact-name OwnerAssignment
      - name: Show a template artifact
        text: |-
               az blueprint version artifact show --management-group MyManagementGroup --blueprint-name \\
               MyBlueprint --version v2 --artifact-name StorageTemplate
"""

helps['blueprint version artifact list'] = """
    type: command
    short-summary: List artifacts for a version of a published blueprint.
    examples:
      - name: List artifacts of a published management group blueprint
        text: |-
               az blueprint version artifact list --management-group MyManagementGroup --blueprint-name \\
               MyBlueprint --version v2
      - name: List artifacts of a published subscription blueprint
        text: |-
               az blueprint version artifact list --subscription MySubscription \\
               --blueprint-name MyBlueprint \\
               --version v2
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
               az blueprint assignment create --subscription MySubscription --name \\
               MyBlueprintAssignment --location eastus --identity-type SystemAssigned \\
               --description "Enforce pre-defined MyBlueprint to this subscription." \\
               --blueprint-version "/providers/Microsoft.Management/managementGroups/ContosoOnlineGroup/provid \\
               ers/Microsoft.Blueprint/blueprints/MyBlueprint/versions/v2" \\
               --resource-group-value artifact_name=rg-art-1 name=rg1 location=westus \\
               --resource-group-value artifact_name=rg-art-2 name=rg2 location=eastus \\
               --parameters "path/to/parameter/file" \\
      - name: Assignment with user-assigned managed identity
        text: |-
               az blueprint assignment create --subscription MySubscription --name \\
               MyBlueprintAssignment --location eastus --identity-type UserAssigned \\
               --user-assigned-identities identity-id \\
               --description "Enforce pre-defined MyBlueprint to this subscription." \\
               --blueprint-version "/providers/Microsoft.Management/managementGroups/ContosoOnlineGroup \\
               /providers/Microsoft.Blueprint/blueprints/MyBlueprint/versions/v2" \\
               --resource-group-value artifact_name=rg-art-1 name=rg1 location=eastus \\
               --parameters "path/to/parameter/file" \\
"""

helps['blueprint assignment update'] = """
    type: command
    short-summary: Update a blueprint assignment.
"""

helps['blueprint assignment delete'] = """
    type: command
    short-summary: Delete a blueprint assignment.
    examples:
      - name: Delete an assignment
        text: |-
               az blueprint assignment delete --subscription MySubscription \\
               --name MyBlueprintAssignment
"""

helps['blueprint assignment show'] = """
    type: command
    short-summary: Get a blueprint assignment.
    examples:
      - name: Show an assignment
        text: |-
               az blueprint assignment show --subscription MySubscription \\
               --name MyBlueprintAssignment
"""

helps['blueprint assignment list'] = """
    type: command
    short-summary: List blueprint assignments within a subscription.
    examples:
      - name: List assignments
        text: |-
               az blueprint assignment list --subscription MySubscription
"""

helps['blueprint assignment wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the Blueprint Assignment is met.
    examples:
        - name: Pause executing next line of CLI script until the Blueprint Assignment is successfully provisioned.
          text: az blueprint assignment wait --subscription MySubscription \\
                --name MyBlueprintAssignment --created
"""

helps['blueprint assignment who'] = """
    type: command
    short-summary: Get Blueprint Servie Principal Name objectId
    examples:
      - name: Get SPN objectId
        text: |-
               az blueprint assignment who --subscription MySubscription \\
               --name MyBlueprintAssignment
"""
