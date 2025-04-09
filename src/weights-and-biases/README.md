# Azure CLI WeightsAndBiases Extension #
This is an extension to Azure CLI to manage WeightsAndBiases resources.

## How to use ##
#### Install the extension ####
Install this extension using the below CLI command
```
az extension add --name weights-and-biases
```
#### Check the version ####
```
az extension show --name weights-and-biases --query version
```
#### Connect to Azure subscription ####
```
az login
az account set -s {subs_id}
```
#### List an weights-and-biases instance ####
```
az weights-and-biases instance list --resource-group jawt-rg
```
#### Get a weights-and-biases instance resource ####
```
az weights-and-biases instance show --resource-group jawt-rg --instancename wnb-test-org-5
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.