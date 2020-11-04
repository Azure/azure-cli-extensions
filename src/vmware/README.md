#  Azure VMware Solution Extension

The Azure CLI extension for Azure VMware Solution is an extension for Azure CLI 2.0.

## Install
``` sh
az extension add --name vmware
```

## Usage
See the [extension reference documenation](https://docs.microsoft.com/en-us/cli/azure/ext/vmware/vmware?view=azure-cli-latest).

``` sh
az vmware --help
az vmware private-cloud list
az vmware private-cloud create -g $resourcegroup -n $privatecloudname --location $location --cluster-size 3 --network-block 10.175.0.0/22
```
See [test_vmware_scenario.py](azext_vmware/tests/latest/test_vmware_scenario.py) for other examples.

## Uninstall
You can see if the extension is installed by running `az --version` or `az extension list`. You can remove the extension by running:
``` sh
az extension remove --name vmware
```