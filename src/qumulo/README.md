# Azure CLI Qumulo Extension #
This is an extension to Azure CLI to manage Qumulo resources.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name qumulo
```

### Included Features ###
#### qumulo storage file-system ####
##### Create #####
```
az qumulo storage file-system create -n sys_name -g rg --admin-password testadmin --delegated-subnet-id subnet-id --initial-capacity 50 --marketplace-details "{offerId:qumulo-saas-mpp,planId:qumulo-on-azure-v1%%gmz7xq9ge3py%%P1M,publisherId:qumulo1584033880660}" --storage-sku Standard --user-details "{email:test@test.com}" --availability-zone 1

```

##### Delete #####
```
az qumulo storage file-system delete -g rg -n sys_name

```

##### List #####
```
az qumulo storage file-system list -g rg

```

##### Show #####
```
az qumulo storage file-system show -g rg -n sys_name

```
