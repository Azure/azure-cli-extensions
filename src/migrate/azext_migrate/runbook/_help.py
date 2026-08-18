# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# coding=utf-8
from knack.help_files import helps  # pylint: disable=unused-import


helps['migrate runbook'] = """
    type: group
    short-summary: Manage Azure Migrate runbooks.
    long-summary: |
        Commands to generate and manage Azure Migrate runbooks and their
        executions. This command group is in preview and under active
        development; additional subgroups and commands are added
        incrementally.
"""


helps['migrate runbook show'] = """
    type: command
    short-summary: Get the details of a runbook.
    examples:
        - name: Show the details of a runbook.
          text: |
            az migrate runbook show -g myRg --project-name myProject \\
              -n myRunbook
"""


helps['migrate runbook generate'] = """
    type: command
    short-summary: Generate a runbook for a migration wave.
    examples:
        - name: Generate a runbook scoped to a wave.
          text: |
            az migrate runbook generate -g myRg --project-name myProject \\
              -n myRunbook --wave-name myWave
        - name: Generate a runbook and return immediately.
          text: |
            az migrate runbook generate -g myRg --project-name myProject \\
              -n myRunbook --wave-name myWave --no-wait
"""


helps['migrate runbook list'] = """
    type: command
    short-summary: List runbooks in a migrate project.
    examples:
        - name: List all runbooks in a project.
          text: |
            az migrate runbook list -g myRg --project-name myProject
        - name: List runbooks filtered by wave and status.
          text: |
            az migrate runbook list -g myRg --project-name myProject \\
              --wave-name myWave --status InExecution
"""


helps['migrate runbook delete'] = """
    type: command
    short-summary: Delete a runbook.
    examples:
        - name: Delete a runbook.
          text: |
            az migrate runbook delete -g myRg --project-name myProject \\
              -n myRunbook
"""


helps['migrate runbook update'] = """
    type: command
    short-summary: Update editable runbook metadata.
    examples:
        - name: Update a runbook description.
          text: |
            az migrate runbook update -g myRg --project-name myProject \\
              -n myRunbook --description "Wave 1 cutover runbook"
"""


helps['migrate runbook regenerate'] = """
    type: command
    short-summary: Regenerate a runbook from its current scope.
    examples:
        - name: Regenerate a runbook.
          text: |
            az migrate runbook regenerate -g myRg \\
              --project-name myProject -n myRunbook
        - name: Regenerate a runbook and return immediately.
          text: |
            az migrate runbook regenerate -g myRg \\
              --project-name myProject -n myRunbook --no-wait
"""


helps['migrate runbook definition'] = """
    type: group
    short-summary: View and download the contents of a runbook definition.
"""


helps['migrate runbook definition show'] = """
    type: command
    short-summary: Show the definition (contents) of a runbook.
    examples:
        - name: Show a runbook definition.
          text: |
            az migrate runbook definition show -g myRg \\
              --project-name myProject -n myRunbook
        - name: Show a single workstream in a runbook definition.
          text: |
            az migrate runbook definition show -g myRg \\
              --project-name myProject -n myRunbook \\
              --workstream-id myWorkstream
"""


helps['migrate runbook definition download'] = """
    type: command
    short-summary: Download the runbook definition and documentation files.
    examples:
        - name: Download a runbook definition to the current directory.
          text: |
            az migrate runbook definition download -g myRg \\
              --project-name myProject -n myRunbook
        - name: Download a runbook definition to a specific directory.
          text: |
            az migrate runbook definition download -g myRg \\
              --project-name myProject -n myRunbook \\
              --destination ./runbooks
"""


helps['migrate runbook definition visualize'] = """
    type: command
    short-summary: Render the runbook definition as a self-contained HTML page.
    examples:
        - name: Visualize a runbook definition and open it in the browser.
          text: |
            az migrate runbook definition visualize -g myRg \\
              --project-name myProject -n myRunbook --open
        - name: Visualize from a local definition file.
          text: |
            az migrate runbook definition visualize \\
              --from-file ./definition.json --file ./definition.html
"""


helps['migrate runbook definition step'] = """
    type: group
    short-summary: Manage individual steps in a runbook definition.
"""


helps['migrate runbook definition step add'] = """
    type: command
    short-summary: Add a step to the runbook definition.
    examples:
        - name: Add a manual step to a workstream.
          text: |
            az migrate runbook definition step add -g myRg \\
              --project-name myProject -n myRunbook \\
              --step-type Manual --step-name "Verify cutover" \\
              --workstream-id workstream-0
        - name: Add an approval step that depends on another step.
          text: |
            az migrate runbook definition step add -g myRg \\
              --project-name myProject -n myRunbook \\
              --step-type Approval --step-name "Change approval" \\
              --workstream-id workstream-0 --depends-on step0
        - name: Add a manual step scoped to specific migration entities.
          text: |
            az migrate runbook definition step add -g myRg \\
              --project-name myProject -n myRunbook \\
              --step-type Manual --step-name "Post checks" \\
              --workstream-id workstream-0 \\
              --migration-entity-ids entity1 entity2
"""


helps['migrate runbook definition step update'] = """
    type: command
    short-summary: Update a step in the runbook definition.
    examples:
        - name: Rename a step and change its dependencies.
          text: |
            az migrate runbook definition step update -g myRg \\
              --project-name myProject -n myRunbook \\
              --step-id step1 --step-name "New name" \\
              --depends-on step0
"""


helps['migrate runbook definition step remove'] = """
    type: command
    short-summary: Remove a step from the runbook definition.
    examples:
        - name: Remove a step by id.
          text: |
            az migrate runbook definition step remove -g myRg \\
              --project-name myProject -n myRunbook --step-id step1
"""


helps['migrate runbook definition workstream'] = """
    type: group
    short-summary: Manage workstreams in a runbook definition.
"""


helps['migrate runbook definition workstream split'] = """
    type: command
    short-summary: Split a workstream into two workstreams.
    examples:
        - name: Move steps into a new workstream.
          text: |
            az migrate runbook definition workstream split -g myRg \\
              --project-name myProject -n myRunbook \\
              --source-workstream-id ws1 \\
              --new-workstream-name "Database tier" \\
              --step-ids step1 step2
"""


helps['migrate runbook definition workstream merge'] = """
    type: command
    short-summary: Merge two or more workstreams into a single workstream.
    examples:
        - name: Merge two workstreams.
          text: |
            az migrate runbook definition workstream merge -g myRg \\
              --project-name myProject -n myRunbook \\
              --source-workstream-ids ws1 ws2 \\
              --new-workstream-name "Combined tier"
"""


helps['migrate runbook execution'] = """
    type: group
    short-summary: Manage runbook executions.
"""


helps['migrate runbook execution start'] = """
    type: command
    short-summary: Start a new execution of a runbook.
    examples:
        - name: Start a runbook execution.
          text: |
            az migrate runbook execution start -g myRg \\
              --project-name myProject --runbook-name myRunbook
        - name: Start without waiting for completion.
          text: |
            az migrate runbook execution start -g myRg \\
              --project-name myProject --runbook-name myRunbook --no-wait
"""


helps['migrate runbook execution show'] = """
    type: command
    short-summary: Show (or watch) the status of a runbook execution.
    examples:
        - name: Show an execution's status.
          text: |
            az migrate runbook execution show -g myRg \\
              --project-name myProject --runbook-name myRunbook \\
              --execution-id myExecution
        - name: Show the status of a single step.
          text: |
            az migrate runbook execution show -g myRg \\
              --project-name myProject --runbook-name myRunbook \\
              --execution-id myExecution --step-id step1
        - name: Auto-refresh the status table until it completes.
          text: |
            az migrate runbook execution show -g myRg \\
              --project-name myProject --runbook-name myRunbook \\
              --execution-id myExecution --watch
"""


helps['migrate runbook execution list'] = """
    type: command
    short-summary: List the executions of a runbook.
    examples:
        - name: List a runbook's executions.
          text: |
            az migrate runbook execution list -g myRg \\
              --project-name myProject --runbook-name myRunbook
"""


helps['migrate runbook execution pause'] = """
    type: command
    short-summary: Pause an in-progress runbook execution.
    examples:
        - name: Pause an execution.
          text: |
            az migrate runbook execution pause -g myRg \\
              --project-name myProject --runbook-name myRunbook \\
              --execution-id myExecution
"""


helps['migrate runbook execution resume'] = """
    type: command
    short-summary: Resume a paused runbook execution.
    examples:
        - name: Resume an execution.
          text: |
            az migrate runbook execution resume -g myRg \\
              --project-name myProject --runbook-name myRunbook \\
              --execution-id myExecution
"""


helps['migrate runbook execution cancel'] = """
    type: command
    short-summary: Cancel an in-progress or paused runbook execution.
    long-summary: >
        Cancellation is terminal; a cancelled execution cannot be
        resumed. Start a new execution instead.
    examples:
        - name: Cancel an execution.
          text: |
            az migrate runbook execution cancel -g myRg \\
              --project-name myProject --runbook-name myRunbook \\
              --execution-id myExecution
"""


helps['migrate runbook wait'] = """
    type: command
    short-summary: Wait until a runbook reaches a desired state.
    examples:
        - name: Wait until execution completes.
          text: |
            az migrate runbook wait -g myRg --project-name myProject \\
              -n myRunbook --custom "properties.state=='ExecutionSucceeded'"
        - name: Wait until the runbook exists.
          text: |
            az migrate runbook wait -g myRg --project-name myProject \\
              -n myRunbook --created
"""


helps['migrate runbook execution visualize'] = """
    type: command
    short-summary: Render an execution's status as a self-contained HTML graph.
    examples:
        - name: Visualize an execution's status and open it in the browser.
          text: |
            az migrate runbook execution visualize -g myRg \\
              --project-name myProject --runbook-name myRunbook \\
              --execution-id myExecution --open
        - name: Regenerate the snapshot on an interval until it completes.
          text: |
            az migrate runbook execution visualize -g myRg \\
              --project-name myProject --runbook-name myRunbook \\
              --execution-id myExecution --watch
"""


helps['migrate runbook execution step'] = """
    type: group
    short-summary: Act on a single step within a runbook execution.
"""


helps['migrate runbook execution step retry'] = """
    type: command
    short-summary: Restart the execution of a failed step.
    examples:
        - name: Retry a failed step.
          text: |
            az migrate runbook execution step retry -g myRg \\
              --project-name myProject --runbook-name myRunbook \\
              --execution-id myExecution --step-id step1
"""


helps['migrate runbook execution step approve'] = """
    type: command
    short-summary: Provide approval for an approval-type step during execution.
    examples:
        - name: Approve a Full approval step.
          text: |
            az migrate runbook execution step approve -g myRg \\
              --project-name myProject --runbook-name myRunbook \\
              --execution-id myExecution --step-id step1
        - name: Approve specific ready entities for a Partial approval step.
          text: |
            az migrate runbook execution step approve -g myRg \\
              --project-name myProject --runbook-name myRunbook \\
              --execution-id myExecution --step-id step1 \\
              --entities vm1 vm2
"""


helps['migrate runbook execution step complete'] = """
    type: command
    short-summary: Mark a manual step as complete during execution.
    examples:
        - name: Complete a manual step with a comment.
          text: |
            az migrate runbook execution step complete -g myRg \\
              --project-name myProject --runbook-name myRunbook \\
              --execution-id myExecution --step-id step1 \\
              --comment "Verified manually"
"""


helps['migrate runbook parameter'] = """
    type: group
    short-summary: Download and upload a runbook's parameters (inputs) file.
"""


helps['migrate runbook parameter download'] = """
    type: command
    short-summary: Download the runbook's parameters file.
    examples:
        - name: Download the parameters file to the current directory.
          text: |
            az migrate runbook parameter download -g myRg \\
              --project-name myProject --runbook-name myRunbook
"""


helps['migrate runbook parameter upload'] = """
    type: command
    short-summary: Upload a new parameters file and validate it.
    examples:
        - name: Upload a parameters file.
          text: |
            az migrate runbook parameter upload -g myRg \\
              --project-name myProject --runbook-name myRunbook \\
              --file ./params.json
"""


helps['migrate runbook execution parameter'] = """
    type: group
    short-summary: Download and upload an execution's input-parameters file.
"""


helps['migrate runbook execution parameter download'] = """
    type: command
    short-summary: Download an execution's input-parameters file.
    examples:
        - name: Download the execution input file.
          text: |
            az migrate runbook execution parameter download -g myRg \\
              --project-name myProject --runbook-name myRunbook \\
              --execution-id myExecution
"""


helps['migrate runbook execution parameter upload'] = """
    type: command
    short-summary: Upload an execution's input-parameters file.
    examples:
        - name: Upload the execution input file.
          text: |
            az migrate runbook execution parameter upload -g myRg \\
              --project-name myProject --runbook-name myRunbook \\
              --execution-id myExecution --file ./input.json
"""
