# Azure CLI Bastion Extension #
This is an extension to Azure CLI to manage Bastion resources.

## How to use ##
Manage Azure Bastion host machines.

### Create a Azure Bastion host machine
```commandline
az network bastion create --location westus2 --name MyBastionHost --public-ip-address MyPublicIpAddress --resource-group MyResourceGroup --vnet-name MyVnet
```

### Delete a Azure Bastion host machine
```commandline
az network bastion delete --name MyBastionHost --resource-group MyResourceGroup
```

### List all Azure Bastion host machines
```commandline
az network bastion list -g MyResourceGroup
```

### Show a Azure Bastion host machine
```commandline
az network bastion show --name MyBastionHost --resource-group MyResourceGroup
```

### Update a Azure Bastion host machine
```commandline
az network bastion update --name MyBastionHost --resource-group MyResourceGroup --enable-tunneling
```
