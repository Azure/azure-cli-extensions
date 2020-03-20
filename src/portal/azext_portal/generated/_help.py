# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from knack.help_files import helps


helps['portal dashboard'] = """
    type: group
    short-summary: portal dashboard
"""

helps['portal dashboard list'] = """
    type: command
    short-summary: Gets all the dashboards within a subscription.
    examples:
      - name: List all custom resource providers on the resourceGroup
        text: |-
               az portal dashboard list --resource-group "testRG"
"""

helps['portal dashboard show'] = """
    type: command
    short-summary: Gets the Dashboard.
    examples:
      - name: Get a Dashboard
        text: |-
               az portal dashboard show --name "testDashboard" --resource-group "testRG"
"""

helps['portal dashboard create'] = """
    type: command
    short-summary: Creates or updates a Dashboard.
    examples:
      - name: Create or update a Dashboard
        text: |-
               az portal dashboard create --location "eastus" --name "testDashboard"
               --resource-group "testRG" --input-path "/src/json/properties.json"
               --tags aKey=aValue anotherKey=anotherValue
"""

helps['portal dashboard update'] = """
    type: command
    short-summary: Updates an existing Dashboard.
    examples:
      - name: Update a Dashboard
        text: |-
               az portal dashboard update --name "testDashboard" --resource-group "testRG"
               --input-path "/src/json/properties.json"
"""

helps['portal dashboard delete'] = """
    type: command
    short-summary: Deletes the Dashboard.
    examples:
      - name: Delete a Dashboard
        text: |-
               az portal dashboard delete --name "testDashboard" --resource-group "testRG"
"""

helps['portal dashboard import'] = """
    type: command
    short-summary: Imports the Dashboard.
    examples:
      - name: Import a Dashboard
        text: |-
               az portal dashboard import --name "testDashboard" --resource-group "testRG"
               --input-path "/src/json/dashboard.json"
"""
