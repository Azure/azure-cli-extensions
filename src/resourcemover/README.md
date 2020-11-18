# Azure CLI resourcemover Extension #
This is the extension for resourcemover

### How to use ###
Install this extension using the below CLI command
```
az extension add --name resourcemover
```

### Included Features ###
#### resourcemover move-collection ####
##### Create #####
```
az resourcemover move-collection create --identity type="SystemAssigned" --location "eastus2" \
    --properties source-region="eastus" target-region="westus" --name "movecollection1" --resource-group "rg1" 
```
##### Show #####
```
az resourcemover move-collection show --name "movecollection1" --resource-group "rg1"
```
##### Update #####
```
az resourcemover move-collection update --identity type="SystemAssigned" --tags key1="mc1" --name "movecollection1" \
    --resource-group "rg1" 
```
##### Bulk-remove #####
```
az resourcemover move-collection bulk-remove \
    --move-resources "/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.Migrate/MoveCollections/movecollection1/MoveResources/moveresource1" \
    --validate-only false --name "movecollection1" --resource-group "rg1" 
```
##### Commit #####
```
az resourcemover move-collection commit \
    --move-resources "/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.Migrate/MoveCollections/movecollection1/MoveResources/moveresource1" \
    --validate-only false --name "movecollection1" --resource-group "rg1" 
```
##### Discard #####
```
az resourcemover move-collection discard \
    --move-resources "/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.Migrate/MoveCollections/movecollection1/MoveResources/moveresource1" \
    --validate-only false --name "movecollection1" --resource-group "rg1" 
```
##### Initiate-move #####
```
az resourcemover move-collection initiate-move \
    --move-resources "/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.Migrate/MoveCollections/movecollection1/MoveResources/moveresource1" \
    --validate-only false --name "movecollection1" --resource-group "rg1" 
```
##### List-move-collection #####
```
az resourcemover move-collection list-move-collection --resource-group "rg1"
```
##### Prepare #####
```
az resourcemover move-collection prepare \
    --move-resources "/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.Migrate/MoveCollections/movecollection1/MoveResources/moveresource1" \
    --validate-only false --name "movecollection1" --resource-group "rg1" 
```
##### Resolve-dependency #####
```
az resourcemover move-collection resolve-dependency --name "movecollection1" --resource-group "rg1"
```
##### Delete #####
```
az resourcemover move-collection delete --name "movecollection1" --resource-group "rg1"
```
#### resourcemover move-resource ####
##### Create #####
```
az resourcemover move-resource create \
    --depends-on-overrides id="/subscriptions/c4488a3f-a7f7-4ad4-aa72-0e1f4d9c0756/resourceGroups/eastusRG/providers/Microsoft.Network/networkInterfaces/eastusvm140" target-id="/subscriptions/c4488a3f-a7f7-4ad4-aa72-0e1f4d9c0756/resourceGroups/westusRG/providers/Microsoft.Network/networkInterfaces/eastusvm140" \
    --resource-settings "{\\"resourceType\\":\\"Microsoft.Compute/virtualMachines\\",\\"targetAvailabilitySetId\\":\\"/subscriptions/subid/resourceGroups/eastusRG/providers/Microsoft.Compute/availabilitySets/avset1\\",\\"targetAvailabilityZone\\":\\"2\\",\\"targetResourceName\\":\\"westusvm1\\",\\"targetVmSize\\":null}" \
    --source-id "/subscriptions/subid/resourceGroups/eastusRG/providers/Microsoft.Compute/virtualMachines/eastusvm1" \
    --move-collection-name "movecollection1" --name "moveresourcename1" --resource-group "rg1" 

az resourcemover move-resource wait --created --name "{myMoveResource3}" --resource-group "{rg}"
```
##### Show #####
```
az resourcemover move-resource show --move-collection-name "movecollection1" --name "moveresourcename1" \
    --resource-group "rg1" 
```
##### List #####
```
az resourcemover move-resource list --move-collection-name "movecollection1" --resource-group "rg1"
```
##### Delete #####
```
az resourcemover move-resource delete --move-collection-name "movecollection1" --name "moveresourcename1" \
    --resource-group "rg1" 
```
#### resourcemover unresolved-dependency ####
##### Show #####
```
az resourcemover unresolved-dependency show --move-collection-name "movecollection1" --resource-group "rg1"
```
#### resourcemover operation-discovery ####
##### Show #####
```
az resourcemover operation-discovery show
```