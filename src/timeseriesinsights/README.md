# Azure CLI timeseriesinsights Extension #
This is the extension for timeseriesinsights

### How to use ###
Install this extension using the below CLI command
```
az extension add --name timeseriesinsights
```

### Included Features ###
#### timeseriesinsights environment ####
##### Create #####
```
az timeseriesinsights environment create --name "env1" \
    --parameters "{\\"kind\\":\\"Gen1\\",\\"location\\":\\"West US\\",\\"properties\\":{\\"dataRetentionTime\\":\\"P31D\\",\\"partitionKeyProperties\\":[{\\"name\\":\\"DeviceId1\\",\\"type\\":\\"String\\"}]},\\"sku\\":{\\"name\\":\\"S1\\",\\"capacity\\":1}}" \
    --resource-group "rg1" 
```
##### Show #####
```
az timeseriesinsights environment show --name "env1" --resource-group "rg1"
```
##### List #####
```
az timeseriesinsights environment list --resource-group "rg1"
```
##### Update #####
```
az timeseriesinsights environment update --name "env1" --tags someTag="someTagValue" --resource-group "rg1"
```
##### Delete #####
```
az timeseriesinsights environment delete --name "env1" --resource-group "rg1"
```
#### timeseriesinsights event-source ####
##### Create #####
```
az timeseriesinsights event-source create --environment-name "env1" --name "es1" \
    --event-hub-event-source-create-or-update-parameters location="West US" timestamp-property-name="someTimestampProperty" event-source-resource-id="somePathInArm" service-bus-namespace="sbn" event-hub-name="ehn" consumer-group-name="cgn" key-name="managementKey" shared-access-key="someSecretvalue" \
    --resource-group "rg1" 
```
##### Show #####
```
az timeseriesinsights event-source show --environment-name "env1" --name "es1" --resource-group "rg1"
```
##### List #####
```
az timeseriesinsights event-source list --environment-name "env1" --resource-group "rg1"
```
##### Update #####
```
az timeseriesinsights event-source update --environment-name "env1" --name "es1" --tags someKey="someValue" \
    --resource-group "rg1" 
```
##### Delete #####
```
az timeseriesinsights event-source delete --environment-name "env1" --name "es1" --resource-group "rg1"
```
#### timeseriesinsights reference-data-set ####
##### Create #####
```
az timeseriesinsights reference-data-set create --environment-name "env1" --location "West US" \
    --key-properties name="DeviceId1" type="String" --key-properties name="DeviceFloor" type="Double" --name "rds1" \
    --resource-group "rg1" 
```
##### Show #####
```
az timeseriesinsights reference-data-set show --environment-name "env1" --name "rds1" --resource-group "rg1"
```
##### List #####
```
az timeseriesinsights reference-data-set list --environment-name "env1" --resource-group "rg1"
```
##### Update #####
```
az timeseriesinsights reference-data-set update --environment-name "env1" --name "rds1" --tags someKey="someValue" \
    --resource-group "rg1" 
```
##### Delete #####
```
az timeseriesinsights reference-data-set delete --environment-name "env1" --name "rds1" --resource-group "rg1"
```
#### timeseriesinsights access-policy ####
##### Create #####
```
az timeseriesinsights access-policy create --name "ap1" --environment-name "env1" --description "some description" \
    --principal-object-id "aGuid" --roles "Reader" --resource-group "rg1" 
```
##### Show #####
```
az timeseriesinsights access-policy show --name "ap1" --environment-name "env1" --resource-group "rg1"
```
##### List #####
```
az timeseriesinsights access-policy list --environment-name "env1" --resource-group "rg1"
```
##### Update #####
```
az timeseriesinsights access-policy update --name "ap1" --roles "Reader" --roles "Contributor" \
    --environment-name "env1" --resource-group "rg1" 
```
##### Delete #####
```
az timeseriesinsights access-policy delete --name "ap1" --environment-name "env1" --resource-group "rg1"
```