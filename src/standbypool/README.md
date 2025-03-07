# Azure CLI Standbypool Extension #

This is an extension to Azure CLI to manage Standbypool resources.

## How to use ##

Install standby virtual machine pool extension using ths blow CLI command
```
az extension add --name standby-vm-pool
```

Install standby container group pool extension using ths blow CLI command
```
az extension add --name standby-container-group-pool
```

### Included features ###

#### standby-vm-pool usage ####

##### Create #####

```
az standby-vm-pool create \
--subscription 461fa159-654a-415f-853a-40b801021944 \
--resource-group myrg \
--name mypool \
--max-ready-capacity 20 \
--vm-state Running \
--vmss-id /subscriptions/461fa159-654a-415f-853a-40b801021944/resourceGroups/myrg/providers/Microsoft.Compute/virtualMachineScaleSets/myvmss \
--location eastus \
```

##### Update #####

Update max ready capacity
```
az standby-vm-pool update \
--subscription  461fa159-654a-415f-853a-40b801021944 \
--resource-group myrg \
--name mypool \
--max-ready-capacity 3 \
```

Update vm state
```
az standby-vm-pool update \
--subscription 461fa159-654a-415f-853a-40b801021944 \
--resource-group myrg \
--name mypool \
--vm-state Deallocate \
```

Update vmssId
```
az standby-vm-pool update \
--subscription 461fa159-654a-415f-853a-40b801021944 \
--resource-group myrg \
--name mypool \
--vmss-id /subscriptions/461fa159-654a-415f-853a-40b801021944/resourceGroups/myrg/providers/Microsoft.Compute/virtualMachineScaleSets/testvmss \

```

##### show #####

```
az standby-vm-pool show --subscription 461fa159-654a-415f-853a-40b801021944 --resource-group myrg --name mypool
```

##### List #####
List by subscription Id

```
az standby-vm-pool list --subscription 461fa159-654a-415f-853a-40b801021944
```

List by resource group
```
az standby-vm-pool list --subscription 461fa159-654a-415f-853a-40b801021944 --resource-group myrg
```

##### Delete #####

```
az standby-vm-pool delete --subscription 461fa159-654a-415f-853a-40b801021944 --resource-group myrg --name mypool
```

##### List VMs in StandbyPool #####

```
az standby-vm-pool vm list --subscription 461fa159-654a-415f-853a-40b801021944 --resource-group myrg --name mypool
```

#### standby-container-group-pool usage ####

##### Create #####

```
az standby-container-group-pool create \
--resource-group myrg \
--name mypool \
--subscription 461fa159-654a-415f-853a-40b801021944 \
--container-profile-id /subscriptions/461fa159-654a-415f-853a-40b801021944/resourceGroups/myrg/providers/Microsoft.ContainerInstance/containerGroupProfiles/mycg \
--profile-revision 1  \
--subnet-ids [0].id=/subscriptions/461fa159-654a-415f-853a-40b801021944/resourceGroups/ru-cli-test-standbypool/providers/Microsoft.Network/virtualNetworks/ru-cli-test-standbypool-vnet/subnets/testSubnet \
--refill-policy always \
--max-ready-capacity 1 \
--location eastus
```

##### show #####

```
az standby-container-group-pool show --subscription 461fa159-654a-415f-853a-40b801021944 --resource-group myrg --name mypool
```

##### List #####
List by subscription Id

```
az standby-container-group-pool list --subscription 461fa159-654a-415f-853a-40b801021944
```

List by resource group
```
az standby-container-pool list --subscription 461fa159-654a-415f-853a-40b801021944 --resource-group myrg
```

##### Delete #####

```
az standby-container-group-pool delete --name mypool --subscription 461fa159-654a-415f-853a-40b801021944 --resource-group
```