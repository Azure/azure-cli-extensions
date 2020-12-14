# Azure CLI managementgroup Extension #
This is the extension for managementgroup

### How to use ###
Install this extension using the below CLI command
```
az extension add --name managementgroup
```

### Included Features ###
#### managementgroup management-group ####
##### Create #####
```
az managementgroup management-group create --cache-control "no-cache" --display-name "ChildGroup" \
    --group-id "ChildGroup" 
```
##### Show #####
```
az managementgroup management-group show --cache-control "no-cache" --group-id "20000000-0001-0000-0000-000000000000"
```
##### Show #####
```
az managementgroup management-group show --expand "children" --cache-control "no-cache" \
    --group-id "20000000-0001-0000-0000-000000000000" 
```
##### Show #####
```
az managementgroup management-group show --expand "children" --recurse true --cache-control "no-cache" \
    --group-id "20000000-0001-0000-0000-000000000000" 
```
##### List #####
```
az managementgroup management-group list --cache-control "no-cache"
```
##### Update #####
```
az managementgroup management-group update --cache-control "no-cache" --group-id "ChildGroup" \
    --display-name "AlternateDisplayName" \
    --parent-group-id "/providers/Microsoft.Management/managementGroups/AlternateRootGroup" 
```
##### Get-descendant #####
```
az managementgroup management-group get-descendant --group-id "20000000-0000-0000-0000-000000000000"
```
##### Delete #####
```
az managementgroup management-group delete --cache-control "no-cache" --group-id "GroupToDelete"
```
#### managementgroup management-group-subscription ####
##### Create #####
```
az managementgroup management-group-subscription create --cache-control "no-cache" --group-id "Group" \
    --subscription-id "728bcbe4-8d56-4510-86c2-4921b8beefbc" 
```
##### Get-subscription #####
```
az managementgroup management-group-subscription get-subscription --cache-control "no-cache" --group-id "Group" \
    --subscription-id "728bcbe4-8d56-4510-86c2-4921b8beefbc" 
```
##### Get-subscription-under-management-group #####
```
az managementgroup management-group-subscription get-subscription-under-management-group --group-id "Group"
```
##### Delete #####
```
az managementgroup management-group-subscription delete --cache-control "no-cache" --group-id "Group" \
    --subscription-id "728bcbe4-8d56-4510-86c2-4921b8beefbc" 
```
#### managementgroup hierarchy-setting ####
##### Create #####
```
az managementgroup hierarchy-setting create \
    --default-management-group "/providers/Microsoft.Management/managementGroups/DefaultGroup" \
    --require-authorization-for-group-creation true --group-id "root" 
```
##### Show #####
```
az managementgroup hierarchy-setting show --group-id "root"
```
##### List #####
```
az managementgroup hierarchy-setting list --group-id "root"
```
##### Update #####
```
az managementgroup hierarchy-setting update \
    --default-management-group "/providers/Microsoft.Management/managementGroups/DefaultGroup" \
    --require-authorization-for-group-creation true --group-id "root" 
```
##### Delete #####
```
az managementgroup hierarchy-setting delete --group-id "root"
```
#### managementgroup  ####
##### Start-tenant-backfill #####
```
az managementgroup  start-tenant-backfill
```
##### Tenant-backfill-status #####
```
az managementgroup  tenant-backfill-status
```
#### managementgroup entity ####
##### List #####
```
az managementgroup entity list
```