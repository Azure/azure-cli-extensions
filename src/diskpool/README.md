# Azure CLI Extension #
This is the extension for diskpool

### How to use ###
Install this extension using the below CLI command
```
az extension add -s https://zuhdefault.blob.core.windows.net/cliext/diskpool-0.2.0-py3-none-any.whl
```

### Included Features ###
#### disk-pool ####
##### Create #####
```
az disk-pool create --name "myDiskPool" --location "westus" --availability-zones "1" \
    --disks id="/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/vm-name_DataDisk_0" \
    --disks id="/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/vm-name_DataDisk_1" \
    --subnet-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.Network/virtualNetworks/myvnet/subnets/mysubnet" \
    --sku name="Standard_ABC" --tags key="value" --resource-group "myResourceGroup" 

az disk-pool wait --created --name "myDiskPool" --resource-group "myResourceGroup"
```
##### Show #####
```
az disk-pool show --name "myDiskPool" --resource-group "myResourceGroup"
```
##### List #####
```
az disk-pool list --resource-group "myResourceGroup"
```
##### Update #####
```
az disk-pool update --name "myDiskPool" --location "westus" --availability-zones "1" \
    --disks id="/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/vm-name_DataDisk_0" \
    --disks id="/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/vm-name_DataDisk_1" \
    --subnet-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.Network/virtualNetworks/myvnet/subnets/mysubnet" \
    --tags key="value" --resource-group "myResourceGroup" 
```
##### Delete #####
```
az disk-pool delete --name "myDiskPool" --resource-group "myResourceGroup"
```
#### disk-pool iscsi-target ####
##### Create #####
```
az disk-pool iscsi-target create --disk-pool-name "myDiskPool" --name "myIscsiTarget" \
    --target-iqn "iqn.2005-03.org.iscsi:server1" \
    --tpgs "[{\\"acls\\":[{\\"credentials\\":{\\"password\\":\\"some_pa$$word\\",\\"username\\":\\"some_username\\"},\\"initiatorIqn\\":\\"iqn.2005-03.org.iscsi:client\\",\\"mappedLuns\\":[\\"lun0\\"]}],\\"attributes\\":{\\"authentication\\":true,\\"prodModeWriteProtect\\":false},\\"luns\\":[{\\"name\\":\\"lun0\\",\\"managedDiskAzureResourceId\\":\\"/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/vm-name_DataDisk_1\\"}]}]" \
    --resource-group "myResourceGroup" 

az disk-pool iscsi-target wait --created --name "myIscsiTarget" --resource-group "myResourceGroup"
```
##### Show #####
```
az disk-pool iscsi-target show --disk-pool-name "myDiskPool" --name "myIscsiTarget" --resource-group "myResourceGroup"
```
##### List #####
```
az disk-pool iscsi-target list --disk-pool-name "myDiskPool" --resource-group "myResourceGroup"
```
##### Delete #####
```
az disk-pool iscsi-target delete --disk-pool-name "myDiskPool" --name "myIscsiTarget" \
    --resource-group "myResourceGroup" 
```