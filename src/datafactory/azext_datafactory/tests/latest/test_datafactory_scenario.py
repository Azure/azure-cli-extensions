# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class DataFactoryScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_datafactory')
    def test_datafactory(self, resource_group):

        self.kwargs.update({
            'name': 'test1'
        })

        self.cmd('az datafactory create '
                 '--resource-group {rg} '
                 '--name "exampleFactoryName" '
                 '--location "East US"',
                 checks=[])

        self.cmd('az datafactory dataset create '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleDataset" '
                 '--linked-service-name-type "LinkedServiceReference" '
                 '--linked-service-name-reference-name "exampleLinkedService"',
                 checks=[])

        self.cmd('az datafactory dataset create '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleDataset" '
                 '--description "Example description" '
                 '--linked-service-name-type "LinkedServiceReference" '
                 '--linked-service-name-reference-name "exampleLinkedService"',
                 checks=[])

        self.cmd('az datafactory trigger create '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleTrigger" '
                 '--description "Example description"',
                 checks=[])

        self.cmd('az datafactory trigger create '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleTrigger"',
                 checks=[])

        self.cmd('az datafactory dataflow create '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleDataFlow" '
                 '--description "Sample demo data flow to convert currencies showing usage of union, derive and conditional split transformation."',
                 checks=[])

        self.cmd('az datafactory pipeline create '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--pipeline-name "examplePipeline"',
                 checks=[])

        self.cmd('az datafactory dataflow create '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleDataFlow" '
                 '--description "Sample demo data flow to convert currencies showing usage of union, derive and conditional split transformation."',
                 checks=[])

        self.cmd('az datafactory pipeline create '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--pipeline-name "examplePipeline" '
                 '--description "Example description"',
                 checks=[])

        self.cmd('az datafactory linkedservice create '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleLinkedService"',
                 checks=[])

        self.cmd('az datafactory linkedservice create '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleLinkedService" '
                 '--description "Example description"',
                 checks=[])

        self.cmd('az datafactory integration-runtime create '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleIntegrationRuntime" '
                 '--description "A selfhosted integration runtime"',
                 checks=[])

        self.cmd('az datafactory trigger rerun-trigger create '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--trigger-name "exampleTrigger" '
                 '--name "exampleRerunTrigger" '
                 '--start-time "2018-06-16T00:39:13.8441801Z" '
                 '--end-time "2018-06-16T00:55:13.8441801Z" '
                 '--max-concurrency "4"',
                 checks=[])

        self.cmd('az datafactory integration-runtime node show '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--name "Node_1"',
                 checks=[])

        self.cmd('az datafactory integration-runtime show '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleIntegrationRuntime"',
                 checks=[])

        self.cmd('az datafactory trigger rerun-trigger list '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--trigger-name "exampleTrigger"',
                 checks=[])

        self.cmd('az datafactory linkedservice show '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleLinkedService"',
                 checks=[])

        self.cmd('az datafactory query-pipeline-run get '
                 '--resource-group {rg} '
                 '--name "exampleFactoryName"',
                 checks=[])

        self.cmd('az datafactory pipeline show '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--pipeline-name "examplePipeline"',
                 checks=[])

        self.cmd('az datafactory dataflow show '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleDataFlow"',
                 checks=[])

        self.cmd('az datafactory dataset show '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleDataset"',
                 checks=[])

        self.cmd('az datafactory trigger show '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleTrigger"',
                 checks=[])

        self.cmd('az datafactory integration-runtime list '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName"',
                 checks=[])

        self.cmd('az datafactory linkedservice list '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName"',
                 checks=[])

        self.cmd('az datafactory dataflow list '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName"',
                 checks=[])

        self.cmd('az datafactory pipeline list '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName"',
                 checks=[])

        self.cmd('az datafactory trigger list '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName"',
                 checks=[])

        self.cmd('az datafactory dataset list '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName"',
                 checks=[])

        self.cmd('az datafactory show '
                 '--resource-group {rg} '
                 '--name "exampleFactoryName"',
                 checks=[])

        self.cmd('az datafactory list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az datafactory list',
                 checks=[])

        self.cmd('az datafactory list',
                 checks=[])

        self.cmd('az datafactory integration-runtime node get_ip_address '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--name "Node_1"',
                 checks=[])

        self.cmd('az datafactory integration-runtime create_linked_integration_runtime '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleIntegrationRuntime" '
                 '--subscription-id "061774c7-4b5a-4159-a55b-365581830283" '
                 '--data-factory-name "e9955d6d-56ea-4be3-841c-52a12c1a9981" '
                 '--data-factory-location "West US"',
                 checks=[])

        self.cmd('az datafactory trigger rerun-trigger cancel '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--trigger-name "exampleTrigger" '
                 '--name "exampleRerunTrigger"',
                 checks=[])

        self.cmd('az datafactory trigger rerun-trigger start '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--trigger-name "exampleTrigger" '
                 '--name "exampleRerunTrigger"',
                 checks=[])

        self.cmd('az datafactory integration-runtime node update '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--name "Node_1" '
                 '--concurrent-jobs-limit "2"',
                 checks=[])

        self.cmd('az datafactory integration-runtime refresh-object-metadata refresh '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "testactivityv2"',
                 checks=[])

        self.cmd('az datafactory trigger rerun-trigger stop '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--trigger-name "exampleTrigger" '
                 '--name "exampleRerunTrigger"',
                 checks=[])

        self.cmd('az datafactory integration-runtime regenerate_auth_key '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleIntegrationRuntime" '
                 '--key-name "authKey2"',
                 checks=[])

        self.cmd('az datafactory trigger trigger-run rerun rerun '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleTrigger" '
                 '--run-id "2f7fdb90-5df1-4b8e-ac2f-064cfa58202b"',
                 checks=[])

        self.cmd('az datafactory integration-runtime refresh-object-metadata get '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "testactivityv2"',
                 checks=[])

        self.cmd('az datafactory integration-runtime get_connection_info '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleIntegrationRuntime"',
                 checks=[])

        self.cmd('az datafactory integration-runtime sync_credentials '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleIntegrationRuntime"',
                 checks=[])

        self.cmd('az datafactory integration-runtime get_monitoring_data '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleIntegrationRuntime"',
                 checks=[])

        self.cmd('az datafactory integration-runtime list_auth_keys '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleIntegrationRuntime"',
                 checks=[])

        self.cmd('az datafactory integration-runtime remove_links '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleIntegrationRuntime"',
                 checks=[])

        self.cmd('az datafactory integration-runtime get_status '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleIntegrationRuntime"',
                 checks=[])

        self.cmd('az datafactory integration-runtime remove_links '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleIntegrationRuntime"',
                 checks=[])

        self.cmd('az datafactory integration-runtime start '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleManagedIntegrationRuntime"',
                 checks=[])

        self.cmd('az datafactory integration-runtime stop '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleManagedIntegrationRuntime"',
                 checks=[])

        self.cmd('az datafactory trigger get_event_subscription_status '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleTrigger"',
                 checks=[])

        self.cmd('az datafactory pipelinerun query-activityrun query_by_pipeline_run '
                 '--resource-group {rg} '
                 '--name "exampleFactoryName" '
                 '--run-id "2f7fdb90-5df1-4b8e-ac2f-064cfa58202b"',
                 checks=[])

        self.cmd('az datafactory integration-runtime update '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleIntegrationRuntime" '
                 '--auto-update "Off" '
                 '--update-delay-offset "\"PT3H\""',
                 checks=[])

        self.cmd('az datafactory trigger unsubscribe_from_events '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleTrigger"',
                 checks=[])

        self.cmd('az datafactory trigger subscribe_to_events '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleTrigger"',
                 checks=[])

        self.cmd('az datafactory query-pipeline-run cancel '
                 '--resource-group {rg} '
                 '--name "exampleFactoryName"',
                 checks=[])

        self.cmd('az datafactory pipeline create_run '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--pipeline-name "examplePipeline"',
                 checks=[])

        self.cmd('az datafactory trigger start '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleTrigger"',
                 checks=[])

        self.cmd('az datafactory trigger stop '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleTrigger"',
                 checks=[])

        self.cmd('az datafactory create-data-flow-debug-session execute_command '
                 '--resource-group {rg} '
                 '--name "exampleFactoryName" '
                 '--session-id "f06ed247-9d07-49b2-b05e-2cb4a2fc871e" '
                 '--command "executePreviewQuery" '
                 '--stream-name "source1" '
                 '--row-limits "100"',
                 checks=[])

        self.cmd('az datafactory create-data-flow-debug-session delete '
                 '--resource-group {rg} '
                 '--name "exampleFactoryName" '
                 '--session-id "91fb57e0-8292-47be-89ff-c8f2d2bb2a7e"',
                 checks=[])

        self.cmd('az datafactory create-data-flow-debug-session create '
                 '--resource-group {rg} '
                 '--name "exampleFactoryName" '
                 '--time-to-live "60"',
                 checks=[])

        self.cmd('az datafactory create-data-flow-debug-session query_by_factory '
                 '--resource-group {rg} '
                 '--name "exampleFactoryName"',
                 checks=[])

        self.cmd('az datafactory create-data-flow-debug-session add_data_flow '
                 '--resource-group {rg} '
                 '--name "exampleFactoryName" '
                 '--session-id "f06ed247-9d07-49b2-b05e-2cb4a2fc871e"',
                 checks=[])

        self.cmd('az datafactory get_git_hub_access_token '
                 '--resource-group {rg} '
                 '--name "exampleFactoryName" '
                 '--git-hub-access-code "some" '
                 '--git-hub-client-id "some" '
                 '--git-hub-access-token-base-url "some"',
                 checks=[])

        self.cmd('az datafactory get_data_plane_access '
                 '--resource-group {rg} '
                 '--name "exampleFactoryName" '
                 '--permissions "r" '
                 '--access-resource-path "" '
                 '--profile-name "DefaultProfile" '
                 '--start-time "2018-11-10T02:46:20.2659347Z" '
                 '--expire-time "2018-11-10T09:46:20.2659347Z"',
                 checks=[])

        self.cmd('az datafactory query-pipeline-run query_by_factory '
                 '--resource-group {rg} '
                 '--name "exampleFactoryName"',
                 checks=[])

        self.cmd('az datafactory trigger trigger-run rerun query_by_factory '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName"',
                 checks=[])

        self.cmd('az datafactory get-feature-value get_feature_value_by_factory',
                 checks=[])

        self.cmd('az datafactory update '
                 '--resource-group {rg} '
                 '--name "exampleFactoryName"',
                 checks=[])

        self.cmd('az datafactory configure_factory_repo '
                 '--factory-resource-id "/subscriptions/{{ subscription_id }}/resourceGroups/{{ resource_group }}/providers/Microsoft.DataFactory/factories/{{ factory_name }}" '
                 '--account-name "ADF" '
                 '--repository-name "repo" '
                 '--collaboration-branch "master" '
                 '--root-folder "/" '
                 '--last-commit-id ""',
                 checks=[])

        self.cmd('az datafactory get-feature-value get_feature_value '
                 '--location-id "WestEurope"',
                 checks=[])

        self.cmd('az datafactory integration-runtime node delete '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--integration-runtime-name "exampleIntegrationRuntime" '
                 '--name "Node_1"',
                 checks=[])

        self.cmd('az datafactory integration-runtime delete '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleIntegrationRuntime"',
                 checks=[])

        self.cmd('az datafactory linkedservice delete '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleLinkedService"',
                 checks=[])

        self.cmd('az datafactory pipeline delete '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--pipeline-name "examplePipeline"',
                 checks=[])

        self.cmd('az datafactory dataflow delete '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleDataFlow"',
                 checks=[])

        self.cmd('az datafactory dataset delete '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleDataset"',
                 checks=[])

        self.cmd('az datafactory trigger delete '
                 '--resource-group {rg} '
                 '--factory-name "exampleFactoryName" '
                 '--name "exampleTrigger"',
                 checks=[])

        self.cmd('az datafactory delete '
                 '--resource-group {rg} '
                 '--name "exampleFactoryName"',
                 checks=[])
