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
az managementgroup management-group create --display-name "ChildGroup" \
    --id "/providers/Microsoft.Management/managementGroups/GroupName" --group-id "ChildGroup" 
```
##### Show #####
```
az managementgroup management-group show --cache-control "no-cache" --group-id "20000000-0001-0000-0000-000000000000"
```
##### Show #####
```
az managementgroup management-group show --expand "ancestors" \
    --group-id "20000000-0001-0000-0000-00000000000" 
```
##### Show #####
```
az managementgroup management-group show --expand "children" \
    --group-id "20000000-0001-0000-0000-000000000000" 
```
##### Show #####
```
az managementgroup management-group show --expand "path" \
    --group-id "20000000-0001-0000-0000-000000000000" 
```
##### Show #####
```
az managementgroup management-group show --expand "children" --recurse true \
    --group-id "20000000-0001-0000-0000-000000000000" 
```
##### List #####
```
az managementgroup management-group list
```
##### Update #####
```
az managementgroup management-group update --group-id "ChildGroup" \
    --display-name "AlternateDisplayName" \
    --parent-group-id "/providers/Microsoft.Management/managementGroups/AlternateParentGroup" 
```
##### Show-descendant #####
```
az managementgroup management-group show-descendant --group-id "20000000-0000-0000-0000-000000000000"
```
##### Delete #####
```
az managementgroup management-group delete --group-id "GroupToDelete"
```
#### managementgroup management-group-subscription ####
##### Create #####
```
az managementgroup management-group-subscription create --group-id "Group" \
    --subscription-id "728bcbe4-8d56-4510-86c2-4921b8beefbc" 
```
##### Show-subscription #####
```
az managementgroup management-group-subscription show-subscription --group-id "Group" \
    --subscription-id "728bcbe4-8d56-4510-86c2-4921b8beefbc" 
```
##### Show-subscription-under-management-group #####
```
az managementgroup management-group-subscription show-subscription-under-management-group --group-id "Group"
```
##### Delete #####
```
az managementgroup management-group-subscription delete --group-id "Group" \
    --subscription-id "728bcbe4-8d56-4510-86c2-4921b8beefbc" 
```
#### managementgroup hierarchy-setting ####
##### Create #####
```
az managementgroup hierarchy-setting create \
    --default-management-group "/providers/Microsoft.Management/managementGroups/DefaultGroup" \
    --require-authorization-for-group-creation true --group-id "groupName" 
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
#### managementgroup ####
##### Start-tenant-backfill #####
```
az managementgroup start-tenant-backfill
```
##### Tenant-backfill-status #####
```
az managementgroup tenant-backfill-status
```
#### managementgroup entity ####
##### List #####
```
az managementgroup entity list
```