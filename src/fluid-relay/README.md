# Azure CLI FluidRelay Extension #
This is an extension to Azure CLI to manage FluidRelay resources.

### How to use ###
```
az extension add --name fluid-relay
```

### Included Features
#### Server:
Manage a fluid relay server: [more info](https://docs.microsoft.com/en-us/azure/azure-fluid-relay/overview/overview)  
*Examples:*
```
az fluid-relay server create \
    -n TestFluidRelay \
    -l westus2 \
    -g MyResourceGroup \
    --sku standard \
    --tags category=sales \
    --identity type="SystemAssigned

az fluid-relay server create  \
    -n TestFluidRelay \
    -l westus2 \
    -g MyResourceGroup \
    --sku standard \
    --tags category=sales \
    --identity type="SystemAssigned, UserAssigned" \
    user-assigned-identities= \
    {"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MyResourceGroup/providers/ \
    Microsoft.ManagedIdentity/userAssignedIdentities/id1","/subscriptions/00000000-0000-0000-0000-000000000000/ \
    resourceGroups/MyResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/id2"}

az fluid-relay server update \
    -n MyFluidRelay \
    -l westus2 \
    -g MyResourceGroup  \
    --tags category=sale

az fluid-relay server list-key \
    -g MyResourceGroup \
    --server-name MyServerName

az fluid-relay server regenerate-key \
    -g MyResourceGroup \
    --server-name MyServerName \
    --key-name key1

az fluid-relay server list \
    --subscription 00000000-0000-0000-0000-000000000000
    
az fluid-relay server list \
    -g MyResourceGroup
    
az fluid-relay server show \
    -g MyResourceGroup \
    -n MyFluidRelay
```

#### Container:
Manage a fluid relay container: [more info](https://docs.microsoft.com/en-us/azure/azure-fluid-relay/overview/overview)
```
az fluid-relay container list \
    -g MyResourceGroup \
    --server-name MyServerName

az fluid-relay container show \
    -g MyResourceGroup \
    --server-name MyServerName \
    -n MyContainerName
    
az fluid-relay container delete \
    -g MyResourceGroup \
    --server-name MyServerName \
    -n MyContainerName
```