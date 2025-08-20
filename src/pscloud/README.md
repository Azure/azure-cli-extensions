# Azure CLI Pscloud Extension #

This is an extension to Azure CLI to manage PureStorage Cloud resources including reservations and storage pools.

## How to use ##

### Install the extension ###

Install this extension using the below CLI command:
```
az extension add --name pscloud
```

### Check the version ###

```
az extension show --name pscloud --query version
```

### Connect to Azure subscription ###

```
az login
az account set -s {subscription_id}
```

### Create a resource group (or use an existing one) ###

```
az group create -n demoResourceGroup -l eastus
```

## Available Commands ##

#### Show a PureStorage Cloud Resource ####

```
az pscloud show --resource-group {resource_group} --name {reservation_name}
```

#### List PureStorage Cloud Resources ####

```
az pscloud list --resource-group {resource_group}
```

#### Create a Storage Pool ####

```
az pscloud pool create --resource-group {resource_group} --storage-pool-name {storage_pool_name} --location {location} --availability-zone {availability_zone} --vnet-injection '{{"subnet-id": "{subnet_id}", "vnet-id": "{vnet_id}"}}' --provisioned-bandwidth {bandwidth_mb_per_sec} --reservation-id {reservation_resource_id} --system-assigned --user-assigned {user_assigned_identity_ids} --tags "{key:value}"
```

#### Show a Storage Pool ####

```
az pscloud pool show --resource-group {resource_group} --storage-pool-name {storage_pool_name}
```

#### List Storage Pools ####

```
az pscloud pool list --resource-group {resource_group}
```

#### Update a Storage Pool ####

```
az pscloud pool update --resource-group {resource_group} --name {storage_pool_name} --provisioned-bandwidth {bandwidth_mb_per_sec}
```

#### Delete a Storage Pool ####

```
az pscloud pool delete --resource-group {resource_group} --storage-pool-name {storage_pool_name}
```

#### Get Storage Pool Health Status ####

```
az pscloud pool get-health-status --resource-group {resource_group} --storage-pool-name {storage_pool_name}
```

#### Get Storage Pool AVS Status ####

```
az pscloud pool get-avs-status --resource-group {resource_group} --storage-pool-name {storage_pool_name}
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.