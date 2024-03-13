# Azure CLI Astronomer Extension #
This is an extension to Azure CLI to manage Astronomer resources.
==========================================

### Usage ###
#### Install the extension ####
Install this extension using the below CLI command
```
az extension add --name astronomer
```
#### Check the version ####
```
az extension show --name astronomer --query version
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
#### Create an astronomer organization resource ####
```
az astronomer organization create --resource-group testrg --name testAstronomerOrganization --location "eastus" 
--marketplace {"subscription-id":"ntthclydlpqmasr","offer-details":{"publisher-id":"gfsqxygpnerxmvols","offer-id":"krzkefmpxztqyusidzgpchfaswuyce","plan-id":"kndxzygsanuiqzwbfbbvoipv","plan-name":"pwqjwlq","term-unit":"xyygyzcazkuelz","term-id":"pwds"}} 
--partner-organization {"organization-name":"orgname","workspace-name":"workspacename","single-sign-on-properties":{"aad-domains":["kfbleh"]}} 
--user {"first-name":"nfh","last-name":"lazfbstcccykibvcrxpmglqam","email-address":".K_@e7N-g1.xjqnbPs"}
```
#### List an astronomer organization resource ####
```
az astronomer organization list -g testrg
```
#### Get an astronomer organization resource ####
```
az astronomer organization show -g testrg -n testAstronomerOrganization
```
#### Update an astronomer organization resource ####
```
az astronomer organization update -g testrg -n testAstronomerOrganization --tags key1=value1
```
#### Delete an astronomer organization resource ####
```
az astronomer organization delete -g testrg -n testAstronomerOrganization
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.
