# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from knack.help_files import helps  # pylint: disable=unused-import


helps['service-group'] = """
    type: group
    short-summary: Manage Azure Service Groups.
    long-summary: |
        Service Groups provide a construct to group multiple resources, resource groups,
        subscriptions and other service groups into an organizational hierarchy and centrally
        manage access control, policies, alerting and reporting for those resources.

        NOTE: This command group is in preview and under development.
"""

helps['service-group create'] = """
    type: command
    short-summary: Create a service group.
    long-summary: Create or update a service group. This is a long-running operation.
    examples:
      - name: Create a service group under the tenant root
        text: >
            az service-group create --name MyServiceGroup --display-name "My Service Group"
            --parent resource-id="/providers/Microsoft.Management/serviceGroups/<tenantId>"
      - name: Create a child service group under an existing parent
        text: >
            az service-group create --name ChildGroup --display-name "Child Group"
            --parent resource-id="/providers/Microsoft.Management/serviceGroups/ParentGroup"
"""

helps['service-group show'] = """
    type: command
    short-summary: Get the details of a service group.
    examples:
      - name: Show a service group
        text: >
            az service-group show --name MyServiceGroup
"""

helps['service-group update'] = """
    type: command
    short-summary: Update a service group.
    long-summary: Update a service group. This is a long-running operation.
    examples:
      - name: Update the display name of a service group
        text: >
            az service-group update --name MyServiceGroup --display-name "Updated Name"
"""

helps['service-group delete'] = """
    type: command
    short-summary: Delete a service group.
    long-summary: Delete a service group. This is a long-running operation.
    examples:
      - name: Delete a service group
        text: >
            az service-group delete --name MyServiceGroup --yes
"""

helps['service-group list-ancestors'] = """
    type: command
    short-summary: List the ancestors of a service group.
    long-summary: Get the details of the service group's ancestors in the hierarchy.
    examples:
      - name: List ancestors of a service group
        text: >
            az service-group list-ancestors --name MyServiceGroup
"""

helps['service-group wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the service group is met.
    examples:
      - name: Wait until a service group is successfully provisioned
        text: >
            az service-group wait --name MyServiceGroup --created
"""
