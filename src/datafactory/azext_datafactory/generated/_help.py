# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from knack.help_files import helps


helps['datafactory factory'] = """
    type: group
    short-summary: datafactory factory
"""

helps['datafactory factory list'] = """
    type: command
    short-summary: Lists factories under the specified subscription.
    examples:
      - name: Factories_ListByResourceGroup
        text: |-
               az datafactory factory list --resource-group "exampleResourceGroup"
"""

helps['datafactory factory show'] = """
    type: command
    short-summary: Gets a factory.
    examples:
      - name: Factories_Get
        text: |-
               az datafactory factory show --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory factory create'] = """
    type: command
    short-summary: Creates or updates a factory.
    examples:
      - name: Factories_CreateOrUpdate
        text: |-
               az datafactory factory create --location "East US" --factory-name "exampleFactoryName"
               --resource-group "exampleResourceGroup"
"""

helps['datafactory factory update'] = """
    type: command
    short-summary: Updates a factory.
    examples:
      - name: Factories_Update
        text: |-
               az datafactory factory update --factory-name "exampleFactoryName" --tags
               exampleTag=exampleValue --resource-group "exampleResourceGroup"
"""

helps['datafactory factory delete'] = """
    type: command
    short-summary: Deletes a factory.
    examples:
      - name: Factories_Delete
        text: |-
               az datafactory factory delete --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory factory get-git-hub-access-token'] = """
    type: command
    short-summary: Get GitHub Access Token.
    examples:
      - name: Factories_GetGitHubAccessToken
        text: |-
               az datafactory factory get-git-hub-access-token --factory-name "exampleFactoryName"
               --git-hub-access-code "some" --git-hub-access-token-base-url "some" --git-hub-client-id
               "some" --resource-group "exampleResourceGroup"
"""

helps['datafactory factory get-data-plane-access'] = """
    type: command
    short-summary: Get Data Plane access.
    examples:
      - name: Factories_GetDataPlaneAccess
        text: |-
               az datafactory factory get-data-plane-access --factory-name "exampleFactoryName"
               --access-resource-path "" --expire-time "2018-11-10T09:46:20.2659347Z" --permissions "r"
               --profile-name "DefaultProfile" --start-time "2018-11-10T02:46:20.2659347Z"
               --resource-group "exampleResourceGroup"
"""

helps['datafactory factory configure-factory-repo'] = """
    type: command
    short-summary: Updates a factory's repo information.
    examples:
      - name: Factories_ConfigureFactoryRepo
        text: |-
               az datafactory factory configure-factory-repo --factory-resource-id "/subscriptions/123456
               78-1234-1234-1234-12345678abc/resourceGroups/exampleResourceGroup/providers/Microsoft.Data
               Factory/factories/exampleFactoryName" --repo-configuration "{\\"type\\":\\"FactoryVSTSConfigu
               ration\\",\\"accountName\\":\\"ADF\\",\\"collaborationBranch\\":\\"master\\",\\"lastCommitId\\":\\"\\",
               \\"projectName\\":\\"project\\",\\"repositoryName\\":\\"repo\\",\\"rootFolder\\":\\"/\\",\\"tenantId\\":
               \\"\\"}" --location-id "East US"
"""

helps['datafactory exposure-control'] = """
    type: group
    short-summary: datafactory exposure-control
"""

helps['datafactory exposure-control get-feature-value-by-factory'] = """
    type: command
    short-summary: Get exposure control feature for specific factory.
    examples:
      - name: ExposureControl_GetFeatureValueByFactory
        text: |-
               az datafactory exposure-control get-feature-value-by-factory --feature-name
               "ADFIntegrationRuntimeSharingRbac" --feature-type "Feature" --factory-name
               "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory exposure-control get-feature-value'] = """
    type: command
    short-summary: Get exposure control feature for specific location.
    examples:
      - name: ExposureControl_GetFeatureValue
        text: |-
               az datafactory exposure-control get-feature-value --feature-name
               "ADFIntegrationRuntimeSharingRbac" --feature-type "Feature" --location-id "WestEurope"
"""

helps['datafactory integration-runtime'] = """
    type: group
    short-summary: datafactory integration-runtime
"""

helps['datafactory integration-runtime list'] = """
    type: command
    short-summary: Lists integration runtimes.
    examples:
      - name: IntegrationRuntimes_ListByFactory
        text: |-
               az datafactory integration-runtime list --factory-name "exampleFactoryName"
               --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime show'] = """
    type: command
    short-summary: Gets an integration runtime.
    examples:
      - name: IntegrationRuntimes_Get
        text: |-
               az datafactory integration-runtime show --factory-name "exampleFactoryName"
               --integration-runtime-name "exampleIntegrationRuntime" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory integration-runtime create'] = """
    type: command
    short-summary: Creates or updates an integration runtime.
    examples:
      - name: IntegrationRuntimes_Create
        text: |-
               az datafactory integration-runtime create --factory-name "exampleFactoryName"
               --properties
               "{\\"type\\":\\"SelfHosted\\",\\"description\\":\\"A selfhosted integration runtime\\"}"
               --integration-runtime-name "exampleIntegrationRuntime" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory integration-runtime update'] = """
    type: command
    short-summary: Updates an integration runtime.
    examples:
      - name: IntegrationRuntimes_Update
        text: |-
               az datafactory integration-runtime update --factory-name "exampleFactoryName"
               --integration-runtime-name "exampleIntegrationRuntime" --resource-group
               "exampleResourceGroup" --auto-update "Off" --update-delay-offset "\\"PT3H\\""
"""

helps['datafactory integration-runtime delete'] = """
    type: command
    short-summary: Deletes an integration runtime.
    examples:
      - name: IntegrationRuntimes_Delete
        text: |-
               az datafactory integration-runtime delete --factory-name "exampleFactoryName"
               --integration-runtime-name "exampleIntegrationRuntime" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory integration-runtime get-status'] = """
    type: command
    short-summary: Gets detailed status information for an integration runtime.
    examples:
      - name: IntegrationRuntimes_GetStatus
        text: |-
               az datafactory integration-runtime get-status --factory-name "exampleFactoryName"
               --integration-runtime-name "exampleIntegrationRuntime" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory integration-runtime get-connection-info'] = """
    type: command
    short-summary: Gets the on-premises integration runtime connection information for encrypting the on-premises data source credentials.
    examples:
      - name: IntegrationRuntimes_GetConnectionInfo
        text: |-
               az datafactory integration-runtime get-connection-info --factory-name
               "exampleFactoryName" --integration-runtime-name "exampleIntegrationRuntime"
               --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime regenerate-auth-key'] = """
    type: command
    short-summary: Regenerates the authentication key for an integration runtime.
    examples:
      - name: IntegrationRuntimes_RegenerateAuthKey
        text: |-
               az datafactory integration-runtime regenerate-auth-key --factory-name
               "exampleFactoryName" --integration-runtime-name "exampleIntegrationRuntime" --key-name
               "authKey2" --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime create-linked-integration-runtime'] = """
    type: command
    short-summary: Create a linked integration runtime entry in a shared integration runtime.
    examples:
      - name: IntegrationRuntimes_CreateLinkedIntegrationRuntime
        text: |-
               az datafactory integration-runtime create-linked-integration-runtime --name
               "bfa92911-9fb6-4fbe-8f23-beae87bc1c83" --data-factory-location "West US"
               --data-factory-name "e9955d6d-56ea-4be3-841c-52a12c1a9981" --subscription-id
               "061774c7-4b5a-4159-a55b-365581830283" --factory-name "exampleFactoryName"
               --integration-runtime-name "exampleIntegrationRuntime" --resource-group
               "exampleResourceGroup" --subscription-id "12345678-1234-1234-1234-12345678abc"
"""

helps['datafactory integration-runtime start'] = """
    type: command
    short-summary: Starts a ManagedReserved type integration runtime.
    examples:
      - name: IntegrationRuntimes_Start
        text: |-
               az datafactory integration-runtime start --factory-name "exampleFactoryName"
               --integration-runtime-name "exampleManagedIntegrationRuntime" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory integration-runtime stop'] = """
    type: command
    short-summary: Stops a ManagedReserved type integration runtime.
    examples:
      - name: IntegrationRuntimes_Stop
        text: |-
               az datafactory integration-runtime stop --factory-name "exampleFactoryName"
               --integration-runtime-name "exampleManagedIntegrationRuntime" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory integration-runtime sync-credentials'] = """
    type: command
    short-summary: Force the integration runtime to synchronize credentials across integration runtime nodes, and this will override the credentials across all worker nodes with those available on the dispatcher node. If you already have the latest credential backup file, you should manually import it (preferred) on any self-hosted integration runtime node than using this API directly.
    examples:
      - name: IntegrationRuntimes_SyncCredentials
        text: |-
               az datafactory integration-runtime sync-credentials --factory-name "exampleFactoryName"
               --integration-runtime-name "exampleIntegrationRuntime" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory integration-runtime get-monitoring-data'] = """
    type: command
    short-summary: Get the integration runtime monitoring data, which includes the monitor data for all the nodes under this integration runtime.
    examples:
      - name: IntegrationRuntimes_GetMonitoringData
        text: |-
               az datafactory integration-runtime get-monitoring-data --factory-name
               "exampleFactoryName" --integration-runtime-name "exampleIntegrationRuntime"
               --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime upgrade'] = """
    type: command
    short-summary: Upgrade self-hosted integration runtime to latest version if availability.
    examples:
      - name: IntegrationRuntimes_Upgrade
        text: |-
               az datafactory integration-runtime upgrade --factory-name "exampleFactoryName"
               --integration-runtime-name "exampleIntegrationRuntime" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory integration-runtime remove-link'] = """
    type: command
    short-summary: Remove all linked integration runtimes under specific data factory in a self-hosted integration runtime.
    examples:
      - name: IntegrationRuntimes_Upgrade
        text: |-
               az datafactory integration-runtime remove-link --factory-name "exampleFactoryName"
               --integration-runtime-name "exampleIntegrationRuntime" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory integration-runtime list-auth-key'] = """
    type: command
    short-summary: Retrieves the authentication keys for an integration runtime.
    examples:
      - name: IntegrationRuntimes_ListAuthKeys
        text: |-
               az datafactory integration-runtime list-auth-key --factory-name "exampleFactoryName"
               --integration-runtime-name "exampleIntegrationRuntime" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory integration-runtime-object-metadata'] = """
    type: group
    short-summary: datafactory integration-runtime-object-metadata
"""

helps['datafactory integration-runtime-object-metadata refresh'] = """
    type: command
    short-summary: Refresh a SSIS integration runtime object metadata.
    examples:
      - name: IntegrationRuntimeObjectMetadata_Refresh
        text: |-
               az datafactory integration-runtime-object-metadata refresh --factory-name
               "exampleFactoryName" --integration-runtime-name "testactivityv2" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory integration-runtime-object-metadata get'] = """
    type: command
    short-summary: Get a SSIS integration runtime object metadata by specified path. The return is pageable metadata list.
    examples:
      - name: IntegrationRuntimeObjectMetadata_Get
        text: |-
               az datafactory integration-runtime-object-metadata get --factory-name
               "exampleFactoryName" --metadata-path "ssisFolders" --integration-runtime-name
               "testactivityv2" --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime-node'] = """
    type: group
    short-summary: datafactory integration-runtime-node
"""

helps['datafactory integration-runtime-node show'] = """
    type: command
    short-summary: Gets a self-hosted integration runtime node.
    examples:
      - name: IntegrationRuntimeNodes_Get
        text: |-
               az datafactory integration-runtime-node show --factory-name "exampleFactoryName"
               --integration-runtime-name "exampleIntegrationRuntime" --node-name "Node_1"
               --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime-node update'] = """
    type: command
    short-summary: Updates a self-hosted integration runtime node.
    examples:
      - name: IntegrationRuntimeNodes_Update
        text: |-
               az datafactory integration-runtime-node update --factory-name "exampleFactoryName"
               --integration-runtime-name "exampleIntegrationRuntime" --node-name "Node_1"
               --resource-group "exampleResourceGroup" --concurrent-jobs-limit 2
"""

helps['datafactory integration-runtime-node delete'] = """
    type: command
    short-summary: Deletes a self-hosted integration runtime node.
    examples:
      - name: IntegrationRuntimesNodes_Delete
        text: |-
               az datafactory integration-runtime-node delete --factory-name "exampleFactoryName"
               --integration-runtime-name "exampleIntegrationRuntime" --node-name "Node_1"
               --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime-node get-ip-address'] = """
    type: command
    short-summary: Get the IP address of self-hosted integration runtime node.
    examples:
      - name: IntegrationRuntimeNodes_GetIpAddress
        text: |-
               az datafactory integration-runtime-node get-ip-address --factory-name
               "exampleFactoryName" --integration-runtime-name "exampleIntegrationRuntime" --node-name
               "Node_1" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service'] = """
    type: group
    short-summary: datafactory linked-service
"""

helps['datafactory linked-service list'] = """
    type: command
    short-summary: Lists linked services.
    examples:
      - name: LinkedServices_ListByFactory
        text: |-
               az datafactory linked-service list --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory linked-service show'] = """
    type: command
    short-summary: Gets a linked service.
    examples:
      - name: LinkedServices_Get
        text: |-
               az datafactory linked-service show --factory-name "exampleFactoryName"
               --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service create --factory-name "exampleFactoryName" --properties "{\\"
               type\\":\\"AzureStorage\\",\\"typeProperties\\":{\\"connectionString\\":{\\"type\\":\\"SecureString\\
               ",\\"value\\":\\"DefaultEndpointsProtocol=https;AccountName=examplestorageaccount;AccountKey=
               <storage key>\\"}}}" --linked-service-name "exampleLinkedService" --resource-group
               "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service create --factory-name "exampleFactoryName" --properties "{\\"
               type\\":\\"AzureStorage\\",\\"description\\":\\"Example description\\",\\"typeProperties\\":{\\"conn
               ectionString\\":{\\"type\\":\\"SecureString\\",\\"value\\":\\"DefaultEndpointsProtocol=https;Accou
               ntName=examplestorageaccount;AccountKey=<storage key>\\"}}}" --linked-service-name
               "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service create --factory-name "exampleFactoryName" --properties "{\\"
               type\\":\\"AzureStorage\\",\\"typeProperties\\":{\\"connectionString\\":{\\"type\\":\\"SecureString\\
               ",\\"value\\":\\"DefaultEndpointsProtocol=https;AccountName=examplestorageaccount;AccountKey=
               <storage key>\\"}}}" --linked-service-name "exampleLinkedService" --resource-group
               "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service create --factory-name "exampleFactoryName" --properties "{\\"
               type\\":\\"AzureStorage\\",\\"description\\":\\"Example description\\",\\"typeProperties\\":{\\"conn
               ectionString\\":{\\"type\\":\\"SecureString\\",\\"value\\":\\"DefaultEndpointsProtocol=https;Accou
               ntName=examplestorageaccount;AccountKey=<storage key>\\"}}}" --linked-service-name
               "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service delete'] = """
    type: command
    short-summary: Deletes a linked service.
    examples:
      - name: LinkedServices_Delete
        text: |-
               az datafactory linked-service delete --factory-name "exampleFactoryName"
               --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset'] = """
    type: group
    short-summary: datafactory dataset
"""

helps['datafactory dataset list'] = """
    type: command
    short-summary: Lists datasets.
    examples:
      - name: Datasets_ListByFactory
        text: |-
               az datafactory dataset list --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory dataset show'] = """
    type: command
    short-summary: Gets a dataset.
    examples:
      - name: Datasets_Get
        text: |-
               az datafactory dataset show --dataset-name "exampleDataset" --factory-name
               "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset create --properties "{\\"type\\":\\"AzureBlob\\",\\"linkedServiceName\\":
               {\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"},\\"paramet
               ers\\":{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}},\\"type
               Properties\\":{\\"format\\":{\\"type\\":\\"TextFormat\\"},\\"fileName\\":{\\"type\\":\\"Expression\\",\\
               "value\\":\\"@dataset().MyFileName\\"},\\"folderPath\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@d
               ataset().MyFolderPath\\"}}}" --dataset-name "exampleDataset" --factory-name
               "exampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset create --properties "{\\"type\\":\\"AzureBlob\\",\\"description\\":\\"Exam
               ple description\\",\\"linkedServiceName\\":{\\"type\\":\\"LinkedServiceReference\\",\\"referenceNa
               me\\":\\"exampleLinkedService\\"},\\"parameters\\":{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFo
               lderPath\\":{\\"type\\":\\"String\\"}},\\"typeProperties\\":{\\"format\\":{\\"type\\":\\"TextFormat\\"}
               ,\\"fileName\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFileName\\"},\\"folderPath\\"
               :{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFolderPath\\"}}}" --dataset-name
               "exampleDataset" --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory dataset update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset create --properties "{\\"type\\":\\"AzureBlob\\",\\"linkedServiceName\\":
               {\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"},\\"paramet
               ers\\":{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}},\\"type
               Properties\\":{\\"format\\":{\\"type\\":\\"TextFormat\\"},\\"fileName\\":{\\"type\\":\\"Expression\\",\\
               "value\\":\\"@dataset().MyFileName\\"},\\"folderPath\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@d
               ataset().MyFolderPath\\"}}}" --dataset-name "exampleDataset" --factory-name
               "exampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset create --properties "{\\"type\\":\\"AzureBlob\\",\\"description\\":\\"Exam
               ple description\\",\\"linkedServiceName\\":{\\"type\\":\\"LinkedServiceReference\\",\\"referenceNa
               me\\":\\"exampleLinkedService\\"},\\"parameters\\":{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFo
               lderPath\\":{\\"type\\":\\"String\\"}},\\"typeProperties\\":{\\"format\\":{\\"type\\":\\"TextFormat\\"}
               ,\\"fileName\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFileName\\"},\\"folderPath\\"
               :{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFolderPath\\"}}}" --dataset-name
               "exampleDataset" --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory dataset delete'] = """
    type: command
    short-summary: Deletes a dataset.
    examples:
      - name: Datasets_Delete
        text: |-
               az datafactory dataset delete --dataset-name "exampleDataset" --factory-name
               "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory pipeline'] = """
    type: group
    short-summary: datafactory pipeline
"""

helps['datafactory pipeline list'] = """
    type: command
    short-summary: Lists pipelines.
    examples:
      - name: Pipelines_ListByFactory
        text: |-
               az datafactory pipeline list --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory pipeline show'] = """
    type: command
    short-summary: Gets a pipeline.
    examples:
      - name: Pipelines_Get
        text: |-
               az datafactory pipeline show --factory-name "exampleFactoryName" --pipeline-name
               "examplePipeline" --resource-group "exampleResourceGroup"
"""

helps['datafactory pipeline create'] = """
    type: command
    short-summary: Creates or updates a pipeline.
    examples:
      - name: Pipelines_Create
        text: |-
               az datafactory pipeline create --factory-name "exampleFactoryName"
               --properties-activities "[{\\"name\\":\\"ExampleForeachActivity\\",\\"type\\":\\"ForEach\\",\\"type
               Properties\\":{\\"activities\\":[{\\"name\\":\\"ExampleCopyActivity\\",\\"type\\":\\"Copy\\",\\"inputs
               \\":[{\\"type\\":\\"DatasetReference\\",\\"parameters\\":{\\"MyFileName\\":\\"examplecontainer.csv\\"
               ,\\"MyFolderPath\\":\\"examplecontainer\\"},\\"referenceName\\":\\"exampleDataset\\"}],\\"outputs\\"
               :[{\\"type\\":\\"DatasetReference\\",\\"parameters\\":{\\"MyFileName\\":{\\"type\\":\\"Expression\\",\\
               "value\\":\\"@item()\\"},\\"MyFolderPath\\":\\"examplecontainer\\"},\\"referenceName\\":\\"exampleDa
               taset\\"}],\\"typeProperties\\":{\\"dataIntegrationUnits\\":32,\\"sink\\":{\\"type\\":\\"BlobSink\\"}
               ,\\"source\\":{\\"type\\":\\"BlobSource\\"}}}],\\"isSequential\\":true,\\"items\\":{\\"type\\":\\"Expre
               ssion\\",\\"value\\":\\"@pipeline().parameters.OutputBlobNameList\\"}}}]"
               --properties-parameters
               "{\\"JobId\\":{\\"type\\":\\"String\\"},\\"OutputBlobNameList\\":{\\"type\\":\\"Array\\"}}"
               --properties-run-dimensions JobId=[object Object] --properties-variables
               "{\\"TestVariableArray\\":{\\"type\\":\\"Array\\"}}" --pipeline-name "examplePipeline"
               --resource-group "exampleResourceGroup"
      - name: Pipelines_Update
        text: |-
               az datafactory pipeline create --factory-name "exampleFactoryName"
               --properties-description "Example description" --properties-activities "[{\\"name\\":\\"Examp
               leForeachActivity\\",\\"type\\":\\"ForEach\\",\\"typeProperties\\":{\\"activities\\":[{\\"name\\":\\"E
               xampleCopyActivity\\",\\"type\\":\\"Copy\\",\\"inputs\\":[{\\"type\\":\\"DatasetReference\\",\\"parame
               ters\\":{\\"MyFileName\\":\\"examplecontainer.csv\\",\\"MyFolderPath\\":\\"examplecontainer\\"},\\"r
               eferenceName\\":\\"exampleDataset\\"}],\\"outputs\\":[{\\"type\\":\\"DatasetReference\\",\\"paramete
               rs\\":{\\"MyFileName\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@item()\\"},\\"MyFolderPath\\":\\"ex
               amplecontainer\\"},\\"referenceName\\":\\"exampleDataset\\"}],\\"typeProperties\\":{\\"dataIntegra
               tionUnits\\":32,\\"sink\\":{\\"type\\":\\"BlobSink\\"},\\"source\\":{\\"type\\":\\"BlobSource\\"}}}],\\"
               isSequential\\":true,\\"items\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@pipeline().parameters.
               OutputBlobNameList\\"}}}]" --properties-parameters
               "{\\"OutputBlobNameList\\":{\\"type\\":\\"Array\\"}}" --pipeline-name "examplePipeline"
               --resource-group "exampleResourceGroup"
"""

helps['datafactory pipeline update'] = """
    type: command
    short-summary: Creates or updates a pipeline.
    examples:
      - name: Pipelines_Create
        text: |-
               az datafactory pipeline create --factory-name "exampleFactoryName"
               --properties-activities "[{\\"name\\":\\"ExampleForeachActivity\\",\\"type\\":\\"ForEach\\",\\"type
               Properties\\":{\\"activities\\":[{\\"name\\":\\"ExampleCopyActivity\\",\\"type\\":\\"Copy\\",\\"inputs
               \\":[{\\"type\\":\\"DatasetReference\\",\\"parameters\\":{\\"MyFileName\\":\\"examplecontainer.csv\\"
               ,\\"MyFolderPath\\":\\"examplecontainer\\"},\\"referenceName\\":\\"exampleDataset\\"}],\\"outputs\\"
               :[{\\"type\\":\\"DatasetReference\\",\\"parameters\\":{\\"MyFileName\\":{\\"type\\":\\"Expression\\",\\
               "value\\":\\"@item()\\"},\\"MyFolderPath\\":\\"examplecontainer\\"},\\"referenceName\\":\\"exampleDa
               taset\\"}],\\"typeProperties\\":{\\"dataIntegrationUnits\\":32,\\"sink\\":{\\"type\\":\\"BlobSink\\"}
               ,\\"source\\":{\\"type\\":\\"BlobSource\\"}}}],\\"isSequential\\":true,\\"items\\":{\\"type\\":\\"Expre
               ssion\\",\\"value\\":\\"@pipeline().parameters.OutputBlobNameList\\"}}}]"
               --properties-parameters
               "{\\"JobId\\":{\\"type\\":\\"String\\"},\\"OutputBlobNameList\\":{\\"type\\":\\"Array\\"}}"
               --properties-run-dimensions JobId=[object Object] --properties-variables
               "{\\"TestVariableArray\\":{\\"type\\":\\"Array\\"}}" --pipeline-name "examplePipeline"
               --resource-group "exampleResourceGroup"
      - name: Pipelines_Update
        text: |-
               az datafactory pipeline create --factory-name "exampleFactoryName"
               --properties-description "Example description" --properties-activities "[{\\"name\\":\\"Examp
               leForeachActivity\\",\\"type\\":\\"ForEach\\",\\"typeProperties\\":{\\"activities\\":[{\\"name\\":\\"E
               xampleCopyActivity\\",\\"type\\":\\"Copy\\",\\"inputs\\":[{\\"type\\":\\"DatasetReference\\",\\"parame
               ters\\":{\\"MyFileName\\":\\"examplecontainer.csv\\",\\"MyFolderPath\\":\\"examplecontainer\\"},\\"r
               eferenceName\\":\\"exampleDataset\\"}],\\"outputs\\":[{\\"type\\":\\"DatasetReference\\",\\"paramete
               rs\\":{\\"MyFileName\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@item()\\"},\\"MyFolderPath\\":\\"ex
               amplecontainer\\"},\\"referenceName\\":\\"exampleDataset\\"}],\\"typeProperties\\":{\\"dataIntegra
               tionUnits\\":32,\\"sink\\":{\\"type\\":\\"BlobSink\\"},\\"source\\":{\\"type\\":\\"BlobSource\\"}}}],\\"
               isSequential\\":true,\\"items\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@pipeline().parameters.
               OutputBlobNameList\\"}}}]" --properties-parameters
               "{\\"OutputBlobNameList\\":{\\"type\\":\\"Array\\"}}" --pipeline-name "examplePipeline"
               --resource-group "exampleResourceGroup"
"""

helps['datafactory pipeline delete'] = """
    type: command
    short-summary: Deletes a pipeline.
    examples:
      - name: Pipelines_Delete
        text: |-
               az datafactory pipeline delete --factory-name "exampleFactoryName" --pipeline-name
               "examplePipeline" --resource-group "exampleResourceGroup"
"""

helps['datafactory pipeline create-run'] = """
    type: command
    short-summary: Creates a run of a pipeline.
    examples:
      - name: Pipelines_CreateRun
        text: |-
               az datafactory pipeline create-run --factory-name "exampleFactoryName" --parameters
               OutputBlobNameList=exampleoutput.csv --pipeline-name "examplePipeline" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory pipeline-run'] = """
    type: group
    short-summary: datafactory pipeline-run
"""

helps['datafactory pipeline-run show'] = """
    type: command
    short-summary: Get a pipeline run by its run ID.
    examples:
      - name: PipelineRuns_Get
        text: |-
               az datafactory pipeline-run show --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup" --run-id "2f7fdb90-5df1-4b8e-ac2f-064cfa58202b"
"""

helps['datafactory pipeline-run cancel'] = """
    type: command
    short-summary: Cancel a pipeline run by its run ID.
    examples:
      - name: PipelineRuns_Cancel
        text: |-
               az datafactory pipeline-run cancel --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup" --run-id "16ac5348-ff82-4f95-a80d-638c1d47b721"
"""

helps['datafactory pipeline-run query-by-factory'] = """
    type: command
    short-summary: Query pipeline runs in the factory based on input filter conditions.
    examples:
      - name: PipelineRuns_QueryByFactory
        text: |-
               az datafactory pipeline-run query-by-factory --factory-name "exampleFactoryName"
               --filters operand=PipelineName operator=Equals values=examplePipeline
               --last-updated-after "2018-06-16T00:36:44.3345758Z" --last-updated-before
               "2018-06-16T00:49:48.3686473Z" --resource-group "exampleResourceGroup"
"""

helps['datafactory activity-run'] = """
    type: group
    short-summary: datafactory activity-run
"""

helps['datafactory activity-run query-by-pipeline-run'] = """
    type: command
    short-summary: Query activity runs based on input filter conditions.
    examples:
      - name: ActivityRuns_QueryByPipelineRun
        text: |-
               az datafactory activity-run query-by-pipeline-run --factory-name "exampleFactoryName"
               --last-updated-after "2018-06-16T00:36:44.3345758Z" --last-updated-before
               "2018-06-16T00:49:48.3686473Z" --resource-group "exampleResourceGroup" --run-id
               "2f7fdb90-5df1-4b8e-ac2f-064cfa58202b"
"""

helps['datafactory trigger'] = """
    type: group
    short-summary: datafactory trigger
"""

helps['datafactory trigger list'] = """
    type: command
    short-summary: Lists triggers.
    examples:
      - name: Triggers_ListByFactory
        text: |-
               az datafactory trigger list --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory trigger show'] = """
    type: command
    short-summary: Gets a trigger.
    examples:
      - name: Triggers_Get
        text: |-
               az datafactory trigger show --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup" --trigger-name "exampleTrigger"
"""

helps['datafactory trigger create'] = """
    type: command
    short-summary: Creates or updates a trigger.
    examples:
      - name: Triggers_Create
        text: |-
               az datafactory trigger create --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup" --properties "{\\"type\\":\\"ScheduleTrigger\\",\\"pipelines\\":[{\\"param
               eters\\":{\\"OutputBlobNameList\\":[\\"exampleoutput.csv\\"]},\\"pipelineReference\\":{\\"type\\":\\
               "PipelineReference\\",\\"referenceName\\":\\"examplePipeline\\"}}],\\"typeProperties\\":{\\"recurr
               ence\\":{\\"endTime\\":\\"2018-06-16T00:55:13.8441801Z\\",\\"frequency\\":\\"Minute\\",\\"interval\\"
               :4,\\"startTime\\":\\"2018-06-16T00:39:13.8441801Z\\",\\"timeZone\\":\\"UTC\\"}}}" --trigger-name
               "exampleTrigger"
      - name: Triggers_Update
        text: |-
               az datafactory trigger create --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup" --properties "{\\"type\\":\\"ScheduleTrigger\\",\\"description\\":\\"Examp
               le description\\",\\"pipelines\\":[{\\"parameters\\":{\\"OutputBlobNameList\\":[\\"exampleoutput.c
               sv\\"]},\\"pipelineReference\\":{\\"type\\":\\"PipelineReference\\",\\"referenceName\\":\\"examplePi
               peline\\"}}],\\"typeProperties\\":{\\"recurrence\\":{\\"endTime\\":\\"2018-06-16T00:55:14.905167Z\\
               ",\\"frequency\\":\\"Minute\\",\\"interval\\":4,\\"startTime\\":\\"2018-06-16T00:39:14.905167Z\\",\\"
               timeZone\\":\\"UTC\\"}}}" --trigger-name "exampleTrigger"
"""

helps['datafactory trigger update'] = """
    type: command
    short-summary: Creates or updates a trigger.
    examples:
      - name: Triggers_Create
        text: |-
               az datafactory trigger create --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup" --properties "{\\"type\\":\\"ScheduleTrigger\\",\\"pipelines\\":[{\\"param
               eters\\":{\\"OutputBlobNameList\\":[\\"exampleoutput.csv\\"]},\\"pipelineReference\\":{\\"type\\":\\
               "PipelineReference\\",\\"referenceName\\":\\"examplePipeline\\"}}],\\"typeProperties\\":{\\"recurr
               ence\\":{\\"endTime\\":\\"2018-06-16T00:55:13.8441801Z\\",\\"frequency\\":\\"Minute\\",\\"interval\\"
               :4,\\"startTime\\":\\"2018-06-16T00:39:13.8441801Z\\",\\"timeZone\\":\\"UTC\\"}}}" --trigger-name
               "exampleTrigger"
      - name: Triggers_Update
        text: |-
               az datafactory trigger create --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup" --properties "{\\"type\\":\\"ScheduleTrigger\\",\\"description\\":\\"Examp
               le description\\",\\"pipelines\\":[{\\"parameters\\":{\\"OutputBlobNameList\\":[\\"exampleoutput.c
               sv\\"]},\\"pipelineReference\\":{\\"type\\":\\"PipelineReference\\",\\"referenceName\\":\\"examplePi
               peline\\"}}],\\"typeProperties\\":{\\"recurrence\\":{\\"endTime\\":\\"2018-06-16T00:55:14.905167Z\\
               ",\\"frequency\\":\\"Minute\\",\\"interval\\":4,\\"startTime\\":\\"2018-06-16T00:39:14.905167Z\\",\\"
               timeZone\\":\\"UTC\\"}}}" --trigger-name "exampleTrigger"
"""

helps['datafactory trigger delete'] = """
    type: command
    short-summary: Deletes a trigger.
    examples:
      - name: Triggers_Delete
        text: |-
               az datafactory trigger delete --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup" --trigger-name "exampleTrigger"
"""

helps['datafactory trigger subscribe-to-event'] = """
    type: command
    short-summary: Subscribe event trigger to events.
    examples:
      - name: Triggers_SubscribeToEvents
        text: |-
               az datafactory trigger subscribe-to-event --factory-name "exampleFactoryName"
               --resource-group "exampleResourceGroup" --trigger-name "exampleTrigger"
"""

helps['datafactory trigger get-event-subscription-status'] = """
    type: command
    short-summary: Get a trigger's event subscription status.
    examples:
      - name: Triggers_GetEventSubscriptionStatus
        text: |-
               az datafactory trigger get-event-subscription-status --factory-name "exampleFactoryName"
               --resource-group "exampleResourceGroup" --trigger-name "exampleTrigger"
"""

helps['datafactory trigger unsubscribe-from-event'] = """
    type: command
    short-summary: Unsubscribe event trigger from events.
    examples:
      - name: Triggers_UnsubscribeFromEvents
        text: |-
               az datafactory trigger unsubscribe-from-event --factory-name "exampleFactoryName"
               --resource-group "exampleResourceGroup" --trigger-name "exampleTrigger"
"""

helps['datafactory trigger start'] = """
    type: command
    short-summary: Starts a trigger.
    examples:
      - name: Triggers_Start
        text: |-
               az datafactory trigger start --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup" --trigger-name "exampleTrigger"
"""

helps['datafactory trigger stop'] = """
    type: command
    short-summary: Stops a trigger.
    examples:
      - name: Triggers_Stop
        text: |-
               az datafactory trigger stop --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup" --trigger-name "exampleTrigger"
"""

helps['datafactory trigger query-by-factory'] = """
    type: command
    short-summary: Query triggers.
    examples:
      - name: Triggers_QueryByFactory
        text: |-
               az datafactory trigger query-by-factory --factory-name "exampleFactoryName"
               --parent-trigger-name "exampleTrigger" --resource-group "exampleResourceGroup"
"""

helps['datafactory trigger-run'] = """
    type: group
    short-summary: datafactory trigger-run
"""

helps['datafactory trigger-run rerun'] = """
    type: command
    short-summary: Rerun single trigger instance by runId.
    examples:
      - name: Triggers_Rerun
        text: |-
               az datafactory trigger-run rerun --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup" --run-id "2f7fdb90-5df1-4b8e-ac2f-064cfa58202b" --trigger-name
               "exampleTrigger"
"""

helps['datafactory trigger-run query-by-factory'] = """
    type: command
    short-summary: Query trigger runs.
    examples:
      - name: TriggerRuns_QueryByFactory
        text: |-
               az datafactory trigger-run query-by-factory --factory-name "exampleFactoryName" --filters
               operand=TriggerName operator=Equals values=exampleTrigger --last-updated-after
               "2018-06-16T00:36:44.3345758Z" --last-updated-before "2018-06-16T00:49:48.3686473Z"
               --resource-group "exampleResourceGroup"
"""

helps['datafactory data-flow'] = """
    type: group
    short-summary: datafactory data-flow
"""

helps['datafactory data-flow list'] = """
    type: command
    short-summary: Lists data flows.
    examples:
      - name: DataFlows_ListByFactory
        text: |-
               az datafactory data-flow list --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory data-flow show'] = """
    type: command
    short-summary: Gets a data flow.
    examples:
      - name: DataFlows_Get
        text: |-
               az datafactory data-flow show --data-flow-name "exampleDataFlow" --factory-name
               "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory data-flow create'] = """
    type: command
    short-summary: Creates or updates a data flow.
    examples:
      - name: DataFlows_Create
        text: |-
               az datafactory data-flow create --properties "{\\"type\\":\\"MappingDataFlow\\",\\"description\\
               ":\\"Sample demo data flow to convert currencies showing usage of union, derive and conditi
               onal split transformation.\\",\\"typeProperties\\":{\\"script\\":\\"source(output(PreviousConver
               sionRate as double,Country as string,DateTime1 as string,CurrentConversionRate as double),
               allowSchemaDrift: false,validateSchema: false) ~> USDCurrency\\\\nsource(output(PreviousConv
               ersionRate as double,Country as string,DateTime1 as string,CurrentConversionRate as double
               ),allowSchemaDrift: true,validateSchema: false) ~> CADSource\\\\nUSDCurrency, CADSource unio
               n(byName: true)~> Union\\\\nUnion derive(NewCurrencyRate = round(CurrentConversionRate*1.25)
               ) ~> NewCurrencyColumn\\\\nNewCurrencyColumn split(Country == 'USD',Country == 'CAD',disjoin
               t: false) ~> ConditionalSplit1@(USD, CAD)\\\\nConditionalSplit1@USD sink(saveMode:'overwrite
               ' ) ~> USDSink\\\\nConditionalSplit1@CAD sink(saveMode:'overwrite' ) ~> CADSink\\",\\"sinks\\":
               [{\\"name\\":\\"USDSink\\",\\"dataset\\":{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"USDO
               utput\\"}},{\\"name\\":\\"CADSink\\",\\"dataset\\":{\\"type\\":\\"DatasetReference\\",\\"referenceName
               \\":\\"CADOutput\\"}}],\\"sources\\":[{\\"name\\":\\"USDCurrency\\",\\"dataset\\":{\\"type\\":\\"Dataset
               Reference\\",\\"referenceName\\":\\"CurrencyDatasetUSD\\"}},{\\"name\\":\\"CADSource\\",\\"dataset\\"
               :{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CurrencyDatasetCAD\\"}}]}}"
               --data-flow-name "exampleDataFlow" --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup"
      - name: DataFlows_Update
        text: |-
               az datafactory data-flow create --properties "{\\"type\\":\\"MappingDataFlow\\",\\"description\\
               ":\\"Sample demo data flow to convert currencies showing usage of union, derive and conditi
               onal split transformation.\\",\\"typeProperties\\":{\\"script\\":\\"source(output(PreviousConver
               sionRate as double,Country as string,DateTime1 as string,CurrentConversionRate as double),
               allowSchemaDrift: false,validateSchema: false) ~> USDCurrency\\\\nsource(output(PreviousConv
               ersionRate as double,Country as string,DateTime1 as string,CurrentConversionRate as double
               ),allowSchemaDrift: true,validateSchema: false) ~> CADSource\\\\nUSDCurrency, CADSource unio
               n(byName: true)~> Union\\\\nUnion derive(NewCurrencyRate = round(CurrentConversionRate*1.25)
               ) ~> NewCurrencyColumn\\\\nNewCurrencyColumn split(Country == 'USD',Country == 'CAD',disjoin
               t: false) ~> ConditionalSplit1@(USD, CAD)\\\\nConditionalSplit1@USD sink(saveMode:'overwrite
               ' ) ~> USDSink\\\\nConditionalSplit1@CAD sink(saveMode:'overwrite' ) ~> CADSink\\",\\"sinks\\":
               [{\\"name\\":\\"USDSink\\",\\"dataset\\":{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"USDO
               utput\\"}},{\\"name\\":\\"CADSink\\",\\"dataset\\":{\\"type\\":\\"DatasetReference\\",\\"referenceName
               \\":\\"CADOutput\\"}}],\\"sources\\":[{\\"name\\":\\"USDCurrency\\",\\"dataset\\":{\\"type\\":\\"Dataset
               Reference\\",\\"referenceName\\":\\"CurrencyDatasetUSD\\"}},{\\"name\\":\\"CADSource\\",\\"dataset\\"
               :{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CurrencyDatasetCAD\\"}}]}}"
               --data-flow-name "exampleDataFlow" --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory data-flow update'] = """
    type: command
    short-summary: Creates or updates a data flow.
    examples:
      - name: DataFlows_Create
        text: |-
               az datafactory data-flow create --properties "{\\"type\\":\\"MappingDataFlow\\",\\"description\\
               ":\\"Sample demo data flow to convert currencies showing usage of union, derive and conditi
               onal split transformation.\\",\\"typeProperties\\":{\\"script\\":\\"source(output(PreviousConver
               sionRate as double,Country as string,DateTime1 as string,CurrentConversionRate as double),
               allowSchemaDrift: false,validateSchema: false) ~> USDCurrency\\\\nsource(output(PreviousConv
               ersionRate as double,Country as string,DateTime1 as string,CurrentConversionRate as double
               ),allowSchemaDrift: true,validateSchema: false) ~> CADSource\\\\nUSDCurrency, CADSource unio
               n(byName: true)~> Union\\\\nUnion derive(NewCurrencyRate = round(CurrentConversionRate*1.25)
               ) ~> NewCurrencyColumn\\\\nNewCurrencyColumn split(Country == 'USD',Country == 'CAD',disjoin
               t: false) ~> ConditionalSplit1@(USD, CAD)\\\\nConditionalSplit1@USD sink(saveMode:'overwrite
               ' ) ~> USDSink\\\\nConditionalSplit1@CAD sink(saveMode:'overwrite' ) ~> CADSink\\",\\"sinks\\":
               [{\\"name\\":\\"USDSink\\",\\"dataset\\":{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"USDO
               utput\\"}},{\\"name\\":\\"CADSink\\",\\"dataset\\":{\\"type\\":\\"DatasetReference\\",\\"referenceName
               \\":\\"CADOutput\\"}}],\\"sources\\":[{\\"name\\":\\"USDCurrency\\",\\"dataset\\":{\\"type\\":\\"Dataset
               Reference\\",\\"referenceName\\":\\"CurrencyDatasetUSD\\"}},{\\"name\\":\\"CADSource\\",\\"dataset\\"
               :{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CurrencyDatasetCAD\\"}}]}}"
               --data-flow-name "exampleDataFlow" --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup"
      - name: DataFlows_Update
        text: |-
               az datafactory data-flow create --properties "{\\"type\\":\\"MappingDataFlow\\",\\"description\\
               ":\\"Sample demo data flow to convert currencies showing usage of union, derive and conditi
               onal split transformation.\\",\\"typeProperties\\":{\\"script\\":\\"source(output(PreviousConver
               sionRate as double,Country as string,DateTime1 as string,CurrentConversionRate as double),
               allowSchemaDrift: false,validateSchema: false) ~> USDCurrency\\\\nsource(output(PreviousConv
               ersionRate as double,Country as string,DateTime1 as string,CurrentConversionRate as double
               ),allowSchemaDrift: true,validateSchema: false) ~> CADSource\\\\nUSDCurrency, CADSource unio
               n(byName: true)~> Union\\\\nUnion derive(NewCurrencyRate = round(CurrentConversionRate*1.25)
               ) ~> NewCurrencyColumn\\\\nNewCurrencyColumn split(Country == 'USD',Country == 'CAD',disjoin
               t: false) ~> ConditionalSplit1@(USD, CAD)\\\\nConditionalSplit1@USD sink(saveMode:'overwrite
               ' ) ~> USDSink\\\\nConditionalSplit1@CAD sink(saveMode:'overwrite' ) ~> CADSink\\",\\"sinks\\":
               [{\\"name\\":\\"USDSink\\",\\"dataset\\":{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"USDO
               utput\\"}},{\\"name\\":\\"CADSink\\",\\"dataset\\":{\\"type\\":\\"DatasetReference\\",\\"referenceName
               \\":\\"CADOutput\\"}}],\\"sources\\":[{\\"name\\":\\"USDCurrency\\",\\"dataset\\":{\\"type\\":\\"Dataset
               Reference\\",\\"referenceName\\":\\"CurrencyDatasetUSD\\"}},{\\"name\\":\\"CADSource\\",\\"dataset\\"
               :{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CurrencyDatasetCAD\\"}}]}}"
               --data-flow-name "exampleDataFlow" --factory-name "exampleFactoryName" --resource-group
               "exampleResourceGroup"
"""

helps['datafactory data-flow delete'] = """
    type: command
    short-summary: Deletes a data flow.
    examples:
      - name: DataFlows_Delete
        text: |-
               az datafactory data-flow delete --data-flow-name "exampleDataFlow" --factory-name
               "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory data-flow-debug-session'] = """
    type: group
    short-summary: datafactory data-flow-debug-session
"""

helps['datafactory data-flow-debug-session create'] = """
    type: command
    short-summary: Creates a data flow debug session.
    examples:
      - name: DataFlowDebugSession_Create
        text: |-
               az datafactory data-flow-debug-session create --factory-name "exampleFactoryName"
               --resource-group "exampleResourceGroup" --integration-runtime "{\\"name\\":\\"ir1\\",\\"propert
               ies\\":{\\"type\\":\\"Managed\\",\\"typeProperties\\":{\\"computeProperties\\":{\\"dataFlowPropertie
               s\\":{\\"computeType\\":\\"General\\",\\"coreCount\\":48,\\"timeToLive\\":10},\\"location\\":\\"AutoRe
               solve\\"}}}}" --time-to-live 60
"""

helps['datafactory data-flow-debug-session delete'] = """
    type: command
    short-summary: Deletes a data flow debug session.
    examples:
      - name: DataFlowDebugSession_Delete
        text: |-
               az datafactory data-flow-debug-session delete --factory-name "exampleFactoryName"
               --resource-group "exampleResourceGroup" --session-id
               "91fb57e0-8292-47be-89ff-c8f2d2bb2a7e"
"""

helps['datafactory data-flow-debug-session query-by-factory'] = """
    type: command
    short-summary: Query all active data flow debug sessions.
    examples:
      - name: DataFlowDebugSession_QueryByFactory
        text: |-
               az datafactory data-flow-debug-session query-by-factory --factory-name
               "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory data-flow-debug-session add-data-flow'] = """
    type: command
    short-summary: Add a data flow into debug session.
    examples:
      - name: DataFlowDebugSession_AddDataFlow
        text: |-
               az datafactory data-flow-debug-session add-data-flow --factory-name "exampleFactoryName"
               --resource-group "exampleResourceGroup" --data-flow "{\\"name\\":\\"dataflow1\\",\\"properties\\
               ":{\\"type\\":\\"MappingDataFlow\\",\\"typeProperties\\":{\\"script\\":\\"\\\\n\\\\nsource(output(\\\\n\\\\
               t\\\\tColumn_1 as string\\\\n\\\\t),\\\\n\\\\tallowSchemaDrift: true,\\\\n\\\\tvalidateSchema: false) ~>
                source1\\",\\"sinks\\":[],\\"sources\\":[{\\"name\\":\\"source1\\",\\"dataset\\":{\\"type\\":\\"Dataset
               Reference\\",\\"referenceName\\":\\"DelimitedText2\\"}}],\\"transformations\\":[]}}}" --datasets 
               "[{\\"name\\":\\"dataset1\\",\\"properties\\":{\\"type\\":\\"DelimitedText\\",\\"schema\\":[{\\"type\\":
               \\"String\\"}],\\"annotations\\":[],\\"linkedServiceName\\":{\\"type\\":\\"LinkedServiceReference\\"
               ,\\"referenceName\\":\\"linkedService5\\"},\\"typeProperties\\":{\\"columnDelimiter\\":\\",\\",\\"esc
               apeChar\\":\\"\\\\\\\\\\",\\"firstRowAsHeader\\":true,\\"location\\":{\\"type\\":\\"AzureBlobStorageLoca
               tion\\",\\"container\\":\\"dataflow-sample-data\\",\\"fileName\\":\\"Ansiencoding.csv\\"},\\"quoteCh
               ar\\":\\"\\\\\\"\\"}}}]" --debug-settings "{\\"datasetParameters\\":{\\"Movies\\":{\\"path\\":\\"abc\\"}
               ,\\"Output\\":{\\"time\\":\\"def\\"}},\\"parameters\\":{\\"sourcePath\\":\\"Toy\\"},\\"sourceSettings\\"
               :[{\\"rowLimit\\":1000,\\"sourceName\\":\\"source1\\"},{\\"rowLimit\\":222,\\"sourceName\\":\\"source
               2\\"}]}" --linked-services "[{\\"name\\":\\"linkedService1\\",\\"properties\\":{\\"type\\":\\"AzureB
               lobStorage\\",\\"annotations\\":[],\\"typeProperties\\":{\\"connectionString\\":\\"DefaultEndpoint
               sProtocol=https;AccountName=<storageName>;EndpointSuffix=core.windows.net;\\",\\"encryptedCr
               edential\\":\\"<credential>\\"}}}]" --session-id "f06ed247-9d07-49b2-b05e-2cb4a2fc871e"
"""

helps['datafactory data-flow-debug-session execute-command'] = """
    type: command
    short-summary: Execute a data flow debug command.
    examples:
      - name: DataFlowDebugSession_ExecuteCommand
        text: |-
               az datafactory data-flow-debug-session execute-command --factory-name
               "exampleFactoryName" --resource-group "exampleResourceGroup" --command
               "executePreviewQuery" --command-payload row-limits=100 stream-name=source1 --session-id
               "f06ed247-9d07-49b2-b05e-2cb4a2fc871e"
"""
