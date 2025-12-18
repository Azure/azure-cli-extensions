# Azure CLI Pscloud Extension #

This is an extension to Azure CLI to manage Pure Storage Cloud Azure Native resources.

## Recent Improvements ##

The pscloud CLI has been recently improved for better usability and consistency:

### Enhanced Parameter Usability ###
- **Simplified zone specification**: Use `--zone` or `-z` instead of `--availability-zone`
- **Flattened network parameters**: Use `--subnet-id` and `--vnet-id` directly instead of complex `--vnet-injection` JSON objects
- **Improved parameter names**: Consistent use of `--name` or `-n` across all commands

### Removed Unsupported Features ###
- **Identity parameters removed**: `--system-assigned`, `--user-assigned`, and related identity options have been removed as they are not supported by the Pure Storage Cloud service
- **Wait command removed**: `az pscloud pool wait` has been removed for consistency with other Azure CLI extensions

### Enhanced Validation ###
- **Required parameters**: Key parameters like `--zone`, `--provisioned-bandwidth`, `--reservation-id`, `--subnet-id`, and `--vnet-id` are now properly validated as required
- **Better examples**: All command examples now show realistic Azure resource IDs and cleaner syntax

## How to use ##

For more details about the Pure Storage Cloud resources please visit [documentation on Pure Support](https://support.purestorage.com/bundle/m_azure_native_pure_storage_cloud/page/Pure_Cloud_Block_Store/Azure_Native_Pure_Storage_Cloud/design/c_resources_in_psc.html).

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
az pscloud pool create --resource-group {resource_group} --name {storage_pool_name} --location {location} --zone {availability_zone} --subnet-name {subnet_name} --vnet-name {vnet_name} --provisioned-bandwidth {bandwidth_mb_per_sec} --reservation-id {reservation_resource_id} --tags "{key:value}"
```

**Required Parameters:**
- `--zone` or `-z`: Azure Availability Zone (1, 2, or 3)
- `--subnet-name`: Name of the delegated subnet
- `--vnet-name`: Name of the virtual network
- `--provisioned-bandwidth`: Bandwidth in MB/s
- `--reservation-id`: Azure resource ID of the Pure Storage Cloud reservation

**Example with realistic values:**
```bash
az pscloud pool create \
  --resource-group myResourceGroup \
  --storage-pool-name myStoragePool \
  --location eastus \
  --zone 1 \
  --subnet-name mySubnet \
  --vnet-name myVnet \
  --provisioned-bandwidth 100 \
  --reservation-id /subscriptions/12345678-1234-1234-1234-123456789abc/providers/PureStorage.Block/reservations/myReservation
```

#### Show a Storage Pool ####

```bash
az pscloud pool show --resource-group {resource_group} --name {storage_pool_name}
```

#### List Storage Pools ####

```bash
az pscloud pool list --resource-group {resource_group}
```

#### Update a Storage Pool ####

```bash
az pscloud pool update --resource-group {resource_group} --name {storage_pool_name} --provisioned-bandwidth {bandwidth_mb_per_sec}
```

**Note:** Identity-related parameters (`--system-assigned`, `--user-assigned`) have been removed as they are not supported by the Pure Storage Cloud service.

#### Delete a Storage Pool ####

```bash
az pscloud pool delete --resource-group {resource_group} --name {storage_pool_name}
```

#### Connect a Storage Pool to AVS ####

Currently, establishing a connection between a Storage Pool and an Azure VMware Solution (AVS) resource must be initiated from the Azure Portal and cannot be initiated from CLI.

#### Get Storage Pool Health Status ####

This command provides the health status about the Storage Pool.

```bash
az pscloud pool get-health-status --resource-group {resource_group} --name {storage_pool_name}
```

#### Get Storage Pool AVS Status ####

This command provides the current connection status between the Storage Pool and Azure VMware Solution (AVS) resource.

```bash
az pscloud pool get-avs-status --resource-group {resource_group} --name {storage_pool_name}
```

**Note:** You can use either `--name` or `-n` for the storage pool name parameter.

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.