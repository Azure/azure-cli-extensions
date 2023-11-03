# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['monitor data-collection'] = """
    type: group
    short-summary: Manage data collection for monitor control service
"""

helps['monitor data-collection endpoint'] = """
    type: group
    short-summary: Manage data collection endpoint for monitor control service
"""

helps['monitor data-collection endpoint list'] = """
    type: command
    short-summary: "List all data collection endpoints."
    examples:
      - name: List data collection endpoints by resource group
        text: |-
               az monitor data-collection endpoint list --resource-group "myResourceGroup"
      - name: List data collection endpoints by subscription
        text: |-
               az monitor data-collection endpoint list
"""

helps['monitor data-collection endpoint show'] = """
    type: command
    short-summary: "Show the specified data collection endpoint."
    examples:
      - name: Get data collection endpoint
        text: |-
               az monitor data-collection endpoint show --name "myCollectionEndpoint" --resource-group \
"myResourceGroup"
"""

helps['monitor data-collection endpoint create'] = """
    type: command
    short-summary: "Create a data collection endpoint."
    examples:
      - name: Create data collection endpoint
        text: |-
               az monitor data-collection endpoint create -g "myResourceGroup" -l "eastus2euap" \
               --name "myCollectionEndpoint" --public-network-access "Enabled"
"""

helps['monitor data-collection endpoint update'] = """
    type: command
    short-summary: "Update a data collection endpoint."
    examples:
      - name: Update data collection endpoint
        text: |-
               az monitor data-collection endpoint update --tags tag1="A" tag2="B" tag3="C" --name \
"myCollectionEndpoint" --resource-group "myResourceGroup"
"""

helps['monitor data-collection endpoint delete'] = """
    type: command
    short-summary: "Delete a data collection endpoint."
    examples:
      - name: Delete data collection endpoint
        text: |-
               az monitor data-collection endpoint delete --name "myCollectionEndpoint" --resource-group \
"myResourceGroup"
"""

helps['monitor data-collection rule association'] = """
    type: group
    short-summary: Manage data collection rule association for monitor control service
"""

helps['monitor data-collection rule association list'] = """
    type: command
    short-summary: "List associations for the specified data collection rule. And Lists associations for the \
specified resource."
    examples:
      - name: List associations for specified data collection rule
        text: |-
               az monitor data-collection rule association list --rule-name "myCollectionRule" --resource-group \
"myResourceGroup"
      - name: List associations for specified resource
        text: |-
               az monitor data-collection rule association list --resource "subscriptions/703362b3-f278-4e4b-9179-c76ea\
f41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtualMachines/myVm"
"""

helps['monitor data-collection rule association show'] = """
    type: command
    short-summary: "Return the specified association."
    examples:
      - name: Get association
        text: |-
               az monitor data-collection rule association show --name "myAssociation" --resource \
"subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtualM\
achines/myVm"
"""

helps['monitor data-collection rule association create'] = """
    type: command
    short-summary: "Create an association."
    examples:
      - name: Create association
        text: |-
               az monitor data-collection rule association create --name "myAssociation" --rule-id \
"/subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Insights/dataCo\
llectionRules/myCollectionRule" --resource "subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourc\
eGroup/providers/Microsoft.Compute/virtualMachines/myVm"
"""

helps['monitor data-collection rule association update'] = """
    type: command
    short-summary: "Update an association."
    examples:
      - name: Update association
        text: |-
               az monitor data-collection rule association update --name "myAssociation" --rule-id \
"/subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Insights/dataCo\
llectionRules/myCollectionRule" --resource "subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourc\
eGroup/providers/Microsoft.Compute/virtualMachines/myVm"
"""

helps['monitor data-collection rule association delete'] = """
    type: command
    short-summary: "Delete an association."
    examples:
      - name: Delete association
        text: |-
               az monitor data-collection rule association delete --name "myAssociation" --resource \
"subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtualM\
achines/myVm"
"""

helps['monitor data-collection rule'] = """
    type: group
    short-summary: Manage data collection rule for monitor control service
"""

helps['monitor data-collection rule list'] = """
    type: command
    short-summary: "List all data collection rules in the specified resource group. And Lists all data collection \
rules in the specified subscription."
    examples:
      - name: List data collection rules by resource group
        text: |-
               az monitor data-collection rule list --resource-group "myResourceGroup"
      - name: List data collection rules by subscription
        text: |-
               az monitor data-collection rule list
"""

helps['monitor data-collection rule show'] = """
    type: command
    short-summary: "Return the specified data collection rule."
    examples:
      - name: Get data collection rule
        text: |-
               az monitor data-collection rule show --name "myCollectionRule" --resource-group "myResourceGroup"
"""

helps['monitor data-collection rule create'] = """
    type: command
    short-summary: "Create a data collection rule."
    parameters:
      - name: --rule-file
        short-summary: "The json file for rule parameters."
        long-summary: |
            Usage:   --rule-file sample.json
            rule json file should be rule parameters organized as json format, like below:
            {
                "properties": {
                    "destinations": {
                        "azureMonitorMetrics": {
                            "name": "azureMonitorMetrics-default"
                        }
                    },
                    "dataFlows": [
                        {
                            "streams": [
                                "Microsoft-InsightsMetrics"
                            ],
                            "destinations": [
                                "azureMonitorMetrics-default"
                            ]
                        }
                    ]
                }
            }
    examples:
      - name: Create data collection rule
        text: |-
               az monitor data-collection rule create --resource-group "myResourceGroup" --location "eastus" \
--name "myCollectionRule" --rule-file "C:\samples\dcrEx1.json"
"""

helps['monitor data-collection rule update'] = """
    type: command
    short-summary: "Update a data collection rule."
    parameters:
      - name: --data-flows
        short-summary: "The specification of data flows."
        long-summary: |
            Usage: --data-flows streams=XX1 streams=XX2 destinations=XX1 destinations=XX2

            streams: Required. List of streams for this data flow.
            destinations: Required. List of destinations for this data flow.

            Multiple actions can be specified by using more than one --data-flows argument.
      - name: --log-analytics
        short-summary: "List of Log Analytics destinations."
        long-summary: |
            Usage: --log-analytics resource-id=XX name=XX

            resource-id: Required. The resource ID of the Log Analytics workspace.
            name: Required. A friendly name for the destination.  This name should be unique across all destinations \
(regardless of type) within the data collection rule.

            Multiple actions can be specified by using more than one --log-analytics argument.
      - name: --monitor-metrics
        short-summary: "Azure Monitor Metrics destination."
        long-summary: |
            Usage: --monitor-metrics name=XX

            name: Required. A friendly name for the destination.  This name should be unique across all destinations \
(regardless of type) within the data collection rule.
      - name: --performance-counters
        short-summary: "The list of performance counter data source configurations."
        long-summary: |
            Usage: --performance-counters streams=XX1 streams=XX2 \
sampling-frequency=XX counter-specifiers=XX1 counter-specifiers=XX2 name=XX

            streams: Required. List of streams that this data source will be sent to. A stream indicates what schema \
will be used for this data and usually what table in Log Analytics the data will be sent to.
            sampling-frequency: Required. The number of seconds between consecutive counter measurements \
(samples).
            counter-specifiers: Required. A list of specifier names of the performance counters you want to collect. \
Use a wildcard (*) to collect a counter for all instances. To get a list of performance counters on Windows, run the \
command 'typeperf'.
            name: Required. A friendly name for the data source.  This name should be unique across all data sources \
(regardless of type) within the data collection rule.

            Multiple actions can be specified by using more than one --performance-counters argument.
      - name: --windows-event-logs
        short-summary: "The list of Windows Event Log data source configurations."
        long-summary: |
            Usage: --windows-event-logs streams=XX1 streams=XX2 x-path-queries=XX1 \
x-path-queries=XX2 name=XX

            streams: Required. List of streams that this data source will be sent to. A stream indicates what schema \
will be used for this data and usually what table in Log Analytics the data will be sent to.
            x-path-queries: Required. A list of Windows Event Log queries in XPATH format.
            name: Required. A friendly name for the data source.  This name should be unique across all data sources \
(regardless of type) within the data collection rule.

            Multiple actions can be specified by using more than one --windows-event-logs argument.
      - name: --syslog
        short-summary: "The list of Syslog data source configurations."
        long-summary: |
            Usage: --syslog streams=XX1 streams=XX2 facility-names=XX1 facility-names=XX2 log-levels=XX1 log-levels=XX2 \
name=XX

            streams: Required. List of streams that this data source will be sent to. A stream indicates what schema \
will be used for this data and usually what table in Log Analytics the data will be sent to.
            facility-names: Required. The list of facility names.
            log-levels: The log levels to collect.
            name: Required. A friendly name for the data source.  This name should be unique across all data sources \
(regardless of type) within the data collection rule.

            Multiple actions can be specified by using more than one --syslog argument.
    examples:
      - name: Update data collection rule
        text: |-
               az monitor data-collection rule update --resource-group "myResourceGroup" --name "myCollectionRule" \
--data-flows destinations="centralWorkspace" streams="Microsoft-Perf" streams="Microsoft-Syslog" \
streams="Microsoft-WindowsEvent" \
--log-analytics name="centralWorkspace" \
resource-id="/subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Mic\
rosoft.OperationalInsights/workspaces/centralTeamWorkspace" \
--performance-counters name="appTeamExtraCounters" \
counter-specifiers="\\\\Process(_Total)\\\\Thread Count" sampling-frequency=30 \
streams="Microsoft-Perf" \
--syslog name="cronSyslog" facility-names="cron" log-levels="Debug" log-levels="Critical" log-levels="Emergency" \
streams="Microsoft-Syslog" \
--windows-event-logs name="cloudSecurityTeamEvents" streams="Microsoft-WindowsEvent" \
x-path-queries="Security!"
"""

helps['monitor data-collection rule delete'] = """
    type: command
    short-summary: "Deletes a data collection rule."
    examples:
      - name: Delete data collection rule
        text: |-
               az monitor data-collection rule delete --name "myCollectionRule" --resource-group "myResourceGroup"
"""

helps['monitor data-collection rule data-flow'] = """
    type: group
    short-summary: Manage data flows.
"""

helps['monitor data-collection rule data-flow list'] = """
    type: command
    short-summary: List data flows.
    examples:
      - name: List data flows
        text: |-
               az monitor data-collection rule data-flow list --rule-name "myCollectionRule" \
--resource-group "myResourceGroup"
"""

helps['monitor data-collection rule data-flow add'] = """
    type: command
    short-summary: Add a data flow.
    examples:
      - name: Add a data flow
        text: |-
               az monitor data-collection rule data-flow add --rule-name "myCollectionRule" \
--resource-group "myResourceGroup" --destinations XX3 XX4 --streams "Microsoft-Perf" "Microsoft-WindowsEvent"
"""

helps['monitor data-collection rule log-analytics'] = """
    type: group
    short-summary: Manage Log Analytics destinations.
"""

helps['monitor data-collection rule log-analytics list'] = """
    type: command
    short-summary: List Log Analytics destinations of a data collection rule.
    examples:
      - name: List Log Analytics destinations of a data collection rule
        text: |-
               az monitor data-collection rule log-analytics list --rule-name "myCollectionRule" \
--resource-group "myResourceGroup"
"""

helps['monitor data-collection rule log-analytics show'] = """
    type: command
    short-summary: Show a Log Analytics destination of a data collection rule.
    examples:
      - name: Show a Log Analytics destination of a data collection rule
        text: |-
               az monitor data-collection rule log-analytics show --rule-name "myCollectionRule" \
--resource-group "myResourceGroup" --name "centralWorkspace"
"""

helps['monitor data-collection rule log-analytics add'] = """
    type: command
    short-summary: Add Log Analytics destinations of a data collection rule.
    examples:
      - name: Add Log Analytics destinations of a data collection rule
        text: |-
               az monitor data-collection rule log-analytics add --rule-name "myCollectionRule" \
--resource-group "myResourceGroup" --name "workspace2" --resource-id "/subscriptions/703362b3-f278-4e4b-9179-c76eaf41ff\
c2/resourceGroups/myResourceGroup/providers/Microsoft.OperationalInsights/workspaces/workspace2"
"""

helps['monitor data-collection rule log-analytics delete'] = """
    type: command
    short-summary: Delete a Log Analytics destinations of a data collection rule.
    examples:
      - name: Delete a Log Analytics destinations of a data collection rule
        text: |-
               az monitor data-collection rule log-analytics delete --rule-name "myCollectionRule" \
--resource-group "myResourceGroup" --name "workspace2"
"""

helps['monitor data-collection rule log-analytics update'] = """
    type: command
    short-summary: Update a Log Analytics destination of a data collection rule.
    examples:
      - name: Update a Log Analytics destination of a data collection rule
        text: |-
               az monitor data-collection rule log-analytics update --rule-name "myCollectionRule" \
--resource-group "myResourceGroup" --name "workspace2" --resource-id "/subscriptions/703362b3-f278-4e4b-9179-c76eaf41ff\
c2/resourceGroups/myResourceGroup/providers/Microsoft.OperationalInsights/workspaces/anotherWorkspace"
"""

helps['monitor data-collection rule performance-counter'] = """
    type: group
    short-summary: Manage Log performance counter data source.
"""

helps['monitor data-collection rule performance-counter list'] = """
    type: command
    short-summary: List Log performance counter data sources.
    examples:
      - name: List Log performance counter data sources
        text: |-
               az monitor data-collection rule performance-counter list --rule-name "myCollectionRule" \
--resource-group "myResourceGroup"
"""

helps['monitor data-collection rule performance-counter show'] = """
    type: command
    short-summary: Show a Log performance counter data source.
    examples:
      - name: Show a Log performance counter data source
        text: |-
               az monitor data-collection rule performance-counter show --rule-name "myCollectionRule" \
--resource-group "myResourceGroup" --name "appTeamExtraCounters"
"""

helps['monitor data-collection rule performance-counter add'] = """
    type: command
    short-summary: Add a Log performance counter data source.
    examples:
      - name: Add a Log performance counter data source
        text: |-
               az monitor data-collection rule performance-counter add --rule-name "myCollectionRule" \
--resource-group "myResourceGroup" --name "team2ExtraCounters" --streams "Microsoft-Perf" \
--counter-specifiers "\\\\Process(_Total)\\\\Thread Count" "\\\\LogicalDisk(_Total)\\\\Free Megabytes" \
--sampling-frequency 30
"""

helps['monitor data-collection rule performance-counter update'] = """
    type: command
    short-summary: Update a Log performance counter data source.
    examples:
      - name: Update a Log performance counter data source
        text: |-
               az monitor data-collection rule performance-counter update --rule-name "myCollectionRule" \
--resource-group "myResourceGroup" --name "team2ExtraCounters"
"""

helps['monitor data-collection rule performance-counter delete'] = """
    type: command
    short-summary: Delete a Log performance counter data source.
    examples:
      - name: Delete a Log performance counter data source
        text: |-
               az monitor data-collection rule performance-counter delete --rule-name "myCollectionRule" \
--resource-group "myResourceGroup" --name "team2ExtraCounters"
"""

helps['monitor data-collection rule windows-event-log'] = """
    type: group
    short-summary: Manage Windows Event Log data source.
"""

helps['monitor data-collection rule windows-event-log list'] = """
    type: command
    short-summary: List Windows Event Log data sources.
    examples:
      - name: List Windows Event Log data sources
        text: |-
               az monitor data-collection rule windows-event-log list --rule-name "myCollectionRule" \
--resource-group "myResourceGroup"
"""

helps['monitor data-collection rule windows-event-log show'] = """
    type: command
    short-summary: Show a Windows Event Log data source.
    examples:
      - name: Show a Windows Event Log data source
        text: |-
               az monitor data-collection rule windows-event-log show --rule-name "myCollectionRule" \
--resource-group "myResourceGroup" --name "appTeam1AppEvents"
"""

helps['monitor data-collection rule windows-event-log add'] = """
    type: command
    short-summary: Add a Windows Event Log data source.
    examples:
      - name: Add a Windows Event Log data source
        text: |-
               az monitor data-collection rule windows-event-log add --rule-name "myCollectionRule" \
--resource-group "myResourceGroup" --name "appTeam1AppEvents" \
--streams "Microsoft-WindowsEvent" --x-path-queries "Application!*[System[(Level = 1 or Level = 2 or Level = 3)]]" \
"System![System[(Level = 1 or Level = 2 or Level = 3)]]"
"""

helps['monitor data-collection rule windows-event-log update'] = """
    type: command
    short-summary: Update a Windows Event Log data source.
    examples:
      - name: Update a Windows Event Log data source
        text: |-
               az monitor data-collection rule windows-event-log update --rule-name "myCollectionRule" \
--resource-group "myResourceGroup" --name "appTeam1AppEvents" \
--x-path-queries "Application!*[System[(Level = 1 or Level = 2 or Level = 3)]]"
"""

helps['monitor data-collection rule windows-event-log delete'] = """
    type: command
    short-summary: Delete a Windows Event Log data source.
    examples:
      - name: Delete a Windows Event Log data source
        text: |-
               az monitor data-collection rule windows-event-log delete --rule-name "myCollectionRule" \
--resource-group "myResourceGroup" --name "appTeam1AppEvents"
"""

helps['monitor data-collection rule syslog'] = """
    type: group
    short-summary: Manage Syslog data source.
"""

helps['monitor data-collection rule syslog list'] = """
    type: command
    short-summary: List Syslog data sources.
    examples:
      - name: List Syslog data sources
        text: |-
               az monitor data-collection rule syslog list --rule-name "myCollectionRule" \
--resource-group "myResourceGroup"
"""

helps['monitor data-collection rule syslog show'] = """
    type: command
    short-summary: Show a Syslog data source.
    examples:
      - name: Show a Syslog data source
        text: |-
               az monitor data-collection rule syslog show --rule-name "myCollectionRule" \
--resource-group "myResourceGroup" --name "syslogBase"
"""

helps['monitor data-collection rule syslog add'] = """
    type: command
    short-summary: Add a Syslog data source.
    examples:
      - name: Add a Syslog data source
        text: |-
               az monitor data-collection rule syslog add --rule-name "myCollectionRule" \
--resource-group "myResourceGroup" --name "syslogBase" --facility-names "syslog" --log-levels "Alert" "Critical" \
--streams "Microsoft-Syslog"
"""

helps['monitor data-collection rule syslog update'] = """
    type: command
    short-summary: Update a Syslog data source.
    examples:
      - name: Update a Syslog data source
        text: |-
               az monitor data-collection rule syslog update --rule-name "myCollectionRule" \
--resource-group "myResourceGroup" --name "syslogBase" --facility-names "syslog" --log-levels "Emergency" "Critical"
"""

helps['monitor data-collection rule syslog delete'] = """
    type: command
    short-summary: Delete a Syslog data source.
    examples:
      - name: Delete a Syslog data source
        text: |-
               az monitor data-collection rule syslog delete --rule-name "myCollectionRule" \
--resource-group "myResourceGroup" --name "syslogBase"
"""
