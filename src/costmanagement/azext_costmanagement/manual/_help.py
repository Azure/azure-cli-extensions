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
      - name: Query in ManagementGroupQuery scope in grouping
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
