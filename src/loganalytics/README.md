# Azure CLI loganalytics Extension #
This is the extension for loganalytics

### How to use ###
Install this extension using the below CLI command
```
az extension add --name loganalytics
```

### Included Features ###
#### loganalytics data-export ####
##### Create #####
```
az loganalytics data-export create --name "export1" \
    --resource-id "/subscriptions/192b9f85-a39a-4276-b96d-d5cd351703f9/resourceGroups/OIAutoRest1234/providers/Microsoft.EventHub/namespaces/test" \
    --table-names "Heartbeat" --resource-group "RgTest1" --workspace-name "DeWnTest1234" 
```
##### Show #####
```
az loganalytics data-export show --name "export1" --resource-group "RgTest1" --workspace-name "DeWnTest1234"
```
##### List #####
```
az loganalytics data-export list --resource-group "RgTest1" --workspace-name "DeWnTest1234"
```
##### Delete #####
```
az loganalytics data-export delete --name "export1" --resource-group "RgTest1" --workspace-name "DeWnTest1234"
```
#### loganalytics data-source ####
##### Create #####
```
az loganalytics data-source create --name "AzTestDS774" --kind "AzureActivityLog" \
    --properties "{\\"LinkedResourceId\\":\\"/subscriptions/00000000-0000-0000-0000-00000000000/providers/microsoft.insights/eventtypes/management\\"}" \
    --resource-group "OIAutoRest5123" --workspace-name "AzTest9724" 
```
##### Show #####
```
az loganalytics data-source show --name "AzTestDS774" --resource-group "OIAutoRest5123" --workspace-name "AzTest9724"
```
##### List #####
```
az loganalytics data-source list --filter "kind=\'WindowsEvent\'" --resource-group "OIAutoRest5123" \
    --workspace-name "AzTest9724" 
```
##### Delete #####
```
az loganalytics data-source delete --name "AzTestDS774" --resource-group "OIAutoRest5123" --workspace-name "AzTest9724"
```
#### loganalytics intelligence-pack ####
##### List #####
```
az loganalytics intelligence-pack list --resource-group "rg1" --workspace-name "TestLinkWS"
```
##### Disable #####
```
az loganalytics intelligence-pack disable --name "ChangeTracking" --resource-group "rg1" --workspace-name "TestLinkWS"
```
##### Enable #####
```
az loganalytics intelligence-pack enable --name "ChangeTracking" --resource-group "rg1" --workspace-name "TestLinkWS"
```
#### loganalytics linked-service ####
##### Create #####
```
az loganalytics linked-service create --name "Cluster" \
    --write-access-resource-id "/subscriptions/00000000-0000-0000-0000-00000000000/resourceGroups/mms-eus/providers/Microsoft.OperationalInsights/clusters/testcluster" \
    --resource-group "mms-eus" --workspace-name "TestLinkWS" 

az loganalytics linked-service wait --created --name "{myLinkedService}" --resource-group "{rg_5}"
```
##### Show #####
```
az loganalytics linked-service show --name "Cluster" --resource-group "mms-eus" --workspace-name "TestLinkWS"
```
##### List #####
```
az loganalytics linked-service list --resource-group "mms-eus" --workspace-name "TestLinkWS"
```
##### Delete #####
```
az loganalytics linked-service delete --name "Cluster" --resource-group "rg1" --workspace-name "TestLinkWS"
```
#### loganalytics linked-storage-account ####
##### Create #####
```
az loganalytics linked-storage-account create --data-source-type "CustomLogs" \
    --storage-account-ids "/subscriptions/00000000-0000-0000-0000-00000000000/resourceGroups/mms-eus/providers/Microsoft.Storage/storageAccounts/testStorageA" "/subscriptions/00000000-0000-0000-0000-00000000000/resourceGroups/mms-eus/providers/Microsoft.Storage/storageAccounts/testStorageB" \
    --resource-group "mms-eus" --workspace-name "testLinkStorageAccountsWS" 
```
##### Show #####
```
az loganalytics linked-storage-account show --data-source-type "CustomLogs" --resource-group "mms-eus" \
    --workspace-name "testLinkStorageAccountsWS" 
```
##### List #####
```
az loganalytics linked-storage-account list --resource-group "mms-eus" --workspace-name "testLinkStorageAccountsWS"
```
##### Delete #####
```
az loganalytics linked-storage-account delete --data-source-type "CustomLogs" --resource-group "mms-eus" \
    --workspace-name "testLinkStorageAccountsWS" 
```
#### loganalytics management-group ####
##### List #####
```
az loganalytics management-group list --resource-group "rg1" --workspace-name "TestLinkWS"
```
#### loganalytics operation-statuses ####
##### Show #####
```
az loganalytics operation-statuses show --async-operation-id "713192d7-503f-477a-9cfe-4efc3ee2bd11" \
    --location "West US" 
```
#### loganalytics shared-key ####
##### Get-shared-key #####
```
az loganalytics shared-key get-shared-key --resource-group "rg1" --workspace-name "TestLinkWS"
```
##### Regenerate #####
```
az loganalytics shared-key regenerate --resource-group "rg1" --workspace-name "workspace1"
```
#### loganalytics usage ####
##### List #####
```
az loganalytics usage list --resource-group "rg1" --workspace-name "TestLinkWS"
```
#### loganalytics storage-insight-config ####
##### Create #####
```
az loganalytics storage-insight-config create --containers "wad-iis-logfiles" \
    --storage-account id="/subscriptions/00000000-0000-0000-0000-000000000005/resourcegroups/OIAutoRest6987/providers/microsoft.storage/storageaccounts/AzTestFakeSA9945" key="1234" \
    --tables "WADWindowsEventLogsTable" "LinuxSyslogVer2v0" --resource-group "OIAutoRest5123" \
    --storage-insight-name "AzTestSI1110" --workspace-name "aztest5048" 
```
##### Show #####
```
az loganalytics storage-insight-config show --resource-group "OIAutoRest5123" --storage-insight-name "AzTestSI1110" \
    --workspace-name "aztest5048" 
```
##### List #####
```
az loganalytics storage-insight-config list --resource-group "OIAutoRest5123" --workspace-name "aztest5048"
```
##### Delete #####
```
az loganalytics storage-insight-config delete --resource-group "OIAutoRest5123" --storage-insight-name "AzTestSI1110" \
    --workspace-name "aztest5048" 
```
#### loganalytics saved-search ####
##### Create #####
```
az loganalytics saved-search create --category "Saved Search Test Category" \
    --display-name "Create or Update Saved Search Test" --function-alias "heartbeat_func" \
    --function-parameters "a:int=1" --query "Heartbeat | summarize Count() by Computer | take a" \
    --tags name="Group" value="Computer" --version 2 --resource-group "TestRG" \
    --saved-search-id "00000000-0000-0000-0000-00000000000" --workspace-name "TestWS" 
```
##### Show #####
```
az loganalytics saved-search show --resource-group "TestRG" --saved-search-id "00000000-0000-0000-0000-00000000000" \
    --workspace-name "TestWS" 
```
##### List #####
```
az loganalytics saved-search list --resource-group "TestRG" --workspace-name "TestWS"
```
##### Delete #####
```
az loganalytics saved-search delete --resource-group "TestRG" --saved-search-id "00000000-0000-0000-0000-00000000000" \
    --workspace-name "TestWS" 
```
#### loganalytics available-service-tier ####
##### List #####
```
az loganalytics available-service-tier list --resource-group "rg1" --workspace-name "workspace1"
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
#### loganalytics workspace-purge ####
##### Purge #####
```
az loganalytics workspace-purge purge \
    --filters "[{\\"column\\":\\"TimeGenerated\\",\\"operator\\":\\">\\",\\"value\\":\\"2017-09-01T00:00:00\\"}]" \
    --table "Heartbeat" --resource-group "OIAutoRest5123" --workspace-name "aztest5048" 
```
##### Show-purge-status #####
```
az loganalytics workspace-purge show-purge-status --purge-id "purge-970318e7-b859-4edb-8903-83b1b54d0b74" \
    --resource-group "OIAutoRest5123" --workspace-name "aztest5048" 
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
az loganalytics table update --retention-in-days 30 --resource-group "oiautorest6685" --name "table1" \
    --workspace-name "oiautorest6685" 
```
#### loganalytics cluster ####
##### Create #####
```
az loganalytics cluster create --name "oiautorest6685" --location "australiasoutheast" \
    --sku name="CapacityReservation" capacity=1000 --tags tag1="val1" --resource-group "oiautorest6685" 

az loganalytics cluster wait --created --name "{rg_8}" --resource-group "{rg_8}"
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
#### loganalytics workspace ####
##### Create #####
```
az loganalytics workspace create --location "australiasoutheast" --retention-in-days 30 --sku name="PerGB2018" \
    --tags tag1="val1" --resource-group "oiautorest6685" --name "oiautorest6685" 

az loganalytics workspace wait --created --resource-group "{rg_8}" --name "{rg_8}"
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
#### loganalytics deleted-workspace ####
##### List #####
```
az loganalytics deleted-workspace list --resource-group "oiautorest6685"
```