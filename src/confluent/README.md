# Azure CLI confluent Extension #
This is the extension for confluent

### How to use ###
Install this extension using the below CLI command
```
az extension add --name confluent
```

### Included Features ###
### User Access Management - Adding users to org ###
```
az confluent organization create-user --organization-name "string" --subscription "string" --resource-group  "string" --invited-email "string" --auth-type AUTH_TYPE_SSO
```
### Creates role binding for a user 
```
az confluent organization create-role-binding --organization-name "string" --subscription "string" --resource-group  "string" --principal User:u-vw7yzn --role-name "Rolename" --crn-pattern  "/environment=env-id"
```
### Deletes role binding for a user 
az confluent organization role-binding delete --organization-name "string" --subscription "string" --resource-group  "string" --role-binding-id "role-id"
### List of role binding for a user based on CRN Pattern
az confluent organization list-role-binding --organization-name "string" --subscription "string" --resource-group  "string" --search-filters "{CRNPattern:/environment=env-id}"
### List of service accounts in the organization
az confluent organization list-service-accounts --organization-name "string" --subscription "string" --resource-group  "string"
### List of users in the organization
az confluent organization list-users --organization-name "string" --subscription "string" --resource-group  "string" --search-filters {pageSize:100}
### List of environments in the organization
```
az confluent organization environment list --organization-name "string" --subscription "string" --resource-group  "string"
```
### List of clusters in an environment of the organization
```

az confluent organization environment cluster list --organization-name "string" --environment-id "env-id" --subscription "string" --resource-group  "string"
```
### List of schema registry clusters in an environment of the organization
```
az confluent organization environment schema-registry-cluster list --organization-name "string" --environment-id "env-id" --subscription "string" --resource-group  "string" 
```
### Create API Key in a cluster of the organization
az confluent organization environment cluster create-api-key --organization-name "string" --environment-id "env-id" --subscription "string" --resource-group  "string" --cluster-id "cluster-id"--description "api key description" --name "api key name"
### Delete API Key in a cluster of the organization
az confluent organization api-key delete --api-key-id "api-key-id" --organization-name "string" --subscription "string" --resource-group  "string"
### Included Features ###
#### confluent terms ####
##### List #####
```
az confluent terms list
```
#### confluent organization ####
##### Create #####
```
az confluent organization create --location "West US" \
    --offer-detail id="string" plan-id="string" plan-name="string" publisher-id="string" term-unit="string" \
    --user-detail email-address="contoso@microsoft.com" first-name="string" last-name="string" \
    --tags Environment="Dev" --name "myOrganization" --resource-group "myResourceGroup" 

az confluent organization wait --created --name "{myOrganization}" --resource-group "{rg}"
```
##### Show #####
```
az confluent organization show --name "myOrganization" --resource-group "myResourceGroup"
```
##### List #####
```
az confluent organization list --resource-group "myResourceGroup"
```
##### Update #####
```
az confluent organization update --tags client="dev-client" env="dev" --name "myOrganization" \
    --resource-group "myResourceGroup" 
```
##### Delete #####
```
az confluent organization delete --name "myOrganization" --resource-group "myResourceGroup"
```