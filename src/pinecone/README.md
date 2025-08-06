# Azure CLI Pinecone Extension #
This is an extension to Azure CLI to manage Pinecone resources.

## How to use ##
#### Install the extension ####
Install this extension using the below CLI command
```
az extension add --name pinecone
```
#### Check the version ####
```
az extension show --name pinecone --query version
```
#### Connect to Azure subscription ####
```
az login
az account set -s {subs_id}
```
#### List an weights-and-biases instance ####
```
az pinecone vector-db organization show --resource-group clitest
```
#### Get a weights-and-biases instance resource ####
```
az pinecone vector-db organization show --resource-group clitest --organizationname test-cli-instance-4
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.