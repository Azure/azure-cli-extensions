# Microsoft Azure CLI ConnectedVMware Extension

The Azure CLI extension for [Azure Arc for VMware PrivateCloud](https://github.com/Azure/azure-arc-enabled-vmware-vsphere-preview/blob/main/docs/overview.md) is an extension for Azure CLI 2.0.

## Install

```
az extension add --name connectedvmware
```

## Usage

See the [extension reference documenation](https://github.com/Azure/azure-arc-enabled-vmware-vsphere-preview/blob/main/docs/overview.md).
_Examples:_

##### Create Vcenter Resource

```
az connectedvmware vcenter connect \
    --subscription subscriptionId \
    --resource-group resourceGroupName \
    --location locationName \
    --custom-location customLocationName \
    --fqdn vcenterFqdn \
    --username userName \
    --password password \
    --name resourceName
```

##### Create Resource Pool Resource

```
az connectedvmware resource-pool create \
    --subscription subscriptionId \
    --resource-group resourceGroupName \
    --location locationName \
    --custom-location customLocationName \
    --vcenter vcenterResourceName \
    --mo-ref-id morefId \
    --name resourceName
```

##### Create Cluster Resource

```
az connectedvmware cluster create \
    --subscription subscriptionId \
    --resource-group resourceGroupName \
    --location locationName \
    --custom-location customLocationName \
    --vcenter vcenterResourceName \
    --mo-ref-id morefId \
    --name resourceName
```

##### Create Host Resource

```
az connectedvmware host create \
    --subscription subscriptionId \
    --resource-group resourceGroupName \
    --location locationName \
    --custom-location customLocationName \
    --vcenter vcenterResourceName \
    --mo-ref-id morefId \
    --name resourceName
```

##### Create Datastore Resource

```
az connectedvmware datastore create \
    --subscription subscriptionId \
    --resource-group resourceGroupName \
    --location locationName \
    --custom-location customLocationName \
    --vcenter vcenterResourceName \
    --mo-ref-id morefId \
    --name resourceName
```

##### Create VM Template Resource

```
az connectedvmware vm-template create \
    --subscription subscriptionId \
    --resource-group resourceGroupName \
    --location locationName \
    --custom-location customLocationName \
    --vcenter vcenterResourceName \
    --mo-ref-id morefId \
    --name resourceName
```

##### Create Virtual Network Resource

```
az connectedvmware virtual-network create \
    --subscription subscriptionId \
    --resource-group resourceGroupName \
    --location locationName \
    --custom-location customLocationName \
    --vcenter vcenterResourceName \
    --mo-ref-id morefId \
    --name resourceName
```

##### Create Virtual Machine Instance Resource

```
az connectedvmware vm create \
    --subscription subscriptionId \
    --resource-group resourceGroupName \
    --location locationName \
    --custom-location customLocationName \
    --vcenter vcenterResourceName \
    --resource-pool resourcePoolResourceName \
    --vm-template vmTemplateResourceName \
    --name resourceName
```

## Uninstall

You can see if the extension is installed by running `az --version` or `az extension list`. You can remove the extension by running:

```
az extension remove --name connectedvmware
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.
