# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['aimanager'] = """
    type: group
    short-summary: Manage AI Manager resources for inference on AKS.
"""

helps['aimanager create'] = """
    type: command
    short-summary: Create an AI Manager resource.
    examples:
        - name: Create an AI Manager
          text: az aimanager create --name my-ai-manager -g myrg -l eastus2
        - name: Create an AI Manager with the Keep delete policy
          text: az aimanager create --name my-ai-manager -g myrg -l eastus2 --delete-policy Keep
"""

helps['aimanager update'] = """
    type: command
    short-summary: Update an AI Manager resource.
    examples:
        - name: Update the tags of an AI Manager
          text: az aimanager update --name my-ai-manager -g myrg --tags env=prod team=alpha
        - name: Update the delete policy of an AI Manager
          text: az aimanager update --name my-ai-manager -g myrg --delete-policy Keep
"""

helps['aimanager show'] = """
    type: command
    short-summary: Show the details of an AI Manager resource.
    examples:
        - name: Show an AI Manager
          text: az aimanager show --name my-ai-manager -g myrg
"""

helps['aimanager delete'] = """
    type: command
    short-summary: Delete an AI Manager resource.
    examples:
        - name: Delete an AI Manager
          text: az aimanager delete --name my-ai-manager -g myrg
"""

helps['aimanager list'] = """
    type: command
    short-summary: List AI Manager resources.
    examples:
        - name: List AI Managers in a resource group
          text: az aimanager list -g myrg
        - name: List all AI Managers in the subscription
          text: az aimanager list
"""

helps['aimanager wait'] = """
    type: command
    short-summary: Wait for an AI Manager resource to reach a desired state.
"""

helps['aimanager namespace'] = """
    type: group
    short-summary: Manage namespaces within an AI Manager.
"""

helps['aimanager namespace add'] = """
    type: command
    short-summary: Add a namespace to an AI Manager.
    examples:
        - name: Add a namespace
          text: az aimanager namespace add -m my-ai-manager -g myrg --name team-alpha
        - name: Add a namespace with labels and annotations
          text: az aimanager namespace add -m my-ai-manager -g myrg --name team-alpha --labels team=alpha --annotations owner=alice
"""

helps['aimanager namespace update'] = """
    type: command
    short-summary: Update a namespace within an AI Manager.
    examples:
        - name: Update the labels of a namespace
          text: az aimanager namespace update -m my-ai-manager -g myrg --name team-alpha --labels team=beta
"""

helps['aimanager namespace show'] = """
    type: command
    short-summary: Show the details of a namespace within an AI Manager.
    examples:
        - name: Show a namespace
          text: az aimanager namespace show -m my-ai-manager -g myrg --name team-alpha
"""

helps['aimanager namespace delete'] = """
    type: command
    short-summary: Delete a namespace within an AI Manager.
    examples:
        - name: Delete a namespace
          text: az aimanager namespace delete -m my-ai-manager -g myrg --name team-alpha
"""

helps['aimanager namespace list'] = """
    type: command
    short-summary: List the namespaces within an AI Manager.
    examples:
        - name: List namespaces in an AI Manager
          text: az aimanager namespace list -m my-ai-manager -g myrg
"""

helps['aimanager namespace wait'] = """
    type: command
    short-summary: Wait for an AI Manager namespace to reach a desired state.
"""
