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
  - name: --action -a
    short-summary: Add an action group and optional webhook properties to fire when the alert is triggered.
    long-summary: |
        Usage:   --action ACTION_GROUP_NAME_OR_ID [KEY=VAL [KEY=VAL ...]]

        Multiple action groups can be specified by using more than one `--action` argument.
  - name: --condition
    short-summary: The condition which triggers the rule.
    long-summary: |
        Usage:  --condition {avg,min,max,total,count} METRIC {=,!=,>,>=,<,<=} THRESHOLD
                           [where DIMENSION {includes,excludes} VALUE [or VALUE ...]
                           [and   DIMENSION {includes,excludes} VALUE [or VALUE ...] ...]]

        Dimensions can be queried by adding the 'where' keyword and multiple dimensions can be queried by combining them with the 'and' keyword.

        Values for METRIC, DIMENSION and appropriate THRESHOLD values can be obtained from `az monitor metrics list-definitions` command.

"""

helps['monitor scheduled-query list'] = """
    type: command
    short-summary: List all scheduled queries.
"""
