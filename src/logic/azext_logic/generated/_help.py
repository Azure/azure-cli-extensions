# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from knack.help_files import helps


helps['logic workflow'] = """
    type: group
    short-summary: logic workflow
"""

helps['logic workflow list'] = """
    type: command
    short-summary: Gets a list of workflows by subscription.
    examples:
      - name: List all workflows in a resource group
        text: |-
               az logic workflow list --resource-group "test_resource_group"
      - name: List all workflows in a subscription
        text: |-
               az logic workflow list
"""

helps['logic workflow show'] = """
    type: command
    short-summary: Gets a workflow.
    examples:
      - name: Get a workflow
        text: |-
               az logic workflow show --resource-group "test_resource_group" --name "test_workflow"
"""

helps['logic workflow create'] = """
    type: command
    short-summary: Creates or updates a workflow using a JSON file for the defintion.
    examples:
      - name: Create or update a workflow
        text: |-
               az logic workflow create --resource-group "test_resource_group" --location "centralus" --name "test_workflow" --definition "workflow.json"
"""

helps['logic workflow update'] = """
    type: command
    short-summary: Updates a workflow.
    examples:
      - name: Patch a workflow
        text: |-
               az logic workflow update --resource-group "test_resource_group" --definition workflow.json --name "test_workflow"
"""

helps['logic workflow delete'] = """
    type: command
    short-summary: Deletes a workflow.
    examples:
      - name: Delete a workflow
        text: |-
               az logic workflow delete --resource-group "test_resource_group" --name "test_workflow"
"""

helps['logic integration-account'] = """
    type: group
    short-summary: logic integration-account
"""

helps['logic integration-account list'] = """
    type: command
    short-summary: Gets a list of integration accounts by subscription.
    examples:
      - name: List integration accounts by resource group name
        text: |-
               az logic integration-account list --resource-group "test_resource_group"
"""

helps['logic integration-account show'] = """
    type: command
    short-summary: Gets an integration account.
    examples:
      - name: Get integration account by name
        text: |-
               az logic integration-account show --name "test_integration_account" --resource-group "test_resource_group"
"""

helps['logic integration-account create'] = """
    type: command
    short-summary: Creates or updates an integration account.
    examples:
      - name: Create or update an integration account
        text: |-
               az logic integration-account create --location "centralus" --sku name=Standard --name "test_integration_account" --resource-group "test_resource_group"
"""

helps['logic integration-account update'] = """
    type: command
    short-summary: Updates an integration account.
    examples:
      - name: Patch an integration account
        text: |-
               az logic integration-account update --sku name=Basic --tag atag=123 --name "test_integration_account" --resource-group "test_resource_group"
"""


helps['logic integration-account import'] = """
    type: command
    short-summary: Import an integration account from a JSON file.
    examples:
      - name: Import an integration account.
        text: |-
               az logic integration-account import --name "test_integration_account" --resource-group "test_resource_group" --input-path "integration.json"
"""

helps['logic integration-account delete'] = """
    type: command
    short-summary: Deletes an integration account.
    examples:
      - name: Delete an integration account
        text: |-
               az logic integration-account delete --name "test_integration_account" --resource-group "test_resource_group"
"""
