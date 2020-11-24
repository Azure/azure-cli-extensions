# Azure CLI storagecache Extension #
This is the extension for storagecache

### How to use ###
Install this extension using the below CLI command
```
az extension add --name storagecache
```

### Included Features ###
#### storagecache sku ####
##### List #####
```
az storagecache sku list
```
#### storagecache usage-model ####
##### List #####
```
az storagecache usage-model list
```
#### storagecache asc-operation ####
##### Show #####
```
az storagecache asc-operation show --operation-id "testoperationid" --location "West US"
```
#### storagecache cache ####
##### Create #####
```
az storagecache cache create --location "westus" --cache-size-gb 3072 \
    --subnet "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/scgroup/providers/Microsoft.Network/virtualNetworks/scvnet/subnets/sub1" \
    --sku-name "Standard_2G" --tags "{\\"Dept\\":\\"ContosoAds\\"}" --cache-name "sc1" --resource-group "scgroup" 
```
##### Show #####
```
az storagecache cache show --cache-name "sc1" --resource-group "scgroup"
```
##### List #####
```
az storagecache cache list --resource-group "scgroup"
```
##### Update #####
```
az storagecache cache update --location "westus" --cache-size-gb 3072 \
    --subnet "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/scgroup/providers/Microsoft.Network/virtualNetworks/scvnet/subnets/sub1" \
    --sku-name "Standard_2G" --tags "{\\"Dept\\":\\"ContosoAds\\"}" --cache-name "sc1" --resource-group "scgroup" 
```
##### Flush #####
```
az storagecache cache flush --cache-name "sc" --resource-group "scgroup"
```
##### Start #####
```
az storagecache cache start --cache-name "sc" --resource-group "scgroup"
```
##### Stop #####
```
az storagecache cache stop --cache-name "sc" --resource-group "scgroup"
```
##### Upgrade-firmware #####
```
az storagecache cache upgrade-firmware --cache-name "sc1" --resource-group "scgroup"
```
##### Delete #####
```
az storagecache cache delete --cache-name "sc" --resource-group "scgroup"
```
#### storagecache storage-target ####
##### Create #####
```
az storagecache storage-target create --cache-name "sc1" --resource-group "scgroup" --name "st1" \
    --junctions namespace-path="/path/on/cache" nfs-export="exp1" target-path="/path/on/exp1" \
    --junctions namespace-path="/path2/on/cache" nfs-export="exp2" target-path="/path2/on/exp2" \
    --nfs3 target="10.0.44.44" usage-model="READ_HEAVY_INFREQ" 

az storagecache storage-target wait --created --resource-group "{rg}" --name "{myStorageTarget}"
```
##### Show #####
```
az storagecache storage-target show --cache-name "sc1" --resource-group "scgroup" --name "st1"
```
##### List #####
```
az storagecache storage-target list --cache-name "sc1" --resource-group "scgroup"
```
##### Delete #####
```
az storagecache storage-target delete --cache-name "sc1" --resource-group "scgroup" --name "st1"
```