# Azure CLI loganalytics Extension #
This is the extension for loganalytics

### How to use ###
Install this extension using the below CLI command
```
az extension add --name loganalytics
```

### Included Features ###
#### loganalytics dataexport ####
##### Create #####
```
az loganalytics dataexport create --name "export1" \
    --resource-id "/subscriptions/192b9f85-a39a-4276-b96d-d5cd351703f9/resourceGroups/OIAutoRest1234/providers/Microsoft.EventHub/namespaces/test" \
    --table-names "Heartbeat" --resource-group "RgTest1" --workspace-name "DeWnTest1234" 
```
##### Show #####
```
az loganalytics dataexport show --name "export1" --resource-group "RgTest1" --workspace-name "DeWnTest1234"
```
##### List #####
```
az loganalytics dataexport list --resource-group "RgTest1" --workspace-name "DeWnTest1234"
```
##### Delete #####
```
az loganalytics dataexport delete --name "export1" --resource-group "RgTest1" --workspace-name "DeWnTest1234"
```
#### loganalytics datasource ####
##### Create #####
```
az loganalytics datasource create --name "AzTestDS774" --kind "AzureActivityLog" \
    --properties "{\\"LinkedResourceId\\":\\"/subscriptions/00000000-0000-0000-0000-00000000000/providers/microsoft.insights/eventtypes/management\\"}" \
    --resource-group "OIAutoRest5123" --workspace-name "AzTest9724" 
```
##### Show #####
```
az loganalytics datasource show --name "AzTestDS774" --resource-group "OIAutoRest5123" --workspace-name "AzTest9724"
```
##### List #####
```
az loganalytics datasource list --filter "kind=\'WindowsEvent\'" --resource-group "OIAutoRest5123" \
    --workspace-name "AzTest9724" 
```
##### Delete #####
```
az loganalytics datasource delete --name "AzTestDS774" --resource-group "OIAutoRest5123" --workspace-name "AzTest9724"
```
#### loganalytics intelligencepack ####
##### List #####
```
az loganalytics intelligencepack list --resource-group "rg1" --workspace-name "TestLinkWS"
```
##### Disable #####
```
az loganalytics intelligencepack disable --name "ChangeTracking" --resource-group "rg1" --workspace-name "TestLinkWS"
```
##### Enable #####
```
az loganalytics intelligencepack enable --name "ChangeTracking" --resource-group "rg1" --workspace-name "TestLinkWS"
```
#### loganalytics linkedservice ####
##### Create #####
```
az loganalytics linkedservice create --name "Cluster" \
    --write-access-resource-id "/subscriptions/00000000-0000-0000-0000-00000000000/resourceGroups/mms-eus/providers/Microsoft.OperationalInsights/clusters/testcluster" \
    --resource-group "mms-eus" --workspace-name "TestLinkWS" 

az loganalytics linkedservice wait --created --name "{myLinkedService}" --resource-group "{rg_5}" \
    --workspace-name "{myWorkspace3}" 
```
##### Show #####
```
az loganalytics linkedservice show --name "Cluster" --resource-group "mms-eus" --workspace-name "TestLinkWS"
```
##### List #####
```
az loganalytics linkedservice list --resource-group "mms-eus" --workspace-name "TestLinkWS"
```
##### Delete #####
```
az loganalytics linkedservice delete --name "Cluster" --resource-group "rg1" --workspace-name "TestLinkWS"
```
#### loganalytics linkedstorageaccount ####
##### Create #####
```
az loganalytics linkedstorageaccount create --data-source-type "CustomLogs" \
    --storage-account-ids "/subscriptions/00000000-0000-0000-0000-00000000000/resourceGroups/mms-eus/providers/Microsoft.Storage/storageAccounts/testStorageA" "/subscriptions/00000000-0000-0000-0000-00000000000/resourceGroups/mms-eus/providers/Microsoft.Storage/storageAccounts/testStorageB" \
    --resource-group "mms-eus" --workspace-name "testLinkStorageAccountsWS" 
```
##### Show #####
```
az loganalytics linkedstorageaccount show --data-source-type "CustomLogs" --resource-group "mms-eus" \
    --workspace-name "testLinkStorageAccountsWS" 
```
##### List #####
```
az loganalytics linkedstorageaccount list --resource-group "mms-eus" --workspace-name "testLinkStorageAccountsWS"
```
##### Delete #####
```
az loganalytics linkedstorageaccount delete --data-source-type "CustomLogs" --resource-group "mms-eus" \
    --workspace-name "testLinkStorageAccountsWS" 
```
#### loganalytics managementgroup ####
##### List #####
```
az loganalytics managementgroup list --resource-group "rg1" --workspace-name "TestLinkWS"
```
#### loganalytics operationstatuses ####
##### Show #####
```
az loganalytics operationstatuses show --async-operation-id "713192d7-503f-477a-9cfe-4efc3ee2bd11" --location "West US"
```
#### loganalytics sharedkey ####
##### Get-shared-key #####
```
az loganalytics sharedkey get-shared-key --resource-group "rg1" --workspace-name "TestLinkWS"
```
##### Regenerate #####
```
az loganalytics sharedkey regenerate --resource-group "rg1" --workspace-name "workspace1"
```
#### loganalytics usage ####
##### List #####
```
az loganalytics usage list --resource-group "rg1" --workspace-name "TestLinkWS"
```
#### loganalytics storageinsightconfig ####
##### Create #####
```
az loganalytics storageinsightconfig create --containers "wad-iis-logfiles" \
    --storage-account id="/subscriptions/00000000-0000-0000-0000-000000000005/resourcegroups/OIAutoRest6987/providers/microsoft.storage/storageaccounts/AzTestFakeSA9945" key="1234" \
    --tables "WADWindowsEventLogsTable" "LinuxSyslogVer2v0" --resource-group "OIAutoRest5123" \
    --storage-insight-name "AzTestSI1110" --workspace-name "aztest5048" 
```
##### Show #####
```
az loganalytics storageinsightconfig show --resource-group "OIAutoRest5123" --storage-insight-name "AzTestSI1110" \
    --workspace-name "aztest5048" 
```
##### List #####
```
az loganalytics storageinsightconfig list --resource-group "OIAutoRest5123" --workspace-name "aztest5048"
```
##### Delete #####
```
az loganalytics storageinsightconfig delete --resource-group "OIAutoRest5123" --storage-insight-name "AzTestSI1110" \
    --workspace-name "aztest5048" 
```
#### loganalytics savedsearch ####
##### Create #####
```
az loganalytics savedsearch create --category "Saved Search Test Category" \
    --display-name "Create or Update Saved Search Test" --function-alias "heartbeat_func" \
    --function-parameters "a:int=1" --input-query "Heartbeat | summarize Count() by Computer | take a" \
    --tags name="Group" value="Computer" --version 2 --resource-group "TestRG" \
    --saved-search-id "00000000-0000-0000-0000-00000000000" --workspace-name "TestWS" 
```
##### Show #####
```
az loganalytics savedsearch show --resource-group "TestRG" --saved-search-id "00000000-0000-0000-0000-00000000000" \
    --workspace-name "TestWS" 
```
##### List #####
```
az loganalytics savedsearch list --resource-group "TestRG" --workspace-name "TestWS"
```
##### Delete #####
```
az loganalytics savedsearch delete --resource-group "TestRG" --saved-search-id "00000000-0000-0000-0000-00000000000" \
    --workspace-name "TestWS" 
```
#### loganalytics availableservicetier ####
##### List #####
```
az loganalytics availableservicetier list --resource-group "rg1" --workspace-name "workspace1"
```
#### loganalytics gateway ####
##### Delete #####
```
az loganalytics gateway delete --gateway-id "00000000-0000-0000-0000-00000000000" --resource-group "OIAutoRest5123" \
    --workspace-name "aztest5048" 
```
#### loganalytics schema ####
##### Get #####
```
az loganalytics schema get --resource-group "mms-eus" --workspace-name "atlantisdemo"
```
#### loganalytics workspacepurge ####
##### Purge #####
```
az loganalytics workspacepurge purge \
    --filters "[{\\"column\\":\\"TimeGenerated\\",\\"operator\\":\\">\\",\\"value\\":\\"2017-09-01T00:00:00\\"}]" \
    --table "Heartbeat" --resource-group "OIAutoRest5123" --workspace-name "aztest5048" 
```
##### Show-purge-status #####
```
az loganalytics workspacepurge show-purge-status --purge-id "purge-970318e7-b859-4edb-8903-83b1b54d0b74" \
    --resource-group "OIAutoRest5123" --workspace-name "aztest5048" 
```
#### loganalytics cluster ####
##### Create #####
```
az loganalytics cluster create --name "oiautorest6685" --location "australiasoutheast" \
    --sku name="CapacityReservation" capacity=1000 --tags tag1="val1" --resource-group "oiautorest6685" 

az loganalytics cluster wait --created --name "{myCluster2}" --resource-group "{rg_8}"
```
##### Show #####
```
az loganalytics cluster show --name "oiautorest6685" --resource-group "oiautorest6685"
```
##### List #####
```
az loganalytics cluster list --resource-group "oiautorest6685"
```
##### Update #####
```
az loganalytics cluster update --name "oiautorest6685" --type "UserAssigned" \
    --user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-00000000000/resourcegroups/oiautorest6685/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myidentity\\":{}}" \
    --key-vault-properties key-name="aztest2170cert" key-rsa-size=1024 key-vault-uri="https://aztest2170.vault.azure.net" key-version="654ft6c4e63845cbb50fd6fg51540429" \
    --sku name="CapacityReservation" capacity=1000 --tags tag1="val1" --resource-group "oiautorest6685" 
```
##### Delete #####
```
az loganalytics cluster delete --name "oiautorest6685" --resource-group "oiautorest6685"
```
#### loganalytics table ####
##### List #####
```
az loganalytics table list --resource-group "oiautorest6685" --workspace-name "oiautorest6685"
```
##### Show #####
```
az loganalytics table show --resource-group "oiautorest6685" --name "table1" --workspace-name "oiautorest6685"
```
##### Update #####
```
az loganalytics table update --is-troubleshoot-enabled true --retention-in-days 40 --resource-group "oiautorest6685" \
    --name "table1" --workspace-name "oiautorest6685" 
```
#### loganalytics workspace ####
##### Create #####
```
az loganalytics workspace create --location "australiasoutheast" --retention-in-days 30 --sku name="PerGB2018" \
    --tags tag1="val1" --resource-group "oiautorest6685" --name "oiautorest6685" 

az loganalytics workspace wait --created --resource-group "{rg_8}" --name "{myWorkspace9}"
```
##### Show #####
```
az loganalytics workspace show --resource-group "oiautorest6685" --name "oiautorest6685"
```
##### List #####
```
az loganalytics workspace list --resource-group "oiautorest6685"
```
##### Update #####
```
az loganalytics workspace update --retention-in-days 30 --sku name="PerGB2018" --daily-quota-gb -1 \
    --resource-group "oiautorest6685" --name "oiautorest6685" 
```
##### Delete #####
```
az loganalytics workspace delete --resource-group "oiautorest6685" --name "oiautorest6685"
```
#### loganalytics deletedworkspace ####
##### List #####
```
az loganalytics deletedworkspace list --resource-group "oiautorest6685"
```