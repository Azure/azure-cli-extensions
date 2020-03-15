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

    @ResourceGroupPreparer(name_prefix='cli_test_logic_test-resource-group', key='rg')
    @ResourceGroupPreparer(name_prefix='cli_test_logic_testResourceGroup', key='rg_2')
    @ResourceGroupPreparer(name_prefix='cli_test_logic_testrg123', key='rg_3')
    def test_logic(self, resource_group):

        self.kwargs.update({
            'test-workflow': self.create_random_name(prefix='workflows', length=24),
            'Workflows_2': self.create_random_name(prefix='workflows', length=24),
            'Workflows_3': self.create_random_name(prefix='workflows', length=24),
            'Workflows_4': self.create_random_name(prefix='workflows', length=24),
            'testIntegrationAccount': self.create_random_name(prefix='integration_accounts', length=24),
            'IntegrationAccounts_2': self.create_random_name(prefix='integration_accounts', length=24),
            'IntegrationAccounts_3': self.create_random_name(prefix='integration_accounts', length=24),
            'testIntegrationServiceEnvironment': self.create_random_name(prefix='integration_service_environments', length=24),
        })

        self.cmd('az logic workflow create '
                 '--resource-group "{rg}" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic integration-account create '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-map create '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--map-name "testMap" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment create '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-schema create '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}" '
                 '--schema-name "testSchema"',
                 checks=[])

        self.cmd('az logic integration-account-session create '
                 '--integration-account-name "{IntegrationAccounts_2}" '
                 '--resource-group "{rg_3}" '
                 '--session-name "testsession123-ICN"',
                 checks=[])

        self.cmd('az logic integration-account-partner create '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--partner-name "testPartner" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-agreement create '
                 '--agreement-name "testAgreement" '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-certificate create '
                 '--certificate-name "testCertificate" '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-assembly create '
                 '--assembly-artifact-name "testAssembly" '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-batch-configuration create '
                 '--batch-configuration-name "testBatchConfiguration" '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic workflow-run-action-repetition-request-history show '
                 '--action-name "HTTP_Webhook" '
                 '--repetition-name "000001" '
                 '--request-history-name "08586611142732800686" '
                 '--resource-group "{rg}" '
                 '--run-name "08586776228332053161046300351" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic workflow-run-action-request-history show '
                 '--action-name "HTTP_Webhook" '
                 '--request-history-name "08586611142732800686" '
                 '--resource-group "{rg}" '
                 '--run-name "08586776228332053161046300351" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic workflow-run-action-scope-repetition show '
                 '--action-name "for_each" '
                 '--repetition-name "000000" '
                 '--resource-group "{rg_2}" '
                 '--run-name "08586776228332053161046300351" '
                 '--workflow-name "{Workflows_2}"',
                 checks=[])

        self.cmd('az logic workflow-run-action-repetition show '
                 '--action-name "testAction" '
                 '--repetition-name "000001" '
                 '--resource-group "{rg_2}" '
                 '--run-name "08586776228332053161046300351" '
                 '--workflow-name "{Workflows_2}"',
                 checks=[])

        self.cmd('az logic integration-account-batch-configuration show '
                 '--batch-configuration-name "testBatchConfiguration" '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment-managed-api list '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment-managed-api show '
                 '--api-name "servicebus" '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment-managed-api put '
                 '--api-name "servicebus" '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment-managed-api-operation list '
                 '--api-name "servicebus" '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-assembly show '
                 '--assembly-artifact-name "testAssembly" '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment-network-health show '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-certificate show '
                 '--certificate-name "testCertificate" '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic workflow-trigger-history show '
                 '--history-name "08586676746934337772206998657CU22" '
                 '--resource-group "{rg_2}" '
                 '--trigger-name "testTriggerName" '
                 '--workflow-name "{Workflows_3}"',
                 checks=[])

        self.cmd('az logic integration-account-agreement show '
                 '--agreement-name "testAgreement" '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-partner show '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--partner-name "testPartner" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-session show '
                 '--integration-account-name "{IntegrationAccounts_2}" '
                 '--resource-group "{rg_3}" '
                 '--session-name "testsession123-ICN"',
                 checks=[])

        self.cmd('az logic integration-account-schema show '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}" '
                 '--schema-name "testSchema"',
                 checks=[])

        self.cmd('az logic workflow-run-operation show '
                 '--operation-id "ebdcbbde-c4db-43ec-987c-fd0f7726f43b" '
                 '--resource-group "{rg_2}" '
                 '--run-name "08586774142730039209110422528" '
                 '--workflow-name "{Workflows_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment show '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic workflow-run-action show '
                 '--action-name "HTTP" '
                 '--resource-group "{rg}" '
                 '--run-name "08586676746934337772206998657CU22" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic integration-account-map show '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--map-name "testMap" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic workflow-trigger show '
                 '--resource-group "{rg}" '
                 '--trigger-name "manual" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic workflow-version show '
                 '--resource-group "{rg}" '
                 '--version-id "08586676824806722526" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic integration-account show '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic workflow-run show '
                 '--resource-group "{rg}" '
                 '--run-name "08586676746934337772206998657CU22" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic workflow show '
                 '--resource-group "{rg}" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic workflow-run-action-repetition-request-history list '
                 '--action-name "HTTP_Webhook" '
                 '--repetition-name "000001" '
                 '--resource-group "{rg}" '
                 '--run-name "08586776228332053161046300351" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic integration-service-environment-managed-api list '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment-managed-api show '
                 '--api-name "servicebus" '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment-managed-api put '
                 '--api-name "servicebus" '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment-managed-api-operation list '
                 '--api-name "servicebus" '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic workflow-run-action-request-history list '
                 '--action-name "HTTP_Webhook" '
                 '--resource-group "{rg}" '
                 '--run-name "08586776228332053161046300351" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic workflow-run-action-scope-repetition list '
                 '--action-name "for_each" '
                 '--resource-group "{rg_2}" '
                 '--run-name "08586776228332053161046300351" '
                 '--workflow-name "{Workflows_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment-managed-api list '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment-managed-api show '
                 '--api-name "servicebus" '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment-managed-api put '
                 '--api-name "servicebus" '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment-managed-api-operation list '
                 '--api-name "servicebus" '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic workflow-run-action-repetition list '
                 '--action-name "testAction" '
                 '--resource-group "{rg_2}" '
                 '--run-name "08586776228332053161046300351" '
                 '--workflow-name "{Workflows_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment-sku list '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-batch-configuration list '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic workflow-trigger-history list '
                 '--resource-group "{rg_2}" '
                 '--trigger-name "testTriggerName" '
                 '--workflow-name "{Workflows_3}"',
                 checks=[])

        self.cmd('az logic integration-account-certificate list '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-assembly list '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-agreement list '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-partner list '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-session list '
                 '--integration-account-name "{IntegrationAccounts_2}" '
                 '--resource-group "{rg_3}"',
                 checks=[])

        self.cmd('az logic integration-account-schema list '
                 '--integration-account-name "{IntegrationAccounts_3}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-map list '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic workflow-run-action list '
                 '--resource-group "{rg}" '
                 '--run-name "08586676746934337772206998657CU22" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic workflow-version list '
                 '--resource-group "{rg}" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic workflow-trigger list '
                 '--resource-group "{rg}" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic workflow-run list '
                 '--resource-group "{rg}" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic integration-service-environment list '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account list '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic workflow list '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az logic integration-service-environment list',
                 checks=[])

        self.cmd('az logic integration-account list',
                 checks=[])

        self.cmd('az logic workflow list',
                 checks=[])

        self.cmd('az logic workflow-run-action-repetition list-expression-trace '
                 '--action-name "testAction" '
                 '--repetition-name "000001" '
                 '--resource-group "{rg_2}" '
                 '--run-name "08586776228332053161046300351" '
                 '--workflow-name "{Workflows_2}"',
                 checks=[])

        self.cmd('az logic integration-account-assembly list-content-callback-url '
                 '--assembly-artifact-name "testAssembly" '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-schema list-content-callback-url '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}" '
                 '--schema-name "testSchema"',
                 checks=[])

        self.cmd('az logic integration-account-map list-content-callback-url '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--map-name "testMap" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-partner list-content-callback-url '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--partner-name "testPartner" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-agreement list-content-callback-url '
                 '--agreement-name "testAgreement" '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-schema list-content-callback-url '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}" '
                 '--schema-name "testSchema"',
                 checks=[])

        self.cmd('az logic integration-account-map list-content-callback-url '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--map-name "testMap" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-partner list-content-callback-url '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--partner-name "testPartner" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-agreement list-content-callback-url '
                 '--agreement-name "testAgreement" '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-schema list-content-callback-url '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}" '
                 '--schema-name "testSchema"',
                 checks=[])

        self.cmd('az logic integration-account-map list-content-callback-url '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--map-name "testMap" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-partner list-content-callback-url '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--partner-name "testPartner" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-agreement list-content-callback-url '
                 '--agreement-name "testAgreement" '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic workflow-version-trigger list-callback-url '
                 '--resource-group "{rg_2}" '
                 '--trigger-name "testTriggerName" '
                 '--version-id "testWorkflowVersionId" '
                 '--workflow-name "{Workflows_3}"',
                 checks=[])

        self.cmd('az logic integration-service-environment-managed-api list '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment-managed-api show '
                 '--api-name "servicebus" '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment-managed-api put '
                 '--api-name "servicebus" '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment-managed-api-operation list '
                 '--api-name "servicebus" '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-schema list-content-callback-url '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}" '
                 '--schema-name "testSchema"',
                 checks=[])

        self.cmd('az logic integration-account-map list-content-callback-url '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--map-name "testMap" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-partner list-content-callback-url '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--partner-name "testPartner" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-agreement list-content-callback-url '
                 '--agreement-name "testAgreement" '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic workflow-run-action list-expression-trace '
                 '--action-name "testAction" '
                 '--resource-group "{rg_2}" '
                 '--run-name "08586776228332053161046300351" '
                 '--workflow-name "{Workflows_2}"',
                 checks=[])

        self.cmd('az logic workflow-trigger-history resubmit '
                 '--history-name "testHistoryName" '
                 '--resource-group "{rg_2}" '
                 '--trigger-name "testTriggerName" '
                 '--workflow-name "{Workflows_3}"',
                 checks=[])

        self.cmd('az logic integration-service-environment restart '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account regenerate-access-key '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic workflow-trigger list-callback-url '
                 '--resource-group "{rg}" '
                 '--trigger-name "manual" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic integration-account log-tracking-event '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment update '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account list-key-vault-key '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic workflow-trigger reset '
                 '--resource-group "{rg_2}" '
                 '--trigger-name "testTrigger" '
                 '--workflow-name "{Workflows_4}"',
                 checks=[])

        self.cmd('az logic integration-account list-callback-url '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic workflow-trigger reset '
                 '--resource-group "{rg_2}" '
                 '--trigger-name "testTrigger" '
                 '--workflow-name "{Workflows_4}"',
                 checks=[])

        self.cmd('az logic workflow validate-by-resource-group '
                 '--resource-group "{rg}" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic workflow validate-by-location '
                 '--location "brazilsouth" '
                 '--resource-group "{rg}" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic workflow-trigger reset '
                 '--resource-group "{rg_2}" '
                 '--trigger-name "testTrigger" '
                 '--workflow-name "{Workflows_4}"',
                 checks=[])

        self.cmd('az logic workflow generate-upgraded-definition '
                 '--resource-group "{rg}" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic workflow-trigger run '
                 '--resource-group "{rg}" '
                 '--trigger-name "manual" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic workflow-run cancel '
                 '--resource-group "{rg}" '
                 '--run-name "08586676746934337772206998657CU22" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic workflow regenerate-access-key '
                 '--key-type "Primary" '
                 '--resource-group "{rg_2}" '
                 '--workflow-name "{Workflows_3}"',
                 checks=[])

        self.cmd('az logic integration-account update '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic workflow list-callback-url '
                 '--resource-group "{rg_2}" '
                 '--workflow-name "{Workflows_4}"',
                 checks=[])

        self.cmd('az logic workflow list-swagger '
                 '--resource-group "{rg_2}" '
                 '--workflow-name "{Workflows_3}"',
                 checks=[])

        self.cmd('az logic workflow validate-by-resource-group '
                 '--resource-group "{rg}" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic workflow validate-by-location '
                 '--location "brazilsouth" '
                 '--resource-group "{rg}" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic workflow disable '
                 '--resource-group "{rg}" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic workflow enable '
                 '--resource-group "{rg}" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic workflow move '
                 '--resource-group "{rg_2}" '
                 '--workflow-name "{Workflows_4}"',
                 checks=[])

        self.cmd('az logic workflow update '
                 '--resource-group "{rg}" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic integration-account-batch-configuration delete '
                 '--batch-configuration-name "testBatchConfiguration" '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment-managed-api delete '
                 '--api-name "servicebus" '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-assembly delete '
                 '--assembly-artifact-name "testAssembly" '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-certificate delete '
                 '--certificate-name "testCertificate" '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-agreement delete '
                 '--agreement-name "testAgreement" '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-partner delete '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--partner-name "testPartner" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account-session delete '
                 '--integration-account-name "{IntegrationAccounts_2}" '
                 '--resource-group "{rg_3}" '
                 '--session-name "testsession123-ICN"',
                 checks=[])

        self.cmd('az logic integration-account-schema delete '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}" '
                 '--schema-name "testSchema"',
                 checks=[])

        self.cmd('az logic integration-account-map delete '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--map-name "testMap" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account delete '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment delete '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-account delete '
                 '--integration-account-name "{testIntegrationAccount}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic integration-service-environment delete '
                 '--integration-service-environment-name "{testIntegrationServiceEnvironment}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic workflow delete '
                 '--resource-group "{rg}" '
                 '--workflow-name "{test-workflow}"',
                 checks=[])
