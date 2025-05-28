# Azure CLI connection Extension #
This is the extension for connection

### How to use ###
Install this extension using the below CLI command
```
az extension add --name connection
```

### Included Features ###
#### connection linker ####
##### Create #####
```
az connection linker create --name "linkName" \
    --auth-info "{\\"name\\":\\"name\\",\\"authType\\":\\"secret\\",\\"secret\\":\\"secret\\"}" \
    --target-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test-rg/providers/Microsoft.DocumentDb/databaseAccounts/test-acc/mongodbDatabases/test-db" \
    --resource-group "test-rg" --source-provider "Microsoft.Web" --source-resource-name "test-app" \
    --source-resource-type "sites" 

az connection linker wait --created --name "{myLinker}" --resource-group "{rg}"
```
##### Show #####
```
az connection linker show --name "linkName" --resource-group "test-rg" --source-provider "Microsoft.Web" \
    --source-resource-name "test-app" --source-resource-type "sites" 
```
##### List #####
```
az connection linker list --resource-group "test-rg" --source-provider "Microsoft.Web" \
    --source-resource-name "test-app" --source-resource-type "sites" 
```
##### Update #####
```
az connection linker update --name "linkName" \
    --auth-info "{\\"name\\":\\"name\\",\\"authType\\":\\"servicePrincipal\\",\\"id\\":\\"id\\"}" \
    --target-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test-rg/providers/Microsoft.DocumentDb/databaseAccounts/test-acc/mongodbDatabases/test-db" \
    --resource-group "test-rg" --source-provider "Microsoft.Web" --source-resource-name "test-app" \
    --source-resource-type "sites" 
```
##### List-configuration #####
```
az connection linker list-configuration --name "linkName" --resource-group "test-rg" --source-provider "Microsoft.Web" \
    --source-resource-name "test-app" --source-resource-type "sites" 
```
##### Validate-linker #####
```
az connection linker validate-linker --name "linkName" --resource-group "test-rg" --source-provider "Microsoft.Web" \
    --source-resource-name "test-app" --source-resource-type "sites" 
```
##### Validate-linker #####
```
az connection linker validate-linker --name "linkName" --resource-group "test-rg" --source-provider "Microsoft.Web" \
    --source-resource-name "test-app" --source-resource-type "sites" 
```
##### Delete #####
```
az connection linker delete --name "linkName" --resource-group "test-rg" --source-provider "Microsoft.Web" \
    --source-resource-name "test-app" --source-resource-type "sites" 
```