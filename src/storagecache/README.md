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
az storagecache asc-operation show --operation-id "testoperationid" --location "westus"
```
#### storagecache ####
##### Create #####
```
az storagecache create --location "westus" --cache-size-gb 3072 --cache-net-bios-name "contosoSmb" \
    --cache-active-directory-settings-credentials password="<password>" username="consotoAdmin" \
    --domain-name "contosoAd.contoso.local" --domain-net-bios-name "contosoAd" --primary-dns-ip-address "192.0.2.10" \
    --secondary-dns-ip-address "192.0.2.11" \
    --credentials bind-dn="cn=ldapadmin,dc=contosoad,dc=contoso,dc=local" bind-password="<bindPassword>" \
    --extended-groups true --ldap-base-dn "dc=contosoad,dc=contoso,dc=local" --ldap-server "192.0.2.12" \
    --username-source "LDAP" --key-url "https://keyvault-cmk.vault.azure.net/keys/key2047/test" \
    --id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/scgroup/providers/Microsoft.KeyVault/vaults/keyvault-cmk" \
    --access-policies name="default" access-rules={"access":"rw","rootSquash":false,"scope":"default","submountAccess":true,"suid":false} \
    --subnet "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/scgroup/providers/Microsoft.Network/virtualNetworks/scvnet/subnets/sub1" \
    --name "Standard_2G" --tags Dept="Contoso" --cache-name "sc1" --resource-group "scgroup" 
```
##### Create #####
```
az storagecache create --location "westus" --cache-size-gb 3072 \
    --credentials bind-dn="cn=ldapadmin,dc=contosoad,dc=contoso,dc=local" bind-password="<bindPassword>" \
    --extended-groups true --ldap-base-dn "dc=contosoad,dc=contoso,dc=local" --ldap-server "192.0.2.12" \
    --username-source "LDAP" --key-url "https://keyvault-cmk.vault.azure.net/keys/key2048/test" \
    --id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/scgroup/providers/Microsoft.KeyVault/vaults/keyvault-cmk" \
    --access-policies name="default" access-rules={"access":"rw","rootSquash":false,"scope":"default","submountAccess":true,"suid":false} \
    --subnet "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/scgroup/providers/Microsoft.Network/virtualNetworks/scvnet/subnets/sub1" \
    --name "Standard_2G" --tags Dept="Contoso" --cache-name "sc1" --resource-group "scgroup" 
```
##### List #####
```
az storagecache list --resource-group "scgroup"
```
##### Show #####
```
az storagecache show --cache-name "sc1" --resource-group "scgroup"
```
##### Update #####
```
az storagecache update --location "westus" --cache-size-gb 3072 --cache-net-bios-name "contosoSmb" \
    --domain-name "contosoAd.contoso.local" --domain-net-bios-name "contosoAd" --primary-dns-ip-address "192.0.2.10" \
    --secondary-dns-ip-address "192.0.2.11" --extended-groups true --username-source "AD" \
    --network-settings dns-search-domain="contoso.com" dns-servers="10.1.22.33" dns-servers="10.1.12.33" mtu=1500 ntp-server="time.contoso.com" \
    --access-policies name="default" access-rules={"access":"rw","rootSquash":false,"scope":"default","submountAccess":true,"suid":false} \
    --access-policies name="restrictive" access-rules={"access":"rw","filter":"10.99.3.145","rootSquash":false,"scope":"host","submountAccess":true,"suid":true} access-rules={"access":"rw","filter":"10.99.1.0/24","rootSquash":false,"scope":"network","submountAccess":true,"suid":true} access-rules={"access":"no","anonymousGID":"65534","anonymousUID":"65534","rootSquash":true,"scope":"default","submountAccess":true,"suid":false} \
    --subnet "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/scgroup/providers/Microsoft.Network/virtualNetworks/scvnet/subnets/sub1" \
    --name "Standard_2G" --tags Dept="Contoso" --cache-name "sc1" --resource-group "scgroup" 
```
##### Update #####
```
az storagecache update --location "westus" --cache-size-gb 3072 \
    --credentials bind-dn="cn=ldapadmin,dc=contosoad,dc=contoso,dc=local" bind-password="<bindPassword>" \
    --extended-groups true --ldap-base-dn "dc=contosoad,dc=contoso,dc=local" --ldap-server "192.0.2.12" \
    --username-source "LDAP" \
    --network-settings dns-search-domain="contoso.com" dns-servers="10.1.22.33" dns-servers="10.1.12.33" mtu=1500 ntp-server="time.contoso.com" \
    --access-policies name="default" access-rules={"access":"rw","rootSquash":false,"scope":"default","submountAccess":true,"suid":false} \
    --access-policies name="restrictive" access-rules={"access":"rw","filter":"10.99.3.145","rootSquash":false,"scope":"host","submountAccess":true,"suid":true} access-rules={"access":"rw","filter":"10.99.1.0/24","rootSquash":false,"scope":"network","submountAccess":true,"suid":true} access-rules={"access":"no","anonymousGID":"65534","anonymousUID":"65534","rootSquash":true,"scope":"default","submountAccess":true,"suid":false} \
    --subnet "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/scgroup/providers/Microsoft.Network/virtualNetworks/scvnet/subnets/sub1" \
    --name "Standard_2G" --tags Dept="Contoso" --cache-name "sc1" --resource-group "scgroup" 
```
##### Debug-info #####
```
az storagecache debug-info --cache-name "sc" --resource-group "scgroup"
```
##### Flush #####
```
az storagecache flush --cache-name "sc" --resource-group "scgroup"
```
##### Start #####
```
az storagecache start --cache-name "sc" --resource-group "scgroup"
```
##### Stop #####
```
az storagecache stop --cache-name "sc" --resource-group "scgroup"
```
##### Upgrade-firmware #####
```
az storagecache upgrade-firmware --cache-name "sc1" --resource-group "scgroup"
```
##### Delete #####
```
az storagecache delete --cache-name "sc" --resource-group "scgroup"
```
#### storagecache storage-target ####
##### Create #####
```
az storagecache storage-target create --cache-name "sc1" --resource-group "scgroup" --name "st1" \
    --junctions namespace-path="/path/on/cache" nfs-access-policy="default" nfs-export="exp1" target-path="/path/on/exp1" \
    --junctions namespace-path="/path2/on/cache" nfs-access-policy="rootSquash" nfs-export="exp2" target-path="/path2/on/exp2" \
    --nfs3 target="10.0.44.44" usage-model="READ_HEAVY_INFREQ" --target-type "nfs3" 

az storagecache storage-target wait --created --resource-group "{rg}" --name "{myStorageTarget}"
```
##### Create #####
```
az storagecache storage-target create --cache-name "sc1" --resource-group "scgroup" --name "st1" \
    --blob-nfs target="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/scgroup/providers/Microsoft.Storage/storageAccounts/blofnfs/blobServices/default/containers/blobnfs" usage-model="WRITE_WORKLOAD_15" \
    --junctions namespace-path="/blobnfs" --target-type "blobNfs" 

az storagecache storage-target wait --created --resource-group "{rg}" --name "{myStorageTarget}"
```
##### Create #####
```
az storagecache storage-target create --cache-name "sc1" --resource-group "scgroup" --name "st1" \
    --nfs3 target="10.0.44.44" usage-model="READ_HEAVY_INFREQ" --target-type "nfs3" 

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
##### Dns-refresh #####
```
az storagecache storage-target dns-refresh --cache-name "sc" --resource-group "scgroup" --name "st1"
```
##### Delete #####
```
az storagecache storage-target delete --cache-name "sc1" --resource-group "scgroup" --name "st1"
```