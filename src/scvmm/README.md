# Microsoft Azure CLI SCVMM Extension

The Azure CLI extension for [Azure Arc for SCVMM PrivateCloud](https://aka.ms/azure-arc/scvmm/docs) is an extension for Azure CLI 2.0.

## Install

```
az extension add --name scvmm
```

## Usage

See the [extension reference documenation](https://aka.ms/azure-arc/scvmm/docs).
_Examples:_

##### Create VMMServer Resource

```
az scvmm vmmserver connect \
    --subscription subscriptionId \
    --resource-group resourceGroupName \
    --location locationName \
    --custom-location customLocationName \
    --fqdn vmmserverFqdn \
    --username userName \
    --password password \
    --name resourceName
```

##### Create Cloud Resource

```
az scvmm cloud create \
    --subscription subscriptionId \
    --resource-group resourceGroupName \
    --location locationName \
    --custom-location customLocationName \
    --vmmserver vmmserverResourceName \
    --inventory-item inventoryItemUUID \
    --name resourceName
```

##### Create VM Template Resource

```
az scvmm vm-template create \
    --subscription subscriptionId \
    --resource-group resourceGroupName \
    --location locationName \
    --custom-location customLocationName \
    --vmmserver vmmserverResourceName \
    --inventory-item inventoryItemUUID \
    --name resourceName
```

##### Create Virtual Network Resource

```
az scvmm virtual-network create \
    --subscription subscriptionId \
    --resource-group resourceGroupName \
    --location locationName \
    --custom-location customLocationName \
    --vmmserver vmmserverResourceName \
    --inventory-item inventoryItemUUID \
    --name resourceName
```

##### Create Availabilty Set Resource

```
az scvmm avset create \
    --subscription subscriptionId \
    --resource-group resourceGroupName \
    --location locationName \
    --custom-location customLocationName \
    --vmmserver vmmserverResourceName \
    --avset-name availabiltySetName \
    --name resourceName
```

##### Create Virtual Machine Instance Resource

###### Onboard existing Virtual Machine Instance to azure

```
az scvmm vm create \
    --subscription subscriptionId \
    --resource-group resourceGroupName \
    --location locationName \
    --custom-location customLocationName \
    --vmmserver vmmserverResourceName \
    --inventory-item inventoryItemUUID \
    --name resourceName
```

###### Create new Virtual Machine Instance

```
az scvmm vm create \
    --subscription subscriptionId \
    --resource-group resourceGroupName \
    --location locationName \
    --custom-location customLocationName \
    --cloud cloudResourceName \
    --vm-template vmTemplateResourceName \
    --name resourceName
```


## Uninstall

You can see if the extension is installed by running `az --version` or `az extension list`. You can remove the extension by running:

```
az extension remove --name scvmm
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.
