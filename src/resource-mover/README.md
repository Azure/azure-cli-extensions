# Azure CLI resource-mover Extension #
This is the extension for resource-mover

### How to use ###
Install this extension using the below CLI command
```
az extension add --name resource-mover
```

### Included Features ###
#### resource-mover move-collection ####
##### Create #####
```
az resource-mover move-collection create --identity type="SystemAssigned" --location "eastus2" \
    --source-region "eastus" --target-region "westus" --name "movecollection1" --resource-group "rg1" 
```
##### Show #####
```
az resource-mover move-collection show --name "movecollection1" --resource-group "rg1"
```
##### Update #####
```
az resource-mover move-collection update --identity type="SystemAssigned" --tags key1="mc1" --name "movecollection1" \
    --resource-group "rg1" 
```
##### Bulk-remove #####
```
az resource-mover move-collection bulk-remove \
    --move-resources "/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.Migrate/MoveCollections/movecollection1/MoveResources/moveresource1" \
    --validate-only false --name "movecollection1" --resource-group "rg1" 
```
##### Commit #####
```
az resource-mover move-collection commit \
    --move-resources "/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.Migrate/MoveCollections/movecollection1/MoveResources/moveresource1" \
    --validate-only false --name "movecollection1" --resource-group "rg1" 
```
##### Discard #####
```
az resource-mover move-collection discard \
    --move-resources "/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.Migrate/MoveCollections/movecollection1/MoveResources/moveresource1" \
    --validate-only false --name "movecollection1" --resource-group "rg1" 
```
##### Initiate-move #####
```
az resource-mover move-collection initiate-move \
    --move-resources "/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.Migrate/MoveCollections/movecollection1/MoveResources/moveresource1" \
    --validate-only false --name "movecollection1" --resource-group "rg1" 
```
##### List-move-collection #####
```
az resource-mover move-collection list-move-collection --resource-group "rg1"
```
##### List-required-for #####
```
az resource-mover move-collection list-required-for --name "movecollection1" --resource-group "rg1" \
    --source-id "/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.Network/virtualNetworks/nic1" 
```
##### Prepare #####
```
az resource-mover move-collection prepare \
    --move-resources "/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.Migrate/MoveCollections/movecollection1/MoveResources/moveresource1" \
    --validate-only false --name "movecollection1" --resource-group "rg1" 
```
##### Resolve-dependency #####
```
az resource-mover move-collection resolve-dependency --name "movecollection1" --resource-group "rg1"
```
##### Delete #####
```
az resource-mover move-collection delete --name "movecollection1" --resource-group "rg1"
```
#### resource-mover move-resource ####
##### Create #####
```
az resource-mover move-resource create \
    --depends-on-overrides id="/subscriptions/c4488a3f-a7f7-4ad4-aa72-0e1f4d9c0756/resourceGroups/eastusRG/providers/Microsoft.Network/networkInterfaces/eastusvm140" target-id="/subscriptions/c4488a3f-a7f7-4ad4-aa72-0e1f4d9c0756/resourceGroups/westusRG/providers/Microsoft.Network/networkInterfaces/eastusvm140" \
    --resource-settings "{\\"resourceType\\":\\"Microsoft.Compute/virtualMachines\\",\\"targetAvailabilitySetId\\":\\"/subscriptions/subid/resourceGroups/eastusRG/providers/Microsoft.Compute/availabilitySets/avset1\\",\\"targetAvailabilityZone\\":\\"2\\",\\"targetResourceName\\":\\"westusvm1\\",\\"targetVmSize\\":null}" \
    --source-id "/subscriptions/subid/resourceGroups/eastusRG/providers/Microsoft.Compute/virtualMachines/eastusvm1" \
    --move-collection-name "movecollection1" --name "moveresourcename1" --resource-group "rg1" 

az resource-mover move-resource wait --created --name "{myMoveResource2}" --resource-group "{rg}"
```
##### Show #####
```
az resource-mover move-resource show --move-collection-name "movecollection1" --name "moveresourcename1" \
    --resource-group "rg1" 
```
##### List #####
```
az resource-mover move-resource list --move-collection-name "movecollection1" --resource-group "rg1"
```
##### Delete #####
```
az resource-mover move-resource delete --move-collection-name "movecollection1" --name "moveresourcename1" \
    --resource-group "rg1" 
```
#### resource-mover unresolved-dependency ####
##### Show #####
```
az resource-mover unresolved-dependency show --move-collection-name "movecollection1" --resource-group "rg1"
```
#### resource-mover operation-discovery ####
##### Show #####
```
az resource-mover operation-discovery show
```