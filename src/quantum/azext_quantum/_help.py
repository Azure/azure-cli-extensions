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

helps['quantum execute'] = """
    type: command
    short-summary: Submit a job to run on Azure Quantum, and waits for the result.
    examples:
      - name: Submit the Q# program from the current folder and wait for the result.
        text: |-
            az quantum execute -g MyResourceGroup -w MyWorkspace -l MyLocation
"""

helps['quantum run'] = """
    type: command
    short-summary: Equivalent to `az quantum execute`
    examples:
      - name: Submit the Q# program from the current folder and wait for the result.
        text: |-
            az quantum run -g MyResourceGroup -w MyWorkspace -l MyLocation
"""

helps['quantum job'] = """
    type: group
    short-summary: Manage jobs for Azure Quantum.
"""

helps['quantum job list'] = """
    type: command
    short-summary: Get the list of jobs in a Quantum Workspace.
    examples:
      - name: Get the list of jobs from an Azure Quantum workspace.
        text: |-
            az quantum job list -g MyResourceGroup -w MyWorkspace -l MyLocation
"""

helps['quantum job output'] = """
    type: command
    short-summary: Get the results of running a Q# job.
    examples:
      - name: Print the results of a successful Azure Quantum job.
        text: |-
            az quantum job output -g MyResourceGroup -w MyWorkspace -l MyLocation \\
                -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy -o table
"""

helps['quantum job show'] = """
    type: command
    short-summary: Get the job's status and details.
    examples:
      - name: Get the status of an Azure Quantum job.
        text: |-
            az quantum job show -g MyResourceGroup -w MyWorkspace -l MyLocation \\
                -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy --query status
"""

helps['quantum job submit'] = """
    type: command
    short-summary: Submit a Q# project to run on Azure Quantum.
    examples:
      - name: Submit the Q# program from the current folder.
        text: |-
            az quantum job submit -g MyResourceGroup -w MyWorkspace -l MyLocation \\
               -l MyLocation --job-name MyJob
"""

helps['quantum job wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until the job finishes running.
    examples:
      - name: Wait for completion of a job for 60 seconds.
        text: |-
            az quantum job wait -g MyResourceGroup -w MyWorkspace -l MyLocation \\
                -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy --max-poll-wait-secs 60 -o table
"""

helps['quantum offerings'] = """
    type: group
    short-summary: Manage provider offerings for Azure Quantum.
"""

helps['quantum offerings list'] = """
    type: command
    short-summary: Get the list of all provider offerings available on the given location.
    examples:
      - name: List offerings available in an Azure location.
        text: |-
            az quantum offerings list -l MyLocation
"""

helps['quantum offerings show-terms'] = """
    type: command
    short-summary: Show the terms of a provider and SKU combination including license URL and acceptance status.
    examples:
      - name: Use a Provider Id and SKU from `az quantum offerings list` to review the terms.
        text: |-
            az quantum offerings show-terms -p MyProviderId -k MySKU -l MyLocation
"""

helps['quantum offerings accept-terms'] = """
    type: command
    short-summary: Accept the terms of a provider and SKU combination to enable it for workspace creation.
    examples:
      - name: Once terms have been reviewed, accept the invoking this command.
        text: |-
            az quantum offerings accept-terms -p MyProviderId -k MySKU -l MyLocation
"""

helps['quantum target'] = """
    type: group
    short-summary: Manage targets for Azure Quantum workspaces.
"""

helps['quantum target clear'] = """
    type: command
    short-summary: Clear the default target-id.
    examples:
      - name: Clear the default target-id.
        text: |-
            az quantum target clear
"""

helps['quantum target list'] = """
    type: command
    short-summary: Get the list of providers and their targets in an Azure Quantum workspace.
    examples:
      - name: Get the list of targets available in a Azure Quantum workspaces
        text: |-
            az quantum target list -g MyResourceGroup -w MyWorkspace -l MyLocation
"""

helps['quantum target set'] = """
    type: command
    short-summary: Select the default target to use when submitting jobs to Azure Quantum.
    examples:
      - name: Select a default when submitting jobs to Azure Quantum.
        text: |-
            az quantum target set -t target-id
"""

helps['quantum target show'] = """
    type: command
    short-summary: Get the details of the given (or current) target to use when submitting jobs to Azure Quantum.
    examples:
      - name: Show the currently selected default target
        text: |-
            az quantum target show
"""

helps['quantum workspace'] = """
    type: group
    short-summary: Manage Azure Quantum workspaces.
"""

helps['quantum workspace clear'] = """
    type: command
    short-summary: Clear the default Azure Quantum workspace.
    examples:
      - name: Clear the default Azure Quantum workspace if previously set.
        text: |-
            az quantum workspace clear
"""

helps['quantum workspace create'] = """
    type: command
    short-summary: Create a new Azure Quantum workspace.
    examples:
      - name: Create a new Azure Quantum workspace with a specific list of providers.
        text: |-
            az quantum workspace create -g MyResourceGroup -w MyWorkspace -l MyLocation \\
                -r "MyProvider1 / MySKU1, MyProvider2 / MySKU2" -a MyStorageAccountName
"""

helps['quantum workspace delete'] = """
    type: command
    short-summary: Delete the given (or current) Azure Quantum workspace.
    examples:
      - name: Delete an Azure Quantum workspace by name and group.
        text: |-
            az quantum workspace delete -g MyResourceGroup -w MyWorkspace
      - name: Delete and clear the default Azure Quantum workspace (if one has been set).
        text: |-
            az quantum workspace delete
"""

helps['quantum workspace list'] = """
    type: command
    short-summary: Get the list of Azure Quantum workspaces available.
    examples:
      - name: Get the list of all Azure Quantum workspaces available.
        text: |-
            az quantum workspace list
      - name: Get the list Azure Quantum workspaces available in a location.
        text: |-
            az quantum workspace list -l MyLocation

"""

helps['quantum workspace quotas'] = """
    type: command
    short-summary: List the quotas for the given (or current) Azure Quantum workspace.
    examples:
      - name: List the quota information of the default workspace if set.
        text: |-
            az quantum workspace quotas
      - name: List the quota information of a specified Azure Quantum workspace.
        text: |-
            az quantum workspace quotas -g MyResourceGroup -w MyWorkspace -l MyLocation
"""

helps['quantum workspace set'] = """
    type: command
    short-summary: Select a default Azure Quantum workspace for future commands.
    examples:
      - name: Set the default Azure Quantum workspace.
        text: |-
            az quantum workspace set -g MyResourceGroup -w MyWorkspace -l MyLocation
"""

helps['quantum workspace show'] = """
    type: command
    short-summary: Get the details of the given (or current) Azure Quantum workspace.
    examples:
      - name: Show the currently selected default Azure Quantum workspace.
        text: |-
            az quantum workspace show
      - name: Show the details of a provided Azure Quantum workspace.
        text: |-
            az quantum workspace show -g MyResourceGroup -w MyWorkspace
"""
