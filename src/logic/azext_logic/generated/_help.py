# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


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
               az logic workflow list --resource-group "test-resource-group"
"""

helps['logic workflow show'] = """
    type: command
    short-summary: Gets a workflow.
    examples:
      - name: Get a workflow
        text: |-
               az logic workflow show --resource-group "test-resource-group" --workflow-name \\
               "test-workflow"
"""

helps['logic workflow create'] = """
    type: command
    short-summary: Creates or updates a workflow.
    examples:
      - name: Create or update a workflow
        text: |-
               az logic workflow create --resource-group "test-resource-group" --workflow-name \\
               "test-workflow"
"""

helps['logic workflow update'] = """
    type: command
    short-summary: Updates a workflow.
    examples:
      - name: Patch a workflow
        text: |-
               az logic workflow update --resource-group "test-resource-group" --workflow-name \\
               "test-workflow"
"""

helps['logic workflow delete'] = """
    type: command
    short-summary: Deletes a workflow.
    examples:
      - name: Delete a workflow
        text: |-
               az logic workflow delete --resource-group "test-resource-group" --workflow-name \\
               "test-workflow"
"""

helps['logic workflow generate-upgraded-definition'] = """
    type: command
    short-summary: Generates the upgraded definition for a workflow.
    examples:
      - name: Generate an upgraded definition
        text: |-
               az logic workflow generate-upgraded-definition --resource-group "test-resource-group" \\
               --workflow-name "test-workflow"
"""

helps['logic workflow list-callback-url'] = """
    type: command
    short-summary: Get the workflow callback Url.
    examples:
      - name: Get callback url
        text: |-
               az logic workflow list-callback-url --resource-group "testResourceGroup" --workflow-name \\
               "testWorkflow"
"""

helps['logic workflow move'] = """
    type: command
    short-summary: Moves an existing workflow.
    examples:
      - name: Move a workflow
        text: |-
               az logic workflow move --resource-group "testResourceGroup" --workflow-name \\
               "testWorkflow"
"""

helps['logic workflow regenerate-access-key'] = """
    type: command
    short-summary: Regenerates the callback URL access key for request triggers.
    examples:
      - name: Regenerate the callback URL access key for request triggers
        text: |-
               az logic workflow regenerate-access-key --key-type "Primary" --resource-group \\
               "testResourceGroup" --workflow-name "testWorkflowName"
"""

helps['logic workflow validate-by-resource-group'] = """
    type: command
    short-summary: Validates the workflow.
    examples:
      - name: Validate a workflow
        text: |-
               az logic workflow validate-by-resource-group --resource-group "test-resource-group" \\
               --workflow-name "test-workflow"
"""

helps['logic workflow validate-by-location'] = """
    type: command
    short-summary: Validates the workflow definition.
    examples:
      - name: Validate a workflow
        text: |-
               az logic workflow validate-by-location --location "brazilsouth" --resource-group \\
               "test-resource-group" --workflow-name "test-workflow"
"""

helps['logic workflow disable'] = """
    type: command
    short-summary: Disables a workflow.
    examples:
      - name: Disable a workflow
        text: |-
               az logic workflow disable --resource-group "test-resource-group" --workflow-name \\
               "test-workflow"
"""

helps['logic workflow enable'] = """
    type: command
    short-summary: Enables a workflow.
    examples:
      - name: Enable a workflow
        text: |-
               az logic workflow enable --resource-group "test-resource-group" --workflow-name \\
               "test-workflow"
"""

helps['logic workflow list-swagger'] = """
    type: command
    short-summary: Gets an OpenAPI definition for the workflow.
    examples:
      - name: Get the swagger for a workflow
        text: |-
               az logic workflow list-swagger --resource-group "testResourceGroup" --workflow-name \\
               "testWorkflowName"
"""

helps['logic workflow-version'] = """
    type: group
    short-summary: logic workflow-version
"""

helps['logic workflow-version list'] = """
    type: command
    short-summary: Gets a list of workflow versions.
    examples:
      - name: List a workflows versions
        text: |-
               az logic workflow-version list --resource-group "test-resource-group" --workflow-name \\
               "test-workflow"
"""

helps['logic workflow-version show'] = """
    type: command
    short-summary: Gets a workflow version.
    examples:
      - name: Get a workflow version
        text: |-
               az logic workflow-version show --resource-group "test-resource-group" --version-id \\
               "08586676824806722526" --workflow-name "test-workflow"
"""

helps['logic workflow-trigger'] = """
    type: group
    short-summary: logic workflow-trigger
"""

helps['logic workflow-trigger list'] = """
    type: command
    short-summary: Gets a list of workflow triggers.
    examples:
      - name: List workflow triggers
        text: |-
               az logic workflow-trigger list --resource-group "test-resource-group" --workflow-name \\
               "test-workflow"
"""

helps['logic workflow-trigger show'] = """
    type: command
    short-summary: Gets a workflow trigger.
    examples:
      - name: Get a workflow trigger
        text: |-
               az logic workflow-trigger show --resource-group "test-resource-group" --trigger-name \\
               "manual" --workflow-name "test-workflow"
"""

helps['logic workflow-trigger reset'] = """
    type: command
    short-summary: Resets a workflow trigger.
    examples:
      - name: Get trigger schema
        text: |-
               az logic workflow-trigger reset --resource-group "testResourceGroup" --trigger-name \\
               "testTrigger" --workflow-name "testWorkflow"
"""

helps['logic workflow-trigger run'] = """
    type: command
    short-summary: Runs a workflow trigger.
    examples:
      - name: Run a workflow trigger
        text: |-
               az logic workflow-trigger run --resource-group "test-resource-group" --trigger-name \\
               "manual" --workflow-name "test-workflow"
"""

helps['logic workflow-trigger list-callback-url'] = """
    type: command
    short-summary: Get the callback URL for a workflow trigger.
    examples:
      - name: Get the callback URL for a trigger
        text: |-
               az logic workflow-trigger list-callback-url --resource-group "test-resource-group" \\
               --trigger-name "manual" --workflow-name "test-workflow"
"""

helps['logic workflow-version-trigger'] = """
    type: group
    short-summary: logic workflow-version-trigger
"""

helps['logic workflow-version-trigger list-callback-url'] = """
    type: command
    short-summary: Get the callback url for a trigger of a workflow version.
    examples:
      - name: Get the callback url for a trigger of a workflow version
        text: |-
               az logic workflow-version-trigger list-callback-url --resource-group "testResourceGroup" \\
               --trigger-name "testTriggerName" --version-id "testWorkflowVersionId" --workflow-name \\
               "testWorkflowName"
"""

helps['logic workflow-trigger-history'] = """
    type: group
    short-summary: logic workflow-trigger-history
"""

helps['logic workflow-trigger-history list'] = """
    type: command
    short-summary: Gets a list of workflow trigger histories.
    examples:
      - name: List a workflow trigger history
        text: |-
               az logic workflow-trigger-history list --resource-group "testResourceGroup" \\
               --trigger-name "testTriggerName" --workflow-name "testWorkflowName"
"""

helps['logic workflow-trigger-history show'] = """
    type: command
    short-summary: Gets a workflow trigger history.
    examples:
      - name: Get a workflow trigger history
        text: |-
               az logic workflow-trigger-history show --history-name "08586676746934337772206998657CU22" \\
               --resource-group "testResourceGroup" --trigger-name "testTriggerName" --workflow-name \\
               "testWorkflowName"
"""

helps['logic workflow-trigger-history resubmit'] = """
    type: command
    short-summary: Resubmits a workflow run based on the trigger history.
    examples:
      - name: Resubmit a workflow run based on the trigger history
        text: |-
               az logic workflow-trigger-history resubmit --history-name "testHistoryName" \\
               --resource-group "testResourceGroup" --trigger-name "testTriggerName" --workflow-name \\
               "testWorkflowName"
"""

helps['logic workflow-run'] = """
    type: group
    short-summary: logic workflow-run
"""

helps['logic workflow-run list'] = """
    type: command
    short-summary: Gets a list of workflow runs.
    examples:
      - name: List workflow runs
        text: |-
               az logic workflow-run list --resource-group "test-resource-group" --workflow-name \\
               "test-workflow"
"""

helps['logic workflow-run show'] = """
    type: command
    short-summary: Gets a workflow run.
    examples:
      - name: Get a run for a workflow
        text: |-
               az logic workflow-run show --resource-group "test-resource-group" --run-name \\
               "08586676746934337772206998657CU22" --workflow-name "test-workflow"
"""

helps['logic workflow-run cancel'] = """
    type: command
    short-summary: Cancels a workflow run.
    examples:
      - name: Cancel a workflow run
        text: |-
               az logic workflow-run cancel --resource-group "test-resource-group" --run-name \\
               "08586676746934337772206998657CU22" --workflow-name "test-workflow"
"""

helps['logic workflow-run-action'] = """
    type: group
    short-summary: logic workflow-run-action
"""

helps['logic workflow-run-action list'] = """
    type: command
    short-summary: Gets a list of workflow run actions.
    examples:
      - name: List a workflow run actions
        text: |-
               az logic workflow-run-action list --resource-group "test-resource-group" --run-name \\
               "08586676746934337772206998657CU22" --workflow-name "test-workflow"
"""

helps['logic workflow-run-action show'] = """
    type: command
    short-summary: Gets a workflow run action.
    examples:
      - name: Get a workflow run action
        text: |-
               az logic workflow-run-action show --action-name "HTTP" --resource-group \\
               "test-resource-group" --run-name "08586676746934337772206998657CU22" --workflow-name \\
               "test-workflow"
"""

helps['logic workflow-run-action list-expression-trace'] = """
    type: command
    short-summary: Lists a workflow run expression trace.
    examples:
      - name: List expression traces
        text: |-
               az logic workflow-run-action list-expression-trace --action-name "testAction" \\
               --resource-group "testResourceGroup" --run-name "08586776228332053161046300351" \\
               --workflow-name "testFlow"
"""

helps['logic workflow-run-action-repetition'] = """
    type: group
    short-summary: logic workflow-run-action-repetition
"""

helps['logic workflow-run-action-repetition list'] = """
    type: command
    short-summary: Get all of a workflow run action repetitions.
    examples:
      - name: List repetitions
        text: |-
               az logic workflow-run-action-repetition list --action-name "testAction" --resource-group \\
               "testResourceGroup" --run-name "08586776228332053161046300351" --workflow-name "testFlow"
"""

helps['logic workflow-run-action-repetition show'] = """
    type: command
    short-summary: Get a workflow run action repetition.
    examples:
      - name: Get a repetition
        text: |-
               az logic workflow-run-action-repetition show --action-name "testAction" --repetition-name \\
               "000001" --resource-group "testResourceGroup" --run-name "08586776228332053161046300351" \\
               --workflow-name "testFlow"
"""

helps['logic workflow-run-action-repetition list-expression-trace'] = """
    type: command
    short-summary: Lists a workflow run expression trace.
    examples:
      - name: List expression traces for a repetition
        text: |-
               az logic workflow-run-action-repetition list-expression-trace --action-name "testAction" \\
               --repetition-name "000001" --resource-group "testResourceGroup" --run-name \\
               "08586776228332053161046300351" --workflow-name "testFlow"
"""

helps['logic workflow-run-action-repetition-request-history'] = """
    type: group
    short-summary: logic workflow-run-action-repetition-request-history
"""

helps['logic workflow-run-action-repetition-request-history list'] = """
    type: command
    short-summary: List a workflow run repetition request history.
    examples:
      - name: List repetition request history
        text: |-
               az logic workflow-run-action-repetition-request-history list --action-name "HTTP_Webhook" \\
               --repetition-name "000001" --resource-group "test-resource-group" --run-name \\
               "08586776228332053161046300351" --workflow-name "test-workflow"
"""

helps['logic workflow-run-action-repetition-request-history show'] = """
    type: command
    short-summary: Gets a workflow run repetition request history.
    examples:
      - name: Get a repetition request history
        text: |-
               az logic workflow-run-action-repetition-request-history show --action-name "HTTP_Webhook" \\
               --repetition-name "000001" --request-history-name "08586611142732800686" --resource-group \\
               "test-resource-group" --run-name "08586776228332053161046300351" --workflow-name \\
               "test-workflow"
"""

helps['logic workflow-run-action-request-history'] = """
    type: group
    short-summary: logic workflow-run-action-request-history
"""

helps['logic workflow-run-action-request-history list'] = """
    type: command
    short-summary: List a workflow run request history.
    examples:
      - name: List a request history
        text: |-
               az logic workflow-run-action-request-history list --action-name "HTTP_Webhook" \\
               --resource-group "test-resource-group" --run-name "08586776228332053161046300351" \\
               --workflow-name "test-workflow"
"""

helps['logic workflow-run-action-request-history show'] = """
    type: command
    short-summary: Gets a workflow run request history.
    examples:
      - name: Get a request history
        text: |-
               az logic workflow-run-action-request-history show --action-name "HTTP_Webhook" \\
               --request-history-name "08586611142732800686" --resource-group "test-resource-group" \\
               --run-name "08586776228332053161046300351" --workflow-name "test-workflow"
"""

helps['logic workflow-run-action-scope-repetition'] = """
    type: group
    short-summary: logic workflow-run-action-scope-repetition
"""

helps['logic workflow-run-action-scope-repetition list'] = """
    type: command
    short-summary: List the workflow run action scoped repetitions.
    examples:
      - name: List the scoped repetitions
        text: |-
               az logic workflow-run-action-scope-repetition list --action-name "for_each" \\
               --resource-group "testResourceGroup" --run-name "08586776228332053161046300351" \\
               --workflow-name "testFlow"
"""

helps['logic workflow-run-action-scope-repetition show'] = """
    type: command
    short-summary: Get a workflow run action scoped repetition.
    examples:
      - name: Get a scoped repetition
        text: |-
               az logic workflow-run-action-scope-repetition show --action-name "for_each" \\
               --repetition-name "000000" --resource-group "testResourceGroup" --run-name \\
               "08586776228332053161046300351" --workflow-name "testFlow"
"""

helps['logic workflow-run-operation'] = """
    type: group
    short-summary: logic workflow-run-operation
"""

helps['logic workflow-run-operation show'] = """
    type: command
    short-summary: Gets an operation for a run.
    examples:
      - name: Get a run operation
        text: |-
               az logic workflow-run-operation show --operation-id \\
               "ebdcbbde-c4db-43ec-987c-fd0f7726f43b" --resource-group "testResourceGroup" --run-name \\
               "08586774142730039209110422528" --workflow-name "testFlow"
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
               az logic integration-account list --resource-group "testResourceGroup"
"""

helps['logic integration-account show'] = """
    type: command
    short-summary: Gets an integration account.
    examples:
      - name: Get integration account by name
        text: |-
               az logic integration-account show --integration-account-name "testIntegrationAccount" \\
               --resource-group "testResourceGroup"
"""

helps['logic integration-account create'] = """
    type: command
    short-summary: Creates or updates an integration account.
    examples:
      - name: Create or update an integration account
        text: |-
               az logic integration-account create --integration-account-name "testIntegrationAccount" \\
               --resource-group "testResourceGroup"
"""

helps['logic integration-account update'] = """
    type: command
    short-summary: Updates an integration account.
    examples:
      - name: Patch an integration account
        text: |-
               az logic integration-account update --integration-account-name "testIntegrationAccount" \\
               --resource-group "testResourceGroup"
"""

helps['logic integration-account delete'] = """
    type: command
    short-summary: Deletes an integration account.
    examples:
      - name: Delete an integration account
        text: |-
               az logic integration-account delete --integration-account-name "testIntegrationAccount" \\
               --resource-group "testResourceGroup"
"""

helps['logic integration-account list-callback-url'] = """
    type: command
    short-summary: Gets the integration account callback URL.
    examples:
      - name: List IntegrationAccount callback URL
        text: |-
               az logic integration-account list-callback-url --integration-account-name \\
               "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account list-key-vault-key'] = """
    type: command
    short-summary: Gets the integration account's Key Vault keys.
    examples:
      - name: Get Integration Account callback URL
        text: |-
               az logic integration-account list-key-vault-key --integration-account-name \\
               "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account log-tracking-event'] = """
    type: command
    short-summary: Logs the integration account's tracking events.
    examples:
      - name: Log a tracked event
        text: |-
               az logic integration-account log-tracking-event --integration-account-name \\
               "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account regenerate-access-key'] = """
    type: command
    short-summary: Regenerates the integration account access key.
    examples:
      - name: Regenerate access key
        text: |-
               az logic integration-account regenerate-access-key --integration-account-name \\
               "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-assembly'] = """
    type: group
    short-summary: logic integration-account-assembly
"""

helps['logic integration-account-assembly list'] = """
    type: command
    short-summary: List the assemblies for an integration account.
    examples:
      - name: List integration account assemblies
        text: |-
               az logic integration-account-assembly list --integration-account-name \\
               "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-assembly show'] = """
    type: command
    short-summary: Get an assembly for an integration account.
    examples:
      - name: Get an integration account assembly
        text: |-
               az logic integration-account-assembly show --assembly-artifact-name "testAssembly" \\
               --integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-assembly create'] = """
    type: command
    short-summary: Create or update an assembly for an integration account.
    examples:
      - name: Create or update an account assembly
        text: |-
               az logic integration-account-assembly create --assembly-artifact-name "testAssembly" \\
               --integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-assembly update'] = """
    type: command
    short-summary: Create or update an assembly for an integration account.
    examples:
      - name: Create or update an account assembly
        text: |-
               az logic integration-account-assembly create --assembly-artifact-name "testAssembly" \\
               --integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-assembly delete'] = """
    type: command
    short-summary: Delete an assembly for an integration account.
    examples:
      - name: Delete an integration account assembly
        text: |-
               az logic integration-account-assembly delete --assembly-artifact-name "testAssembly" \\
               --integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-assembly list-content-callback-url'] = """
    type: command
    short-summary: Get the content callback url for an integration account assembly.
    examples:
      - name: Get the callback url for an integration account assembly
        text: |-
               az logic integration-account-assembly list-content-callback-url --assembly-artifact-name \\
               "testAssembly" --integration-account-name "testIntegrationAccount" --resource-group \\
               "testResourceGroup"
"""

helps['logic integration-account-batch-configuration'] = """
    type: group
    short-summary: logic integration-account-batch-configuration
"""

helps['logic integration-account-batch-configuration list'] = """
    type: command
    short-summary: List the batch configurations for an integration account.
    examples:
      - name: List batch configurations
        text: |-
               az logic integration-account-batch-configuration list --integration-account-name \\
               "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-batch-configuration show'] = """
    type: command
    short-summary: Get a batch configuration for an integration account.
    examples:
      - name: Get a batch configuration
        text: |-
               az logic integration-account-batch-configuration show --batch-configuration-name \\
               "testBatchConfiguration" --integration-account-name "testIntegrationAccount" \\
               --resource-group "testResourceGroup"
"""

helps['logic integration-account-batch-configuration create'] = """
    type: command
    short-summary: Create or update a batch configuration for an integration account.
    examples:
      - name: Create or update a batch configuration
        text: |-
               az logic integration-account-batch-configuration create --batch-configuration-name \\
               "testBatchConfiguration" --integration-account-name "testIntegrationAccount" \\
               --resource-group "testResourceGroup"
"""

helps['logic integration-account-batch-configuration update'] = """
    type: command
    short-summary: Create or update a batch configuration for an integration account.
    examples:
      - name: Create or update a batch configuration
        text: |-
               az logic integration-account-batch-configuration create --batch-configuration-name \\
               "testBatchConfiguration" --integration-account-name "testIntegrationAccount" \\
               --resource-group "testResourceGroup"
"""

helps['logic integration-account-batch-configuration delete'] = """
    type: command
    short-summary: Delete a batch configuration for an integration account.
    examples:
      - name: Delete a batch configuration
        text: |-
               az logic integration-account-batch-configuration delete --batch-configuration-name \\
               "testBatchConfiguration" --integration-account-name "testIntegrationAccount" \\
               --resource-group "testResourceGroup"
"""

helps['logic integration-account-schema'] = """
    type: group
    short-summary: logic integration-account-schema
"""

helps['logic integration-account-schema list'] = """
    type: command
    short-summary: Gets a list of integration account schemas.
    examples:
      - name: Get schemas by integration account name
        text: |-
               az logic integration-account-schema list --integration-account-name \\
               "<integrationAccountName>" --resource-group "testResourceGroup"
"""

helps['logic integration-account-schema show'] = """
    type: command
    short-summary: Gets an integration account schema.
    examples:
      - name: Get schema by name
        text: |-
               az logic integration-account-schema show --integration-account-name \\
               "testIntegrationAccount" --resource-group "testResourceGroup" --schema-name "testSchema"
"""

helps['logic integration-account-schema create'] = """
    type: command
    short-summary: Creates or updates an integration account schema.
    examples:
      - name: Create or update schema
        text: |-
               az logic integration-account-schema create --integration-account-name \\
               "testIntegrationAccount" --resource-group "testResourceGroup" --schema-name "testSchema"
"""

helps['logic integration-account-schema update'] = """
    type: command
    short-summary: Creates or updates an integration account schema.
    examples:
      - name: Create or update schema
        text: |-
               az logic integration-account-schema create --integration-account-name \\
               "testIntegrationAccount" --resource-group "testResourceGroup" --schema-name "testSchema"
"""

helps['logic integration-account-schema delete'] = """
    type: command
    short-summary: Deletes an integration account schema.
    examples:
      - name: Delete a schema by name
        text: |-
               az logic integration-account-schema delete --integration-account-name \\
               "testIntegrationAccount" --resource-group "testResourceGroup" --schema-name "testSchema"
"""

helps['logic integration-account-schema list-content-callback-url'] = """
    type: command
    short-summary: Get the content callback url.
    examples:
      - name: Get the content callback url
        text: |-
               az logic integration-account-schema list-content-callback-url --integration-account-name \\
               "testIntegrationAccount" --resource-group "testResourceGroup" --schema-name "testSchema"
"""

helps['logic integration-account-map'] = """
    type: group
    short-summary: logic integration-account-map
"""

helps['logic integration-account-map list'] = """
    type: command
    short-summary: Gets a list of integration account maps.
    examples:
      - name: Get maps by integration account name
        text: |-
               az logic integration-account-map list --integration-account-name "testIntegrationAccount" \\
               --resource-group "testResourceGroup"
"""

helps['logic integration-account-map show'] = """
    type: command
    short-summary: Gets an integration account map.
    examples:
      - name: Get map by name
        text: |-
               az logic integration-account-map show --integration-account-name "testIntegrationAccount" \\
               --map-name "testMap" --resource-group "testResourceGroup"
"""

helps['logic integration-account-map create'] = """
    type: command
    short-summary: Creates or updates an integration account map.
    examples:
      - name: Create or update a map
        text: |-
               az logic integration-account-map create --integration-account-name \\
               "testIntegrationAccount" --map-name "testMap" --resource-group "testResourceGroup"
"""

helps['logic integration-account-map update'] = """
    type: command
    short-summary: Creates or updates an integration account map.
    examples:
      - name: Create or update a map
        text: |-
               az logic integration-account-map create --integration-account-name \\
               "testIntegrationAccount" --map-name "testMap" --resource-group "testResourceGroup"
"""

helps['logic integration-account-map delete'] = """
    type: command
    short-summary: Deletes an integration account map.
    examples:
      - name: Delete a map
        text: |-
               az logic integration-account-map delete --integration-account-name \\
               "testIntegrationAccount" --map-name "testMap" --resource-group "testResourceGroup"
"""

helps['logic integration-account-map list-content-callback-url'] = """
    type: command
    short-summary: Get the content callback url.
    examples:
      - name: Get the content callback url
        text: |-
               az logic integration-account-map list-content-callback-url --integration-account-name \\
               "testIntegrationAccount" --map-name "testMap" --resource-group "testResourceGroup"
"""

helps['logic integration-account-partner'] = """
    type: group
    short-summary: logic integration-account-partner
"""

helps['logic integration-account-partner list'] = """
    type: command
    short-summary: Gets a list of integration account partners.
    examples:
      - name: Get partners by integration account name
        text: |-
               az logic integration-account-partner list --integration-account-name \\
               "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-partner show'] = """
    type: command
    short-summary: Gets an integration account partner.
    examples:
      - name: Get partner by name
        text: |-
               az logic integration-account-partner show --integration-account-name \\
               "testIntegrationAccount" --partner-name "testPartner" --resource-group \\
               "testResourceGroup"
"""

helps['logic integration-account-partner create'] = """
    type: command
    short-summary: Creates or updates an integration account partner.
    examples:
      - name: Create or update a partner
        text: |-
               az logic integration-account-partner create --integration-account-name \\
               "testIntegrationAccount" --partner-name "testPartner" --resource-group \\
               "testResourceGroup"
"""

helps['logic integration-account-partner update'] = """
    type: command
    short-summary: Creates or updates an integration account partner.
    examples:
      - name: Create or update a partner
        text: |-
               az logic integration-account-partner create --integration-account-name \\
               "testIntegrationAccount" --partner-name "testPartner" --resource-group \\
               "testResourceGroup"
"""

helps['logic integration-account-partner delete'] = """
    type: command
    short-summary: Deletes an integration account partner.
    examples:
      - name: Delete a partner
        text: |-
               az logic integration-account-partner delete --integration-account-name \\
               "testIntegrationAccount" --partner-name "testPartner" --resource-group \\
               "testResourceGroup"
"""

helps['logic integration-account-partner list-content-callback-url'] = """
    type: command
    short-summary: Get the content callback url.
    examples:
      - name: Get the content callback url
        text: |-
               az logic integration-account-partner list-content-callback-url --integration-account-name \\
               "testIntegrationAccount" --partner-name "testPartner" --resource-group \\
               "testResourceGroup"
"""

helps['logic integration-account-agreement'] = """
    type: group
    short-summary: logic integration-account-agreement
"""

helps['logic integration-account-agreement list'] = """
    type: command
    short-summary: Gets a list of integration account agreements.
    examples:
      - name: Get agreements by integration account name
        text: |-
               az logic integration-account-agreement list --integration-account-name \\
               "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-agreement show'] = """
    type: command
    short-summary: Gets an integration account agreement.
    examples:
      - name: Get agreement by name
        text: |-
               az logic integration-account-agreement show --agreement-name "testAgreement" \\
               --integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-agreement create'] = """
    type: command
    short-summary: Creates or updates an integration account agreement.
    examples:
      - name: Create or update an agreement
        text: |-
               az logic integration-account-agreement create --agreement-name "testAgreement" \\
               --integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-agreement update'] = """
    type: command
    short-summary: Creates or updates an integration account agreement.
    examples:
      - name: Create or update an agreement
        text: |-
               az logic integration-account-agreement create --agreement-name "testAgreement" \\
               --integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-agreement delete'] = """
    type: command
    short-summary: Deletes an integration account agreement.
    examples:
      - name: Delete an agreement
        text: |-
               az logic integration-account-agreement delete --agreement-name "testAgreement" \\
               --integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-agreement list-content-callback-url'] = """
    type: command
    short-summary: Get the content callback url.
    examples:
      - name: Get the content callback url
        text: |-
               az logic integration-account-agreement list-content-callback-url --agreement-name \\
               "testAgreement" --integration-account-name "testIntegrationAccount" --resource-group \\
               "testResourceGroup"
"""

helps['logic integration-account-certificate'] = """
    type: group
    short-summary: logic integration-account-certificate
"""

helps['logic integration-account-certificate list'] = """
    type: command
    short-summary: Gets a list of integration account certificates.
    examples:
      - name: Get certificates by integration account name
        text: |-
               az logic integration-account-certificate list --integration-account-name \\
               "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-certificate show'] = """
    type: command
    short-summary: Gets an integration account certificate.
    examples:
      - name: Get certificate by name
        text: |-
               az logic integration-account-certificate show --certificate-name "testCertificate" \\
               --integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-certificate create'] = """
    type: command
    short-summary: Creates or updates an integration account certificate.
    examples:
      - name: Create or update a certificate
        text: |-
               az logic integration-account-certificate create --certificate-name "testCertificate" \\
               --integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-certificate update'] = """
    type: command
    short-summary: Creates or updates an integration account certificate.
    examples:
      - name: Create or update a certificate
        text: |-
               az logic integration-account-certificate create --certificate-name "testCertificate" \\
               --integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-certificate delete'] = """
    type: command
    short-summary: Deletes an integration account certificate.
    examples:
      - name: Delete a certificate
        text: |-
               az logic integration-account-certificate delete --certificate-name "testCertificate" \\
               --integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-session'] = """
    type: group
    short-summary: logic integration-account-session
"""

helps['logic integration-account-session list'] = """
    type: command
    short-summary: Gets a list of integration account sessions.
    examples:
      - name: List by integration account session examples
        text: |-
               az logic integration-account-session list --integration-account-name "testia123" \\
               --resource-group "testrg123"
"""

helps['logic integration-account-session show'] = """
    type: command
    short-summary: Gets an integration account session.
    examples:
      - name: Get integration account session examples
        text: |-
               az logic integration-account-session show --integration-account-name "testia123" \\
               --resource-group "testrg123" --session-name "testsession123-ICN"
"""

helps['logic integration-account-session create'] = """
    type: command
    short-summary: Creates or updates an integration account session.
    examples:
      - name: Create or update integration account session example
        text: |-
               az logic integration-account-session create --integration-account-name "testia123" \\
               --resource-group "testrg123" --session-name "testsession123-ICN"
"""

helps['logic integration-account-session update'] = """
    type: command
    short-summary: Creates or updates an integration account session.
    examples:
      - name: Create or update integration account session example
        text: |-
               az logic integration-account-session create --integration-account-name "testia123" \\
               --resource-group "testrg123" --session-name "testsession123-ICN"
"""

helps['logic integration-account-session delete'] = """
    type: command
    short-summary: Deletes an integration account session.
    examples:
      - name: Delete integration account session examples
        text: |-
               az logic integration-account-session delete --integration-account-name "testia123" \\
               --resource-group "testrg123" --session-name "testsession123-ICN"
"""

helps['logic integration-service-environment'] = """
    type: group
    short-summary: logic integration-service-environment
"""

helps['logic integration-service-environment list'] = """
    type: command
    short-summary: Gets a list of integration service environments by subscription.
    examples:
      - name: List integration service environments by resource group name
        text: |-
               az logic integration-service-environment list --resource-group "testResourceGroup"
"""

helps['logic integration-service-environment show'] = """
    type: command
    short-summary: Gets an integration service environment.
    examples:
      - name: Get integration service environment by name
        text: |-
               az logic integration-service-environment show --integration-service-environment-name \\
               "testIntegrationServiceEnvironment" --resource-group "testResourceGroup"
"""

helps['logic integration-service-environment create'] = """
    type: command
    short-summary: Creates or updates an integration service environment.
    examples:
      - name: Create or update an integration service environment
        text: |-
               az logic integration-service-environment create --integration-service-environment-name \\
               "testIntegrationServiceEnvironment" --resource-group "testResourceGroup"
"""

helps['logic integration-service-environment update'] = """
    type: command
    short-summary: Updates an integration service environment.
    examples:
      - name: Patch an integration service environment
        text: |-
               az logic integration-service-environment update --integration-service-environment-name \\
               "testIntegrationServiceEnvironment" --resource-group "testResourceGroup"
"""

helps['logic integration-service-environment delete'] = """
    type: command
    short-summary: Deletes an integration service environment.
    examples:
      - name: Delete an integration account
        text: |-
               az logic integration-service-environment delete --integration-service-environment-name \\
               "testIntegrationServiceEnvironment" --resource-group "testResourceGroup"
"""

helps['logic integration-service-environment restart'] = """
    type: command
    short-summary: Restarts an integration service environment.
    examples:
      - name: Restarts an integration service environment
        text: |-
               az logic integration-service-environment restart --integration-service-environment-name \\
               "testIntegrationServiceEnvironment" --resource-group "testResourceGroup"
"""

helps['logic integration-service-environment-sku'] = """
    type: group
    short-summary: logic integration-service-environment-sku
"""

helps['logic integration-service-environment-sku list'] = """
    type: command
    short-summary: Gets a list of integration service environment Skus.
    examples:
      - name: List integration service environment skus
        text: |-
               az logic integration-service-environment-sku list --integration-service-environment-name \\
               "testIntegrationServiceEnvironment" --resource-group "testResourceGroup"
"""

helps['logic integration-service-environment-network-health'] = """
    type: group
    short-summary: logic integration-service-environment-network-health
"""

helps['logic integration-service-environment-network-health show'] = """
    type: command
    short-summary: Gets the integration service environment network health.
    examples:
      - name: Gets the integration service environment network health
        text: |-
               az logic integration-service-environment-network-health show \\
               --integration-service-environment-name "testIntegrationServiceEnvironment" \\
               --resource-group "testResourceGroup"
"""

helps['logic integration-service-environment-managed-api'] = """
    type: group
    short-summary: logic integration-service-environment-managed-api
"""

helps['logic integration-service-environment-managed-api list'] = """
    type: command
    short-summary: Gets the integration service environment managed Apis.
    examples:
      - name: Gets the integration service environment managed Apis
        text: |-
               az logic integration-service-environment-managed-api list \\
               --integration-service-environment-name "testIntegrationServiceEnvironment" \\
               --resource-group "testResourceGroup"
"""

helps['logic integration-service-environment-managed-api show'] = """
    type: command
    short-summary: Gets the integration service environment managed Api.
    examples:
      - name: Gets the integration service environment managed Apis
        text: |-
               az logic integration-service-environment-managed-api show --api-name "servicebus" \\
               --integration-service-environment-name "testIntegrationServiceEnvironment" \\
               --resource-group "testResourceGroup"
"""

helps['logic integration-service-environment-managed-api delete'] = """
    type: command
    short-summary: Deletes the integration service environment managed Api.
    examples:
      - name: Deletes the integration service environment managed Apis
        text: |-
               az logic integration-service-environment-managed-api delete --api-name "servicebus" \\
               --integration-service-environment-name "testIntegrationServiceEnvironment" \\
               --resource-group "testResourceGroup"
"""

helps['logic integration-service-environment-managed-api put'] = """
    type: command
    short-summary: Puts the integration service environment managed Api.
    examples:
      - name: Gets the integration service environment managed Apis
        text: |-
               az logic integration-service-environment-managed-api put --api-name "servicebus" \\
               --integration-service-environment-name "testIntegrationServiceEnvironment" \\
               --resource-group "testResourceGroup"
"""

helps['logic integration-service-environment-managed-api-operation'] = """
    type: group
    short-summary: logic integration-service-environment-managed-api-operation
"""

helps['logic integration-service-environment-managed-api-operation list'] = """
    type: command
    short-summary: Gets the managed Api operations.
    examples:
      - name: Gets the integration service environment managed Apis
        text: |-
               az logic integration-service-environment-managed-api-operation list --api-name \\
               "servicebus" --integration-service-environment-name "testIntegrationServiceEnvironment" \\
               --resource-group "testResourceGroup"
"""
