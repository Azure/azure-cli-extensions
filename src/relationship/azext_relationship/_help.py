# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from knack.help_files import helps  # pylint: disable=unused-import


helps['relationship'] = """
    type: group
    short-summary: Manage Azure Relationships.
    long-summary: |
        Relationships are ARM extension resources that create semantic associations between
        a source resource and a target resource. Supported relationship types are
        dependencyOf (dependency links), serviceGroupMember (service group membership),
        and contains (read-only, system-discovered containment).

        NOTE: This command group is in preview and under development.
"""

helps['relationship dependency-of'] = """
    type: group
    short-summary: Manage dependencyOf relationships.
    long-summary: |
        DependencyOf relationships create dependency links between ARM resources.
        Valid sources: Management Groups, Service Groups, Subscriptions, Resource Groups, Resources.
        Valid targets: Management Groups, Service Groups, Resources.
"""

helps['relationship dependency-of create'] = """
    type: command
    short-summary: Create a dependencyOf relationship.
    long-summary: Create or update a dependencyOf relationship. This is a long-running operation.
    examples:
      - name: Create a dependency from a resource group to a service group
        text: >
            az relationship dependency-of create
            --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}"
            --name myDependency
            --target-id "/providers/Microsoft.Management/serviceGroups/mySG"
      - name: Create a dependency from a subscription to a service group
        text: >
            az relationship dependency-of create
            --resource-uri "/subscriptions/{sub}"
            --name subDep
            --target-id "/providers/Microsoft.Management/serviceGroups/mySG"
"""

helps['relationship dependency-of show'] = """
    type: command
    short-summary: Get the details of a dependencyOf relationship.
    examples:
      - name: Show a dependencyOf relationship
        text: >
            az relationship dependency-of show
            --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}"
            --name myDependency
"""

helps['relationship dependency-of delete'] = """
    type: command
    short-summary: Delete a dependencyOf relationship.
    long-summary: Delete a dependencyOf relationship. This is a long-running operation.
    examples:
      - name: Delete a dependencyOf relationship
        text: >
            az relationship dependency-of delete
            --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}"
            --name myDependency --yes
"""

helps['relationship service-group-member'] = """
    type: group
    short-summary: Manage serviceGroupMember relationships.
    long-summary: |
        ServiceGroupMember relationships associate Azure resources with Service Groups.
        The source must be a Service Group. The target is the resource identified by --resource-uri.
"""

helps['relationship service-group-member create'] = """
    type: command
    short-summary: Create a serviceGroupMember relationship.
    long-summary: Create or update a serviceGroupMember relationship. This is a long-running operation.
    examples:
      - name: Add a resource group to a service group
        text: >
            az relationship service-group-member create
            --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}"
            --name myMembership
            --source-id "/providers/Microsoft.Management/serviceGroups/mySG"
      - name: Add a subscription to a service group
        text: >
            az relationship service-group-member create
            --resource-uri "/subscriptions/{sub}"
            --name subMembership
            --source-id "/providers/Microsoft.Management/serviceGroups/mySG"
"""

helps['relationship service-group-member show'] = """
    type: command
    short-summary: Get the details of a serviceGroupMember relationship.
    examples:
      - name: Show a serviceGroupMember relationship
        text: >
            az relationship service-group-member show
            --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}"
            --name myMembership
"""

helps['relationship service-group-member delete'] = """
    type: command
    short-summary: Delete a serviceGroupMember relationship.
    long-summary: Delete a serviceGroupMember relationship. This is a long-running operation.
    examples:
      - name: Delete a serviceGroupMember relationship
        text: >
            az relationship service-group-member delete
            --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}"
            --name myMembership --yes
"""

helps['relationship dependency-of list'] = """
    type: command
    short-summary: List dependencyOf relationships at a resource scope.
    examples:
      - name: List dependencies attached to a resource group
        text: >
            az relationship dependency-of list
            --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}"
"""

helps['relationship dependency-of update'] = """
    type: command
    short-summary: Update an existing dependencyOf relationship.
    long-summary: Read the relationship, apply changes, and submit the updated resource using PUT.
    examples:
      - name: Update the target of a dependencyOf relationship
        text: >
            az relationship dependency-of update
            --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}"
            --name myDependency
            --target-id "/providers/Microsoft.Management/serviceGroups/mySG"
"""

helps['relationship service-group-member list'] = """
    type: command
    short-summary: List serviceGroupMember relationships at a resource scope.
    examples:
      - name: List memberships attached to a resource group
        text: >
            az relationship service-group-member list
            --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}"
"""

helps['relationship service-group-member update'] = """
    type: command
    short-summary: Update an existing serviceGroupMember relationship.
    long-summary: Read the relationship, apply changes, and submit the updated resource using PUT.
    examples:
      - name: Update the Service Group source of a membership
        text: >
            az relationship service-group-member update
            --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}"
            --name myMembership
            --source-id "/providers/Microsoft.Management/serviceGroups/mySG"
"""

helps['relationship contains'] = """
    type: group
    short-summary: List system-discovered contains relationships.
    long-summary: Contains relationships are read-only and cannot be created, updated, or deleted.
"""

helps['relationship contains list'] = """
    type: command
    short-summary: List contains relationships in a subscription or resource group.
    long-summary: Omit --resource-group to list at subscription scope. Use --filter for OData filtering.
    examples:
      - name: List contains relationships in a subscription
        text: az relationship contains list --subscription "{sub}"
      - name: List resource-group containment relationships filtered by target type
        text: >
            az relationship contains list --subscription "{sub}" --resource-group "{rg}"
            --filter "properties.metadata.targetType eq 'Microsoft.Compute/virtualMachines'"
"""

helps['relationship dependency-of-by-service-group'] = """
    type: group
    short-summary: Manage dependencyOf relationships attached to a Service Group.
    long-summary: |
        Use --service-group-name to select the source Service Group at tenant scope.
        These commands use the explicit Microsoft.Management/serviceGroups relationship routes.
"""

helps['relationship dependency-of-by-service-group create'] = """
    type: command
    short-summary: Create a dependencyOf relationship attached to a Service Group.
    examples:
      - name: Create a dependency between Service Groups
        text: >
            az relationship dependency-of-by-service-group create
            --service-group-name sourceSG --name myDependency
            --target-id "/providers/Microsoft.Management/serviceGroups/targetSG"
"""

helps['relationship dependency-of-by-service-group list'] = """
    type: command
    short-summary: List dependencyOf relationships attached to a Service Group.
    examples:
      - name: List dependencies attached to a Service Group
        text: az relationship dependency-of-by-service-group list --service-group-name sourceSG
"""

helps['relationship dependency-of-by-service-group update'] = """
    type: command
    short-summary: Update an existing Service Group-scoped dependencyOf relationship.
    long-summary: Read the relationship, apply changes, and submit the updated resource using PUT.
    examples:
      - name: Update a Service Group dependency target
        text: >
            az relationship dependency-of-by-service-group update
            --service-group-name sourceSG --name myDependency
            --target-id "/providers/Microsoft.Management/serviceGroups/targetSG"
"""
