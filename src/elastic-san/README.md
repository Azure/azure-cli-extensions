# Azure CLI ElasticSan Extension #
This is an extension to Azure CLI to manage ElasticSan resources.

## How to use ##

## Elastic San
### Create an Elastic SAN.
`az elastic-san create -n {san_name} -g {rg} --tags "{key1810:aaaa}" -l southcentralusstg --base-size-tib 23 --extended-capacity-size-tib 14 --sku "{name:Premium_LRS,tier:Premium}"`
### Delete an Elastic SAN.
`az elastic-san delete -g {rg} -n {san_name}`
### Get a list of Elastic SANs in a subscription.
`az elastic-san list -g {rg}`
### Get a list of Elastic SAN skus.
`az elastic-san list-sku`
### Get an Elastic SAN.
`az elastic-san show -g {rg} -n {san_name}`
### Update an Elastic SAN.
`az elastic-san update -n {san_name} -g {rg} --tags "{key1710:bbbb}" --base-size-tib 25 --extended-capacity-size-tib 15`

## Volume Group
### Create a Volume Group.
`az elastic-san volume-group create -e {san_name} -n {vg_name} -g {rg} --tags "{key1910:bbbb}" --encryption EncryptionAtRestWithPlatformKey --protocol-type Iscsi --network-acls "{virtual-network-rules:["{id:{subnet_id},action:Allow}"]}"`
### Delete a Volume Group.
`az elastic-san volume-group delete -g {rg} -e {san_name} -n {vg_name}`
### List Volume Groups.
`az elastic-san volume-group list -g {rg} -e {san_name}`
### Get a Volume Group.
`az elastic-san volume-group show -g {rg} -e {san_name} -n {vg_name}`
### Update a Volume Group.
`elastic-san volume-group update -e {san_name} -n {vg_name} -g {rg} --tags "{key2011:cccc}" --protocol-type None --network-acls "{virtual-network-rules:["{id:{subnet_id_2},action:Allow}"]}"`

## Volume
### Create a Volume.
`az elastic-san volume create -g {rg} -e {san_name} -v {vg_name} -n {volume_name} --size-gib 2`
### Delete a Volume.
`az elastic-san volume delete -g {rg} -e {san_name} -v {vg_name} -n {volume_name}`
### List Volumes in a Volume Group.
`az elastic-san volume list -g {rg} -e {san_name} -v {vg_name}`
### Get a Volume.
`az elastic-san volume show -g {rg} -e {san_name} -v {vg_name} -n {volume_name}`
### Update a Volume.
`az elastic-san volume update -g {rg} -e {san_name} -v {vg_name} -n {volume_name} --size-gib 3`

## Snapshot case
### Create an ElasticSAN
`az elastic-san create -n "san_name" -g "rg" --tags '{key1810:aaaa}' -l eastus2euap --base-size-tib 23 --extended-capacity-size-tib 14 --sku '{name:Premium_LRS,tier:Premium}'`
### Create Vnet        
`az network vnet create -g "rg" -n "vnet_name" --address-prefix 10.0.0.0/16`
### Get subnet id
`subnet_id=$(az network vnet subnet create -g "rg" --vnet-name "vnet_name" --name "subnet_name" --address-prefixes 10.0.0.0/24 --service-endpoints Microsoft.Storage --query "id" -o tsv)`
### Create volume group
`az elastic-san volume-group create -e "san_name" -n "vg_name" -g "rg" --encryption EncryptionAtRestWithPlatformKey --protocol-type Iscsi --network-acls '{virtual-network-rules:[{id:"subnet_id",action:Allow}]}'`
### Create volume
`az elastic-san volume create -g "rg" -e "san_name" -v "vg_name" -n "volume_name" --size-gib 2`
### Get volume id
`volume_id=$(az elastic-san volume show -g "rg" -e "san_name" -v "vg_name" -n "volume_name" --query "id" -o tsv)`
### Create a snapshot
`az elastic-san volume snapshot create -g "rg" -e "san_name" -v "vg_name" -n "snapshot_name" --creation-data '{source-id:"volume_id"}'`
### Get snapshot_id 
`snapshot_id=$(az elastic-san volume snapshot show -g "rg" -e "san_name" -v "vg_name" -n "snapshot_name" --query "id" -o tsv)`
### Create volume from a snapshot
`az elastic-san volume create -g "rg" -e "san_name" -v "vg_name" -n "volume_name_2" --size-gib 2 --creation-data '{source-id:"snapshot_id",create-source:VolumeSnapshot}'`
### Delete volume with the snapshot
`az elastic-san volume delete -g "rg" -e "san_name" -v "vg_name" -n "volume_name" -y --x-ms-delete-snapshots true --x-ms-force-delete true`

## Customer Managed Key System Assigned Identity scenario
#### Create an ElasticSAN
`az elastic-san create -n "san_name" -g "rg" --tags '{key1810:aaaa}' -l eastus2euap --base-size-tib 23 --extended-capacity-size-tib 14 --sku '{name:Premium_LRS,tier:Premium}'`
### 1. Create a key vault with a key in it. Key type should be RSA
#### Create keyvault
`az keyvault create --name "kv_name" --resource-group "rg" --location eastus2 --enable-purge-protection --retention-days 7`
#### Get vault_url
`vault_uri=$(az keyvault show --name "kv_name" --resource-group "rg" --query "properties.vaultUri" -o tsv)`
#### Set key policy
`az keyvault set-policy -n "kv_name" --object-id "logged_in_user" --key-permissions backup create delete get import get list update restore`
#### Create key
`az keyvault key create --vault-name "kv_name" -n "key_name" --protection software`
### 2. PUT a volume group with PMK and a system assigned identity with it
#### Get the system identity's principalId from the response of PUT volume group request.
`vg_identity_principal_id=$(az elastic-san volume-group create -e "san_name" -n "vg_name" -g "rg" --encryption EncryptionAtRestWithPlatformKey --protocol-type Iscsi --identity '{type:SystemAssigned}' --query "identity.principalId" -o tsv)`
### 3. Grant access to  the system assigned identity to the key vault created in step1
#### (key permissions: Get, Unwrap Key, Wrap Key)
`az keyvault set-policy -n "kv_name" --object-id "vg_identity_principal_id" --key-permissions backup create delete get import get list update restore`
### 4. PATCH the volume group with the key created in step 1
`az elastic-san volume-group update -e "san_name" -n "vg_name" -g "rg" --encryption EncryptionAtRestWithCustomerManagedKey --encryption-properties '{key-vault-properties:{key-name:"key_name",key-vault-uri:"vault_uri"}}'`

## Customer Managed Key User Assigned Identity scenario
#### Create an ElasticSAN
`az elastic-san create -n "san_name" -g "rg" --tags '{key1810:aaaa}' -l eastus2euap --base-size-tib 23 --extended-capacity-size-tib 14 --sku '{name:Premium_LRS,tier:Premium}'`
### 1. Create a user assigned identity and grant it the access to the key vault
#### create a user assigned identity
`uai=$(az identity create -g "rg" -n "user_assigned_identity_name" -o tsv)`
`uai_principal_id=$(uai["principalId"])`
`uai_id=$(uai["id"])`
`uai_client_id=$(uai["clientId"])`
#### create a keyvault
`az keyvault create --name "kv_name" --resource-group "rg" --location eastus2 --enable-purge-protection --retention-days 7`
`vault_uri=$(az keyvault show --name "kv_name" --resource-group "rg" --query "properties.vaultUri" -o tsv)`
#### set policy for key permission
`az keyvault set-policy -n "kv_name" --object-id "uai_principal_id" --key-permissions get wrapkey unwrapkey`
#### create key
`az keyvault key create --vault-name "kv_name" -n "key_name" --protection software`
### 2. PUT a volume group with CMK
`az elastic-san volume-group create -e "san_name" -n "vg_name" -g "rg" --encryption EncryptionAtRestWithCustomerManagedKey --protocol-type Iscsi --identity '{type:UserAssigned,user-assigned-identity:"uai_id"}' --encryption-properties '{key-vault-properties:{key-name:"key_name",key-vault-uri:"vault_uri"},identity:{user-assigned-identity:"uai_id"}}'`
`az elastic-san volume create -g "rg" -e "san_name" -v "vg_name" -n "volume_name" --size-gib 2`     
### 3. Change to another user assigned identity
`uai_2=$(az identity create -g "rg" -n "user_assigned_identity_name_2"  -o tsv)`
`uai_2_principal_id=$(uai_2["principalId"])`
`uai_2_id=$(uai_2["id"])`
`uai_2_client_id=$(uai_2["clientId"])`
`az keyvault set-policy -n "kv_name" --object-id "uai_2_principal_id" --key-permissions get wrapkey unwrapkey`
`az elastic-san volume-group update -e "san_name" -n "vg_name" -g "rg" --identity '{type:UserAssigned,user-assigned-identity:"uai_2_id"}' --encryption-properties '{key-vault-properties:{key-name:"key_name",key-vault-uri:"vault_uri"},identity:{user-assigned-identity:"uai_2_id"}}'` 
### 4. Change to pmk
`az elastic-san volume-group update -e "san_name" -n "vg_name" -g "rg" --encryption EncryptionAtRestWithPlatformKey`
### 5. Change to system assigned identity
`az elastic-san volume-group update -e "san_name" -n "vg_name" -g "rg" --identity '{type:SystemAssigned}'`
