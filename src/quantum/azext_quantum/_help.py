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
    short-summary: Submit a job to run on Azure Quantum, and wait for the result. Equivalent to `az quantum run`.
    examples:
      - name: Run QIR bitcode from a file in the current folder and wait for the result.
        text: |-
            az quantum execute -g MyResourceGroup -w MyWorkspace -t MyTarget \\
                --job-name MyJob --job-input-format qir.v1 --job-input-file MyQirBitcode.bc \\
                --entry-point MyQirEntryPoint
      - name: Run a Quil pass-through job on the Rigetti simulator and wait for the result.
        text: |-
            az quantum execute -g MyResourceGroup -w MyWorkspace \\
               -t rigetti.sim.qvm --job-name MyJob --job-input-file MyProgram.quil \\
               --job-input-format rigetti.quil.v1 --job-output-format rigetti.quil-results.v1
      - name: Submit a Qiskit circuit to the IonQ simulator with job params and wait for the results.
        text: |-
            az quantum execute -g MyResourceGroup -w MyWorkspace \\
               -t ionq.simulator --job-name MyJobName --job-input-file MyCircuit.json \\
               --job-input-format ionq.circuit.v1 --job-output-format ionq.quantum-results.v1 \\
               --job-params count=100 content-type=application/json

"""

helps['quantum run'] = """
    type: command
    short-summary: Submit a job to run on Azure Quantum, and wait for the result. Equivalent to `az quantum execute`
    examples:
      - name: Run QIR bitcode from a file in the current folder and wait for the result.
        text: |-
            az quantum run -g MyResourceGroup -w MyWorkspace -t MyTarget \\
                --job-name MyJob --job-input-format qir.v1 --job-input-file MyQirBitcode.bc \\
                --entry-point MyQirEntryPoint
      - name: Run a Quil pass-through job on the Rigetti simulator and wait for the result.
        text: |-
            az quantum run -g MyResourceGroup -w MyWorkspace \\
               -t rigetti.sim.qvm --job-name MyJob --job-input-file MyProgram.quil \\
               --job-input-format rigetti.quil.v1 --job-output-format rigetti.quil-results.v1
      - name: Submit a Qiskit circuit to the IonQ simulator with job params and wait for the results.
        text: |-
            az quantum run -g MyResourceGroup -w MyWorkspace \\
               -t ionq.simulator --job-name MyJobName --job-input-file MyCircuit.json \\
               --job-input-format ionq.circuit.v1 --job-output-format ionq.quantum-results.v1 \\
               --job-params count=100 content-type=application/json
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
            az quantum job list -g MyResourceGroup -w MyWorkspace
      - name: List jobs that used the quantinuum provider.
        text: |-
            az quantum job list -g MyResourceGroup -w MyWorkspace --provider-id quantinuum
      - name: List jobs that ran on the ionq.simulator target.
        text: |-
            az quantum job list -g MyResourceGroup -w MyWorkspace --target-id ionq.simulator
      - name: List jobs that completed successfully.
        text: |-
            az quantum job list -g MyResourceGroup -w MyWorkspace --status Succeeded
      - name: List jobs created after January 15th, 2025.
        text: |-
            az quantum job list -g MyResourceGroup -w MyWorkspace --created-after 2025-01-15
      - name: List jobs whose names start with "Generate...".
        text: |-
            az quantum job list -g MyResourceGroup -w MyWorkspace --job-name Generate
      - name: Skip the first 50 jobs, start listing at the 51st job and list 10 jobs.
        text: |-
            az quantum job list -g MyResourceGroup -w MyWorkspace --skip 50 --top 10
      - name: Sort the job list by Target ID and display in tabular format.
        text: |-
            az quantum job list -g MyResourceGroup -w MyWorkspace --orderby Target -o table
      - name: Sort the job list by Job Name in descending order, display in tabular format.
        text: |-
            az quantum job list -g MyResourceGroup -w MyWorkspace --orderby Name --order desc -o table
"""

helps['quantum job output'] = """
    type: command
    short-summary: Get the results of running a job.
    examples:
      - name: Print the results of a successful Azure Quantum job.
        text: |-
            az quantum job output -g MyResourceGroup -w MyWorkspace \\
                -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy -o table
"""

helps['quantum job file'] = """
    type: group
    short-summary: Manage a quantum job's associated files.
"""

helps['quantum job file list'] = """
    type: command
    short-summary: List the files stored in a job's output storage container.
    long-summary: >
        Returns one entry per file, each reporting the file name, its size in bytes,
        and the last-modified time as an ISO 8601 timestamp. Use "-o table" for a
        condensed view.
    examples:
      - name: List the files in an Azure Quantum job's output container.
        text: |-
            az quantum job file list -g MyResourceGroup -w MyWorkspace \\
                -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy -o table
"""

helps['quantum job file download'] = """
    type: command
    short-summary: Download a file from a job's output storage container.
    examples:
      - name: Download a file from an Azure Quantum job's output container.
        text: |-
            az quantum job file download -g MyResourceGroup -w MyWorkspace \\
                -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy -n rawOutputData
      - name: Download a file to a specific directory.
        text: |-
            az quantum job file download -g MyResourceGroup -w MyWorkspace \\
                -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy -n rawOutputData --dest ./downloads
"""
helps['quantum job show'] = """
    type: command
    short-summary: Get the job's status and details.
    examples:
      - name: Get the status of an Azure Quantum job.
        text: |-
            az quantum job show -g MyResourceGroup -w MyWorkspace \\
                -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy --query status
"""

helps['quantum job submit'] = """
    type: command
    short-summary: Submit a program or circuit to run on Azure Quantum.
    examples:
      - name: Submit QIR bitcode from a file in the current folder.
        text: |-
            az quantum job submit -g MyResourceGroup -w MyWorkspace -t MyTarget \\
                --job-name MyJob --job-input-format qir.v1 --job-input-file MyQirBitcode.bc \\
                --entry-point MyQirEntryPoint
      - name: Submit a Quil pass-through job to the Rigetti simulator.
        text: |-
            az quantum job submit -g MyResourceGroup -w MyWorkspace \\
               -t rigetti.sim.qvm --job-name MyJob --job-input-file MyProgram.quil \\
               --job-input-format rigetti.quil.v1 --job-output-format rigetti.quil-results.v1
      - name: Submit a IonQ JSON circuit to the IonQ simulator with job params.
        text: |-
            az quantum job submit -g MyResourceGroup -w MyWorkspace \\
               -t ionq.simulator --job-name MyJobName --job-input-file MyCircuit.json \\
               --job-input-format ionq.circuit.v1 --job-output-format ionq.quantum-results.v1 \\
               --job-params count=100 content-type=application/json
"""

helps['quantum job wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until the job finishes running.
    examples:
      - name: Wait for completion of a job, check at 60 second intervals.
        text: |-
            az quantum job wait -g MyResourceGroup -w MyWorkspace \\
                -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy --max-poll-wait-secs 60 -o table
"""

helps['quantum job cancel'] = """
    type: command
    short-summary: Request to cancel a job on Azure Quantum if it hasn't completed.
    examples:
      - name: Cancel an Azure Quantum job by id.
        text: |-
            az quantum job cancel -g MyResourceGroup -w MyWorkspace \\
                -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy
"""

helps['quantum job delete'] = """
    type: command
    short-summary: Delete a job from an Azure Quantum workspace.
    examples:
      - name: Delete an Azure Quantum job by id.
        text: |-
            az quantum job delete -g MyResourceGroup -w MyWorkspace \\
                -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy
"""

helps['quantum job update'] = """
    type: command
    short-summary: Update a submitted job's name, priority, and/or tags.
    examples:
      - name: Rename an Azure Quantum job.
        text: |-
            az quantum job update -g MyResourceGroup -w MyWorkspace \\
                -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy --job-name "My new job name"
      - name: Change the priority of an Azure Quantum job.
        text: |-
            az quantum job update -g MyResourceGroup -w MyWorkspace \\
                -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy --job-priority High
      - name: Replace the tags of an Azure Quantum job.
        text: |-
            az quantum job update -g MyResourceGroup -w MyWorkspace \\
                -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy --job-tags tag1 tag2
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
            az quantum target list -g MyResourceGroup -w MyWorkspace
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
      - name: Create a V2 workspace with quota allocations for provider targets.
        text: |-
            az quantum workspace create -g MyResourceGroup -w MyWorkspace -l MyLocation \\
                --workspace-kind V2 -r "MyProvider/default" --skip-autoadd -a MyStorageAccountName \\
                --quota provider-id=MyProvider target-id=MyProvider.Target1 standard-minutes-lifetime=500 high-minutes-lifetime=50 \\
                --quota provider-id=MyProvider target-id=MyProvider.Target2 standard-minutes-lifetime=250
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
      - name: List the quota information of a specified Azure Quantum workspace. If a default workspace has been set, the -g and -w parameters are not required.
        text: |-
            az quantum workspace quotas -g MyResourceGroup -w MyWorkspace
"""

helps['quantum workspace set'] = """
    type: command
    short-summary: Select a default Azure Quantum workspace for future commands.
    examples:
      - name: Set the default Azure Quantum workspace.
        text: |-
            az quantum workspace set -g MyResourceGroup -w MyWorkspace
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
      - name: Update a target quota allocation on a V2 workspace.
        text: |-
            az quantum workspace update -g MyResourceGroup -w MyWorkspace \\
                --quota provider-id=MyProvider target-id=MyProvider.Target1 standard-minutes-lifetime=1000
"""

helps['quantum workspace keys'] = """
    type: group
    short-summary: Manage Azure Quantum Workspace api keys.
"""

helps['quantum workspace user'] = """
    type: group
    short-summary: Manage users of an Azure Quantum workspace.
"""

helps['quantum workspace user create'] = """
    type: command
    short-summary: Grant a user, group, or service principal access to an Azure Quantum workspace.
    long-summary: >-
        Assigns the 'Quantum Workspace Data Contributor' role (by default) at the scope of the given
        (or current) Azure Quantum workspace.
    examples:
      - name: Grant a user access to a workspace using their sign-in name.
        text: |-
            az quantum workspace user create -g MyResourceGroup -w MyWorkspace \\
                --assignee user@contoso.com
      - name: Grant a user access to a workspace using their object id.
        text: |-
            az quantum workspace user create -g MyResourceGroup -w MyWorkspace \\
                --assignee-object-id 00000000-0000-0000-0000-000000000000
      - name: Grant a group access to a workspace using its object id and principal type.
        text: |-
            az quantum workspace user create -g MyResourceGroup -w MyWorkspace \\
                --assignee-object-id 00000000-0000-0000-0000-000000000000 --assignee-principal-type Group
"""

helps['quantum workspace user delete'] = """
    type: command
    short-summary: Remove a user, group, or service principal's access to an Azure Quantum workspace.
    examples:
      - name: Remove a user's access to a workspace using their sign-in name.
        text: |-
            az quantum workspace user delete -g MyResourceGroup -w MyWorkspace \\
                --assignee user@contoso.com
      - name: Remove a user's access to a workspace using their object id.
        text: |-
            az quantum workspace user delete -g MyResourceGroup -w MyWorkspace \\
                --assignee-object-id 00000000-0000-0000-0000-000000000000
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
