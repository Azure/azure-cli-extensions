# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['alertsmanagement operation'] = """
    type: group
    short-summary: Commands to manage alertsmanagement operation.
"""

helps['alertsmanagement operation list'] = """
    type: command
    short-summary: List all operations available through Azure Alerts Management Resource Provider.
"""

helps['alertsmanagement alert'] = """
    type: group
    short-summary: Commands to manage alertsmanagement alert.
"""

helps['alertsmanagement alert change-state'] = """
    type: command
    short-summary: Change the state of an alert.
    examples:
      - name: Resolve
        text: |-
               az alertsmanagement alert change-state --alert-id "66114d64-d9d9-478b-95c9-b789d6502100" \\
               --new-state "Acknowledged"
"""

helps['alertsmanagement alert meta-data'] = """
    type: command
    short-summary: List alerts meta data information based on value of identifier parameter.
    examples:
      - name: MonService
        text: |-
               az alertsmanagement alert meta-data --identifier "MonitorServiceList"
"""

helps['alertsmanagement alert get-all'] = """
    type: command
    short-summary: List all existing alerts, where the results can be filtered on the basis of multiple parameters (e.g. time range). The results can then be sorted on the basis specific fields, with the default being lastModifiedDateTime.
    examples:
      - name: ListAlerts
        text: |-
               az alertsmanagement alert get-all
"""

helps['alertsmanagement alert get-by-id'] = """
    type: command
    short-summary: Get information related to a specific alert
    examples:
      - name: GetById
        text: |-
               az alertsmanagement alert get-by-id --alert-id "66114d64-d9d9-478b-95c9-b789d6502100"
"""

helps['alertsmanagement alert get-history'] = """
    type: command
    short-summary: Get the history of an alert, which captures any monitor condition changes (Fired/Resolved) and alert state changes (New/Acknowledged/Closed).
    examples:
      - name: Resolve
        text: |-
               az alertsmanagement alert get-history --alert-id "66114d64-d9d9-478b-95c9-b789d6502100"
"""

helps['alertsmanagement alert get-summary'] = """
    type: command
    short-summary: Get a summarized count of your alerts grouped by various parameters (e.g. grouping by 'Severity' returns the count of alerts for each severity).
    examples:
      - name: Summary
        text: |-
               az alertsmanagement alert get-summary --groupby "severity,alertState"
"""

helps['alertsmanagement smart-group'] = """
    type: group
    short-summary: Commands to manage alertsmanagement smart group.
"""

helps['alertsmanagement smart-group change-state'] = """
    type: command
    short-summary: Change the state of a Smart Group.
    examples:
      - name: changestate
        text: |-
               az alertsmanagement smart-group change-state --smart-group-id \\
               "a808445e-bb38-4751-85c2-1b109ccc1059" --new-state "Acknowledged"
"""

helps['alertsmanagement smart-group get-all'] = """
    type: command
    short-summary: List all the Smart Groups within a specified subscription.
    examples:
      - name: List
        text: |-
               az alertsmanagement smart-group get-all
"""

helps['alertsmanagement smart-group get-by-id'] = """
    type: command
    short-summary: Get information related to a specific Smart Group.
    examples:
      - name: Get
        text: |-
               az alertsmanagement smart-group get-by-id --smart-group-id \\
               "603675da-9851-4b26-854a-49fc53d32715"
"""

helps['alertsmanagement smart-group get-history'] = """
    type: command
    short-summary: Get the history a smart group, which captures any Smart Group state changes (New/Acknowledged/Closed) .
    examples:
      - name: Resolve
        text: |-
               az alertsmanagement smart-group get-history --smart-group-id \\
               "a808445e-bb38-4751-85c2-1b109ccc1059"
"""

helps['alertsmanagement action-rule'] = """
    type: group
    short-summary: Commands to manage alertsmanagement action rule.
"""

helps['alertsmanagement action-rule create'] = """
    type: command
    short-summary: Creates/Updates a specific action rule
    examples:
      - name: PutActionRule
        text: |-
               az alertsmanagement action-rule create --resource-group "alertscorrelationrg" --name "rule" --location "Global" --status "Enabled" --rule-type Suppression --severity Equals Sev0 Sev2 --recurrence-type Daily --start-date 12/09/2018 --end-date 12/18/2018 --start-time 06:00:00 --end-time 14:00:00

"""

helps['alertsmanagement action-rule update'] = """
    type: command
    short-summary: Creates/Updates a specific action rule
    examples:
      - name: PatchActionRule
        text: |-
               az alertsmanagement action-rule update --resource-group "alertscorrelationrg" --name \\
               "WeeklySuppression" --status "Disabled"
"""

helps['alertsmanagement action-rule delete'] = """
    type: command
    short-summary: Deletes a given action rule
    examples:
      - name: DeleteActionRule
        text: |-
               az alertsmanagement action-rule delete --resource-group "alertscorrelationrg" --name \\
               "DailySuppression"
"""

helps['alertsmanagement action-rule show'] = """
    type: command
    short-summary: Get a specific action rule
    examples:
      - name: GetActionRuleById
        text: |-
               az alertsmanagement action-rule show --resource-group "alertscorrelationrg" --name \\
               "DailySuppression"
"""

helps['alertsmanagement action-rule list'] = """
    type: command
    short-summary: List all action rules of the subscription, created in given resource group and given input filters
    examples:
      - name: GetActionRulesSubscriptionWide
        text: |-
               az alertsmanagement action-rule list
      - name: GetActionRulesResourceGroupWide
        text: |-
               az alertsmanagement action-rule list --resource-group "alertscorrelationrg"
"""

helps['alertsmanagement smart-detector-alert-rule'] = """
    type: group
    short-summary: Commands to manage alertsmanagement smart detector alert rule.
"""

helps['alertsmanagement smart-detector-alert-rule create'] = """
    type: command
    short-summary: Create or update a Smart Detector alert rule.
    examples:
      - name: Create or update a Smart Detector alert rule
        text: |-
               az alertsmanagement smart-detector-alert-rule create --resource-group "MyAlertRules" \\
               --name "MyAlertRule" --description "Sample smart detector alert rule description" --state \\
               "Enabled" --severity "Sev3" --frequency "PT5M"
"""

helps['alertsmanagement smart-detector-alert-rule update'] = """
    type: command
    short-summary: Create or update a Smart Detector alert rule.
    examples:
      - name: Patch alert rules
        text: |-
               az alertsmanagement smart-detector-alert-rule update --resource-group "MyAlertRules" \\
               --name "MyAlertRule" --description "New description for patching" --frequency "PT1M"
"""

helps['alertsmanagement smart-detector-alert-rule delete'] = """
    type: command
    short-summary: Delete an existing Smart Detector alert rule.
    examples:
      - name: Delete a Smart Detector alert rule
        text: |-
               az alertsmanagement smart-detector-alert-rule delete --resource-group "MyAlertRules" \\
               --name "MyAlertRule"
"""

helps['alertsmanagement smart-detector-alert-rule show'] = """
    type: command
    short-summary: Get a specific Smart Detector alert rule.
    examples:
      - name: Get a Smart Detector alert rule
        text: |-
               az alertsmanagement smart-detector-alert-rule show --resource-group "MyAlertRules" --name \\
               "MyAlertRule"
"""

helps['alertsmanagement smart-detector-alert-rule list'] = """
    type: command
    short-summary: List all the existing Smart Detector alert rules within the subscription and resource group.
    examples:
      - name: List Smart Detector alert rules
        text: |-
               az alertsmanagement smart-detector-alert-rule list --resource-group "MyAlertRules"
      - name: List alert rules
        text: |-
               az alertsmanagement smart-detector-alert-rule list --resource-group "MyAlertRules"
"""
