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
