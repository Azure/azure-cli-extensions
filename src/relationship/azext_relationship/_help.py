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
        a source resource and a target resource. Two relationship types are supported:
        dependencyOf (dependency links) and serviceGroupMember (service group membership).

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
        ServiceGroupMember relationships associate resources with Service Groups.
        Valid sources: Service Groups, Subscriptions, Resource Groups, Resources.
        Valid targets: Service Groups ONLY.
"""

helps['relationship service-group-member create'] = """
    type: command
    short-summary: Create a serviceGroupMember relationship.
    long-summary: Create or update a serviceGroupMember relationship. This is a long-running operation.
    examples:
      - name: Create a service group membership from a resource group
        text: >
            az relationship service-group-member create
            --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}"
            --name myMembership
            --target-id "/providers/Microsoft.Management/serviceGroups/mySG"
      - name: Create a service group membership from a subscription
        text: >
            az relationship service-group-member create
            --resource-uri "/subscriptions/{sub}"
            --name subMembership
            --target-id "/providers/Microsoft.Management/serviceGroups/mySG"
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
