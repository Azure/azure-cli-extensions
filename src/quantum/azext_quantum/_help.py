# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps['quantum'] = """
    type: group
    short-summary: Manage Azure Quantum Workspaces and submit jobs to Azure Quantum Providers.
"""

helps['quantum job'] = """
    type: group
    short-summary: Manage jobs for Azure Quantum.
    examples:
      - name: Get the list of jobs from an Azure Quantum workspace
        text: |-
            az quantum job list -g MyResourceGroup -w MyWorkspace
      - name: Submit the Q# program from the current folder
        text: |-
            az quantum job submit -g MyResourceGroup -w MyWorkspace \\
               --job-name MyJob
      - name: Get the status of an Azure Quantum job
        text: |-
            az quantum job show -g MyResourceGroup -w MyWorkspace \\
                -id yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy --query status
      - name: Print the results of a successful Azure Quantum job
        text: |-
            az quantum job output -g MyResourceGroup -w MyWorkspace \\
                -id yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy -o table
"""

helps['quantum target'] = """
    type: group
    short-summary: Manage execution targets for Azure Quantum workspaces.
    examples:
      - name: Get the list of targets available in a Azure Quantum workspaces
        text: |-
            az quantum target list -g MyResourceGroup -w MyWorkspace
      - name: Select a default when submitting jobs to Azure Quantum
        text: |-
            az quantum target set -t target-id
      - name: Show the currently selected default target
        text: |-
            az quantum target show
"""

helps['quantum workspace'] = """
    type: group
    short-summary: Manage Azure Quantum workspaces.
    examples:
      - name: Get the list of Azure Quantum workspaces available
        text: |-
            az quantum workspace list
      - name: Select a default Azure Quantum workspace for future commands
        text: |-
            az quantum workspace set -g MyResourceGroup -w MyWorkspace
      - name: Show the currently selected default Azure Quantum workspace
        text: |-
            az quantum workspace show
"""
