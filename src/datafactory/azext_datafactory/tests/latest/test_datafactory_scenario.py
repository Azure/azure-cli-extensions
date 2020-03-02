# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class DataFactoryManagementClientScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_datafactory')
    def test_datafactory(self, resource_group):

        self.cmd('az datafactory factory create '
                 '--location "East US" '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory trigger create '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg} '
                 '--trigger-name "exampleTrigger"',
                 checks=[])

        self.cmd('az datafactory trigger create '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg} '
                 '--trigger-name "exampleTrigger"',
                 checks=[])

        self.cmd('az datafactory dataset create '
                 '--dataset-name "exampleDataset" '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory dataset create '
                 '--dataset-name "exampleDataset" '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory data-flow create '
                 '--data-flow-name "exampleDataFlow" '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory data-flow create '
                 '--data-flow-name "exampleDataFlow" '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory pipeline create '
                 '--factory-name "exampleFactoryName" '
                 '--description "Example description" '
                 '--pipeline-name "examplePipeline" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory pipeline create '
                 '--factory-name "exampleFactoryName" '
                 '--pipeline-name "examplePipeline" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory data-flow-debug-session create '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg} '
                 '--compute-type "General" '
                 '--core-count 48 '
                 '--time-to-live 60',
                 checks=[])

        self.cmd('az datafactory linked-service create '
                 '--factory-name "exampleFactoryName" '
                 '--linked-service-name "exampleLinkedService" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory linked-service create '
                 '--factory-name "exampleFactoryName" '
                 '--linked-service-name "exampleLinkedService" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory integration-runtime create '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory integration-runtime-node get-ip-address '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--node-name "Node_1" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory integration-runtime create-linked-integration-runtime '
                 '--name "bfa92911-9fb6-4fbe-8f23-beae87bc1c83" '
                 '--data-factory-location "West US" '
                 '--data-factory-name "e9955d6d-56ea-4be3-841c-52a12c1a9981" '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory integration-runtime-object-metadata refresh '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "testactivityv2" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory integration-runtime regenerate-auth-key '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--key-name "authKey2" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory integration-runtime get-connection-info '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory integration-runtime-object-metadata get '
                 '--factory-name "exampleFactoryName" '
                 '--metadata-path "ssisFolders" '
                 '--integration-runtime-name "testactivityv2" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory integration-runtime-node show '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--node-name "Node_1" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory integration-runtime-node update '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--node-name "Node_1" '
                 '--resource-group {rg} '
                 '--concurrent-jobs-limit 2',
                 checks=[])

        self.cmd('az datafactory integration-runtime sync-credentials '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory integration-runtime get-monitoring-data '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory integration-runtime list-auth-key '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory integration-runtime remove-link '
                 '--factory-name "exampleFactoryName-linked" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory integration-runtime upgrade '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory integration-runtime get-status '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory integration-runtime remove-link '
                 '--factory-name "exampleFactoryName-linked" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory integration-runtime upgrade '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory integration-runtime start '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleManagedIntegrationRuntime" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory integration-runtime stop '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleManagedIntegrationRuntime" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory trigger get-event-subscription-status '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg} '
                 '--trigger-name "exampleTrigger"',
                 checks=[])

        self.cmd('az datafactory trigger-run rerun '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg} '
                 '--run-id "2f7fdb90-5df1-4b8e-ac2f-064cfa58202b" '
                 '--trigger-name "exampleTrigger"',
                 checks=[])

        self.cmd('az datafactory integration-runtime show '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory integration-runtime update '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--resource-group {rg} '
                 '--auto-update "Off" '
                 '--update-delay-offset "\"PT3H\""',
                 checks=[])

        self.cmd('az datafactory trigger unsubscribe-from-event '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg} '
                 '--trigger-name "exampleTrigger"',
                 checks=[])

        self.cmd('az datafactory trigger subscribe-to-event '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg} '
                 '--trigger-name "exampleTrigger"',
                 checks=[])

        self.cmd('az datafactory activity-run query-by-pipeline-run '
                 '--factory-name "exampleFactoryName" '
                 '--last-updated-after "2018-06-16T00:36:44.3345758Z" '
                 '--last-updated-before "2018-06-16T00:49:48.3686473Z" '
                 '--resource-group {rg} '
                 '--run-id "2f7fdb90-5df1-4b8e-ac2f-064cfa58202b"',
                 checks=[])

        self.cmd('az datafactory linked-service show '
                 '--factory-name "exampleFactoryName" '
                 '--linked-service-name "exampleLinkedService" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory pipeline create-run '
                 '--factory-name "exampleFactoryName" '
                 '--pipeline-name "examplePipeline" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory trigger start '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg} '
                 '--trigger-name "exampleTrigger"',
                 checks=[])

        self.cmd('az datafactory pipeline-run cancel '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg} '
                 '--run-id "16ac5348-ff82-4f95-a80d-638c1d47b721"',
                 checks=[])

        self.cmd('az datafactory trigger stop '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg} '
                 '--trigger-name "exampleTrigger"',
                 checks=[])

        self.cmd('az datafactory data-flow-debug-session execute-command '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg} '
                 '--command "executePreviewQuery" '
                 '--session-id "f06ed247-9d07-49b2-b05e-2cb4a2fc871e"',
                 checks=[])

        self.cmd('az datafactory data-flow-debug-session query-by-factory '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory data-flow-debug-session add-data-flow '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg} '
                 '--session-id "f06ed247-9d07-49b2-b05e-2cb4a2fc871e"',
                 checks=[])

        self.cmd('az datafactory pipeline show '
                 '--factory-name "exampleFactoryName" '
                 '--pipeline-name "examplePipeline" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory data-flow show '
                 '--data-flow-name "exampleDataFlow" '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory dataset show '
                 '--dataset-name "exampleDataset" '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory trigger show '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg} '
                 '--trigger-name "exampleTrigger"',
                 checks=[])

        self.cmd('az datafactory factory get-git-hub-access-token '
                 '--factory-name "exampleFactoryName" '
                 '--git-hub-access-code "some" '
                 '--git-hub-access-token-base-url "some" '
                 '--git-hub-client-id "some" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory pipeline-run show '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg} '
                 '--run-id "2f7fdb90-5df1-4b8e-ac2f-064cfa58202b"',
                 checks=[])

        self.cmd('az datafactory integration-runtime list '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory factory get-data-plane-access '
                 '--factory-name "exampleFactoryName" '
                 '--access-resource-path "" '
                 '--expire-time "2018-11-10T09:46:20.2659347Z" '
                 '--permissions "r" '
                 '--profile-name "DefaultProfile" '
                 '--start-time "2018-11-10T02:46:20.2659347Z" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory pipeline-run query-by-factory '
                 '--factory-name "exampleFactoryName" '
                 '--last-updated-after "2018-06-16T00:36:44.3345758Z" '
                 '--last-updated-before "2018-06-16T00:49:48.3686473Z" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory trigger-run query-by-factory '
                 '--factory-name "exampleFactoryName" '
                 '--last-updated-after "2018-06-16T00:36:44.3345758Z" '
                 '--last-updated-before "2018-06-16T00:49:48.3686473Z" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory exposure-control get-feature-value-by-factory '
                 '--feature-name "ADFIntegrationRuntimeSharingRbac" '
                 '--feature-type "Feature" '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory linked-service list '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory trigger query-by-factory '
                 '--factory-name "exampleFactoryName" '
                 '--parent-trigger-name "exampleTrigger" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory pipeline list '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory data-flow list '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory dataset list '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory trigger list '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory factory show '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory factory update '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory factory list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory factory configure-factory-repo '
                 '--factory-resource-id "/subscriptions/12345678-1234-1234-1234-12345678abc/resourceGroups/exampleResourceGroup/providers/Microsoft.DataFactory/factories/exampleFactoryName" '
                 '--location-id "East US"',
                 checks=[])

        self.cmd('az datafactory exposure-control get-feature-value '
                 '--feature-name "ADFIntegrationRuntimeSharingRbac" '
                 '--feature-type "Feature" '
                 '--location-id "WestEurope"',
                 checks=[])

        self.cmd('az datafactory factory list',
                 checks=[])

        self.cmd('az datafactory integration-runtime-node delete '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--node-name "Node_1" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory integration-runtime delete '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory linked-service delete '
                 '--factory-name "exampleFactoryName" '
                 '--linked-service-name "exampleLinkedService" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory data-flow-debug-session delete '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg} '
                 '--session-id "91fb57e0-8292-47be-89ff-c8f2d2bb2a7e"',
                 checks=[])

        self.cmd('az datafactory pipeline delete '
                 '--factory-name "exampleFactoryName" '
                 '--pipeline-name "examplePipeline" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory data-flow delete '
                 '--data-flow-name "exampleDataFlow" '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory dataset delete '
                 '--dataset-name "exampleDataset" '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory trigger delete '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg} '
                 '--trigger-name "exampleTrigger"',
                 checks=[])

        self.cmd('az datafactory factory delete '
                 '--factory-name "exampleFactoryName" '
                 '--resource-group {rg}',
                 checks=[])
