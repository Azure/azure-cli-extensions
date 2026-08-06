# Azure CLI Interconnect Extension #
This is an extension to Azure CLI to manage Interconnect resources.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name interconnect
```

### Included Features
### Manage interconnect groups ###

Create an interconnect group:

```
az interconnect-group create --resource-group rg1 --interconnect-group-name test-ig
```

Show an interconnect group:

```
az interconnect-group show --resource-group rg1 --interconnect-group-name test-ig
```

List interconnect groups (in a subscription, or scoped to a resource group):

```
az interconnect-group list
az interconnect-group list --resource-group rg1
```

Update an interconnect group:

```
az interconnect-group update --resource-group rg1 --interconnect-group-name test-ig
```

Delete an interconnect group:

```
az interconnect-group delete --resource-group rg1 --interconnect-group-name test-ig
```

Get node availability for all subgroups in an interconnect group:

```
az interconnect-group get-node-availability --resource-group rg1 --interconnect-group-name test-ig
```

### Manage subgroups ###

List subgroups in an interconnect group:

```
az interconnect-group subgroup list --resource-group rg1 --interconnect-group-name test-ig
```

Show a subgroup:

```
az interconnect-group subgroup show --resource-group rg1 --interconnect-group-name test-ig --subgroup-name subgroup0
```

#### Interconnect Block:
##### Creates a new Interconnect Block resource.
```
az interconnect-block create --name training-icb-001 --resource-group ai-training-rg \
    --location eastus --zones 1 --sku-name Standard_ND128isr_GB300_v6 --sku-capacity 36 \
    --interconnect-group-id \
    "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/network-\
    rg/providers/Microsoft.Network/interconnectGroups/training-ig" --tags Environment=Production\
    Workload=AI-Training CostCenter=ML-Engineering
```

##### Delete an Interconnect Block.
```
az interconnect-block delete --name training-icb-001 --resource-group ai-training-rg
```

##### Delete without confirmation
```
az interconnect-block delete --name training-icb-001 --resource-group ai-training-rg --yes
```

##### List all in subscription
```
az interconnect-block list
```

##### List by resource group
```
az interconnect-block list --resource-group ai-training-rg
```

##### List and filter by capacity
```
az interconnect-block list --resource-group ai-training-rg --query "[?sku.capacity>=36]"
```

##### Get basic information
```
az interconnect-block show --name training-icb-001 --resource-group ai-training-rg
```

##### Get with instance view (includes runtime details)
```
az interconnect-block show --name training-icb-001 --resource-group ai-training-rg --expand \
    instanceView
```

##### Update scale capacity
```
az interconnect-block update --name training-icb-001 --resource-group ai-training-rg --sku-\
    capacity 54
```

##### Update tags
```
az interconnect-block update --name training-icb-001 --resource-group ai-training-rg --tags \
    Environment=Production Capacity=54-nodes LastScaled=$(date +%Y-%m-%d)
```

##### Update scale with no-wait
```
az interconnect-block update --name training-icb-001 --resource-group ai-training-rg --sku-\
    capacity 72 --no-wait
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.
