# Microsoft Azure CLI VMware Extension #

The Azure CLI extension for [Azure VMware Solution](https://docs.microsoft.com/azure/azure-vmware/) (AVS) is an extension for Azure CLI 2.0.

## Install
``` sh
az extension add --name vmware
```

## Usage
See the [extension reference documentation](https://docs.microsoft.com/cli/azure/vmware).

``` sh
az vmware --help
az vmware private-cloud list
az vmware private-cloud create -g $resourcegroup -n $privatecloudname --location $location --cluster-size 3 --network-block 10.175.0.0/22
```

## Uninstall
You can see if the extension is installed by running `az --version` or `az extension list`. You can remove the extension by running:
``` sh
az extension remove --name vmware
```
