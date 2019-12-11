# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['datafactory'] = """
    type: group
    short-summary: Commands to manage datafactory.
"""

helps['datafactory list'] = """
    type: command
    short-summary: Lists the available Azure Data Factory API operations.
    examples:
      - name: Operations_List
        text: |-
               az datafactory list
"""

helps['datafactory'] = """
    type: group
    short-summary: Commands to manage datafactory.
"""

helps['datafactory create'] = """
    type: command
    short-summary: Creates or updates a factory.
    examples:
      - name: Factories_CreateOrUpdate
        text: |-
               az datafactory create --resource-group "exampleResourceGroup" --name "exampleFactoryName" \\
               --location "East US"
"""

helps['datafactory update'] = """
    type: command
    short-summary: Creates or updates a factory.
    examples:
      - name: Factories_Update
        text: |-
               az datafactory update --resource-group "exampleResourceGroup" --name "exampleFactoryName"
"""

helps['datafactory delete'] = """
    type: command
    short-summary: Deletes a factory.
    examples:
      - name: Factories_Delete
        text: |-
               az datafactory delete --resource-group "exampleResourceGroup" --name "exampleFactoryName"
"""

helps['datafactory show'] = """
    type: command
    short-summary: Gets a factory.
    examples:
      - name: Factories_Get
        text: |-
               az datafactory show --resource-group "exampleResourceGroup" --name "exampleFactoryName"
"""

helps['datafactory list'] = """
    type: command
    short-summary: Lists factories.
    examples:
      - name: Factories_List
        text: |-
               az datafactory list
      - name: Factories_ListByResourceGroup
        text: |-
               az datafactory list --resource-group "exampleResourceGroup"
"""

helps['datafactory configure_factory_repo'] = """
    type: command
    short-summary: Updates a factory's repo information.
    examples:
      - name: Factories_ConfigureFactoryRepo
        text: |-
               az datafactory configure_factory_repo --location-id "East US"
"""

helps['datafactory get_git_hub_access_token'] = """
    type: command
    short-summary: Get GitHub Access Token.
    examples:
      - name: Factories_GetGitHubAccessToken
        text: |-
               az datafactory get_git_hub_access_token --resource-group "exampleResourceGroup" --name \\
               "exampleFactoryName"
"""

helps['datafactory get_data_plane_access'] = """
    type: command
    short-summary: Get Data Plane access.
    examples:
      - name: Factories_GetDataPlaneAccess
        text: |-
               az datafactory get_data_plane_access --resource-group "exampleResourceGroup" --name \\
               "exampleFactoryName"
"""

helps['datafactory get-feature-value'] = """
    type: group
    short-summary: Commands to manage datafactory get feature value.
"""

helps['datafactory get-feature-value get_feature_value'] = """
    type: command
    short-summary: Get exposure control feature for specific location.
    examples:
      - name: ExposureControl_GetFeatureValue
        text: |-
               az datafactory get-feature-value get_feature_value --location-id "WestEurope"
"""

helps['datafactory get-feature-value get_feature_value_by_factory'] = """
    type: command
    short-summary: Get exposure control feature for specific factory.
    examples:
      - name: ExposureControl_GetFeatureValueByFactory
        text: |-
               az datafactory get-feature-value get_feature_value_by_factory --resource-group \\
               "exampleResourceGroup" --name "exampleFactoryName"
"""

helps['datafactory integration-runtime'] = """
    type: group
    short-summary: Commands to manage datafactory integration runtime.
"""

helps['datafactory integration-runtime create'] = """
    type: command
    short-summary: Creates or updates an integration runtime.
    examples:
      - name: IntegrationRuntimes_Create
        text: |-
               az datafactory integration-runtime create --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --name "exampleIntegrationRuntime" --description \\
               "A selfhosted integration runtime"
"""

helps['datafactory integration-runtime update'] = """
    type: command
    short-summary: Creates or updates an integration runtime.
    examples:
      - name: IntegrationRuntimes_Update
        text: |-
               az datafactory integration-runtime update --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --name "exampleIntegrationRuntime" --auto-update \\
               "Off" --update-delay-offset "\\"PT3H\\""
"""

helps['datafactory integration-runtime delete'] = """
    type: command
    short-summary: Deletes an integration runtime.
    examples:
      - name: IntegrationRuntimes_Delete
        text: |-
               az datafactory integration-runtime delete --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --name "exampleIntegrationRuntime"
"""

helps['datafactory integration-runtime show'] = """
    type: command
    short-summary: Gets an integration runtime.
    examples:
      - name: IntegrationRuntimes_Get
        text: |-
               az datafactory integration-runtime show --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --name "exampleIntegrationRuntime"
"""

helps['datafactory integration-runtime list'] = """
    type: command
    short-summary: Lists integration runtimes.
    examples:
      - name: IntegrationRuntimes_ListByFactory
        text: |-
               az datafactory integration-runtime list --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName"
"""

helps['datafactory integration-runtime get_status'] = """
    type: command
    short-summary: Gets detailed status information for an integration runtime.
    examples:
      - name: IntegrationRuntimes_GetStatus
        text: |-
               az datafactory integration-runtime get_status --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --name "exampleIntegrationRuntime"
"""

helps['datafactory integration-runtime get_connection_info'] = """
    type: command
    short-summary: Gets the on-premises integration runtime connection information for encrypting the on-premises data source credentials.
    examples:
      - name: IntegrationRuntimes_GetConnectionInfo
        text: |-
               az datafactory integration-runtime get_connection_info --resource-group \\
               "exampleResourceGroup" --factory-name "exampleFactoryName" --name \\
               "exampleIntegrationRuntime"
"""

helps['datafactory integration-runtime regenerate_auth_key'] = """
    type: command
    short-summary: Regenerates the authentication key for an integration runtime.
    examples:
      - name: IntegrationRuntimes_RegenerateAuthKey
        text: |-
               az datafactory integration-runtime regenerate_auth_key --resource-group \\
               "exampleResourceGroup" --factory-name "exampleFactoryName" --name \\
               "exampleIntegrationRuntime"
"""

helps['datafactory integration-runtime create_linked_integration_runtime'] = """
    type: command
    short-summary: Create a linked integration runtime entry in a shared integration runtime.
    examples:
      - name: IntegrationRuntimes_CreateLinkedIntegrationRuntime
        text: |-
               az datafactory integration-runtime create_linked_integration_runtime --resource-group \\
               "exampleResourceGroup" --factory-name "exampleFactoryName" --name \\
               "exampleIntegrationRuntime"
"""

helps['datafactory integration-runtime start'] = """
    type: command
    short-summary: Starts a ManagedReserved type integration runtime.
    examples:
      - name: IntegrationRuntimes_Start
        text: |-
               az datafactory integration-runtime start --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --name "exampleManagedIntegrationRuntime"
"""

helps['datafactory integration-runtime stop'] = """
    type: command
    short-summary: Stops a ManagedReserved type integration runtime.
    examples:
      - name: IntegrationRuntimes_Stop
        text: |-
               az datafactory integration-runtime stop --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --name "exampleManagedIntegrationRuntime"
"""

helps['datafactory integration-runtime sync_credentials'] = """
    type: command
    short-summary: Force the integration runtime to synchronize credentials across integration runtime nodes, and this will override the credentials across all worker nodes with those available on the dispatcher node. If you already have the latest credential backup file, you should manually import it (preferred) on any self-hosted integration runtime node than using this API directly.
    examples:
      - name: IntegrationRuntimes_SyncCredentials
        text: |-
               az datafactory integration-runtime sync_credentials --resource-group \\
               "exampleResourceGroup" --factory-name "exampleFactoryName" --name \\
               "exampleIntegrationRuntime"
"""

helps['datafactory integration-runtime get_monitoring_data'] = """
    type: command
    short-summary: Get the integration runtime monitoring data, which includes the monitor data for all the nodes under this integration runtime.
    examples:
      - name: IntegrationRuntimes_GetMonitoringData
        text: |-
               az datafactory integration-runtime get_monitoring_data --resource-group \\
               "exampleResourceGroup" --factory-name "exampleFactoryName" --name \\
               "exampleIntegrationRuntime"
"""

helps['datafactory integration-runtime upgrade'] = """
    type: command
    short-summary: Upgrade self-hosted integration runtime to latest version if availability.
    examples:
      - name: IntegrationRuntimes_Upgrade
        text: |-
               az datafactory integration-runtime upgrade --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --name "exampleIntegrationRuntime"
"""

helps['datafactory integration-runtime remove_links'] = """
    type: command
    short-summary: Remove all linked integration runtimes under specific data factory in a self-hosted integration runtime.
    examples:
      - name: IntegrationRuntimes_Upgrade
        text: |-
               az datafactory integration-runtime remove_links --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --name "exampleIntegrationRuntime"
"""

helps['datafactory integration-runtime list_auth_keys'] = """
    type: command
    short-summary: Retrieves the authentication keys for an integration runtime.
    examples:
      - name: IntegrationRuntimes_ListAuthKeys
        text: |-
               az datafactory integration-runtime list_auth_keys --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --name "exampleIntegrationRuntime"
"""

helps['datafactory integration-runtime refresh-object-metadata'] = """
    type: group
    short-summary: Commands to manage datafactory integration runtime refresh object metadata.
"""

helps['datafactory integration-runtime refresh-object-metadata refresh'] = """
    type: command
    short-summary: Refresh a SSIS integration runtime object metadata.
    examples:
      - name: IntegrationRuntimeObjectMetadata_Refresh
        text: |-
               az datafactory integration-runtime refresh-object-metadata refresh --resource-group \\
               "exampleResourceGroup" --factory-name "exampleFactoryName" --name "testactivityv2"
"""

helps['datafactory integration-runtime refresh-object-metadata get'] = """
    type: command
    short-summary: Get a SSIS integration runtime object metadata by specified path. The return is pageable metadata list.
    examples:
      - name: IntegrationRuntimeObjectMetadata_Get
        text: |-
               az datafactory integration-runtime refresh-object-metadata get --resource-group \\
               "exampleResourceGroup" --factory-name "exampleFactoryName" --name "testactivityv2"
"""

helps['datafactory integration-runtime node'] = """
    type: group
    short-summary: Commands to manage datafactory integration runtime node.
"""

helps['datafactory integration-runtime node update'] = """
    type: command
    short-summary: Updates a self-hosted integration runtime node.
    examples:
      - name: IntegrationRuntimeNodes_Update
        text: |-
               az datafactory integration-runtime node update --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --integration-runtime-name \\
               "exampleIntegrationRuntime" --name "Node_1" --concurrent-jobs-limit "2"
"""

helps['datafactory integration-runtime node delete'] = """
    type: command
    short-summary: Deletes a self-hosted integration runtime node.
    examples:
      - name: IntegrationRuntimesNodes_Delete
        text: |-
               az datafactory integration-runtime node delete --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --integration-runtime-name \\
               "exampleIntegrationRuntime" --name "Node_1"
"""

helps['datafactory integration-runtime node show'] = """
    type: command
    short-summary: Gets a self-hosted integration runtime node.
    examples:
      - name: IntegrationRuntimeNodes_Get
        text: |-
               az datafactory integration-runtime node show --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --integration-runtime-name \\
               "exampleIntegrationRuntime" --name "Node_1"
"""

helps['datafactory integration-runtime node get_ip_address'] = """
    type: command
    short-summary: Get the IP address of self-hosted integration runtime node.
    examples:
      - name: IntegrationRuntimeNodes_GetIpAddress
        text: |-
               az datafactory integration-runtime node get_ip_address --resource-group \\
               "exampleResourceGroup" --factory-name "exampleFactoryName" --integration-runtime-name \\
               "exampleIntegrationRuntime" --name "Node_1"
"""

helps['datafactory linkedservice'] = """
    type: group
    short-summary: Commands to manage datafactory linkedservice.
"""

helps['datafactory linkedservice create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linkedservice create --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --name "exampleLinkedService"
      - name: LinkedServices_Update
        text: |-
               az datafactory linkedservice create --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --name "exampleLinkedService" --description \\
               "Example description"
"""

helps['datafactory linkedservice update'] = """
    type: command
    short-summary: Creates or updates a linked service.
"""

helps['datafactory linkedservice delete'] = """
    type: command
    short-summary: Deletes a linked service.
    examples:
      - name: LinkedServices_Delete
        text: |-
               az datafactory linkedservice delete --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --name "exampleLinkedService"
"""

helps['datafactory linkedservice show'] = """
    type: command
    short-summary: Gets a linked service.
    examples:
      - name: LinkedServices_Get
        text: |-
               az datafactory linkedservice show --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName" --name "exampleLinkedService"
"""

helps['datafactory linkedservice list'] = """
    type: command
    short-summary: Lists linked services.
    examples:
      - name: LinkedServices_ListByFactory
        text: |-
               az datafactory linkedservice list --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName"
"""

helps['datafactory dataset'] = """
    type: group
    short-summary: Commands to manage datafactory dataset.
"""

helps['datafactory dataset create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset create --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName" --name "exampleDataset"
      - name: Datasets_Update
        text: |-
               az datafactory dataset create --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName" --name "exampleDataset" --description "Example description"
"""

helps['datafactory dataset update'] = """
    type: command
    short-summary: Creates or updates a dataset.
"""

helps['datafactory dataset delete'] = """
    type: command
    short-summary: Deletes a dataset.
    examples:
      - name: Datasets_Delete
        text: |-
               az datafactory dataset delete --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName" --name "exampleDataset"
"""

helps['datafactory dataset show'] = """
    type: command
    short-summary: Gets a dataset.
    examples:
      - name: Datasets_Get
        text: |-
               az datafactory dataset show --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName" --name "exampleDataset"
"""

helps['datafactory dataset list'] = """
    type: command
    short-summary: Lists datasets.
    examples:
      - name: Datasets_ListByFactory
        text: |-
               az datafactory dataset list --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName"
"""

helps['datafactory pipeline'] = """
    type: group
    short-summary: Commands to manage datafactory pipeline.
"""

helps['datafactory pipeline create'] = """
    type: command
    short-summary: Creates or updates a pipeline.
    examples:
      - name: Pipelines_Create
        text: |-
               az datafactory pipeline create --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName" --pipeline-name "examplePipeline"
      - name: Pipelines_Update
        text: |-
               az datafactory pipeline create --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName" --pipeline-name "examplePipeline" --description \\
               "Example description"
"""

helps['datafactory pipeline update'] = """
    type: command
    short-summary: Creates or updates a pipeline.
"""

helps['datafactory pipeline delete'] = """
    type: command
    short-summary: Deletes a pipeline.
    examples:
      - name: Pipelines_Delete
        text: |-
               az datafactory pipeline delete --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName" --pipeline-name "examplePipeline"
"""

helps['datafactory pipeline show'] = """
    type: command
    short-summary: Gets a pipeline.
    examples:
      - name: Pipelines_Get
        text: |-
               az datafactory pipeline show --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName" --pipeline-name "examplePipeline"
"""

helps['datafactory pipeline list'] = """
    type: command
    short-summary: Lists pipelines.
    examples:
      - name: Pipelines_ListByFactory
        text: |-
               az datafactory pipeline list --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName"
"""

helps['datafactory pipeline create_run'] = """
    type: command
    short-summary: Creates a run of a pipeline.
    examples:
      - name: Pipelines_CreateRun
        text: |-
               az datafactory pipeline create_run --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName" --pipeline-name "examplePipeline"
"""

helps['datafactory query-pipeline-run'] = """
    type: group
    short-summary: Commands to manage datafactory query pipeline run.
"""

helps['datafactory query-pipeline-run query_by_factory'] = """
    type: command
    short-summary: Query pipeline runs in the factory based on input filter conditions.
    examples:
      - name: PipelineRuns_QueryByFactory
        text: |-
               az datafactory query-pipeline-run query_by_factory --resource-group \\
               "exampleResourceGroup" --name "exampleFactoryName"
"""

helps['datafactory query-pipeline-run cancel'] = """
    type: command
    short-summary: Cancel a pipeline run by its run ID.
    examples:
      - name: PipelineRuns_Cancel
        text: |-
               az datafactory query-pipeline-run cancel --resource-group "exampleResourceGroup" --name \\
               "exampleFactoryName" --run-id "16ac5348-ff82-4f95-a80d-638c1d47b721"
"""

helps['datafactory query-pipeline-run get'] = """
    type: command
    short-summary: Get a pipeline run by its run ID.
    examples:
      - name: PipelineRuns_Get
        text: |-
               az datafactory query-pipeline-run get --resource-group "exampleResourceGroup" --name \\
               "exampleFactoryName" --run-id "2f7fdb90-5df1-4b8e-ac2f-064cfa58202b"
"""

helps['datafactory pipelinerun query-activityrun'] = """
    type: group
    short-summary: Commands to manage datafactory pipelinerun query activityrun.
"""

helps['datafactory pipelinerun query-activityrun query_by_pipeline_run'] = """
    type: command
    short-summary: Query activity runs based on input filter conditions.
    examples:
      - name: ActivityRuns_QueryByPipelineRun
        text: |-
               az datafactory pipelinerun query-activityrun query_by_pipeline_run --resource-group \\
               "exampleResourceGroup" --name "exampleFactoryName" --run-id \\
               "2f7fdb90-5df1-4b8e-ac2f-064cfa58202b"
"""

helps['datafactory trigger'] = """
    type: group
    short-summary: Commands to manage datafactory trigger.
"""

helps['datafactory trigger create'] = """
    type: command
    short-summary: Creates or updates a trigger.
    examples:
      - name: Triggers_Create
        text: |-
               az datafactory trigger create --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName" --name "exampleTrigger"
      - name: Triggers_Update
        text: |-
               az datafactory trigger create --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName" --name "exampleTrigger" --description "Example description"
"""

helps['datafactory trigger update'] = """
    type: command
    short-summary: Creates or updates a trigger.
"""

helps['datafactory trigger delete'] = """
    type: command
    short-summary: Deletes a trigger.
    examples:
      - name: Triggers_Delete
        text: |-
               az datafactory trigger delete --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName" --name "exampleTrigger"
"""

helps['datafactory trigger show'] = """
    type: command
    short-summary: Gets a trigger.
    examples:
      - name: Triggers_Get
        text: |-
               az datafactory trigger show --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName" --name "exampleTrigger"
"""

helps['datafactory trigger list'] = """
    type: command
    short-summary: Lists triggers.
    examples:
      - name: Triggers_ListByFactory
        text: |-
               az datafactory trigger list --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName"
"""

helps['datafactory trigger subscribe_to_events'] = """
    type: command
    short-summary: Subscribe event trigger to events.
    examples:
      - name: Triggers_SubscribeToEvents
        text: |-
               az datafactory trigger subscribe_to_events --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --name "exampleTrigger"
"""

helps['datafactory trigger get_event_subscription_status'] = """
    type: command
    short-summary: Get a trigger's event subscription status.
    examples:
      - name: Triggers_GetEventSubscriptionStatus
        text: |-
               az datafactory trigger get_event_subscription_status --resource-group \\
               "exampleResourceGroup" --factory-name "exampleFactoryName" --name "exampleTrigger"
"""

helps['datafactory trigger unsubscribe_from_events'] = """
    type: command
    short-summary: Unsubscribe event trigger from events.
    examples:
      - name: Triggers_UnsubscribeFromEvents
        text: |-
               az datafactory trigger unsubscribe_from_events --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --name "exampleTrigger"
"""

helps['datafactory trigger start'] = """
    type: command
    short-summary: Starts a trigger.
    examples:
      - name: Triggers_Start
        text: |-
               az datafactory trigger start --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName" --name "exampleTrigger"
"""

helps['datafactory trigger stop'] = """
    type: command
    short-summary: Stops a trigger.
    examples:
      - name: Triggers_Stop
        text: |-
               az datafactory trigger stop --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName" --name "exampleTrigger"
"""

helps['datafactory trigger trigger-run rerun'] = """
    type: group
    short-summary: Commands to manage datafactory trigger trigger run rerun.
"""

helps['datafactory trigger trigger-run rerun rerun'] = """
    type: command
    short-summary: Rerun single trigger instance by runId.
    examples:
      - name: Triggers_Rerun
        text: |-
               az datafactory trigger trigger-run rerun rerun --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --name "exampleTrigger" --run-id \\
               "2f7fdb90-5df1-4b8e-ac2f-064cfa58202b"
"""

helps['datafactory trigger trigger-run rerun query_by_factory'] = """
    type: command
    short-summary: Query trigger runs.
    examples:
      - name: TriggerRuns_QueryByFactory
        text: |-
               az datafactory trigger trigger-run rerun query_by_factory --resource-group \\
               "exampleResourceGroup" --factory-name "exampleFactoryName"
"""

helps['datafactory trigger rerun-trigger'] = """
    type: group
    short-summary: Commands to manage datafactory trigger rerun trigger.
"""

helps['datafactory trigger rerun-trigger create'] = """
    type: command
    short-summary: Creates a rerun trigger.
    examples:
      - name: RerunTriggers_Create
        text: |-
               az datafactory trigger rerun-trigger create --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --trigger-name "exampleTrigger" --name \\
               "exampleRerunTrigger" --start-time "2018-06-16T00:39:13.8441801Z" --end-time \\
               "2018-06-16T00:55:13.8441801Z" --max-concurrency "4"
"""

helps['datafactory trigger rerun-trigger update'] = """
    type: command
    short-summary: Creates a rerun trigger.
"""

helps['datafactory trigger rerun-trigger list'] = """
    type: command
    short-summary: Lists rerun triggers by an original trigger name.
    examples:
      - name: RerunTriggers_ListByTrigger
        text: |-
               az datafactory trigger rerun-trigger list --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --trigger-name "exampleTrigger"
"""

helps['datafactory trigger rerun-trigger start'] = """
    type: command
    short-summary: Starts a trigger.
    examples:
      - name: RerunTriggers_Start
        text: |-
               az datafactory trigger rerun-trigger start --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --trigger-name "exampleTrigger" --name \\
               "exampleRerunTrigger"
"""

helps['datafactory trigger rerun-trigger stop'] = """
    type: command
    short-summary: Stops a trigger.
    examples:
      - name: RerunTriggers_Stop
        text: |-
               az datafactory trigger rerun-trigger stop --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --trigger-name "exampleTrigger" --name \\
               "exampleRerunTrigger"
"""

helps['datafactory trigger rerun-trigger cancel'] = """
    type: command
    short-summary: Cancels a trigger.
    examples:
      - name: RerunTriggers_Cancel
        text: |-
               az datafactory trigger rerun-trigger cancel --resource-group "exampleResourceGroup" \\
               --factory-name "exampleFactoryName" --trigger-name "exampleTrigger" --name \\
               "exampleRerunTrigger"
"""

helps['datafactory dataflow'] = """
    type: group
    short-summary: Commands to manage datafactory dataflow.
"""

helps['datafactory dataflow create'] = """
    type: command
    short-summary: Creates or updates a data flow.
    examples:
      - name: DataFlows_Create
        text: |-
               az datafactory dataflow create --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName" --name "exampleDataFlow" --description "Sample demo data flow to conv
               ert currencies showing usage of union, derive and conditional split transformation."
      - name: DataFlows_Update
        text: |-
               az datafactory dataflow create --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName" --name "exampleDataFlow" --description "Sample demo data flow to conv
               ert currencies showing usage of union, derive and conditional split transformation."
"""

helps['datafactory dataflow update'] = """
    type: command
    short-summary: Creates or updates a data flow.
"""

helps['datafactory dataflow delete'] = """
    type: command
    short-summary: Deletes a data flow.
    examples:
      - name: DataFlows_Delete
        text: |-
               az datafactory dataflow delete --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName" --name "exampleDataFlow"
"""

helps['datafactory dataflow show'] = """
    type: command
    short-summary: Gets a data flow.
    examples:
      - name: DataFlows_Get
        text: |-
               az datafactory dataflow show --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName" --name "exampleDataFlow"
"""

helps['datafactory dataflow list'] = """
    type: command
    short-summary: Lists data flows.
    examples:
      - name: DataFlows_ListByFactory
        text: |-
               az datafactory dataflow list --resource-group "exampleResourceGroup" --factory-name \\
               "exampleFactoryName"
"""

helps['datafactory create-data-flow-debug-session'] = """
    type: group
    short-summary: Commands to manage datafactory create data flow debug session.
"""

helps['datafactory create-data-flow-debug-session create'] = """
    type: command
    short-summary: Creates a data flow debug session.
    examples:
      - name: DataFlowDebugSession_Create
        text: |-
               az datafactory create-data-flow-debug-session create --resource-group \\
               "exampleResourceGroup" --name "exampleFactoryName" --time-to-live "60"
"""

helps['datafactory create-data-flow-debug-session query_by_factory'] = """
    type: command
    short-summary: Query all active data flow debug sessions.
    examples:
      - name: DataFlowDebugSession_QueryByFactory
        text: |-
               az datafactory create-data-flow-debug-session query_by_factory --resource-group \\
               "exampleResourceGroup" --name "exampleFactoryName"
"""

helps['datafactory create-data-flow-debug-session add_data_flow'] = """
    type: command
    short-summary: Add a data flow into debug session.
    examples:
      - name: DataFlowDebugSession_AddDataFlow
        text: |-
               az datafactory create-data-flow-debug-session add_data_flow --resource-group \\
               "exampleResourceGroup" --name "exampleFactoryName"
"""

helps['datafactory create-data-flow-debug-session delete'] = """
    type: command
    short-summary: Deletes a data flow debug session.
    examples:
      - name: DataFlowDebugSession_Delete
        text: |-
               az datafactory create-data-flow-debug-session delete --resource-group \\
               "exampleResourceGroup" --name "exampleFactoryName"
"""

helps['datafactory create-data-flow-debug-session execute_command'] = """
    type: command
    short-summary: Execute a data flow debug command.
    examples:
      - name: DataFlowDebugSession_ExecuteCommand
        text: |-
               az datafactory create-data-flow-debug-session execute_command --resource-group \\
               "exampleResourceGroup" --name "exampleFactoryName"
"""
