# Azure CLI DependencyMap Extension #
This is an extension to Azure CLI to manage DependencyMap resources.
==========================================

## How to use ##
### Usage ###
#### Install the extension ####
Install this extension using the below CLI command
```
az extension add --name dependency-map
```
#### Check the version ####
```
az extension show --name dependency-map --query version
```
#### Connect to Azure subscription ####
```
az login
az account set -s {subs_id}
```
#### Create a resource group (or use an existing one) ####
```
az group create -n testrg -l eastus
```
#### Create a dependency map resource ####
```
az dependency-map create --resource-group testrg --map-name mapname --location westus2
```
#### List dependency map resources ####
```
az dependency-map list -g testrg
```
#### Get a dependency map resource ####
```
az dependency-map show -g testrg -n mapname
```
#### Update a dependency map resource ####
```
az dependency-map update -g testrg -n mapname --tags key1=value1
```
#### Delete a dependency map resource ####
```
az dependency-map delete -g testrg -n mapname
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.
