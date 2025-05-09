# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


helps['costmanagement'] = """
    type: group
    short-summary: Manage cost and billing in Azure
"""

# override from generated._help
helps['costmanagement export'] = """
    type: group
    short-summary: costmanagement export
"""

helps['costmanagement export list'] = """
    type: command
    short-summary: The operation to list all exports at the given scope.
    examples:
      - name: list exports in a ManagementGroup scope
        text: |-
               az costmanagement export list --scope "providers/Microsoft.Management/managementGroups/TestMG"
      - name: list exports in a ResourceGroup scope
        text: |-
               az costmanagement export list --scope "subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups\
/MYDEVTESTRG"
      - name: list exports in a Subscription scope
        text: |-
               az costmanagement export list --scope "subscriptions/00000000-0000-0000-0000-000000000000"
"""

helps['costmanagement export show'] = """
    type: command
    short-summary: The operation to get the execution history of an export for the defined scope by export name.
    examples:
      - name: Show an export in a ManagementGroup scope
        text: |-
               az costmanagement export show --name "TestExport" --scope "providers/Microsoft.Management/managem\
entGroups/TestMG"
      - name: Show an export in a ResourceGroup scope
        text: |-
               az costmanagement export show --name "TestExport" --scope "subscriptions/00000000-0000-0000-0000-\
000000000000/resourceGroups/MYDEVTESTRG"
      - name: Show an export in a Subscription scope
        text: |-
               az costmanagement export show --name "TestExport" --scope "subscriptions/00000000-0000-0000-0000-\
000000000000"
"""

helps['costmanagement export create'] = """
    type: command
    short-summary: The operation to create an export.
    examples:
      - name: Create an export for ManagementGroup scope
        text: >
          az costmanagement export create
          --name "TestExport"
          --type "Usage"
          --dataset-configuration columns="Date" columns="MeterId" columns="InstanceId" columns="ResourceLocation" columns="PreTaxCost"
          --timeframe "MonthToDate"
          --storage-container="exports"
          --storage-account-id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MYDEVTESTRG/providers/Microsoft.Storage/storageAccounts/ccmeastusdiag182"
          --storage-directory="ad-hoc"
          --recurrence "Weekly"
          --recurrence-period from="2018-06-01T00:00:00Z" to="2018-10-31T00:00:00Z"
          --schedule-status "Active"
          --scope "providers/Microsoft.Management/managementGroups/TestMG"
      - name: Create an export for ResourceGroup scope
        text: >
          az costmanagement export create
          --name "TestExport"
          --type "Usage"
          --dataset-configuration columns="Date" columns="MeterId" columns="InstanceId" columns="ResourceLocation" columns="PreTaxCost"
          --timeframe "MonthToDate"
          --storage-container="exports"
          --storage-account-id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MYDEVTESTRG/providers/Microsoft.Storage/storageAccounts/ccmeastusdiag182"
          --storage-directory="ad-hoc"
          --recurrence "Weekly"
          --recurrence-period from="2018-06-01T00:00:00Z" to="2018-10-31T00:00:00Z"
          --schedule-status "Active"
          --scope "subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MYDEVTESTRG"
      - name: Create an export for Subscription scope
        text: >
          az costmanagement export create
          --name "TestExport"
          --type "Usage"
          --dataset-configuration columns="Date" columns="MeterId" columns="InstanceId" columns="ResourceLocation" columns="PreTaxCost"
          --timeframe "MonthToDate"
          --storage-container="exports"
          --storage-account-id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MYDEVTESTRG/providers/Microsoft.Storage/storageAccounts/ccmeastusdiag182"
          --storage-directory="ad-hoc"
          --recurrence "Weekly"
          --recurrence-period from="2018-06-01T00:00:00Z" to="2018-10-31T00:00:00Z"
          --schedule-status "Active"
          --scope "subscriptions/00000000-0000-0000-0000-000000000000"
"""

helps['costmanagement export update'] = """
    type: command
    short-summary: The operation to update an export.
    examples:
      - name: Update an export in a ManagementGroup scope
        text: >
          az costmanagement export update
          --name "TestExport"
          --dataset-configuration columns="Date" columns="MeterId" columns="InstanceId" columns="ResourceLocation" columns="PreTaxCost"
          --timeframe "MonthToDate"
          --storage-container="exports"
          --storage-account-id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MYDEVTESTRG/providers/Microsoft.Storage/storageAccounts/ccmeastusdiag182"
          --storage-directory="ad-hoc"
          --recurrence "Weekly"
          --recurrence-period from="2018-06-01T00:00:00Z" to="2018-10-31T00:00:00Z"
          --schedule-status "Active"
          --scope "providers/Microsoft.Management/managementGroups/TestMG"
      - name: Update an export in a ResourceGroup scope
        text: >
          az costmanagement export update
          --name "TestExport"
          --dataset-configuration columns="Date" columns="MeterId" columns="InstanceId" columns="ResourceLocation" columns="PreTaxCost"
          --timeframe "MonthToDate"
          --storage-container="exports"
          --storage-account-id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MYDEVTESTRG/providers/Microsoft.Storage/storageAccounts/ccmeastusdiag182"
          --storage-directory="ad-hoc"
          --recurrence "Weekly"
          --recurrence-period from="2018-06-01T00:00:00Z" to="2018-10-31T00:00:00Z"
          --schedule-status "Active"
          --scope "subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MYDEVTESTRG"
      - name: Update an export in a Subscription scope
        text: >
          az costmanagement export update
          --name "TestExport"
          --dataset-configuration columns="Date" columns="MeterId" columns="InstanceId" columns="ResourceLocation" columns="PreTaxCost"
          --timeframe "MonthToDate"
          --storage-container="exports"
          --storage-account-id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MYDEVTESTRG/providers/Microsoft.Storage/storageAccounts/ccmeastusdiag182"
          --storage-directory="ad-hoc"
          --recurrence "Weekly"
          --recurrence-period from="2018-06-01T00:00:00Z" to="2018-10-31T00:00:00Z"
          --schedule-status "Active"
          --scope "subscriptions/00000000-0000-0000-0000-000000000000"
"""

helps['costmanagement export delete'] = """
    type: command
    short-summary: The operation to delete an export.
    examples:
      - name: delete an export for a ManagementGroup scope
        text: |-
               az costmanagement export delete --name "TestExport" --scope "providers/Microsoft.Management/manag\
ementGroups/TestMG"
      - name: delete an export for ResourceGroup scope
        text: |-
               az costmanagement export delete --name "TestExport" --scope "subscriptions/00000000-0000-0000-000\
0-000000000000/resourceGroups/MYDEVTESTRG"
      - name: delete an export for Subscription scope
        text: |-
               az costmanagement export delete --name "TestExport" --scope "subscriptions/00000000-0000-0000-000\
0-000000000000"
"""
