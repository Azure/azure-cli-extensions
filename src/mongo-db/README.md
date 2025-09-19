# Azure CLI MongoDB Extension #

This is an extension to create MongoDB Atlas organizations in Azure via Azure CLI.

## How to use ##

### Install the extension ###

Install this extension using the below CLI command:
```
az extension add --name mongo-db
```

### Check the version ###

```
az extension show --name mongo-db --query version
```

### Connect to Azure subscription ###

```
az login
az account set -s {subs_id}
```

### Create a resource group (or use an existing one) ###

```
az group create -n demoResourceGroup -l eastus
```

## Available Commands ##

### Organization Commands ###

#### Create a MongoDB Atlas Organization ####

```
az mongo-db atlas organization create -name MyOrganizationResourceName --resource-group MyResourceGroup --location "eastus" --subscription "abcd1234-5678-90ab-cdef-12345678abcd"--user {"first-name":"John","last-name":"Doe","email-address":"test@email.com"}" --marketplace "{"subscription-id":"abcd1234-5678-90ab-cdef-12345678abcd","subscription-status":"PendingFulfillmentStart","offer-details":{"publisher-id":"mongodb","offer-id":"mongodb_atlas_azure_native_prod","plan-id":"private_plan","plan-name":"Pay as You Go (Free) (Private)","term-unit":"P1M","term-id":"gmz7xq9ge3py"}}" --partner-properties "{"organization-name":"partner-org-name"}"
```

#### Show a MongoDB Atlas Organization ####

```
az mongo-db atlas organization show --resource-group {resource_group} --name {resource_name}
```

#### Delete a MongoDB Atlas Organization. This deletes the MongoDB Atlas resource in Azure ####

```
az mongo-db atlas organization delete --resource-group {resource_group} --name {resource_name}
```

#### List MongoDB Atlas Organizations by Subscription ####

```
az mongo-db atlas organization list --subscription {subscription_id} --resource-group {resource_group}
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.