Microsoft Azure CLI 'timeseriesinsights' Extension
==========================================

This package is for the 'timeseriesinsights' extension:

```sh
az timeseriesinsights
```

## Install

```sh
az extension add --name timeseriesinsights
```

## Uninstall

```sh
az extension remove --name timeseriesinsights
```

## Examples

All commands are for Bash. For PowerShell, please set the variables like 

```powershell
$rg='rg1'
```

### Create a resource group for the environments

```sh
rg={resource_group_name}
az group create --name $rg --location westus
```

### Create a standard environment

```sh
env={standard_environment_name}
az timeseriesinsights environment standard create -g $rg --name $env --location westus --sku-name S1 --sku-capacity 1 --data-retention-time P31D --partition-key DeviceId1 --storage-limit-exceeded-behavior PauseIngress
```

### Create a storage account and use it to create a long-term environment

```sh
storage={storage_account_name}
env_lt={longterm_environment_name}

az storage account create -g $rg -n $storage --https-only
key=$(az storage account keys list -g $rg -n $storage --query [0].value --output tsv)

az timeseriesinsights environment longterm create -g $rg --name $env_lt --location westus --sku-name L1 --sku-capacity 1 --data-retention 7 --time-series-id-properties DeviceId1 --storage-account-name $storage --storage-management-key $key
```

### Create an event hub and use it to create an event source

```sh
ehns={eventhub_namespace}
eh={eventhub_name}

az eventhubs namespace create -g $rg -n $ehns
es_resource_id=$(az eventhubs eventhub create -g $rg -n $eh --namespace-name $ehns --query id --output tsv)
shared_access_key=$(az eventhubs namespace authorization-rule keys list -g $rg --namespace-name $ehns -n RootManageSharedAccessKey --query primaryKey --output tsv)

az timeseriesinsights event-source eventhub create -g $rg --environment-name $env --name {es1} --key-name RootManageSharedAccessKey --shared-access-key $shared_access_key --event-source-resource-id $es_resource_id --consumer-group-name '$Default' --timestamp-property-name DeviceId
```

### Create an IoT hub and use it to create an event source

```sh
iothub={iothub_name}
es_resource_id=$(az iot hub create -g $rg -n $iothub --query id --output tsv)
shared_access_key=$(az iot hub policy list -g $rg --hub-name $iothub --query "[?keyName=='iothubowner'].primaryKey" --output tsv)
az timeseriesinsights event-source iothub create -g $rg --environment-name $env --name {es2} --consumer-group-name '$Default' --key-name iothubowner --shared-access-key $shared_access_key --event-source-resource-id $es_resource_id --timestamp-property-name DeviceId
```

### Create a reference data set     

```sh
az timeseriesinsights reference-data-set create -g $rg --environment-name $env --name {rds} --key-properties DeviceId1 String DeviceFloor Double --data-string-comparison-behavior Ordinal
```

### Create an access policy

```sh
az timeseriesinsights access-policy create -g $rg --environment-name $env --name ap1 --principal-object-id 001 --description "some description" --roles Contributor Reader
```

### Delete the environment and all its sub-resources

```sh
az timeseriesinsights environment delete --resource-group $rg --name $env
az group delete -n $rg
```
