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
      - name: Create an action rule to suppress notifications for all Sev4 alerts on all VMs within the subscription every weekend
        text: |-
               az monitor action-rule create --resource-group rg --name rule --location Global --status Enabled --rule-type Suppression --severity Equals Sev4 --target-resource-type Equals Microsoft.Compute/VirtualMachines --suppression-recurrence-type Weekly --suppression-recurrence 0 6 --suppression-start-date 12/09/2018 --suppression-end-date 12/18/2018 --suppression-start-time 06:00:00 --suppression-end-time 14:00:00
      - name: Create an action rule to suppress notifications for all log alerts generated for Computer-01 in subscription indefinitely as it's going through maintenance
        text: |-
               az monitor action-rule create --resource-group rg --name rule --location Global --status Enabled --rule-type Suppression --suppression-recurrence-type Always --alert-context Contains Computer-01 --monitor-service Equals "Log Analytics"
      - name: Create an action rule to suppress notifications in a resource group
        text: |-
               az monitor action-rule create --resource-group rg --name rule --location Global --status Enabled --rule-type Suppression --scope-type ResourceGroup --scope /subscriptions/0b1f6471-1bf0-4dda-aec3-cb9272f09590/resourceGroups/rg --suppression-recurrence-type Always --alert-context Contains Computer-01 --monitor-service Equals "Log Analytics"
"""

helps['monitor action-rule update'] = """
    type: command
    short-summary: Update an action rule
    examples:
      - name: Update an action rule
        text: |-
               az monitor action-rule update --resource-group rg --name rule --status Disabled
"""

helps['monitor action-rule delete'] = """
    type: command
    short-summary: Delete an action rule
    examples:
      - name: Delete an action rule
        text: |-
               az monitor action-rule delete --resource-group rg --name rule
"""

helps['monitor action-rule show'] = """
    type: command
    short-summary: Get an action rule
    examples:
      - name: Get an action rule
        text: |-
               az monitor action-rule show --resource-group rg --name rule
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
               az monitor action-rule list --resource-group rg
"""
