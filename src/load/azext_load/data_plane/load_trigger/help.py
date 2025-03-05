# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

helps = {}

helps[
    "load trigger schedule create"
] = """
type: command
short-summary: Create a new load trigger schedule.
examples:
    - name: Create schedule.
      text: |
        az load trigger schedule create --load-test-resource sample-alt-resource --resource-group sample-rg --trigger-id sample-trigger-id --description "Sample description" --display-name "Sample display name" --start-date-time 2023-01-01T15:16:17Z --recurrence-type Daily --recurrence-properties '{"interval":1}' --end-after-occurrence 5 --test-ids sample-test-id
"""

helps[
    "load trigger schedule update"
] = """
type: command
short-summary: Update a load trigger schedule.
examples:
    - name: Update schedule.
      text: |
        az load trigger schedule update --load-test-resource sample-alt-resource --resource-group sample-rg --trigger-id sample-trigger-id --display-name "Updated display name"
    
"""

helps[
    "load trigger schedule delete"
] = """
type: command
short-summary: Delete a load trigger schedule.
examples:
    - name: Delete schedule.
      text: |
        az load trigger schedule delete --load-test-resource sample-alt-resource --resource-group sample-rg --trigger-id sample-trigger-id
"""

helps[
    "load trigger schedule show"
] = """
type: command
short-summary: Show details of a load trigger schedule.
examples:
    - name: Show schedule.
      text: |
        az load trigger schedule show --load-test-resource sample-alt-resource --resource-group sample-rg --trigger-id sample-trigger-id
""" 

helps[
    "load trigger schedule pause"
] = """
type: command
short-summary: Pause a load trigger schedule.
examples:
    - name: Pause schedule.
      text: |
        az load trigger schedule pause --load-test-resource sample-alt-resource --resource-group sample-rg --trigger-id sample-trigger-id
""" 

helps[
    "load trigger schedule enable"
] = """
type: command
short-summary: Enable a load trigger schedule.
examples:
    - name: Enable schedule.
      text: |
        az load trigger schedule enable --load-test-resource sample-alt-resource --resource-group sample-rg --trigger-id sample-trigger-id
"""

helps[
    "load trigger schedule list"
] = """
type: command
short-summary: List all load trigger schedules.
examples:
    - name: List schedule.
      text: |
        az load trigger schedule list --load-test-resource sample-alt-resource --resource-group sample-rg --test-ids sample-test-id1 sample-test-id2 --states Active
"""