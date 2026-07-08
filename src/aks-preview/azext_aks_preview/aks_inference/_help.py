# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Help definitions — the classic equivalent of `_help.py`.

Unlike AAZ (where the command class docstring is the help), classic command
modules register help as YAML strings in the `helps` dict. Import this module
once (e.g. from the extension's real `_help.py`) so the strings get registered.
"""

from knack.help_files import helps


helps['aks inference'] = """
    type: group
    short-summary: Manage AI Manager resources for inference on AKS.
"""

helps['aks inference create'] = """
    type: command
    short-summary: Create an AI Manager resource.
    examples:
        - name: Create an AI Manager
          text: az aks inference create --name my-ai-manager -g myrg -l eastus2
        - name: Create an AI Manager with the Keep delete policy
          text: az aks inference create --name my-ai-manager -g myrg -l eastus2 --delete-policy Keep
"""

helps['aks inference show'] = """
    type: command
    short-summary: Show the details of an AI Manager resource.
    examples:
        - name: Show an AI Manager
          text: az aks inference show --name my-ai-manager -g myrg
"""

helps['aks inference delete'] = """
    type: command
    short-summary: Delete an AI Manager resource.
    examples:
        - name: Delete an AI Manager
          text: az aks inference delete --name my-ai-manager -g myrg
"""

helps['aks inference list'] = """
    type: command
    short-summary: List AI Manager resources.
    examples:
        - name: List AI Managers in a resource group
          text: az aks inference list -g myrg
        - name: List all AI Managers in the subscription
          text: az aks inference list
"""

helps['aks inference namespace'] = """
    type: group
    short-summary: Manage namespaces within an AI Manager.
"""

helps['aks inference namespace create'] = """
    type: command
    short-summary: Create a namespace within an AI Manager.
    examples:
        - name: Create a namespace
          text: az aks inference namespace create -m my-ai-manager -g myrg --name team-alpha
        - name: Create a namespace with labels and annotations
          text: az aks inference namespace create -m my-ai-manager -g myrg --name team-alpha --labels team=alpha --annotations owner=alice
"""

helps['aks inference namespace show'] = """
    type: command
    short-summary: Show the details of a namespace within an AI Manager.
    examples:
        - name: Show a namespace
          text: az aks inference namespace show -m my-ai-manager -g myrg --name team-alpha
"""

helps['aks inference namespace delete'] = """
    type: command
    short-summary: Delete a namespace within an AI Manager.
    examples:
        - name: Delete a namespace
          text: az aks inference namespace delete -m my-ai-manager -g myrg --name team-alpha
"""

helps['aks inference namespace list'] = """
    type: command
    short-summary: List the namespaces within an AI Manager.
    examples:
        - name: List namespaces in an AI Manager
          text: az aks inference namespace list -m my-ai-manager -g myrg
"""
