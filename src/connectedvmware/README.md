# Microsoft Azure CLI ConnectedVMware Extension #

The Azure CLI extension for [Azure Arc VMware Service](https://azure.microsoft.com/en-us/services/azure-arc) is an extension for Azure CLI 2.0.

## Install
``` sh
az extension add --name connectedvmware
```

## Usage
See the [extension reference documenation](https://azure.microsoft.com/en-us/services/azure-arc).

``` sh
az connectedvmware --help
az connectedvmware vcenter list -g $resourcegroup
az connectedvmware vcenter connect -g $rg --location $location  --custom-location $customLocation --fqdn $fqdn --username $username --password $pwd
```

## Uninstall
You can see if the extension is installed by running `az --version` or `az extension list`. You can remove the extension by running:
``` sh
az extension remove --name connectedvmware
```
