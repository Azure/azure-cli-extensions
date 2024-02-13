# Azure CLI purview Extension #
This is the extension for purview

### How to use ###
Install this extension using the below CLI command
```
az extension add --name purview
```

### Included Features ###
#### purview account ####
##### Create #####
```
az purview account create --location "WestUS2" --managed-group-name "custom-rgname" \
     --name "account1" --resource-group "SampleResourceGroup" 

az purview account wait --created --name "{myAccount}" --resource-group "{rg}"
```
##### Show #####
```
az purview account show --name "account1" --resource-group "SampleResourceGroup"
```
##### List #####
```
az purview account list --resource-group "SampleResourceGroup"
```
##### Update #####
```
az purview account update --name "account1" --tags newTag="New tag value." --resource-group "SampleResourceGroup"
```
##### Add-root-collection-admin #####
```
az purview account add-root-collection-admin --name "account1" --object-id "7e8de0e7-2bfc-4e1f-9659-2a5785e4356f" \
    --resource-group "SampleResourceGroup" 
```
##### List-key #####
```
az purview account list-key --name "account1" --resource-group "SampleResourceGroup"
```
##### Delete #####
```
az purview account delete --name "account1" --resource-group "SampleResourceGroup"
```
#### purview default-account ####
##### Show #####
```
az purview default-account show --subscription-id "12345678-1234-1234-12345678abc" \
    --scope-tenant-id "12345678-1234-1234-12345678abc" 
```
##### Remove #####
```
az purview default-account remove --scope-tenant-id "12345678-1234-1234-12345678abc" --scope-type "Tenant" 
```
##### Set #####
```
az purview default-account set --account-name "myDefaultAccount" --resource-group "rg-1" \
     --scope-tenant-id "12345678-1234-1234-12345678abc" --scope-type "Tenant" 
```