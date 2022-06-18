# Azure CLI diskpool Extension #
This is the extension for diskpool

### How to use ###
Install this extension using the below CLI command
```
az extension add --name diskpool
```

### Included Features ###
#### disk-pool ####
##### Create #####
```
az disk-pool create --location "westus" --availability-zones "1" \
    --disks "/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/vm-name_DataDisk_0" \
    --disks "/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/vm-name_DataDisk_1" \
    --subnet-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.Network/virtualNetworks/myvnet/subnets/mysubnet" \
    --sku name="Basic_V1" tier="Basic" --tags key="value" --name "myDiskPool" --resource-group "myResourceGroup" 

az disk-pool wait --created --name "{myDiskPool}" --resource-group "{rg}"
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
az disk-pool update --name "myDiskPool" \
    --disks "/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/vm-name_DataDisk_0" \
    --disks "/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/vm-name_DataDisk_1" \
    --sku name="Basic_B1" tier="Basic" --tags key="value" --resource-group "myResourceGroup" 
```
##### List-outbound-network-dependency-endpoint #####
```
az disk-pool list-outbound-network-dependency-endpoint --name "SampleAse" --resource-group "Sample-WestUSResourceGroup"
```
##### Start #####
```
az disk-pool start --name "myDiskPool" --resource-group "myResourceGroup"
```
##### Stop #####
```
az disk-pool stop --name "myDiskPool" --resource-group "myResourceGroup"
```
##### Upgrade #####
```
az disk-pool upgrade --name "myDiskPool" --resource-group "myResourceGroup"
```
##### Delete #####
```
az disk-pool delete --name "myDiskPool" --resource-group "myResourceGroup"
```
#### disk-pool ####
##### List-skus #####
```
az disk-pool list-skus --location "eastus"
```
##### List-zones #####
```
az disk-pool list-zones --location "eastus"
```
#### disk-pool iscsi-target ####
##### Create #####
```
az disk-pool iscsi-target create --disk-pool-name "myDiskPool" --acl-mode "Dynamic" \
    --luns name="lun0" managed-disk-azure-resource-id="/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/vm-name_DataDisk_1" \
    --target-iqn "iqn.2005-03.org.iscsi:server1" --name "myIscsiTarget" --resource-group "myResourceGroup" 

az disk-pool iscsi-target wait --created --disk-pool-name "{myDiskPool}" --name "{myIscsiTarget}" \
    --resource-group "{rg}" 
```
##### Show #####
```
az disk-pool iscsi-target show --disk-pool-name "myDiskPool" --name "myIscsiTarget" --resource-group "myResourceGroup"
```
##### List #####
```
az disk-pool iscsi-target list --disk-pool-name "myDiskPool" --resource-group "myResourceGroup"
```
##### Update #####
```
az disk-pool iscsi-target update --disk-pool-name "myDiskPool" --name "myIscsiTarget" \
    --luns name="lun0" managed-disk-azure-resource-id="/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/vm-name_DataDisk_1" \
    --static-acls initiator-iqn="iqn.2005-03.org.iscsi:client" mapped-luns="lun0" --resource-group "myResourceGroup" 
```
##### Delete #####
```
az disk-pool iscsi-target delete --disk-pool-name "myDiskPool" --name "myIscsiTarget" \
    --resource-group "myResourceGroup" 
```