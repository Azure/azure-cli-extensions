# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['monitor log-analytics solution'] = """
type: group
short-summary: Commands to manage monitor log-analytics solution.
"""

helps['monitor log-analytics solution create'] = """
type: command
short-summary: Create a log-analytics solution.
examples:
  - name: Create a log-analytics solution for the plan product of OMSGallery/Containers
    text: |-
           az monitor log-analytics solution create --resource-group MyResourceGroup \\
           --name Containers({SolutionName}) --tags key=value \\
           --plan-publisher Microsoft --plan-product "OMSGallery/Containers" \\
           --workspace "/subscriptions/{SubID}/resourceGroups/{ResourceGroup}/providers/ \\
           Microsoft.OperationalInsights/workspaces/{WorkspaceName}"
"""

helps['monitor log-analytics solution update'] = """
type: command
short-summary:  Update an existing log-analytics solution.
examples:
  - name: Update a log-analytics solution
    text: |-
           az monitor log-analytics solution update --resource-group MyResourceGroup \\
           --name SolutionName --tags key=value
"""

helps['monitor log-analytics solution delete'] = """
type: command
short-summary: Delete a log-analytics solution.
examples:
  - name: Delete a log-analytics solution
    text: |-
           az monitor log-analytics solution delete --resource-group MyResourceGroup --name SolutionName
"""

helps['monitor log-analytics solution show'] = """
type: command
short-summary: Get details about the specified log-analytics solution.
examples:
  - name: Get a log-analytics solution
    text: |-
           az monitor log-analytics solution show --resource-group MyResourceGroup --name SolutionName
"""

helps['monitor log-analytics solution list'] = """
type: command
short-summary: List all of the log-analytics solutions in the specified subscription or resource group
examples:
  - name: List all log-analytics solutions in the current subscription
    text: |-
           az monitor log-analytics solution list
  - name: List all log-analytics solutions in a subscription
    text: |-
           az monitor log-analytics solution list --subscription MySubscription
  - name: List all log-analytics solutions in a resource group
    text: |-
           az monitor log-analytics solution list --resource-group MyResourceGroup
"""
