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
helps['costmanagement query'] = """
    type: command
    short-summary: Query the usage data for scope defined.
    examples:
      - name: Query in ManagementGroup scope
        text: |-
               az costmanagement query --type "Usage" --dataset-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\
\\"name\\":\\"ResourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\
\\"name\\":\\"Environment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\
\\":\\"ResourceGroup\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --timeframe "MonthToDate" --scope "provid\
ers/Microsoft.Management/managementGroups/MyMgId"
      - name: Query in ManagementGroupQuery scope via grouping
        text: |-
               az costmanagement query --type "Usage" --dataset-aggregation "{\\"totalCost\\":{\\"name\\":\\"PreT\
axCost\\",\\"function\\":\\"Sum\\"}}" --dataset-grouping name="ResourceGroup" type="Dimension" --timeframe "TheLastMont\
h" --scope "providers/Microsoft.Management/managementGroups/MyMgId"
      - name: Query in a ResourceGroup scope
        text: |-
               az costmanagement query --type "Usage" --dataset-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\
\\"name\\":\\"ResourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\
\\"name\\":\\"Environment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\
\\":\\"ResourceGroup\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --timeframe "MonthToDate" --scope "subscr\
iptions/00000000-0000-0000-0000-000000000000/resourceGroups/ScreenSharingTest-peer"
      - name: Query in a ResourceGroupQuery scope via grouping
        text: |-
               az costmanagement query --type "Usage" --dataset-aggregation "{\\"totalCost\\":{\\"name\\":\\"PreT\
axCost\\",\\"function\\":\\"Sum\\"}}" --dataset-grouping name="ResourceType" type="Dimension" --timeframe "TheLastMonth\
" --scope "subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ScreenSharingTest-peer"
      - name: Query in a Subscription scope
        text: |-
               az costmanagement query --type "Usage" --dataset-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\
\\"name\\":\\"ResourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\
\\"name\\":\\"Environment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\
\\":\\"ResourceGroup\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --timeframe "MonthToDate" --scope "subscr\
iptions/00000000-0000-0000-0000-000000000000"
      - name: Query in a Subscription scope via grouping
        text: |-
               az costmanagement query --type "Usage" --dataset-aggregation "{\\"totalCost\\":{\\"name\\":\\"PreT\
axCost\\",\\"function\\":\\"Sum\\"}}" --dataset-grouping name="ResourceGroup" type="Dimension" --timeframe "TheLastMont\
h" --scope "subscriptions/00000000-0000-0000-0000-000000000000"
"""


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
    short-summary: The operation to create or update a export. Update operation requires latest eTag to be set in the r\
equest. You may obtain the latest eTag by performing a get operation. Create operation does not require eTag.
    examples:
      - name: Create an export for ManagementGroup scope
        text: |-
               az costmanagement export create --name "TestExport" --definition-type "Usage" --definition-datase\
t-aggregation "{\\"costSum\\":{\\"name\\":\\"PreTaxCost\\",\\"function\\":\\"Sum\\"}}" --definition-dataset-configurati\
on columns="Date" columns="MeterId" columns="InstanceId" columns="ResourceLocation" columns="PreTaxCost" --definition-d\
ataset-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"ResourceLocation\\",\\"operator\\":\\"In\\",\\"va\
lues\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"Environment\\",\\"operator\\":\\"In\\",\\"values\
\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"ResourceGroup\\",\\"operator\\":\\"In\\",\\"values\\":[\
\\"API\\"]}}]}" --definition-dataset-grouping name="SubscriptionName" type="Dimension" --definition-dataset-grouping na\
me="Environment" type="Tag" --definition-timeframe "MonthToDate" --delivery-info-destination container="exports" resour\
ce-id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MYDEVTESTRG/providers/Microsoft.Storage/stora\
geAccounts/ccmeastusdiag182" root-folder-path="ad-hoc" --schedule-recurrence "Weekly" --schedule-recurrence-period from\
="2018-06-01T00:00:00Z" to="2018-10-31T00:00:00Z" --schedule-status "Active" --scope "providers/Microsoft.Management/ma\
nagementGroups/TestMG"
      - name: Create an export for ResourceGroup scope
        text: |-
               az costmanagement export create --name "TestExport" --definition-type "Usage" --definition-datase\
t-aggregation "{\\"costSum\\":{\\"name\\":\\"PreTaxCost\\",\\"function\\":\\"Sum\\"}}" --definition-dataset-configurati\
on columns="Date" columns="MeterId" columns="InstanceId" columns="ResourceLocation" columns="PreTaxCost" --definition-d\
ataset-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"ResourceLocation\\",\\"operator\\":\\"In\\",\\"va\
lues\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"Environment\\",\\"operator\\":\\"In\\",\\"values\
\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"ResourceGroup\\",\\"operator\\":\\"In\\",\\"values\\":[\
\\"API\\"]}}]}" --definition-dataset-grouping name="SubscriptionName" type="Dimension" --definition-dataset-grouping na\
me="Environment" type="Tag" --definition-timeframe "MonthToDate" --delivery-info-destination container="exports" resour\
ce-id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MYDEVTESTRG/providers/Microsoft.Storage/stora\
geAccounts/ccmeastusdiag182" root-folder-path="ad-hoc" --schedule-recurrence "Weekly" --schedule-recurrence-period from\
="2018-06-01T00:00:00Z" to="2018-10-31T00:00:00Z" --schedule-status "Active" --scope "subscriptions/00000000-0000-0000-\
0000-000000000000/resourceGroups/MYDEVTESTRG"
      - name: Create an export for Subscription scope
        text: |-
               az costmanagement export create --name "TestExport" --definition-type "Usage" --definition-datase\
t-aggregation "{\\"costSum\\":{\\"name\\":\\"PreTaxCost\\",\\"function\\":\\"Sum\\"}}" --definition-dataset-configurati\
on columns="Date" columns="MeterId" columns="InstanceId" columns="ResourceLocation" columns="PreTaxCost" --definition-d\
ataset-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"ResourceLocation\\",\\"operator\\":\\"In\\",\\"va\
lues\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"Environment\\",\\"operator\\":\\"In\\",\\"values\
\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"ResourceGroup\\",\\"operator\\":\\"In\\",\\"values\\":[\
\\"API\\"]}}]}" --definition-dataset-grouping name="SubscriptionName" type="Dimension" --definition-dataset-grouping na\
me="Environment" type="Tag" --definition-timeframe "MonthToDate" --delivery-info-destination container="exports" resour\
ce-id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MYDEVTESTRG/providers/Microsoft.Storage/stora\
geAccounts/ccmeastusdiag182" root-folder-path="ad-hoc" --schedule-recurrence "Weekly" --schedule-recurrence-period from\
="2018-06-01T00:00:00Z" to="2018-10-31T00:00:00Z" --schedule-status "Active" --scope "subscriptions/00000000-0000-0000-\
0000-000000000000"
"""

helps['costmanagement export update'] = """
    type: command
    short-summary: The operation to create or update a export. Update operation requires latest eTag to be set in the r\
equest. You may obtain the latest eTag by performing a get operation. Create operation does not require eTag.
    examples:
      - name: Update an export for ManagementGroup scope
        text: |-
               az costmanagement export update --name "TestExport" --definition-type "Usage" --definition-datase\
t-aggregation "{\\"costSum\\":{\\"name\\":\\"PreTaxCost\\",\\"function\\":\\"Sum\\"}}" --definition-dataset-configurati\
on columns="Date" columns="MeterId" columns="InstanceId" columns="ResourceLocation" columns="PreTaxCost" --definition-d\
ataset-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"ResourceLocation\\",\\"operator\\":\\"In\\",\\"va\
lues\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"Environment\\",\\"operator\\":\\"In\\",\\"values\
\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"ResourceGroup\\",\\"operator\\":\\"In\\",\\"values\\":[\
\\"API\\"]}}]}" --definition-dataset-grouping name="SubscriptionName" type="Dimension" --definition-dataset-grouping na\
me="Environment" type="Tag" --definition-timeframe "MonthToDate" --delivery-info-destination container="exports" resour\
ce-id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MYDEVTESTRG/providers/Microsoft.Storage/stora\
geAccounts/ccmeastusdiag182" root-folder-path="ad-hoc" --schedule-recurrence "Weekly" --schedule-recurrence-period from\
="2018-06-01T00:00:00Z" to="2018-10-31T00:00:00Z" --schedule-status "Active" --scope "providers/Microsoft.Management/ma\
nagementGroups/TestMG"
      - name: Update an export for ResourceGroup scope
        text: |-
               az costmanagement export update --name "TestExport" --definition-type "Usage" --definition-datase\
t-aggregation "{\\"costSum\\":{\\"name\\":\\"PreTaxCost\\",\\"function\\":\\"Sum\\"}}" --definition-dataset-configurati\
on columns="Date" columns="MeterId" columns="InstanceId" columns="ResourceLocation" columns="PreTaxCost" --definition-d\
ataset-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"ResourceLocation\\",\\"operator\\":\\"In\\",\\"va\
lues\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"Environment\\",\\"operator\\":\\"In\\",\\"values\
\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"ResourceGroup\\",\\"operator\\":\\"In\\",\\"values\\":[\
\\"API\\"]}}]}" --definition-dataset-grouping name="SubscriptionName" type="Dimension" --definition-dataset-grouping na\
me="Environment" type="Tag" --definition-timeframe "MonthToDate" --delivery-info-destination container="exports" resour\
ce-id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MYDEVTESTRG/providers/Microsoft.Storage/stora\
geAccounts/ccmeastusdiag182" root-folder-path="ad-hoc" --schedule-recurrence "Weekly" --schedule-recurrence-period from\
="2018-06-01T00:00:00Z" to="2018-10-31T00:00:00Z" --schedule-status "Active" --scope "subscriptions/00000000-0000-0000-\
0000-000000000000/resourceGroups/MYDEVTESTRG"
      - name: Update an export for Subscription scope
        text: |-
               az costmanagement export update --name "TestExport" --definition-type "Usage" --definition-datase\
t-aggregation "{\\"costSum\\":{\\"name\\":\\"PreTaxCost\\",\\"function\\":\\"Sum\\"}}" --definition-dataset-configurati\
on columns="Date" columns="MeterId" columns="InstanceId" columns="ResourceLocation" columns="PreTaxCost" --definition-d\
ataset-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"ResourceLocation\\",\\"operator\\":\\"In\\",\\"va\
lues\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"Environment\\",\\"operator\\":\\"In\\",\\"values\
\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"ResourceGroup\\",\\"operator\\":\\"In\\",\\"values\\":[\
\\"API\\"]}}]}" --definition-dataset-grouping name="SubscriptionName" type="Dimension" --definition-dataset-grouping na\
me="Environment" type="Tag" --definition-timeframe "MonthToDate" --delivery-info-destination container="exports" resour\
ce-id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MYDEVTESTRG/providers/Microsoft.Storage/stora\
geAccounts/ccmeastusdiag182" root-folder-path="ad-hoc" --schedule-recurrence "Weekly" --schedule-recurrence-period from\
="2018-06-01T00:00:00Z" to="2018-10-31T00:00:00Z" --schedule-status "Active" --scope "subscriptions/00000000-0000-0000-\
0000-000000000000"
"""

helps['costmanagement export delete'] = """
    type: command
    short-summary: The operation to delete a export.
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
