# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['monitor scheduled-query'] = """
    type: group
    short-summary: Commands to manage scheduled queries.
"""

helps['monitor scheduled-query create'] = """
type: command
short-summary: Create a scheduled query.
parameters:
  - name: --action-groups
    short-summary: Action Group resource Ids to invoke when the alert fires.
    long-summary: |
        Usage:   --action-groups ACTION_GROUP_NAME_OR_ID [NAME_OR_ID,...]
  - name: --custom-properties
    short-summary: The properties of an alert payload.
    long-summary: |
        Usage:   --custom-properties ALERT_PAYLOAD_PROPERTIES [KEY=VAL,KEY=VAL ...]
  - name: --condition
    short-summary: The condition which triggers the rule.
    long-summary: |
        Usage:  --condition {avg,min,max,total,count} ["METRIC COLUMN" from]
                            "QUERY_PLACEHOLDER" {=,!=,>,>=,<,<=} THRESHOLD
                            [resource id RESOURCEID]
                            [where DIMENSION {includes,excludes} VALUE [or VALUE ...]
                            [and   DIMENSION {includes,excludes} VALUE [or VALUE ...] ...]]
                            [at least MinTimeToFail violations out of EvaluationPeriod aggregated points]'
        Query placeholders can be defined in --condition-query argument
        Dimensions can be queried by adding the 'where' keyword and multiple dimensions can be queried by combining them with the 'and' keyword.
examples:
  - name: Create a scheduled query for a VM.
    text: az monitor scheduled-query create -g {rg} -n {name1} --scopes {vm_id} --condition "count 'Placeholder_1' > 360 resource id _ResourceId at least 1 violations out of 5 aggregated points" --condition-query Placeholder_1="union Event, Syslog | where TimeGenerated > ago(1h) | where EventLevelName=='Error' or SeverityLevel=='err'" --description "Test rule"
  - name: Create a scheduled query for VMs in a resource group.
    text: az monitor scheduled-query create -g {rg} -n {name1} --scopes {rg_id} --condition "count 'Placeholder_1' > 360 resource id _ResourceId at least 1 violations out of 5 aggregated points" --condition-query Placeholder_1="union Event, Syslog | where TimeGenerated > ago(1h) | where EventLevelName=='Error' or SeverityLevel=='err'" --description "Test rule"
"""

helps['monitor scheduled-query update'] = """
type: command
short-summary: Update a scheduled query.
parameters:
  - name: --action-groups
  - name: --custom-properties
    short-summary: The properties of an alert payload.
    long-summary: |
        Usage:   --custom-properties ALERT_PAYLOAD_PROPERTIES [KEY=VAL,KEY=VAL ...]
  - name: --condition
    short-summary: The condition which triggers the rule.
    long-summary: |
        Usage:  --condition {avg,min,max,total,count} ["METRIC COLUMN" from]
                            "QUERY_PLACEHOLDER" {=,!=,>,>=,<,<=} THRESHOLD
                            [resource id RESOURCEID]
                            [where DIMENSION {includes,excludes} VALUE [or VALUE ...]
                            [and   DIMENSION {includes,excludes} VALUE [or VALUE ...] ...]]
                            [at least MinTimeToFail violations out of EvaluationPeriod aggregated points]'

        Query placeholders can be defined in --condition-query argument
        Dimensions can be queried by adding the 'where' keyword and multiple dimensions can be queried by combining them with the 'and' keyword.
"""

helps['monitor scheduled-query list'] = """
    type: command
    short-summary: List all scheduled queries.
"""

helps['monitor scheduled-query show'] = """
    type: command
    short-summary: Show detail of a scheduled query.
"""

helps['monitor scheduled-query delete'] = """
    type: command
    short-summary: Delete a scheduled query.
"""
