# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['alertsmanagement'] = """
    type: group
    short-summary: Commands to manage alertsmanagement.
"""

helps['alertsmanagement list'] = """
    type: command
    short-summary: List all operations available through Azure Alerts Management Resource Provider.
"""

helps['alertsmanagement changestate'] = """
    type: group
    short-summary: Commands to manage alertsmanagement changestate.
"""

helps['alertsmanagement changestate change_state'] = """
    type: command
    short-summary: Change the state of an alert.
    examples:
      - name: Resolve
        text: |-
               az alertsmanagement changestate change_state --alert-id \\
               "66114d64-d9d9-478b-95c9-b789d6502100" --new-state "Acknowledged"
"""

helps['alertsmanagement changestate meta_data'] = """
    type: command
    short-summary: List alerts meta data information based on value of identifier parameter.
    examples:
      - name: MonService
        text: |-
               az alertsmanagement changestate meta_data --identifier "MonitorServiceList"
"""

helps['alertsmanagement changestate get_all'] = """
    type: command
    short-summary: List all existing alerts, where the results can be filtered on the basis of multiple parameters (e.g. time range). The results can then be sorted on the basis specific fields, with the default being lastModifiedDateTime. 
    examples:
      - name: ListAlerts
        text: |-
               az alertsmanagement changestate get_all
"""

helps['alertsmanagement changestate get_by_id'] = """
    type: command
    short-summary: Get information related to a specific alert
    examples:
      - name: GetById
        text: |-
               az alertsmanagement changestate get_by_id --alert-id \\
               "66114d64-d9d9-478b-95c9-b789d6502100"
"""

helps['alertsmanagement changestate get_history'] = """
    type: command
    short-summary: Get the history of an alert, which captures any monitor condition changes (Fired/Resolved) and alert state changes (New/Acknowledged/Closed).
    examples:
      - name: Resolve
        text: |-
               az alertsmanagement changestate get_history --alert-id \\
               "66114d64-d9d9-478b-95c9-b789d6502100"
"""

helps['alertsmanagement changestate get_summary'] = """
    type: command
    short-summary: Get a summarized count of your alerts grouped by various parameters (e.g. grouping by 'Severity' returns the count of alerts for each severity).
    examples:
      - name: Summary
        text: |-
               az alertsmanagement changestate get_summary --groupby "severity,alertState"
"""

helps['alertsmanagement change-state'] = """
    type: group
    short-summary: Commands to manage alertsmanagement change state.
"""

helps['alertsmanagement change-state change_state'] = """
    type: command
    short-summary: Change the state of a Smart Group.
    examples:
      - name: changestate
        text: |-
               az alertsmanagement change-state change_state --smart-group-id \\
               "a808445e-bb38-4751-85c2-1b109ccc1059" --new-state "Acknowledged"
"""

helps['alertsmanagement change-state get_all'] = """
    type: command
    short-summary: List all the Smart Groups within a specified subscription. 
    examples:
      - name: List
        text: |-
               az alertsmanagement change-state get_all
"""

helps['alertsmanagement change-state get_by_id'] = """
    type: command
    short-summary: Get information related to a specific Smart Group.
    examples:
      - name: Get
        text: |-
               az alertsmanagement change-state get_by_id --smart-group-id \\
               "603675da-9851-4b26-854a-49fc53d32715"
"""

helps['alertsmanagement change-state get_history'] = """
    type: command
    short-summary: Get the history a smart group, which captures any Smart Group state changes (New/Acknowledged/Closed) .
    examples:
      - name: Resolve
        text: |-
               az alertsmanagement change-state get_history --smart-group-id \\
               "a808445e-bb38-4751-85c2-1b109ccc1059"
"""

helps['alertsmanagement'] = """
    type: group
    short-summary: Commands to manage alertsmanagement.
"""

helps['alertsmanagement create'] = """
    type: command
    short-summary: Creates/Updates a specific action rule
    examples:
      - name: PutActionRule
        text: |-
               az alertsmanagement create --resource-group "alertscorrelationrg" --name \\
               "DailySuppression" --location "Global" --status "Enabled"
"""

helps['alertsmanagement update'] = """
    type: command
    short-summary: Creates/Updates a specific action rule
    examples:
      - name: PatchActionRule
        text: |-
               az alertsmanagement update --resource-group "alertscorrelationrg" --name \\
               "WeeklySuppression" --status "Disabled"
"""

helps['alertsmanagement delete'] = """
    type: command
    short-summary: Deletes a given action rule
    examples:
      - name: DeleteActionRule
        text: |-
               az alertsmanagement delete --resource-group "alertscorrelationrg" --name \\
               "DailySuppression"
"""

helps['alertsmanagement show'] = """
    type: command
    short-summary: Get a specific action rule
    examples:
      - name: GetActionRuleById
        text: |-
               az alertsmanagement show --resource-group "alertscorrelationrg" --name "DailySuppression"
"""

helps['alertsmanagement list'] = """
    type: command
    short-summary: List all action rules of the subscription, created in given resource group and given input filters
    examples:
      - name: GetActionRulesSubscriptionWide
        text: |-
               az alertsmanagement list
      - name: GetActionRulesResourceGroupWide
        text: |-
               az alertsmanagement list --resource-group "alertscorrelationrg"
"""

helps['alertsmanagement'] = """
    type: group
    short-summary: Commands to manage alertsmanagement.
"""

helps['alertsmanagement create'] = """
    type: command
    short-summary: Create or update a Smart Detector alert rule.
    examples:
      - name: Create or update a Smart Detector alert rule
        text: |-
               az alertsmanagement create --resource-group "MyAlertRules" --name "MyAlertRule" \\
               --description "Sample smart detector alert rule description" --state "Enabled" --severity \\
               "Sev3" --frequency "PT5M"
"""

helps['alertsmanagement update'] = """
    type: command
    short-summary: Create or update a Smart Detector alert rule.
    examples:
      - name: Patch alert rules
        text: |-
               az alertsmanagement update --resource-group "MyAlertRules" --name "MyAlertRule" \\
               --description "New description for patching" --frequency "PT1M"
"""

helps['alertsmanagement delete'] = """
    type: command
    short-summary: Delete an existing Smart Detector alert rule.
    examples:
      - name: Delete a Smart Detector alert rule
        text: |-
               az alertsmanagement delete --resource-group "MyAlertRules" --name "MyAlertRule"
"""

helps['alertsmanagement show'] = """
    type: command
    short-summary: Get a specific Smart Detector alert rule.
    examples:
      - name: Get a Smart Detector alert rule
        text: |-
               az alertsmanagement show --resource-group "MyAlertRules" --name "MyAlertRule"
"""

helps['alertsmanagement list'] = """
    type: command
    short-summary: List all the existing Smart Detector alert rules within the subscription and resource group.
    examples:
      - name: List Smart Detector alert rules
        text: |-
               az alertsmanagement list --resource-group "MyAlertRules"
      - name: List alert rules
        text: |-
               az alertsmanagement list --resource-group "MyAlertRules"
"""
