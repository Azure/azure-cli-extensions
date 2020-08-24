Microsoft Azure CLI 'swiftlet' Extension
==========================================

This package is for the 'swiftlet' extension. Swiftlet is a new Azure Compute offering. Swiftlet is conceived to offer a greatly simplified Azure experience for non-enterprise developers.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name swiftlet
```

### Sample Commands ###
Create a Swiftlet VM
```
az swiftlet vm create --location "westus" --password "{your-password}," --ports \
port-range="3389" protocol="*" --startup-script "{inline startup script}" --swiftlet-bundle-sku "Windows_1" \
--swiftlet-image-id "windows-2019-datacenter" --username "SwiftletUser" --tags key1="value1" key2="value2" \
--resource-group "myResourceGroup" --name "myVirtualMachine"
```
Show information of a Swiftlet VM
```
az swiftlet vm show --resource-group "myResourceGroup" --name "myVirtualMachine"
```
List available Swiftlet bundles
```
az swiftlet vm list-bundle --location "westus"
```
List available Swiftlet images
```
az swiftlet vm list-image --location "westus"
```
