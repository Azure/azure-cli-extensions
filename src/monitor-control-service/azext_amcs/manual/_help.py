# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['monitor data-collection'] = """
    type: group
    short-summary: Manage data collection
"""

helps['monitor data-collection rule association'] = """
    type: group
    short-summary: Manage data collection rule association with data collection
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
    short-summary: Manage data collection rule with data collection
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
      - name: --data-flow
        short-summary: "The specification of data flows."
        long-summary: |
            Usage: --data-flow stream=XX1 stream=XX2 destination=XX1 destination=XX2

            stream: Required. List of streams for this data flow.
            destination: Required. List of destinations for this data flow.

            Multiple actions can be specified by using more than one --data-flow argument.
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
      - name: --performance-counter
        short-summary: "The list of performance counter data source configurations."
        long-summary: |
            Usage: --performance-counter stream=XX1 stream=XX2 transfer-period=XX \
sampling-frequency=XX counter-specifier=XX1 counter-specifier=XX2 name=XX

            stream: Required. List of streams that this data source will be sent to. A stream indicates what schema \
will be used for this data and usually what table in Log Analytics the data will be sent to.
            transfer-period: Required. The interval between data uploads (scheduled transfers), rounded up \
to the nearest minute.
            sampling-frequency: Required. The number of seconds between consecutive counter measurements \
(samples).
            counter-specifier: Required. A list of specifier names of the performance counters you want to collect. \
Use a wildcard (*) to collect a counter for all instances. To get a list of performance counters on Windows, run the \
command 'typeperf'.
            name: Required. A friendly name for the data source.  This name should be unique across all data sources \
(regardless of type) within the data collection rule.

            Multiple actions can be specified by using more than one --performance-counter argument.
      - name: --windows-event-log
        short-summary: "The list of Windows Event Log data source configurations."
        long-summary: |
            Usage: --windows-event-log stream=XX1 stream=XX2 transfer-period=XX x-path-query=XX1 \
x-path-query=XX2 name=XX

            stream: Required. List of streams that this data source will be sent to. A stream indicates what schema \
will be used for this data and usually what table in Log Analytics the data will be sent to.
            transfer-period: Required. The interval between data uploads (scheduled transfers), rounded up \
to the nearest minute.
            x-path-query: Required. A list of Windows Event Log queries in XPATH format.
            name: Required. A friendly name for the data source.  This name should be unique across all data sources \
(regardless of type) within the data collection rule.

            Multiple actions can be specified by using more than one --windows-event-log argument.
      - name: --syslog
        short-summary: "The list of Syslog data source configurations."
        long-summary: |
            Usage: --syslog stream=XX1 stream=XX2 facility-name=XX1 facility-name=XX2 log-level=XX1 log-level=XX2 \
name=XX

            stream: Required. List of streams that this data source will be sent to. A stream indicates what schema \
will be used for this data and usually what table in Log Analytics the data will be sent to.
            facility-name: Required. The list of facility names.
            log-level: The log levels to collect.
            name: Required. A friendly name for the data source.  This name should be unique across all data sources \
(regardless of type) within the data collection rule.

            Multiple actions can be specified by using more than one --syslog argument.
    examples:
      - name: Create data collection rule
        text: |-
               az monitor data-collection rule create --resource-group "myResourceGroup" --location "eastus" \
--name "myCollectionRule" \
--data-flow destination="centralWorkspace" stream="Microsoft-Perf" stream="Microsoft-Syslog" \
stream="Microsoft-WindowsEvent" \
--performance-counter name="cloudTeamCoreCounters" counter-specifier="\\\\Processor(_Total)\\\\% Processor Time" \
counter-specifier="\\\\Memory\\\\Committed Bytes" counter-specifier="\\\\LogicalDisk(_Total)\\\\Free Megabytes" \
counter-specifier="\\\\PhysicalDisk(_Total)\\\\Avg. Disk Queue Length" sampling-frequency=15 \
transfer-period="PT1M" stream="Microsoft-Perf" \
--performance-counter name="appTeamExtraCounters" \
counter-specifier="\\\\Process(_Total)\\\\Thread Count" sampling-frequency=30 \
transfer-period="PT5M" stream="Microsoft-Perf" \
--syslog name="cronSyslog" facility-name="cron" log-level="Debug" log-level="Critical" log-level="Emergency" \
stream="Microsoft-Syslog" \
--syslog name="syslogBase" facility-name="syslog" log-level="Alert" log-level="Critical" log-level="Emergency" \
stream="Microsoft-Syslog" \
--windows-event-log name="cloudSecurityTeamEvents" transfer-period="PT1M" stream="Microsoft-WindowsEvent" \
x-path-query="Security!" \
--windows-event-log name="appTeam1AppEvents" transfer-period="PT5M" stream="Microsoft-WindowsEvent" \
x-path-query="System![System[(Level = 1 or Level = 2 or Level = 3)]]" \
x-path-query="Application!*[System[(Level = 1 or Level = 2 or Level = 3)]]" \
--log-analytics name="centralWorkspace" \
resource-id="/subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Mic\
rosoft.OperationalInsights/workspaces/centralTeamWorkspace"

"""

helps['monitor data-collection rule update'] = """
    type: command
    short-summary: "Update a data collection rule."
    parameters:
      - name: --data-flow
        short-summary: "The specification of data flows."
        long-summary: |
            Usage: --data-flow stream=XX1 stream=XX2 destination=XX1 destination=XX2

            stream: Required. List of streams for this data flow.
            destination: Required. List of destinations for this data flow.

            Multiple actions can be specified by using more than one --data-flow argument.
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
      - name: --performance-counter
        short-summary: "The list of performance counter data source configurations."
        long-summary: |
            Usage: --performance-counter stream=XX1 stream=XX2 transfer-period=XX \
sampling-frequency=XX counter-specifier=XX1 counter-specifier=XX2 name=XX

            stream: Required. List of streams that this data source will be sent to. A stream indicates what schema \
will be used for this data and usually what table in Log Analytics the data will be sent to.
            transfer-period: Required. The interval between data uploads (scheduled transfers), rounded up \
to the nearest minute.
            sampling-frequency: Required. The number of seconds between consecutive counter measurements \
(samples).
            counter-specifier: Required. A list of specifier names of the performance counters you want to collect. \
Use a wildcard (*) to collect a counter for all instances. To get a list of performance counters on Windows, run the \
command 'typeperf'.
            name: Required. A friendly name for the data source.  This name should be unique across all data sources \
(regardless of type) within the data collection rule.

            Multiple actions can be specified by using more than one --performance-counter argument.
      - name: --windows-event-log
        short-summary: "The list of Windows Event Log data source configurations."
        long-summary: |
            Usage: --windows-event-log stream=XX1 stream=XX2 transfer-period=XX x-path-query=XX1 \
x-path-query=XX2 name=XX

            stream: Required. List of streams that this data source will be sent to. A stream indicates what schema \
will be used for this data and usually what table in Log Analytics the data will be sent to.
            transfer-period: Required. The interval between data uploads (scheduled transfers), rounded up \
to the nearest minute.
            x-path-query: Required. A list of Windows Event Log queries in XPATH format.
            name: Required. A friendly name for the data source.  This name should be unique across all data sources \
(regardless of type) within the data collection rule.

            Multiple actions can be specified by using more than one --windows-event-log argument.
      - name: --syslog
        short-summary: "The list of Syslog data source configurations."
        long-summary: |
            Usage: --syslog stream=XX1 stream=XX2 facility-name=XX1 facility-name=XX2 log-level=XX1 log-level=XX2 \
name=XX

            stream: Required. List of streams that this data source will be sent to. A stream indicates what schema \
will be used for this data and usually what table in Log Analytics the data will be sent to.
            facility-name: Required. The list of facility names.
            log-level: The log levels to collect.
            name: Required. A friendly name for the data source.  This name should be unique across all data sources \
(regardless of type) within the data collection rule.

            Multiple actions can be specified by using more than one --syslog argument.
    examples:
      - name: Create data collection rule
        text: |-
               az monitor data-collection rule create --resource-group "myResourceGroup" --location "eastus" \
--name "myCollectionRule" \
--data-flow destination="centralWorkspace" stream="Microsoft-Perf" stream="Microsoft-Syslog" \
stream="Microsoft-WindowsEvent" \
--performance-counter name="cloudTeamCoreCounters" counter-specifier="\\\\Processor(_Total)\\\\% Processor Time" \
counter-specifier="\\\\Memory\\\\Committed Bytes" counter-specifier="\\\\LogicalDisk(_Total)\\\\Free Megabytes" \
counter-specifier="\\\\PhysicalDisk(_Total)\\\\Avg. Disk Queue Length" sampling-frequency=15 \
transfer-period="PT1M" stream="Microsoft-Perf" \
--performance-counter name="appTeamExtraCounters" \
counter-specifier="\\\\Process(_Total)\\\\Thread Count" sampling-frequency=30 \
transfer-period="PT5M" stream="Microsoft-Perf" \
--syslog name="cronSyslog" facility-name="cron" log-level="Debug" log-level="Critical" log-level="Emergency" \
stream="Microsoft-Syslog" \
--syslog name="syslogBase" facility-name="syslog" log-level="Alert" log-level="Critical" log-level="Emergency" \
stream="Microsoft-Syslog" \
--windows-event-log name="cloudSecurityTeamEvents" transfer-period="PT1M" stream="Microsoft-WindowsEvent" \
x-path-query="Security!" \
--windows-event-log name="appTeam1AppEvents" transfer-period="PT5M" stream="Microsoft-WindowsEvent" \
x-path-query="System![System[(Level = 1 or Level = 2 or Level = 3)]]" \
x-path-query="Application!*[System[(Level = 1 or Level = 2 or Level = 3)]]" \
--log-analytics name="centralWorkspace" \
resource-id="/subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Mic\
rosoft.OperationalInsights/workspaces/centralTeamWorkspace"

"""

helps['monitor data-collection rule delete'] = """
    type: command
    short-summary: "Deletes a data collection rule."
    examples:
      - name: Delete data collection rule
        text: |-
               az monitor data-collection rule delete --name "myCollectionRule" --resource-group "myResourceGroup"
"""
