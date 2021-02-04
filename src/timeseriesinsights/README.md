# Azure CLI timeseriesinsights Extension
This is the extension for Azure Time Series Insights.

### How to use
Install this extension using the below CLI command:
```
az extension add --name timeseriesinsights
```

### Included Features
#### timeseriesinsights environment
##### Gen1 Create
```
az tsi environment gen1 create --name "env1" --location westus --data-retention-time "P31D" --partition-key-properties name="DeviceId1" type="String" --sku name="S1" capacity=1 --resource-group "rg1"
```

##### Gen1 Update
```
az tsi environment gen1 update --name "env1" --sku name="S1" capacity=2 --resource-group "rg1" --data-retention-time "P30D" --storage-limit-exceeded-behavior PurgeOldData
```

##### Gen2 Create
```
az tsi environment gen2 create --name "env2" --location westus --resource-group "rg1" --sku name="L1" capacity=1 --time-series-id-properties name=idName type=String --storage-configuration account-name=your-account-name  management-key=your-account-key
```

##### Gen2 Update
```
az tsi environment gen2 update --name "env2" --resource-group "rg1" --warm-store-configuration data-retention=P30D --storage-configuration account-name=your-account-name management-key=your-account-key
```

##### Show
```
az tsi environment show --name "env1" --resource-group "rg1"
```

##### List
```
az tsi environment list --resource-group "rg1"
```

##### Delete
```
az tsi environment delete --name "env1" --resource-group "rg1"
```
#### timeseriesinsights event-source
##### Event Hub Create
```sh
ehns={eventhub_namespace}
eh={eventhub_name}
az eventhubs namespace create -g $rg -n $ehns
es_resource_id=$(az eventhubs eventhub create -g $rg -n $eh --namespace-name $ehns --query id --output tsv)
shared_access_key=$(az eventhubs namespace authorization-rule keys list -g $rg --namespace-name $ehns -n RootManageSharedAccessKey --query primaryKey --output tsv)

az tsi event-source eventhub create --environment-name $env --name {es1} --location westus --consumer-group-name "cgn" --event-hub-name $eh --event-source-resource-id $es_resource_id --key-name RootManageSharedAccessKey --service-bus-namespace $ehns --shared-access-key $shared_access_key --timestamp-property-name {someTimestampProperty} --resource-group $rg
```
##### Iot Hub Create
```sh
iothub={iothub_name}
es_resource_id=$(az iot hub create -g $rg -n $iothub --query id --output tsv)
shared_access_key=$(az iot hub policy list -g $rg --hub-name $iothub --query "[?keyName=='iothubowner'].primaryKey" --output tsv)

az tsi event-source iothub create -g $rg --environment-name $env --name {eventsource} --consumer-group-name {consumer-group} --iot-hub-name $iothub --key-name iothubowner --shared-access-key $shared_access_key --event-source-resource-id $es_resource_id
```
##### Event Hub Update
```
az tsi event-source iothub update -g "rg" --environment-name "env1" --name "eventsource" --timestamp-property-name timestampProp --shared-access-key "someSecretvalue" --tags test=tag
```
##### Show
```sh
az tsi event-source show --environment-name "env1" --name "es1" --resource-group "rg1"
```
##### List
```
az tsi event-source list --environment-name "env1" --resource-group "rg1"
```
##### Delete
```
az tsi event-source delete --environment-name "env1" --name "es1" --resource-group "rg1"
```
#### timeseriesinsights reference-data-set
##### Create
```
az tsi reference-data-set create --environment-name "env1" --location westus --key-properties name="DeviceId1" type="String" --key-properties name="DeviceFloor" type="Double" --name "rds1" --resource-group "rg1" 
```
##### Show
```
az tsi reference-data-set show --environment-name "env1" --name "rds1" --resource-group "rg1"
```
##### List
```
az tsi reference-data-set list --environment-name "env1" --resource-group "rg1"
```
##### Update
```
az tsi reference-data-set update --environment-name "env1" --name "rds1" --tags someKey="someValue" --resource-group "rg1" 
```
##### Delete
```
az tsi reference-data-set delete --environment-name "env1" --name "rds1" --resource-group "rg1"
```
#### timeseriesinsights access-policy
##### Create
```
az tsi access-policy create --name "ap1" --environment-name "env1" --description "some description" --principal-object-id "aGuid" --roles "Reader" --resource-group "rg1" 
```
##### Show
```
az tsi access-policy show --name "ap1" --environment-name "env1" --resource-group "rg1"
```
##### List
```
az tsi access-policy list --environment-name "env1" --resource-group "rg1"
```
##### Update
```
az tsi access-policy update --name "ap1" --roles "Reader" --roles "Contributor" --environment-name "env1" --resource-group "rg1" 
```
##### Delete
```
az tsi access-policy delete --name "ap1" --environment-name "env1" --resource-group "rg1"
```
