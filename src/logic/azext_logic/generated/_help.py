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
               az logic workflow list --resource-group "test-resource-group"
"""

helps['logic workflow show'] = """
    type: command
    short-summary: Gets a workflow.
    examples:
      - name: Get a workflow
        text: |-
               az logic workflow show --resource-group "test-resource-group" --workflow-name
               "test-workflow"
"""

helps['logic workflow create'] = """
    type: command
    short-summary: Creates or updates a workflow.
    examples:
      - name: Create or update a workflow
        text: |-
               az logic workflow create --resource-group "test-resource-group" --location "brazilsouth"
               --properties-definition $schema=https://schema.management.azure.com/providers/Microsoft.Lo\\
               gic/schemas/2016-06-01/workflowdefinition.json# actions=[object Object] contentVersion=1.0\\
               .0.0 outputs=[object Object] parameters=[object Object] triggers=[object Object]
               --properties-integration-account id=/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/re\\
               sourceGroups/test-resource-group/providers/Microsoft.Logic/integrationAccounts/test-integr\\
               ation-account --properties-parameters "{\\"$connections\\":{\\"value\\":{\\"test-custom-connect
               or\\":{\\"connectionId\\":\\"/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourceGroup
               s/test-resource-group/providers/Microsoft.Web/connections/test-custom-connector\\",\\"connec
               tionName\\":\\"test-custom-connector\\",\\"id\\":\\"/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a
               69ab345/providers/Microsoft.Web/locations/brazilsouth/managedApis/test-custom-connector\\"}
               }}}" --workflow-name "test-workflow"
"""

helps['logic workflow update'] = """
    type: command
    short-summary: Updates a workflow.
    examples:
      - name: Patch a workflow
        text: |-
               az logic workflow update --resource-group "test-resource-group" --location "brazilsouth"
               --properties-definition $schema=https://schema.management.azure.com/providers/Microsoft.Lo\\
               gic/schemas/2016-06-01/workflowdefinition.json# actions=[object Object] contentVersion=1.0\\
               .0.0 outputs=[object Object] parameters=[object Object] triggers=[object Object]
               --properties-integration-account id=/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/re\\
               sourceGroups/test-resource-group/providers/Microsoft.Logic/integrationAccounts/test-integr\\
               ation-account --properties-parameters "{\\"$connections\\":{\\"value\\":{\\"test-custom-connect
               or\\":{\\"connectionId\\":\\"/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourceGroup
               s/test-resource-group/providers/Microsoft.Web/connections/test-custom-connector\\",\\"connec
               tionName\\":\\"test-custom-connector\\",\\"id\\":\\"/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a
               69ab345/providers/Microsoft.Web/locations/brazilsouth/managedApis/test-custom-connector\\"}
               }}}" --workflow-name "test-workflow"
"""

helps['logic workflow delete'] = """
    type: command
    short-summary: Deletes a workflow.
    examples:
      - name: Delete a workflow
        text: |-
               az logic workflow delete --resource-group "test-resource-group" --workflow-name
               "test-workflow"
"""

helps['logic workflow move'] = """
    type: command
    short-summary: Moves an existing workflow.
    examples:
      - name: Move a workflow
        text: |-
               az logic workflow move --resource-group "testResourceGroup" --workflow-name
               "testWorkflow"
"""

helps['logic workflow validate-by-resource-group'] = """
    type: command
    short-summary: Validates the workflow.
    examples:
      - name: Validate a workflow
        text: |-
               az logic workflow validate-by-resource-group --resource-group "test-resource-group"
               --location "brazilsouth" --properties-definition $schema=https://schema.management.azure.c\\
               om/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json# actions=[object O\\
               bject] contentVersion=1.0.0.0 outputs=[object Object] parameters=[object Object] triggers=\\
               [object Object] --properties-integration-account id=/subscriptions/34adfa4f-cedf-4dc0-ba29\\
               -b6d1a69ab345/resourceGroups/test-resource-group/providers/Microsoft.Logic/integrationAcco\\
               unts/test-integration-account --workflow-name "test-workflow"
"""

helps['logic workflow list-callback-url'] = """
    type: command
    short-summary: Get the workflow callback Url.
    examples:
      - name: Get callback url
        text: |-
               az logic workflow list-callback-url --key-type "Primary" --not-after
               "2018-04-19T16:00:00Z" --resource-group "testResourceGroup" --workflow-name
               "testWorkflow"
"""

helps['logic workflow generate-upgraded-definition'] = """
    type: command
    short-summary: Generates the upgraded definition for a workflow.
    examples:
      - name: Generate an upgraded definition
        text: |-
               az logic workflow generate-upgraded-definition --target-schema-version "2016-06-01"
               --resource-group "test-resource-group" --workflow-name "test-workflow"
"""

helps['logic workflow regenerate-access-key'] = """
    type: command
    short-summary: Regenerates the callback URL access key for request triggers.
    examples:
      - name: Regenerate the callback URL access key for request triggers
        text: |-
               az logic workflow regenerate-access-key --resource-group "testResourceGroup"
               --workflow-name "testWorkflowName"
"""

helps['logic workflow validate-by-location'] = """
    type: command
    short-summary: Validates the workflow definition.
    examples:
      - name: Validate a workflow
        text: |-
               az logic workflow validate-by-location --location "brazilsouth" --resource-group
               "test-resource-group" --workflow-name "test-workflow"
"""

helps['logic workflow disable'] = """
    type: command
    short-summary: Disables a workflow.
    examples:
      - name: Disable a workflow
        text: |-
               az logic workflow disable --resource-group "test-resource-group" --workflow-name
               "test-workflow"
"""

helps['logic workflow enable'] = """
    type: command
    short-summary: Enables a workflow.
    examples:
      - name: Enable a workflow
        text: |-
               az logic workflow enable --resource-group "test-resource-group" --workflow-name
               "test-workflow"
"""

helps['logic workflow list-swagger'] = """
    type: command
    short-summary: Gets an OpenAPI definition for the workflow.
    examples:
      - name: Get the swagger for a workflow
        text: |-
               az logic workflow list-swagger --resource-group "testResourceGroup" --workflow-name
               "testWorkflowName"
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
               az logic integration-account show --integration-account-name "testIntegrationAccount"
               --resource-group "testResourceGroup"
"""

helps['logic integration-account create'] = """
    type: command
    short-summary: Creates or updates an integration account.
    examples:
      - name: Create or update an integration account
        text: |-
               az logic integration-account create --location "westus" --sku name=Standard
               --integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account update'] = """
    type: command
    short-summary: Updates an integration account.
    examples:
      - name: Patch an integration account
        text: |-
               az logic integration-account update --location "westus" --sku name=Standard
               --integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
"""

helps['logic integration-account delete'] = """
    type: command
    short-summary: Deletes an integration account.
    examples:
      - name: Delete an integration account
        text: |-
               az logic integration-account delete --integration-account-name "testIntegrationAccount"
               --resource-group "testResourceGroup"
"""

helps['logic integration-account log-tracking-event'] = """
    type: command
    short-summary: Logs the integration account's tracking events.
    examples:
      - name: Log a tracked event
        text: |-
               az logic integration-account log-tracking-event --integration-account-name
               "testIntegrationAccount" --events "[{\\"error\\":{\\"code\\":\\"NotFound\\",\\"message\\":\\"Some e
               rror occurred\\"},\\"eventLevel\\":\\"Informational\\",\\"eventTime\\":\\"2016-08-05T01:54:49.5055
               67Z\\",\\"record\\":{\\"agreementProperties\\":{\\"agreementName\\":\\"testAgreement\\",\\"as2From\\"
               :\\"testas2from\\",\\"as2To\\":\\"testas2to\\",\\"receiverPartnerName\\":\\"testPartner2\\",\\"sender
               PartnerName\\":\\"testPartner1\\"},\\"messageProperties\\":{\\"IsMessageEncrypted\\":false,\\"IsMe
               ssageSigned\\":false,\\"correlationMessageId\\":\\"Unique message identifier\\",\\"direction\\":\\
               "Receive\\",\\"dispositionType\\":\\"received-success\\",\\"fileName\\":\\"test\\",\\"isMdnExpected\\
               ":true,\\"isMessageCompressed\\":false,\\"isMessageFailed\\":false,\\"isNrrEnabled\\":true,\\"mdn
               Type\\":\\"Async\\",\\"messageId\\":\\"12345\\"}},\\"recordType\\":\\"AS2Message\\"}]" --source-type
               "Microsoft.Logic/workflows" --resource-group "testResourceGroup"
"""

helps['logic integration-account list-callback-url'] = """
    type: command
    short-summary: Gets the integration account callback URL.
    examples:
      - name: List IntegrationAccount callback URL
        text: |-
               az logic integration-account list-callback-url --integration-account-name
               "testIntegrationAccount" --key-type "Primary" --not-after "2017-03-05T08:00:00Z"
               --resource-group "testResourceGroup"
"""

helps['logic integration-account list-key-vault-key'] = """
    type: command
    short-summary: Gets the integration account's Key Vault keys.
    examples:
      - name: Get Integration Account callback URL
        text: |-
               az logic integration-account list-key-vault-key --integration-account-name
               "testIntegrationAccount" --key-vault id=subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345\\
               /resourceGroups/testResourceGroup/providers/Microsoft.KeyVault/vaults/testKeyVault
               --skip-token "testSkipToken" --resource-group "testResourceGroup"
"""

helps['logic integration-account regenerate-access-key'] = """
    type: command
    short-summary: Regenerates the integration account access key.
    examples:
      - name: Regenerate access key
        text: |-
               az logic integration-account regenerate-access-key --integration-account-name
               "testIntegrationAccount" --key-type "Primary" --resource-group "testResourceGroup"
"""
