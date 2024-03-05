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
      - name: Submit a Q# program from the current folder and wait for the result.
        text: |-
            az quantum execute -g MyResourceGroup -w MyWorkspace -l MyLocation -t MyTarget
      - name: Submit and wait for a Q# program from the current folder with job and program parameters.
        text: |-
            az quantum execute -g MyResourceGroup -w MyWorkspace -l MyLocation -t MyTarget \\
                --job-params key1=value1 key2=value2 -- --n-qubits=3
      - name: Submit and wait for a Q# program from the current folder with a target-capability parameter.
        text: |-
            az quantum execute -g MyResourceGroup -w MyWorkspace -l MyLocation -t MyTarget \\
                --target-capability MyTargetCapability
"""

helps['quantum run'] = """
    type: command
    short-summary: Equivalent to `az quantum execute`
    examples:
      - name: Submit a Q# program from the current folder and wait for the result.
        text: |-
            az quantum run -g MyResourceGroup -w MyWorkspace -l MyLocation -t MyTarget
      - name: Submit and wait for a Q# program from the current folder with job and program parameters.
        text: |-
            az quantum run -g MyResourceGroup -w MyWorkspace -l MyLocation -t MyTarget \\
                --job-params key1=value1 key2=value2 -- --n-qubits=3
      - name: Submit and wait for a Q# program from the current folder with a target-capability parameter.
        text: |-
            az quantum run -g MyResourceGroup -w MyWorkspace -l MyLocation -t MyTarget \\
                --target-capability MyTargetCapability
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
    short-summary: Get the results of running a job.
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
    short-summary: Submit a program or circuit to run on Azure Quantum.
    examples:
      - name: Submit a Q# program from the current folder.
        text: |-
            az quantum job submit -g MyResourceGroup -w MyWorkspace -l MyLocation \\
               -t MyTarget --job-name MyJob
      - name: Submit a Q# program from the current folder with job parameters for a target.
        text: |-
            az quantum job submit -g MyResourceGroup -w MyWorkspace -l MyLocation \\
               -t MyTarget --job-name MyJob --job-params param1=value1 param2=value2
      - name: Submit a Q# program with program parameters (e.g. n-qubits = 2).
        text: |-
            az quantum job submit -g MyResourceGroup -w MyWorkspace -l MyLocation \\
               -t MyTarget --job-name MyJob -- --n-qubits=2
      - name: Submit a Q# program from the current folder with a target-capability parameter.
        text: |-
            az quantum job submit -g MyResourceGroup -w MyWorkspace -l MyLocation -t MyTarget \\
                --target-capability MyTargetCapability
      - name: Submit QIR bitcode or human-readable LLVM code from a file in the current folder.
        text: |-
            az quantum job submit -g MyResourceGroup -w MyWorkspace -l MyLocation -t MyTarget \\
                --job-name MyJob --job-input-format qir.v1 --job-input-file MyQirBitcode.bc \\
                --entry-point MyQirEntryPoint
"""

helps['quantum job wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until the job finishes running.
    examples:
      - name: Wait for completion of a job, check at 60 second intervals.
        text: |-
            az quantum job wait -g MyResourceGroup -w MyWorkspace -l MyLocation \\
                -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy --max-poll-wait-secs 60 -o table
"""

helps['quantum job cancel'] = """
    type: command
    short-summary: Request to cancel a job on Azure Quantum if it hasn't completed.
    examples:
      - name: Cancel an Azure Quantum job by id.
        text: |-
            az quantum job cancel -g MyResourceGroup -w MyWorkspace -l MyLocation \\
                -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy
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
            az quantum offerings list -l MyLocation -o table
      - name: List only the offerings flagged "autoAdd" in an Azure location.
        text: |-
            az quantum offerings list -l MyLocation --autoadd-only -o table
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
    short-summary: Get the Target ID of the current default target to use when submitting jobs to Azure Quantum.
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
      - name: Create a new Azure Quantum workspace with the providers that offer free credit.
        text: |-
            az quantum workspace create -g MyResourceGroup -w MyWorkspace -l MyLocation \\
                -a MyStorageAccountName
      - name: Create a new Azure Quantum workspace with a specific list of providers.
        text: |-
            az quantum workspace create -g MyResourceGroup -w MyWorkspace -l MyLocation \\
                -r "MyProvider1 / MySKU1, MyProvider2 / MySKU2" --skip-autoadd -a MyStorageAccountName\n
            To display a list of available providers and their SKUs, use the following command:
                az quantum offerings list -l MyLocation -o table
"""

helps['quantum workspace delete'] = """
    type: command
    short-summary: Delete the given (or current) Azure Quantum workspace.
    examples:
      - name: Delete an Azure Quantum workspace by resource group and workspace name. If a default workspace has been set, the -g and -w parameters are not required.
        text: |-
            az quantum workspace delete -g MyResourceGroup -w MyWorkspace
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
      - name: List the quota information of a specified Azure Quantum workspace. If a default workspace has been set, the -g, -w, and -l parameters are not required.
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

helps['quantum workspace update'] = """
    type: command
    short-summary: Update the given (or current) Azure Quantum workspace.
    examples:
      - name: Enable a provided Azure Quantum workspace api keys.
        text: |-
            az quantum workspace update --enable-api-key True
      - name: Disable a provided Azure Quantum workspace api keys.
        text: |-
            az quantum workspace update --enable-api-key False
"""

helps['quantum workspace keys'] = """
    type: group
    short-summary: Manage Azure Quantum Workspace api keys.
"""

helps['quantum workspace keys list'] = """
    type: command
    short-summary: List api keys for the given (or current) Azure Quantum workspace.
    examples:
      - name: Show the currently selected default Azure Quantum workspace api keys.
        text: |-
            az quantum workspace keys list
"""

helps['quantum workspace keys regenerate'] = """
    type: command
    short-summary: Regenerate api key for the given (or current) Azure Quantum workspace.
    examples:
      - name: Regenerate the currently selected default Azure Quantum workspace primary api key.
        text: |-
            az quantum workspace keys regenerate --key-type Primary
      - name: Regenerate the currently selected default Azure Quantum workspace secondary api key.
        text: |-
            az quantum workspace keys regenerate --key-type Secondary
      - name: Regenerate the currently selected default Azure Quantum workspace secondary api key.
        text: |-
            az quantum workspace keys regenerate --key-type Primary,Secondary
"""
