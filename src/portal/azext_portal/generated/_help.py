# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from knack.help_files import helps


helps['portal dashboard'] = """
    type: group
    short-summary: Manage portal dashboards
"""

helps['portal dashboard list'] = """
    type: command
    short-summary: Lists the dashboards within a subscription or resource group.
    examples:
      - name: List all dashboards in a resourceGroup
        text: |-
               az portal dashboard list --resource-group "testRG"
      - name: List all dashboards in a subscription
        text: |-
               az portal dashboard list
"""

helps['portal dashboard show'] = """
    type: command
    short-summary: Gets details for a single dashboard.
    examples:
      - name: Get a Dashboard
        text: |-
               az portal dashboard show --name "testDashboard" --resource-group "testRG"
"""

helps['portal dashboard create'] = """
    type: command
    short-summary: Creates or updates a dashboard.
    examples:
      - name: Create or update a Dashboard
        text: |-
               az portal dashboard create --location "eastus" --name "testDashboard" \\
               --resource-group "testRG" --input-path "/src/json/properties.json" \\
               --tags aKey=aValue anotherKey=anotherValue
"""

helps['portal dashboard update'] = """
    type: command
    short-summary: Updates an existing dashboard.
    examples:
      - name: Update a Dashboard
        text: |-
               az portal dashboard update --name "testDashboard" --resource-group "testRG" \\
               --input-path "/src/json/properties.json"
"""

helps['portal dashboard delete'] = """
    type: command
    short-summary: Deletes a dashboard.
    examples:
      - name: Delete a Dashboard
        text: |-
               az portal dashboard delete --name "testDashboard" --resource-group "testRG"
"""

helps['portal dashboard import'] = """
    type: command
    short-summary: Imports a dashboard from a JSON file.
    examples:
      - name: Import a Dashboard
        text: |-
               az portal dashboard import --name "testDashboard" --resource-group "testRG" \\
               --input-path "/src/json/dashboard.json"
"""
