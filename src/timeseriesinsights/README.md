# Azure CLI timeseriesinsights Extension
This is the extension for timeseriesinsights

### How to use
Install this extension using the below CLI command
```
az extension add --name timeseriesinsights
```

### Included Features
#### timeseriesinsights environment
##### Gen1 Create
```
az timeseriesinsights environment gen1 create --name "env1" --location westus --data-retention-time "P31D" --partition-key-properties name="DeviceId1" type="String" --sku name="S1" capacity=1 --resource-group "rg1"
```

##### Gen1 Update
```
az timeseriesinsights environment gen1 update --name "env1" --sku name="S1" capacity=2 --resource-group "rg1" --data-retention-time "P30D" --storage-limit-exceeded-behavior PurgeOldData
```

##### Gen2 Create
```
az timeseriesinsights environment gen2 create --name "env2" --location westus --resource-group "rg1" --sku name="L1" capacity=1 --time-series-id-properties name=idName type=String --storage-configuration account-name=your-account-name  management-key=your-account-key
```

##### Gen2 Update
```
az timeseriesinsights environment gen2 update --name "env2" --resource-group "rg1" --warm-store-configuration data-retention=P30D --storage-configuration account-name=your-account-name management-key=your-account-key
```

##### Show
```
az timeseriesinsights environment show --name "env1" --resource-group "rg1"
```

##### List
```
az timeseriesinsights environment list --resource-group "rg1"
```

##### Delete
```
az timeseriesinsights environment delete --name "env1" --resource-group "rg1"
```
#### timeseriesinsights event-source
##### Event Hub Create
```
az timeseriesinsights event-source eventhub create --environment-name "env1" --name "es1" --location westus --consumer-group-name "cgn" --event-hub-name "ehn" --event-source-resource-id "somePathInArm" --key-name "managementKey" --service-bus-namespace "sbn" --shared-access-key "someSecretvalue" --timestamp-property-name "someTimestampProperty" --resource-group "rg1"
```
##### Iot Hub Create
```
az timeseriesinsights event-source iothub create -g "rg" --environment-name "env1" --name "eventsource" --consumer-group-name "consumer-group" --iot-hub-name "iothub" --key-name "key-name" --shared-access-key "someSecretvalue" --event-source-resource-id "resource-id"
```
##### Event Hub Update
```
az timeseriesinsights event-source iothub update -g "rg" --environment-name "env1" --name "eventsource" --timestamp-property-name timestampProp --shared-access-key "someSecretvalue" --tags test=tag
```
##### Show
```
az timeseriesinsights event-source show --environment-name "env1" --name "es1" --resource-group "rg1"
```
##### List
```
az timeseriesinsights event-source list --environment-name "env1" --resource-group "rg1"
```
##### Delete
```
az timeseriesinsights event-source delete --environment-name "env1" --name "es1" --resource-group "rg1"
```
#### timeseriesinsights reference-data-set
##### Create
```
az timeseriesinsights reference-data-set create --environment-name "env1" --location westus --key-properties name="DeviceId1" type="String" --key-properties name="DeviceFloor" type="Double" --name "rds1" --resource-group "rg1" 
```
##### Show
```
az timeseriesinsights reference-data-set show --environment-name "env1" --name "rds1" --resource-group "rg1"
```
##### List
```
az timeseriesinsights reference-data-set list --environment-name "env1" --resource-group "rg1"
```
##### Update
```
az timeseriesinsights reference-data-set update --environment-name "env1" --name "rds1" --tags someKey="someValue" --resource-group "rg1" 
```
##### Delete
```
az timeseriesinsights reference-data-set delete --environment-name "env1" --name "rds1" --resource-group "rg1"
```
#### timeseriesinsights access-policy
##### Create
```
az timeseriesinsights access-policy create --name "ap1" --environment-name "env1" --description "some description" --principal-object-id "aGuid" --roles "Reader" --resource-group "rg1" 
```
##### Show
```
az timeseriesinsights access-policy show --name "ap1" --environment-name "env1" --resource-group "rg1"
```
##### List
```
az timeseriesinsights access-policy list --environment-name "env1" --resource-group "rg1"
```
##### Update
```
az timeseriesinsights access-policy update --name "ap1" --roles "Reader" --roles "Contributor" --environment-name "env1" --resource-group "rg1" 
```
##### Delete
```
az timeseriesinsights access-policy delete --name "ap1" --environment-name "env1" --resource-group "rg1"
```