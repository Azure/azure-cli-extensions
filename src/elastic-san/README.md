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
