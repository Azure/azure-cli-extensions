# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

# pylint: disable=line-too-long

helps['monitor log-analytics'] = """
    type: group
    short-summary: Commands for querying data in Log Analytics workspaces.
"""

helps['monitor log-analytics query'] = """
    type: command
    short-summary: Query a Log Analytics workspace.
    examples:
      - name: Execute a simple query over past 3.5 days.
        text: |
          az monitor log-analytics query -w workspace-customId --analytics-query "AzureActivity | summarize count() by bin(TimeGenerated, 1h)" -t P3DT12H
      - name: Execute a saved query in workspace
        text: |
          QUERY=$(az monitor log-analytics workspace saved-search show -g resource-group --workspace-name workspace-name -n query-name --query query --output tsv)
          az monitor log-analytics query -w workspace-customId --analytics-query "$QUERY"
"""
