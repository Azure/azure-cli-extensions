# Azure CLI ArizeAi Extension #
This is an extension to Azure CLI to manage ArizeAi resources.

## How to use ##
#### Install the extension ####
Install this extension using the below CLI command
```
az extension add --name arize-ai
```
#### Check the version ####
```
az extension show --name arize-ai --query version
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
#### Create an arize-ai organization resource ####
```
az arize-ai observability-eval organization create --resource-group QM_clitest_qumulo2_eastus --organizationname test-cli-instance-4 --marketplace "{subscription-id: fc35d936-3b89-41f8-8110-a24b56826c37,offer-details:{publisher-id:arizeai1657829589668,offer-id:arize-liftr-0,plan-id:liftr-test-0,plan-name:Liftr Test 0}}" --user "{first-name:"",last-name:"",email-address:aggarwalsw@microsoft.com,upn:aggarwalsw@microsoft.com}" --partner-properties "{description:'Test Description'}" --location "East US"
```
#### List an arize-ai organization resource ####
```
az arize-ai observability-eval organization show --resource-group QM_clitest_qumulo2_eastus
```
#### Get an arize-ai organization resource ####
```
az arize-ai observability-eval organization show --resource-group QM_clitest_qumulo2_eastus --organizationname test-cli-instance-5
```
#### Delete an arize-ai organization resource ####
```
az arize-ai observability-eval organization delete --resource-group QM_clitest_qumulo2_eastus --organizationname test-cli-instance-5
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.
