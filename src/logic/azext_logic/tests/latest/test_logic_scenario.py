# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk import ResourceGroupPreparer


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class LogicManagementClientScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_logic_test-resource-group'[:9], key='rg')
    @ResourceGroupPreparer(name_prefix='cli_test_logic_testResourceGroup'[:9], key='rg_2')
    def test_logic(self, resource_group):

        self.kwargs.update({
            'subscription_id': self.get_subscription_id()
        })

        self.kwargs.update({
            'test-integration-account': 'test-integration-account',
            'IntegrationAccounts_2': self.create_random_name(prefix='cli_test_integration_accounts'[:9], length=24),
            'test-workflow': self.create_random_name(prefix='cli_test_workflows'[:9], length=24),
            'Workflows_2': 'Workflows_2',
            'Workflows_3': 'Workflows_3',
        })

        # EXAMPLE: IntegrationAccounts/resource-group-name/Create or update an integration account
        self.cmd('az logic integration-account create '
                 '--location "westus" '
                 '--sku name=Standard '
                 '--integration-account-name "{IntegrationAccounts_2}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        # EXAMPLE: Workflows/resource-group-name/Create or update a workflow
        self.cmd('az logic workflow create '
                 '--resource-group "{rg}" '
                 '--location "brazilsouth" '
                 '--definition "{{\\"$schema\\":\\"https://schema.management.azure.com/providers/Microsoft.Logic/schema'
                 's/2016-06-01/workflowdefinition.json#\\",\\"actions\\":{{\\"Find_pet_by_ID\\":{{\\"type\\":\\"ApiConn'
                 'ection\\",\\"inputs\\":{{\\"path\\":\\"/pet/@{{encodeURIComponent(\'1\')}}\\",\\"method\\":\\"get\\",'
                 '\\"host\\":{{\\"connection\\":{{\\"name\\":\\"@parameters(\'$connections\')[\'test-custom-connector\''
                 '][\'connectionId\']\\"}}}}}},\\"runAfter\\":{{}}}}}},\\"contentVersion\\":\\"1.0.0.0\\",\\"outputs\\"'
                 ':{{}},\\"parameters\\":{{\\"$connections\\":{{\\"type\\":\\"Object\\",\\"defaultValue\\":{{}}}}}},\\"'
                 'triggers\\":{{\\"manual\\":{{\\"type\\":\\"Request\\",\\"inputs\\":{{\\"schema\\":{{}}}},\\"kind\\":'
                 '\\"Http\\"}}}}}}" '
                 '--integration-account id=/subscriptions/{subscription_id}/resourceGroups/{rg}/providers/Microsoft.Log'
                 'ic/integrationAccounts/{test-integration-account} '
                 '--parameters "{{\\"$connections\\":{{\\"value\\":{{\\"test-custom-connector\\":{{\\"connectionId\\":'
                 '\\"/subscriptions/{subscription_id}/resourceGroups/{rg}/providers/Microsoft.Web/connections/test-cust'
                 'om-connector\\",\\"connectionName\\":\\"test-custom-connector\\",\\"id\\":\\"/subscriptions/{subscrip'
                 'tion_id}/providers/Microsoft.Web/locations/brazilsouth/managedApis/test-custom-connector\\"}}}}}}}}" '
                 ''
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        # EXAMPLE: IntegrationAccounts/resource-group-name/Get integration account by name
        self.cmd('az logic integration-account show '
                 '--integration-account-name "{IntegrationAccounts_2}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        # EXAMPLE: Workflows/resource-group-name/Get a workflow
        self.cmd('az logic workflow show '
                 '--resource-group "{rg}" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        # EXAMPLE: IntegrationAccounts/resource-group-name/List integration accounts by resource group name
        self.cmd('az logic integration-account list '
                 '--resource-group "{rg_2}"',
                 checks=[])

        # EXAMPLE: Workflows/resource-group-name/List all workflows in a resource group
        self.cmd('az logic workflow list '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: IntegrationAccounts/top/List integration accounts by subscription
        self.cmd('az logic integration-account list',
                 checks=[])

        # EXAMPLE: Workflows/top/List all workflows in a subscription
        self.cmd('az logic workflow list',
                 checks=[])

        # EXAMPLE: IntegrationAccounts/resource-group-name/Regenerate access key
        self.cmd('az logic integration-account regenerate-access-key '
                 '--integration-account-name "{IntegrationAccounts_2}" '
                 '--key-type "Primary" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        # EXAMPLE: IntegrationAccounts/resource-group-name/Log a tracked event
        self.cmd('az logic integration-account log-tracking-event '
                 '--integration-account-name "{IntegrationAccounts_2}" '
                 '--events "[{{\\"error\\":{{\\"code\\":\\"NotFound\\",\\"message\\":\\"Some error occurred\\"}},\\"eve'
                 'ntLevel\\":\\"Informational\\",\\"eventTime\\":\\"2016-08-05T01:54:49.505567Z\\",\\"record\\":{{\\"ag'
                 'reementProperties\\":{{\\"agreementName\\":\\"testAgreement\\",\\"as2From\\":\\"testas2from\\",\\"as2'
                 'To\\":\\"testas2to\\",\\"receiverPartnerName\\":\\"testPartner2\\",\\"senderPartnerName\\":\\"testPar'
                 'tner1\\"}},\\"messageProperties\\":{{\\"IsMessageEncrypted\\":false,\\"IsMessageSigned\\":false,\\"co'
                 'rrelationMessageId\\":\\"Unique message identifier\\",\\"direction\\":\\"Receive\\",\\"dispositionTyp'
                 'e\\":\\"received-success\\",\\"fileName\\":\\"test\\",\\"isMdnExpected\\":true,\\"isMessageCompressed'
                 '\\":false,\\"isMessageFailed\\":false,\\"isNrrEnabled\\":true,\\"mdnType\\":\\"Async\\",\\"messageId'
                 '\\":\\"12345\\"}}}},\\"recordType\\":\\"AS2Message\\"}}]" '
                 '--source-type "Microsoft.Logic/workflows" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        # EXAMPLE: IntegrationAccounts/resource-group-name/Get Integration Account callback URL
        self.cmd('az logic integration-account list-key-vault-key '
                 '--integration-account-name "{IntegrationAccounts_2}" '
                 '--key-vault id=subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourceGroups/testResourceGroup/pr'
                 'oviders/Microsoft.KeyVault/vaults/testKeyVault '
                 '--skip-token "testSkipToken" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        # EXAMPLE: IntegrationAccounts/resource-group-name/List IntegrationAccount callback URL
        self.cmd('az logic integration-account list-callback-url '
                 '--integration-account-name "{IntegrationAccounts_2}" '
                 '--key-type "Primary" '
                 '--not-after "2017-03-05T08:00:00Z" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        # EXAMPLE: Workflows/resource-group-name/Validate a workflow
        self.cmd('az logic workflow validate-by-location '
                 '--location "brazilsouth" '
                 '--resource-group "{rg}" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        # EXAMPLE: Workflows/resource-group-name/Validate a workflow
        self.cmd('az logic workflow validate-by-resource-group '
                 '--resource-group "{rg}" '
                 '--location "brazilsouth" '
                 '--definition "{{\\"$schema\\":\\"https://schema.management.azure.com/providers/Microsoft.Logic/schema'
                 's/2016-06-01/workflowdefinition.json#\\",\\"actions\\":{{}},\\"contentVersion\\":\\"1.0.0.0\\",\\"out'
                 'puts\\":{{}},\\"parameters\\":{{}},\\"triggers\\":{{}}}}" '
                 '--integration-account id=/subscriptions/{subscription_id}/resourceGroups/{rg}/providers/Microsoft.Log'
                 'ic/integrationAccounts/{test-integration-account} '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        # EXAMPLE: Workflows/resource-group-name/Generate an upgraded definition
        self.cmd('az logic workflow generate-upgraded-definition '
                 '--target-schema-version "2016-06-01" '
                 '--resource-group "{rg}" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        # EXAMPLE: Workflows/resource-group-name/Regenerate the callback URL access key for request triggers
        self.cmd('az logic workflow regenerate-access-key '
                 '--resource-group "{rg_2}" '
                 '--workflow-name "{Workflows_2}"',
                 checks=[])

        # EXAMPLE: IntegrationAccounts/resource-group-name/Patch an integration account
        self.cmd('az logic integration-account update '
                 '--location "westus" '
                 '--sku name=Standard '
                 '--integration-account-name "{IntegrationAccounts_2}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        # EXAMPLE: Workflows/resource-group-name/Get callback url
        self.cmd('az logic workflow list-callback-url '
                 '--key-type "Primary" '
                 '--not-after "2018-04-19T16:00:00Z" '
                 '--resource-group "{rg_2}" '
                 '--workflow-name "{Workflows_3}"',
                 checks=[])

        # EXAMPLE: Workflows/resource-group-name/Get the swagger for a workflow
        self.cmd('az logic workflow list-swagger '
                 '--resource-group "{rg_2}" '
                 '--workflow-name "{Workflows_2}"',
                 checks=[])

        # EXAMPLE: Workflows/resource-group-name/Validate a workflow
        self.cmd('az logic workflow validate-by-location '
                 '--location "brazilsouth" '
                 '--resource-group "{rg}" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        # EXAMPLE: Workflows/resource-group-name/Validate a workflow
        self.cmd('az logic workflow validate-by-resource-group '
                 '--resource-group "{rg}" '
                 '--location "brazilsouth" '
                 '--definition "{{\\"$schema\\":\\"https://schema.management.azure.com/providers/Microsoft.Logic/schema'
                 's/2016-06-01/workflowdefinition.json#\\",\\"actions\\":{{}},\\"contentVersion\\":\\"1.0.0.0\\",\\"out'
                 'puts\\":{{}},\\"parameters\\":{{}},\\"triggers\\":{{}}}}" '
                 '--integration-account id=/subscriptions/{subscription_id}/resourceGroups/{rg}/providers/Microsoft.Log'
                 'ic/integrationAccounts/{test-integration-account} '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        # EXAMPLE: Workflows/resource-group-name/Disable a workflow
        self.cmd('az logic workflow disable '
                 '--resource-group "{rg}" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        # EXAMPLE: Workflows/resource-group-name/Enable a workflow
        self.cmd('az logic workflow enable '
                 '--resource-group "{rg}" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        # EXAMPLE: Workflows/resource-group-name/Move a workflow
        self.cmd('az logic workflow move '
                 '--resource-group "{rg_2}" '
                 '--workflow-name "{Workflows_3}"',
                 checks=[])

        # EXAMPLE: Workflows/resource-group-name/Patch a workflow
        self.cmd('az logic workflow update '
                 '--resource-group "{rg}" '
                 '--location "brazilsouth" '
                 '--definition "{{\\"$schema\\":\\"https://schema.management.azure.com/providers/Microsoft.Logic/schema'
                 's/2016-06-01/workflowdefinition.json#\\",\\"actions\\":{{\\"Find_pet_by_ID\\":{{\\"type\\":\\"ApiConn'
                 'ection\\",\\"inputs\\":{{\\"path\\":\\"/pet/@{{encodeURIComponent(\'1\')}}\\",\\"method\\":\\"get\\",'
                 '\\"host\\":{{\\"connection\\":{{\\"name\\":\\"@parameters(\'$connections\')[\'test-custom-connector\''
                 '][\'connectionId\']\\"}}}}}},\\"runAfter\\":{{}}}}}},\\"contentVersion\\":\\"1.0.0.0\\",\\"outputs\\"'
                 ':{{}},\\"parameters\\":{{\\"$connections\\":{{\\"type\\":\\"Object\\",\\"defaultValue\\":{{}}}}}},\\"'
                 'triggers\\":{{\\"manual\\":{{\\"type\\":\\"Request\\",\\"inputs\\":{{\\"schema\\":{{}}}},\\"kind\\":'
                 '\\"Http\\"}}}}}}" '
                 '--integration-account id=/subscriptions/{subscription_id}/resourceGroups/{rg}/providers/Microsoft.Log'
                 'ic/integrationAccounts/{test-integration-account} '
                 '--parameters "{{\\"$connections\\":{{\\"value\\":{{\\"test-custom-connector\\":{{\\"connectionId\\":'
                 '\\"/subscriptions/{subscription_id}/resourceGroups/{rg}/providers/Microsoft.Web/connections/test-cust'
                 'om-connector\\",\\"connectionName\\":\\"test-custom-connector\\",\\"id\\":\\"/subscriptions/{subscrip'
                 'tion_id}/providers/Microsoft.Web/locations/brazilsouth/managedApis/test-custom-connector\\"}}}}}}}}" '
                 ''
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        # EXAMPLE: Workflows/resource-group-name/Delete a workflow
        self.cmd('az logic workflow delete '
                 '--resource-group "{rg}" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        # EXAMPLE: IntegrationAccounts/resource-group-name/Delete an integration account
        self.cmd('az logic integration-account delete '
                 '--integration-account-name "{IntegrationAccounts_2}" '
                 '--resource-group "{rg_2}"',
                 checks=[])
