# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from knack.help_files import helps


helps['monitor alert-processing-rule'] = """
    type: group
    short-summary: Manage alert processing rule with alertsmanagement
"""

helps['monitor alert-processing-rule delete'] = """
    type: command
    short-summary: Delete an alert processing rule.
    examples:
      - name: Delete an alert processing rule.
        text: |-
              az monitor alert-processing-rule delete \\
              --resource-group myResourceGroup \\
              --name myRuleName
"""

helps['monitor alert-processing-rule update'] = """
    type: command
    short-summary: Enable, disable, or update tags for an alert processing rule.
    examples:
      - name: Disable an alert processing rule
        text: |-
              az monitor alert-processing-rule update \\
              --resource-group myResourceGroup \\
              --name myRuleName \\
              --enabled False
      - name: "Change tags on an alert processing rule."
        text: |-
              az monitor alert-processing-rule show \\
              --resource-group myResourceGroup \\
              --name myRuleName \\
              --tags key1=value1 key2=value2
      - name: "Change the description's value in an alert processing rule."
        text: |-
              az monitor alert-processing-rule show \\
              --resource-group myResourceGroup \\
              --name myRuleName \\
              --set properties.description="this is a new description"
"""

helps['monitor alert-processing-rule list'] = """
    type: command
    short-summary: List all alert processing rules in a subscription or resource group
    examples:
      - name: List all alert processing rules in current subscription
        text: |-
              az monitor alert-processing-rule list
      - name: List all alert processing rules in a resource group
        text: |-
              az monitor alert-processing-rule list \\
              --resource-group myResourceGroup
"""

helps['monitor alert-processing-rule show'] = """
    type: command
    short-summary: Get an alert processing rule.
    examples:
      - name: Get an alert processing rule by name
        text: |-
              az monitor alert-processing-rule show \\
              --name myRuleName \\
              --resource-group myRuleNameResourceGroup
      - name: Get alerts processing rule by ids
        text: |-
              az monitor alert-processing-rule show \\
              --ids ruleId1 ruleId2
"""

helps['monitor alert-processing-rule create'] = """
    type: command
    short-summary: Create an alert processing rule.
    parameters:
      - name: --filter-alert-context
        short-summary: Filter alerts by alert context (payload).
        long-summary: |
            Filter format is <operator> <space-delimited values> where
            Operator: one of <Equals, NotEquals, Contains, DoesNotContain>
            Values: List of values to match for a given condition
      - name: --schedule-recurrence
        short-summary: List of recurrence pattern values
        long-summary: |
            --schedule-recurrence              : List of recurrence pattern values (space-delimited).
            For a weekly recurrence type, allowed values are Sunday to Saturday.
            For a monthly recurrence type, allowed values are 1 to 31 (days of month)

      - name: --schedule-recurrence-2
        short-summary: List of recurrence pattern values for the second recurrence pattern.
        long-summary: |
              --schedule-recurrence-2              : List of recurrence pattern values (space-delimited).
              For a weekly recurrence type, allowed values are Sunday to Saturday.
              For a monthly recurrence type, allowed values are 1 to 31 (days of month)
    examples:
      - name: Create or update a rule that adds an action group to all alerts in a subscription
        text: |-
              az monitor alert-processing-rule create \\
              --name 'AddActionGroupToSubscription' \\
              --rule-type AddActionGroups \\
              --scopes "/subscriptions/MySubscriptionId" \\
              --action-groups "/subscriptions/MySubscriptionId/resourcegroups/MyResourceGroup1/providers/microsoft.insights/actiongroups/ActionGroup1" \\
              --enabled true \\
              --resource-group alertscorrelationrg \\
              --description "Add ActionGroup1 to all alerts in the subscription"

      - name: Create or update a rule that adds two action groups to all Sev0 and Sev1 alerts in two resource groups
        text: |-
              az monitor alert-processing-rule create \\
              --name 'AddActionGroupsBySeverity' \\
              --rule-type AddActionGroups \\
              --action-groups "/subscriptions/MySubscriptionId/resourcegroups/MyResourceGroup1/providers/microsoft.insights/actiongroups/MyActionGroupId1" "/subscriptions/MySubscriptionId/resourceGroups/MyResourceGroup2/providers/microsoft.insights/actionGroups/MyActionGroup2" \\
              --scopes "/subscriptions/MySubscriptionId" \\
              --resource-group alertscorrelationrg \\
              --filter-severity Equals Sev0 Sev1 \\
              --description "Add AGId1 and AGId2 to all Sev0 and Sev1 alerts in these resourceGroups"

      - name: Create or update a rule that removes all action groups from alerts on a specific VM during a one-off maintenance window (1800-2000 at a specific date, Pacific Standard Time)
        text: |-
              az monitor alert-processing-rule create \\
              --name 'RemoveActionGroupsMaintenanceWindow' \\
              --rule-type RemoveAllActionGroups \\
              --scopes "/subscriptions/MySubscriptionId/resourceGroups/MyResourceGroup1/providers/Microsoft.Compute/virtualMachines/VMName" \\
              --resource-group alertscorrelationrg \\
              --schedule-start-datetime '2022-01-02 18:00:00' \\
              --schedule-end-datetime '2022-01-02 20:00:00' \\
              --schedule-time-zone 'Pacific Standard Time' \\
              --description "Removes all ActionGroups from all Alerts on VMName during the maintenance window"

      - name: Create or update a rule that removes all action groups from all alerts in a subscription coming from a specific alert rule
        text: |-
              az monitor alert-processing-rule create \\
              --name 'RemoveActionGroupsSpecificAlertRule' \\
              --rule-type RemoveAllActionGroups \\
              --scopes "/subscriptions/MySubscriptionId" \\
              --resource-group alertscorrelationrg \\
              --filter-alert-rule-id Equals "/subscriptions/MySubscriptionId/resourceGroups/MyResourceGroup1/providers/microsoft.insights/activityLogAlerts/RuleName" \\
              --description "Removes all ActionGroups from all Alerts that fire on above AlertRule"

      - name: Create or update a rule that removes all action groups from all alerts on any VM in two resource groups during a recurring maintenance window (2200-0400 every Sat and Sun, India Standard Time)
        text: |-
              az monitor alert-processing-rule create \\
              --name 'RemoveActionGroupsRecurringMaintenance' \\
              --rule-type RemoveAllActionGroups \\
              --scopes "/subscriptions/MySubscriptionId/resourceGroups/MyResourceGroup1" "/subscriptions/MySubscriptionId/resourceGroups/MyResourceGroup2" \\
              --resource-group alertscorrelationrg \\
              --filter-resource-type Equals "microsoft.compute/virtualmachines" \\
              --schedule-time-zone "India Standard Time" \\
              --schedule-recurrence-type Weekly \\
              --schedule-recurrence-start-time "22:00:00" \\
              --schedule-recurrence-end-time "04:00:00" \\
              --schedule-recurrence Sunday Saturday \\
              --description "Remove all ActionGroups from all Virtual machine Alerts during the recurring maintenance"

      - name: Create or update a rule that removes all action groups outside business hours (Mon-Fri 09:00-17:00, Eastern Standard Time)
        text: |-
              az monitor alert-processing-rule create \\
              --name 'RemoveActionGroupsOutsideBusinessHours' \\
              --rule-type RemoveAllActionGroups \\
              --scopes "/subscriptions/MySubscriptionId" \\
              --resource-group alertscorrelationrg \\
              --schedule-time-zone "Eastern Standard Time" \\
              --schedule-recurrence-type Daily \\
              --schedule-recurrence-start-time "17:00:00" \\
              --schedule-recurrence-end-time "09:00:00" \\
              --schedule-recurrence-2-type Weekly \\
              --schedule-recurrence-2 Saturday Sunday \\
              --description "Remove all ActionGroups outside business hours"
"""

helps['monitor alert-processing-rule update'] = """
    type: command
    short-summary: Enable, disable, or update tags for an alert processing rule.
    examples:
      - name: PatchAlertProcessingRule
        text: |-
              az monitor alert-processing-rule update \\
              --name "WeeklySuppression" \\
              --enabled false \\
              --tags key1="value1" key2="value2" --resource-group "alertscorrelationrg"
"""
