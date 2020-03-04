# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from knack.help_files import helps

helps['maintenance'] = """
    type: group
    short-summary: Manage Azure Maintenance.
    """

helps['maintenance configuration'] = """
    type: group
    short-summary: Manage Azure Maintenance configurations.
    """

helps['maintenance update'] = """
    type: group
    short-summary: Azure Maintenance updates.
    """

helps['maintenance assignment'] = """
    type: group
    short-summary: Manage Azure Maintenance configuration assignment to resource.
    """

helps['maintenance applyupdate'] = """
    type: group
    short-summary: Manage Azure Maintenance update applications.
    """

helps['maintenance configuration create'] = """
    type: command
    short-summary: Creates a Maintenance Configuration.
    examples:
        - name: Create a Maintenance Configuration with the All scope.
          text: >
            az maintenance configuration create --name workervms -g MyResourceGroup -l westus
"""

helps['maintenance configuration update'] = """
    type: command
    short-summary: Creates a Maintenance Configuration.
    examples:
        - name: Create a Maintenance Configuration with the All scope.
          text: >
            az maintenance configuration update --name workervms -g MyResourceGroup -l westus --maintenanceScope All
"""

helps['maintenance configuration delete'] = """
    type: command
    short-summary: Deletes a Maintenance Configuration.
    examples:
        - name: Delete a Maintenance Configuration.
          text: >
            az maintenance configuration delete --name workervms -g MyResourceGroup
"""

helps['maintenance configuration show'] = """
    type: command
    short-summary: Get the details of a Maintenance Configuration.
    examples:
        - name: Get the Maintenance Configuration.
          text: >
            az maintenance configuration show --name workervms -g MyResourceGroup
"""


helps['maintenance configuration list'] = """
    type: command
    short-summary: Get Configuration records within a subscription.
    examples:
        - name: Get Configuration records within a subscription.
          text: >
            az maintenance configuration list --subscription 2b4ce620-bb0f-4964-8428-dea4aefe00000
"""

helps['maintenance assignment create'] = """
    type: command
    short-summary: Creates a Maintenance Assignment.
    examples:
        - name: Create a Maintenance Assignment.
          text: >
            az maintenance assignment create -g smdtest --resource-name smdVM --resource-type virtualMachines --provider-name Microsoft.Compute --configuration-assignment-name workervms --maintenance-configuration-id "/subscriptions/2b4ce620-bb0f-4964-8428-dea4aefec295/resourcegroups/smdtest/providers/Microsoft.Maintenance/maintenanceConfigurations/workervms" -l eastus2
"""

helps['maintenance assignment delete'] = """
    type: command
    short-summary: Delete a Maintenance Assignment.
    examples:
        - name: Delete a Maintenance Assignment.
          text: >
            az maintenance assignment delete -g smdtest --resource-name smdVM --resource-type virtualMachines --provider-name Microsoft.Compute --configuration-assignment-name workervms
"""

helps['maintenance assignment list'] = """
    type: command
    short-summary: Lists Maintenance Assignment.
    examples:
        - name: List Maintenance Assignment.
          text: >
            az maintenance assignment list -g smdtest --resource-name smdVM --resource-type virtualMachines --provider-name Microsoft.Compute
"""

helps['maintenance update list'] = """
    type: command
    short-summary: List pending a Maintenance Updates.
    examples:
        - name: List pending a Maintenance Updates.
          text: >
            az maintenance update list -g smdtest --resource-name smdVM --resource-type virtualMachines --provider-name Microsoft.Compute
"""

helps['maintenance applyupdate create'] = """
    type: command
    short-summary: Creates a ApplyUpdate request.
    examples:
        - name: Creates a ApplyUpdate request.
          text: >
            az maintenance applyupdate create -g smdtest --resource-name smdVM --resource-type virtualMachines --provider-name Microsoft.Compute
"""

helps['maintenance applyupdate get'] = """
    type: command
    short-summary: Gets the state of a ApplyUpdate request.
    examples:
        - name: Gets the state of a ApplyUpdate request.
          text: >
            az maintenance applyupdate get -g smdtest --resource-name smdVM --resource-type virtualMachines --provider-name Microsoft.Compute --apply-update-name 7b1b66dc-e93a-4183-81ff-591f1b2d4f07
"""

helps['maintenance applyupdate show'] = """
    type: command
    short-summary: Shows the state of a ApplyUpdate request.
    examples:
        - name: Shows the state of a ApplyUpdate request.
          text: >
            az maintenance applyupdate show -g smdtest --resource-name smdVM --resource-type virtualMachines --provider-name Microsoft.Compute --apply-update-name 7b1b66dc-e93a-4183-81ff-591f1b2d4f07
"""
