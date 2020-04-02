# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import ScenarioTest
from .. import try_manual
from azure.cli.testsdk import ResourceGroupPreparer


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


@try_manual
def setup(test):
    pass


# EXAMPLE: /Factories/put/Factories_CreateOrUpdate
@try_manual
def step__factories_put_factories_createorupdate(test):
    test.cmd('az datafactory factory create '
             '--location "East US" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Triggers/put/Triggers_Update
@try_manual
def step__triggers_put_triggers_update(test):
    test.cmd('az datafactory trigger create '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}" '
             '--properties "{{\\"type\\":\\"ScheduleTrigger\\",\\"description\\":\\"Example description\\",\\"pipelines'
             '\\":[{{\\"parameters\\":{{\\"OutputBlobNameList\\":[\\"exampleoutput.csv\\"]}},\\"pipelineReference\\":{{'
             '\\"type\\":\\"PipelineReference\\",\\"referenceName\\":\\"examplePipeline\\"}}}}],\\"typeProperties\\":{{'
             '\\"recurrence\\":{{\\"endTime\\":\\"2018-06-16T00:55:14.905167Z\\",\\"frequency\\":\\"Minute\\",\\"interv'
             'al\\":4,\\"startTime\\":\\"2018-06-16T00:39:14.905167Z\\",\\"timeZone\\":\\"UTC\\"}}}}}}" '
             '--trigger-name "{exampleTrigger}"',
             checks=[])


# EXAMPLE: /Triggers/put/Triggers_Create
@try_manual
def step__triggers_put_triggers_create(test):
    test.cmd('az datafactory trigger create '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}" '
             '--properties "{{\\"type\\":\\"ScheduleTrigger\\",\\"pipelines\\":[{{\\"parameters\\":{{\\"OutputBlobNameL'
             'ist\\":[\\"exampleoutput.csv\\"]}},\\"pipelineReference\\":{{\\"type\\":\\"PipelineReference\\",\\"refere'
             'nceName\\":\\"examplePipeline\\"}}}}],\\"typeProperties\\":{{\\"recurrence\\":{{\\"endTime\\":\\"2018-06-'
             '16T00:55:13.8441801Z\\",\\"frequency\\":\\"Minute\\",\\"interval\\":4,\\"startTime\\":\\"2018-06-16T00:39'
             ':13.8441801Z\\",\\"timeZone\\":\\"UTC\\"}}}}}}" '
             '--trigger-name "{exampleTrigger}"',
             checks=[])


# EXAMPLE: /DataFlows/put/DataFlows_Update
@try_manual
def step__dataflows_put_dataflows_update(test):
    test.cmd('az datafactory data-flow create '
             '--properties "{{\\"type\\":\\"MappingDataFlow\\",\\"description\\":\\"Sample demo data flow to convert cu'
             'rrencies showing usage of union, derive and conditional split transformation.\\",\\"typeProperties\\":{{'
             '\\"script\\":\\"source(output(PreviousConversionRate as double,Country as string,DateTime1 as string,Curr'
             'entConversionRate as double),allowSchemaDrift: false,validateSchema: false) ~> USDCurrency\\\\nsource(out'
             'put(PreviousConversionRate as double,Country as string,DateTime1 as string,CurrentConversionRate as doubl'
             'e),allowSchemaDrift: true,validateSchema: false) ~> CADSource\\\\nUSDCurrency, CADSource union(byName: tr'
             'ue)~> Union\\\\nUnion derive(NewCurrencyRate = round(CurrentConversionRate*1.25)) ~> NewCurrencyColumn\\'
             '\\nNewCurrencyColumn split(Country == \'USD\',Country == \'CAD\',disjoint: false) ~> ConditionalSplit1@(U'
             'SD, CAD)\\\\nConditionalSplit1@USD sink(saveMode:\'overwrite\' ) ~> USDSink\\\\nConditionalSplit1@CAD sin'
             'k(saveMode:\'overwrite\' ) ~> CADSink\\",\\"sinks\\":[{{\\"name\\":\\"USDSink\\",\\"dataset\\":{{\\"type'
             '\\":\\"DatasetReference\\",\\"referenceName\\":\\"USDOutput\\"}}}},{{\\"name\\":\\"CADSink\\",\\"dataset'
             '\\":{{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CADOutput\\"}}}}],\\"sources\\":[{{\\"name'
             '\\":\\"USDCurrency\\",\\"dataset\\":{{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CurrencyDa'
             'tasetUSD\\"}}}},{{\\"name\\":\\"CADSource\\",\\"dataset\\":{{\\"type\\":\\"DatasetReference\\",\\"referen'
             'ceName\\":\\"CurrencyDatasetCAD\\"}}}}]}}}}" '
             '--data-flow-name "{exampleDataFlow}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /DataFlows/put/DataFlows_Create
@try_manual
def step__dataflows_put_dataflows_create(test):
    test.cmd('az datafactory data-flow create '
             '--properties "{{\\"type\\":\\"MappingDataFlow\\",\\"description\\":\\"Sample demo data flow to convert cu'
             'rrencies showing usage of union, derive and conditional split transformation.\\",\\"typeProperties\\":{{'
             '\\"script\\":\\"source(output(PreviousConversionRate as double,Country as string,DateTime1 as string,Curr'
             'entConversionRate as double),allowSchemaDrift: false,validateSchema: false) ~> USDCurrency\\\\nsource(out'
             'put(PreviousConversionRate as double,Country as string,DateTime1 as string,CurrentConversionRate as doubl'
             'e),allowSchemaDrift: true,validateSchema: false) ~> CADSource\\\\nUSDCurrency, CADSource union(byName: tr'
             'ue)~> Union\\\\nUnion derive(NewCurrencyRate = round(CurrentConversionRate*1.25)) ~> NewCurrencyColumn\\'
             '\\nNewCurrencyColumn split(Country == \'USD\',Country == \'CAD\',disjoint: false) ~> ConditionalSplit1@(U'
             'SD, CAD)\\\\nConditionalSplit1@USD sink(saveMode:\'overwrite\' ) ~> USDSink\\\\nConditionalSplit1@CAD sin'
             'k(saveMode:\'overwrite\' ) ~> CADSink\\",\\"sinks\\":[{{\\"name\\":\\"USDSink\\",\\"dataset\\":{{\\"type'
             '\\":\\"DatasetReference\\",\\"referenceName\\":\\"USDOutput\\"}}}},{{\\"name\\":\\"CADSink\\",\\"dataset'
             '\\":{{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CADOutput\\"}}}}],\\"sources\\":[{{\\"name'
             '\\":\\"USDCurrency\\",\\"dataset\\":{{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CurrencyDa'
             'tasetUSD\\"}}}},{{\\"name\\":\\"CADSource\\",\\"dataset\\":{{\\"type\\":\\"DatasetReference\\",\\"referen'
             'ceName\\":\\"CurrencyDatasetCAD\\"}}}}]}}}}" '
             '--data-flow-name "{exampleDataFlow}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Pipelines/put/Pipelines_Update
@try_manual
def step__pipelines_put_pipelines_update(test):
    test.cmd('az datafactory pipeline create '
             '--factory-name "{exampleFactoryName}" '
             '--pipeline "{{\\"properties\\":{{\\"description\\":\\"Example description\\",\\"activities\\":[{{\\"name'
             '\\":\\"ExampleForeachActivity\\",\\"type\\":\\"ForEach\\",\\"typeProperties\\":{{\\"activities\\":[{{\\"n'
             'ame\\":\\"ExampleCopyActivity\\",\\"type\\":\\"Copy\\",\\"inputs\\":[{{\\"type\\":\\"DatasetReference\\",'
             '\\"parameters\\":{{\\"MyFileName\\":\\"examplecontainer.csv\\",\\"MyFolderPath\\":\\"examplecontainer\\"}'
             '},\\"referenceName\\":\\"exampleDataset\\"}}],\\"outputs\\":[{{\\"type\\":\\"DatasetReference\\",\\"param'
             'eters\\":{{\\"MyFileName\\":{{\\"type\\":\\"Expression\\",\\"value\\":\\"@item()\\"}},\\"MyFolderPath\\":'
             '\\"examplecontainer\\"}},\\"referenceName\\":\\"exampleDataset\\"}}],\\"typeProperties\\":{{\\"dataIntegr'
             'ationUnits\\":32,\\"sink\\":{{\\"type\\":\\"BlobSink\\"}},\\"source\\":{{\\"type\\":\\"BlobSource\\"}}}}}'
             '}],\\"isSequential\\":true,\\"items\\":{{\\"type\\":\\"Expression\\",\\"value\\":\\"@pipeline().parameter'
             's.OutputBlobNameList\\"}}}}}}],\\"parameters\\":{{\\"OutputBlobNameList\\":{{\\"type\\":\\"Array\\"}}}}}}'
             '}}" '
             '--pipeline-name "{examplePipeline}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Pipelines/put/Pipelines_Create
@try_manual
def step__pipelines_put_pipelines_create(test):
    test.cmd('az datafactory pipeline create '
             '--factory-name "{exampleFactoryName}" '
             '--pipeline "{{\\"properties\\":{{\\"activities\\":[{{\\"name\\":\\"ExampleForeachActivity\\",\\"type\\":'
             '\\"ForEach\\",\\"typeProperties\\":{{\\"activities\\":[{{\\"name\\":\\"ExampleCopyActivity\\",\\"type\\":'
             '\\"Copy\\",\\"inputs\\":[{{\\"type\\":\\"DatasetReference\\",\\"parameters\\":{{\\"MyFileName\\":\\"examp'
             'lecontainer.csv\\",\\"MyFolderPath\\":\\"examplecontainer\\"}},\\"referenceName\\":\\"exampleDataset\\"}}'
             '],\\"outputs\\":[{{\\"type\\":\\"DatasetReference\\",\\"parameters\\":{{\\"MyFileName\\":{{\\"type\\":\\"'
             'Expression\\",\\"value\\":\\"@item()\\"}},\\"MyFolderPath\\":\\"examplecontainer\\"}},\\"referenceName\\"'
             ':\\"exampleDataset\\"}}],\\"typeProperties\\":{{\\"dataIntegrationUnits\\":32,\\"sink\\":{{\\"type\\":\\"'
             'BlobSink\\"}},\\"source\\":{{\\"type\\":\\"BlobSource\\"}}}}}}],\\"isSequential\\":true,\\"items\\":{{\\"'
             'type\\":\\"Expression\\",\\"value\\":\\"@pipeline().parameters.OutputBlobNameList\\"}}}}}}],\\"parameters'
             '\\":{{\\"JobId\\":{{\\"type\\":\\"String\\"}},\\"OutputBlobNameList\\":{{\\"type\\":\\"Array\\"}}}},\\"ru'
             'nDimensions\\":{{\\"JobId\\":{{\\"type\\":\\"Expression\\",\\"value\\":\\"@pipeline().parameters.JobId\\"'
             '}}}},\\"variables\\":{{\\"TestVariableArray\\":{{\\"type\\":\\"Array\\"}}}}}}}}" '
             '--pipeline-name "{examplePipeline}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /IntegrationRuntimes/put/IntegrationRuntimes_Create
@try_manual
def step__integrationruntimes_put_integrationruntimes_create(test):
    test.cmd('az datafactory integration-runtime managed create '
             '--factory-name "{exampleFactoryName}" '
             '--type "SelfHosted" '
             '--description "A selfhosted integration runtime" '
             '--integration-runtime-name "{exampleIntegrationRuntime}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /IntegrationRuntimes/put/IntegrationRuntimes_Create
@try_manual
def step__integrationruntimes_put_integrationruntimes_create(test):
    test.cmd('az datafactory integration-runtime managed create '
             '--factory-name "{exampleFactoryName}" '
             '--type "SelfHosted" '
             '--description "A selfhosted integration runtime" '
             '--integration-runtime-name "{exampleIntegrationRuntime}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Pipelines/get/Pipelines_Get
@try_manual
def step__pipelines_get_pipelines_get(test):
    test.cmd('az datafactory pipeline show '
             '--factory-name "{exampleFactoryName}" '
             '--pipeline-name "{examplePipeline}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /DataFlows/get/DataFlows_Get
@try_manual
def step__dataflows_get_dataflows_get(test):
    test.cmd('az datafactory data-flow show '
             '--data-flow-name "{exampleDataFlow}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Triggers/get/Triggers_Get
@try_manual
def step__triggers_get_triggers_get(test):
    test.cmd('az datafactory trigger show '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}" '
             '--trigger-name "{exampleTrigger}"',
             checks=[])


# EXAMPLE: /PipelineRuns/get/PipelineRuns_Get
@try_manual
def step__pipelineruns_get_pipelineruns_get(test):
    test.cmd('az datafactory pipeline-run show '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}" '
             '--run-id "2f7fdb90-5df1-4b8e-ac2f-064cfa58202b"',
             checks=[])


# EXAMPLE: /Factories/get/Factories_Get
@try_manual
def step__factories_get_factories_get(test):
    test.cmd('az datafactory factory show '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /IntegrationRuntimes/get/IntegrationRuntimes_ListByFactory
@try_manual
def step__integrationruntimes_get_integrationruntimes_listbyfactory(test):
    test.cmd('az datafactory integration-runtime list '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Pipelines/get/Pipelines_ListByFactory
@try_manual
def step__pipelines_get_pipelines_listbyfactory(test):
    test.cmd('az datafactory pipeline list '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /DataFlows/get/DataFlows_ListByFactory
@try_manual
def step__dataflows_get_dataflows_listbyfactory(test):
    test.cmd('az datafactory data-flow list '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Triggers/get/Triggers_ListByFactory
@try_manual
def step__triggers_get_triggers_listbyfactory(test):
    test.cmd('az datafactory trigger list '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Factories/get/Factories_ListByResourceGroup
@try_manual
def step__factories_get_factories_listbyresourcegroup(test):
    test.cmd('az datafactory factory list '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Factories/get/Factories_List
@try_manual
def step__factories_get_factories_list(test):
    test.cmd('az datafactory factory list',
             checks=[])


# EXAMPLE: /IntegrationRuntimeNodes/post/IntegrationRuntimeNodes_GetIpAddress
@try_manual
def step__integrationruntimenodes_post_integrationruntimenodes_getipaddress(test):
    test.cmd('az datafactory integration-runtime-node get-ip-address '
             '--factory-name "{exampleFactoryName}" '
             '--integration-runtime-name "{exampleIntegrationRuntime}" '
             '--node-name "Node_1" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /IntegrationRuntimes/post/IntegrationRuntimes_CreateLinkedIntegrationRuntime
@try_manual
def step__integrationruntimes_post_integrationruntimes_createlinkedintegrationruntime(test):
    test.cmd('az datafactory integration-runtime create-linked-integration-runtime '
             '--name "bfa92911-9fb6-4fbe-8f23-beae87bc1c83" '
             '--data-factory-location "West US" '
             '--data-factory-name "e9955d6d-56ea-4be3-841c-52a12c1a9981" '
             '--subscription-id "061774c7-4b5a-4159-a55b-365581830283" '
             '--factory-name "{exampleFactoryName}" '
             '--integration-runtime-name "{exampleIntegrationRuntime}" '
             '--resource-group "{rg}" '
             '--subscription-id "12345678-1234-1234-1234-12345678abc"',
             checks=[])


# EXAMPLE: /IntegrationRuntimeObjectMetadata/post/IntegrationRuntimeObjectMetadata_Refresh
@try_manual
def step__integrationruntimeobjectmetadata_post_integrationruntimeobjectmetadata_refresh(test):
    test.cmd('az datafactory integration-runtime-object-metadata refresh '
             '--factory-name "{exampleFactoryName}" '
             '--integration-runtime-name "{IntegrationRuntimes_2}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /IntegrationRuntimes/post/IntegrationRuntimes_GetConnectionInfo
@try_manual
def step__integrationruntimes_post_integrationruntimes_getconnectioninfo(test):
    test.cmd('az datafactory integration-runtime get-connection-info '
             '--factory-name "{exampleFactoryName}" '
             '--integration-runtime-name "{exampleIntegrationRuntime}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /IntegrationRuntimes/post/IntegrationRuntimes_RegenerateAuthKey
@try_manual
def step__integrationruntimes_post_integrationruntimes_regenerateauthkey(test):
    test.cmd('az datafactory integration-runtime regenerate-auth-key '
             '--factory-name "{exampleFactoryName}" '
             '--integration-runtime-name "{exampleIntegrationRuntime}" '
             '--key-name "authKey2" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /IntegrationRuntimeObjectMetadata/post/IntegrationRuntimeObjectMetadata_Get
@try_manual
def step__integrationruntimeobjectmetadata_post_integrationruntimeobjectmetadata_get(test):
    test.cmd('az datafactory integration-runtime-object-metadata get '
             '--factory-name "{exampleFactoryName}" '
             '--metadata-path "ssisFolders" '
             '--integration-runtime-name "{IntegrationRuntimes_2}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /IntegrationRuntimeNodes/patch/IntegrationRuntimeNodes_Update
@try_manual
def step__integrationruntimenodes_patch_integrationruntimenodes_update(test):
    test.cmd('az datafactory integration-runtime-node update '
             '--factory-name "{exampleFactoryName}" '
             '--integration-runtime-name "{exampleIntegrationRuntime}" '
             '--node-name "Node_1" '
             '--resource-group "{rg}" '
             '--concurrent-jobs-limit 2',
             checks=[])


# EXAMPLE: /IntegrationRuntimes/post/IntegrationRuntimes_SyncCredentials
@try_manual
def step__integrationruntimes_post_integrationruntimes_synccredentials(test):
    test.cmd('az datafactory integration-runtime sync-credentials '
             '--factory-name "{exampleFactoryName}" '
             '--integration-runtime-name "{exampleIntegrationRuntime}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /IntegrationRuntimes/post/IntegrationRuntimes_GetMonitoringData
@try_manual
def step__integrationruntimes_post_integrationruntimes_getmonitoringdata(test):
    test.cmd('az datafactory integration-runtime get-monitoring-data '
             '--factory-name "{exampleFactoryName}" '
             '--integration-runtime-name "{exampleIntegrationRuntime}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /IntegrationRuntimes/post/IntegrationRuntimes_ListAuthKeys
@try_manual
def step__integrationruntimes_post_integrationruntimes_listauthkeys(test):
    test.cmd('az datafactory integration-runtime list-auth-key '
             '--factory-name "{exampleFactoryName}" '
             '--integration-runtime-name "{exampleIntegrationRuntime}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /IntegrationRuntimes/post/IntegrationRuntimes_Upgrade
@try_manual
def step__integrationruntimes_post_integrationruntimes_upgrade(test):
    test.cmd('az datafactory integration-runtime remove-link '
             '--factory-name "{exampleFactoryName}" '
             '--integration-runtime-name "{exampleIntegrationRuntime}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /IntegrationRuntimes/post/IntegrationRuntimes_GetStatus
@try_manual
def step__integrationruntimes_post_integrationruntimes_getstatus(test):
    test.cmd('az datafactory integration-runtime get-status '
             '--factory-name "{exampleFactoryName}" '
             '--integration-runtime-name "{exampleIntegrationRuntime}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /IntegrationRuntimes/post/IntegrationRuntimes_Upgrade
@try_manual
def step__integrationruntimes_post_integrationruntimes_upgrade(test):
    test.cmd('az datafactory integration-runtime remove-link '
             '--factory-name "{exampleFactoryName}" '
             '--integration-runtime-name "{exampleIntegrationRuntime}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /IntegrationRuntimes/post/IntegrationRuntimes_Start
@try_manual
def step__integrationruntimes_post_integrationruntimes_start(test):
    test.cmd('az datafactory integration-runtime start '
             '--factory-name "{exampleFactoryName}" '
             '--integration-runtime-name "{IntegrationRuntimes_3}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /IntegrationRuntimes/post/IntegrationRuntimes_Stop
@try_manual
def step__integrationruntimes_post_integrationruntimes_stop(test):
    test.cmd('az datafactory integration-runtime stop '
             '--factory-name "{exampleFactoryName}" '
             '--integration-runtime-name "{IntegrationRuntimes_3}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Triggers/post/Triggers_GetEventSubscriptionStatus
@try_manual
def step__triggers_post_triggers_geteventsubscriptionstatus(test):
    test.cmd('az datafactory trigger get-event-subscription-status '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}" '
             '--trigger-name "{exampleTrigger}"',
             checks=[])


# EXAMPLE: /TriggerRuns/post/Triggers_Rerun
@try_manual
def step__triggerruns_post_triggers_rerun(test):
    test.cmd('az datafactory trigger-run rerun '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}" '
             '--run-id "2f7fdb90-5df1-4b8e-ac2f-064cfa58202b" '
             '--trigger-name "{exampleTrigger}"',
             checks=[])


# EXAMPLE: /IntegrationRuntimeNodes/get/IntegrationRuntimeNodes_Get
@try_manual
def step__integrationruntimenodes_get_integrationruntimenodes_get(test):
    test.cmd('az datafactory integration-runtime-node show '
             '--factory-name "{exampleFactoryName}" '
             '--integration-runtime-name "{exampleIntegrationRuntime}" '
             '--node-name "Node_1" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /IntegrationRuntimes/get/IntegrationRuntimes_Get
@try_manual
def step__integrationruntimes_get_integrationruntimes_get(test):
    test.cmd('az datafactory integration-runtime show '
             '--factory-name "{exampleFactoryName}" '
             '--integration-runtime-name "{exampleIntegrationRuntime}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /IntegrationRuntimes/patch/IntegrationRuntimes_Update
@try_manual
def step__integrationruntimes_patch_integrationruntimes_update(test):
    test.cmd('az datafactory integration-runtime update '
             '--factory-name "{exampleFactoryName}" '
             '--integration-runtime-name "{exampleIntegrationRuntime}" '
             '--resource-group "{rg}" '
             '--auto-update "Off" '
             '--update-delay-offset "\\"PT3H\\""',
             checks=[])


# EXAMPLE: /Triggers/post/Triggers_UnsubscribeFromEvents
@try_manual
def step__triggers_post_triggers_unsubscribefromevents(test):
    test.cmd('az datafactory trigger unsubscribe-from-event '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}" '
             '--trigger-name "{exampleTrigger}"',
             checks=[])


# EXAMPLE: /Triggers/post/Triggers_SubscribeToEvents
@try_manual
def step__triggers_post_triggers_subscribetoevents(test):
    test.cmd('az datafactory trigger subscribe-to-event '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}" '
             '--trigger-name "{exampleTrigger}"',
             checks=[])


# EXAMPLE: /ActivityRuns/post/ActivityRuns_QueryByPipelineRun
@try_manual
def step__activityruns_post_activityruns_querybypipelinerun(test):
    test.cmd('az datafactory activity-run query-by-pipeline-run '
             '--factory-name "{exampleFactoryName}" '
             '--last-updated-after "2018-06-16T00:36:44.3345758Z" '
             '--last-updated-before "2018-06-16T00:49:48.3686473Z" '
             '--resource-group "{rg}" '
             '--run-id "2f7fdb90-5df1-4b8e-ac2f-064cfa58202b"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Create
@try_manual
def step__linkedservices_put_linkedservices_create(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/put/LinkedServices_Update
@try_manual
def step__linkedservices_put_linkedservices_update(test):
    test.cmd('az datafactory linked-service amazon-m-w-s create '
             '--factory-name "{exampleFactoryName}" '
             '--type "AzureStorage" '
             '--description "Example description" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/get/LinkedServices_Get
@try_manual
def step__linkedservices_get_linkedservices_get(test):
    test.cmd('az datafactory linked-service show '
             '--factory-name "{exampleFactoryName}" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/get/LinkedServices_ListByFactory
@try_manual
def step__linkedservices_get_linkedservices_listbyfactory(test):
    test.cmd('az datafactory linked-service list '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Pipelines/post/Pipelines_CreateRun
@try_manual
def step__pipelines_post_pipelines_createrun(test):
    test.cmd('az datafactory pipeline create-run '
             '--factory-name "{exampleFactoryName}" '
             '--parameters "{{\\"OutputBlobNameList\\":[\\"exampleoutput.csv\\"]}}" '
             '--pipeline-name "{examplePipeline}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Triggers/post/Triggers_Start
@try_manual
def step__triggers_post_triggers_start(test):
    test.cmd('az datafactory trigger start '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}" '
             '--trigger-name "{exampleTrigger}"',
             checks=[])


# EXAMPLE: /PipelineRuns/post/PipelineRuns_Cancel
@try_manual
def step__pipelineruns_post_pipelineruns_cancel(test):
    test.cmd('az datafactory pipeline-run cancel '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}" '
             '--run-id "16ac5348-ff82-4f95-a80d-638c1d47b721"',
             checks=[])


# EXAMPLE: /Triggers/post/Triggers_Stop
@try_manual
def step__triggers_post_triggers_stop(test):
    test.cmd('az datafactory trigger stop '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}" '
             '--trigger-name "{exampleTrigger}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Create
@try_manual
def step__datasets_put_datasets_create(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/put/Datasets_Update
@try_manual
def step__datasets_put_datasets_update(test):
    test.cmd('az datafactory dataset amazon-m-w-s-object create '
             '--type "AzureBlob" '
             '--description "Example description" '
             '--linked-service-name "{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ'
             'ice\\"}}" '
             '--parameters "{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"'
             '}}}}" '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Datasets/get/Datasets_ListByFactory
@try_manual
def step__datasets_get_datasets_listbyfactory(test):
    test.cmd('az datafactory dataset list '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /DataFlowDebugSession/post/DataFlowDebugSession_ExecuteCommand
@try_manual
def step__dataflowdebugsession_post_dataflowdebugsession_executecommand(test):
    test.cmd('az datafactory data-flow-debug-session execute-command '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}" '
             '--command "executePreviewQuery" '
             '--command-payload row-limits=0 stream-name="source1" '
             '--session-id "f06ed247-9d07-49b2-b05e-2cb4a2fc871e"',
             checks=[])


# EXAMPLE: /DataFlowDebugSession/post/DataFlowDebugSession_QueryByFactory
@try_manual
def step__dataflowdebugsession_post_dataflowdebugsession_querybyfactory(test):
    test.cmd('az datafactory data-flow-debug-session query-by-factory '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /DataFlowDebugSession/post/DataFlowDebugSession_AddDataFlow
@try_manual
def step__dataflowdebugsession_post_dataflowdebugsession_adddataflow(test):
    test.cmd('az datafactory data-flow-debug-session add-data-flow '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}" '
             '--data-flow "{{\\"name\\":\\"dataflow1\\",\\"properties\\":{{\\"type\\":\\"MappingDataFlow\\",\\"typeProp'
             'erties\\":{{\\"script\\":\\"\\\\n\\\\nsource(output(\\\\n\\\\t\\\\tColumn_1 as string\\\\n\\\\t),\\\\n\\'
             '\\tallowSchemaDrift: true,\\\\n\\\\tvalidateSchema: false) ~> source1\\",\\"sinks\\":[],\\"sources\\":[{{'
             '\\"name\\":\\"source1\\",\\"dataset\\":{{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"Delimit'
             'edText2\\"}}}}],\\"transformations\\":[]}}}}}}" '
             '--datasets "[{{\\"name\\":\\"dataset1\\",\\"properties\\":{{\\"type\\":\\"DelimitedText\\",\\"schema\\":['
             '{{\\"type\\":\\"String\\"}}],\\"annotations\\":[],\\"linkedServiceName\\":{{\\"type\\":\\"LinkedServiceRe'
             'ference\\",\\"referenceName\\":\\"linkedService5\\"}},\\"typeProperties\\":{{\\"columnDelimiter\\":\\",\\'
             '",\\"escapeChar\\":\\"\\\\\\\\\\",\\"firstRowAsHeader\\":true,\\"location\\":{{\\"type\\":\\"AzureBlobSto'
             'rageLocation\\",\\"container\\":\\"dataflow-sample-data\\",\\"fileName\\":\\"Ansiencoding.csv\\"}},\\"quo'
             'teChar\\":\\"\\\\\\"\\"}}}}}}]" '
             '--debug-settings "{{\\"datasetParameters\\":{{\\"Movies\\":{{\\"path\\":\\"abc\\"}},\\"Output\\":{{\\"tim'
             'e\\":\\"def\\"}}}},\\"parameters\\":{{\\"sourcePath\\":\\"Toy\\"}},\\"sourceSettings\\":[{{\\"rowLimit\\"'
             ':1000,\\"sourceName\\":\\"source1\\"}},{{\\"rowLimit\\":222,\\"sourceName\\":\\"source2\\"}}]}}" '
             '--linked-services "[{{\\"name\\":\\"linkedService1\\",\\"properties\\":{{\\"type\\":\\"AzureBlobStorage\\'
             '",\\"annotations\\":[],\\"typeProperties\\":{{\\"connectionString\\":\\"DefaultEndpointsProtocol=https;Ac'
             'countName=<storageName>;EndpointSuffix=core.windows.net;\\",\\"encryptedCredential\\":\\"<credential>\\"}'
             '}}}}}]" '
             '--session-id "f06ed247-9d07-49b2-b05e-2cb4a2fc871e"',
             checks=[])


# EXAMPLE: /DataFlowDebugSession/post/DataFlowDebugSession_Create
@try_manual
def step__dataflowdebugsession_post_dataflowdebugsession_create(test):
    test.cmd('az datafactory data-flow-debug-session create '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}" '
             '--integration-runtime "{{\\"name\\":\\"ir1\\",\\"properties\\":{{\\"type\\":\\"Managed\\",\\"typeProperti'
             'es\\":{{\\"computeProperties\\":{{\\"dataFlowProperties\\":{{\\"computeType\\":\\"General\\",\\"coreCount'
             '\\":48,\\"timeToLive\\":10}},\\"location\\":\\"AutoResolve\\"}}}}}}}}" '
             '--time-to-live 60',
             checks=[])


# EXAMPLE: /Datasets/get/Datasets_Get
@try_manual
def step__datasets_get_datasets_get(test):
    test.cmd('az datafactory dataset show '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Factories/post/Factories_GetGitHubAccessToken
@try_manual
def step__factories_post_factories_getgithubaccesstoken(test):
    test.cmd('az datafactory factory get-git-hub-access-token '
             '--factory-name "{exampleFactoryName}" '
             '--git-hub-access-code "some" '
             '--git-hub-access-token-base-url "some" '
             '--git-hub-client-id "some" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Factories/post/Factories_GetDataPlaneAccess
@try_manual
def step__factories_post_factories_getdataplaneaccess(test):
    test.cmd('az datafactory factory get-data-plane-access '
             '--factory-name "{exampleFactoryName}" '
             '--access-resource-path "" '
             '--expire-time "2018-11-10T09:46:20.2659347Z" '
             '--permissions "r" '
             '--profile-name "DefaultProfile" '
             '--start-time "2018-11-10T02:46:20.2659347Z" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /PipelineRuns/post/PipelineRuns_QueryByFactory
@try_manual
def step__pipelineruns_post_pipelineruns_querybyfactory(test):
    test.cmd('az datafactory pipeline-run query-by-factory '
             '--factory-name "{exampleFactoryName}" '
             '--filters operand="PipelineName" operator="Equals" values="examplePipeline" '
             '--last-updated-after "2018-06-16T00:36:44.3345758Z" '
             '--last-updated-before "2018-06-16T00:49:48.3686473Z" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /TriggerRuns/post/TriggerRuns_QueryByFactory
@try_manual
def step__triggerruns_post_triggerruns_querybyfactory(test):
    test.cmd('az datafactory trigger-run query-by-factory '
             '--factory-name "{exampleFactoryName}" '
             '--filters operand="TriggerName" operator="Equals" values="exampleTrigger" '
             '--last-updated-after "2018-06-16T00:36:44.3345758Z" '
             '--last-updated-before "2018-06-16T00:49:48.3686473Z" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /ExposureControl/post/ExposureControl_GetFeatureValueByFactory
@try_manual
def step__exposurecontrol_post_exposurecontrol_getfeaturevaluebyfactory(test):
    test.cmd('az datafactory exposure-control get-feature-value-by-factory '
             '--feature-name "ADFIntegrationRuntimeSharingRbac" '
             '--feature-type "Feature" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Triggers/post/Triggers_QueryByFactory
@try_manual
def step__triggers_post_triggers_querybyfactory(test):
    test.cmd('az datafactory trigger query-by-factory '
             '--factory-name "{exampleFactoryName}" '
             '--parent-trigger-name "exampleTrigger" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Factories/patch/Factories_Update
@try_manual
def step__factories_patch_factories_update(test):
    test.cmd('az datafactory factory update '
             '--factory-name "{exampleFactoryName}" '
             '--tags exampleTag="exampleValue" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Factories/post/Factories_ConfigureFactoryRepo
@try_manual
def step__factories_post_factories_configurefactoryrepo(test):
    test.cmd('az datafactory factory configure-factory-repo '
             '--factory-resource-id "/subscriptions/{subscription_id}/resourceGroups/{rg}/providers/Microsoft.DataFacto'
             'ry/factories/{exampleFactoryName}" '
             '--repo-configuration "{{\\"type\\":\\"FactoryVSTSConfiguration\\",\\"accountName\\":\\"ADF\\",\\"collabor'
             'ationBranch\\":\\"master\\",\\"lastCommitId\\":\\"\\",\\"projectName\\":\\"project\\",\\"repositoryName\\'
             '":\\"repo\\",\\"rootFolder\\":\\"/\\",\\"tenantId\\":\\"\\"}}" '
             '--location-id "East US"',
             checks=[])


# EXAMPLE: /ExposureControl/post/ExposureControl_GetFeatureValue
@try_manual
def step__exposurecontrol_post_exposurecontrol_getfeaturevalue(test):
    test.cmd('az datafactory exposure-control get-feature-value '
             '--feature-name "ADFIntegrationRuntimeSharingRbac" '
             '--feature-type "Feature" '
             '--location-id "WestEurope"',
             checks=[])


# EXAMPLE: /IntegrationRuntimeNodes/delete/IntegrationRuntimesNodes_Delete
@try_manual
def step__integrationruntimenodes_delete_integrationruntimesnodes_delete(test):
    test.cmd('az datafactory integration-runtime-node delete '
             '--factory-name "{exampleFactoryName}" '
             '--integration-runtime-name "{exampleIntegrationRuntime}" '
             '--node-name "Node_1" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /IntegrationRuntimes/delete/IntegrationRuntimes_Delete
@try_manual
def step__integrationruntimes_delete_integrationruntimes_delete(test):
    test.cmd('az datafactory integration-runtime delete '
             '--factory-name "{exampleFactoryName}" '
             '--integration-runtime-name "{exampleIntegrationRuntime}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /DataFlowDebugSession/post/DataFlowDebugSession_Delete
@try_manual
def step__dataflowdebugsession_post_dataflowdebugsession_delete(test):
    test.cmd('az datafactory data-flow-debug-session delete '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}" '
             '--session-id "91fb57e0-8292-47be-89ff-c8f2d2bb2a7e"',
             checks=[])


# EXAMPLE: /Datasets/delete/Datasets_Delete
@try_manual
def step__datasets_delete_datasets_delete(test):
    test.cmd('az datafactory dataset delete '
             '--dataset-name "{exampleDataset}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Pipelines/delete/Pipelines_Delete
@try_manual
def step__pipelines_delete_pipelines_delete(test):
    test.cmd('az datafactory pipeline delete '
             '--factory-name "{exampleFactoryName}" '
             '--pipeline-name "{examplePipeline}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /DataFlows/delete/DataFlows_Delete
@try_manual
def step__dataflows_delete_dataflows_delete(test):
    test.cmd('az datafactory data-flow delete '
             '--data-flow-name "{exampleDataFlow}" '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /LinkedServices/delete/LinkedServices_Delete
@try_manual
def step__linkedservices_delete_linkedservices_delete(test):
    test.cmd('az datafactory linked-service delete '
             '--factory-name "{exampleFactoryName}" '
             '--linked-service-name "{exampleLinkedService}" '
             '--resource-group "{rg}"',
             checks=[])


# EXAMPLE: /Triggers/delete/Triggers_Delete
@try_manual
def step__triggers_delete_triggers_delete(test):
    test.cmd('az datafactory trigger delete '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}" '
             '--trigger-name "{exampleTrigger}"',
             checks=[])


# EXAMPLE: /Factories/delete/Factories_Delete
@try_manual
def step__factories_delete_factories_delete(test):
    test.cmd('az datafactory factory delete '
             '--factory-name "{exampleFactoryName}" '
             '--resource-group "{rg}"',
             checks=[])


@try_manual
def cleanup(test):
    pass


class DataFactoryManagementClientScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_datafactory_exampleResourceGroup'[:9], key='rg')
    def test_datafactory(self, resource_group):

        self.kwargs.update({
            'subscription_id': self.get_subscription_id()
        })

        self.kwargs.update({
            'exampleFactoryName': self.create_random_name(prefix='cli_test_factories'[:9], length=24),
            'exampleIntegrationRuntime': self.create_random_name(prefix='cli_test_integration_runtimes'[:9],
                                                                 length=24),
            'IntegrationRuntimes_2': 'IntegrationRuntimes_2',
            'IntegrationRuntimes_3': 'IntegrationRuntimes_3',
            'exampleLinkedService': self.create_random_name(prefix='cli_test_linked_services'[:9], length=24),
            'exampleDataset': self.create_random_name(prefix='cli_test_datasets'[:9], length=24),
            'examplePipeline': self.create_random_name(prefix='cli_test_pipelines'[:9], length=24),
            'exampleTrigger': self.create_random_name(prefix='cli_test_triggers'[:9], length=24),
            'exampleDataFlow': self.create_random_name(prefix='cli_test_data_flows'[:9], length=24),
        })

        setup(self)
        step__factories_put_factories_createorupdate(self)
        step__triggers_put_triggers_update(self)
        step__triggers_put_triggers_create(self)
        step__dataflows_put_dataflows_update(self)
        step__dataflows_put_dataflows_create(self)
        step__pipelines_put_pipelines_update(self)
        step__pipelines_put_pipelines_create(self)
        step__linkedservices_put_linkedservices_create(self)
        step__integrationruntimes_put_integrationruntimes_create(self)
        step__integrationruntimes_put_integrationruntimes_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__pipelines_get_pipelines_get(self)
        step__dataflows_get_dataflows_get(self)
        step__linkedservices_put_linkedservices_create(self)
        step__triggers_get_triggers_get(self)
        step__pipelineruns_get_pipelineruns_get(self)
        step__factories_get_factories_get(self)
        step__integrationruntimes_get_integrationruntimes_listbyfactory(self)
        step__linkedservices_put_linkedservices_update(self)
        step__pipelines_get_pipelines_listbyfactory(self)
        step__dataflows_get_dataflows_listbyfactory(self)
        step__linkedservices_put_linkedservices_create(self)
        step__triggers_get_triggers_listbyfactory(self)
        step__factories_get_factories_listbyresourcegroup(self)
        step__factories_get_factories_list(self)
        step__integrationruntimenodes_post_integrationruntimenodes_getipaddress(self)
        step__integrationruntimes_post_integrationruntimes_createlinkedintegrationruntime(self)
        step__integrationruntimeobjectmetadata_post_integrationruntimeobjectmetadata_refresh(self)
        step__integrationruntimes_post_integrationruntimes_getconnectioninfo(self)
        step__integrationruntimes_post_integrationruntimes_regenerateauthkey(self)
        step__integrationruntimeobjectmetadata_post_integrationruntimeobjectmetadata_get(self)
        step__integrationruntimenodes_patch_integrationruntimenodes_update(self)
        step__integrationruntimes_post_integrationruntimes_synccredentials(self)
        step__integrationruntimes_post_integrationruntimes_getmonitoringdata(self)
        step__integrationruntimes_post_integrationruntimes_listauthkeys(self)
        step__integrationruntimes_post_integrationruntimes_upgrade(self)
        step__integrationruntimes_post_integrationruntimes_getstatus(self)
        step__integrationruntimes_post_integrationruntimes_upgrade(self)
        step__integrationruntimes_post_integrationruntimes_start(self)
        step__integrationruntimes_post_integrationruntimes_stop(self)
        step__triggers_post_triggers_geteventsubscriptionstatus(self)
        step__triggerruns_post_triggers_rerun(self)
        step__integrationruntimenodes_get_integrationruntimenodes_get(self)
        step__integrationruntimes_get_integrationruntimes_get(self)
        step__integrationruntimes_patch_integrationruntimes_update(self)
        step__triggers_post_triggers_unsubscribefromevents(self)
        step__triggers_post_triggers_subscribetoevents(self)
        step__activityruns_post_activityruns_querybypipelinerun(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__linkedservices_put_linkedservices_create(self)
        step__linkedservices_put_linkedservices_update(self)
        step__datasets_put_datasets_create(self)
        step__linkedservices_get_linkedservices_get(self)
        step__datasets_put_datasets_update(self)
        step__linkedservices_get_linkedservices_listbyfactory(self)
        step__datasets_put_datasets_create(self)
        step__pipelines_post_pipelines_createrun(self)
        step__triggers_post_triggers_start(self)
        step__pipelineruns_post_pipelineruns_cancel(self)
        step__triggers_post_triggers_stop(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_put_datasets_create(self)
        step__datasets_put_datasets_update(self)
        step__datasets_get_datasets_listbyfactory(self)
        step__dataflowdebugsession_post_dataflowdebugsession_executecommand(self)
        step__dataflowdebugsession_post_dataflowdebugsession_querybyfactory(self)
        step__dataflowdebugsession_post_dataflowdebugsession_adddataflow(self)
        step__dataflowdebugsession_post_dataflowdebugsession_create(self)
        step__datasets_get_datasets_get(self)
        step__factories_post_factories_getgithubaccesstoken(self)
        step__factories_post_factories_getdataplaneaccess(self)
        step__pipelineruns_post_pipelineruns_querybyfactory(self)
        step__triggerruns_post_triggerruns_querybyfactory(self)
        step__exposurecontrol_post_exposurecontrol_getfeaturevaluebyfactory(self)
        step__triggers_post_triggers_querybyfactory(self)
        step__factories_patch_factories_update(self)
        step__factories_post_factories_configurefactoryrepo(self)
        step__exposurecontrol_post_exposurecontrol_getfeaturevalue(self)
        step__integrationruntimenodes_delete_integrationruntimesnodes_delete(self)
        step__integrationruntimes_delete_integrationruntimes_delete(self)
        step__dataflowdebugsession_post_dataflowdebugsession_delete(self)
        step__datasets_delete_datasets_delete(self)
        step__pipelines_delete_pipelines_delete(self)
        step__dataflows_delete_dataflows_delete(self)
        step__linkedservices_delete_linkedservices_delete(self)
        step__triggers_delete_triggers_delete(self)
        step__factories_delete_factories_delete(self)
        cleanup(self)
