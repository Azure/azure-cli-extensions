# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from knack.help_files import helps  # pylint: disable=unused-import


helps['monitor trace-association'] = """
    type: group
    short-summary: Manage trace associations that route a scope's traces to an Azure Monitor Workspace.
    long-summary: >
        A trace association (Microsoft.Monitor/traceAssociations) is an ARM extension resource
        mapping a scope (Application Insights component, resource group, or subscription) to an
        Azure Monitor Workspace. Each scope has at most one direct association (singleton 'default').
"""

helps['monitor trace-association create'] = """
    type: command
    short-summary: Create or update the trace association for a scope.
    examples:
      - name: Route an Application Insights component's traces to an Azure Monitor Workspace.
        text: |
            az monitor trace-association create \\
              --resource-uri "subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myRg/providers/Microsoft.Insights/components/myAppInsights" \\
              --azure-monitor-workspace-resource-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/obs-rg/providers/Microsoft.Monitor/accounts/app-amw"
"""

helps['monitor trace-association update'] = """
    type: command
    short-summary: Update the trace association for a scope.
"""

helps['monitor trace-association show'] = """
    type: command
    short-summary: Show the trace association for a scope.
"""

helps['monitor trace-association delete'] = """
    type: command
    short-summary: Delete the trace association for a scope.
"""

helps['monitor trace-association list'] = """
    type: command
    short-summary: List trace associations for a scope.
"""
