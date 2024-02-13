# Azure CLI Bastion Extension #
This is an extension to Azure CLI to manage Bastion resources.

Documentation References: 

https://learn.microsoft.com/en-us/azure/bastion/connect-ip-address#connect-to-vm---native-client

https://learn.microsoft.com/en-us/azure/bastion/connect-native-client-windows#connect-IP

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

### RDP to VM/VMSS using Azure Bastion host machine
```commandline
az network bastion rdp --name MyBastionHost --resource-group MyResourceGroup --target-resource-id ResourceId
```

### SSH to VM/VMSS using Azure Bastion host machine
```commandline
az network bastion ssh --name MyBastionHost --resource-group MyResourceGroup --target-resource-id ResourceId --auth-type password
```

### RDP to Target IP address using Azure Bastion
```commandline
az network bastion rdp --name MyBastionHost --resource-group MyResourceGroup --target-ip-address 10.1.1.1
```

### SSH to Target IP address using Azure Bastion
```commandline
az network bastion ssh --name MyBastionHost --resource-group MyResourceGroup --target-ip-address 10.1.1.1 --auth-type password
```