# Azure CLI Pscloud Extension #

This is an extension to Azure CLI to manage Pure Storage Cloud Azure Native resources.

## How to use ##

For more details about the Pure Storage Cloud resources please visit [documentation on Pure Support](https://support.purestorage.com/bundle/m_azure_native_pure_storage_cloud/page/Pure_Cloud_Block_Store/Azure_Native_Pure_Storage_Cloud/design/c_resources_in_psc.html).

### Install the extension ###

Install this extension using the below CLI command:
```
az extension add --name pscloud --allow-preview
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

### Pure Storage Cloud Resource ###

This resource represents the enablement of the Pure Storage Cloud service within a selected region of the Azure subscription. This resource may be referred to in the documentation as a *Reservation* resource.

#### Create a Pure Storage Cloud Resource ####

To create a Pure Storage Cloud, you need to provide a subscription, resource group, selected location and the company information for billing.

Currently, creating a Pure Storage Cloud resource cannot be initiated from CLI.

#### Show a Pure Storage Cloud Resource ####

```bash
az pscloud show --resource-group {resource_group} --name {reservation_name}
```

#### List Pure Storage Cloud Resources ####

```bash
az pscloud list --resource-group {resource_group}
```

### Storage Pool Resource ###

This resource represents a block storage array instance, delivered as a service, within a specified availability zone and virtual network.

#### Create a Storage Pool ####

To create a Storage Pool, you need to have a virtual network with a delegated subnet to `PureStorage.Block` service.

```bash
az pscloud pool create --resource-group {resource_group} --storage-pool-name {storage_pool_name} --location {location} --availability-zone {availability_zone} --vnet-injection '{{"subnet-id": "{subnet_id}", "vnet-id": "{vnet_id}"}}' --provisioned-bandwidth {bandwidth_mb_per_sec} --reservation-id {reservation_resource_id} --system-assigned --user-assigned {user_assigned_identity_ids} --tags "{key:value}"
```

#### Show a Storage Pool ####

```bash
az pscloud pool show --resource-group {resource_group} --storage-pool-name {storage_pool_name}
```

#### List Storage Pools ####

```bash
az pscloud pool list --resource-group {resource_group}
```

#### Update a Storage Pool ####

```bash
az pscloud pool update --resource-group {resource_group} --name {storage_pool_name} --provisioned-bandwidth {bandwidth_mb_per_sec}
```

#### Delete a Storage Pool ####

```bash
az pscloud pool delete --resource-group {resource_group} --storage-pool-name {storage_pool_name}
```

#### Connect a Storage Pool to AVS ####

Currently, establishing a connection between a Storage Pool and an Azure VMware Solution (AVS) resource must be initiated from the Azure Portal and cannot be initiated from CLI.

#### Get Storage Pool Health Status ####

This command provides the health status about the Storage Pool.

```bash
az pscloud pool get-health-status --resource-group {resource_group} --storage-pool-name {storage_pool_name}
```

#### Get Storage Pool AVS Status ####

This command provides the current connection status between the Storage Pool and Azure VMware Solution (AVS) resource.

```bash
az pscloud pool get-avs-status --resource-group {resource_group} --storage-pool-name {storage_pool_name}
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.