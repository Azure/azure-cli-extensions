# Azure CLI LambdaTest Extension #
This is an extension to Azure CLI to manage LambdaTest resources.

## How to use ##
#### Install the extension ####
Install this extension using the below CLI command
```
az extension add --name lambda-test
```
#### Check the version ####
```
az extension show --name lambda-test --query version
```
#### Connect to Azure subscription ####
```
az login
az account set -s {subs_id}
```
#### List an weights-and-biases instance ####
```
az lambda-test hyper-execute organization list --resource-group jawt-rg
```
#### Get a weights-and-biases instance resource ####
```
az lambda-test hyper-execute organization show --resource-group jawt-rg --organizationname wnb-test-org-5
```