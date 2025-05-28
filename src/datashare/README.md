# Azure CLI datashare Extension #
This is the extension for datashare

### How to use ###
Install this extension using the below CLI command
```
az extension add --name datashare
```

### Included Features ###
#### datashare account ####
##### Create #####
```
az datashare account create --location "West US 2" --tags tag1="Red" tag2="White" --name "Account1" \
    --resource-group "SampleResourceGroup" 

az datashare account wait --created --name "{myAccount}" --resource-group "{rg}"
```
##### Show #####
```
az datashare account show --name "Account1" --resource-group "SampleResourceGroup"
```
##### List #####
```
az datashare account list --resource-group "SampleResourceGroup"
```
##### Update #####
```
az datashare account update --name "Account1" --tags tag1="Red" tag2="White" --resource-group "SampleResourceGroup"
```
##### Delete #####
```
az datashare account delete --name "Account1" --resource-group "SampleResourceGroup"
```
#### datashare consumer-invitation ####
##### Show #####
```
az datashare consumer-invitation show --invitation-id "dfbbc788-19eb-4607-a5a1-c74181bfff03" --location "East US 2"
```
##### List-invitation #####
```
az datashare consumer-invitation list-invitation
```
##### Reject-invitation #####
```
az datashare consumer-invitation reject-invitation --invitation-id "dfbbc788-19eb-4607-a5a1-c74181bfff03" \
    --location "East US 2" 
```
#### datashare data-set ####
##### Create #####
```
az datashare data-set create --account-name "Account1" \
    --data-set "{\\"kind\\":\\"Blob\\",\\"properties\\":{\\"containerName\\":\\"C1\\",\\"filePath\\":\\"file21\\",\\"resourceGroup\\":\\"SampleResourceGroup\\",\\"storageAccountName\\":\\"storage2\\",\\"subscriptionId\\":\\"433a8dfd-e5d5-4e77-ad86-90acdc75eb1a\\"}}" \
    --name "Dataset1" --resource-group "SampleResourceGroup" --share-name "Share1" 
```
##### Create #####
```
az datashare data-set create --account-name "Account1" \
    --data-set "{\\"kind\\":\\"KustoCluster\\",\\"properties\\":{\\"kustoClusterResourceId\\":\\"/subscriptions/433a8dfd-e5d5-4e77-ad86-90acdc75eb1a/resourceGroups/SampleResourceGroup/providers/Microsoft.Kusto/clusters/Cluster1\\"}}" \
    --name "Dataset1" --resource-group "SampleResourceGroup" --share-name "Share1" 
```
##### Create #####
```
az datashare data-set create --account-name "Account1" \
    --data-set "{\\"kind\\":\\"KustoDatabase\\",\\"properties\\":{\\"kustoDatabaseResourceId\\":\\"/subscriptions/433a8dfd-e5d5-4e77-ad86-90acdc75eb1a/resourceGroups/SampleResourceGroup/providers/Microsoft.Kusto/clusters/Cluster1/databases/Database1\\"}}" \
    --name "Dataset1" --resource-group "SampleResourceGroup" --share-name "Share1" 
```
##### Create #####
```
az datashare data-set create --account-name "Account1" \
    --data-set "{\\"kind\\":\\"KustoTable\\",\\"properties\\":{\\"kustoDatabaseResourceId\\":\\"/subscriptions/433a8dfd-e5d5-4e77-ad86-90acdc75eb1a/resourceGroups/SampleResourceGroup/providers/Microsoft.Kusto/clusters/Cluster1/databases/Database1\\",\\"tableLevelSharingProperties\\":{\\"externalTablesToExclude\\":[\\"test11\\",\\"test12\\"],\\"externalTablesToInclude\\":[\\"test9\\",\\"test10\\"],\\"materializedViewsToExclude\\":[\\"test7\\",\\"test8\\"],\\"materializedViewsToInclude\\":[\\"test5\\",\\"test6\\"],\\"tablesToExclude\\":[\\"test3\\",\\"test4\\"],\\"tablesToInclude\\":[\\"test1\\",\\"test2\\"]}}}" \
    --name "Dataset1" --resource-group "SampleResourceGroup" --share-name "Share1" 
```
##### Create #####
```
az datashare data-set create --account-name "Account1" \
    --data-set "{\\"kind\\":\\"SqlDBTable\\",\\"properties\\":{\\"databaseName\\":\\"SqlDB1\\",\\"schemaName\\":\\"dbo\\",\\"sqlServerResourceId\\":\\"/subscriptions/433a8dfd-e5d5-4e77-ad86-90acdc75eb1a/resourceGroups/SampleResourceGroup/providers/Microsoft.Sql/servers/Server1\\",\\"tableName\\":\\"Table1\\"}}" \
    --name "Dataset1" --resource-group "SampleResourceGroup" --share-name "Share1" 
```
##### Create #####
```
az datashare data-set create --account-name "Account1" \
    --data-set "{\\"kind\\":\\"SqlDWTable\\",\\"properties\\":{\\"dataWarehouseName\\":\\"DataWarehouse1\\",\\"schemaName\\":\\"dbo\\",\\"sqlServerResourceId\\":\\"/subscriptions/433a8dfd-e5d5-4e77-ad86-90acdc75eb1a/resourceGroups/SampleResourceGroup/providers/Microsoft.Sql/servers/Server1\\",\\"tableName\\":\\"Table1\\"}}" \
    --name "Dataset1" --resource-group "SampleResourceGroup" --share-name "Share1" 
```
##### Create #####
```
az datashare data-set create --account-name "sourceAccount" \
    --data-set "{\\"kind\\":\\"SynapseWorkspaceSqlPoolTable\\",\\"properties\\":{\\"synapseWorkspaceSqlPoolTableResourceId\\":\\"/subscriptions/0f3dcfc3-18f8-4099-b381-8353e19d43a7/resourceGroups/SampleResourceGroup/providers/Microsoft.Synapse/workspaces/ExampleWorkspace/sqlPools/ExampleSqlPool/schemas/dbo/tables/table1\\"}}" \
    --name "dataset1" --resource-group "SampleResourceGroup" --share-name "share1" 
```
##### Show #####
```
az datashare data-set show --account-name "Account1" --name "Dataset1" --resource-group "SampleResourceGroup" \
    --share-name "Share1" 
```
##### List #####
```
az datashare data-set list --account-name "Account1" --resource-group "SampleResourceGroup" --share-name "Share1"
```
##### Delete #####
```
az datashare data-set delete --account-name "Account1" --name "Dataset1" --resource-group "SampleResourceGroup" \
    --share-name "Share1" 
```
#### datashare data-set-mapping ####
##### Create #####
```
az datashare data-set-mapping create --account-name "Account1" \
    --adls-gen2-file-data-set-mapping data-set-id="a08f184b-0567-4b11-ba22-a1199336d226" file-path="file21" file-system="fileSystem" output-type="Csv" resource-group="SampleResourceGroup" storage-account-name="storage2" subscription-id="433a8dfd-e5d5-4e77-ad86-90acdc75eb1a" \
    --name "DatasetMapping1" --resource-group "SampleResourceGroup" --share-subscription-name "ShareSubscription1" 
```
##### Show #####
```
az datashare data-set-mapping show --account-name "Account1" --name "DatasetMapping1" \
    --resource-group "SampleResourceGroup" --share-subscription-name "ShareSubscription1" 
```
##### List #####
```
az datashare data-set-mapping list --account-name "Account1" --resource-group "SampleResourceGroup" \
    --share-subscription-name "ShareSubscription1" 
```
##### Delete #####
```
az datashare data-set-mapping delete --account-name "Account1" --name "DatasetMapping1" \
    --resource-group "SampleResourceGroup" --share-subscription-name "ShareSubscription1" 
```
#### datashare email-registration ####
##### Activate-email #####
```
az datashare email-registration activate-email --activation-code "djsfhakj2lekowd3wepfklpwe9lpflcd" \
    --location "East US 2" 
```
##### Register-email #####
```
az datashare email-registration register-email --location "East US 2"
```
#### datashare invitation ####
##### Create #####
```
az datashare invitation create --account-name "Account1" --expiration-date "2020-08-26T22:33:24.5785265Z" \
    --target-email "receiver@microsoft.com" --name "Invitation1" --resource-group "SampleResourceGroup" \
    --share-name "Share1" 
```
##### Show #####
```
az datashare invitation show --account-name "Account1" --name "Invitation1" --resource-group "SampleResourceGroup" \
    --share-name "Share1" 
```
##### List #####
```
az datashare invitation list --account-name "Account1" --resource-group "SampleResourceGroup" --share-name "Share1"
```
##### Delete #####
```
az datashare invitation delete --account-name "Account1" --name "Invitation1" --resource-group "SampleResourceGroup" \
    --share-name "Share1" 
```
#### datashare ####
##### Create #####
```
az datashare create --account-name "Account1" --resource-group "SampleResourceGroup" --description "share description" \
    --share-kind "CopyBased" --terms "Confidential" --name "Share1" 
```
##### Show #####
```
az datashare show --account-name "Account1" --resource-group "SampleResourceGroup" --name "Share1"
```
##### List #####
```
az datashare list --account-name "Account1" --resource-group "SampleResourceGroup"
```
##### List-synchronization #####
```
az datashare list-synchronization --account-name "Account1" --resource-group "SampleResourceGroup" --name "Share1"
```
##### List-synchronization-detail #####
```
az datashare list-synchronization-detail --account-name "Account1" --resource-group "SampleResourceGroup" \
    --name "Share1" --synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb" 
```
##### Delete #####
```
az datashare delete --account-name "Account1" --resource-group "SampleResourceGroup" --name "Share1"
```
#### datashare provider-share-subscription ####
##### List #####
```
az datashare provider-share-subscription list --account-name "Account1" --resource-group "SampleResourceGroup" \
    --share-name "Share1" 
```
##### Show #####
```
az datashare provider-share-subscription show --account-name "Account1" \
    --provider-share-subscription-id "4256e2cf-0f82-4865-961b-12f83333f487" --resource-group "SampleResourceGroup" \
    --share-name "Share1" 
```
##### Adjust #####
```
az datashare provider-share-subscription adjust --account-name "Account1" \
    --expiration-date "2020-12-26T22:33:24.5785265Z" \
    --provider-share-subscription-id "4256e2cf-0f82-4865-961b-12f83333f487" --resource-group "SampleResourceGroup" \
    --share-name "Share1" 
```
##### Reinstate #####
```
az datashare provider-share-subscription reinstate --account-name "Account1" \
    --expiration-date "2020-12-26T22:33:24.5785265Z" \
    --provider-share-subscription-id "4256e2cf-0f82-4865-961b-12f83333f487" --resource-group "SampleResourceGroup" \
    --share-name "Share1" 
```
##### Revoke #####
```
az datashare provider-share-subscription revoke --account-name "Account1" \
    --provider-share-subscription-id "4256e2cf-0f82-4865-961b-12f83333f487" --resource-group "SampleResourceGroup" \
    --share-name "Share1" 
```
#### datashare share-subscription ####
##### Create #####
```
az datashare share-subscription create --account-name "Account1" --resource-group "SampleResourceGroup" \
    --expiration-date "2020-08-26T22:33:24.5785265Z" --invitation-id "12345678-1234-1234-12345678abd" \
    --source-share-location "eastus2" --name "ShareSubscription1" 
```
##### Show #####
```
az datashare share-subscription show --account-name "Account1" --resource-group "SampleResourceGroup" \
    --name "ShareSubscription1" 
```
##### List #####
```
az datashare share-subscription list --account-name "Account1" --resource-group "SampleResourceGroup"
```
##### Cancel-synchronization #####
```
az datashare share-subscription cancel-synchronization --account-name "Account1" \
    --resource-group "SampleResourceGroup" --name "ShareSubscription1" \
    --synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb" 
```
##### List-source-share-synchronization-setting #####
```
az datashare share-subscription list-source-share-synchronization-setting --account-name "Account1" \
    --resource-group "SampleResourceGroup" --name "ShareSub1" 
```
##### List-synchronization #####
```
az datashare share-subscription list-synchronization --account-name "Account1" --resource-group "SampleResourceGroup" \
    --name "ShareSub1" 
```
##### List-synchronization-detail #####
```
az datashare share-subscription list-synchronization-detail --account-name "Account1" \
    --resource-group "SampleResourceGroup" --name "ShareSub1" \
    --synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb" 
```
##### Synchronize #####
```
az datashare share-subscription synchronize --account-name "Account1" --resource-group "SampleResourceGroup" \
    --name "ShareSubscription1" --synchronization-mode "Incremental" 
```
##### Delete #####
```
az datashare share-subscription delete --account-name "Account1" --resource-group "SampleResourceGroup" \
    --name "ShareSubscription1" 
```
#### datashare consumer-source-data-set ####
##### List #####
```
az datashare consumer-source-data-set list --account-name "Account1" --resource-group "SampleResourceGroup" \
    --share-subscription-name "Share1" 
```
#### datashare synchronization-setting ####
##### Create #####
```
az datashare synchronization-setting create --account-name "Account1" --resource-group "SampleResourceGroup" \
    --share-name "Share1" \
    --scheduled-synchronization-setting recurrence-interval="Day" synchronization-time="2018-11-14T04:47:52.9614956Z" \
    --name "Dataset1" 
```
##### Show #####
```
az datashare synchronization-setting show --account-name "Account1" --resource-group "SampleResourceGroup" \
    --share-name "Share1" --name "SynchronizationSetting1" 
```
##### List #####
```
az datashare synchronization-setting list --account-name "Account1" --resource-group "SampleResourceGroup" \
    --share-name "Share1" 
```
##### Delete #####
```
az datashare synchronization-setting delete --account-name "Account1" --resource-group "SampleResourceGroup" \
    --share-name "Share1" --name "SynchronizationSetting1" 
```
#### datashare trigger ####
##### Create #####
```
az datashare trigger create --account-name "Account1" --resource-group "SampleResourceGroup" \
    --share-subscription-name "ShareSubscription1" \
    --scheduled-trigger recurrence-interval="Day" synchronization-mode="Incremental" synchronization-time="2018-11-14T04:47:52.9614956Z" \
    --name "Trigger1" 
```
##### Show #####
```
az datashare trigger show --account-name "Account1" --resource-group "SampleResourceGroup" \
    --share-subscription-name "ShareSubscription1" --name "Trigger1" 
```
##### List #####
```
az datashare trigger list --account-name "Account1" --resource-group "SampleResourceGroup" \
    --share-subscription-name "ShareSubscription1" 
```
##### Delete #####
```
az datashare trigger delete --account-name "Account1" --resource-group "SampleResourceGroup" \
    --share-subscription-name "ShareSubscription1" --name "Trigger1" 
```