Microsoft Azure CLI 'hardware-security-modules' Extension
==========================================

### How to use ###
Install this extension using the below CLI command
```
az extension add --name hardware-security-modules
```

### Getting Help

To see examples of commands and parameters details of commands or command groups, one should run the command of interest with a -h

Examples:
```
az dedicated-hsm create -h

az dedicated-hsm list -h

az dedicated-hsm update -h
```


##### Creating a dedicated hardware security module

To create a dedicate hardware security module, one must have already setup all of the following in Azure:

- A VNET
- A subnet for the HSMs in the specified VNET (delegation must be set to HSM)
- A subnet for the virtual network gateway 
- A public IP address for the gateway 

More instructions can be found at: https://docs.microsoft.com/en-us/azure/dedicated-hsm/

An example of CLI commands that would setup a very basic network that manages a dedicated HSM via a VM would be:

```
az feature register --namespace Microsoft.HardwareSecurityModules --name AzureDedicatedHSM

az feature register --namespace Microsoft.Network --name AllowBaremetalServers

az network vnet create --name vn -g rg1 --subnet-name default

az vm create -g rg1 --name vm1 --image UbuntuLTS

az network vnet subnet create --vnet-name vn -n GatewaySubnet -g rg1 --address-prefix 10.0.5.0/24

az network vnet subnet create --vnet-name vn -g rg1 --name hsm --address-prefixes 10.0.2.0/24 --delegations Microsoft.HardwareSecurityModules/dedicatedHSMs

az network public-ip create -n ERGWVIP -g rg1 --allocation-method Dynamic

az network vnet-gateway create -n ERGW -l japaneast --public-ip-address ERGWVIP -g rg1 --vnet vn --sku standard --gateway-type ExpressRoute

```
