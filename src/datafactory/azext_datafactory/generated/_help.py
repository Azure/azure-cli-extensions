# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
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
               az datafactory factory show --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory factory create'] = """
    type: command
    short-summary: Creates or updates a factory.
    examples:
      - name: Factories_CreateOrUpdate
        text: |-
               az datafactory factory create --location "East US" --factory-name "exampleFactoryName" --resource-group \
"exampleResourceGroup"
"""

helps['datafactory factory update'] = """
    type: command
    short-summary: Updates a factory.
    examples:
      - name: Factories_Update
        text: |-
               az datafactory factory update --factory-name "exampleFactoryName" --tags exampleTag=exampleValue --resou\
rce-group "exampleResourceGroup"
"""

helps['datafactory factory delete'] = """
    type: command
    short-summary: Deletes a factory.
    examples:
      - name: Factories_Delete
        text: |-
               az datafactory factory delete --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup\
"
"""

helps['datafactory factory configure-factory-repo'] = """
    type: command
    short-summary: Updates a factory's repo information.
    examples:
      - name: Factories_ConfigureFactoryRepo
        text: |-
               az datafactory factory configure-factory-repo --factory-resource-id "/subscriptions/12345678-1234-1234-1\
234-12345678abc/resourceGroups/exampleResourceGroup/providers/Microsoft.DataFactory/factories/exampleFactoryName" --rep\
o-configuration "{\\"type\\":\\"FactoryVSTSConfiguration\\",\\"accountName\\":\\"ADF\\",\\"collaborationBranch\\":\\"ma\
ster\\",\\"lastCommitId\\":\\"\\",\\"projectName\\":\\"project\\",\\"repositoryName\\":\\"repo\\",\\"rootFolder\\":\\"/\
\\",\\"tenantId\\":\\"\\"}" --location-id "East US"
"""

helps['datafactory factory get-data-plane-access'] = """
    type: command
    short-summary: Get Data Plane access.
    examples:
      - name: Factories_GetDataPlaneAccess
        text: |-
               az datafactory factory get-data-plane-access --factory-name "exampleFactoryName" --access-resource-path \
"" --expire-time "2018-11-10T09:46:20.2659347Z" --permissions "r" --profile-name "DefaultProfile" --start-time "2018-11\
-10T02:46:20.2659347Z" --resource-group "exampleResourceGroup"
"""

helps['datafactory factory get-git-hub-access-token'] = """
    type: command
    short-summary: Get GitHub Access Token.
    examples:
      - name: Factories_GetGitHubAccessToken
        text: |-
               az datafactory factory get-git-hub-access-token --factory-name "exampleFactoryName" --git-hub-access-cod\
e "some" --git-hub-access-token-base-url "some" --git-hub-client-id "some" --resource-group "exampleResourceGroup"
"""

helps['datafactory exposure-control'] = """
    type: group
    short-summary: datafactory exposure-control
"""

helps['datafactory exposure-control get-feature-value'] = """
    type: command
    short-summary: Get exposure control feature for specific location.
    examples:
      - name: ExposureControl_GetFeatureValue
        text: |-
               az datafactory exposure-control get-feature-value --feature-name "ADFIntegrationRuntimeSharingRbac" --fe\
ature-type "Feature" --location-id "WestEurope"
"""

helps['datafactory exposure-control get-feature-value-by-factory'] = """
    type: command
    short-summary: Get exposure control feature for specific factory.
    examples:
      - name: ExposureControl_GetFeatureValueByFactory
        text: |-
               az datafactory exposure-control get-feature-value-by-factory --feature-name "ADFIntegrationRuntimeSharin\
gRbac" --feature-type "Feature" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
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
               az datafactory integration-runtime list --factory-name "exampleFactoryName" --resource-group "exampleRes\
ourceGroup"
"""

helps['datafactory integration-runtime show'] = """
    type: command
    short-summary: Gets an integration runtime.
    examples:
      - name: IntegrationRuntimes_Get
        text: |-
               az datafactory integration-runtime show --factory-name "exampleFactoryName" --integration-runtime-name "\
exampleIntegrationRuntime" --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime managed'] = """
    type: group
    short-summary: datafactory integration-runtime sub group managed
"""

helps['datafactory integration-runtime managed create'] = """
    type: command
    short-summary: Creates or updates an integration runtime.
    examples:
      - name: IntegrationRuntimes_Create
        text: |-
               az datafactory integration-runtime managed create --factory-name "exampleFactoryName" --type "SelfHosted\
" --description "A selfhosted integration runtime" --integration-runtime-name "exampleIntegrationRuntime" --resource-gr\
oup "exampleResourceGroup"
"""

helps['datafactory integration-runtime self-hosted'] = """
    type: group
    short-summary: datafactory integration-runtime sub group self-hosted
"""

helps['datafactory integration-runtime self-hosted create'] = """
    type: command
    short-summary: Creates or updates an integration runtime.
    examples:
      - name: IntegrationRuntimes_Create
        text: |-
               az datafactory integration-runtime self-hosted create --factory-name "exampleFactoryName" --type "SelfHo\
sted" --description "A selfhosted integration runtime" --integration-runtime-name "exampleIntegrationRuntime" --resourc\
e-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime update'] = """
    type: command
    short-summary: Updates an integration runtime.
    examples:
      - name: IntegrationRuntimes_Update
        text: |-
               az datafactory integration-runtime update --factory-name "exampleFactoryName" --integration-runtime-name\
 "exampleIntegrationRuntime" --resource-group "exampleResourceGroup" --auto-update "Off" --update-delay-offset "\\"PT3H\
\\""
"""

helps['datafactory integration-runtime delete'] = """
    type: command
    short-summary: Deletes an integration runtime.
    examples:
      - name: IntegrationRuntimes_Delete
        text: |-
               az datafactory integration-runtime delete --factory-name "exampleFactoryName" --integration-runtime-name\
 "exampleIntegrationRuntime" --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime create-linked-integration-runtime'] = """
    type: command
    short-summary: Create a linked integration runtime entry in a shared integration runtime.
    examples:
      - name: IntegrationRuntimes_CreateLinkedIntegrationRuntime
        text: |-
               az datafactory integration-runtime create-linked-integration-runtime --name "bfa92911-9fb6-4fbe-8f23-bea\
e87bc1c83" --data-factory-location "West US" --data-factory-name "e9955d6d-56ea-4be3-841c-52a12c1a9981" --subscription-\
id "061774c7-4b5a-4159-a55b-365581830283" --factory-name "exampleFactoryName" --integration-runtime-name "exampleIntegr\
ationRuntime" --resource-group "exampleResourceGroup" --subscription-id "12345678-1234-1234-1234-12345678abc"
"""

helps['datafactory integration-runtime get-connection-info'] = """
    type: command
    short-summary: Gets the on-premises integration runtime connection information for encrypting the on-premises data \
source credentials.
    examples:
      - name: IntegrationRuntimes_GetConnectionInfo
        text: |-
               az datafactory integration-runtime get-connection-info --factory-name "exampleFactoryName" --integration\
-runtime-name "exampleIntegrationRuntime" --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime get-monitoring-data'] = """
    type: command
    short-summary: Get the integration runtime monitoring data, which includes the monitor data for all the nodes under\
 this integration runtime.
    examples:
      - name: IntegrationRuntimes_GetMonitoringData
        text: |-
               az datafactory integration-runtime get-monitoring-data --factory-name "exampleFactoryName" --integration\
-runtime-name "exampleIntegrationRuntime" --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime get-status'] = """
    type: command
    short-summary: Gets detailed status information for an integration runtime.
    examples:
      - name: IntegrationRuntimes_GetStatus
        text: |-
               az datafactory integration-runtime get-status --factory-name "exampleFactoryName" --integration-runtime-\
name "exampleIntegrationRuntime" --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime list-auth-key'] = """
    type: command
    short-summary: Retrieves the authentication keys for an integration runtime.
    examples:
      - name: IntegrationRuntimes_ListAuthKeys
        text: |-
               az datafactory integration-runtime list-auth-key --factory-name "exampleFactoryName" --integration-runti\
me-name "exampleIntegrationRuntime" --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime regenerate-auth-key'] = """
    type: command
    short-summary: Regenerates the authentication key for an integration runtime.
    examples:
      - name: IntegrationRuntimes_RegenerateAuthKey
        text: |-
               az datafactory integration-runtime regenerate-auth-key --factory-name "exampleFactoryName" --integration\
-runtime-name "exampleIntegrationRuntime" --key-name "authKey2" --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime remove-link'] = """
    type: command
    short-summary: Remove all linked integration runtimes under specific data factory in a self-hosted integration runt\
ime.
    examples:
      - name: IntegrationRuntimes_Upgrade
        text: |-
               az datafactory integration-runtime remove-link --factory-name "exampleFactoryName" --integration-runtime\
-name "exampleIntegrationRuntime" --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime start'] = """
    type: command
    short-summary: Starts a ManagedReserved type integration runtime.
    examples:
      - name: IntegrationRuntimes_Start
        text: |-
               az datafactory integration-runtime start --factory-name "exampleFactoryName" --integration-runtime-name \
"exampleManagedIntegrationRuntime" --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime stop'] = """
    type: command
    short-summary: Stops a ManagedReserved type integration runtime.
    examples:
      - name: IntegrationRuntimes_Stop
        text: |-
               az datafactory integration-runtime stop --factory-name "exampleFactoryName" --integration-runtime-name "\
exampleManagedIntegrationRuntime" --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime sync-credentials'] = """
    type: command
    short-summary: Force the integration runtime to synchronize credentials across integration runtime nodes, and this \
will override the credentials across all worker nodes with those available on the dispatcher node. If you already have \
the latest credential backup file, you should manually import it (preferred) on any self-hosted integration runtime nod\
e than using this API directly.
    examples:
      - name: IntegrationRuntimes_SyncCredentials
        text: |-
               az datafactory integration-runtime sync-credentials --factory-name "exampleFactoryName" --integration-ru\
ntime-name "exampleIntegrationRuntime" --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime upgrade'] = """
    type: command
    short-summary: Upgrade self-hosted integration runtime to latest version if availability.
    examples:
      - name: IntegrationRuntimes_Upgrade
        text: |-
               az datafactory integration-runtime upgrade --factory-name "exampleFactoryName" --integration-runtime-nam\
e "exampleIntegrationRuntime" --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime-object-metadata'] = """
    type: group
    short-summary: datafactory integration-runtime-object-metadata
"""

helps['datafactory integration-runtime-object-metadata get'] = """
    type: command
    short-summary: Get a SSIS integration runtime object metadata by specified path. The return is pageable metadata li\
st.
    examples:
      - name: IntegrationRuntimeObjectMetadata_Get
        text: |-
               az datafactory integration-runtime-object-metadata get --factory-name "exampleFactoryName" --metadata-pa\
th "ssisFolders" --integration-runtime-name "testactivityv2" --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime-object-metadata refresh'] = """
    type: command
    short-summary: Refresh a SSIS integration runtime object metadata.
    examples:
      - name: IntegrationRuntimeObjectMetadata_Refresh
        text: |-
               az datafactory integration-runtime-object-metadata refresh --factory-name "exampleFactoryName" --integra\
tion-runtime-name "testactivityv2" --resource-group "exampleResourceGroup"
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
               az datafactory integration-runtime-node show --factory-name "exampleFactoryName" --integration-runtime-n\
ame "exampleIntegrationRuntime" --node-name "Node_1" --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime-node update'] = """
    type: command
    short-summary: Updates a self-hosted integration runtime node.
    examples:
      - name: IntegrationRuntimeNodes_Update
        text: |-
               az datafactory integration-runtime-node update --factory-name "exampleFactoryName" --integration-runtime\
-name "exampleIntegrationRuntime" --node-name "Node_1" --resource-group "exampleResourceGroup" --concurrent-jobs-limit \
2
"""

helps['datafactory integration-runtime-node delete'] = """
    type: command
    short-summary: Deletes a self-hosted integration runtime node.
    examples:
      - name: IntegrationRuntimesNodes_Delete
        text: |-
               az datafactory integration-runtime-node delete --factory-name "exampleFactoryName" --integration-runtime\
-name "exampleIntegrationRuntime" --node-name "Node_1" --resource-group "exampleResourceGroup"
"""

helps['datafactory integration-runtime-node get-ip-address'] = """
    type: command
    short-summary: Get the IP address of self-hosted integration runtime node.
    examples:
      - name: IntegrationRuntimeNodes_GetIpAddress
        text: |-
               az datafactory integration-runtime-node get-ip-address --factory-name "exampleFactoryName" --integration\
-runtime-name "exampleIntegrationRuntime" --node-name "Node_1" --resource-group "exampleResourceGroup"
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
               az datafactory linked-service list --factory-name "exampleFactoryName" --resource-group "exampleResource\
Group"
"""

helps['datafactory linked-service show'] = """
    type: command
    short-summary: Gets a linked service.
    examples:
      - name: LinkedServices_Get
        text: |-
               az datafactory linked-service show --factory-name "exampleFactoryName" --linked-service-name "exampleLin\
kedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service amazon-m-w-s'] = """
    type: group
    short-summary: datafactory linked-service sub group amazon-m-w-s
"""

helps['datafactory linked-service amazon-m-w-s create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service amazon-m-w-s create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service amazon-m-w-s create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceG\
roup"
"""

helps['datafactory linked-service amazon-m-w-s update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service amazon-m-w-s create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service amazon-m-w-s create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceG\
roup"
"""

helps['datafactory linked-service amazon-redshift'] = """
    type: group
    short-summary: datafactory linked-service sub group amazon-redshift
"""

helps['datafactory linked-service amazon-redshift create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service amazon-redshift create --factory-name "exampleFactoryName" --type "AzureSt\
orage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service amazon-redshift create --factory-name "exampleFactoryName" --type "AzureSt\
orage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResour\
ceGroup"
"""

helps['datafactory linked-service amazon-redshift update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service amazon-redshift create --factory-name "exampleFactoryName" --type "AzureSt\
orage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service amazon-redshift create --factory-name "exampleFactoryName" --type "AzureSt\
orage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResour\
ceGroup"
"""

helps['datafactory linked-service amazon-s3'] = """
    type: group
    short-summary: datafactory linked-service sub group amazon-s3
"""

helps['datafactory linked-service amazon-s3 create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service amazon-s3 create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service amazon-s3 create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service amazon-s3 update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service amazon-s3 create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service amazon-s3 create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service azure-batch'] = """
    type: group
    short-summary: datafactory linked-service sub group azure-batch
"""

helps['datafactory linked-service azure-batch create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-batch create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --type-properties-linked-service-name "\\"exampleLinkedService\\"" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-batch create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --description "Example description" --type-properties-linked-service-name "\\"exampleLinkedService\\"" --resource-gr\
oup "exampleResourceGroup"
"""

helps['datafactory linked-service azure-batch update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-batch create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --type-properties-linked-service-name "\\"exampleLinkedService\\"" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-batch create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --description "Example description" --type-properties-linked-service-name "\\"exampleLinkedService\\"" --resource-gr\
oup "exampleResourceGroup"
"""

helps['datafactory linked-service azure-blob-f-s'] = """
    type: group
    short-summary: datafactory linked-service sub group azure-blob-f-s
"""

helps['datafactory linked-service azure-blob-f-s create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-blob-f-s create --factory-name "exampleFactoryName" --type "AzureSto\
rage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-blob-f-s create --factory-name "exampleFactoryName" --type "AzureSto\
rage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourc\
eGroup"
"""

helps['datafactory linked-service azure-blob-f-s update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-blob-f-s create --factory-name "exampleFactoryName" --type "AzureSto\
rage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-blob-f-s create --factory-name "exampleFactoryName" --type "AzureSto\
rage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourc\
eGroup"
"""

helps['datafactory linked-service azure-blob-storage'] = """
    type: group
    short-summary: datafactory linked-service sub group azure-blob-storage
"""

helps['datafactory linked-service azure-blob-storage create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-blob-storage create --factory-name "exampleFactoryName" --type "Azur\
eStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-blob-storage create --factory-name "exampleFactoryName" --type "Azur\
eStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleRes\
ourceGroup"
"""

helps['datafactory linked-service azure-blob-storage update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-blob-storage create --factory-name "exampleFactoryName" --type "Azur\
eStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-blob-storage create --factory-name "exampleFactoryName" --type "Azur\
eStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleRes\
ourceGroup"
"""

helps['datafactory linked-service azure-data-explorer'] = """
    type: group
    short-summary: datafactory linked-service sub group azure-data-explorer
"""

helps['datafactory linked-service azure-data-explorer create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-data-explorer create --factory-name "exampleFactoryName" --type "Azu\
reStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-data-explorer create --factory-name "exampleFactoryName" --type "Azu\
reStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleRe\
sourceGroup"
"""

helps['datafactory linked-service azure-data-explorer update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-data-explorer create --factory-name "exampleFactoryName" --type "Azu\
reStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-data-explorer create --factory-name "exampleFactoryName" --type "Azu\
reStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleRe\
sourceGroup"
"""

helps['datafactory linked-service azure-data-lake-analytics'] = """
    type: group
    short-summary: datafactory linked-service sub group azure-data-lake-analytics
"""

helps['datafactory linked-service azure-data-lake-analytics create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-data-lake-analytics create --factory-name "exampleFactoryName" --typ\
e "AzureStorage" --linked-service-name "exampleLinkedService" --type-properties-resource-group-name "\\"exampleResource\
Group\\"" --type-properties-subscription-id "\\"12345678-1234-1234-1234-12345678abc\\""
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-data-lake-analytics create --factory-name "exampleFactoryName" --typ\
e "AzureStorage" --description "Example description" --linked-service-name "exampleLinkedService" --type-properties-res\
ource-group-name "\\"exampleResourceGroup\\"" --type-properties-subscription-id "\\"12345678-1234-1234-1234-12345678abc\
\\""
"""

helps['datafactory linked-service azure-data-lake-analytics update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-data-lake-analytics create --factory-name "exampleFactoryName" --typ\
e "AzureStorage" --linked-service-name "exampleLinkedService" --type-properties-resource-group-name "\\"exampleResource\
Group\\"" --type-properties-subscription-id "\\"12345678-1234-1234-1234-12345678abc\\""
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-data-lake-analytics create --factory-name "exampleFactoryName" --typ\
e "AzureStorage" --description "Example description" --linked-service-name "exampleLinkedService" --type-properties-res\
ource-group-name "\\"exampleResourceGroup\\"" --type-properties-subscription-id "\\"12345678-1234-1234-1234-12345678abc\
\\""
"""

helps['datafactory linked-service azure-data-lake-store'] = """
    type: group
    short-summary: datafactory linked-service sub group azure-data-lake-store
"""

helps['datafactory linked-service azure-data-lake-store create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-data-lake-store create --factory-name "exampleFactoryName" --type "A\
zureStorage" --linked-service-name "exampleLinkedService" --type-properties-resource-group-name "\\"exampleResourceGrou\
p\\"" --type-properties-subscription-id "\\"12345678-1234-1234-1234-12345678abc\\""
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-data-lake-store create --factory-name "exampleFactoryName" --type "A\
zureStorage" --description "Example description" --linked-service-name "exampleLinkedService" --type-properties-resourc\
e-group-name "\\"exampleResourceGroup\\"" --type-properties-subscription-id "\\"12345678-1234-1234-1234-12345678abc\\""
"""

helps['datafactory linked-service azure-data-lake-store update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-data-lake-store create --factory-name "exampleFactoryName" --type "A\
zureStorage" --linked-service-name "exampleLinkedService" --type-properties-resource-group-name "\\"exampleResourceGrou\
p\\"" --type-properties-subscription-id "\\"12345678-1234-1234-1234-12345678abc\\""
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-data-lake-store create --factory-name "exampleFactoryName" --type "A\
zureStorage" --description "Example description" --linked-service-name "exampleLinkedService" --type-properties-resourc\
e-group-name "\\"exampleResourceGroup\\"" --type-properties-subscription-id "\\"12345678-1234-1234-1234-12345678abc\\""
"""

helps['datafactory linked-service azure-databricks'] = """
    type: group
    short-summary: datafactory linked-service sub group azure-databricks
"""

helps['datafactory linked-service azure-databricks create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-databricks create --factory-name "exampleFactoryName" --type "AzureS\
torage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-databricks create --factory-name "exampleFactoryName" --type "AzureS\
torage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResou\
rceGroup"
"""

helps['datafactory linked-service azure-databricks update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-databricks create --factory-name "exampleFactoryName" --type "AzureS\
torage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-databricks create --factory-name "exampleFactoryName" --type "AzureS\
torage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResou\
rceGroup"
"""

helps['datafactory linked-service azure-file-storage'] = """
    type: group
    short-summary: datafactory linked-service sub group azure-file-storage
"""

helps['datafactory linked-service azure-file-storage create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-file-storage create --factory-name "exampleFactoryName" --type "Azur\
eStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-file-storage create --factory-name "exampleFactoryName" --type "Azur\
eStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleRes\
ourceGroup"
"""

helps['datafactory linked-service azure-file-storage update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-file-storage create --factory-name "exampleFactoryName" --type "Azur\
eStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-file-storage create --factory-name "exampleFactoryName" --type "Azur\
eStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleRes\
ourceGroup"
"""

helps['datafactory linked-service azure-function'] = """
    type: group
    short-summary: datafactory linked-service sub group azure-function
"""

helps['datafactory linked-service azure-function create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-function create --factory-name "exampleFactoryName" --type "AzureSto\
rage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-function create --factory-name "exampleFactoryName" --type "AzureSto\
rage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourc\
eGroup"
"""

helps['datafactory linked-service azure-function update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-function create --factory-name "exampleFactoryName" --type "AzureSto\
rage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-function create --factory-name "exampleFactoryName" --type "AzureSto\
rage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourc\
eGroup"
"""

helps['datafactory linked-service azure-key-vault'] = """
    type: group
    short-summary: datafactory linked-service sub group azure-key-vault
"""

helps['datafactory linked-service azure-key-vault create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-key-vault create --factory-name "exampleFactoryName" --type "AzureSt\
orage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-key-vault create --factory-name "exampleFactoryName" --type "AzureSt\
orage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResour\
ceGroup"
"""

helps['datafactory linked-service azure-key-vault update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-key-vault create --factory-name "exampleFactoryName" --type "AzureSt\
orage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-key-vault create --factory-name "exampleFactoryName" --type "AzureSt\
orage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResour\
ceGroup"
"""

helps['datafactory linked-service azure-m-l'] = """
    type: group
    short-summary: datafactory linked-service sub group azure-m-l
"""

helps['datafactory linked-service azure-m-l create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-m-l create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-m-l create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service azure-m-l update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-m-l create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-m-l create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service azure-m-l-service'] = """
    type: group
    short-summary: datafactory linked-service sub group azure-m-l-service
"""

helps['datafactory linked-service azure-m-l-service create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-m-l-service create --factory-name "exampleFactoryName" --type "Azure\
Storage" --linked-service-name "exampleLinkedService" --type-properties-resource-group-name "\\"exampleResourceGroup\\"\
" --type-properties-subscription-id "\\"12345678-1234-1234-1234-12345678abc\\""
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-m-l-service create --factory-name "exampleFactoryName" --type "Azure\
Storage" --description "Example description" --linked-service-name "exampleLinkedService" --type-properties-resource-gr\
oup-name "\\"exampleResourceGroup\\"" --type-properties-subscription-id "\\"12345678-1234-1234-1234-12345678abc\\""
"""

helps['datafactory linked-service azure-m-l-service update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-m-l-service create --factory-name "exampleFactoryName" --type "Azure\
Storage" --linked-service-name "exampleLinkedService" --type-properties-resource-group-name "\\"exampleResourceGroup\\"\
" --type-properties-subscription-id "\\"12345678-1234-1234-1234-12345678abc\\""
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-m-l-service create --factory-name "exampleFactoryName" --type "Azure\
Storage" --description "Example description" --linked-service-name "exampleLinkedService" --type-properties-resource-gr\
oup-name "\\"exampleResourceGroup\\"" --type-properties-subscription-id "\\"12345678-1234-1234-1234-12345678abc\\""
"""

helps['datafactory linked-service azure-maria-d-b'] = """
    type: group
    short-summary: datafactory linked-service sub group azure-maria-d-b
"""

helps['datafactory linked-service azure-maria-d-b create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-maria-d-b create --factory-name "exampleFactoryName" --type "AzureSt\
orage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-maria-d-b create --factory-name "exampleFactoryName" --type "AzureSt\
orage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResour\
ceGroup"
"""

helps['datafactory linked-service azure-maria-d-b update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-maria-d-b create --factory-name "exampleFactoryName" --type "AzureSt\
orage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-maria-d-b create --factory-name "exampleFactoryName" --type "AzureSt\
orage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResour\
ceGroup"
"""

helps['datafactory linked-service azure-my-sql'] = """
    type: group
    short-summary: datafactory linked-service sub group azure-my-sql
"""

helps['datafactory linked-service azure-my-sql create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-my-sql create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-my-sql create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceG\
roup"
"""

helps['datafactory linked-service azure-my-sql update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-my-sql create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-my-sql create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceG\
roup"
"""

helps['datafactory linked-service azure-postgre-sql'] = """
    type: group
    short-summary: datafactory linked-service sub group azure-postgre-sql
"""

helps['datafactory linked-service azure-postgre-sql create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-postgre-sql create --factory-name "exampleFactoryName" --type "Azure\
Storage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-postgre-sql create --factory-name "exampleFactoryName" --type "Azure\
Storage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleReso\
urceGroup"
"""

helps['datafactory linked-service azure-postgre-sql update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-postgre-sql create --factory-name "exampleFactoryName" --type "Azure\
Storage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-postgre-sql create --factory-name "exampleFactoryName" --type "Azure\
Storage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleReso\
urceGroup"
"""

helps['datafactory linked-service azure-search'] = """
    type: group
    short-summary: datafactory linked-service sub group azure-search
"""

helps['datafactory linked-service azure-search create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-search create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-search create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceG\
roup"
"""

helps['datafactory linked-service azure-search update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-search create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-search create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceG\
roup"
"""

helps['datafactory linked-service azure-sql-d-w'] = """
    type: group
    short-summary: datafactory linked-service sub group azure-sql-d-w
"""

helps['datafactory linked-service azure-sql-d-w create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-sql-d-w create --factory-name "exampleFactoryName" --type "AzureStor\
age" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-sql-d-w create --factory-name "exampleFactoryName" --type "AzureStor\
age" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResource\
Group"
"""

helps['datafactory linked-service azure-sql-d-w update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-sql-d-w create --factory-name "exampleFactoryName" --type "AzureStor\
age" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-sql-d-w create --factory-name "exampleFactoryName" --type "AzureStor\
age" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResource\
Group"
"""

helps['datafactory linked-service azure-sql-database'] = """
    type: group
    short-summary: datafactory linked-service sub group azure-sql-database
"""

helps['datafactory linked-service azure-sql-database create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-sql-database create --factory-name "exampleFactoryName" --type "Azur\
eStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-sql-database create --factory-name "exampleFactoryName" --type "Azur\
eStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleRes\
ourceGroup"
"""

helps['datafactory linked-service azure-sql-database update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-sql-database create --factory-name "exampleFactoryName" --type "Azur\
eStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-sql-database create --factory-name "exampleFactoryName" --type "Azur\
eStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleRes\
ourceGroup"
"""

helps['datafactory linked-service azure-sql-m-i'] = """
    type: group
    short-summary: datafactory linked-service sub group azure-sql-m-i
"""

helps['datafactory linked-service azure-sql-m-i create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-sql-m-i create --factory-name "exampleFactoryName" --type "AzureStor\
age" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-sql-m-i create --factory-name "exampleFactoryName" --type "AzureStor\
age" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResource\
Group"
"""

helps['datafactory linked-service azure-sql-m-i update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-sql-m-i create --factory-name "exampleFactoryName" --type "AzureStor\
age" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-sql-m-i create --factory-name "exampleFactoryName" --type "AzureStor\
age" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResource\
Group"
"""

helps['datafactory linked-service azure-storage'] = """
    type: group
    short-summary: datafactory linked-service sub group azure-storage
"""

helps['datafactory linked-service azure-storage create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-storage create --factory-name "exampleFactoryName" --type "AzureStor\
age" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-storage create --factory-name "exampleFactoryName" --type "AzureStor\
age" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResource\
Group"
"""

helps['datafactory linked-service azure-storage update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-storage create --factory-name "exampleFactoryName" --type "AzureStor\
age" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-storage create --factory-name "exampleFactoryName" --type "AzureStor\
age" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResource\
Group"
"""

helps['datafactory linked-service azure-table-storage'] = """
    type: group
    short-summary: datafactory linked-service sub group azure-table-storage
"""

helps['datafactory linked-service azure-table-storage create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-table-storage create --factory-name "exampleFactoryName" --type "Azu\
reStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-table-storage create --factory-name "exampleFactoryName" --type "Azu\
reStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleRe\
sourceGroup"
"""

helps['datafactory linked-service azure-table-storage update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service azure-table-storage create --factory-name "exampleFactoryName" --type "Azu\
reStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service azure-table-storage create --factory-name "exampleFactoryName" --type "Azu\
reStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleRe\
sourceGroup"
"""

helps['datafactory linked-service cassandra'] = """
    type: group
    short-summary: datafactory linked-service sub group cassandra
"""

helps['datafactory linked-service cassandra create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service cassandra create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service cassandra create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service cassandra update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service cassandra create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service cassandra create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service common-data-service-for-apps'] = """
    type: group
    short-summary: datafactory linked-service sub group common-data-service-for-apps
"""

helps['datafactory linked-service common-data-service-for-apps create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service common-data-service-for-apps create --factory-name "exampleFactoryName" --\
type "AzureStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service common-data-service-for-apps create --factory-name "exampleFactoryName" --\
type "AzureStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "\
exampleResourceGroup"
"""

helps['datafactory linked-service common-data-service-for-apps update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service common-data-service-for-apps create --factory-name "exampleFactoryName" --\
type "AzureStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service common-data-service-for-apps create --factory-name "exampleFactoryName" --\
type "AzureStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "\
exampleResourceGroup"
"""

helps['datafactory linked-service concur'] = """
    type: group
    short-summary: datafactory linked-service sub group concur
"""

helps['datafactory linked-service concur create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service concur create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service concur create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service concur update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service concur create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service concur create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service cosmos-db'] = """
    type: group
    short-summary: datafactory linked-service sub group cosmos-db
"""

helps['datafactory linked-service cosmos-db create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service cosmos-db create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service cosmos-db create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service cosmos-db update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service cosmos-db create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service cosmos-db create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service cosmos-db-mongo-db-api'] = """
    type: group
    short-summary: datafactory linked-service sub group cosmos-db-mongo-db-api
"""

helps['datafactory linked-service cosmos-db-mongo-db-api create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service cosmos-db-mongo-db-api create --factory-name "exampleFactoryName" --type "\
AzureStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service cosmos-db-mongo-db-api create --factory-name "exampleFactoryName" --type "\
AzureStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampl\
eResourceGroup"
"""

helps['datafactory linked-service cosmos-db-mongo-db-api update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service cosmos-db-mongo-db-api create --factory-name "exampleFactoryName" --type "\
AzureStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service cosmos-db-mongo-db-api create --factory-name "exampleFactoryName" --type "\
AzureStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampl\
eResourceGroup"
"""

helps['datafactory linked-service couchbase'] = """
    type: group
    short-summary: datafactory linked-service sub group couchbase
"""

helps['datafactory linked-service couchbase create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service couchbase create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service couchbase create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service couchbase update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service couchbase create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service couchbase create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service custom-data-source'] = """
    type: group
    short-summary: datafactory linked-service sub group custom-data-source
"""

helps['datafactory linked-service custom-data-source create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service custom-data-source create --factory-name "exampleFactoryName" --type "Azur\
eStorage" --type-properties "{\\"connectionString\\":{\\"type\\":\\"SecureString\\",\\"value\\":\\"DefaultEndpointsProt\
ocol=https;AccountName=examplestorageaccount;AccountKey=<storage key>\\"}}" --linked-service-name "exampleLinkedService\
" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service custom-data-source create --factory-name "exampleFactoryName" --type "Azur\
eStorage" --description "Example description" --type-properties "{\\"connectionString\\":{\\"type\\":\\"SecureString\\"\
,\\"value\\":\\"DefaultEndpointsProtocol=https;AccountName=examplestorageaccount;AccountKey=<storage key>\\"}}" --linke\
d-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service custom-data-source update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service custom-data-source create --factory-name "exampleFactoryName" --type "Azur\
eStorage" --type-properties "{\\"connectionString\\":{\\"type\\":\\"SecureString\\",\\"value\\":\\"DefaultEndpointsProt\
ocol=https;AccountName=examplestorageaccount;AccountKey=<storage key>\\"}}" --linked-service-name "exampleLinkedService\
" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service custom-data-source create --factory-name "exampleFactoryName" --type "Azur\
eStorage" --description "Example description" --type-properties "{\\"connectionString\\":{\\"type\\":\\"SecureString\\"\
,\\"value\\":\\"DefaultEndpointsProtocol=https;AccountName=examplestorageaccount;AccountKey=<storage key>\\"}}" --linke\
d-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service db2'] = """
    type: group
    short-summary: datafactory linked-service sub group db2
"""

helps['datafactory linked-service db2 create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service db2 create --factory-name "exampleFactoryName" --type "AzureStorage" --lin\
ked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service db2 create --factory-name "exampleFactoryName" --type "AzureStorage" --des\
cription "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service db2 update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service db2 create --factory-name "exampleFactoryName" --type "AzureStorage" --lin\
ked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service db2 create --factory-name "exampleFactoryName" --type "AzureStorage" --des\
cription "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service drill'] = """
    type: group
    short-summary: datafactory linked-service sub group drill
"""

helps['datafactory linked-service drill create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service drill create --factory-name "exampleFactoryName" --type "AzureStorage" --l\
inked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service drill create --factory-name "exampleFactoryName" --type "AzureStorage" --d\
escription "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service drill update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service drill create --factory-name "exampleFactoryName" --type "AzureStorage" --l\
inked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service drill create --factory-name "exampleFactoryName" --type "AzureStorage" --d\
escription "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service dynamics'] = """
    type: group
    short-summary: datafactory linked-service sub group dynamics
"""

helps['datafactory linked-service dynamics create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service dynamics create --factory-name "exampleFactoryName" --type "AzureStorage" \
--linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service dynamics create --factory-name "exampleFactoryName" --type "AzureStorage" \
--description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup\
"
"""

helps['datafactory linked-service dynamics update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service dynamics create --factory-name "exampleFactoryName" --type "AzureStorage" \
--linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service dynamics create --factory-name "exampleFactoryName" --type "AzureStorage" \
--description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup\
"
"""

helps['datafactory linked-service dynamics-a-x'] = """
    type: group
    short-summary: datafactory linked-service sub group dynamics-a-x
"""

helps['datafactory linked-service dynamics-a-x create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service dynamics-a-x create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service dynamics-a-x create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceG\
roup"
"""

helps['datafactory linked-service dynamics-a-x update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service dynamics-a-x create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service dynamics-a-x create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceG\
roup"
"""

helps['datafactory linked-service dynamics-crm'] = """
    type: group
    short-summary: datafactory linked-service sub group dynamics-crm
"""

helps['datafactory linked-service dynamics-crm create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service dynamics-crm create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service dynamics-crm create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceG\
roup"
"""

helps['datafactory linked-service dynamics-crm update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service dynamics-crm create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service dynamics-crm create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceG\
roup"
"""

helps['datafactory linked-service eloqua'] = """
    type: group
    short-summary: datafactory linked-service sub group eloqua
"""

helps['datafactory linked-service eloqua create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service eloqua create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service eloqua create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service eloqua update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service eloqua create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service eloqua create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service file-server'] = """
    type: group
    short-summary: datafactory linked-service sub group file-server
"""

helps['datafactory linked-service file-server create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service file-server create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service file-server create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGr\
oup"
"""

helps['datafactory linked-service file-server update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service file-server create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service file-server create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGr\
oup"
"""

helps['datafactory linked-service ftp-server'] = """
    type: group
    short-summary: datafactory linked-service sub group ftp-server
"""

helps['datafactory linked-service ftp-server create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service ftp-server create --factory-name "exampleFactoryName" --type "AzureStorage\
" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service ftp-server create --factory-name "exampleFactoryName" --type "AzureStorage\
" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGro\
up"
"""

helps['datafactory linked-service ftp-server update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service ftp-server create --factory-name "exampleFactoryName" --type "AzureStorage\
" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service ftp-server create --factory-name "exampleFactoryName" --type "AzureStorage\
" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGro\
up"
"""

helps['datafactory linked-service google-ad-words'] = """
    type: group
    short-summary: datafactory linked-service sub group google-ad-words
"""

helps['datafactory linked-service google-ad-words create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service google-ad-words create --factory-name "exampleFactoryName" --type "AzureSt\
orage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service google-ad-words create --factory-name "exampleFactoryName" --type "AzureSt\
orage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResour\
ceGroup"
"""

helps['datafactory linked-service google-ad-words update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service google-ad-words create --factory-name "exampleFactoryName" --type "AzureSt\
orage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service google-ad-words create --factory-name "exampleFactoryName" --type "AzureSt\
orage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResour\
ceGroup"
"""

helps['datafactory linked-service google-big-query'] = """
    type: group
    short-summary: datafactory linked-service sub group google-big-query
"""

helps['datafactory linked-service google-big-query create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service google-big-query create --factory-name "exampleFactoryName" --type "AzureS\
torage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service google-big-query create --factory-name "exampleFactoryName" --type "AzureS\
torage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResou\
rceGroup"
"""

helps['datafactory linked-service google-big-query update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service google-big-query create --factory-name "exampleFactoryName" --type "AzureS\
torage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service google-big-query create --factory-name "exampleFactoryName" --type "AzureS\
torage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResou\
rceGroup"
"""

helps['datafactory linked-service google-cloud-storage'] = """
    type: group
    short-summary: datafactory linked-service sub group google-cloud-storage
"""

helps['datafactory linked-service google-cloud-storage create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service google-cloud-storage create --factory-name "exampleFactoryName" --type "Az\
ureStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service google-cloud-storage create --factory-name "exampleFactoryName" --type "Az\
ureStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleR\
esourceGroup"
"""

helps['datafactory linked-service google-cloud-storage update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service google-cloud-storage create --factory-name "exampleFactoryName" --type "Az\
ureStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service google-cloud-storage create --factory-name "exampleFactoryName" --type "Az\
ureStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleR\
esourceGroup"
"""

helps['datafactory linked-service greenplum'] = """
    type: group
    short-summary: datafactory linked-service sub group greenplum
"""

helps['datafactory linked-service greenplum create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service greenplum create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service greenplum create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service greenplum update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service greenplum create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service greenplum create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service h-base'] = """
    type: group
    short-summary: datafactory linked-service sub group h-base
"""

helps['datafactory linked-service h-base create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service h-base create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service h-base create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service h-base update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service h-base create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service h-base create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service h-d-insight'] = """
    type: group
    short-summary: datafactory linked-service sub group h-d-insight
"""

helps['datafactory linked-service h-d-insight create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service h-d-insight create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --type-properties-linked-service-name "\\"exampleLinkedService\\"" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service h-d-insight create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --description "Example description" --type-properties-linked-service-name "\\"exampleLinkedService\\"" --resource-gr\
oup "exampleResourceGroup"
"""

helps['datafactory linked-service h-d-insight update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service h-d-insight create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --type-properties-linked-service-name "\\"exampleLinkedService\\"" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service h-d-insight create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --description "Example description" --type-properties-linked-service-name "\\"exampleLinkedService\\"" --resource-gr\
oup "exampleResourceGroup"
"""

helps['datafactory linked-service h-d-insight-on-demand'] = """
    type: group
    short-summary: datafactory linked-service sub group h-d-insight-on-demand
"""

helps['datafactory linked-service h-d-insight-on-demand create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service h-d-insight-on-demand create --factory-name "exampleFactoryName" --type "A\
zureStorage" --type-properties-linked-service-name "\\"exampleLinkedService\\"" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service h-d-insight-on-demand create --factory-name "exampleFactoryName" --type "A\
zureStorage" --description "Example description" --type-properties-linked-service-name "\\"exampleLinkedService\\"" --r\
esource-group "exampleResourceGroup"
"""

helps['datafactory linked-service h-d-insight-on-demand update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service h-d-insight-on-demand create --factory-name "exampleFactoryName" --type "A\
zureStorage" --type-properties-linked-service-name "\\"exampleLinkedService\\"" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service h-d-insight-on-demand create --factory-name "exampleFactoryName" --type "A\
zureStorage" --description "Example description" --type-properties-linked-service-name "\\"exampleLinkedService\\"" --r\
esource-group "exampleResourceGroup"
"""

helps['datafactory linked-service hdfs'] = """
    type: group
    short-summary: datafactory linked-service sub group hdfs
"""

helps['datafactory linked-service hdfs create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service hdfs create --factory-name "exampleFactoryName" --type "AzureStorage" --li\
nked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service hdfs create --factory-name "exampleFactoryName" --type "AzureStorage" --de\
scription "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service hdfs update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service hdfs create --factory-name "exampleFactoryName" --type "AzureStorage" --li\
nked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service hdfs create --factory-name "exampleFactoryName" --type "AzureStorage" --de\
scription "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service hive'] = """
    type: group
    short-summary: datafactory linked-service sub group hive
"""

helps['datafactory linked-service hive create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service hive create --factory-name "exampleFactoryName" --type "AzureStorage" --li\
nked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service hive create --factory-name "exampleFactoryName" --type "AzureStorage" --de\
scription "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service hive update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service hive create --factory-name "exampleFactoryName" --type "AzureStorage" --li\
nked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service hive create --factory-name "exampleFactoryName" --type "AzureStorage" --de\
scription "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service http-server'] = """
    type: group
    short-summary: datafactory linked-service sub group http-server
"""

helps['datafactory linked-service http-server create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service http-server create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service http-server create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGr\
oup"
"""

helps['datafactory linked-service http-server update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service http-server create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service http-server create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGr\
oup"
"""

helps['datafactory linked-service hubspot'] = """
    type: group
    short-summary: datafactory linked-service sub group hubspot
"""

helps['datafactory linked-service hubspot create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service hubspot create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service hubspot create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service hubspot update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service hubspot create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service hubspot create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service impala'] = """
    type: group
    short-summary: datafactory linked-service sub group impala
"""

helps['datafactory linked-service impala create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service impala create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service impala create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service impala update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service impala create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service impala create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service informix'] = """
    type: group
    short-summary: datafactory linked-service sub group informix
"""

helps['datafactory linked-service informix create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service informix create --factory-name "exampleFactoryName" --type "AzureStorage" \
--linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service informix create --factory-name "exampleFactoryName" --type "AzureStorage" \
--description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup\
"
"""

helps['datafactory linked-service informix update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service informix create --factory-name "exampleFactoryName" --type "AzureStorage" \
--linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service informix create --factory-name "exampleFactoryName" --type "AzureStorage" \
--description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup\
"
"""

helps['datafactory linked-service jira'] = """
    type: group
    short-summary: datafactory linked-service sub group jira
"""

helps['datafactory linked-service jira create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service jira create --factory-name "exampleFactoryName" --type "AzureStorage" --li\
nked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service jira create --factory-name "exampleFactoryName" --type "AzureStorage" --de\
scription "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service jira update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service jira create --factory-name "exampleFactoryName" --type "AzureStorage" --li\
nked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service jira create --factory-name "exampleFactoryName" --type "AzureStorage" --de\
scription "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service magento'] = """
    type: group
    short-summary: datafactory linked-service sub group magento
"""

helps['datafactory linked-service magento create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service magento create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service magento create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service magento update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service magento create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service magento create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service maria-d-b'] = """
    type: group
    short-summary: datafactory linked-service sub group maria-d-b
"""

helps['datafactory linked-service maria-d-b create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service maria-d-b create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service maria-d-b create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service maria-d-b update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service maria-d-b create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service maria-d-b create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service marketo'] = """
    type: group
    short-summary: datafactory linked-service sub group marketo
"""

helps['datafactory linked-service marketo create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service marketo create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service marketo create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service marketo update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service marketo create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service marketo create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service microsoft-access'] = """
    type: group
    short-summary: datafactory linked-service sub group microsoft-access
"""

helps['datafactory linked-service microsoft-access create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service microsoft-access create --factory-name "exampleFactoryName" --type "AzureS\
torage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service microsoft-access create --factory-name "exampleFactoryName" --type "AzureS\
torage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResou\
rceGroup"
"""

helps['datafactory linked-service microsoft-access update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service microsoft-access create --factory-name "exampleFactoryName" --type "AzureS\
torage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service microsoft-access create --factory-name "exampleFactoryName" --type "AzureS\
torage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResou\
rceGroup"
"""

helps['datafactory linked-service mongo-db'] = """
    type: group
    short-summary: datafactory linked-service sub group mongo-db
"""

helps['datafactory linked-service mongo-db create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service mongo-db create --factory-name "exampleFactoryName" --type "AzureStorage" \
--linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service mongo-db create --factory-name "exampleFactoryName" --type "AzureStorage" \
--description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup\
"
"""

helps['datafactory linked-service mongo-db update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service mongo-db create --factory-name "exampleFactoryName" --type "AzureStorage" \
--linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service mongo-db create --factory-name "exampleFactoryName" --type "AzureStorage" \
--description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup\
"
"""

helps['datafactory linked-service mongo-db-v2'] = """
    type: group
    short-summary: datafactory linked-service sub group mongo-db-v2
"""

helps['datafactory linked-service mongo-db-v2 create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service mongo-db-v2 create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service mongo-db-v2 create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGr\
oup"
"""

helps['datafactory linked-service mongo-db-v2 update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service mongo-db-v2 create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service mongo-db-v2 create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGr\
oup"
"""

helps['datafactory linked-service my-sql'] = """
    type: group
    short-summary: datafactory linked-service sub group my-sql
"""

helps['datafactory linked-service my-sql create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service my-sql create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service my-sql create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service my-sql update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service my-sql create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service my-sql create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service netezza'] = """
    type: group
    short-summary: datafactory linked-service sub group netezza
"""

helps['datafactory linked-service netezza create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service netezza create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service netezza create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service netezza update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service netezza create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service netezza create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service o-data'] = """
    type: group
    short-summary: datafactory linked-service sub group o-data
"""

helps['datafactory linked-service o-data create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service o-data create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service o-data create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service o-data update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service o-data create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service o-data create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service odbc'] = """
    type: group
    short-summary: datafactory linked-service sub group odbc
"""

helps['datafactory linked-service odbc create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service odbc create --factory-name "exampleFactoryName" --type "AzureStorage" --li\
nked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service odbc create --factory-name "exampleFactoryName" --type "AzureStorage" --de\
scription "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service odbc update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service odbc create --factory-name "exampleFactoryName" --type "AzureStorage" --li\
nked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service odbc create --factory-name "exampleFactoryName" --type "AzureStorage" --de\
scription "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service office365'] = """
    type: group
    short-summary: datafactory linked-service sub group office365
"""

helps['datafactory linked-service office365 create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service office365 create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service office365 create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service office365 update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service office365 create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service office365 create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service oracle'] = """
    type: group
    short-summary: datafactory linked-service sub group oracle
"""

helps['datafactory linked-service oracle create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service oracle create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service oracle create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service oracle update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service oracle create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service oracle create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service oracle-service-cloud'] = """
    type: group
    short-summary: datafactory linked-service sub group oracle-service-cloud
"""

helps['datafactory linked-service oracle-service-cloud create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service oracle-service-cloud create --factory-name "exampleFactoryName" --type "Az\
ureStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service oracle-service-cloud create --factory-name "exampleFactoryName" --type "Az\
ureStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleR\
esourceGroup"
"""

helps['datafactory linked-service oracle-service-cloud update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service oracle-service-cloud create --factory-name "exampleFactoryName" --type "Az\
ureStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service oracle-service-cloud create --factory-name "exampleFactoryName" --type "Az\
ureStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleR\
esourceGroup"
"""

helps['datafactory linked-service paypal'] = """
    type: group
    short-summary: datafactory linked-service sub group paypal
"""

helps['datafactory linked-service paypal create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service paypal create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service paypal create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service paypal update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service paypal create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service paypal create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service phoenix'] = """
    type: group
    short-summary: datafactory linked-service sub group phoenix
"""

helps['datafactory linked-service phoenix create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service phoenix create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service phoenix create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service phoenix update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service phoenix create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service phoenix create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service postgre-sql'] = """
    type: group
    short-summary: datafactory linked-service sub group postgre-sql
"""

helps['datafactory linked-service postgre-sql create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service postgre-sql create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service postgre-sql create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGr\
oup"
"""

helps['datafactory linked-service postgre-sql update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service postgre-sql create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service postgre-sql create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGr\
oup"
"""

helps['datafactory linked-service presto'] = """
    type: group
    short-summary: datafactory linked-service sub group presto
"""

helps['datafactory linked-service presto create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service presto create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service presto create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service presto update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service presto create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service presto create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service quick-books'] = """
    type: group
    short-summary: datafactory linked-service sub group quick-books
"""

helps['datafactory linked-service quick-books create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service quick-books create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service quick-books create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGr\
oup"
"""

helps['datafactory linked-service quick-books update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service quick-books create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service quick-books create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGr\
oup"
"""

helps['datafactory linked-service responsys'] = """
    type: group
    short-summary: datafactory linked-service sub group responsys
"""

helps['datafactory linked-service responsys create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service responsys create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service responsys create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service responsys update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service responsys create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service responsys create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service rest-service'] = """
    type: group
    short-summary: datafactory linked-service sub group rest-service
"""

helps['datafactory linked-service rest-service create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service rest-service create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service rest-service create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceG\
roup"
"""

helps['datafactory linked-service rest-service update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service rest-service create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service rest-service create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceG\
roup"
"""

helps['datafactory linked-service salesforce'] = """
    type: group
    short-summary: datafactory linked-service sub group salesforce
"""

helps['datafactory linked-service salesforce create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service salesforce create --factory-name "exampleFactoryName" --type "AzureStorage\
" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service salesforce create --factory-name "exampleFactoryName" --type "AzureStorage\
" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGro\
up"
"""

helps['datafactory linked-service salesforce update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service salesforce create --factory-name "exampleFactoryName" --type "AzureStorage\
" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service salesforce create --factory-name "exampleFactoryName" --type "AzureStorage\
" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGro\
up"
"""

helps['datafactory linked-service salesforce-marketing-cloud'] = """
    type: group
    short-summary: datafactory linked-service sub group salesforce-marketing-cloud
"""

helps['datafactory linked-service salesforce-marketing-cloud create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service salesforce-marketing-cloud create --factory-name "exampleFactoryName" --ty\
pe "AzureStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service salesforce-marketing-cloud create --factory-name "exampleFactoryName" --ty\
pe "AzureStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "ex\
ampleResourceGroup"
"""

helps['datafactory linked-service salesforce-marketing-cloud update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service salesforce-marketing-cloud create --factory-name "exampleFactoryName" --ty\
pe "AzureStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service salesforce-marketing-cloud create --factory-name "exampleFactoryName" --ty\
pe "AzureStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "ex\
ampleResourceGroup"
"""

helps['datafactory linked-service salesforce-service-cloud'] = """
    type: group
    short-summary: datafactory linked-service sub group salesforce-service-cloud
"""

helps['datafactory linked-service salesforce-service-cloud create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service salesforce-service-cloud create --factory-name "exampleFactoryName" --type\
 "AzureStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service salesforce-service-cloud create --factory-name "exampleFactoryName" --type\
 "AzureStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exam\
pleResourceGroup"
"""

helps['datafactory linked-service salesforce-service-cloud update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service salesforce-service-cloud create --factory-name "exampleFactoryName" --type\
 "AzureStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service salesforce-service-cloud create --factory-name "exampleFactoryName" --type\
 "AzureStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exam\
pleResourceGroup"
"""

helps['datafactory linked-service sap-b-w'] = """
    type: group
    short-summary: datafactory linked-service sub group sap-b-w
"""

helps['datafactory linked-service sap-b-w create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service sap-b-w create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service sap-b-w create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service sap-b-w update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service sap-b-w create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service sap-b-w create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service sap-cloud-for-customer'] = """
    type: group
    short-summary: datafactory linked-service sub group sap-cloud-for-customer
"""

helps['datafactory linked-service sap-cloud-for-customer create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service sap-cloud-for-customer create --factory-name "exampleFactoryName" --type "\
AzureStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service sap-cloud-for-customer create --factory-name "exampleFactoryName" --type "\
AzureStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampl\
eResourceGroup"
"""

helps['datafactory linked-service sap-cloud-for-customer update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service sap-cloud-for-customer create --factory-name "exampleFactoryName" --type "\
AzureStorage" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service sap-cloud-for-customer create --factory-name "exampleFactoryName" --type "\
AzureStorage" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampl\
eResourceGroup"
"""

helps['datafactory linked-service sap-ecc'] = """
    type: group
    short-summary: datafactory linked-service sub group sap-ecc
"""

helps['datafactory linked-service sap-ecc create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service sap-ecc create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service sap-ecc create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service sap-ecc update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service sap-ecc create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service sap-ecc create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service sap-hana'] = """
    type: group
    short-summary: datafactory linked-service sub group sap-hana
"""

helps['datafactory linked-service sap-hana create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service sap-hana create --factory-name "exampleFactoryName" --type "AzureStorage" \
--linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service sap-hana create --factory-name "exampleFactoryName" --type "AzureStorage" \
--description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup\
"
"""

helps['datafactory linked-service sap-hana update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service sap-hana create --factory-name "exampleFactoryName" --type "AzureStorage" \
--linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service sap-hana create --factory-name "exampleFactoryName" --type "AzureStorage" \
--description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup\
"
"""

helps['datafactory linked-service sap-open-hub'] = """
    type: group
    short-summary: datafactory linked-service sub group sap-open-hub
"""

helps['datafactory linked-service sap-open-hub create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service sap-open-hub create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service sap-open-hub create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceG\
roup"
"""

helps['datafactory linked-service sap-open-hub update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service sap-open-hub create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service sap-open-hub create --factory-name "exampleFactoryName" --type "AzureStora\
ge" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceG\
roup"
"""

helps['datafactory linked-service sap-table'] = """
    type: group
    short-summary: datafactory linked-service sub group sap-table
"""

helps['datafactory linked-service sap-table create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service sap-table create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service sap-table create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service sap-table update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service sap-table create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service sap-table create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service service-now'] = """
    type: group
    short-summary: datafactory linked-service sub group service-now
"""

helps['datafactory linked-service service-now create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service service-now create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service service-now create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGr\
oup"
"""

helps['datafactory linked-service service-now update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service service-now create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service service-now create --factory-name "exampleFactoryName" --type "AzureStorag\
e" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGr\
oup"
"""

helps['datafactory linked-service sftp'] = """
    type: group
    short-summary: datafactory linked-service sub group sftp
"""

helps['datafactory linked-service sftp create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service sftp create --factory-name "exampleFactoryName" --type "AzureStorage" --li\
nked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service sftp create --factory-name "exampleFactoryName" --type "AzureStorage" --de\
scription "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service sftp update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service sftp create --factory-name "exampleFactoryName" --type "AzureStorage" --li\
nked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service sftp create --factory-name "exampleFactoryName" --type "AzureStorage" --de\
scription "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service shopify'] = """
    type: group
    short-summary: datafactory linked-service sub group shopify
"""

helps['datafactory linked-service shopify create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service shopify create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service shopify create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service shopify update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service shopify create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service shopify create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service snowflake'] = """
    type: group
    short-summary: datafactory linked-service sub group snowflake
"""

helps['datafactory linked-service snowflake create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service snowflake create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service snowflake create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service snowflake update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service snowflake create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service snowflake create --factory-name "exampleFactoryName" --type "AzureStorage"\
 --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGrou\
p"
"""

helps['datafactory linked-service spark'] = """
    type: group
    short-summary: datafactory linked-service sub group spark
"""

helps['datafactory linked-service spark create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service spark create --factory-name "exampleFactoryName" --type "AzureStorage" --l\
inked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service spark create --factory-name "exampleFactoryName" --type "AzureStorage" --d\
escription "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service spark update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service spark create --factory-name "exampleFactoryName" --type "AzureStorage" --l\
inked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service spark create --factory-name "exampleFactoryName" --type "AzureStorage" --d\
escription "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service sql-server'] = """
    type: group
    short-summary: datafactory linked-service sub group sql-server
"""

helps['datafactory linked-service sql-server create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service sql-server create --factory-name "exampleFactoryName" --type "AzureStorage\
" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service sql-server create --factory-name "exampleFactoryName" --type "AzureStorage\
" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGro\
up"
"""

helps['datafactory linked-service sql-server update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service sql-server create --factory-name "exampleFactoryName" --type "AzureStorage\
" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service sql-server create --factory-name "exampleFactoryName" --type "AzureStorage\
" --description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGro\
up"
"""

helps['datafactory linked-service square'] = """
    type: group
    short-summary: datafactory linked-service sub group square
"""

helps['datafactory linked-service square create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service square create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service square create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service square update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service square create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service square create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service sybase'] = """
    type: group
    short-summary: datafactory linked-service sub group sybase
"""

helps['datafactory linked-service sybase create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service sybase create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service sybase create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service sybase update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service sybase create --factory-name "exampleFactoryName" --type "AzureStorage" --\
linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service sybase create --factory-name "exampleFactoryName" --type "AzureStorage" --\
description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service teradata'] = """
    type: group
    short-summary: datafactory linked-service sub group teradata
"""

helps['datafactory linked-service teradata create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service teradata create --factory-name "exampleFactoryName" --type "AzureStorage" \
--linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service teradata create --factory-name "exampleFactoryName" --type "AzureStorage" \
--description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup\
"
"""

helps['datafactory linked-service teradata update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service teradata create --factory-name "exampleFactoryName" --type "AzureStorage" \
--linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service teradata create --factory-name "exampleFactoryName" --type "AzureStorage" \
--description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup\
"
"""

helps['datafactory linked-service vertica'] = """
    type: group
    short-summary: datafactory linked-service sub group vertica
"""

helps['datafactory linked-service vertica create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service vertica create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service vertica create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service vertica update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service vertica create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service vertica create --factory-name "exampleFactoryName" --type "AzureStorage" -\
-description "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service web'] = """
    type: group
    short-summary: datafactory linked-service sub group web
"""

helps['datafactory linked-service web create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service web create --factory-name "exampleFactoryName" --type "AzureStorage" --typ\
e-properties "{\\"connectionString\\":{\\"type\\":\\"SecureString\\",\\"value\\":\\"DefaultEndpointsProtocol=https;Acco\
untName=examplestorageaccount;AccountKey=<storage key>\\"}}" --linked-service-name "exampleLinkedService" --resource-gr\
oup "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service web create --factory-name "exampleFactoryName" --type "AzureStorage" --des\
cription "Example description" --type-properties "{\\"connectionString\\":{\\"type\\":\\"SecureString\\",\\"value\\":\\\
"DefaultEndpointsProtocol=https;AccountName=examplestorageaccount;AccountKey=<storage key>\\"}}" --linked-service-name \
"exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service web update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service web create --factory-name "exampleFactoryName" --type "AzureStorage" --typ\
e-properties "{\\"connectionString\\":{\\"type\\":\\"SecureString\\",\\"value\\":\\"DefaultEndpointsProtocol=https;Acco\
untName=examplestorageaccount;AccountKey=<storage key>\\"}}" --linked-service-name "exampleLinkedService" --resource-gr\
oup "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service web create --factory-name "exampleFactoryName" --type "AzureStorage" --des\
cription "Example description" --type-properties "{\\"connectionString\\":{\\"type\\":\\"SecureString\\",\\"value\\":\\\
"DefaultEndpointsProtocol=https;AccountName=examplestorageaccount;AccountKey=<storage key>\\"}}" --linked-service-name \
"exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service xero'] = """
    type: group
    short-summary: datafactory linked-service sub group xero
"""

helps['datafactory linked-service xero create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service xero create --factory-name "exampleFactoryName" --type "AzureStorage" --li\
nked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service xero create --factory-name "exampleFactoryName" --type "AzureStorage" --de\
scription "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service xero update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service xero create --factory-name "exampleFactoryName" --type "AzureStorage" --li\
nked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service xero create --factory-name "exampleFactoryName" --type "AzureStorage" --de\
scription "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service zoho'] = """
    type: group
    short-summary: datafactory linked-service sub group zoho
"""

helps['datafactory linked-service zoho create'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service zoho create --factory-name "exampleFactoryName" --type "AzureStorage" --li\
nked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service zoho create --factory-name "exampleFactoryName" --type "AzureStorage" --de\
scription "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service zoho update'] = """
    type: command
    short-summary: Creates or updates a linked service.
    examples:
      - name: LinkedServices_Create
        text: |-
               az datafactory linked-service zoho create --factory-name "exampleFactoryName" --type "AzureStorage" --li\
nked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
      - name: LinkedServices_Update
        text: |-
               az datafactory linked-service zoho create --factory-name "exampleFactoryName" --type "AzureStorage" --de\
scription "Example description" --linked-service-name "exampleLinkedService" --resource-group "exampleResourceGroup"
"""

helps['datafactory linked-service delete'] = """
    type: command
    short-summary: Deletes a linked service.
    examples:
      - name: LinkedServices_Delete
        text: |-
               az datafactory linked-service delete --factory-name "exampleFactoryName" --linked-service-name "exampleL\
inkedService" --resource-group "exampleResourceGroup"
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
               az datafactory dataset list --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset show'] = """
    type: command
    short-summary: Gets a dataset.
    examples:
      - name: Datasets_Get
        text: |-
               az datafactory dataset show --dataset-name "exampleDataset" --factory-name "exampleFactoryName" --resour\
ce-group "exampleResourceGroup"
"""

helps['datafactory dataset amazon-m-w-s-object'] = """
    type: group
    short-summary: datafactory dataset sub group amazon-m-w-s-object
"""

helps['datafactory dataset amazon-m-w-s-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset amazon-m-w-s-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset amazon-m-w-s-object create --type "AzureBlob" --description "Example description"\
 --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --par\
ameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exa\
mpleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset amazon-m-w-s-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset amazon-m-w-s-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset amazon-m-w-s-object create --type "AzureBlob" --description "Example description"\
 --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --par\
ameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exa\
mpleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset amazon-redshift-table'] = """
    type: group
    short-summary: datafactory dataset sub group amazon-redshift-table
"""

helps['datafactory dataset amazon-redshift-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset amazon-redshift-table create --type "AzureBlob" --linked-service-name "{\\"type\\\
":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"typ\
e\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "examp\
leFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset amazon-redshift-table create --type "AzureBlob" --description "Example descriptio\
n" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --p\
arameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "e\
xampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset amazon-redshift-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset amazon-redshift-table create --type "AzureBlob" --linked-service-name "{\\"type\\\
":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"typ\
e\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "examp\
leFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset amazon-redshift-table create --type "AzureBlob" --description "Example descriptio\
n" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --p\
arameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "e\
xampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset amazon-s3-object'] = """
    type: group
    short-summary: datafactory dataset sub group amazon-s3-object
"""

helps['datafactory dataset amazon-s3-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset amazon-s3-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"\
LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset amazon-s3-object create --type "AzureBlob" --description "Example description" --\
linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parame\
ters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampl\
eDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset amazon-s3-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset amazon-s3-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"\
LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset amazon-s3-object create --type "AzureBlob" --description "Example description" --\
linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parame\
ters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampl\
eDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset avro'] = """
    type: group
    short-summary: datafactory dataset sub group avro
"""

helps['datafactory dataset avro create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset avro create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"LinkedServic\
eReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"\
},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryName" --\
resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset avro create --type "AzureBlob" --description "Example description" --linked-servi\
ce-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"My\
FileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --\
factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset avro update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset avro create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"LinkedServic\
eReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"\
},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryName" --\
resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset avro create --type "AzureBlob" --description "Example description" --linked-servi\
ce-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"My\
FileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --\
factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-blob'] = """
    type: group
    short-summary: datafactory dataset sub group azure-blob
"""

helps['datafactory dataset azure-blob create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-blob create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Linked\
ServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"Str\
ing\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryNa\
me" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-blob create --type "AzureBlob" --description "Example description" --linked\
-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "\
{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDatas\
et" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-blob update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-blob create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Linked\
ServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"Str\
ing\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryNa\
me" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-blob create --type "AzureBlob" --description "Example description" --linked\
-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "\
{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDatas\
et" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-blob-f-s-file'] = """
    type: group
    short-summary: datafactory dataset sub group azure-blob-f-s-file
"""

helps['datafactory dataset azure-blob-f-s-file create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-blob-f-s-file create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-blob-f-s-file create --type "AzureBlob" --description "Example description"\
 --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --par\
ameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exa\
mpleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-blob-f-s-file update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-blob-f-s-file create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-blob-f-s-file create --type "AzureBlob" --description "Example description"\
 --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --par\
ameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exa\
mpleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-data-explorer-table'] = """
    type: group
    short-summary: datafactory dataset sub group azure-data-explorer-table
"""

helps['datafactory dataset azure-data-explorer-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-data-explorer-table create --type "AzureBlob" --linked-service-name "{\\"ty\
pe\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\\
"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "e\
xampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-data-explorer-table create --type "AzureBlob" --description "Example descri\
ption" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}"\
 --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-nam\
e "exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-data-explorer-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-data-explorer-table create --type "AzureBlob" --linked-service-name "{\\"ty\
pe\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\\
"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "e\
xampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-data-explorer-table create --type "AzureBlob" --description "Example descri\
ption" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}"\
 --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-nam\
e "exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-data-lake-store-file'] = """
    type: group
    short-summary: datafactory dataset sub group azure-data-lake-store-file
"""

helps['datafactory dataset azure-data-lake-store-file create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-data-lake-store-file create --type "AzureBlob" --linked-service-name "{\\"t\
ype\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\
\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name \
"exampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-data-lake-store-file create --type "AzureBlob" --description "Example descr\
iption" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}\
" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-na\
me "exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-data-lake-store-file update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-data-lake-store-file create --type "AzureBlob" --linked-service-name "{\\"t\
ype\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\
\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name \
"exampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-data-lake-store-file create --type "AzureBlob" --description "Example descr\
iption" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}\
" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-na\
me "exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-maria-d-b-table'] = """
    type: group
    short-summary: datafactory dataset sub group azure-maria-d-b-table
"""

helps['datafactory dataset azure-maria-d-b-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-maria-d-b-table create --type "AzureBlob" --linked-service-name "{\\"type\\\
":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"typ\
e\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "examp\
leFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-maria-d-b-table create --type "AzureBlob" --description "Example descriptio\
n" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --p\
arameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "e\
xampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-maria-d-b-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-maria-d-b-table create --type "AzureBlob" --linked-service-name "{\\"type\\\
":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"typ\
e\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "examp\
leFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-maria-d-b-table create --type "AzureBlob" --description "Example descriptio\
n" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --p\
arameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "e\
xampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-my-sql-table'] = """
    type: group
    short-summary: datafactory dataset sub group azure-my-sql-table
"""

helps['datafactory dataset azure-my-sql-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-my-sql-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-my-sql-table create --type "AzureBlob" --description "Example description" \
--linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --para\
meters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exam\
pleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-my-sql-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-my-sql-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-my-sql-table create --type "AzureBlob" --description "Example description" \
--linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --para\
meters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exam\
pleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-postgre-sql-table'] = """
    type: group
    short-summary: datafactory dataset sub group azure-postgre-sql-table
"""

helps['datafactory dataset azure-postgre-sql-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-postgre-sql-table create --type "AzureBlob" --linked-service-name "{\\"type\
\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"t\
ype\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exa\
mpleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-postgre-sql-table create --type "AzureBlob" --description "Example descript\
ion" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" -\
-parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name \
"exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-postgre-sql-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-postgre-sql-table create --type "AzureBlob" --linked-service-name "{\\"type\
\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"t\
ype\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exa\
mpleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-postgre-sql-table create --type "AzureBlob" --description "Example descript\
ion" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" -\
-parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name \
"exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-search-index'] = """
    type: group
    short-summary: datafactory dataset sub group azure-search-index
"""

helps['datafactory dataset azure-search-index create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-search-index create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-search-index create --type "AzureBlob" --description "Example description" \
--linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --para\
meters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exam\
pleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-search-index update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-search-index create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-search-index create --type "AzureBlob" --description "Example description" \
--linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --para\
meters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exam\
pleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-sql-d-w-table'] = """
    type: group
    short-summary: datafactory dataset sub group azure-sql-d-w-table
"""

helps['datafactory dataset azure-sql-d-w-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-sql-d-w-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-sql-d-w-table create --type "AzureBlob" --description "Example description"\
 --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --par\
ameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exa\
mpleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-sql-d-w-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-sql-d-w-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-sql-d-w-table create --type "AzureBlob" --description "Example description"\
 --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --par\
ameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exa\
mpleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-sql-m-i-table'] = """
    type: group
    short-summary: datafactory dataset sub group azure-sql-m-i-table
"""

helps['datafactory dataset azure-sql-m-i-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-sql-m-i-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-sql-m-i-table create --type "AzureBlob" --description "Example description"\
 --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --par\
ameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exa\
mpleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-sql-m-i-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-sql-m-i-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-sql-m-i-table create --type "AzureBlob" --description "Example description"\
 --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --par\
ameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exa\
mpleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-sql-table'] = """
    type: group
    short-summary: datafactory dataset sub group azure-sql-table
"""

helps['datafactory dataset azure-sql-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-sql-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"L\
inkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-sql-table create --type "AzureBlob" --description "Example description" --l\
inked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramet\
ers "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "example\
Dataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-sql-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-sql-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"L\
inkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-sql-table create --type "AzureBlob" --description "Example description" --l\
inked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramet\
ers "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "example\
Dataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-table'] = """
    type: group
    short-summary: datafactory dataset sub group azure-table
"""

helps['datafactory dataset azure-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Linke\
dServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"St\
ring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryN\
ame" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-table create --type "AzureBlob" --description "Example description" --linke\
d-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters \
"{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleData\
set" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset azure-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset azure-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Linke\
dServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"St\
ring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryN\
ame" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset azure-table create --type "AzureBlob" --description "Example description" --linke\
d-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters \
"{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleData\
set" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset binary'] = """
    type: group
    short-summary: datafactory dataset sub group binary
"""

helps['datafactory dataset binary create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset binary create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"LinkedServ\
iceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\
\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryName"\
 --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset binary create --type "AzureBlob" --description "Example description" --linked-ser\
vice-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"\
MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" \
--factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset binary update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset binary create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"LinkedServ\
iceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\
\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryName"\
 --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset binary create --type "AzureBlob" --description "Example description" --linked-ser\
vice-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"\
MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" \
--factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset cassandra-table'] = """
    type: group
    short-summary: datafactory dataset sub group cassandra-table
"""

helps['datafactory dataset cassandra-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset cassandra-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"L\
inkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset cassandra-table create --type "AzureBlob" --description "Example description" --l\
inked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramet\
ers "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "example\
Dataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset cassandra-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset cassandra-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"L\
inkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset cassandra-table create --type "AzureBlob" --description "Example description" --l\
inked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramet\
ers "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "example\
Dataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset common-data-service-for-apps-entity'] = """
    type: group
    short-summary: datafactory dataset sub group common-data-service-for-apps-entity
"""

helps['datafactory dataset common-data-service-for-apps-entity create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset common-data-service-for-apps-entity create --type "AzureBlob" --linked-service-na\
me "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileN\
ame\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --facto\
ry-name "exampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset common-data-service-for-apps-entity create --type "AzureBlob" --description "Exam\
ple description" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedSe\
rvice\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --d\
ataset-name "exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset common-data-service-for-apps-entity update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset common-data-service-for-apps-entity create --type "AzureBlob" --linked-service-na\
me "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileN\
ame\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --facto\
ry-name "exampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset common-data-service-for-apps-entity create --type "AzureBlob" --description "Exam\
ple description" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedSe\
rvice\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --d\
ataset-name "exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset concur-object'] = """
    type: group
    short-summary: datafactory dataset sub group concur-object
"""

helps['datafactory dataset concur-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset concur-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Lin\
kedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"\
String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactor\
yName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset concur-object create --type "AzureBlob" --description "Example description" --lin\
ked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameter\
s "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDa\
taset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset concur-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset concur-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Lin\
kedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"\
String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactor\
yName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset concur-object create --type "AzureBlob" --description "Example description" --lin\
ked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameter\
s "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDa\
taset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset cosmos-db-mongo-db-api-collection'] = """
    type: group
    short-summary: datafactory dataset sub group cosmos-db-mongo-db-api-collection
"""

helps['datafactory dataset cosmos-db-mongo-db-api-collection create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset cosmos-db-mongo-db-api-collection create --type "AzureBlob" --linked-service-name\
 "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileNam\
e\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory\
-name "exampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset cosmos-db-mongo-db-api-collection create --type "AzureBlob" --description "Exampl\
e description" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ\
ice\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dat\
aset-name "exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset cosmos-db-mongo-db-api-collection update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset cosmos-db-mongo-db-api-collection create --type "AzureBlob" --linked-service-name\
 "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileNam\
e\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory\
-name "exampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset cosmos-db-mongo-db-api-collection create --type "AzureBlob" --description "Exampl\
e description" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ\
ice\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dat\
aset-name "exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset cosmos-db-sql-api-collection'] = """
    type: group
    short-summary: datafactory dataset sub group cosmos-db-sql-api-collection
"""

helps['datafactory dataset cosmos-db-sql-api-collection create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset cosmos-db-sql-api-collection create --properties type=AzureBlob linked-service-na\
me={\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"} parameters={\\"MyFileName\\\
":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}} typeProperties={\\"format\\":{\\"type\\":\\"T\
extFormat\\"},\\"fileName\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFileName\\"},\\"folderPath\\":{\\\
"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFolderPath\\"}} --dataset-name "exampleDataset" --factory-name "e\
xampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset cosmos-db-sql-api-collection create --properties type=AzureBlob description=Examp\
le description linked-service-name={\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\
\\"} parameters={\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}} typePropertie\
s={\\"format\\":{\\"type\\":\\"TextFormat\\"},\\"fileName\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyF\
ileName\\"},\\"folderPath\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFolderPath\\"}} --dataset-name "e\
xampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset cosmos-db-sql-api-collection update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset cosmos-db-sql-api-collection create --properties type=AzureBlob linked-service-na\
me={\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"} parameters={\\"MyFileName\\\
":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}} typeProperties={\\"format\\":{\\"type\\":\\"T\
extFormat\\"},\\"fileName\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFileName\\"},\\"folderPath\\":{\\\
"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFolderPath\\"}} --dataset-name "exampleDataset" --factory-name "e\
xampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset cosmos-db-sql-api-collection create --properties type=AzureBlob description=Examp\
le description linked-service-name={\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\
\\"} parameters={\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}} typePropertie\
s={\\"format\\":{\\"type\\":\\"TextFormat\\"},\\"fileName\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyF\
ileName\\"},\\"folderPath\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFolderPath\\"}} --dataset-name "e\
xampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset couchbase-table'] = """
    type: group
    short-summary: datafactory dataset sub group couchbase-table
"""

helps['datafactory dataset couchbase-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset couchbase-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"L\
inkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset couchbase-table create --type "AzureBlob" --description "Example description" --l\
inked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramet\
ers "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "example\
Dataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset couchbase-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset couchbase-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"L\
inkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset couchbase-table create --type "AzureBlob" --description "Example description" --l\
inked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramet\
ers "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "example\
Dataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset custom-dataset'] = """
    type: group
    short-summary: datafactory dataset sub group custom-dataset
"""

helps['datafactory dataset custom-dataset create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset custom-dataset create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Li\
nkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\\
"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --type-properties "{\\"format\\":{\\"type\\":\\"TextFormat\\\
"},\\"fileName\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFileName\\"},\\"folderPath\\":{\\"type\\":\\\
"Expression\\",\\"value\\":\\"@dataset().MyFolderPath\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFact\
oryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset custom-dataset create --type "AzureBlob" --description "Example description" --li\
nked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramete\
rs "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --type-properties "{\\"f\
ormat\\":{\\"type\\":\\"TextFormat\\"},\\"fileName\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFileName\
\\"},\\"folderPath\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFolderPath\\"}}" --dataset-name "example\
Dataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset custom-dataset update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset custom-dataset create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Li\
nkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\\
"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --type-properties "{\\"format\\":{\\"type\\":\\"TextFormat\\\
"},\\"fileName\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFileName\\"},\\"folderPath\\":{\\"type\\":\\\
"Expression\\",\\"value\\":\\"@dataset().MyFolderPath\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFact\
oryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset custom-dataset create --type "AzureBlob" --description "Example description" --li\
nked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramete\
rs "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --type-properties "{\\"f\
ormat\\":{\\"type\\":\\"TextFormat\\"},\\"fileName\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFileName\
\\"},\\"folderPath\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFolderPath\\"}}" --dataset-name "example\
Dataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset db2-table'] = """
    type: group
    short-summary: datafactory dataset sub group db2-table
"""

helps['datafactory dataset db2-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset db2-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"LinkedS\
erviceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"Stri\
ng\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryNam\
e" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset db2-table create --type "AzureBlob" --description "Example description" --linked-\
service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\
\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDatase\
t" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset db2-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset db2-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"LinkedS\
erviceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"Stri\
ng\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryNam\
e" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset db2-table create --type "AzureBlob" --description "Example description" --linked-\
service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\
\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDatase\
t" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset delimited-text'] = """
    type: group
    short-summary: datafactory dataset sub group delimited-text
"""

helps['datafactory dataset delimited-text create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset delimited-text create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Li\
nkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\\
"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFacto\
ryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset delimited-text create --type "AzureBlob" --description "Example description" --li\
nked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramete\
rs "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleD\
ataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset delimited-text update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset delimited-text create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Li\
nkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\\
"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFacto\
ryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset delimited-text create --type "AzureBlob" --description "Example description" --li\
nked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramete\
rs "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleD\
ataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset document-db-collection'] = """
    type: group
    short-summary: datafactory dataset sub group document-db-collection
"""

helps['datafactory dataset document-db-collection create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset document-db-collection create --type "AzureBlob" --linked-service-name "{\\"type\
\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"t\
ype\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exa\
mpleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset document-db-collection create --type "AzureBlob" --description "Example descripti\
on" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --\
parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "\
exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset document-db-collection update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset document-db-collection create --type "AzureBlob" --linked-service-name "{\\"type\
\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"t\
ype\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exa\
mpleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset document-db-collection create --type "AzureBlob" --description "Example descripti\
on" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --\
parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "\
exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset drill-table'] = """
    type: group
    short-summary: datafactory dataset sub group drill-table
"""

helps['datafactory dataset drill-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset drill-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Linke\
dServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"St\
ring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryN\
ame" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset drill-table create --type "AzureBlob" --description "Example description" --linke\
d-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters \
"{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleData\
set" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset drill-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset drill-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Linke\
dServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"St\
ring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryN\
ame" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset drill-table create --type "AzureBlob" --description "Example description" --linke\
d-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters \
"{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleData\
set" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset dynamics-a-x-resource'] = """
    type: group
    short-summary: datafactory dataset sub group dynamics-a-x-resource
"""

helps['datafactory dataset dynamics-a-x-resource create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset dynamics-a-x-resource create --type "AzureBlob" --linked-service-name "{\\"type\\\
":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"typ\
e\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "examp\
leFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset dynamics-a-x-resource create --type "AzureBlob" --description "Example descriptio\
n" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --p\
arameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "e\
xampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset dynamics-a-x-resource update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset dynamics-a-x-resource create --type "AzureBlob" --linked-service-name "{\\"type\\\
":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"typ\
e\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "examp\
leFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset dynamics-a-x-resource create --type "AzureBlob" --description "Example descriptio\
n" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --p\
arameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "e\
xampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset dynamics-crm-entity'] = """
    type: group
    short-summary: datafactory dataset sub group dynamics-crm-entity
"""

helps['datafactory dataset dynamics-crm-entity create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset dynamics-crm-entity create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset dynamics-crm-entity create --type "AzureBlob" --description "Example description"\
 --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --par\
ameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exa\
mpleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset dynamics-crm-entity update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset dynamics-crm-entity create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset dynamics-crm-entity create --type "AzureBlob" --description "Example description"\
 --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --par\
ameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exa\
mpleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset dynamics-entity'] = """
    type: group
    short-summary: datafactory dataset sub group dynamics-entity
"""

helps['datafactory dataset dynamics-entity create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset dynamics-entity create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"L\
inkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset dynamics-entity create --type "AzureBlob" --description "Example description" --l\
inked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramet\
ers "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "example\
Dataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset dynamics-entity update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset dynamics-entity create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"L\
inkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset dynamics-entity create --type "AzureBlob" --description "Example description" --l\
inked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramet\
ers "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "example\
Dataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset eloqua-object'] = """
    type: group
    short-summary: datafactory dataset sub group eloqua-object
"""

helps['datafactory dataset eloqua-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset eloqua-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Lin\
kedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"\
String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactor\
yName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset eloqua-object create --type "AzureBlob" --description "Example description" --lin\
ked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameter\
s "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDa\
taset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset eloqua-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset eloqua-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Lin\
kedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"\
String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactor\
yName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset eloqua-object create --type "AzureBlob" --description "Example description" --lin\
ked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameter\
s "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDa\
taset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset file-share'] = """
    type: group
    short-summary: datafactory dataset sub group file-share
"""

helps['datafactory dataset file-share create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset file-share create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Linked\
ServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"Str\
ing\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryNa\
me" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset file-share create --type "AzureBlob" --description "Example description" --linked\
-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "\
{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDatas\
et" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset file-share update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset file-share create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Linked\
ServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"Str\
ing\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryNa\
me" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset file-share create --type "AzureBlob" --description "Example description" --linked\
-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "\
{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDatas\
et" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset google-ad-words-object'] = """
    type: group
    short-summary: datafactory dataset sub group google-ad-words-object
"""

helps['datafactory dataset google-ad-words-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset google-ad-words-object create --type "AzureBlob" --linked-service-name "{\\"type\
\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"t\
ype\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exa\
mpleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset google-ad-words-object create --type "AzureBlob" --description "Example descripti\
on" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --\
parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "\
exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset google-ad-words-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset google-ad-words-object create --type "AzureBlob" --linked-service-name "{\\"type\
\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"t\
ype\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exa\
mpleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset google-ad-words-object create --type "AzureBlob" --description "Example descripti\
on" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --\
parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "\
exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset google-big-query-object'] = """
    type: group
    short-summary: datafactory dataset sub group google-big-query-object
"""

helps['datafactory dataset google-big-query-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset google-big-query-object create --type-properties-dataset "{\\"properties\\":{\\"t\
ype\\":\\"AzureBlob\\",\\"linkedServiceName\\":{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleL\
inkedService\\"},\\"parameters\\":{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\
\\"}},\\"typeProperties\\":{\\"format\\":{\\"type\\":\\"TextFormat\\"},\\"fileName\\":{\\"type\\":\\"Expression\\",\\"v\
alue\\":\\"@dataset().MyFileName\\"},\\"folderPath\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFolderPa\
th\\"}}}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset google-big-query-object create --type-properties-dataset "{\\"properties\\":{\\"t\
ype\\":\\"AzureBlob\\",\\"description\\":\\"Example description\\",\\"linkedServiceName\\":{\\"type\\":\\"LinkedService\
Reference\\",\\"referenceName\\":\\"exampleLinkedService\\"},\\"parameters\\":{\\"MyFileName\\":{\\"type\\":\\"String\\\
"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}},\\"typeProperties\\":{\\"format\\":{\\"type\\":\\"TextFormat\\"},\\"fi\
leName\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFileName\\"},\\"folderPath\\":{\\"type\\":\\"Express\
ion\\",\\"value\\":\\"@dataset().MyFolderPath\\"}}}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryNam\
e" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset google-big-query-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset google-big-query-object create --type-properties-dataset "{\\"properties\\":{\\"t\
ype\\":\\"AzureBlob\\",\\"linkedServiceName\\":{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleL\
inkedService\\"},\\"parameters\\":{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\
\\"}},\\"typeProperties\\":{\\"format\\":{\\"type\\":\\"TextFormat\\"},\\"fileName\\":{\\"type\\":\\"Expression\\",\\"v\
alue\\":\\"@dataset().MyFileName\\"},\\"folderPath\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFolderPa\
th\\"}}}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset google-big-query-object create --type-properties-dataset "{\\"properties\\":{\\"t\
ype\\":\\"AzureBlob\\",\\"description\\":\\"Example description\\",\\"linkedServiceName\\":{\\"type\\":\\"LinkedService\
Reference\\",\\"referenceName\\":\\"exampleLinkedService\\"},\\"parameters\\":{\\"MyFileName\\":{\\"type\\":\\"String\\\
"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}},\\"typeProperties\\":{\\"format\\":{\\"type\\":\\"TextFormat\\"},\\"fi\
leName\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFileName\\"},\\"folderPath\\":{\\"type\\":\\"Express\
ion\\",\\"value\\":\\"@dataset().MyFolderPath\\"}}}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryNam\
e" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset greenplum-table'] = """
    type: group
    short-summary: datafactory dataset sub group greenplum-table
"""

helps['datafactory dataset greenplum-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset greenplum-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"L\
inkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset greenplum-table create --type "AzureBlob" --description "Example description" --l\
inked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramet\
ers "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "example\
Dataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset greenplum-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset greenplum-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"L\
inkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset greenplum-table create --type "AzureBlob" --description "Example description" --l\
inked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramet\
ers "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "example\
Dataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset h-base-object'] = """
    type: group
    short-summary: datafactory dataset sub group h-base-object
"""

helps['datafactory dataset h-base-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset h-base-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Lin\
kedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"\
String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactor\
yName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset h-base-object create --type "AzureBlob" --description "Example description" --lin\
ked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameter\
s "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDa\
taset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset h-base-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset h-base-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Lin\
kedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"\
String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactor\
yName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset h-base-object create --type "AzureBlob" --description "Example description" --lin\
ked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameter\
s "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDa\
taset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset hive-object'] = """
    type: group
    short-summary: datafactory dataset sub group hive-object
"""

helps['datafactory dataset hive-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset hive-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Linke\
dServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"St\
ring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryN\
ame" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset hive-object create --type "AzureBlob" --description "Example description" --linke\
d-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters \
"{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleData\
set" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset hive-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset hive-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Linke\
dServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"St\
ring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryN\
ame" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset hive-object create --type "AzureBlob" --description "Example description" --linke\
d-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters \
"{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleData\
set" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset http-file'] = """
    type: group
    short-summary: datafactory dataset sub group http-file
"""

helps['datafactory dataset http-file create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset http-file create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"LinkedS\
erviceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"Stri\
ng\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryNam\
e" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset http-file create --type "AzureBlob" --description "Example description" --linked-\
service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\
\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDatase\
t" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset http-file update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset http-file create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"LinkedS\
erviceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"Stri\
ng\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryNam\
e" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset http-file create --type "AzureBlob" --description "Example description" --linked-\
service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\
\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDatase\
t" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset hubspot-object'] = """
    type: group
    short-summary: datafactory dataset sub group hubspot-object
"""

helps['datafactory dataset hubspot-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset hubspot-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Li\
nkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\\
"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFacto\
ryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset hubspot-object create --type "AzureBlob" --description "Example description" --li\
nked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramete\
rs "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleD\
ataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset hubspot-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset hubspot-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Li\
nkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\\
"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFacto\
ryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset hubspot-object create --type "AzureBlob" --description "Example description" --li\
nked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramete\
rs "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleD\
ataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset impala-object'] = """
    type: group
    short-summary: datafactory dataset sub group impala-object
"""

helps['datafactory dataset impala-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset impala-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Lin\
kedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"\
String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactor\
yName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset impala-object create --type "AzureBlob" --description "Example description" --lin\
ked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameter\
s "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDa\
taset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset impala-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset impala-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Lin\
kedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"\
String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactor\
yName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset impala-object create --type "AzureBlob" --description "Example description" --lin\
ked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameter\
s "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDa\
taset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset informix-table'] = """
    type: group
    short-summary: datafactory dataset sub group informix-table
"""

helps['datafactory dataset informix-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset informix-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Li\
nkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\\
"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFacto\
ryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset informix-table create --type "AzureBlob" --description "Example description" --li\
nked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramete\
rs "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleD\
ataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset informix-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset informix-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Li\
nkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\\
"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFacto\
ryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset informix-table create --type "AzureBlob" --description "Example description" --li\
nked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramete\
rs "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleD\
ataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset jira-object'] = """
    type: group
    short-summary: datafactory dataset sub group jira-object
"""

helps['datafactory dataset jira-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset jira-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Linke\
dServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"St\
ring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryN\
ame" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset jira-object create --type "AzureBlob" --description "Example description" --linke\
d-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters \
"{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleData\
set" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset jira-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset jira-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Linke\
dServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"St\
ring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryN\
ame" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset jira-object create --type "AzureBlob" --description "Example description" --linke\
d-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters \
"{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleData\
set" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset json'] = """
    type: group
    short-summary: datafactory dataset sub group json
"""

helps['datafactory dataset json create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset json create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"LinkedServic\
eReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"\
},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryName" --\
resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset json create --type "AzureBlob" --description "Example description" --linked-servi\
ce-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"My\
FileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --\
factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset json update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset json create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"LinkedServic\
eReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"\
},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryName" --\
resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset json create --type "AzureBlob" --description "Example description" --linked-servi\
ce-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"My\
FileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --\
factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset magento-object'] = """
    type: group
    short-summary: datafactory dataset sub group magento-object
"""

helps['datafactory dataset magento-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset magento-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Li\
nkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\\
"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFacto\
ryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset magento-object create --type "AzureBlob" --description "Example description" --li\
nked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramete\
rs "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleD\
ataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset magento-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset magento-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Li\
nkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\\
"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFacto\
ryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset magento-object create --type "AzureBlob" --description "Example description" --li\
nked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramete\
rs "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleD\
ataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset maria-d-b-table'] = """
    type: group
    short-summary: datafactory dataset sub group maria-d-b-table
"""

helps['datafactory dataset maria-d-b-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset maria-d-b-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"L\
inkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset maria-d-b-table create --type "AzureBlob" --description "Example description" --l\
inked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramet\
ers "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "example\
Dataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset maria-d-b-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset maria-d-b-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"L\
inkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset maria-d-b-table create --type "AzureBlob" --description "Example description" --l\
inked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramet\
ers "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "example\
Dataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset marketo-object'] = """
    type: group
    short-summary: datafactory dataset sub group marketo-object
"""

helps['datafactory dataset marketo-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset marketo-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Li\
nkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\\
"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFacto\
ryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset marketo-object create --type "AzureBlob" --description "Example description" --li\
nked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramete\
rs "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleD\
ataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset marketo-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset marketo-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Li\
nkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\\
"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFacto\
ryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset marketo-object create --type "AzureBlob" --description "Example description" --li\
nked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramete\
rs "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleD\
ataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset microsoft-access-table'] = """
    type: group
    short-summary: datafactory dataset sub group microsoft-access-table
"""

helps['datafactory dataset microsoft-access-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset microsoft-access-table create --type "AzureBlob" --linked-service-name "{\\"type\
\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"t\
ype\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exa\
mpleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset microsoft-access-table create --type "AzureBlob" --description "Example descripti\
on" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --\
parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "\
exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset microsoft-access-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset microsoft-access-table create --type "AzureBlob" --linked-service-name "{\\"type\
\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"t\
ype\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exa\
mpleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset microsoft-access-table create --type "AzureBlob" --description "Example descripti\
on" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --\
parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "\
exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset mongo-db-collection'] = """
    type: group
    short-summary: datafactory dataset sub group mongo-db-collection
"""

helps['datafactory dataset mongo-db-collection create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset mongo-db-collection create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset mongo-db-collection create --type "AzureBlob" --description "Example description"\
 --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --par\
ameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exa\
mpleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset mongo-db-collection update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset mongo-db-collection create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset mongo-db-collection create --type "AzureBlob" --description "Example description"\
 --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --par\
ameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exa\
mpleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset mongo-db-v2-collection'] = """
    type: group
    short-summary: datafactory dataset sub group mongo-db-v2-collection
"""

helps['datafactory dataset mongo-db-v2-collection create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset mongo-db-v2-collection create --type "AzureBlob" --linked-service-name "{\\"type\
\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"t\
ype\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exa\
mpleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset mongo-db-v2-collection create --type "AzureBlob" --description "Example descripti\
on" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --\
parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "\
exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset mongo-db-v2-collection update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset mongo-db-v2-collection create --type "AzureBlob" --linked-service-name "{\\"type\
\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"t\
ype\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exa\
mpleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset mongo-db-v2-collection create --type "AzureBlob" --description "Example descripti\
on" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --\
parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "\
exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset my-sql-table'] = """
    type: group
    short-summary: datafactory dataset sub group my-sql-table
"""

helps['datafactory dataset my-sql-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset my-sql-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Link\
edServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"S\
tring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactory\
Name" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset my-sql-table create --type "AzureBlob" --description "Example description" --link\
ed-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters\
 "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDat\
aset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset my-sql-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset my-sql-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Link\
edServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"S\
tring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactory\
Name" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset my-sql-table create --type "AzureBlob" --description "Example description" --link\
ed-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters\
 "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDat\
aset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset netezza-table'] = """
    type: group
    short-summary: datafactory dataset sub group netezza-table
"""

helps['datafactory dataset netezza-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset netezza-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Lin\
kedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"\
String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactor\
yName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset netezza-table create --type "AzureBlob" --description "Example description" --lin\
ked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameter\
s "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDa\
taset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset netezza-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset netezza-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Lin\
kedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"\
String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactor\
yName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset netezza-table create --type "AzureBlob" --description "Example description" --lin\
ked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameter\
s "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDa\
taset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset o-data-resource'] = """
    type: group
    short-summary: datafactory dataset sub group o-data-resource
"""

helps['datafactory dataset o-data-resource create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset o-data-resource create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"L\
inkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset o-data-resource create --type "AzureBlob" --description "Example description" --l\
inked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramet\
ers "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "example\
Dataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset o-data-resource update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset o-data-resource create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"L\
inkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset o-data-resource create --type "AzureBlob" --description "Example description" --l\
inked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramet\
ers "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "example\
Dataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset odbc-table'] = """
    type: group
    short-summary: datafactory dataset sub group odbc-table
"""

helps['datafactory dataset odbc-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset odbc-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Linked\
ServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"Str\
ing\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryNa\
me" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset odbc-table create --type "AzureBlob" --description "Example description" --linked\
-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "\
{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDatas\
et" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset odbc-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset odbc-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Linked\
ServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"Str\
ing\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryNa\
me" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset odbc-table create --type "AzureBlob" --description "Example description" --linked\
-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "\
{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDatas\
et" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset office365-table'] = """
    type: group
    short-summary: datafactory dataset sub group office365-table
"""

helps['datafactory dataset office365-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset office365-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"L\
inkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset office365-table create --type "AzureBlob" --description "Example description" --l\
inked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramet\
ers "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "example\
Dataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset office365-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset office365-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"L\
inkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset office365-table create --type "AzureBlob" --description "Example description" --l\
inked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramet\
ers "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "example\
Dataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset oracle-service-cloud-object'] = """
    type: group
    short-summary: datafactory dataset sub group oracle-service-cloud-object
"""

helps['datafactory dataset oracle-service-cloud-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset oracle-service-cloud-object create --type "AzureBlob" --linked-service-name "{\\"\
type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\
\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name \
"exampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset oracle-service-cloud-object create --type "AzureBlob" --description "Example desc\
ription" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"\
}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-n\
ame "exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset oracle-service-cloud-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset oracle-service-cloud-object create --type "AzureBlob" --linked-service-name "{\\"\
type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\
\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name \
"exampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset oracle-service-cloud-object create --type "AzureBlob" --description "Example desc\
ription" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"\
}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-n\
ame "exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset oracle-table'] = """
    type: group
    short-summary: datafactory dataset sub group oracle-table
"""

helps['datafactory dataset oracle-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset oracle-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Link\
edServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"S\
tring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactory\
Name" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset oracle-table create --type "AzureBlob" --description "Example description" --link\
ed-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters\
 "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDat\
aset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset oracle-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset oracle-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Link\
edServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"S\
tring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactory\
Name" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset oracle-table create --type "AzureBlob" --description "Example description" --link\
ed-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters\
 "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDat\
aset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset orc'] = """
    type: group
    short-summary: datafactory dataset sub group orc
"""

helps['datafactory dataset orc create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset orc create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"LinkedService\
Reference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"}\
,\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryName" --r\
esource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset orc create --type "AzureBlob" --description "Example description" --linked-servic\
e-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyF\
ileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --f\
actory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset orc update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset orc create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"LinkedService\
Reference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"}\
,\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryName" --r\
esource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset orc create --type "AzureBlob" --description "Example description" --linked-servic\
e-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyF\
ileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --f\
actory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset parquet'] = """
    type: group
    short-summary: datafactory dataset sub group parquet
"""

helps['datafactory dataset parquet create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset parquet create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"LinkedSer\
viceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\
\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryName"\
 --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset parquet create --type "AzureBlob" --description "Example description" --linked-se\
rvice-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\\
"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset"\
 --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset parquet update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset parquet create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"LinkedSer\
viceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\
\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryName"\
 --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset parquet create --type "AzureBlob" --description "Example description" --linked-se\
rvice-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\\
"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset"\
 --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset paypal-object'] = """
    type: group
    short-summary: datafactory dataset sub group paypal-object
"""

helps['datafactory dataset paypal-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset paypal-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Lin\
kedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"\
String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactor\
yName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset paypal-object create --type "AzureBlob" --description "Example description" --lin\
ked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameter\
s "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDa\
taset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset paypal-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset paypal-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Lin\
kedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"\
String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactor\
yName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset paypal-object create --type "AzureBlob" --description "Example description" --lin\
ked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameter\
s "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDa\
taset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset phoenix-object'] = """
    type: group
    short-summary: datafactory dataset sub group phoenix-object
"""

helps['datafactory dataset phoenix-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset phoenix-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Li\
nkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\\
"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFacto\
ryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset phoenix-object create --type "AzureBlob" --description "Example description" --li\
nked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramete\
rs "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleD\
ataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset phoenix-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset phoenix-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Li\
nkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\\
"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFacto\
ryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset phoenix-object create --type "AzureBlob" --description "Example description" --li\
nked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramete\
rs "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleD\
ataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset postgre-sql-table'] = """
    type: group
    short-summary: datafactory dataset sub group postgre-sql-table
"""

helps['datafactory dataset postgre-sql-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset postgre-sql-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\\
"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\"\
:\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFa\
ctoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset postgre-sql-table create --type "AzureBlob" --description "Example description" -\
-linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --param\
eters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "examp\
leDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset postgre-sql-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset postgre-sql-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\\
"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\"\
:\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFa\
ctoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset postgre-sql-table create --type "AzureBlob" --description "Example description" -\
-linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --param\
eters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "examp\
leDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset presto-object'] = """
    type: group
    short-summary: datafactory dataset sub group presto-object
"""

helps['datafactory dataset presto-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset presto-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Lin\
kedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"\
String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactor\
yName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset presto-object create --type "AzureBlob" --description "Example description" --lin\
ked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameter\
s "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDa\
taset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset presto-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset presto-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Lin\
kedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"\
String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactor\
yName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset presto-object create --type "AzureBlob" --description "Example description" --lin\
ked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameter\
s "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDa\
taset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset quick-books-object'] = """
    type: group
    short-summary: datafactory dataset sub group quick-books-object
"""

helps['datafactory dataset quick-books-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset quick-books-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset quick-books-object create --type "AzureBlob" --description "Example description" \
--linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --para\
meters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exam\
pleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset quick-books-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset quick-books-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset quick-books-object create --type "AzureBlob" --description "Example description" \
--linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --para\
meters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exam\
pleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset relational-table'] = """
    type: group
    short-summary: datafactory dataset sub group relational-table
"""

helps['datafactory dataset relational-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset relational-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"\
LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset relational-table create --type "AzureBlob" --description "Example description" --\
linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parame\
ters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampl\
eDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset relational-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset relational-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"\
LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset relational-table create --type "AzureBlob" --description "Example description" --\
linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parame\
ters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampl\
eDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset responsys-object'] = """
    type: group
    short-summary: datafactory dataset sub group responsys-object
"""

helps['datafactory dataset responsys-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset responsys-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"\
LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset responsys-object create --type "AzureBlob" --description "Example description" --\
linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parame\
ters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampl\
eDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset responsys-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset responsys-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"\
LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset responsys-object create --type "AzureBlob" --description "Example description" --\
linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parame\
ters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampl\
eDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset rest-resource'] = """
    type: group
    short-summary: datafactory dataset sub group rest-resource
"""

helps['datafactory dataset rest-resource create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset rest-resource create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Lin\
kedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"\
String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactor\
yName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset rest-resource create --type "AzureBlob" --description "Example description" --lin\
ked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameter\
s "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDa\
taset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset rest-resource update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset rest-resource create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Lin\
kedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"\
String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactor\
yName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset rest-resource create --type "AzureBlob" --description "Example description" --lin\
ked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameter\
s "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDa\
taset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset salesforce-marketing-cloud-object'] = """
    type: group
    short-summary: datafactory dataset sub group salesforce-marketing-cloud-object
"""

helps['datafactory dataset salesforce-marketing-cloud-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset salesforce-marketing-cloud-object create --type "AzureBlob" --linked-service-name\
 "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileNam\
e\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory\
-name "exampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset salesforce-marketing-cloud-object create --type "AzureBlob" --description "Exampl\
e description" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ\
ice\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dat\
aset-name "exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset salesforce-marketing-cloud-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset salesforce-marketing-cloud-object create --type "AzureBlob" --linked-service-name\
 "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileNam\
e\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory\
-name "exampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset salesforce-marketing-cloud-object create --type "AzureBlob" --description "Exampl\
e description" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServ\
ice\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dat\
aset-name "exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset salesforce-object'] = """
    type: group
    short-summary: datafactory dataset sub group salesforce-object
"""

helps['datafactory dataset salesforce-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset salesforce-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\\
"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\"\
:\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFa\
ctoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset salesforce-object create --type "AzureBlob" --description "Example description" -\
-linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --param\
eters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "examp\
leDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset salesforce-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset salesforce-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\\
"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\"\
:\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFa\
ctoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset salesforce-object create --type "AzureBlob" --description "Example description" -\
-linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --param\
eters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "examp\
leDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset salesforce-service-cloud-object'] = """
    type: group
    short-summary: datafactory dataset sub group salesforce-service-cloud-object
"""

helps['datafactory dataset salesforce-service-cloud-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset salesforce-service-cloud-object create --type "AzureBlob" --linked-service-name "\
{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\
\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-\
name "exampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset salesforce-service-cloud-object create --type "AzureBlob" --description "Example \
description" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServic\
e\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --datas\
et-name "exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset salesforce-service-cloud-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset salesforce-service-cloud-object create --type "AzureBlob" --linked-service-name "\
{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\
\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-\
name "exampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset salesforce-service-cloud-object create --type "AzureBlob" --description "Example \
description" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServic\
e\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --datas\
et-name "exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset sap-bw-cube'] = """
    type: group
    short-summary: datafactory dataset sub group sap-bw-cube
"""

helps['datafactory dataset sap-bw-cube create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset sap-bw-cube create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Linke\
dServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"St\
ring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryN\
ame" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset sap-bw-cube create --type "AzureBlob" --description "Example description" --linke\
d-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters \
"{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleData\
set" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset sap-bw-cube update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset sap-bw-cube create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Linke\
dServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"St\
ring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryN\
ame" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset sap-bw-cube create --type "AzureBlob" --description "Example description" --linke\
d-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters \
"{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleData\
set" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset sap-cloud-for-customer-resource'] = """
    type: group
    short-summary: datafactory dataset sub group sap-cloud-for-customer-resource
"""

helps['datafactory dataset sap-cloud-for-customer-resource create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset sap-cloud-for-customer-resource create --type "AzureBlob" --linked-service-name "\
{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\
\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-\
name "exampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset sap-cloud-for-customer-resource create --type "AzureBlob" --description "Example \
description" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServic\
e\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --datas\
et-name "exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset sap-cloud-for-customer-resource update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset sap-cloud-for-customer-resource create --type "AzureBlob" --linked-service-name "\
{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\
\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-\
name "exampleFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset sap-cloud-for-customer-resource create --type "AzureBlob" --description "Example \
description" --linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedServic\
e\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --datas\
et-name "exampleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset sap-ecc-resource'] = """
    type: group
    short-summary: datafactory dataset sub group sap-ecc-resource
"""

helps['datafactory dataset sap-ecc-resource create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset sap-ecc-resource create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"\
LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset sap-ecc-resource create --type "AzureBlob" --description "Example description" --\
linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parame\
ters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampl\
eDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset sap-ecc-resource update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset sap-ecc-resource create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"\
LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset sap-ecc-resource create --type "AzureBlob" --description "Example description" --\
linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parame\
ters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampl\
eDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset sap-hana-table'] = """
    type: group
    short-summary: datafactory dataset sub group sap-hana-table
"""

helps['datafactory dataset sap-hana-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset sap-hana-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Li\
nkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\\
"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFacto\
ryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset sap-hana-table create --type "AzureBlob" --description "Example description" --li\
nked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramete\
rs "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleD\
ataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset sap-hana-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset sap-hana-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Li\
nkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\\
"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFacto\
ryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset sap-hana-table create --type "AzureBlob" --description "Example description" --li\
nked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramete\
rs "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleD\
ataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset sap-open-hub-table'] = """
    type: group
    short-summary: datafactory dataset sub group sap-open-hub-table
"""

helps['datafactory dataset sap-open-hub-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset sap-open-hub-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset sap-open-hub-table create --type "AzureBlob" --description "Example description" \
--linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --para\
meters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exam\
pleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset sap-open-hub-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset sap-open-hub-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset sap-open-hub-table create --type "AzureBlob" --description "Example description" \
--linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --para\
meters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exam\
pleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset sap-table-resource'] = """
    type: group
    short-summary: datafactory dataset sub group sap-table-resource
"""

helps['datafactory dataset sap-table-resource create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset sap-table-resource create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset sap-table-resource create --type "AzureBlob" --description "Example description" \
--linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --para\
meters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exam\
pleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset sap-table-resource update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset sap-table-resource create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset sap-table-resource create --type "AzureBlob" --description "Example description" \
--linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --para\
meters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exam\
pleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset service-now-object'] = """
    type: group
    short-summary: datafactory dataset sub group service-now-object
"""

helps['datafactory dataset service-now-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset service-now-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset service-now-object create --type "AzureBlob" --description "Example description" \
--linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --para\
meters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exam\
pleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset service-now-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset service-now-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\
\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\
\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampl\
eFactoryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset service-now-object create --type "AzureBlob" --description "Example description" \
--linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --para\
meters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exam\
pleDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset shopify-object'] = """
    type: group
    short-summary: datafactory dataset sub group shopify-object
"""

helps['datafactory dataset shopify-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset shopify-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Li\
nkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\\
"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFacto\
ryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset shopify-object create --type "AzureBlob" --description "Example description" --li\
nked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramete\
rs "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleD\
ataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset shopify-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset shopify-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Li\
nkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\\
"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFacto\
ryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset shopify-object create --type "AzureBlob" --description "Example description" --li\
nked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramete\
rs "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleD\
ataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset snowflake-table'] = """
    type: group
    short-summary: datafactory dataset sub group snowflake-table
"""

helps['datafactory dataset snowflake-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset snowflake-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"L\
inkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset snowflake-table create --type "AzureBlob" --description "Example description" --l\
inked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramet\
ers "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "example\
Dataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset snowflake-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset snowflake-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"L\
inkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset snowflake-table create --type "AzureBlob" --description "Example description" --l\
inked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramet\
ers "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "example\
Dataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset spark-object'] = """
    type: group
    short-summary: datafactory dataset sub group spark-object
"""

helps['datafactory dataset spark-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset spark-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Link\
edServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"S\
tring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactory\
Name" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset spark-object create --type "AzureBlob" --description "Example description" --link\
ed-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters\
 "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDat\
aset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset spark-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset spark-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Link\
edServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"S\
tring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactory\
Name" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset spark-object create --type "AzureBlob" --description "Example description" --link\
ed-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters\
 "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDat\
aset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset sql-server-table'] = """
    type: group
    short-summary: datafactory dataset sub group sql-server-table
"""

helps['datafactory dataset sql-server-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset sql-server-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"\
LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset sql-server-table create --type "AzureBlob" --description "Example description" --\
linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parame\
ters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampl\
eDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset sql-server-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset sql-server-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"\
LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\
\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFac\
toryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset sql-server-table create --type "AzureBlob" --description "Example description" --\
linked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parame\
ters "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampl\
eDataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset square-object'] = """
    type: group
    short-summary: datafactory dataset sub group square-object
"""

helps['datafactory dataset square-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset square-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Lin\
kedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"\
String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactor\
yName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset square-object create --type "AzureBlob" --description "Example description" --lin\
ked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameter\
s "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDa\
taset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset square-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset square-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Lin\
kedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"\
String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactor\
yName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset square-object create --type "AzureBlob" --description "Example description" --lin\
ked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameter\
s "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDa\
taset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset sybase-table'] = """
    type: group
    short-summary: datafactory dataset sub group sybase-table
"""

helps['datafactory dataset sybase-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset sybase-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Link\
edServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"S\
tring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactory\
Name" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset sybase-table create --type "AzureBlob" --description "Example description" --link\
ed-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters\
 "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDat\
aset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset sybase-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset sybase-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Link\
edServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"S\
tring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactory\
Name" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset sybase-table create --type "AzureBlob" --description "Example description" --link\
ed-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters\
 "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDat\
aset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset teradata-table'] = """
    type: group
    short-summary: datafactory dataset sub group teradata-table
"""

helps['datafactory dataset teradata-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset teradata-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Li\
nkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\\
"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFacto\
ryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset teradata-table create --type "AzureBlob" --description "Example description" --li\
nked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramete\
rs "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleD\
ataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset teradata-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset teradata-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Li\
nkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\\
"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFacto\
ryName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset teradata-table create --type "AzureBlob" --description "Example description" --li\
nked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --paramete\
rs "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleD\
ataset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset vertica-table'] = """
    type: group
    short-summary: datafactory dataset sub group vertica-table
"""

helps['datafactory dataset vertica-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset vertica-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Lin\
kedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"\
String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactor\
yName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset vertica-table create --type "AzureBlob" --description "Example description" --lin\
ked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameter\
s "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDa\
taset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset vertica-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset vertica-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Lin\
kedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"\
String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactor\
yName" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset vertica-table create --type "AzureBlob" --description "Example description" --lin\
ked-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameter\
s "{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDa\
taset" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset web-table'] = """
    type: group
    short-summary: datafactory dataset sub group web-table
"""

helps['datafactory dataset web-table create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset web-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"LinkedS\
erviceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"Stri\
ng\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryNam\
e" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset web-table create --type "AzureBlob" --description "Example description" --linked-\
service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\
\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDatase\
t" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset web-table update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset web-table create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"LinkedS\
erviceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"Stri\
ng\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryNam\
e" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset web-table create --type "AzureBlob" --description "Example description" --linked-\
service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\
\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDatase\
t" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset xero-object'] = """
    type: group
    short-summary: datafactory dataset sub group xero-object
"""

helps['datafactory dataset xero-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset xero-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Linke\
dServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"St\
ring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryN\
ame" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset xero-object create --type "AzureBlob" --description "Example description" --linke\
d-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters \
"{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleData\
set" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset xero-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset xero-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Linke\
dServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"St\
ring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryN\
ame" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset xero-object create --type "AzureBlob" --description "Example description" --linke\
d-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters \
"{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleData\
set" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset zoho-object'] = """
    type: group
    short-summary: datafactory dataset sub group zoho-object
"""

helps['datafactory dataset zoho-object create'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset zoho-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Linke\
dServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"St\
ring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryN\
ame" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset zoho-object create --type "AzureBlob" --description "Example description" --linke\
d-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters \
"{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleData\
set" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset zoho-object update'] = """
    type: command
    short-summary: Creates or updates a dataset.
    examples:
      - name: Datasets_Create
        text: |-
               az datafactory dataset zoho-object create --type "AzureBlob" --linked-service-name "{\\"type\\":\\"Linke\
dServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters "{\\"MyFileName\\":{\\"type\\":\\"St\
ring\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleDataset" --factory-name "exampleFactoryN\
ame" --resource-group "exampleResourceGroup"
      - name: Datasets_Update
        text: |-
               az datafactory dataset zoho-object create --type "AzureBlob" --description "Example description" --linke\
d-service-name "{\\"type\\":\\"LinkedServiceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"}" --parameters \
"{\\"MyFileName\\":{\\"type\\":\\"String\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}}" --dataset-name "exampleData\
set" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory dataset delete'] = """
    type: command
    short-summary: Deletes a dataset.
    examples:
      - name: Datasets_Delete
        text: |-
               az datafactory dataset delete --dataset-name "exampleDataset" --factory-name "exampleFactoryName" --reso\
urce-group "exampleResourceGroup"
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
               az datafactory pipeline list --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory pipeline show'] = """
    type: command
    short-summary: Gets a pipeline.
    examples:
      - name: Pipelines_Get
        text: |-
               az datafactory pipeline show --factory-name "exampleFactoryName" --pipeline-name "examplePipeline" --res\
ource-group "exampleResourceGroup"
"""

helps['datafactory pipeline create'] = """
    type: command
    short-summary: Creates or updates a pipeline.
    examples:
      - name: Pipelines_Create
        text: |-
               az datafactory pipeline create --factory-name "exampleFactoryName" --pipeline "{\\"properties\\":{\\"act\
ivities\\":[{\\"name\\":\\"ExampleForeachActivity\\",\\"type\\":\\"ForEach\\",\\"typeProperties\\":{\\"activities\\":[{\
\\"name\\":\\"ExampleCopyActivity\\",\\"type\\":\\"Copy\\",\\"inputs\\":[{\\"type\\":\\"DatasetReference\\",\\"paramete\
rs\\":{\\"MyFileName\\":\\"examplecontainer.csv\\",\\"MyFolderPath\\":\\"examplecontainer\\"},\\"referenceName\\":\\"ex\
ampleDataset\\"}],\\"outputs\\":[{\\"type\\":\\"DatasetReference\\",\\"parameters\\":{\\"MyFileName\\":{\\"type\\":\\"E\
xpression\\",\\"value\\":\\"@item()\\"},\\"MyFolderPath\\":\\"examplecontainer\\"},\\"referenceName\\":\\"exampleDatase\
t\\"}],\\"typeProperties\\":{\\"dataIntegrationUnits\\":32,\\"sink\\":{\\"type\\":\\"BlobSink\\"},\\"source\\":{\\"type\
\\":\\"BlobSource\\"}}}],\\"isSequential\\":true,\\"items\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@pipeline().pa\
rameters.OutputBlobNameList\\"}}}],\\"parameters\\":{\\"JobId\\":{\\"type\\":\\"String\\"},\\"OutputBlobNameList\\":{\\\
"type\\":\\"Array\\"}},\\"runDimensions\\":{\\"JobId\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@pipeline().paramet\
ers.JobId\\"}},\\"variables\\":{\\"TestVariableArray\\":{\\"type\\":\\"Array\\"}}}}" --pipeline-name "examplePipeline" \
--resource-group "exampleResourceGroup"
      - name: Pipelines_Update
        text: |-
               az datafactory pipeline create --factory-name "exampleFactoryName" --pipeline "{\\"properties\\":{\\"des\
cription\\":\\"Example description\\",\\"activities\\":[{\\"name\\":\\"ExampleForeachActivity\\",\\"type\\":\\"ForEach\
\\",\\"typeProperties\\":{\\"activities\\":[{\\"name\\":\\"ExampleCopyActivity\\",\\"type\\":\\"Copy\\",\\"inputs\\":[{\
\\"type\\":\\"DatasetReference\\",\\"parameters\\":{\\"MyFileName\\":\\"examplecontainer.csv\\",\\"MyFolderPath\\":\\"e\
xamplecontainer\\"},\\"referenceName\\":\\"exampleDataset\\"}],\\"outputs\\":[{\\"type\\":\\"DatasetReference\\",\\"par\
ameters\\":{\\"MyFileName\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@item()\\"},\\"MyFolderPath\\":\\"exampleconta\
iner\\"},\\"referenceName\\":\\"exampleDataset\\"}],\\"typeProperties\\":{\\"dataIntegrationUnits\\":32,\\"sink\\":{\\"\
type\\":\\"BlobSink\\"},\\"source\\":{\\"type\\":\\"BlobSource\\"}}}],\\"isSequential\\":true,\\"items\\":{\\"type\\":\
\\"Expression\\",\\"value\\":\\"@pipeline().parameters.OutputBlobNameList\\"}}}],\\"parameters\\":{\\"OutputBlobNameLis\
t\\":{\\"type\\":\\"Array\\"}}}}" --pipeline-name "examplePipeline" --resource-group "exampleResourceGroup"
"""

helps['datafactory pipeline update'] = """
    type: command
    short-summary: Creates or updates a pipeline.
    examples:
      - name: Pipelines_Create
        text: |-
               az datafactory pipeline create --factory-name "exampleFactoryName" --pipeline "{\\"properties\\":{\\"act\
ivities\\":[{\\"name\\":\\"ExampleForeachActivity\\",\\"type\\":\\"ForEach\\",\\"typeProperties\\":{\\"activities\\":[{\
\\"name\\":\\"ExampleCopyActivity\\",\\"type\\":\\"Copy\\",\\"inputs\\":[{\\"type\\":\\"DatasetReference\\",\\"paramete\
rs\\":{\\"MyFileName\\":\\"examplecontainer.csv\\",\\"MyFolderPath\\":\\"examplecontainer\\"},\\"referenceName\\":\\"ex\
ampleDataset\\"}],\\"outputs\\":[{\\"type\\":\\"DatasetReference\\",\\"parameters\\":{\\"MyFileName\\":{\\"type\\":\\"E\
xpression\\",\\"value\\":\\"@item()\\"},\\"MyFolderPath\\":\\"examplecontainer\\"},\\"referenceName\\":\\"exampleDatase\
t\\"}],\\"typeProperties\\":{\\"dataIntegrationUnits\\":32,\\"sink\\":{\\"type\\":\\"BlobSink\\"},\\"source\\":{\\"type\
\\":\\"BlobSource\\"}}}],\\"isSequential\\":true,\\"items\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@pipeline().pa\
rameters.OutputBlobNameList\\"}}}],\\"parameters\\":{\\"JobId\\":{\\"type\\":\\"String\\"},\\"OutputBlobNameList\\":{\\\
"type\\":\\"Array\\"}},\\"runDimensions\\":{\\"JobId\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@pipeline().paramet\
ers.JobId\\"}},\\"variables\\":{\\"TestVariableArray\\":{\\"type\\":\\"Array\\"}}}}" --pipeline-name "examplePipeline" \
--resource-group "exampleResourceGroup"
      - name: Pipelines_Update
        text: |-
               az datafactory pipeline create --factory-name "exampleFactoryName" --pipeline "{\\"properties\\":{\\"des\
cription\\":\\"Example description\\",\\"activities\\":[{\\"name\\":\\"ExampleForeachActivity\\",\\"type\\":\\"ForEach\
\\",\\"typeProperties\\":{\\"activities\\":[{\\"name\\":\\"ExampleCopyActivity\\",\\"type\\":\\"Copy\\",\\"inputs\\":[{\
\\"type\\":\\"DatasetReference\\",\\"parameters\\":{\\"MyFileName\\":\\"examplecontainer.csv\\",\\"MyFolderPath\\":\\"e\
xamplecontainer\\"},\\"referenceName\\":\\"exampleDataset\\"}],\\"outputs\\":[{\\"type\\":\\"DatasetReference\\",\\"par\
ameters\\":{\\"MyFileName\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@item()\\"},\\"MyFolderPath\\":\\"exampleconta\
iner\\"},\\"referenceName\\":\\"exampleDataset\\"}],\\"typeProperties\\":{\\"dataIntegrationUnits\\":32,\\"sink\\":{\\"\
type\\":\\"BlobSink\\"},\\"source\\":{\\"type\\":\\"BlobSource\\"}}}],\\"isSequential\\":true,\\"items\\":{\\"type\\":\
\\"Expression\\",\\"value\\":\\"@pipeline().parameters.OutputBlobNameList\\"}}}],\\"parameters\\":{\\"OutputBlobNameLis\
t\\":{\\"type\\":\\"Array\\"}}}}" --pipeline-name "examplePipeline" --resource-group "exampleResourceGroup"
"""

helps['datafactory pipeline delete'] = """
    type: command
    short-summary: Deletes a pipeline.
    examples:
      - name: Pipelines_Delete
        text: |-
               az datafactory pipeline delete --factory-name "exampleFactoryName" --pipeline-name "examplePipeline" --r\
esource-group "exampleResourceGroup"
"""

helps['datafactory pipeline create-run'] = """
    type: command
    short-summary: Creates a run of a pipeline.
    examples:
      - name: Pipelines_CreateRun
        text: |-
               az datafactory pipeline create-run --factory-name "exampleFactoryName" --parameters OutputBlobNameList=[\
\\"exampleoutput.csv\\"] --pipeline-name "examplePipeline" --resource-group "exampleResourceGroup"
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
               az datafactory pipeline-run show --factory-name "exampleFactoryName" --resource-group "exampleResourceGr\
oup" --run-id "2f7fdb90-5df1-4b8e-ac2f-064cfa58202b"
"""

helps['datafactory pipeline-run cancel'] = """
    type: command
    short-summary: Cancel a pipeline run by its run ID.
    examples:
      - name: PipelineRuns_Cancel
        text: |-
               az datafactory pipeline-run cancel --factory-name "exampleFactoryName" --resource-group "exampleResource\
Group" --run-id "16ac5348-ff82-4f95-a80d-638c1d47b721"
"""

helps['datafactory pipeline-run query-by-factory'] = """
    type: command
    short-summary: Query pipeline runs in the factory based on input filter conditions.
    examples:
      - name: PipelineRuns_QueryByFactory
        text: |-
               az datafactory pipeline-run query-by-factory --factory-name "exampleFactoryName" --filters operand=Pipel\
ineName operator=Equals values=[\\"examplePipeline\\"] --last-updated-after "2018-06-16T00:36:44.3345758Z" --last-updat\
ed-before "2018-06-16T00:49:48.3686473Z" --resource-group "exampleResourceGroup"
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
               az datafactory activity-run query-by-pipeline-run --factory-name "exampleFactoryName" --last-updated-aft\
er "2018-06-16T00:36:44.3345758Z" --last-updated-before "2018-06-16T00:49:48.3686473Z" --resource-group "exampleResourc\
eGroup" --run-id "2f7fdb90-5df1-4b8e-ac2f-064cfa58202b"
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
               az datafactory trigger list --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory trigger show'] = """
    type: command
    short-summary: Gets a trigger.
    examples:
      - name: Triggers_Get
        text: |-
               az datafactory trigger show --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup" \
--trigger-name "exampleTrigger"
"""

helps['datafactory trigger create'] = """
    type: command
    short-summary: Creates or updates a trigger.
    examples:
      - name: Triggers_Create
        text: |-
               az datafactory trigger create --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup\
" --properties "{\\"type\\":\\"ScheduleTrigger\\",\\"pipelines\\":[{\\"parameters\\":{\\"OutputBlobNameList\\":[\\"exam\
pleoutput.csv\\"]},\\"pipelineReference\\":{\\"type\\":\\"PipelineReference\\",\\"referenceName\\":\\"examplePipeline\\\
"}}],\\"typeProperties\\":{\\"recurrence\\":{\\"endTime\\":\\"2018-06-16T00:55:13.8441801Z\\",\\"frequency\\":\\"Minute\
\\",\\"interval\\":4,\\"startTime\\":\\"2018-06-16T00:39:13.8441801Z\\",\\"timeZone\\":\\"UTC\\"}}}" --trigger-name "ex\
ampleTrigger"
      - name: Triggers_Update
        text: |-
               az datafactory trigger create --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup\
" --properties "{\\"type\\":\\"ScheduleTrigger\\",\\"description\\":\\"Example description\\",\\"pipelines\\":[{\\"para\
meters\\":{\\"OutputBlobNameList\\":[\\"exampleoutput.csv\\"]},\\"pipelineReference\\":{\\"type\\":\\"PipelineReference\
\\",\\"referenceName\\":\\"examplePipeline\\"}}],\\"typeProperties\\":{\\"recurrence\\":{\\"endTime\\":\\"2018-06-16T00\
:55:14.905167Z\\",\\"frequency\\":\\"Minute\\",\\"interval\\":4,\\"startTime\\":\\"2018-06-16T00:39:14.905167Z\\",\\"ti\
meZone\\":\\"UTC\\"}}}" --trigger-name "exampleTrigger"
"""

helps['datafactory trigger update'] = """
    type: command
    short-summary: Creates or updates a trigger.
    examples:
      - name: Triggers_Create
        text: |-
               az datafactory trigger create --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup\
" --properties "{\\"type\\":\\"ScheduleTrigger\\",\\"pipelines\\":[{\\"parameters\\":{\\"OutputBlobNameList\\":[\\"exam\
pleoutput.csv\\"]},\\"pipelineReference\\":{\\"type\\":\\"PipelineReference\\",\\"referenceName\\":\\"examplePipeline\\\
"}}],\\"typeProperties\\":{\\"recurrence\\":{\\"endTime\\":\\"2018-06-16T00:55:13.8441801Z\\",\\"frequency\\":\\"Minute\
\\",\\"interval\\":4,\\"startTime\\":\\"2018-06-16T00:39:13.8441801Z\\",\\"timeZone\\":\\"UTC\\"}}}" --trigger-name "ex\
ampleTrigger"
      - name: Triggers_Update
        text: |-
               az datafactory trigger create --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup\
" --properties "{\\"type\\":\\"ScheduleTrigger\\",\\"description\\":\\"Example description\\",\\"pipelines\\":[{\\"para\
meters\\":{\\"OutputBlobNameList\\":[\\"exampleoutput.csv\\"]},\\"pipelineReference\\":{\\"type\\":\\"PipelineReference\
\\",\\"referenceName\\":\\"examplePipeline\\"}}],\\"typeProperties\\":{\\"recurrence\\":{\\"endTime\\":\\"2018-06-16T00\
:55:14.905167Z\\",\\"frequency\\":\\"Minute\\",\\"interval\\":4,\\"startTime\\":\\"2018-06-16T00:39:14.905167Z\\",\\"ti\
meZone\\":\\"UTC\\"}}}" --trigger-name "exampleTrigger"
"""

helps['datafactory trigger delete'] = """
    type: command
    short-summary: Deletes a trigger.
    examples:
      - name: Triggers_Delete
        text: |-
               az datafactory trigger delete --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup\
" --trigger-name "exampleTrigger"
"""

helps['datafactory trigger get-event-subscription-status'] = """
    type: command
    short-summary: Get a trigger's event subscription status.
    examples:
      - name: Triggers_GetEventSubscriptionStatus
        text: |-
               az datafactory trigger get-event-subscription-status --factory-name "exampleFactoryName" --resource-grou\
p "exampleResourceGroup" --trigger-name "exampleTrigger"
"""

helps['datafactory trigger query-by-factory'] = """
    type: command
    short-summary: Query triggers.
    examples:
      - name: Triggers_QueryByFactory
        text: |-
               az datafactory trigger query-by-factory --factory-name "exampleFactoryName" --parent-trigger-name "examp\
leTrigger" --resource-group "exampleResourceGroup"
"""

helps['datafactory trigger start'] = """
    type: command
    short-summary: Starts a trigger.
    examples:
      - name: Triggers_Start
        text: |-
               az datafactory trigger start --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"\
 --trigger-name "exampleTrigger"
"""

helps['datafactory trigger stop'] = """
    type: command
    short-summary: Stops a trigger.
    examples:
      - name: Triggers_Stop
        text: |-
               az datafactory trigger stop --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup" \
--trigger-name "exampleTrigger"
"""

helps['datafactory trigger subscribe-to-event'] = """
    type: command
    short-summary: Subscribe event trigger to events.
    examples:
      - name: Triggers_SubscribeToEvents
        text: |-
               az datafactory trigger subscribe-to-event --factory-name "exampleFactoryName" --resource-group "exampleR\
esourceGroup" --trigger-name "exampleTrigger"
"""

helps['datafactory trigger unsubscribe-from-event'] = """
    type: command
    short-summary: Unsubscribe event trigger from events.
    examples:
      - name: Triggers_UnsubscribeFromEvents
        text: |-
               az datafactory trigger unsubscribe-from-event --factory-name "exampleFactoryName" --resource-group "exam\
pleResourceGroup" --trigger-name "exampleTrigger"
"""

helps['datafactory trigger-run'] = """
    type: group
    short-summary: datafactory trigger-run
"""

helps['datafactory trigger-run query-by-factory'] = """
    type: command
    short-summary: Query trigger runs.
    examples:
      - name: TriggerRuns_QueryByFactory
        text: |-
               az datafactory trigger-run query-by-factory --factory-name "exampleFactoryName" --filters operand=Trigge\
rName operator=Equals values=[\\"exampleTrigger\\"] --last-updated-after "2018-06-16T00:36:44.3345758Z" --last-updated-\
before "2018-06-16T00:49:48.3686473Z" --resource-group "exampleResourceGroup"
"""

helps['datafactory trigger-run rerun'] = """
    type: command
    short-summary: Rerun single trigger instance by runId.
    examples:
      - name: Triggers_Rerun
        text: |-
               az datafactory trigger-run rerun --factory-name "exampleFactoryName" --resource-group "exampleResourceGr\
oup" --run-id "2f7fdb90-5df1-4b8e-ac2f-064cfa58202b" --trigger-name "exampleTrigger"
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
               az datafactory data-flow list --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup\
"
"""

helps['datafactory data-flow show'] = """
    type: command
    short-summary: Gets a data flow.
    examples:
      - name: DataFlows_Get
        text: |-
               az datafactory data-flow show --data-flow-name "exampleDataFlow" --factory-name "exampleFactoryName" --r\
esource-group "exampleResourceGroup"
"""

helps['datafactory data-flow create'] = """
    type: command
    short-summary: Creates or updates a data flow.
    examples:
      - name: DataFlows_Create
        text: |-
               az datafactory data-flow create --properties "{\\"type\\":\\"MappingDataFlow\\",\\"description\\":\\"Sam\
ple demo data flow to convert currencies showing usage of union, derive and conditional split transformation.\\",\\"typ\
eProperties\\":{\\"script\\":\\"source(output(PreviousConversionRate as double,Country as string,DateTime1 as string,Cu\
rrentConversionRate as double),allowSchemaDrift: false,validateSchema: false) ~> USDCurrency\\\\nsource(output(Previous\
ConversionRate as double,Country as string,DateTime1 as string,CurrentConversionRate as double),allowSchemaDrift: true,\
validateSchema: false) ~> CADSource\\\\nUSDCurrency, CADSource union(byName: true)~> Union\\\\nUnion derive(NewCurrency\
Rate = round(CurrentConversionRate*1.25)) ~> NewCurrencyColumn\\\\nNewCurrencyColumn split(Country == 'USD',Country == \
'CAD',disjoint: false) ~> ConditionalSplit1@(USD, CAD)\\\\nConditionalSplit1@USD sink(saveMode:'overwrite' ) ~> USDSink\
\\\\nConditionalSplit1@CAD sink(saveMode:'overwrite' ) ~> CADSink\\",\\"sinks\\":[{\\"name\\":\\"USDSink\\",\\"dataset\
\\":{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"USDOutput\\"}},{\\"name\\":\\"CADSink\\",\\"dataset\\":{\
\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CADOutput\\"}}],\\"sources\\":[{\\"name\\":\\"USDCurrency\\",\
\\"dataset\\":{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CurrencyDatasetUSD\\"}},{\\"name\\":\\"CADSourc\
e\\",\\"dataset\\":{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CurrencyDatasetCAD\\"}}]}}" --data-flow-na\
me "exampleDataFlow" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
      - name: DataFlows_Update
        text: |-
               az datafactory data-flow create --properties "{\\"type\\":\\"MappingDataFlow\\",\\"description\\":\\"Sam\
ple demo data flow to convert currencies showing usage of union, derive and conditional split transformation.\\",\\"typ\
eProperties\\":{\\"script\\":\\"source(output(PreviousConversionRate as double,Country as string,DateTime1 as string,Cu\
rrentConversionRate as double),allowSchemaDrift: false,validateSchema: false) ~> USDCurrency\\\\nsource(output(Previous\
ConversionRate as double,Country as string,DateTime1 as string,CurrentConversionRate as double),allowSchemaDrift: true,\
validateSchema: false) ~> CADSource\\\\nUSDCurrency, CADSource union(byName: true)~> Union\\\\nUnion derive(NewCurrency\
Rate = round(CurrentConversionRate*1.25)) ~> NewCurrencyColumn\\\\nNewCurrencyColumn split(Country == 'USD',Country == \
'CAD',disjoint: false) ~> ConditionalSplit1@(USD, CAD)\\\\nConditionalSplit1@USD sink(saveMode:'overwrite' ) ~> USDSink\
\\\\nConditionalSplit1@CAD sink(saveMode:'overwrite' ) ~> CADSink\\",\\"sinks\\":[{\\"name\\":\\"USDSink\\",\\"dataset\
\\":{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"USDOutput\\"}},{\\"name\\":\\"CADSink\\",\\"dataset\\":{\
\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CADOutput\\"}}],\\"sources\\":[{\\"name\\":\\"USDCurrency\\",\
\\"dataset\\":{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CurrencyDatasetUSD\\"}},{\\"name\\":\\"CADSourc\
e\\",\\"dataset\\":{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CurrencyDatasetCAD\\"}}]}}" --data-flow-na\
me "exampleDataFlow" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory data-flow update'] = """
    type: command
    short-summary: Creates or updates a data flow.
    examples:
      - name: DataFlows_Create
        text: |-
               az datafactory data-flow create --properties "{\\"type\\":\\"MappingDataFlow\\",\\"description\\":\\"Sam\
ple demo data flow to convert currencies showing usage of union, derive and conditional split transformation.\\",\\"typ\
eProperties\\":{\\"script\\":\\"source(output(PreviousConversionRate as double,Country as string,DateTime1 as string,Cu\
rrentConversionRate as double),allowSchemaDrift: false,validateSchema: false) ~> USDCurrency\\\\nsource(output(Previous\
ConversionRate as double,Country as string,DateTime1 as string,CurrentConversionRate as double),allowSchemaDrift: true,\
validateSchema: false) ~> CADSource\\\\nUSDCurrency, CADSource union(byName: true)~> Union\\\\nUnion derive(NewCurrency\
Rate = round(CurrentConversionRate*1.25)) ~> NewCurrencyColumn\\\\nNewCurrencyColumn split(Country == 'USD',Country == \
'CAD',disjoint: false) ~> ConditionalSplit1@(USD, CAD)\\\\nConditionalSplit1@USD sink(saveMode:'overwrite' ) ~> USDSink\
\\\\nConditionalSplit1@CAD sink(saveMode:'overwrite' ) ~> CADSink\\",\\"sinks\\":[{\\"name\\":\\"USDSink\\",\\"dataset\
\\":{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"USDOutput\\"}},{\\"name\\":\\"CADSink\\",\\"dataset\\":{\
\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CADOutput\\"}}],\\"sources\\":[{\\"name\\":\\"USDCurrency\\",\
\\"dataset\\":{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CurrencyDatasetUSD\\"}},{\\"name\\":\\"CADSourc\
e\\",\\"dataset\\":{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CurrencyDatasetCAD\\"}}]}}" --data-flow-na\
me "exampleDataFlow" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
      - name: DataFlows_Update
        text: |-
               az datafactory data-flow create --properties "{\\"type\\":\\"MappingDataFlow\\",\\"description\\":\\"Sam\
ple demo data flow to convert currencies showing usage of union, derive and conditional split transformation.\\",\\"typ\
eProperties\\":{\\"script\\":\\"source(output(PreviousConversionRate as double,Country as string,DateTime1 as string,Cu\
rrentConversionRate as double),allowSchemaDrift: false,validateSchema: false) ~> USDCurrency\\\\nsource(output(Previous\
ConversionRate as double,Country as string,DateTime1 as string,CurrentConversionRate as double),allowSchemaDrift: true,\
validateSchema: false) ~> CADSource\\\\nUSDCurrency, CADSource union(byName: true)~> Union\\\\nUnion derive(NewCurrency\
Rate = round(CurrentConversionRate*1.25)) ~> NewCurrencyColumn\\\\nNewCurrencyColumn split(Country == 'USD',Country == \
'CAD',disjoint: false) ~> ConditionalSplit1@(USD, CAD)\\\\nConditionalSplit1@USD sink(saveMode:'overwrite' ) ~> USDSink\
\\\\nConditionalSplit1@CAD sink(saveMode:'overwrite' ) ~> CADSink\\",\\"sinks\\":[{\\"name\\":\\"USDSink\\",\\"dataset\
\\":{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"USDOutput\\"}},{\\"name\\":\\"CADSink\\",\\"dataset\\":{\
\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CADOutput\\"}}],\\"sources\\":[{\\"name\\":\\"USDCurrency\\",\
\\"dataset\\":{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CurrencyDatasetUSD\\"}},{\\"name\\":\\"CADSourc\
e\\",\\"dataset\\":{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"CurrencyDatasetCAD\\"}}]}}" --data-flow-na\
me "exampleDataFlow" --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
"""

helps['datafactory data-flow delete'] = """
    type: command
    short-summary: Deletes a data flow.
    examples:
      - name: DataFlows_Delete
        text: |-
               az datafactory data-flow delete --data-flow-name "exampleDataFlow" --factory-name "exampleFactoryName" -\
-resource-group "exampleResourceGroup"
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
               az datafactory data-flow-debug-session create --factory-name "exampleFactoryName" --resource-group "exam\
pleResourceGroup" --integration-runtime "{\\"name\\":\\"ir1\\",\\"properties\\":{\\"type\\":\\"Managed\\",\\"typeProper\
ties\\":{\\"computeProperties\\":{\\"dataFlowProperties\\":{\\"computeType\\":\\"General\\",\\"coreCount\\":48,\\"timeT\
oLive\\":10},\\"location\\":\\"AutoResolve\\"}}}}" --time-to-live 60
"""

helps['datafactory data-flow-debug-session delete'] = """
    type: command
    short-summary: Deletes a data flow debug session.
    examples:
      - name: DataFlowDebugSession_Delete
        text: |-
               az datafactory data-flow-debug-session delete --factory-name "exampleFactoryName" --resource-group "exam\
pleResourceGroup" --session-id "91fb57e0-8292-47be-89ff-c8f2d2bb2a7e"
"""

helps['datafactory data-flow-debug-session add-data-flow'] = """
    type: command
    short-summary: Add a data flow into debug session.
    examples:
      - name: DataFlowDebugSession_AddDataFlow
        text: |-
               az datafactory data-flow-debug-session add-data-flow --factory-name "exampleFactoryName" --resource-grou\
p "exampleResourceGroup" --data-flow "{\\"name\\":\\"dataflow1\\",\\"properties\\":{\\"type\\":\\"MappingDataFlow\\",\\\
"typeProperties\\":{\\"script\\":\\"\\\\n\\\\nsource(output(\\\\n\\\\t\\\\tColumn_1 as string\\\\n\\\\t),\\\\n\\\\tallo\
wSchemaDrift: true,\\\\n\\\\tvalidateSchema: false) ~> source1\\",\\"sinks\\":[],\\"sources\\":[{\\"name\\":\\"source1\
\\",\\"dataset\\":{\\"type\\":\\"DatasetReference\\",\\"referenceName\\":\\"DelimitedText2\\"}}],\\"transformations\\":\
[]}}}" --datasets "[{\\"name\\":\\"dataset1\\",\\"properties\\":{\\"type\\":\\"DelimitedText\\",\\"schema\\":[{\\"type\
\\":\\"String\\"}],\\"annotations\\":[],\\"linkedServiceName\\":{\\"type\\":\\"LinkedServiceReference\\",\\"referenceNa\
me\\":\\"linkedService5\\"},\\"typeProperties\\":{\\"columnDelimiter\\":\\",\\",\\"escapeChar\\":\\"\\\\\\\\\\",\\"firs\
tRowAsHeader\\":true,\\"location\\":{\\"type\\":\\"AzureBlobStorageLocation\\",\\"container\\":\\"dataflow-sample-data\
\\",\\"fileName\\":\\"Ansiencoding.csv\\"},\\"quoteChar\\":\\"\\\\\\"\\"}}}]" --debug-settings "{\\"datasetParameters\\\
":{\\"Movies\\":{\\"path\\":\\"abc\\"},\\"Output\\":{\\"time\\":\\"def\\"}},\\"parameters\\":{\\"sourcePath\\":\\"Toy\\\
"},\\"sourceSettings\\":[{\\"rowLimit\\":1000,\\"sourceName\\":\\"source1\\"},{\\"rowLimit\\":222,\\"sourceName\\":\\"s\
ource2\\"}]}" --linked-services "[{\\"name\\":\\"linkedService1\\",\\"properties\\":{\\"type\\":\\"AzureBlobStorage\\",\
\\"annotations\\":[],\\"typeProperties\\":{\\"connectionString\\":\\"DefaultEndpointsProtocol=https;AccountName=<storag\
eName>;EndpointSuffix=core.windows.net;\\",\\"encryptedCredential\\":\\"<credential>\\"}}}]" --session-id "f06ed247-9d0\
7-49b2-b05e-2cb4a2fc871e"
"""

helps['datafactory data-flow-debug-session execute-command'] = """
    type: command
    short-summary: Execute a data flow debug command.
    examples:
      - name: DataFlowDebugSession_ExecuteCommand
        text: |-
               az datafactory data-flow-debug-session execute-command --factory-name "exampleFactoryName" --resource-gr\
oup "exampleResourceGroup" --command "executePreviewQuery" --command-payload row-limits=100 stream-name=source1 --sessi\
on-id "f06ed247-9d07-49b2-b05e-2cb4a2fc871e"
"""

helps['datafactory data-flow-debug-session query-by-factory'] = """
    type: command
    short-summary: Query all active data flow debug sessions.
    examples:
      - name: DataFlowDebugSession_QueryByFactory
        text: |-
               az datafactory data-flow-debug-session query-by-factory --factory-name "exampleFactoryName" --resource-g\
roup "exampleResourceGroup"
"""
