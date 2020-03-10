# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['alertsmanagement action-rule'] = """
    type: group
    short-summary: Commands to manage alertsmanagement action rule.
"""

helps['alertsmanagement action-rule create'] = """
    type: command
    short-summary: Creates/Updates a specific action rule
    examples:
      - name: Create an action rule.
        text: |-
               az alertsmanagement action-rule create --resource-group "alertscorrelationrg" --name "rule" --location "Global" --status "Enabled" --rule-type Suppression --severity Equals Sev0 Sev2 --recurrence-type Daily --start-date 12/09/2018 --end-date 12/18/2018 --start-time 06:00:00 --end-time 14:00:00

"""

helps['alertsmanagement action-rule update'] = """
    type: command
    short-summary: Creates/Updates a specific action rule
    examples:
      - name: Update an action rule.
        text: |-
               az alertsmanagement action-rule update --resource-group "alertscorrelationrg" --name \\
               "WeeklySuppression" --status "Disabled"
"""

helps['alertsmanagement action-rule delete'] = """
    type: command
    short-summary: Delete a given action rule
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
      - name: List action rules of the subscription
        text: |-
               az alertsmanagement action-rule list
      - name: List action rules of the resource group
        text: |-
               az alertsmanagement action-rule list --resource-group "alertscorrelationrg"
"""
