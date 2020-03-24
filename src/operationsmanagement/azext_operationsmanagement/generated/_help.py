# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-many-lines

from knack.help_files import helps


helps['operationsmanagement solution'] = """
    type: group
    short-summary: operationsmanagement solution
"""

helps['operationsmanagement solution list'] = """
    type: command
    short-summary: Retrieves the solution list. It will retrieve both first party and third party solutions
    examples:
      - name: SolutionList
        text: |-
               az operationsmanagement solution list --resource-group "rg1"
"""

helps['operationsmanagement solution show'] = """
    type: command
    short-summary: Retrieves the user solution.
    examples:
      - name: SolutionGet
        text: |-
               az operationsmanagement solution show --resource-group "rg1" --solution-name "solution1"
"""

helps['operationsmanagement solution create'] = """
    type: command
    short-summary: Creates or updates the Solution.
    examples:
      - name: SolutionCreate
        text: |-
               az operationsmanagement solution create --location "East US" --plan name=name1 product=product1 promotio\
n-code=promocode1 publisher=publisher1 --properties contained-resources=[\\"/subscriptions/sub2/resourceGroups/rg2/prov\
iders/provider1/resources/resource1\\",\\"/subscriptions/sub2/resourceGroups/rg2/providers/provider2/resources/resource\
2\\"] referenced-resources=[\\"/subscriptions/sub2/resourceGroups/rg2/providers/provider1/resources/resource2\\",\\"/su\
bscriptions/sub2/resourceGroups/rg2/providers/provider2/resources/resource3\\"] workspace-resource-id=/subscriptions/su\
b2/resourceGroups/rg2/providers/Microsoft.OperationalInsights/workspaces/ws1 --resource-group "rg1" --solution-name "so\
lution1"
"""

helps['operationsmanagement solution update'] = """
    type: command
    short-summary: Patch a Solution. Only updating tags supported.
    examples:
      - name: SolutionUpdate
        text: |-
               az operationsmanagement solution update --tags Dept=IT Environment=Test --resource-group "rg1" --solutio\
n-name "solution1"
"""

helps['operationsmanagement solution delete'] = """
    type: command
    short-summary: Deletes the solution in the subscription.
    examples:
      - name: SolutionDelete
        text: |-
               az operationsmanagement solution delete --resource-group "rg1" --solution-name "solution1"
"""

helps['operationsmanagement management-association'] = """
    type: group
    short-summary: operationsmanagement management-association
"""

helps['operationsmanagement management-association list'] = """
    type: command
    short-summary: Retrieves the ManagementAssociations list.
    examples:
      - name: SolutionList
        text: |-
               az operationsmanagement management-association list
"""

helps['operationsmanagement management-association show'] = """
    type: command
    short-summary: Retrieves the user ManagementAssociation.
    examples:
      - name: SolutionGet
        text: |-
               az operationsmanagement management-association show --management-association-name "managementAssociation\
1" --provider-name "providerName" --resource-group "rg1" --resource-name "resourceName" --resource-type "resourceType"
"""

helps['operationsmanagement management-association create'] = """
    type: command
    short-summary: Creates or updates the ManagementAssociation.
    examples:
      - name: SolutionCreate
        text: |-
               az operationsmanagement management-association create --management-association-name "managementAssociati\
on1" --location "East US" --properties application-id=/subscriptions/sub1/resourcegroups/rg1/providers/Microsoft.Applia\
nce/Appliances/appliance1 --provider-name "providerName" --resource-group "rg1" --resource-name "resourceName" --resour\
ce-type "resourceType"
"""

helps['operationsmanagement management-association update'] = """
    type: command
    short-summary: Creates or updates the ManagementAssociation.
    examples:
      - name: SolutionCreate
        text: |-
               az operationsmanagement management-association create --management-association-name "managementAssociati\
on1" --location "East US" --properties application-id=/subscriptions/sub1/resourcegroups/rg1/providers/Microsoft.Applia\
nce/Appliances/appliance1 --provider-name "providerName" --resource-group "rg1" --resource-name "resourceName" --resour\
ce-type "resourceType"
"""

helps['operationsmanagement management-association delete'] = """
    type: command
    short-summary: Deletes the ManagementAssociation in the subscription.
    examples:
      - name: SolutionDelete
        text: |-
               az operationsmanagement management-association delete --management-association-name "managementAssociati\
onName" --provider-name "providerName" --resource-group "rg1" --resource-name "resourceName" --resource-type "resourceT\
ype"
"""

helps['operationsmanagement management-configuration'] = """
    type: group
    short-summary: operationsmanagement management-configuration
"""

helps['operationsmanagement management-configuration list'] = """
    type: command
    short-summary: Retrieves the ManagementConfigurations list.
    examples:
      - name: SolutionList
        text: |-
               az operationsmanagement management-configuration list
"""

helps['operationsmanagement management-configuration show'] = """
    type: command
    short-summary: Retrieves the user ManagementConfiguration.
    examples:
      - name: SolutionGet
        text: |-
               az operationsmanagement management-configuration show --management-configuration-name "managementConfigu\
rationName" --resource-group "rg1"
"""

helps['operationsmanagement management-configuration create'] = """
    type: command
    short-summary: Creates or updates the ManagementConfiguration.
    examples:
      - name: ManagementConfigurationCreate
        text: |-
               az operationsmanagement management-configuration create --management-configuration-name "managementConfi\
guration1" --location "East US" --resource-group "rg1"
"""

helps['operationsmanagement management-configuration update'] = """
    type: command
    short-summary: Creates or updates the ManagementConfiguration.
    examples:
      - name: ManagementConfigurationCreate
        text: |-
               az operationsmanagement management-configuration create --management-configuration-name "managementConfi\
guration1" --location "East US" --resource-group "rg1"
"""

helps['operationsmanagement management-configuration delete'] = """
    type: command
    short-summary: Deletes the ManagementConfiguration in the subscription.
    examples:
      - name: ManagementConfigurationDelete
        text: |-
               az operationsmanagement management-configuration delete --management-configuration-name "managementConfi\
gurationName" --resource-group "rg1"
"""
