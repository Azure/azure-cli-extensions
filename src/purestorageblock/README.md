# Azure CLI Purestorageblock Extension #

This is an extension to Azure CLI to manage Pure Storage Block resources in Azure. The extension provides comprehensive management capabilities for Pure Storage Block reservations and storage pools.

## How to use ##

### Install the extension ###

Install this extension using the below CLI command:
```
az extension add --name purestorageblock
```

### Check the version ###

```
az extension show --name purestorageblock --query version
```

### Connect to Azure subscription ###

```
az login
az account set -s {subscription_id}
```

### Create a resource group (or use an existing one) ###

```
az group create -n myResourceGroup -l "Central US"
```

## Available Commands ##

### Reservation Commands ###

#### List Pure Storage Block Reservations ####

```
az purestorageblock reservation list
```

#### Show a specific Pure Storage Block Reservation ####

```
az purestorageblock reservation show --resource-group {resource_group} --reservation-name {reservation_name}
```

#### Create a Pure Storage Block Reservation ####

```
az purestorageblock reservation create \
  --resource-group {resource_group} \
  --reservation-name {reservation_name} \
  --location {location} \
  --tags '{"key1":"value1","key2":"value2"}' \
  --marketplace '{"subscription-status":"{subscription_status}","offer-details":{"publisher-id":"{publisher_id}","offer-id":"{offer_id}","plan-id":"{plan_id}","term-unit":"{term_unit}","term-id":"{term_id}"}}' \
  --user '{"first-name":"{first_name}","last-name":"{last_name}","email-address":"{email_address}","company-details":{"company-name":"{company_name}","address":{"address-line1":"{address_line1}","address-line2":"{address_line2}","city":"{city}","state":"{state}","country":"{country}","postal-code":"{postal_code}"}}}'
```

#### Delete a Pure Storage Block Reservation ####

```
az purestorageblock reservation delete --resource-group {resource_group} --reservation-name {reservation_name}
```

#### Get Resource Limit for Reservations ####

```
az purestorageblock reservation get-resource-limit --resource-group {resource_group} --reservation-name {reservation_name}
```

#### Wait for Reservation Operation to Complete ####

```
az purestorageblock reservation wait --resource-group {resource_group} --reservation-name {reservation_name} --created
```

### Storage Pool Commands ###

#### List Pure Storage Block Storage Pools ####

```
az purestorageblock storagepool list --resource-group {resource_group}
```

#### Show a specific Pure Storage Block Storage Pool ####

```
az purestorageblock storagepool show --resource-group {resource_group} --storage-pool-name {storage_pool_name}
```

#### Create a Pure Storage Block Storage Pool ####

```
az purestorageblock storagepool create \
  --resource-group {resource_group} \
  --storage-pool-name {storage_pool_name} \
  --location {location} \
  --tags '{"environment":"production","team":"storage"}' \
  --reservation-id {reservation_id} \
  --availability-zone {availability_zone} \
  --provisioned-bandwidth {provisioned_bandwidth_mb_per_sec} \
  --vnet-injection '{"subnet-id":"{subnet_id}","vnet-id":"{vnet_id}"}' \
  --system-assigned {system_assigned_identity} \
  --user-assigned {user_assigned_identities}
```

#### Update a Pure Storage Block Storage Pool ####

```
az purestorageblock storagepool update \
  --resource-group {resource_group} \
  --storage-pool-name {storage_pool_name} \
  --provisioned-bandwidth {provisioned_bandwidth_mb_per_sec} \
```

#### Delete a Pure Storage Block Storage Pool ####

```
az purestorageblock storagepool delete --resource-group {resource_group} --storage-pool-name {storage_pool_name}
```

#### Get Health Status of Storage Pool ####

```
az purestorageblock storagepool get-health-status --resource-group {resource_group} --storage-pool-name {storage_pool_name}
```

#### Wait for Storage Pool Operation to Complete ####

```
az purestorageblock storagepool wait --resource-group {resource_group} --storage-pool-name {storage_pool_name} --created
```

## Common Parameters ##

- `--resource-group` or `-g`: Name of the resource group
- `--location` or `-l`: Location/region for the resource
- `--tags`: Space-separated tags in 'key[=value]' format
- `--reservation-name`: Name of the Pure Storage Block reservation
- `--storage-pool-name`: Name of the Pure Storage Block storage pool
- `--reservation-id`: Azure resource ID of the Pure Storage Block reservation
- `--availability-zone`: Azure Availability Zone for the storage pool
- `--provisioned-bandwidth`: Total bandwidth provisioned for the pool, in MB/s
- `--vnet-injection`: Network properties for virtual network injection
- `--system-assigned`: System managed identity configuration
- `--user-assigned`: User managed identities configuration

## JSON Parameter Formats ##

### Marketplace Details ###
```json
{
  "subscription-status": "{subscription_status}",
  "offer-details": {
    "publisher-id": "{publisher_id}",
    "offer-id": "{offer_id}",
    "plan-id": "{plan_id}",
    "term-unit": "{term_unit}",
    "term-id": "{term_id}"
  }
}
```

### User Details ###
```json
{
  "first-name": "{first_name}",
  "last-name": "{last_name}",
  "email-address": "{email_address}",
  "company-details": {
    "company-name": "{company_name}",
    "address": {
      "address-line1": "{address_line1}",
      "address-line2": "{address_line2}",
      "city": "{city}",
      "state": "{state}",
      "country": "{country}",
      "postal-code": "{postal_code}"
    }
  }
}
```

### VNet Injection ###
```json
{
  "subnet-id": "{subnet_id}",
  "vnet-id": "{vnet_id}"
}
```

## Support ##

For issues and questions, please refer to the [Azure CLI documentation](https://docs.microsoft.com/cli/azure/) or file an issue in the [Azure CLI Extensions repository](https://github.com/Azure/azure-cli-extensions).