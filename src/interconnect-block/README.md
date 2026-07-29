# Azure CLI InterconnectBlock Extension #
This is an extension to Azure CLI to manage InterconnectBlock resources.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name interconnect-block
```

### Included Features
#### Interconnect Block:
*Examples:*

##### Creates a new InterconnectBlock resource.
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
