# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['monitor action-rule'] = """
    type: group
    short-summary: Commands to manage action rule.
"""

helps['monitor action-rule create'] = """
    type: command
    short-summary: Create an action rule
    examples:
      - name: Create an action rule with suppression type
        text: |-
               az monitor action-rule create --resource-group "rg" --name "rule" --location "Global" --status "Enabled" --rule-type Suppression --severity Equals Sev0 Sev2 --recurrence-type Daily --suppression-start-date 12/09/2018 --suppression-end-date 12/18/2018 --suppression-start-time 06:00:00 --suppression-end-time 14:00:00

"""

helps['monitor action-rule update'] = """
    type: command
    short-summary: Update an action rule
    examples:
      - name: Update an action rule
        text: |-
               az monitor action-rule update --resource-group "rg" --name "rule" --status "Disabled"
"""

helps['monitor action-rule delete'] = """
    type: command
    short-summary: Delete an action rule
    examples:
      - name: Delete an action rule
        text: |-
               az monitor action-rule delete --resource-group "rg" --name "rule"
"""

helps['monitor action-rule show'] = """
    type: command
    short-summary: Get a specific action rule
    examples:
      - name: Get a specific action rule
        text: |-
               az monitor action-rule show --resource-group "rg" --name "rule"
"""

helps['monitor action-rule list'] = """
    type: command
    short-summary: List all action rules of the subscription, created in given resource group and given input filters
    examples:
      - name: List action rules of the subscription
        text: |-
               az monitor action-rule list
      - name: List action rules of the resource group
        text: |-
               az monitor action-rule list --resource-group "rg"
"""
