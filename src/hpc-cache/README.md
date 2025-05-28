Microsoft Azure CLI 'hpc-cache' Extension
==========================================

### How to use ###
Install this extension using the below CLI command
```
az extension add --name hpc-cache
```

### Included Features
#### Create HPC cache 
*Examples:*
```
az hpc-cache create --resource-group "scgroup" --name "sc1" --location "eastus" \
    --cache-size-gb "3072" --subnet "/subscriptions/{subscription_id}/resourceGroups/{re \
    source_group}/providers/Microsoft.Network/virtualNetworks/{virtual_network_name}/sub \
    nets/{subnet_name}" --sku-name "Standard_2G"
```
#### Start/Stop HPC cache 
*Examples:*
```
az hpc-cache start --resource-group "scgroup" --name "sc1"
az hpc-cache stop --resource-group "scgroup" --name "sc1"
```
#### Add blob storage target in HPC cache 
*Examples:*
```
az hpc-cache blob-storage-target add --resource-group "scgroup" --cache-name "sc1" --name \
    "st1" --storage-account "/subscriptions/{subscription_id}/resourceGroups/{resource_group} \
    /providers/Microsoft.Storage/storageAccounts/{acount_name}" \
    --container-name "cn" --virtual-namespace-path "/test"
```
#### Add nfs storage target in HPC cache 
*Examples:*
```
az hpc-cache nfs-storage-target add --resource-group "scgroup" --cache-name "sc1" \
    --name "st1" --nfs3-target 10.7.0.24 --nfs3-usage-model WRITE_AROUND \
    --junction namespace-path="/nt2" nfs-export="/export/a" target-path="/1" \
    --junction namespace-path="/nt3" nfs-export="/export/b"
```
#### Remove storage target in HPC cache 
*Examples:*
```
az hpc-cache storage-target remove --resource-group "scgroup" \
    --cache-name "sc1" \
    --name "st1" 
```