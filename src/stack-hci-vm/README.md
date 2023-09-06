# Azure CLI azurestackhci Extension #
This is the extension for azurestackhci

### How to use ###
Install this extension using the below CLI command
```
az extension add --name azurestackhci
```

### Included Features ###
#### azurestackhci galleryimage ####
##### Create #####
```
az azurestackhci galleryimage create \
    --extended-location name="/subscriptions/a95612cb-f1fa-4daa-a4fd-272844fa512c/resourceGroups/dogfoodarc/providers/Microsoft.ExtendedLocation/customLocations/dogfood-location" type="CustomLocation" \
    --location "West US2" --container-name "Default_Container" --image-path "C:\\\\test.vhdx" \
    --galleryimages-name "test-gallery-image" --resource-group "test-rg" 
```
##### List #####
```
az azurestackhci galleryimage list --resource-group "test-rg"
```
##### Update #####
```
az azurestackhci galleryimage update --tags additionalProperties="sample" --galleryimages-name "test-gallery-image" \
    --resource-group "test-rg" 
```
##### Retrieve #####
```
az azurestackhci galleryimage retrieve --galleryimages-name "test-gallery-image" --resource-group "test-rg"
```
##### Delete #####
```
az azurestackhci galleryimage delete --galleryimages-name "test-gallery-image" --resource-group "test-rg"
```
#### azurestackhci networkinterface ####
##### Create #####
```
az azurestackhci networkinterface create \
    --extended-location name="/subscriptions/a95612cb-f1fa-4daa-a4fd-272844fa512c/resourceGroups/dogfoodarc/providers/Microsoft.ExtendedLocation/customLocations/dogfood-location" type="CustomLocation" \
    --name "test-nic"
    --location "West US2" \
    --subnet-id" "test-vnet" --gateway "1.2.3.4" --ip-address "1.2.3.4"

OR

az azurestackhci networkinterface create \
    --extended-location name="/subscriptions/a95612cb-f1fa-4daa-a4fd-272844fa512c/resourceGroups/dogfoodarc/providers/Microsoft.ExtendedLocation/customLocations/dogfood-location" type="CustomLocation" \
    --location "West US2" \
    --ip-configurations "[{\"name\":\"ipconfig-sample\",\"properties\":{\"subnet\":{\"id\":\"test-vnet\"}, \"gateway\":\"1.2.3.4\", \"ip_address\":\"1.2.3.4\"}}]" \
    --networkinterfaces-name "test-nic"
```
##### List #####
```
az azurestackhci networkinterface list --resource-group "test-rg"
```
##### Update #####
```
az azurestackhci networkinterface update --tags additionalProperties="sample" --networkinterfaces-name "test-nic" \
    --resource-group "test-rg" 
```
##### Retrieve #####
```
az azurestackhci networkinterface retrieve --networkinterfaces-name "test-nic" --resource-group "test-rg"
```
##### Delete #####
```
az azurestackhci networkinterface delete --networkinterfaces-name "test-nic" --resource-group "test-rg"
```
#### azurestackhci virtualharddisk ####
##### Create #####
```
az azurestackhci virtualharddisk create --resource-group "test-rg" \
    --extended-location name="/subscriptions/a95612cb-f1fa-4daa-a4fd-272844fa512c/resourceGroups/dogfoodarc/providers/Microsoft.ExtendedLocation/customLocations/dogfood-location" type="CustomLocation" \
    --location "West US2" --disk-size-gb 32 --virtualharddisks-name "test-vhd" 
```
##### List #####
```
az azurestackhci virtualharddisk list --resource-group "test-rg"
```
##### Update #####
```
az azurestackhci virtualharddisk update --resource-group "test-rg" --tags additionalProperties="sample" \
    --virtualharddisks-name "test-vhd" 
```
##### Retrieve #####
```
az azurestackhci virtualharddisk retrieve --resource-group "test-rg" --virtualharddisks-name "test-vhd"
```
##### Delete #####
```
az azurestackhci virtualharddisk delete --resource-group "test-rg" --virtualharddisks-name "test-vhd"
```
#### azurestackhci virtualmachine ####
##### Create #####
```
az azurestackhci virtualmachine create --resource-group "test-rg" \
    --extended-location name="/subscriptions/a95612cb-f1fa-4daa-a4fd-272844fa512c/resourceGroups/dogfoodarc/providers/Microsoft.ExtendedLocation/customLocations/dogfood-location" type="CustomLocation" \
    --location "West US2" --hardware-profile vm-size="Default" maximum_memory_mb=1 minimum_memory_mb=1 target_memory_buffer=100  --network-profile network-interfaces={"id":"test-nic"} \
    --os-profile "{\\"adminPassword\\":\\"password\\",\\"adminUsername\\":\\"localadmin\\",\\"computerName\\":\\"luamaster\\"}" \
    --storage-profile "{\\"imageReference\\":{\\"id\\":\\"test-gallery-image\\"}}" --virtualmachines-name "test-vm" 
    ----linux-configuration ssh_keys='{\"key_data\": \"ssh_public_key\"}' ssh_keys='{\"path\": \"/path/to/id_rsa.pub\"}'
```
##### List #####
```
az azurestackhci virtualmachine list --resource-group "test-rg"
```
##### Update #####
```
az azurestackhci virtualmachine update --resource-group "test-rg" --tags additionalProperties="sample" \
    --virtualmachines-name "test-vm" 
```
##### Retrieve #####
```
az azurestackhci virtualmachine retrieve --resource-group "test-rg" --virtualmachines-name "test-vm"
```
##### Start #####
```
az azurestackhci virtualmachine start --resource-group "test-rg" --virtualmachines-name "test-vm"
```
##### Stop #####
```
az azurestackhci virtualmachine stop --resource-group "test-rg" --virtualmachines-name "test-vm"
```
##### Delete #####
```
az azurestackhci virtualmachine delete --resource-group "test-rg" --virtualmachines-name "test-vm"
```
##### Add Vnic #####
```
az azurestackhci virtualmachine vnic add --resource-group "test-rg" --virtualmachines-name "test-vm" --vnic-name "test-vnic"
```
##### Remove Vnic #####
```
az azurestackhci virtualmachine vnic remove --resource-group "test-rg" --virtualmachines-name "test-vm" --vnic-name "test-vnic"
```
#### azurestackhci virtualnetwork ####
##### Create #####
```
az azurestackhci virtualnetwork create --resource-group "test-rg" \
    --extended-location name="/subscriptions/a95612cb-f1fa-4daa-a4fd-272844fa512c/resourceGroups/dogfoodarc/providers/Microsoft.ExtendedLocation/customLocations/dogfood-location" type="CustomLocation" \
    --location "West US2" --network-type "Transparent" ---name "test-vnet" --address-prefix "10.0.0.0/16" \
    --ip-allocation-method "Static" --ip-pool-type "Static" --ip-pool-start "10.0.0.0" ip-pool-end "10.0.0.16" --vlan 10"
```
##### List #####
```
az azurestackhci virtualnetwork list --resource-group "test-rg"
```
##### Update #####
```
az azurestackhci virtualnetwork update --resource-group "test-rg" --tags additionalProperties="sample" \
    --virtualnetworks-name "test-vnet" 
```
##### Retrieve #####
```
az azurestackhci virtualnetwork retrieve --resource-group "test-rg" --virtualnetworks-name "test-vnet"
```
##### Delete #####
```
az azurestackhci virtualnetwork delete --resource-group "test-rg" --virtualnetworks-name "test-vnet"
```
#### azurestackhci storagecontainer ####
##### Create #####
```
az azurestackhci storagecontainer create --resource-group "test-rg" \
    --extended-location name="/subscriptions/a95612cb-f1fa-4daa-a4fd-272844fa512c/resourceGroups/dogfoodarc/providers/Microsoft.ExtendedLocation/customLocations/dogfood-location" type="CustomLocation" \
    --location "West US2" --path "C:\\\\container_storage" --storagecontainers-name "Default_Container" 
```
##### List #####
```
az azurestackhci storagecontainer list --resource-group "test-rg"
```
##### Update #####
```
az azurestackhci storagecontainer update --resource-group "test-rg" --tags additionalProperties="sample" \
    --storagecontainers-name "Default_Container" 
```
##### Retrieve #####
```
az azurestackhci storagecontainer retrieve --resource-group "test-rg" --storagecontainers-name "Default_Container"
```
##### Delete #####
```
az azurestackhci storagecontainer delete --resource-group "test-rg" --storagecontainers-name "Default_Container"
```
#### azurestackhci cluster ####
##### Create #####
```
az azurestackhci cluster create --location "East US" --aad-client-id "24a6e53d-04e5-44d2-b7cc-1b732a847dfc" \
    --aad-tenant-id "7e589cc1-a8b6-4dff-91bd-5ec0fa18db94" --name "myCluster" --resource-group "test-rg" 
```
##### Show #####
```
az azurestackhci cluster show --name "myCluster" --resource-group "test-rg"
```
##### List #####
```
az azurestackhci cluster list --resource-group "test-rg"
```
##### Update #####
```
az azurestackhci cluster update --tags tag1="value1" tag2="value2" --name "myCluster" --resource-group "test-rg"
```
##### Delete #####
```
az azurestackhci cluster delete --name "myCluster" --resource-group "test-rg"
```