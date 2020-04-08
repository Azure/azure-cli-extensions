# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
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
               az logic workflow list --resource-group "test-resource-group"
"""

helps['logic workflow show'] = """
    type: command
    short-summary: Gets a workflow.
    examples:
      - name: Get a workflow
        text: |-
               az logic workflow show --resource-group "test-resource-group" --workflow-name "test-workflow"
"""

helps['logic workflow create'] = """
    type: command
    short-summary: Creates or updates a workflow.
    examples:
      - name: Create or update a workflow
        text: |-
               az logic workflow create --resource-group "test-resource-group" --location "brazilsouth" --definition "{\
\\"$schema\\":\\"https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.js\
on#\\",\\"actions\\":{\\"Find_pet_by_ID\\":{\\"type\\":\\"ApiConnection\\",\\"inputs\\":{\\"path\\":\\"/pet/@{encodeURI\
Component('1')}\\",\\"method\\":\\"get\\",\\"host\\":{\\"connection\\":{\\"name\\":\\"@parameters('$connections')['test\
-custom-connector']['connectionId']\\"}}},\\"runAfter\\":{}}},\\"contentVersion\\":\\"1.0.0.0\\",\\"outputs\\":{},\\"pa\
rameters\\":{\\"$connections\\":{\\"type\\":\\"Object\\",\\"defaultValue\\":{}}},\\"triggers\\":{\\"manual\\":{\\"type\
\\":\\"Request\\",\\"inputs\\":{\\"schema\\":{}},\\"kind\\":\\"Http\\"}}}" --integration-account id=/subscriptions/34ad\
fa4f-cedf-4dc0-ba29-b6d1a69ab345/resourceGroups/test-resource-group/providers/Microsoft.Logic/integrationAccounts/test-\
integration-account --parameters "{\\"$connections\\":{\\"value\\":{\\"test-custom-connector\\":{\\"connectionId\\":\\"\
/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourceGroups/test-resource-group/providers/Microsoft.Web/connecti\
ons/test-custom-connector\\",\\"connectionName\\":\\"test-custom-connector\\",\\"id\\":\\"/subscriptions/34adfa4f-cedf-\
4dc0-ba29-b6d1a69ab345/providers/Microsoft.Web/locations/brazilsouth/managedApis/test-custom-connector\\"}}}}" --workfl\
ow-name "test-workflow"
"""

helps['logic workflow update'] = """
    type: command
    short-summary: Updates a workflow.
    examples:
      - name: Patch a workflow
        text: |-
               az logic workflow update --resource-group "test-resource-group" --location "brazilsouth" --definition "{\
\\"$schema\\":\\"https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.js\
on#\\",\\"actions\\":{\\"Find_pet_by_ID\\":{\\"type\\":\\"ApiConnection\\",\\"inputs\\":{\\"path\\":\\"/pet/@{encodeURI\
Component('1')}\\",\\"method\\":\\"get\\",\\"host\\":{\\"connection\\":{\\"name\\":\\"@parameters('$connections')['test\
-custom-connector']['connectionId']\\"}}},\\"runAfter\\":{}}},\\"contentVersion\\":\\"1.0.0.0\\",\\"outputs\\":{},\\"pa\
rameters\\":{\\"$connections\\":{\\"type\\":\\"Object\\",\\"defaultValue\\":{}}},\\"triggers\\":{\\"manual\\":{\\"type\
\\":\\"Request\\",\\"inputs\\":{\\"schema\\":{}},\\"kind\\":\\"Http\\"}}}" --integration-account id=/subscriptions/34ad\
fa4f-cedf-4dc0-ba29-b6d1a69ab345/resourceGroups/test-resource-group/providers/Microsoft.Logic/integrationAccounts/test-\
integration-account --parameters "{\\"$connections\\":{\\"value\\":{\\"test-custom-connector\\":{\\"connectionId\\":\\"\
/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourceGroups/test-resource-group/providers/Microsoft.Web/connecti\
ons/test-custom-connector\\",\\"connectionName\\":\\"test-custom-connector\\",\\"id\\":\\"/subscriptions/34adfa4f-cedf-\
4dc0-ba29-b6d1a69ab345/providers/Microsoft.Web/locations/brazilsouth/managedApis/test-custom-connector\\"}}}}" --workfl\
ow-name "test-workflow"
"""

helps['logic workflow delete'] = """
    type: command
    short-summary: Deletes a workflow.
    examples:
      - name: Delete a workflow
        text: |-
               az logic workflow delete --resource-group "test-resource-group" --workflow-name "test-workflow"
"""

helps['logic workflow disable'] = """
    type: command
    short-summary: Disables a workflow.
    examples:
      - name: Disable a workflow
        text: |-
               az logic workflow disable --resource-group "test-resource-group" --workflow-name "test-workflow"
"""

helps['logic workflow enable'] = """
    type: command
    short-summary: Enables a workflow.
    examples:
      - name: Enable a workflow
        text: |-
               az logic workflow enable --resource-group "test-resource-group" --workflow-name "test-workflow"
"""

helps['logic workflow generate-upgraded-definition'] = """
    type: command
    short-summary: Generates the upgraded definition for a workflow.
    examples:
      - name: Generate an upgraded definition
        text: |-
               az logic workflow generate-upgraded-definition --target-schema-version "2016-06-01" --resource-group "te\
st-resource-group" --workflow-name "test-workflow"
"""

helps['logic workflow list-callback-url'] = """
    type: command
    short-summary: Get the workflow callback Url.
    examples:
      - name: Get callback url
        text: |-
               az logic workflow list-callback-url --key-type "Primary" --not-after "2018-04-19T16:00:00Z" --resource-g\
roup "testResourceGroup" --workflow-name "testWorkflow"
"""

helps['logic workflow list-swagger'] = """
    type: command
    short-summary: Gets an OpenAPI definition for the workflow.
    examples:
      - name: Get the swagger for a workflow
        text: |-
               az logic workflow list-swagger --resource-group "testResourceGroup" --workflow-name "testWorkflowName"
"""

helps['logic workflow move'] = """
    type: command
    short-summary: Moves an existing workflow.
    examples:
      - name: Move a workflow
        text: |-
               az logic workflow move --resource-group "testResourceGroup" --workflow-name "testWorkflow"
"""

helps['logic workflow regenerate-access-key'] = """
    type: command
    short-summary: Regenerates the callback URL access key for request triggers.
    examples:
      - name: Regenerate the callback URL access key for request triggers
        text: |-
               az logic workflow regenerate-access-key --resource-group "testResourceGroup" --workflow-name "testWorkfl\
owName"
"""

helps['logic workflow validate-by-location'] = """
    type: command
    short-summary: Validates the workflow definition.
    examples:
      - name: Validate a workflow
        text: |-
               az logic workflow validate-by-location --location "brazilsouth" --resource-group "test-resource-group" -\
-workflow-name "test-workflow"
"""

helps['logic workflow validate-by-resource-group'] = """
    type: command
    short-summary: Validates the workflow.
    examples:
      - name: Validate a workflow
        text: |-
               az logic workflow validate-by-resource-group --resource-group "test-resource-group" --location "brazilso\
uth" --definition "{\\"$schema\\":\\"https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/w\
orkflowdefinition.json#\\",\\"actions\\":{},\\"contentVersion\\":\\"1.0.0.0\\",\\"outputs\\":{},\\"parameters\\":{},\\"\
triggers\\":{}}" --integration-account id=/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourceGroups/test-resou\
rce-group/providers/Microsoft.Logic/integrationAccounts/test-integration-account --workflow-name "test-workflow"
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
               az logic workflow-version list --resource-group "test-resource-group" --workflow-name "test-workflow"
"""

helps['logic workflow-version show'] = """
    type: command
    short-summary: Gets a workflow version.
    examples:
      - name: Get a workflow version
        text: |-
               az logic workflow-version show --resource-group "test-resource-group" --version-id "08586676824806722526\
" --workflow-name "test-workflow"
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
               az logic workflow-trigger list --resource-group "test-resource-group" --workflow-name "test-workflow"
"""

helps['logic workflow-trigger show'] = """
    type: command
    short-summary: Get the trigger schema as JSON.
    examples:
      - name: Get a workflow trigger
        text: |-
               az logic workflow-trigger show --resource-group "test-resource-group" --trigger-name "manual" --workflow\
-name "test-workflow"
"""

helps['logic workflow-trigger list-callback-url'] = """
    type: command
    short-summary: Get the callback URL for a workflow trigger.
    examples:
      - name: Get the callback URL for a trigger
        text: |-
               az logic workflow-trigger list-callback-url --resource-group "test-resource-group" --trigger-name "manua\
l" --workflow-name "test-workflow"
"""

helps['logic workflow-trigger reset'] = """
    type: command
    short-summary: Resets a workflow trigger.
    examples:
      - name: Reset trigger
        text: |-
               az logic workflow-trigger reset --resource-group "testResourceGroup" --trigger-name "testTrigger" --work\
flow-name "testWorkflow"
"""

helps['logic workflow-trigger run'] = """
    type: command
    short-summary: Runs a workflow trigger.
    examples:
      - name: Run a workflow trigger
        text: |-
               az logic workflow-trigger run --resource-group "test-resource-group" --trigger-name "manual" --workflow-\
name "test-workflow"
"""

helps['logic workflow-trigger set-state'] = """
    type: command
    short-summary: Sets the state of a workflow trigger.
    examples:
      - name: Set trigger state
        text: |-
               az logic workflow-trigger set-state --resource-group "testResourceGroup" --source "{\\"id\\":\\"subscrip\
tions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourceGroups/sourceResGroup/providers/Microsoft.Logic/workflows/sourceWork\
flow/triggers/sourceTrigger\\"}" --trigger-name "testTrigger" --workflow-name "testWorkflow"
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
               az logic workflow-version-trigger list-callback-url --key-type "Primary" --not-after "2017-03-05T08:00:0\
0Z" --resource-group "testResourceGroup" --trigger-name "testTriggerName" --version-id "testWorkflowVersionId" --workfl\
ow-name "testWorkflowName"
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
               az logic workflow-trigger-history list --resource-group "testResourceGroup" --trigger-name "testTriggerN\
ame" --workflow-name "testWorkflowName"
"""

helps['logic workflow-trigger-history show'] = """
    type: command
    short-summary: Gets a workflow trigger history.
    examples:
      - name: Get a workflow trigger history
        text: |-
               az logic workflow-trigger-history show --history-name "08586676746934337772206998657CU22" --resource-gro\
up "testResourceGroup" --trigger-name "testTriggerName" --workflow-name "testWorkflowName"
"""

helps['logic workflow-trigger-history resubmit'] = """
    type: command
    short-summary: Resubmits a workflow run based on the trigger history.
    examples:
      - name: Resubmit a workflow run based on the trigger history
        text: |-
               az logic workflow-trigger-history resubmit --history-name "testHistoryName" --resource-group "testResour\
ceGroup" --trigger-name "testTriggerName" --workflow-name "testWorkflowName"
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
               az logic workflow-run list --resource-group "test-resource-group" --workflow-name "test-workflow"
"""

helps['logic workflow-run show'] = """
    type: command
    short-summary: Gets a workflow run.
    examples:
      - name: Get a run for a workflow
        text: |-
               az logic workflow-run show --resource-group "test-resource-group" --run-name "08586676746934337772206998\
657CU22" --workflow-name "test-workflow"
"""

helps['logic workflow-run cancel'] = """
    type: command
    short-summary: Cancels a workflow run.
    examples:
      - name: Cancel a workflow run
        text: |-
               az logic workflow-run cancel --resource-group "test-resource-group" --run-name "085866767469343377722069\
98657CU22" --workflow-name "test-workflow"
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
               az logic workflow-run-action list --resource-group "test-resource-group" --run-name "0858667674693433777\
2206998657CU22" --workflow-name "test-workflow"
"""

helps['logic workflow-run-action show'] = """
    type: command
    short-summary: Gets a workflow run action.
    examples:
      - name: Get a workflow run action
        text: |-
               az logic workflow-run-action show --action-name "HTTP" --resource-group "test-resource-group" --run-name\
 "08586676746934337772206998657CU22" --workflow-name "test-workflow"
"""

helps['logic workflow-run-action list-expression-trace'] = """
    type: command
    short-summary: Lists a workflow run expression trace.
    examples:
      - name: List expression traces
        text: |-
               az logic workflow-run-action list-expression-trace --action-name "testAction" --resource-group "testReso\
urceGroup" --run-name "08586776228332053161046300351" --workflow-name "testFlow"
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
               az logic workflow-run-action-repetition list --action-name "testAction" --resource-group "testResourceGr\
oup" --run-name "08586776228332053161046300351" --workflow-name "testFlow"
"""

helps['logic workflow-run-action-repetition show'] = """
    type: command
    short-summary: Get a workflow run action repetition.
    examples:
      - name: Get a repetition
        text: |-
               az logic workflow-run-action-repetition show --action-name "testAction" --repetition-name "000001" --res\
ource-group "testResourceGroup" --run-name "08586776228332053161046300351" --workflow-name "testFlow"
"""

helps['logic workflow-run-action-repetition list-expression-trace'] = """
    type: command
    short-summary: Lists a workflow run expression trace.
    examples:
      - name: List expression traces for a repetition
        text: |-
               az logic workflow-run-action-repetition list-expression-trace --action-name "testAction" --repetition-na\
me "000001" --resource-group "testResourceGroup" --run-name "08586776228332053161046300351" --workflow-name "testFlow"
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
               az logic workflow-run-action-repetition-request-history list --action-name "HTTP_Webhook" --repetition-n\
ame "000001" --resource-group "test-resource-group" --run-name "08586776228332053161046300351" --workflow-name "test-wo\
rkflow"
"""

helps['logic workflow-run-action-repetition-request-history show'] = """
    type: command
    short-summary: Gets a workflow run repetition request history.
    examples:
      - name: Get a repetition request history
        text: |-
               az logic workflow-run-action-repetition-request-history show --action-name "HTTP_Webhook" --repetition-n\
ame "000001" --request-history-name "08586611142732800686" --resource-group "test-resource-group" --run-name "085867762\
28332053161046300351" --workflow-name "test-workflow"
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
               az logic workflow-run-action-request-history list --action-name "HTTP_Webhook" --resource-group "test-re\
source-group" --run-name "08586776228332053161046300351" --workflow-name "test-workflow"
"""

helps['logic workflow-run-action-request-history show'] = """
    type: command
    short-summary: Gets a workflow run request history.
    examples:
      - name: Get a request history
        text: |-
               az logic workflow-run-action-request-history show --action-name "HTTP_Webhook" --request-history-name "0\
8586611142732800686" --resource-group "test-resource-group" --run-name "08586776228332053161046300351" --workflow-name \
"test-workflow"
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
               az logic workflow-run-action-scope-repetition list --action-name "for_each" --resource-group "testResour\
ceGroup" --run-name "08586776228332053161046300351" --workflow-name "testFlow"
"""

helps['logic workflow-run-action-scope-repetition show'] = """
    type: command
    short-summary: Get a workflow run action scoped repetition.
    examples:
      - name: Get a scoped repetition
        text: |-
               az logic workflow-run-action-scope-repetition show --action-name "for_each" --repetition-name "000000" -\
-resource-group "testResourceGroup" --run-name "08586776228332053161046300351" --workflow-name "testFlow"
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
               az logic workflow-run-operation show --operation-id "ebdcbbde-c4db-43ec-987c-fd0f7726f43b" --resource-gr\
oup "testResourceGroup" --run-name "08586774142730039209110422528" --workflow-name "testFlow"
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
               az logic integration-account show --integration-account-name "testIntegrationAccount" --resource-group "\
testResourceGroup"
"""

helps['logic integration-account create'] = """
    type: command
    short-summary: Creates or updates an integration account.
    examples:
      - name: Create or update an integration account
        text: |-
               az logic integration-account create --location "westus" --sku name=Standard --integration-account-name "\
testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account update'] = """
    type: command
    short-summary: Updates an integration account.
    examples:
      - name: Patch an integration account
        text: |-
               az logic integration-account update --location "westus" --sku name=Standard --integration-account-name "\
testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account delete'] = """
    type: command
    short-summary: Deletes an integration account.
    examples:
      - name: Delete an integration account
        text: |-
               az logic integration-account delete --integration-account-name "testIntegrationAccount" --resource-group\
 "testResourceGroup"
"""

helps['logic integration-account list-callback-url'] = """
    type: command
    short-summary: Gets the integration account callback URL.
    examples:
      - name: List IntegrationAccount callback URL
        text: |-
               az logic integration-account list-callback-url --integration-account-name "testIntegrationAccount" --key\
-type "Primary" --not-after "2017-03-05T08:00:00Z" --resource-group "testResourceGroup"
"""

helps['logic integration-account list-key-vault-key'] = """
    type: command
    short-summary: Gets the integration account's Key Vault keys.
    examples:
      - name: Get Integration Account callback URL
        text: |-
               az logic integration-account list-key-vault-key --integration-account-name "testIntegrationAccount" --ke\
y-vault id=subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourceGroups/testResourceGroup/providers/Microsoft.KeyV\
ault/vaults/testKeyVault --skip-token "testSkipToken" --resource-group "testResourceGroup"
"""

helps['logic integration-account log-tracking-event'] = """
    type: command
    short-summary: Logs the integration account's tracking events.
    examples:
      - name: Log a tracked event
        text: |-
               az logic integration-account log-tracking-event --integration-account-name "testIntegrationAccount" --ev\
ents "[{\\"error\\":{\\"code\\":\\"NotFound\\",\\"message\\":\\"Some error occurred\\"},\\"eventLevel\\":\\"Information\
al\\",\\"eventTime\\":\\"2016-08-05T01:54:49.505567Z\\",\\"record\\":{\\"agreementProperties\\":{\\"agreementName\\":\\\
"testAgreement\\",\\"as2From\\":\\"testas2from\\",\\"as2To\\":\\"testas2to\\",\\"receiverPartnerName\\":\\"testPartner2\
\\",\\"senderPartnerName\\":\\"testPartner1\\"},\\"messageProperties\\":{\\"IsMessageEncrypted\\":false,\\"IsMessageSig\
ned\\":false,\\"correlationMessageId\\":\\"Unique message identifier\\",\\"direction\\":\\"Receive\\",\\"dispositionTyp\
e\\":\\"received-success\\",\\"fileName\\":\\"test\\",\\"isMdnExpected\\":true,\\"isMessageCompressed\\":false,\\"isMes\
sageFailed\\":false,\\"isNrrEnabled\\":true,\\"mdnType\\":\\"Async\\",\\"messageId\\":\\"12345\\"}},\\"recordType\\":\\\
"AS2Message\\"}]" --source-type "Microsoft.Logic/workflows" --resource-group "testResourceGroup"
"""

helps['logic integration-account regenerate-access-key'] = """
    type: command
    short-summary: Regenerates the integration account access key.
    examples:
      - name: Regenerate access key
        text: |-
               az logic integration-account regenerate-access-key --integration-account-name "testIntegrationAccount" -\
-key-type "Primary" --resource-group "testResourceGroup"
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
               az logic integration-account-assembly list --integration-account-name "testIntegrationAccount" --resourc\
e-group "testResourceGroup"
"""

helps['logic integration-account-assembly show'] = """
    type: command
    short-summary: Get an assembly for an integration account.
    examples:
      - name: Get an integration account assembly
        text: |-
               az logic integration-account-assembly show --assembly-artifact-name "testAssembly" --integration-account\
-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-assembly create'] = """
    type: command
    short-summary: Create or update an assembly for an integration account.
    examples:
      - name: Create or update an account assembly
        text: |-
               az logic integration-account-assembly create --location "westus" --properties assembly-name=System.Ident\
ityModel.Tokens.Jwt content=Base64 encoded Assembly Content metadata={} --assembly-artifact-name "testAssembly" --integ\
ration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-assembly update'] = """
    type: command
    short-summary: Create or update an assembly for an integration account.
    examples:
      - name: Create or update an account assembly
        text: |-
               az logic integration-account-assembly create --location "westus" --properties assembly-name=System.Ident\
ityModel.Tokens.Jwt content=Base64 encoded Assembly Content metadata={} --assembly-artifact-name "testAssembly" --integ\
ration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-assembly delete'] = """
    type: command
    short-summary: Delete an assembly for an integration account.
    examples:
      - name: Delete an integration account assembly
        text: |-
               az logic integration-account-assembly delete --assembly-artifact-name "testAssembly" --integration-accou\
nt-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-assembly list-content-callback-url'] = """
    type: command
    short-summary: Get the content callback url for an integration account assembly.
    examples:
      - name: Get the callback url for an integration account assembly
        text: |-
               az logic integration-account-assembly list-content-callback-url --assembly-artifact-name "testAssembly" \
--integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
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
               az logic integration-account-batch-configuration list --integration-account-name "testIntegrationAccount\
" --resource-group "testResourceGroup"
"""

helps['logic integration-account-batch-configuration show'] = """
    type: command
    short-summary: Get a batch configuration for an integration account.
    examples:
      - name: Get a batch configuration
        text: |-
               az logic integration-account-batch-configuration show --batch-configuration-name "testBatchConfiguration\
" --integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-batch-configuration create'] = """
    type: command
    short-summary: Create or update a batch configuration for an integration account.
    examples:
      - name: Create or update a batch configuration
        text: |-
               az logic integration-account-batch-configuration create --location "westus" --properties "{\\"batchGroup\
Name\\":\\"DEFAULT\\",\\"releaseCriteria\\":{\\"batchSize\\":234567,\\"messageCount\\":10,\\"recurrence\\":{\\"frequenc\
y\\":\\"Minute\\",\\"interval\\":1,\\"startTime\\":\\"2017-03-24T11:43:00\\",\\"timeZone\\":\\"India Standard Time\\"}}\
}" --batch-configuration-name "testBatchConfiguration" --integration-account-name "testIntegrationAccount" --resource-g\
roup "testResourceGroup"
"""

helps['logic integration-account-batch-configuration update'] = """
    type: command
    short-summary: Create or update a batch configuration for an integration account.
    examples:
      - name: Create or update a batch configuration
        text: |-
               az logic integration-account-batch-configuration create --location "westus" --properties "{\\"batchGroup\
Name\\":\\"DEFAULT\\",\\"releaseCriteria\\":{\\"batchSize\\":234567,\\"messageCount\\":10,\\"recurrence\\":{\\"frequenc\
y\\":\\"Minute\\",\\"interval\\":1,\\"startTime\\":\\"2017-03-24T11:43:00\\",\\"timeZone\\":\\"India Standard Time\\"}}\
}" --batch-configuration-name "testBatchConfiguration" --integration-account-name "testIntegrationAccount" --resource-g\
roup "testResourceGroup"
"""

helps['logic integration-account-batch-configuration delete'] = """
    type: command
    short-summary: Delete a batch configuration for an integration account.
    examples:
      - name: Delete a batch configuration
        text: |-
               az logic integration-account-batch-configuration delete --batch-configuration-name "testBatchConfigurati\
on" --integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
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
               az logic integration-account-schema list --integration-account-name "<integrationAccountName>" --resourc\
e-group "testResourceGroup"
"""

helps['logic integration-account-schema show'] = """
    type: command
    short-summary: Gets an integration account schema.
    examples:
      - name: Get schema by name
        text: |-
               az logic integration-account-schema show --integration-account-name "testIntegrationAccount" --resource-\
group "testResourceGroup" --schema-name "testSchema"
"""

helps['logic integration-account-schema create'] = """
    type: command
    short-summary: Creates or updates an integration account schema.
    examples:
      - name: Create or update schema
        text: |-
               az logic integration-account-schema create --location "westus" --content "<?xml version=\\"1.0\\" encodi\
ng=\\"utf-16\\"?>\\r\\n<xs:schema xmlns:b=\\"http://schemas.microsoft.com/BizTalk/2003\\" xmlns=\\"http://Inbound_EDI.O\
rderFile\\" targetNamespace=\\"http://Inbound_EDI.OrderFile\\" xmlns:xs=\\"http://www.w3.org/2001/XMLSchema\\">\\r\\n  \
<xs:annotation>\\r\\n    <xs:appinfo>\\r\\n      <b:schemaInfo default_pad_char=\\" \\" count_positions_by_byte=\\"fals\
e\\" parser_optimization=\\"speed\\" lookahead_depth=\\"3\\" suppress_empty_nodes=\\"false\\" generate_empty_nodes=\\"t\
rue\\" allow_early_termination=\\"false\\" early_terminate_optional_fields=\\"false\\" allow_message_breakup_of_infix_r\
oot=\\"false\\" compile_parse_tables=\\"false\\" standard=\\"Flat File\\" root_reference=\\"OrderFile\\" />\\r\\n      \
<schemaEditorExtension:schemaInfo namespaceAlias=\\"b\\" extensionClass=\\"Microsoft.BizTalk.FlatFileExtension.FlatFile\
Extension\\" standardName=\\"Flat File\\" xmlns:schemaEditorExtension=\\"http://schemas.microsoft.com/BizTalk/2003/Sche\
maEditorExtensions\\" />\\r\\n    </xs:appinfo>\\r\\n  </xs:annotation>\\r\\n  <xs:element name=\\"OrderFile\\">\\r\\n \
   <xs:annotation>\\r\\n      <xs:appinfo>\\r\\n        <b:recordInfo structure=\\"delimited\\" preserve_delimiter_for_\
empty_data=\\"true\\" suppress_trailing_delimiters=\\"false\\" sequence_number=\\"1\\" />\\r\\n      </xs:appinfo>\\r\\\
n    </xs:annotation>\\r\\n    <xs:complexType>\\r\\n      <xs:sequence>\\r\\n        <xs:annotation>\\r\\n          <x\
s:appinfo>\\r\\n            <b:groupInfo sequence_number=\\"0\\" />\\r\\n          </xs:appinfo>\\r\\n        </xs:anno\
tation>\\r\\n        <xs:element name=\\"Order\\">\\r\\n          <xs:annotation>\\r\\n            <xs:appinfo>\\r\\n  \
            <b:recordInfo sequence_number=\\"1\\" structure=\\"delimited\\" preserve_delimiter_for_empty_data=\\"true\\\
" suppress_trailing_delimiters=\\"false\\" child_delimiter_type=\\"hex\\" child_delimiter=\\"0x0D 0x0A\\" child_order=\
\\"infix\\" />\\r\\n            </xs:appinfo>\\r\\n          </xs:annotation>\\r\\n          <xs:complexType>\\r\\n    \
        <xs:sequence>\\r\\n              <xs:annotation>\\r\\n                <xs:appinfo>\\r\\n                  <b:gr\
oupInfo sequence_number=\\"0\\" />\\r\\n                </xs:appinfo>\\r\\n              </xs:annotation>\\r\\n        \
      <xs:element name=\\"Header\\">\\r\\n                <xs:annotation>\\r\\n                  <xs:appinfo>\\r\\n    \
                <b:recordInfo sequence_number=\\"1\\" structure=\\"delimited\\" preserve_delimiter_for_empty_data=\\"tr\
ue\\" suppress_trailing_delimiters=\\"false\\" child_delimiter_type=\\"char\\" child_delimiter=\\"|\\" child_order=\\"i\
nfix\\" tag_name=\\"HDR|\\" />\\r\\n                  </xs:appinfo>\\r\\n                </xs:annotation>\\r\\n        \
        <xs:complexType>\\r\\n                  <xs:sequence>\\r\\n                    <xs:annotation>\\r\\n           \
           <xs:appinfo>\\r\\n                        <b:groupInfo sequence_number=\\"0\\" />\\r\\n                     \
 </xs:appinfo>\\r\\n                    </xs:annotation>\\r\\n                    <xs:element name=\\"PODate\\" type=\\\
"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n                        <xs:appinfo>\\r\\n              \
            <b:fieldInfo sequence_number=\\"1\\" justification=\\"left\\" />\\r\\n                        </xs:appinfo>\
\\r\\n                      </xs:annotation>\\r\\n                    </xs:element>\\r\\n                    <xs:elemen\
t name=\\"PONumber\\" type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n                        <xs\
:appinfo>\\r\\n                          <b:fieldInfo justification=\\"left\\" sequence_number=\\"2\\" />\\r\\n        \
                </xs:appinfo>\\r\\n                      </xs:annotation>\\r\\n                    </xs:element>\\r\\n \
                   <xs:element name=\\"CustomerID\\" type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\\
r\\n                        <xs:appinfo>\\r\\n                          <b:fieldInfo sequence_number=\\"3\\" justificat\
ion=\\"left\\" />\\r\\n                        </xs:appinfo>\\r\\n                      </xs:annotation>\\r\\n         \
           </xs:element>\\r\\n                    <xs:element name=\\"CustomerContactName\\" type=\\"xs:string\\">\\r\\\
n                      <xs:annotation>\\r\\n                        <xs:appinfo>\\r\\n                          <b:fiel\
dInfo sequence_number=\\"4\\" justification=\\"left\\" />\\r\\n                        </xs:appinfo>\\r\\n             \
         </xs:annotation>\\r\\n                    </xs:element>\\r\\n                    <xs:element name=\\"CustomerC\
ontactPhone\\" type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n                        <xs:appinf\
o>\\r\\n                          <b:fieldInfo sequence_number=\\"5\\" justification=\\"left\\" />\\r\\n               \
         </xs:appinfo>\\r\\n                      </xs:annotation>\\r\\n                    </xs:element>\\r\\n        \
          </xs:sequence>\\r\\n                </xs:complexType>\\r\\n              </xs:element>\\r\\n              <xs\
:element minOccurs=\\"1\\" maxOccurs=\\"unbounded\\" name=\\"LineItems\\">\\r\\n                <xs:annotation>\\r\\n  \
                <xs:appinfo>\\r\\n                    <b:recordInfo sequence_number=\\"2\\" structure=\\"delimited\\" p\
reserve_delimiter_for_empty_data=\\"true\\" suppress_trailing_delimiters=\\"false\\" child_delimiter_type=\\"char\\" ch\
ild_delimiter=\\"|\\" child_order=\\"infix\\" tag_name=\\"DTL|\\" />\\r\\n                  </xs:appinfo>\\r\\n        \
        </xs:annotation>\\r\\n                <xs:complexType>\\r\\n                  <xs:sequence>\\r\\n              \
      <xs:annotation>\\r\\n                      <xs:appinfo>\\r\\n                        <b:groupInfo sequence_number\
=\\"0\\" />\\r\\n                      </xs:appinfo>\\r\\n                    </xs:annotation>\\r\\n                   \
 <xs:element name=\\"PONumber\\" type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n                \
        <xs:appinfo>\\r\\n                          <b:fieldInfo sequence_number=\\"1\\" justification=\\"left\\" />\\r\
\\n                        </xs:appinfo>\\r\\n                      </xs:annotation>\\r\\n                    </xs:elem\
ent>\\r\\n                    <xs:element name=\\"ItemOrdered\\" type=\\"xs:string\\">\\r\\n                      <xs:a\
nnotation>\\r\\n                        <xs:appinfo>\\r\\n                          <b:fieldInfo sequence_number=\\"2\\\
" justification=\\"left\\" />\\r\\n                        </xs:appinfo>\\r\\n                      </xs:annotation>\\r\
\\n                    </xs:element>\\r\\n                    <xs:element name=\\"Quantity\\" type=\\"xs:string\\">\\r\
\\n                      <xs:annotation>\\r\\n                        <xs:appinfo>\\r\\n                          <b:fi\
eldInfo sequence_number=\\"3\\" justification=\\"left\\" />\\r\\n                        </xs:appinfo>\\r\\n           \
           </xs:annotation>\\r\\n                    </xs:element>\\r\\n                    <xs:element name=\\"UOM\\" \
type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n                        <xs:appinfo>\\r\\n       \
                   <b:fieldInfo sequence_number=\\"4\\" justification=\\"left\\" />\\r\\n                        </xs:a\
ppinfo>\\r\\n                      </xs:annotation>\\r\\n                    </xs:element>\\r\\n                    <xs\
:element name=\\"Price\\" type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n                       \
 <xs:appinfo>\\r\\n                          <b:fieldInfo sequence_number=\\"5\\" justification=\\"left\\" />\\r\\n    \
                    </xs:appinfo>\\r\\n                      </xs:annotation>\\r\\n                    </xs:element>\\r\
\\n                    <xs:element name=\\"ExtendedPrice\\" type=\\"xs:string\\">\\r\\n                      <xs:annota\
tion>\\r\\n                        <xs:appinfo>\\r\\n                          <b:fieldInfo sequence_number=\\"6\\" jus\
tification=\\"left\\" />\\r\\n                        </xs:appinfo>\\r\\n                      </xs:annotation>\\r\\n  \
                  </xs:element>\\r\\n                    <xs:element name=\\"Description\\" type=\\"xs:string\\">\\r\\n\
                      <xs:annotation>\\r\\n                        <xs:appinfo>\\r\\n                          <b:field\
Info sequence_number=\\"7\\" justification=\\"left\\" />\\r\\n                        </xs:appinfo>\\r\\n              \
        </xs:annotation>\\r\\n                    </xs:element>\\r\\n                  </xs:sequence>\\r\\n            \
    </xs:complexType>\\r\\n              </xs:element>\\r\\n            </xs:sequence>\\r\\n          </xs:complexType>\
\\r\\n        </xs:element>\\r\\n      </xs:sequence>\\r\\n    </xs:complexType>\\r\\n  </xs:element>\\r\\n</xs:schema>\
" --properties-content-type "application/xml" --metadata "{}" --schema-type "Xml" --tags integrationAccountSchemaName=I\
ntegrationAccountSchema8120 --integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup" --\
schema-name "testSchema"
"""

helps['logic integration-account-schema update'] = """
    type: command
    short-summary: Creates or updates an integration account schema.
    examples:
      - name: Create or update schema
        text: |-
               az logic integration-account-schema create --location "westus" --content "<?xml version=\\"1.0\\" encodi\
ng=\\"utf-16\\"?>\\r\\n<xs:schema xmlns:b=\\"http://schemas.microsoft.com/BizTalk/2003\\" xmlns=\\"http://Inbound_EDI.O\
rderFile\\" targetNamespace=\\"http://Inbound_EDI.OrderFile\\" xmlns:xs=\\"http://www.w3.org/2001/XMLSchema\\">\\r\\n  \
<xs:annotation>\\r\\n    <xs:appinfo>\\r\\n      <b:schemaInfo default_pad_char=\\" \\" count_positions_by_byte=\\"fals\
e\\" parser_optimization=\\"speed\\" lookahead_depth=\\"3\\" suppress_empty_nodes=\\"false\\" generate_empty_nodes=\\"t\
rue\\" allow_early_termination=\\"false\\" early_terminate_optional_fields=\\"false\\" allow_message_breakup_of_infix_r\
oot=\\"false\\" compile_parse_tables=\\"false\\" standard=\\"Flat File\\" root_reference=\\"OrderFile\\" />\\r\\n      \
<schemaEditorExtension:schemaInfo namespaceAlias=\\"b\\" extensionClass=\\"Microsoft.BizTalk.FlatFileExtension.FlatFile\
Extension\\" standardName=\\"Flat File\\" xmlns:schemaEditorExtension=\\"http://schemas.microsoft.com/BizTalk/2003/Sche\
maEditorExtensions\\" />\\r\\n    </xs:appinfo>\\r\\n  </xs:annotation>\\r\\n  <xs:element name=\\"OrderFile\\">\\r\\n \
   <xs:annotation>\\r\\n      <xs:appinfo>\\r\\n        <b:recordInfo structure=\\"delimited\\" preserve_delimiter_for_\
empty_data=\\"true\\" suppress_trailing_delimiters=\\"false\\" sequence_number=\\"1\\" />\\r\\n      </xs:appinfo>\\r\\\
n    </xs:annotation>\\r\\n    <xs:complexType>\\r\\n      <xs:sequence>\\r\\n        <xs:annotation>\\r\\n          <x\
s:appinfo>\\r\\n            <b:groupInfo sequence_number=\\"0\\" />\\r\\n          </xs:appinfo>\\r\\n        </xs:anno\
tation>\\r\\n        <xs:element name=\\"Order\\">\\r\\n          <xs:annotation>\\r\\n            <xs:appinfo>\\r\\n  \
            <b:recordInfo sequence_number=\\"1\\" structure=\\"delimited\\" preserve_delimiter_for_empty_data=\\"true\\\
" suppress_trailing_delimiters=\\"false\\" child_delimiter_type=\\"hex\\" child_delimiter=\\"0x0D 0x0A\\" child_order=\
\\"infix\\" />\\r\\n            </xs:appinfo>\\r\\n          </xs:annotation>\\r\\n          <xs:complexType>\\r\\n    \
        <xs:sequence>\\r\\n              <xs:annotation>\\r\\n                <xs:appinfo>\\r\\n                  <b:gr\
oupInfo sequence_number=\\"0\\" />\\r\\n                </xs:appinfo>\\r\\n              </xs:annotation>\\r\\n        \
      <xs:element name=\\"Header\\">\\r\\n                <xs:annotation>\\r\\n                  <xs:appinfo>\\r\\n    \
                <b:recordInfo sequence_number=\\"1\\" structure=\\"delimited\\" preserve_delimiter_for_empty_data=\\"tr\
ue\\" suppress_trailing_delimiters=\\"false\\" child_delimiter_type=\\"char\\" child_delimiter=\\"|\\" child_order=\\"i\
nfix\\" tag_name=\\"HDR|\\" />\\r\\n                  </xs:appinfo>\\r\\n                </xs:annotation>\\r\\n        \
        <xs:complexType>\\r\\n                  <xs:sequence>\\r\\n                    <xs:annotation>\\r\\n           \
           <xs:appinfo>\\r\\n                        <b:groupInfo sequence_number=\\"0\\" />\\r\\n                     \
 </xs:appinfo>\\r\\n                    </xs:annotation>\\r\\n                    <xs:element name=\\"PODate\\" type=\\\
"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n                        <xs:appinfo>\\r\\n              \
            <b:fieldInfo sequence_number=\\"1\\" justification=\\"left\\" />\\r\\n                        </xs:appinfo>\
\\r\\n                      </xs:annotation>\\r\\n                    </xs:element>\\r\\n                    <xs:elemen\
t name=\\"PONumber\\" type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n                        <xs\
:appinfo>\\r\\n                          <b:fieldInfo justification=\\"left\\" sequence_number=\\"2\\" />\\r\\n        \
                </xs:appinfo>\\r\\n                      </xs:annotation>\\r\\n                    </xs:element>\\r\\n \
                   <xs:element name=\\"CustomerID\\" type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\\
r\\n                        <xs:appinfo>\\r\\n                          <b:fieldInfo sequence_number=\\"3\\" justificat\
ion=\\"left\\" />\\r\\n                        </xs:appinfo>\\r\\n                      </xs:annotation>\\r\\n         \
           </xs:element>\\r\\n                    <xs:element name=\\"CustomerContactName\\" type=\\"xs:string\\">\\r\\\
n                      <xs:annotation>\\r\\n                        <xs:appinfo>\\r\\n                          <b:fiel\
dInfo sequence_number=\\"4\\" justification=\\"left\\" />\\r\\n                        </xs:appinfo>\\r\\n             \
         </xs:annotation>\\r\\n                    </xs:element>\\r\\n                    <xs:element name=\\"CustomerC\
ontactPhone\\" type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n                        <xs:appinf\
o>\\r\\n                          <b:fieldInfo sequence_number=\\"5\\" justification=\\"left\\" />\\r\\n               \
         </xs:appinfo>\\r\\n                      </xs:annotation>\\r\\n                    </xs:element>\\r\\n        \
          </xs:sequence>\\r\\n                </xs:complexType>\\r\\n              </xs:element>\\r\\n              <xs\
:element minOccurs=\\"1\\" maxOccurs=\\"unbounded\\" name=\\"LineItems\\">\\r\\n                <xs:annotation>\\r\\n  \
                <xs:appinfo>\\r\\n                    <b:recordInfo sequence_number=\\"2\\" structure=\\"delimited\\" p\
reserve_delimiter_for_empty_data=\\"true\\" suppress_trailing_delimiters=\\"false\\" child_delimiter_type=\\"char\\" ch\
ild_delimiter=\\"|\\" child_order=\\"infix\\" tag_name=\\"DTL|\\" />\\r\\n                  </xs:appinfo>\\r\\n        \
        </xs:annotation>\\r\\n                <xs:complexType>\\r\\n                  <xs:sequence>\\r\\n              \
      <xs:annotation>\\r\\n                      <xs:appinfo>\\r\\n                        <b:groupInfo sequence_number\
=\\"0\\" />\\r\\n                      </xs:appinfo>\\r\\n                    </xs:annotation>\\r\\n                   \
 <xs:element name=\\"PONumber\\" type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n                \
        <xs:appinfo>\\r\\n                          <b:fieldInfo sequence_number=\\"1\\" justification=\\"left\\" />\\r\
\\n                        </xs:appinfo>\\r\\n                      </xs:annotation>\\r\\n                    </xs:elem\
ent>\\r\\n                    <xs:element name=\\"ItemOrdered\\" type=\\"xs:string\\">\\r\\n                      <xs:a\
nnotation>\\r\\n                        <xs:appinfo>\\r\\n                          <b:fieldInfo sequence_number=\\"2\\\
" justification=\\"left\\" />\\r\\n                        </xs:appinfo>\\r\\n                      </xs:annotation>\\r\
\\n                    </xs:element>\\r\\n                    <xs:element name=\\"Quantity\\" type=\\"xs:string\\">\\r\
\\n                      <xs:annotation>\\r\\n                        <xs:appinfo>\\r\\n                          <b:fi\
eldInfo sequence_number=\\"3\\" justification=\\"left\\" />\\r\\n                        </xs:appinfo>\\r\\n           \
           </xs:annotation>\\r\\n                    </xs:element>\\r\\n                    <xs:element name=\\"UOM\\" \
type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n                        <xs:appinfo>\\r\\n       \
                   <b:fieldInfo sequence_number=\\"4\\" justification=\\"left\\" />\\r\\n                        </xs:a\
ppinfo>\\r\\n                      </xs:annotation>\\r\\n                    </xs:element>\\r\\n                    <xs\
:element name=\\"Price\\" type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n                       \
 <xs:appinfo>\\r\\n                          <b:fieldInfo sequence_number=\\"5\\" justification=\\"left\\" />\\r\\n    \
                    </xs:appinfo>\\r\\n                      </xs:annotation>\\r\\n                    </xs:element>\\r\
\\n                    <xs:element name=\\"ExtendedPrice\\" type=\\"xs:string\\">\\r\\n                      <xs:annota\
tion>\\r\\n                        <xs:appinfo>\\r\\n                          <b:fieldInfo sequence_number=\\"6\\" jus\
tification=\\"left\\" />\\r\\n                        </xs:appinfo>\\r\\n                      </xs:annotation>\\r\\n  \
                  </xs:element>\\r\\n                    <xs:element name=\\"Description\\" type=\\"xs:string\\">\\r\\n\
                      <xs:annotation>\\r\\n                        <xs:appinfo>\\r\\n                          <b:field\
Info sequence_number=\\"7\\" justification=\\"left\\" />\\r\\n                        </xs:appinfo>\\r\\n              \
        </xs:annotation>\\r\\n                    </xs:element>\\r\\n                  </xs:sequence>\\r\\n            \
    </xs:complexType>\\r\\n              </xs:element>\\r\\n            </xs:sequence>\\r\\n          </xs:complexType>\
\\r\\n        </xs:element>\\r\\n      </xs:sequence>\\r\\n    </xs:complexType>\\r\\n  </xs:element>\\r\\n</xs:schema>\
" --properties-content-type "application/xml" --metadata "{}" --schema-type "Xml" --tags integrationAccountSchemaName=I\
ntegrationAccountSchema8120 --integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup" --\
schema-name "testSchema"
"""

helps['logic integration-account-schema delete'] = """
    type: command
    short-summary: Deletes an integration account schema.
    examples:
      - name: Delete a schema by name
        text: |-
               az logic integration-account-schema delete --integration-account-name "testIntegrationAccount" --resourc\
e-group "testResourceGroup" --schema-name "testSchema"
"""

helps['logic integration-account-schema list-content-callback-url'] = """
    type: command
    short-summary: Get the content callback url.
    examples:
      - name: Get the content callback url
        text: |-
               az logic integration-account-schema list-content-callback-url --integration-account-name "testIntegratio\
nAccount" --key-type "Primary" --not-after "2018-04-19T16:00:00Z" --resource-group "testResourceGroup" --schema-name "t\
estSchema"
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
               az logic integration-account-map list --integration-account-name "testIntegrationAccount" --resource-gro\
up "testResourceGroup"
"""

helps['logic integration-account-map show'] = """
    type: command
    short-summary: Gets an integration account map.
    examples:
      - name: Get map by name
        text: |-
               az logic integration-account-map show --integration-account-name "testIntegrationAccount" --map-name "te\
stMap" --resource-group "testResourceGroup"
"""

helps['logic integration-account-map create'] = """
    type: command
    short-summary: Creates or updates an integration account map.
    examples:
      - name: Create or update a map
        text: |-
               az logic integration-account-map create --integration-account-name "testIntegrationAccount" --location "\
westus" --content "<?xml version=\\"1.0\\" encoding=\\"UTF-16\\"?>\\r\\n<xsl:stylesheet xmlns:xsl=\\"http://www.w3.org/\
1999/XSL/Transform\\" xmlns:msxsl=\\"urn:schemas-microsoft-com:xslt\\" xmlns:var=\\"http://schemas.microsoft.com/BizTal\
k/2003/var\\" exclude-result-prefixes=\\"msxsl var s0 userCSharp\\" version=\\"1.0\\" xmlns:ns0=\\"http://BizTalk_Serve\
r_Project4.StringFunctoidsDestinationSchema\\" xmlns:s0=\\"http://BizTalk_Server_Project4.StringFunctoidsSourceSchema\\\
" xmlns:userCSharp=\\"http://schemas.microsoft.com/BizTalk/2003/userCSharp\\">\\r\\n  <xsl:import href=\\"http://btsfun\
ctoids.blob.core.windows.net/functoids/functoids.xslt\\" />\\r\\n  <xsl:output omit-xml-declaration=\\"yes\\" method=\\\
"xml\\" version=\\"1.0\\" />\\r\\n  <xsl:template match=\\"/\\">\\r\\n    <xsl:apply-templates select=\\"/s0:Root\\" />\
\\r\\n  </xsl:template>\\r\\n  <xsl:template match=\\"/s0:Root\\">\\r\\n    <xsl:variable name=\\"var:v1\\" select=\\"u\
serCSharp:StringFind(string(StringFindSource/text()) , &quot;SearchString&quot;)\\" />\\r\\n    <xsl:variable name=\\"v\
ar:v2\\" select=\\"userCSharp:StringLeft(string(StringLeftSource/text()) , &quot;2&quot;)\\" />\\r\\n    <xsl:variable \
name=\\"var:v3\\" select=\\"userCSharp:StringRight(string(StringRightSource/text()) , &quot;2&quot;)\\" />\\r\\n    <xs\
l:variable name=\\"var:v4\\" select=\\"userCSharp:StringUpperCase(string(UppercaseSource/text()))\\" />\\r\\n    <xsl:v\
ariable name=\\"var:v5\\" select=\\"userCSharp:StringLowerCase(string(LowercaseSource/text()))\\" />\\r\\n    <xsl:vari\
able name=\\"var:v6\\" select=\\"userCSharp:StringSize(string(SizeSource/text()))\\" />\\r\\n    <xsl:variable name=\\"\
var:v7\\" select=\\"userCSharp:StringSubstring(string(StringExtractSource/text()) , &quot;0&quot; , &quot;2&quot;)\\" /\
>\\r\\n    <xsl:variable name=\\"var:v8\\" select=\\"userCSharp:StringConcat(string(StringConcatSource/text()))\\" />\\\
r\\n    <xsl:variable name=\\"var:v9\\" select=\\"userCSharp:StringTrimLeft(string(StringLeftTrimSource/text()))\\" />\
\\r\\n    <xsl:variable name=\\"var:v10\\" select=\\"userCSharp:StringTrimRight(string(StringRightTrimSource/text()))\\\
" />\\r\\n    <ns0:Root>\\r\\n      <StringFindDestination>\\r\\n        <xsl:value-of select=\\"$var:v1\\" />\\r\\n   \
   </StringFindDestination>\\r\\n      <StringLeftDestination>\\r\\n        <xsl:value-of select=\\"$var:v2\\" />\\r\\n\
      </StringLeftDestination>\\r\\n      <StringRightDestination>\\r\\n        <xsl:value-of select=\\"$var:v3\\" />\\\
r\\n      </StringRightDestination>\\r\\n      <UppercaseDestination>\\r\\n        <xsl:value-of select=\\"$var:v4\\" /\
>\\r\\n      </UppercaseDestination>\\r\\n      <LowercaseDestination>\\r\\n        <xsl:value-of select=\\"$var:v5\\" \
/>\\r\\n      </LowercaseDestination>\\r\\n      <SizeDestination>\\r\\n        <xsl:value-of select=\\"$var:v6\\" />\\\
r\\n      </SizeDestination>\\r\\n      <StringExtractDestination>\\r\\n        <xsl:value-of select=\\"$var:v7\\" />\\\
r\\n      </StringExtractDestination>\\r\\n      <StringConcatDestination>\\r\\n        <xsl:value-of select=\\"$var:v8\
\\" />\\r\\n      </StringConcatDestination>\\r\\n      <StringLeftTrimDestination>\\r\\n        <xsl:value-of select=\
\\"$var:v9\\" />\\r\\n      </StringLeftTrimDestination>\\r\\n      <StringRightTrimDestination>\\r\\n        <xsl:valu\
e-of select=\\"$var:v10\\" />\\r\\n      </StringRightTrimDestination>\\r\\n    </ns0:Root>\\r\\n  </xsl:template>\\r\\\
n</xsl:stylesheet>" --properties-content-type "application/xml" --map-type "Xslt" --metadata "{}" --map-name "testMap" \
--resource-group "testResourceGroup"
"""

helps['logic integration-account-map update'] = """
    type: command
    short-summary: Creates or updates an integration account map.
    examples:
      - name: Create or update a map
        text: |-
               az logic integration-account-map create --integration-account-name "testIntegrationAccount" --location "\
westus" --content "<?xml version=\\"1.0\\" encoding=\\"UTF-16\\"?>\\r\\n<xsl:stylesheet xmlns:xsl=\\"http://www.w3.org/\
1999/XSL/Transform\\" xmlns:msxsl=\\"urn:schemas-microsoft-com:xslt\\" xmlns:var=\\"http://schemas.microsoft.com/BizTal\
k/2003/var\\" exclude-result-prefixes=\\"msxsl var s0 userCSharp\\" version=\\"1.0\\" xmlns:ns0=\\"http://BizTalk_Serve\
r_Project4.StringFunctoidsDestinationSchema\\" xmlns:s0=\\"http://BizTalk_Server_Project4.StringFunctoidsSourceSchema\\\
" xmlns:userCSharp=\\"http://schemas.microsoft.com/BizTalk/2003/userCSharp\\">\\r\\n  <xsl:import href=\\"http://btsfun\
ctoids.blob.core.windows.net/functoids/functoids.xslt\\" />\\r\\n  <xsl:output omit-xml-declaration=\\"yes\\" method=\\\
"xml\\" version=\\"1.0\\" />\\r\\n  <xsl:template match=\\"/\\">\\r\\n    <xsl:apply-templates select=\\"/s0:Root\\" />\
\\r\\n  </xsl:template>\\r\\n  <xsl:template match=\\"/s0:Root\\">\\r\\n    <xsl:variable name=\\"var:v1\\" select=\\"u\
serCSharp:StringFind(string(StringFindSource/text()) , &quot;SearchString&quot;)\\" />\\r\\n    <xsl:variable name=\\"v\
ar:v2\\" select=\\"userCSharp:StringLeft(string(StringLeftSource/text()) , &quot;2&quot;)\\" />\\r\\n    <xsl:variable \
name=\\"var:v3\\" select=\\"userCSharp:StringRight(string(StringRightSource/text()) , &quot;2&quot;)\\" />\\r\\n    <xs\
l:variable name=\\"var:v4\\" select=\\"userCSharp:StringUpperCase(string(UppercaseSource/text()))\\" />\\r\\n    <xsl:v\
ariable name=\\"var:v5\\" select=\\"userCSharp:StringLowerCase(string(LowercaseSource/text()))\\" />\\r\\n    <xsl:vari\
able name=\\"var:v6\\" select=\\"userCSharp:StringSize(string(SizeSource/text()))\\" />\\r\\n    <xsl:variable name=\\"\
var:v7\\" select=\\"userCSharp:StringSubstring(string(StringExtractSource/text()) , &quot;0&quot; , &quot;2&quot;)\\" /\
>\\r\\n    <xsl:variable name=\\"var:v8\\" select=\\"userCSharp:StringConcat(string(StringConcatSource/text()))\\" />\\\
r\\n    <xsl:variable name=\\"var:v9\\" select=\\"userCSharp:StringTrimLeft(string(StringLeftTrimSource/text()))\\" />\
\\r\\n    <xsl:variable name=\\"var:v10\\" select=\\"userCSharp:StringTrimRight(string(StringRightTrimSource/text()))\\\
" />\\r\\n    <ns0:Root>\\r\\n      <StringFindDestination>\\r\\n        <xsl:value-of select=\\"$var:v1\\" />\\r\\n   \
   </StringFindDestination>\\r\\n      <StringLeftDestination>\\r\\n        <xsl:value-of select=\\"$var:v2\\" />\\r\\n\
      </StringLeftDestination>\\r\\n      <StringRightDestination>\\r\\n        <xsl:value-of select=\\"$var:v3\\" />\\\
r\\n      </StringRightDestination>\\r\\n      <UppercaseDestination>\\r\\n        <xsl:value-of select=\\"$var:v4\\" /\
>\\r\\n      </UppercaseDestination>\\r\\n      <LowercaseDestination>\\r\\n        <xsl:value-of select=\\"$var:v5\\" \
/>\\r\\n      </LowercaseDestination>\\r\\n      <SizeDestination>\\r\\n        <xsl:value-of select=\\"$var:v6\\" />\\\
r\\n      </SizeDestination>\\r\\n      <StringExtractDestination>\\r\\n        <xsl:value-of select=\\"$var:v7\\" />\\\
r\\n      </StringExtractDestination>\\r\\n      <StringConcatDestination>\\r\\n        <xsl:value-of select=\\"$var:v8\
\\" />\\r\\n      </StringConcatDestination>\\r\\n      <StringLeftTrimDestination>\\r\\n        <xsl:value-of select=\
\\"$var:v9\\" />\\r\\n      </StringLeftTrimDestination>\\r\\n      <StringRightTrimDestination>\\r\\n        <xsl:valu\
e-of select=\\"$var:v10\\" />\\r\\n      </StringRightTrimDestination>\\r\\n    </ns0:Root>\\r\\n  </xsl:template>\\r\\\
n</xsl:stylesheet>" --properties-content-type "application/xml" --map-type "Xslt" --metadata "{}" --map-name "testMap" \
--resource-group "testResourceGroup"
"""

helps['logic integration-account-map delete'] = """
    type: command
    short-summary: Deletes an integration account map.
    examples:
      - name: Delete a map
        text: |-
               az logic integration-account-map delete --integration-account-name "testIntegrationAccount" --map-name "\
testMap" --resource-group "testResourceGroup"
"""

helps['logic integration-account-map list-content-callback-url'] = """
    type: command
    short-summary: Get the content callback url.
    examples:
      - name: Get the content callback url
        text: |-
               az logic integration-account-map list-content-callback-url --integration-account-name "testIntegrationAc\
count" --key-type "Primary" --not-after "2018-04-19T16:00:00Z" --map-name "testMap" --resource-group "testResourceGroup\
"
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
               az logic integration-account-partner list --integration-account-name "testIntegrationAccount" --resource\
-group "testResourceGroup"
"""

helps['logic integration-account-partner show'] = """
    type: command
    short-summary: Gets an integration account partner.
    examples:
      - name: Get partner by name
        text: |-
               az logic integration-account-partner show --integration-account-name "testIntegrationAccount" --partner-\
name "testPartner" --resource-group "testResourceGroup"
"""

helps['logic integration-account-partner create'] = """
    type: command
    short-summary: Creates or updates an integration account partner.
    examples:
      - name: Create or update a partner
        text: |-
               az logic integration-account-partner create --integration-account-name "testIntegrationAccount" --locati\
on "westus" --content "{\\"b2b\\":{\\"businessIdentities\\":[{\\"qualifier\\":\\"AA\\",\\"value\\":\\"ZZ\\"}]}}" --meta\
data "{}" --partner-type "B2B" --partner-name "testPartner" --resource-group "testResourceGroup"
"""

helps['logic integration-account-partner update'] = """
    type: command
    short-summary: Creates or updates an integration account partner.
    examples:
      - name: Create or update a partner
        text: |-
               az logic integration-account-partner create --integration-account-name "testIntegrationAccount" --locati\
on "westus" --content "{\\"b2b\\":{\\"businessIdentities\\":[{\\"qualifier\\":\\"AA\\",\\"value\\":\\"ZZ\\"}]}}" --meta\
data "{}" --partner-type "B2B" --partner-name "testPartner" --resource-group "testResourceGroup"
"""

helps['logic integration-account-partner delete'] = """
    type: command
    short-summary: Deletes an integration account partner.
    examples:
      - name: Delete a partner
        text: |-
               az logic integration-account-partner delete --integration-account-name "testIntegrationAccount" --partne\
r-name "testPartner" --resource-group "testResourceGroup"
"""

helps['logic integration-account-partner list-content-callback-url'] = """
    type: command
    short-summary: Get the content callback url.
    examples:
      - name: Get the content callback url
        text: |-
               az logic integration-account-partner list-content-callback-url --integration-account-name "testIntegrati\
onAccount" --key-type "Primary" --not-after "2018-04-19T16:00:00Z" --partner-name "testPartner" --resource-group "testR\
esourceGroup"
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
               az logic integration-account-agreement list --integration-account-name "testIntegrationAccount" --resour\
ce-group "testResourceGroup"
"""

helps['logic integration-account-agreement show'] = """
    type: command
    short-summary: Gets an integration account agreement.
    examples:
      - name: Get agreement by name
        text: |-
               az logic integration-account-agreement show --agreement-name "testAgreement" --integration-account-name \
"testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-agreement create'] = """
    type: command
    short-summary: Creates or updates an integration account agreement.
    examples:
      - name: Create or update an agreement
        text: |-
               az logic integration-account-agreement create --location "westus" --agreement-type "AS2" --content "{\\"\
aS2\\":{\\"receiveAgreement\\":{\\"protocolSettings\\":{\\"acknowledgementConnectionSettings\\":{\\"ignoreCertificateNa\
meMismatch\\":true,\\"keepHttpConnectionAlive\\":true,\\"supportHttpStatusCodeContinue\\":true,\\"unfoldHttpHeaders\\":\
true},\\"envelopeSettings\\":{\\"autogenerateFileName\\":true,\\"fileNameTemplate\\":\\"Test\\",\\"messageContentType\\\
":\\"text/plain\\",\\"suspendMessageOnFileNameGenerationError\\":true,\\"transmitFileNameInMimeHeader\\":true},\\"error\
Settings\\":{\\"resendIfMDNNotReceived\\":true,\\"suspendDuplicateMessage\\":true},\\"mdnSettings\\":{\\"dispositionNot\
ificationTo\\":\\"http://tempuri.org\\",\\"mdnText\\":\\"Sample\\",\\"micHashingAlgorithm\\":\\"SHA1\\",\\"needMDN\\":t\
rue,\\"receiptDeliveryUrl\\":\\"http://tempuri.org\\",\\"sendInboundMdnToMessageBox\\":true,\\"sendMDNAsynchronously\\"\
:true,\\"signMDN\\":true,\\"signOutboundMdnIfOptional\\":true},\\"messageConnectionSettings\\":{\\"ignoreCertificateNam\
eMismatch\\":true,\\"keepHttpConnectionAlive\\":true,\\"supportHttpStatusCodeContinue\\":true,\\"unfoldHttpHeaders\\":t\
rue},\\"securitySettings\\":{\\"enableNRRForInboundDecodedMessages\\":true,\\"enableNRRForInboundEncodedMessages\\":tru\
e,\\"enableNRRForInboundMDN\\":true,\\"enableNRRForOutboundDecodedMessages\\":true,\\"enableNRRForOutboundEncodedMessag\
es\\":true,\\"enableNRRForOutboundMDN\\":true,\\"overrideGroupSigningCertificate\\":false},\\"validationSettings\\":{\\\
"checkCertificateRevocationListOnReceive\\":true,\\"checkCertificateRevocationListOnSend\\":true,\\"checkDuplicateMessa\
ge\\":true,\\"compressMessage\\":true,\\"encryptMessage\\":false,\\"encryptionAlgorithm\\":\\"AES128\\",\\"interchangeD\
uplicatesValidityDays\\":100,\\"overrideMessageProperties\\":true,\\"signMessage\\":false}},\\"receiverBusinessIdentity\
\\":{\\"qualifier\\":\\"ZZ\\",\\"value\\":\\"ZZ\\"},\\"senderBusinessIdentity\\":{\\"qualifier\\":\\"AA\\",\\"value\\":\
\\"AA\\"}},\\"sendAgreement\\":{\\"protocolSettings\\":{\\"acknowledgementConnectionSettings\\":{\\"ignoreCertificateNa\
meMismatch\\":true,\\"keepHttpConnectionAlive\\":true,\\"supportHttpStatusCodeContinue\\":true,\\"unfoldHttpHeaders\\":\
true},\\"envelopeSettings\\":{\\"autogenerateFileName\\":true,\\"fileNameTemplate\\":\\"Test\\",\\"messageContentType\\\
":\\"text/plain\\",\\"suspendMessageOnFileNameGenerationError\\":true,\\"transmitFileNameInMimeHeader\\":true},\\"error\
Settings\\":{\\"resendIfMDNNotReceived\\":true,\\"suspendDuplicateMessage\\":true},\\"mdnSettings\\":{\\"dispositionNot\
ificationTo\\":\\"http://tempuri.org\\",\\"mdnText\\":\\"Sample\\",\\"micHashingAlgorithm\\":\\"SHA1\\",\\"needMDN\\":t\
rue,\\"receiptDeliveryUrl\\":\\"http://tempuri.org\\",\\"sendInboundMdnToMessageBox\\":true,\\"sendMDNAsynchronously\\"\
:true,\\"signMDN\\":true,\\"signOutboundMdnIfOptional\\":true},\\"messageConnectionSettings\\":{\\"ignoreCertificateNam\
eMismatch\\":true,\\"keepHttpConnectionAlive\\":true,\\"supportHttpStatusCodeContinue\\":true,\\"unfoldHttpHeaders\\":t\
rue},\\"securitySettings\\":{\\"enableNRRForInboundDecodedMessages\\":true,\\"enableNRRForInboundEncodedMessages\\":tru\
e,\\"enableNRRForInboundMDN\\":true,\\"enableNRRForOutboundDecodedMessages\\":true,\\"enableNRRForOutboundEncodedMessag\
es\\":true,\\"enableNRRForOutboundMDN\\":true,\\"overrideGroupSigningCertificate\\":false},\\"validationSettings\\":{\\\
"checkCertificateRevocationListOnReceive\\":true,\\"checkCertificateRevocationListOnSend\\":true,\\"checkDuplicateMessa\
ge\\":true,\\"compressMessage\\":true,\\"encryptMessage\\":false,\\"encryptionAlgorithm\\":\\"AES128\\",\\"interchangeD\
uplicatesValidityDays\\":100,\\"overrideMessageProperties\\":true,\\"signMessage\\":false}},\\"receiverBusinessIdentity\
\\":{\\"qualifier\\":\\"AA\\",\\"value\\":\\"AA\\"},\\"senderBusinessIdentity\\":{\\"qualifier\\":\\"ZZ\\",\\"value\\":\
\\"ZZ\\"}}}}" --guest-identity qualifier=AA value=AA --guest-partner "GuestPartner" --host-identity qualifier=ZZ value=\
ZZ --host-partner "HostPartner" --metadata "{}" --tags IntegrationAccountAgreement=<IntegrationAccountAgreementName> --\
agreement-name "testAgreement" --integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-agreement update'] = """
    type: command
    short-summary: Creates or updates an integration account agreement.
    examples:
      - name: Create or update an agreement
        text: |-
               az logic integration-account-agreement create --location "westus" --agreement-type "AS2" --content "{\\"\
aS2\\":{\\"receiveAgreement\\":{\\"protocolSettings\\":{\\"acknowledgementConnectionSettings\\":{\\"ignoreCertificateNa\
meMismatch\\":true,\\"keepHttpConnectionAlive\\":true,\\"supportHttpStatusCodeContinue\\":true,\\"unfoldHttpHeaders\\":\
true},\\"envelopeSettings\\":{\\"autogenerateFileName\\":true,\\"fileNameTemplate\\":\\"Test\\",\\"messageContentType\\\
":\\"text/plain\\",\\"suspendMessageOnFileNameGenerationError\\":true,\\"transmitFileNameInMimeHeader\\":true},\\"error\
Settings\\":{\\"resendIfMDNNotReceived\\":true,\\"suspendDuplicateMessage\\":true},\\"mdnSettings\\":{\\"dispositionNot\
ificationTo\\":\\"http://tempuri.org\\",\\"mdnText\\":\\"Sample\\",\\"micHashingAlgorithm\\":\\"SHA1\\",\\"needMDN\\":t\
rue,\\"receiptDeliveryUrl\\":\\"http://tempuri.org\\",\\"sendInboundMdnToMessageBox\\":true,\\"sendMDNAsynchronously\\"\
:true,\\"signMDN\\":true,\\"signOutboundMdnIfOptional\\":true},\\"messageConnectionSettings\\":{\\"ignoreCertificateNam\
eMismatch\\":true,\\"keepHttpConnectionAlive\\":true,\\"supportHttpStatusCodeContinue\\":true,\\"unfoldHttpHeaders\\":t\
rue},\\"securitySettings\\":{\\"enableNRRForInboundDecodedMessages\\":true,\\"enableNRRForInboundEncodedMessages\\":tru\
e,\\"enableNRRForInboundMDN\\":true,\\"enableNRRForOutboundDecodedMessages\\":true,\\"enableNRRForOutboundEncodedMessag\
es\\":true,\\"enableNRRForOutboundMDN\\":true,\\"overrideGroupSigningCertificate\\":false},\\"validationSettings\\":{\\\
"checkCertificateRevocationListOnReceive\\":true,\\"checkCertificateRevocationListOnSend\\":true,\\"checkDuplicateMessa\
ge\\":true,\\"compressMessage\\":true,\\"encryptMessage\\":false,\\"encryptionAlgorithm\\":\\"AES128\\",\\"interchangeD\
uplicatesValidityDays\\":100,\\"overrideMessageProperties\\":true,\\"signMessage\\":false}},\\"receiverBusinessIdentity\
\\":{\\"qualifier\\":\\"ZZ\\",\\"value\\":\\"ZZ\\"},\\"senderBusinessIdentity\\":{\\"qualifier\\":\\"AA\\",\\"value\\":\
\\"AA\\"}},\\"sendAgreement\\":{\\"protocolSettings\\":{\\"acknowledgementConnectionSettings\\":{\\"ignoreCertificateNa\
meMismatch\\":true,\\"keepHttpConnectionAlive\\":true,\\"supportHttpStatusCodeContinue\\":true,\\"unfoldHttpHeaders\\":\
true},\\"envelopeSettings\\":{\\"autogenerateFileName\\":true,\\"fileNameTemplate\\":\\"Test\\",\\"messageContentType\\\
":\\"text/plain\\",\\"suspendMessageOnFileNameGenerationError\\":true,\\"transmitFileNameInMimeHeader\\":true},\\"error\
Settings\\":{\\"resendIfMDNNotReceived\\":true,\\"suspendDuplicateMessage\\":true},\\"mdnSettings\\":{\\"dispositionNot\
ificationTo\\":\\"http://tempuri.org\\",\\"mdnText\\":\\"Sample\\",\\"micHashingAlgorithm\\":\\"SHA1\\",\\"needMDN\\":t\
rue,\\"receiptDeliveryUrl\\":\\"http://tempuri.org\\",\\"sendInboundMdnToMessageBox\\":true,\\"sendMDNAsynchronously\\"\
:true,\\"signMDN\\":true,\\"signOutboundMdnIfOptional\\":true},\\"messageConnectionSettings\\":{\\"ignoreCertificateNam\
eMismatch\\":true,\\"keepHttpConnectionAlive\\":true,\\"supportHttpStatusCodeContinue\\":true,\\"unfoldHttpHeaders\\":t\
rue},\\"securitySettings\\":{\\"enableNRRForInboundDecodedMessages\\":true,\\"enableNRRForInboundEncodedMessages\\":tru\
e,\\"enableNRRForInboundMDN\\":true,\\"enableNRRForOutboundDecodedMessages\\":true,\\"enableNRRForOutboundEncodedMessag\
es\\":true,\\"enableNRRForOutboundMDN\\":true,\\"overrideGroupSigningCertificate\\":false},\\"validationSettings\\":{\\\
"checkCertificateRevocationListOnReceive\\":true,\\"checkCertificateRevocationListOnSend\\":true,\\"checkDuplicateMessa\
ge\\":true,\\"compressMessage\\":true,\\"encryptMessage\\":false,\\"encryptionAlgorithm\\":\\"AES128\\",\\"interchangeD\
uplicatesValidityDays\\":100,\\"overrideMessageProperties\\":true,\\"signMessage\\":false}},\\"receiverBusinessIdentity\
\\":{\\"qualifier\\":\\"AA\\",\\"value\\":\\"AA\\"},\\"senderBusinessIdentity\\":{\\"qualifier\\":\\"ZZ\\",\\"value\\":\
\\"ZZ\\"}}}}" --guest-identity qualifier=AA value=AA --guest-partner "GuestPartner" --host-identity qualifier=ZZ value=\
ZZ --host-partner "HostPartner" --metadata "{}" --tags IntegrationAccountAgreement=<IntegrationAccountAgreementName> --\
agreement-name "testAgreement" --integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-agreement delete'] = """
    type: command
    short-summary: Deletes an integration account agreement.
    examples:
      - name: Delete an agreement
        text: |-
               az logic integration-account-agreement delete --agreement-name "testAgreement" --integration-account-nam\
e "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-agreement list-content-callback-url'] = """
    type: command
    short-summary: Get the content callback url.
    examples:
      - name: Get the content callback url
        text: |-
               az logic integration-account-agreement list-content-callback-url --agreement-name "testAgreement" --inte\
gration-account-name "testIntegrationAccount" --key-type "Primary" --not-after "2018-04-19T16:00:00Z" --resource-group \
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
               az logic integration-account-certificate list --integration-account-name "testIntegrationAccount" --reso\
urce-group "testResourceGroup"
"""

helps['logic integration-account-certificate show'] = """
    type: command
    short-summary: Gets an integration account certificate.
    examples:
      - name: Get certificate by name
        text: |-
               az logic integration-account-certificate show --certificate-name "testCertificate" --integration-account\
-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-certificate create'] = """
    type: command
    short-summary: Creates or updates an integration account certificate.
    examples:
      - name: Create or update a certificate
        text: |-
               az logic integration-account-certificate create --location "brazilsouth" --key "{\\"keyName\\":\\"<keyNa\
me>\\",\\"keyVault\\":{\\"id\\":\\"/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourcegroups/testResourceGroup\
/providers/microsoft.keyvault/vaults/<keyVaultName>\\"},\\"keyVersion\\":\\"87d9764197604449b9b8eb7bd8710868\\"}" --pub\
lic-certificate "<publicCertificateValue>" --certificate-name "testCertificate" --integration-account-name "testIntegra\
tionAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-certificate update'] = """
    type: command
    short-summary: Creates or updates an integration account certificate.
    examples:
      - name: Create or update a certificate
        text: |-
               az logic integration-account-certificate create --location "brazilsouth" --key "{\\"keyName\\":\\"<keyNa\
me>\\",\\"keyVault\\":{\\"id\\":\\"/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourcegroups/testResourceGroup\
/providers/microsoft.keyvault/vaults/<keyVaultName>\\"},\\"keyVersion\\":\\"87d9764197604449b9b8eb7bd8710868\\"}" --pub\
lic-certificate "<publicCertificateValue>" --certificate-name "testCertificate" --integration-account-name "testIntegra\
tionAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account-certificate delete'] = """
    type: command
    short-summary: Deletes an integration account certificate.
    examples:
      - name: Delete a certificate
        text: |-
               az logic integration-account-certificate delete --certificate-name "testCertificate" --integration-accou\
nt-name "testIntegrationAccount" --resource-group "testResourceGroup"
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
               az logic integration-account-session list --integration-account-name "testia123" --resource-group "testr\
g123"
"""

helps['logic integration-account-session show'] = """
    type: command
    short-summary: Gets an integration account session.
    examples:
      - name: Get integration account session examples
        text: |-
               az logic integration-account-session show --integration-account-name "testia123" --resource-group "testr\
g123" --session-name "testsession123-ICN"
"""

helps['logic integration-account-session create'] = """
    type: command
    short-summary: Creates or updates an integration account session.
    examples:
      - name: Create or update integration account session example
        text: |-
               az logic integration-account-session create --integration-account-name "testia123" --resource-group "tes\
trg123" --content "{\\"controlNumber\\":\\"1234\\",\\"controlNumberChangedTime\\":\\"2017-02-21T22:30:11.9923759Z\\"}" \
--session-name "testsession123-ICN"
"""

helps['logic integration-account-session update'] = """
    type: command
    short-summary: Creates or updates an integration account session.
    examples:
      - name: Create or update integration account session example
        text: |-
               az logic integration-account-session create --integration-account-name "testia123" --resource-group "tes\
trg123" --content "{\\"controlNumber\\":\\"1234\\",\\"controlNumberChangedTime\\":\\"2017-02-21T22:30:11.9923759Z\\"}" \
--session-name "testsession123-ICN"
"""

helps['logic integration-account-session delete'] = """
    type: command
    short-summary: Deletes an integration account session.
    examples:
      - name: Delete integration account session examples
        text: |-
               az logic integration-account-session delete --integration-account-name "testia123" --resource-group "tes\
trg123" --session-name "testsession123-ICN"
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
               az logic integration-service-environment show --integration-service-environment-name "testIntegrationSer\
viceEnvironment" --resource-group "testResourceGroup"
"""

helps['logic integration-service-environment create'] = """
    type: command
    short-summary: Creates or updates an integration service environment.
    examples:
      - name: Create or update an integration service environment
        text: |-
               az logic integration-service-environment create --location "brazilsouth" --properties "{\\"networkConfig\
uration\\":{\\"accessEndpoint\\":{\\"type\\":\\"Internal\\"},\\"subnets\\":[{\\"id\\":\\"/subscriptions/f34b22a3-2202-4\
fb1-b040-1332bd928c84/resourceGroups/testResourceGroup/providers/Microsoft.Network/virtualNetworks/testVNET/subnets/s1\
\\"},{\\"id\\":\\"/subscriptions/f34b22a3-2202-4fb1-b040-1332bd928c84/resourceGroups/testResourceGroup/providers/Micros\
oft.Network/virtualNetworks/testVNET/subnets/s2\\"},{\\"id\\":\\"/subscriptions/f34b22a3-2202-4fb1-b040-1332bd928c84/re\
sourceGroups/testResourceGroup/providers/Microsoft.Network/virtualNetworks/testVNET/subnets/s3\\"},{\\"id\\":\\"/subscr\
iptions/f34b22a3-2202-4fb1-b040-1332bd928c84/resourceGroups/testResourceGroup/providers/Microsoft.Network/virtualNetwor\
ks/testVNET/subnets/s4\\"}]}}" --sku name=Premium capacity=2 --integration-service-environment-name "testIntegrationSer\
viceEnvironment" --resource-group "testResourceGroup"
"""

helps['logic integration-service-environment update'] = """
    type: command
    short-summary: Updates an integration service environment.
    examples:
      - name: Patch an integration service environment
        text: |-
               az logic integration-service-environment update --sku name=Developer capacity=0 --tags tag1=value1 --int\
egration-service-environment-name "testIntegrationServiceEnvironment" --resource-group "testResourceGroup"
"""

helps['logic integration-service-environment delete'] = """
    type: command
    short-summary: Deletes an integration service environment.
    examples:
      - name: Delete an integration account
        text: |-
               az logic integration-service-environment delete --integration-service-environment-name "testIntegrationS\
erviceEnvironment" --resource-group "testResourceGroup"
"""

helps['logic integration-service-environment restart'] = """
    type: command
    short-summary: Restarts an integration service environment.
    examples:
      - name: Restarts an integration service environment
        text: |-
               az logic integration-service-environment restart --integration-service-environment-name "testIntegration\
ServiceEnvironment" --resource-group "testResourceGroup"
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
               az logic integration-service-environment-sku list --integration-service-environment-name "testIntegratio\
nServiceEnvironment" --resource-group "testResourceGroup"
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
               az logic integration-service-environment-network-health show --integration-service-environment-name "tes\
tIntegrationServiceEnvironment" --resource-group "testResourceGroup"
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
               az logic integration-service-environment-managed-api list --integration-service-environment-name "testIn\
tegrationServiceEnvironment" --resource-group "testResourceGroup"
"""

helps['logic integration-service-environment-managed-api show'] = """
    type: command
    short-summary: Gets the integration service environment managed Api.
    examples:
      - name: Gets the integration service environment managed Apis
        text: |-
               az logic integration-service-environment-managed-api show --api-name "servicebus" --integration-service-\
environment-name "testIntegrationServiceEnvironment" --resource-group "testResourceGroup"
"""

helps['logic integration-service-environment-managed-api delete'] = """
    type: command
    short-summary: Deletes the integration service environment managed Api.
    examples:
      - name: Deletes the integration service environment managed Apis
        text: |-
               az logic integration-service-environment-managed-api delete --api-name "servicebus" --integration-servic\
e-environment-name "testIntegrationServiceEnvironment" --resource-group "testResourceGroup"
"""

helps['logic integration-service-environment-managed-api put'] = """
    type: command
    short-summary: Puts the integration service environment managed Api.
    examples:
      - name: Gets the integration service environment managed Apis
        text: |-
               az logic integration-service-environment-managed-api put --api-name "servicebus" --integration-service-e\
nvironment-name "testIntegrationServiceEnvironment" --resource-group "testResourceGroup"
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
               az logic integration-service-environment-managed-api-operation list --api-name "servicebus" --integratio\
n-service-environment-name "testIntegrationServiceEnvironment" --resource-group "testResourceGroup"
"""
