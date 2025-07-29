# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

helps = {}

helps[
    "load notification-rule create"
] = """
type: command
short-summary: Create a new notification rule for load test resource.
examples:
    - name: Create a notification rule for all events.
      text: |
        az load notification-rule create --load-test-resource sample-alt-resource --resource-group sample-rg --action-groups /subscriptions/000000-0000-0000-0000-000000000000/resourcegroups/sample-rg/providers/microsoft.insights/actiongroups/sample-ag --notification-rule-id notification-sample-id --all-events
    - name: Create a notification rule for all tests and TestRunEnded event.
      text: |
        az load notification-rule create --load-test-resource sample-alt-resource --resource-group sample-rg --action-groups /subscriptions/000000-0000-0000-0000-000000000000/resourcegroups/sample-rg/providers/microsoft.insights/actiongroups/sample-ag --notification-rule-id notification-sample-id --all-tests --event event-id=event1 type=TestRunEnded status=DONE,FAILED result=PASSED
"""

helps[
    "load notification-rule update"
] = """
type: command
short-summary: Update an existing notification rule for load test resource.
examples:
    - name: Update a notification rule enabled for all tests.
      text: |
        az load notification-rule update --load-test-resource sample-alt-resource --resource-group sample-rg --notification-rule-id notification-sample-id --all-tests
    - name: Add a TestRunStarted event to an existing notification rule.
      text: |
        az load notification-rule update --load-test-resource sample-alt-resource --resource-group sample-rg --notification-rule-id notification-sample-id --add-event event-id=event1 type=TestRunStarted
    - name: Remove an event from an existing notification rule and update the action group list.
      text: |
        az load notification-rule update --load-test-resource sample-alt-resource --resource-group sample-rg --notification-rule-id notification-sample-id --remove-event event-id=event1 --action-groups /subscriptions/000000-0000-0000-0000-000000000000/resourcegroups/sample-rg/providers/microsoft.insights/actiongroups/sample-ag
"""

helps[
    "load notification-rule show"
] = """
type: command
short-summary: Get the specified notification rule for load test resource.
examples:
    - name: Get a notification rule.
      text: |
        az load notification-rule show --load-test-resource sample-alt-resource --resource-group sample-rg --notification-rule-id notification-sample-id
"""

helps[
    "load notification-rule delete"
] = """
type: command
short-summary: Delete the specified notification rule for load test resource.
examples:
    - name: Delete a notification rule.
      text: |
        az load notification-rule delete --load-test-resource sample-alt-resource --resource-group sample-rg --notification-rule-id notification-sample-id --yes
"""

helps[
    "load notification-rule list"
] = """
type: command
short-summary: List all the notification rules for load test resource.
examples:
    - name: List all notification rules.
      text: |
        az load notification-rule list --load-test-resource sample-alt-resource --resource-group sample-rg
    - name: List all notification rules for the specified test IDs.
      text: |
        az load notification-rule list --load-test-resource sample-alt-resource --resource-group sample-rg --test-ids sample-test-id
"""
