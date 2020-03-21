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


class DataFactoryManagementClientScenarioTest(ScenarioTest):

    def current_subscription(self):
        subs = self.cmd('az account show').get_output_in_json()
        return subs['id']

    @ResourceGroupPreparer(name_prefix='cli_test_datafactory_exampleResourceGroup'[:9], key='rg')
    def test_datafactory(self, resource_group):

        self.kwargs.update({
            'subscription_id': self.current_subscription()
        })

        self.kwargs.update({
            'exampleFactoryName': self.create_random_name(prefix='cli_test_factories'[:9], length=24),
            'exampleIntegrationRuntime': self.create_random_name(prefix='cli_test_integration_runtimes'[:9],
                                                                 length=24),
            'IntegrationRuntimes_2': self.create_random_name(prefix='cli_test_integration_runtimes'[:9], length=24),
            'IntegrationRuntimes_3': self.create_random_name(prefix='cli_test_integration_runtimes'[:9], length=24),
            'exampleLinkedService': self.create_random_name(prefix='cli_test_linked_services'[:9], length=24),
            'exampleDataset': self.create_random_name(prefix='cli_test_datasets'[:9], length=24),
            'examplePipeline': self.create_random_name(prefix='cli_test_pipelines'[:9], length=24),
            'exampleTrigger': self.create_random_name(prefix='cli_test_triggers'[:9], length=24),
            'exampleDataFlow': self.create_random_name(prefix='cli_test_data_flows'[:9], length=24),
        })

        # EXAMPLE: Factories/resource-group-name/Factories_CreateOrUpdate
        self.cmd('az datafactory factory create '
                 '--location "East US" '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Triggers/properties/Triggers_Update
        self.cmd('az datafactory trigger create '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}" '
                 '--properties "{{\\"type\\":\\"ScheduleTrigger\\",\\"description\\":\\"Example description\\",\\"pipel'
                 'ines\\":[{{\\"parameters\\":{{\\"OutputBlobNameList\\":[\\"exampleoutput.csv\\"]}},\\"pipelineReferen'
                 'ce\\":{{\\"type\\":\\"PipelineReference\\",\\"referenceName\\":\\"examplePipeline\\"}}}}],\\"typeProp'
                 'erties\\":{{\\"recurrence\\":{{\\"endTime\\":\\"2018-06-16T00:55:14.905167Z\\",\\"frequency\\":\\"Min'
                 'ute\\",\\"interval\\":4,\\"startTime\\":\\"2018-06-16T00:39:14.905167Z\\",\\"timeZone\\":\\"UTC\\"}}}'
                 '}}}" '
                 '--trigger-name "{exampleTrigger}"',
                 checks=[])

        # EXAMPLE: Triggers/resource-group-name/Triggers_Create
        self.cmd('az datafactory trigger create '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}" '
                 '--properties "{{\\"type\\":\\"ScheduleTrigger\\",\\"pipelines\\":[{{\\"parameters\\":{{\\"OutputBlobN'
                 'ameList\\":[\\"exampleoutput.csv\\"]}},\\"pipelineReference\\":{{\\"type\\":\\"PipelineReference\\",\'
                 '\"referenceName\\":\\"examplePipeline\\"}}}}],\\"typeProperties\\":{{\\"recurrence\\":{{\\"endTime\\"'
                 ':\\"2018-06-16T00:55:13.8441801Z\\",\\"frequency\\":\\"Minute\\",\\"interval\\":4,\\"startTime\\":\\"'
                 '2018-06-16T00:39:13.8441801Z\\",\\"timeZone\\":\\"UTC\\"}}}}}}" '
                 '--trigger-name "{exampleTrigger}"',
                 checks=[])

        # EXAMPLE: Datasets/properties/Datasets_Update
        self.cmd('az datafactory dataset create '
                 '--properties "{{\\"type\\":\\"AzureBlob\\",\\"description\\":\\"Example description\\",\\"linkedServi'
                 'ceName\\":{{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}},'
                 '\\"parameters\\":{{\\"MyFileName\\":{{\\"type\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"St'
                 'ring\\"}}}},\\"typeProperties\\":{{\\"format\\":{{\\"type\\":\\"TextFormat\\"}},\\"fileName\\":{{\\"t'
                 'ype\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFileName\\"}},\\"folderPath\\":{{\\"type\\":\\"Ex'
                 'pression\\",\\"value\\":\\"@dataset().MyFolderPath\\"}}}}}}" '
                 '--dataset-name "{exampleDataset}" '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Datasets/resource-group-name/Datasets_Create
        self.cmd('az datafactory dataset create '
                 '--properties "{{\\"type\\":\\"AzureBlob\\",\\"linkedServiceName\\":{{\\"type\\":\\"LinkedServiceRefer'
                 'ence\\",\\"referenceName\\":\\"exampleLinkedService\\"}},\\"parameters\\":{{\\"MyFileName\\":{{\\"typ'
                 'e\\":\\"String\\"}},\\"MyFolderPath\\":{{\\"type\\":\\"String\\"}}}},\\"typeProperties\\":{{\\"format'
                 '\\":{{\\"type\\":\\"TextFormat\\"}},\\"fileName\\":{{\\"type\\":\\"Expression\\",\\"value\\":\\"@data'
                 'set().MyFileName\\"}},\\"folderPath\\":{{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFold'
                 'erPath\\"}}}}}}" '
                 '--dataset-name "{exampleDataset}" '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: DataFlows/properties/DataFlows_Update
        self.cmd('az datafactory data-flow create '
                 '--properties "{{\\"type\\":\\"MappingDataFlow\\",\\"description\\":\\"Sample demo data flow to conver'
                 't currencies showing usage of union, derive and conditional split transformation.\\",\\"typePropertie'
                 's\\":{{\\"script\\":\\"source(output(PreviousConversionRate as double,Country as string,DateTime1 as '
                 'string,CurrentConversionRate as double),allowSchemaDrift: false,validateSchema: false) ~> USDCurrency'
                 '\\\\nsource(output(PreviousConversionRate as double,Country as string,DateTime1 as string,CurrentConv'
                 'ersionRate as double),allowSchemaDrift: true,validateSchema: false) ~> CADSource\\\\nUSDCurrency, CAD'
                 'Source union(byName: true)~> Union\\\\nUnion derive(NewCurrencyRate = round(CurrentConversionRate*1.2'
                 '5)) ~> NewCurrencyColumn\\\\nNewCurrencyColumn split(Country == \'USD\',Country == \'CAD\',disjoint: '
                 'false) ~> ConditionalSplit1@(USD, CAD)\\\\nConditionalSplit1@USD sink(saveMode:\'overwrite\' ) ~> USD'
                 'Sink\\\\nConditionalSplit1@CAD sink(saveMode:\'overwrite\' ) ~> CADSink\\",\\"sinks\\":[{{\\"name\\":'
                 '\\"USDSink\\",\\"dataset\\":{{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"USDOutput\\"}}'
                 '}},{{\\"name\\":\\"CADSink\\",\\"dataset\\":{{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\'
                 '\"CADOutput\\"}}}}],\\"sources\\":[{{\\"name\\":\\"USDCurrency\\",\\"dataset\\":{{\\"type\\":\\"Datas'
                 'etReference\\",\\"referenceName\\":\\"CurrencyDatasetUSD\\"}}}},{{\\"name\\":\\"CADSource\\",\\"datas'
                 'et\\":{{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CurrencyDatasetCAD\\"}}}}]}}}}" '
                 '--data-flow-name "{exampleDataFlow}" '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: DataFlows/resource-group-name/DataFlows_Create
        self.cmd('az datafactory data-flow create '
                 '--properties "{{\\"type\\":\\"MappingDataFlow\\",\\"description\\":\\"Sample demo data flow to conver'
                 't currencies showing usage of union, derive and conditional split transformation.\\",\\"typePropertie'
                 's\\":{{\\"script\\":\\"source(output(PreviousConversionRate as double,Country as string,DateTime1 as '
                 'string,CurrentConversionRate as double),allowSchemaDrift: false,validateSchema: false) ~> USDCurrency'
                 '\\\\nsource(output(PreviousConversionRate as double,Country as string,DateTime1 as string,CurrentConv'
                 'ersionRate as double),allowSchemaDrift: true,validateSchema: false) ~> CADSource\\\\nUSDCurrency, CAD'
                 'Source union(byName: true)~> Union\\\\nUnion derive(NewCurrencyRate = round(CurrentConversionRate*1.2'
                 '5)) ~> NewCurrencyColumn\\\\nNewCurrencyColumn split(Country == \'USD\',Country == \'CAD\',disjoint: '
                 'false) ~> ConditionalSplit1@(USD, CAD)\\\\nConditionalSplit1@USD sink(saveMode:\'overwrite\' ) ~> USD'
                 'Sink\\\\nConditionalSplit1@CAD sink(saveMode:\'overwrite\' ) ~> CADSink\\",\\"sinks\\":[{{\\"name\\":'
                 '\\"USDSink\\",\\"dataset\\":{{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"USDOutput\\"}}'
                 '}},{{\\"name\\":\\"CADSink\\",\\"dataset\\":{{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\'
                 '\"CADOutput\\"}}}}],\\"sources\\":[{{\\"name\\":\\"USDCurrency\\",\\"dataset\\":{{\\"type\\":\\"Datas'
                 'etReference\\",\\"referenceName\\":\\"CurrencyDatasetUSD\\"}}}},{{\\"name\\":\\"CADSource\\",\\"datas'
                 'et\\":{{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CurrencyDatasetCAD\\"}}}}]}}}}" '
                 '--data-flow-name "{exampleDataFlow}" '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Pipelines/folder/Pipelines_Update
        self.cmd('az datafactory pipeline create '
                 '--factory-name "{exampleFactoryName}" '
                 '--properties-description "Example description" '
                 '--properties-activities "[{{\\"name\\":\\"ExampleForeachActivity\\",\\"type\\":\\"ForEach\\",\\"typeP'
                 'roperties\\":{{\\"activities\\":[{{\\"name\\":\\"ExampleCopyActivity\\",\\"type\\":\\"Copy\\",\\"inpu'
                 'ts\\":[{{\\"type\\":\\"DatasetReference\\",\\"parameters\\":{{\\"MyFileName\\":\\"examplecontainer.cs'
                 'v\\",\\"MyFolderPath\\":\\"examplecontainer\\"}},\\"referenceName\\":\\"exampleDataset\\"}}],\\"outpu'
                 'ts\\":[{{\\"type\\":\\"DatasetReference\\",\\"parameters\\":{{\\"MyFileName\\":{{\\"type\\":\\"Expres'
                 'sion\\",\\"value\\":\\"@item()\\"}},\\"MyFolderPath\\":\\"examplecontainer\\"}},\\"referenceName\\":\'
                 '\"exampleDataset\\"}}],\\"typeProperties\\":{{\\"dataIntegrationUnits\\":32,\\"sink\\":{{\\"type\\":\'
                 '\"BlobSink\\"}},\\"source\\":{{\\"type\\":\\"BlobSource\\"}}}}}}],\\"isSequential\\":true,\\"items\\"'
                 ':{{\\"type\\":\\"Expression\\",\\"value\\":\\"@pipeline().parameters.OutputBlobNameList\\"}}}}}}]" '
                 '--properties-parameters "{{\\"OutputBlobNameList\\":{{\\"type\\":\\"Array\\"}}}}" '
                 '--pipeline-name "{examplePipeline}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Pipelines/resource-group-name/Pipelines_Create
        self.cmd('az datafactory pipeline create '
                 '--factory-name "{exampleFactoryName}" '
                 '--properties-activities "[{{\\"name\\":\\"ExampleForeachActivity\\",\\"type\\":\\"ForEach\\",\\"typeP'
                 'roperties\\":{{\\"activities\\":[{{\\"name\\":\\"ExampleCopyActivity\\",\\"type\\":\\"Copy\\",\\"inpu'
                 'ts\\":[{{\\"type\\":\\"DatasetReference\\",\\"parameters\\":{{\\"MyFileName\\":\\"examplecontainer.cs'
                 'v\\",\\"MyFolderPath\\":\\"examplecontainer\\"}},\\"referenceName\\":\\"exampleDataset\\"}}],\\"outpu'
                 'ts\\":[{{\\"type\\":\\"DatasetReference\\",\\"parameters\\":{{\\"MyFileName\\":{{\\"type\\":\\"Expres'
                 'sion\\",\\"value\\":\\"@item()\\"}},\\"MyFolderPath\\":\\"examplecontainer\\"}},\\"referenceName\\":\'
                 '\"exampleDataset\\"}}],\\"typeProperties\\":{{\\"dataIntegrationUnits\\":32,\\"sink\\":{{\\"type\\":\'
                 '\"BlobSink\\"}},\\"source\\":{{\\"type\\":\\"BlobSource\\"}}}}}}],\\"isSequential\\":true,\\"items\\"'
                 ':{{\\"type\\":\\"Expression\\",\\"value\\":\\"@pipeline().parameters.OutputBlobNameList\\"}}}}}}]" '
                 '--properties-parameters "{{\\"JobId\\":{{\\"type\\":\\"String\\"}},\\"OutputBlobNameList\\":{{\\"type'
                 '\\":\\"Array\\"}}}}" '
                 '--properties-run-dimensions JobId={"type":"Expression","value":"@pipeline().parameters.JobId"} '
                 '--properties-variables "{{\\"TestVariableArray\\":{{\\"type\\":\\"Array\\"}}}}" '
                 '--pipeline-name "{examplePipeline}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: LinkedServices/properties/LinkedServices_Update
        self.cmd('az datafactory linked-service create '
                 '--factory-name "{exampleFactoryName}" '
                 '--properties "{{\\"type\\":\\"AzureStorage\\",\\"description\\":\\"Example description\\",\\"typeProp'
                 'erties\\":{{\\"connectionString\\":{{\\"type\\":\\"SecureString\\",\\"value\\":\\"DefaultEndpointsPro'
                 'tocol=https;AccountName=examplestorageaccount;AccountKey=<storage key>\\"}}}}}}" '
                 '--linked-service-name "{exampleLinkedService}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: LinkedServices/resource-group-name/LinkedServices_Create
        self.cmd('az datafactory linked-service create '
                 '--factory-name "{exampleFactoryName}" '
                 '--properties "{{\\"type\\":\\"AzureStorage\\",\\"typeProperties\\":{{\\"connectionString\\":{{\\"type'
                 '\\":\\"SecureString\\",\\"value\\":\\"DefaultEndpointsProtocol=https;AccountName=examplestorageaccoun'
                 't;AccountKey=<storage key>\\"}}}}}}" '
                 '--linked-service-name "{exampleLinkedService}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: DataFlowDebugSession/resource-group-name/DataFlowDebugSession_Create
        self.cmd('az datafactory data-flow-debug-session create '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}" '
                 '--integration-runtime "{{\\"name\\":\\"ir1\\",\\"properties\\":{{\\"type\\":\\"Managed\\",\\"typeProp'
                 'erties\\":{{\\"computeProperties\\":{{\\"dataFlowProperties\\":{{\\"computeType\\":\\"General\\",\\"c'
                 'oreCount\\":48,\\"timeToLive\\":10}},\\"location\\":\\"AutoResolve\\"}}}}}}}}" '
                 '--time-to-live 60',
                 checks=[])

        # EXAMPLE: IntegrationRuntimes/resource-group-name/IntegrationRuntimes_Create
        self.cmd('az datafactory integration-runtime create '
                 '--factory-name "{exampleFactoryName}" '
                 '--properties "{{\\"type\\":\\"SelfHosted\\",\\"description\\":\\"A selfhosted integration runtime\\"}'
                 '}" '
                 '--integration-runtime-name "{exampleIntegrationRuntime}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: IntegrationRuntimeNodes/resource-group-name/IntegrationRuntimeNodes_Get
        self.cmd('az datafactory integration-runtime-node show '
                 '--factory-name "{exampleFactoryName}" '
                 '--integration-runtime-name "{exampleIntegrationRuntime}" '
                 '--node-name "Node_1" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: IntegrationRuntimes/resource-group-name/IntegrationRuntimes_Get
        self.cmd('az datafactory integration-runtime show '
                 '--factory-name "{exampleFactoryName}" '
                 '--integration-runtime-name "{exampleIntegrationRuntime}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: LinkedServices/resource-group-name/LinkedServices_Get
        self.cmd('az datafactory linked-service show '
                 '--factory-name "{exampleFactoryName}" '
                 '--linked-service-name "{exampleLinkedService}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Pipelines/resource-group-name/Pipelines_Get
        self.cmd('az datafactory pipeline show '
                 '--factory-name "{exampleFactoryName}" '
                 '--pipeline-name "{examplePipeline}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: DataFlows/resource-group-name/DataFlows_Get
        self.cmd('az datafactory data-flow show '
                 '--data-flow-name "{exampleDataFlow}" '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Datasets/resource-group-name/Datasets_Get
        self.cmd('az datafactory dataset show '
                 '--dataset-name "{exampleDataset}" '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Triggers/resource-group-name/Triggers_Get
        self.cmd('az datafactory trigger show '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}" '
                 '--trigger-name "{exampleTrigger}"',
                 checks=[])

        # EXAMPLE: PipelineRuns/resource-group-name/PipelineRuns_Get
        self.cmd('az datafactory pipeline-run show '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}" '
                 '--run-id "2f7fdb90-5df1-4b8e-ac2f-064cfa58202b"',
                 checks=[])

        # EXAMPLE: Factories/resource-group-name/Factories_Get
        self.cmd('az datafactory factory show '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: IntegrationRuntimes/resource-group-name/IntegrationRuntimes_ListByFactory
        self.cmd('az datafactory integration-runtime list '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: LinkedServices/resource-group-name/LinkedServices_ListByFactory
        self.cmd('az datafactory linked-service list '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Pipelines/resource-group-name/Pipelines_ListByFactory
        self.cmd('az datafactory pipeline list '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: DataFlows/resource-group-name/DataFlows_ListByFactory
        self.cmd('az datafactory data-flow list '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Datasets/resource-group-name/Datasets_ListByFactory
        self.cmd('az datafactory dataset list '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Triggers/resource-group-name/Triggers_ListByFactory
        self.cmd('az datafactory trigger list '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Factories/resource-group-name/Factories_ListByResourceGroup
        self.cmd('az datafactory factory list '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Factories/api-version/Factories_List
        self.cmd('az datafactory factory list',
                 checks=[])

        # EXAMPLE: IntegrationRuntimeNodes/resource-group-name/IntegrationRuntimeNodes_GetIpAddress
        self.cmd('az datafactory integration-runtime-node get-ip-address '
                 '--factory-name "{exampleFactoryName}" '
                 '--integration-runtime-name "{exampleIntegrationRuntime}" '
                 '--node-name "Node_1" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: IntegrationRuntimes/resource-group-name/IntegrationRuntimes_CreateLinkedIntegrationRuntime
        self.cmd('az datafactory integration-runtime create-linked-integration-runtime '
                 '--name "bfa92911-9fb6-4fbe-8f23-beae87bc1c83" '
                 '--data-factory-location "West US" '
                 '--data-factory-name "e9955d6d-56ea-4be3-841c-52a12c1a9981" '
                 '--subscription-id "061774c7-4b5a-4159-a55b-365581830283" '
                 '--factory-name "{exampleFactoryName}" '
                 '--integration-runtime-name "{exampleIntegrationRuntime}" '
                 '--resource-group "{rg}" '
                 '--subscription-id "12345678-1234-1234-1234-12345678abc"',
                 checks=[])

        # EXAMPLE: IntegrationRuntimeObjectMetadata/resource-group-name/IntegrationRuntimeObjectMetadata_Refresh
        self.cmd('az datafactory integration-runtime-object-metadata refresh '
                 '--factory-name "{exampleFactoryName}" '
                 '--integration-runtime-name "{IntegrationRuntimes_2}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: IntegrationRuntimes/resource-group-name/IntegrationRuntimes_GetConnectionInfo
        self.cmd('az datafactory integration-runtime get-connection-info '
                 '--factory-name "{exampleFactoryName}" '
                 '--integration-runtime-name "{exampleIntegrationRuntime}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: IntegrationRuntimes/resource-group-name/IntegrationRuntimes_RegenerateAuthKey
        self.cmd('az datafactory integration-runtime regenerate-auth-key '
                 '--factory-name "{exampleFactoryName}" '
                 '--integration-runtime-name "{exampleIntegrationRuntime}" '
                 '--key-name "authKey2" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: IntegrationRuntimeObjectMetadata/resource-group-name/IntegrationRuntimeObjectMetadata_Get
        self.cmd('az datafactory integration-runtime-object-metadata get '
                 '--factory-name "{exampleFactoryName}" '
                 '--metadata-path "ssisFolders" '
                 '--integration-runtime-name "{IntegrationRuntimes_2}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: IntegrationRuntimeNodes/resource-group-name/IntegrationRuntimeNodes_Update
        self.cmd('az datafactory integration-runtime-node update '
                 '--factory-name "{exampleFactoryName}" '
                 '--integration-runtime-name "{exampleIntegrationRuntime}" '
                 '--node-name "Node_1" '
                 '--resource-group "{rg}" '
                 '--concurrent-jobs-limit 2',
                 checks=[])

        # EXAMPLE: IntegrationRuntimes/resource-group-name/IntegrationRuntimes_SyncCredentials
        self.cmd('az datafactory integration-runtime sync-credentials '
                 '--factory-name "{exampleFactoryName}" '
                 '--integration-runtime-name "{exampleIntegrationRuntime}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: IntegrationRuntimes/resource-group-name/IntegrationRuntimes_GetMonitoringData
        self.cmd('az datafactory integration-runtime get-monitoring-data '
                 '--factory-name "{exampleFactoryName}" '
                 '--integration-runtime-name "{exampleIntegrationRuntime}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: IntegrationRuntimes/resource-group-name/IntegrationRuntimes_ListAuthKeys
        self.cmd('az datafactory integration-runtime list-auth-key '
                 '--factory-name "{exampleFactoryName}" '
                 '--integration-runtime-name "{exampleIntegrationRuntime}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: IntegrationRuntimes/resource-group-name/IntegrationRuntimes_Upgrade
        self.cmd('az datafactory integration-runtime upgrade '
                 '--factory-name "{exampleFactoryName}" '
                 '--integration-runtime-name "{exampleIntegrationRuntime}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: IntegrationRuntimes/resource-group-name/IntegrationRuntimes_Upgrade
        self.cmd('az datafactory integration-runtime remove-link '
                 '--factory-name "{exampleFactoryName}" '
                 '--integration-runtime-name "{exampleIntegrationRuntime}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: IntegrationRuntimes/resource-group-name/IntegrationRuntimes_GetStatus
        self.cmd('az datafactory integration-runtime get-status '
                 '--factory-name "{exampleFactoryName}" '
                 '--integration-runtime-name "{exampleIntegrationRuntime}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: IntegrationRuntimes/resource-group-name/IntegrationRuntimes_Upgrade
        self.cmd('az datafactory integration-runtime upgrade '
                 '--factory-name "{exampleFactoryName}" '
                 '--integration-runtime-name "{exampleIntegrationRuntime}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: IntegrationRuntimes/resource-group-name/IntegrationRuntimes_Upgrade
        self.cmd('az datafactory integration-runtime remove-link '
                 '--factory-name "{exampleFactoryName}" '
                 '--integration-runtime-name "{exampleIntegrationRuntime}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: IntegrationRuntimes/resource-group-name/IntegrationRuntimes_Start
        self.cmd('az datafactory integration-runtime start '
                 '--factory-name "{exampleFactoryName}" '
                 '--integration-runtime-name "{IntegrationRuntimes_3}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: IntegrationRuntimes/resource-group-name/IntegrationRuntimes_Stop
        self.cmd('az datafactory integration-runtime stop '
                 '--factory-name "{exampleFactoryName}" '
                 '--integration-runtime-name "{IntegrationRuntimes_3}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Triggers/resource-group-name/Triggers_GetEventSubscriptionStatus
        self.cmd('az datafactory trigger get-event-subscription-status '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}" '
                 '--trigger-name "{exampleTrigger}"',
                 checks=[])

        # EXAMPLE: TriggerRuns/resource-group-name/Triggers_Rerun
        self.cmd('az datafactory trigger-run rerun '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}" '
                 '--run-id "2f7fdb90-5df1-4b8e-ac2f-064cfa58202b" '
                 '--trigger-name "{exampleTrigger}"',
                 checks=[])

        # EXAMPLE: IntegrationRuntimes/resource-group-name/IntegrationRuntimes_Update
        self.cmd('az datafactory integration-runtime update '
                 '--factory-name "{exampleFactoryName}" '
                 '--integration-runtime-name "{exampleIntegrationRuntime}" '
                 '--resource-group "{rg}" '
                 '--auto-update "Off" '
                 '--update-delay-offset "\\"PT3H\\""',
                 checks=[])

        # EXAMPLE: Triggers/resource-group-name/Triggers_UnsubscribeFromEvents
        self.cmd('az datafactory trigger unsubscribe-from-event '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}" '
                 '--trigger-name "{exampleTrigger}"',
                 checks=[])

        # EXAMPLE: Triggers/resource-group-name/Triggers_SubscribeToEvents
        self.cmd('az datafactory trigger subscribe-to-event '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}" '
                 '--trigger-name "{exampleTrigger}"',
                 checks=[])

        # EXAMPLE: ActivityRuns/resource-group-name/ActivityRuns_QueryByPipelineRun
        self.cmd('az datafactory activity-run query-by-pipeline-run '
                 '--factory-name "{exampleFactoryName}" '
                 '--last-updated-after "2018-06-16T00:36:44.3345758Z" '
                 '--last-updated-before "2018-06-16T00:49:48.3686473Z" '
                 '--resource-group "{rg}" '
                 '--run-id "2f7fdb90-5df1-4b8e-ac2f-064cfa58202b"',
                 checks=[])

        # EXAMPLE: Pipelines/resource-group-name/Pipelines_CreateRun
        self.cmd('az datafactory pipeline create-run '
                 '--factory-name "{exampleFactoryName}" '
                 '--parameters OutputBlobNameList=["exampleoutput.csv"] '
                 '--pipeline-name "{examplePipeline}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Triggers/resource-group-name/Triggers_Start
        self.cmd('az datafactory trigger start '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}" '
                 '--trigger-name "{exampleTrigger}"',
                 checks=[])

        # EXAMPLE: PipelineRuns/resource-group-name/PipelineRuns_Cancel
        self.cmd('az datafactory pipeline-run cancel '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}" '
                 '--run-id "16ac5348-ff82-4f95-a80d-638c1d47b721"',
                 checks=[])

        # EXAMPLE: Triggers/resource-group-name/Triggers_Stop
        self.cmd('az datafactory trigger stop '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}" '
                 '--trigger-name "{exampleTrigger}"',
                 checks=[])

        # EXAMPLE: DataFlowDebugSession/resource-group-name/DataFlowDebugSession_ExecuteCommand
        self.cmd('az datafactory data-flow-debug-session execute-command '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}" '
                 '--command "executePreviewQuery" '
                 '--command-payload row-limits=100 stream-name=source1 '
                 '--session-id "f06ed247-9d07-49b2-b05e-2cb4a2fc871e"',
                 checks=[])

        # EXAMPLE: DataFlowDebugSession/resource-group-name/DataFlowDebugSession_QueryByFactory
        self.cmd('az datafactory data-flow-debug-session query-by-factory '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: DataFlowDebugSession/resource-group-name/DataFlowDebugSession_AddDataFlow
        self.cmd('az datafactory data-flow-debug-session add-data-flow '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}" '
                 '--data-flow "{{\\"name\\":\\"dataflow1\\",\\"properties\\":{{\\"type\\":\\"MappingDataFlow\\",\\"type'
                 'Properties\\":{{\\"script\\":\\"\\\\n\\\\nsource(output(\\\\n\\\\t\\\\tColumn_1 as string\\\\n\\\\t),'
                 '\\\\n\\\\tallowSchemaDrift: true,\\\\n\\\\tvalidateSchema: false) ~> source1\\",\\"sinks\\":[],\\"sou'
                 'rces\\":[{{\\"name\\":\\"source1\\",\\"dataset\\":{{\\"type\\":\\"DatasetReference\\",\\"referenceNam'
                 'e\\":\\"DelimitedText2\\"}}}}],\\"transformations\\":[]}}}}}}" '
                 '--datasets "[{{\\"name\\":\\"dataset1\\",\\"properties\\":{{\\"type\\":\\"DelimitedText\\",\\"schema'
                 '\\":[{{\\"type\\":\\"String\\"}}],\\"annotations\\":[],\\"linkedServiceName\\":{{\\"type\\":\\"Linke'
                 'dServiceReference\\",\\"referenceName\\":\\"linkedService5\\"}},\\"typeProperties\\":{{\\"columnDeli'
                 'miter\\":\\",\\",\\"escapeChar\\":\\"\\\\\\\\\\",\\"firstRowAsHeader\\":true,\\"location\\":{{\\"typ'
                 'e\\":\\"AzureBlobStorageLocation\\",\\"container\\":\\"dataflow-sample-data\\",\\"fileName\\":\\"Ans'
                 'iencoding.csv\\"}},\\"quoteChar\\":\\"\\\\\\"\\"}}}}}}]" '
                 '--debug-settings "{{\\"datasetParameters\\":{{\\"Movies\\":{{\\"path\\":\\"abc\\"}},\\"Output\\":{{'
                 '\\"time\\":\\"def\\"}}}},\\"parameters\\":{{\\"sourcePath\\":\\"Toy\\"}},\\"sourceSettings\\":[{{\\'
                 '"rowLimit\\":1000,\\"sourceName\\":\\"source1\\"}},{{\\"rowLimit\\":222,\\"sourceName\\":\\"source2'
                 '\\"}}]}}" '
                 '--linked-services "[{{\\"name\\":\\"linkedService1\\",\\"properties\\":{{\\"type\\":\\"AzureBlobStora'
                 'ge\\",\\"annotations\\":[],\\"typeProperties\\":{{\\"connectionString\\":\\"DefaultEndpointsProtocol='
                 'https;AccountName=<storageName>;EndpointSuffix=core.windows.net;\\",\\"encryptedCredential\\":\\"<cre'
                 'dential>\\"}}}}}}]" '
                 '--session-id "f06ed247-9d07-49b2-b05e-2cb4a2fc871e"',
                 checks=[])

        # EXAMPLE: Factories/resource-group-name/Factories_GetGitHubAccessToken
        self.cmd('az datafactory factory get-git-hub-access-token '
                 '--factory-name "{exampleFactoryName}" '
                 '--git-hub-access-code "some" '
                 '--git-hub-access-token-base-url "some" '
                 '--git-hub-client-id "some" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Factories/resource-group-name/Factories_GetDataPlaneAccess
        self.cmd('az datafactory factory get-data-plane-access '
                 '--factory-name "{exampleFactoryName}" '
                 '--access-resource-path "" '
                 '--expire-time "2018-11-10T09:46:20.2659347Z" '
                 '--permissions "r" '
                 '--profile-name "DefaultProfile" '
                 '--start-time "2018-11-10T02:46:20.2659347Z" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: PipelineRuns/resource-group-name/PipelineRuns_QueryByFactory
        self.cmd('az datafactory pipeline-run query-by-factory '
                 '--factory-name "{exampleFactoryName}" '
                 '--filters operand=PipelineName operator=Equals values=["examplePipeline"] '
                 '--last-updated-after "2018-06-16T00:36:44.3345758Z" '
                 '--last-updated-before "2018-06-16T00:49:48.3686473Z" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: TriggerRuns/resource-group-name/TriggerRuns_QueryByFactory
        self.cmd('az datafactory trigger-run query-by-factory '
                 '--factory-name "{exampleFactoryName}" '
                 '--filters operand=TriggerName operator=Equals values=["exampleTrigger"] '
                 '--last-updated-after "2018-06-16T00:36:44.3345758Z" '
                 '--last-updated-before "2018-06-16T00:49:48.3686473Z" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: ExposureControl/resource-group-name/ExposureControl_GetFeatureValueByFactory
        self.cmd('az datafactory exposure-control get-feature-value-by-factory '
                 '--feature-name "ADFIntegrationRuntimeSharingRbac" '
                 '--feature-type "Feature" '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Triggers/resource-group-name/Triggers_QueryByFactory
        self.cmd('az datafactory trigger query-by-factory '
                 '--factory-name "{exampleFactoryName}" '
                 '--parent-trigger-name "exampleTrigger" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Factories/resource-group-name/Factories_Update
        self.cmd('az datafactory factory update '
                 '--factory-name "{exampleFactoryName}" '
                 '--tags exampleTag=exampleValue '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Factories/location-id/Factories_ConfigureFactoryRepo
        self.cmd('az datafactory factory configure-factory-repo '
                 '--factory-resource-id "/subscriptions/{subscription_id}/resourceGroups/{rg}/providers/Microsoft.DataF'
                 'actory/factories/{exampleFactoryName}" '
                 '--repo-configuration "{{\\"type\\":\\"FactoryVSTSConfiguration\\",\\"accountName\\":\\"ADF\\",\\"coll'
                 'aborationBranch\\":\\"master\\",\\"lastCommitId\\":\\"\\",\\"projectName\\":\\"project\\",\\"reposito'
                 'ryName\\":\\"repo\\",\\"rootFolder\\":\\"/\\",\\"tenantId\\":\\"\\"}}" '
                 '--location-id "East US"',
                 checks=[])

        # EXAMPLE: ExposureControl/location-id/ExposureControl_GetFeatureValue
        self.cmd('az datafactory exposure-control get-feature-value '
                 '--feature-name "ADFIntegrationRuntimeSharingRbac" '
                 '--feature-type "Feature" '
                 '--location-id "WestEurope"',
                 checks=[])

        # EXAMPLE: IntegrationRuntimeNodes/resource-group-name/IntegrationRuntimesNodes_Delete
        self.cmd('az datafactory integration-runtime-node delete '
                 '--factory-name "{exampleFactoryName}" '
                 '--integration-runtime-name "{exampleIntegrationRuntime}" '
                 '--node-name "Node_1" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: IntegrationRuntimes/resource-group-name/IntegrationRuntimes_Delete
        self.cmd('az datafactory integration-runtime delete '
                 '--factory-name "{exampleFactoryName}" '
                 '--integration-runtime-name "{exampleIntegrationRuntime}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: DataFlowDebugSession/resource-group-name/DataFlowDebugSession_Delete
        self.cmd('az datafactory data-flow-debug-session delete '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}" '
                 '--session-id "91fb57e0-8292-47be-89ff-c8f2d2bb2a7e"',
                 checks=[])

        # EXAMPLE: LinkedServices/resource-group-name/LinkedServices_Delete
        self.cmd('az datafactory linked-service delete '
                 '--factory-name "{exampleFactoryName}" '
                 '--linked-service-name "{exampleLinkedService}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Pipelines/resource-group-name/Pipelines_Delete
        self.cmd('az datafactory pipeline delete '
                 '--factory-name "{exampleFactoryName}" '
                 '--pipeline-name "{examplePipeline}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: DataFlows/resource-group-name/DataFlows_Delete
        self.cmd('az datafactory data-flow delete '
                 '--data-flow-name "{exampleDataFlow}" '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Datasets/resource-group-name/Datasets_Delete
        self.cmd('az datafactory dataset delete '
                 '--dataset-name "{exampleDataset}" '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Triggers/resource-group-name/Triggers_Delete
        self.cmd('az datafactory trigger delete '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}" '
                 '--trigger-name "{exampleTrigger}"',
                 checks=[])

        # EXAMPLE: Factories/resource-group-name/Factories_Delete
        self.cmd('az datafactory factory delete '
                 '--factory-name "{exampleFactoryName}" '
                 '--resource-group "{rg}"',
                 checks=[])
