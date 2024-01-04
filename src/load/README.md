# Azure CLI Load Testing Extension #
This is an extension to Azure CLI to create and manage Azure Load Testing resources.

## How to use ##

Install this extension using the below CLI command
```
az extension add --name load
```

### Create Azure Load Testing resource ###

```
az load create \
    --name sample-resource \
    --resource-group sample-rg \
    --location westus2
```

```
az load create \
    -n sample-resource \
    -g sample-rg \
    -l westus2
```

```
az load create \
    --name sample-resource \
    --resource-group sample-rg \
    --location westus2 \
    --tags type=testing target=infra
```

```
az load create \
    --name sample-resource \
    --resource-group sample-rg \
    --location westus2 \
    --identity-type SystemAssigned,UserAssigned \
    --user-assigned "{'/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/sample-mi':{}}"
```

```
az load create \
    --name sample-resource \
    --resource-group sample-rg \
    --location westus2 \
    --identity-type SystemAssigned,UserAssigned \
    --user-assigned "{'/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/sample-mi':{}}" \
    --encryption-key https://sample-kv.vault.azure.net/keys/samplekey/2d1ccd5c50234ea2a0858fe148b69cde \
    --encryption-identity /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/sample-mi

```
---
<br/>

### Update Azure Load Testing resource ###

```
az load update \
    --name sample-resource \
    --resource-group sample-rg \
    --identity-type SystemAssigned
```
```
az load update \
    --name sample-resource \
    --resource-group sample-rg \
    --tags type=server
```
```
az load update \
    --name sample-resource \
    --resource-group sample-rg \
    --encryption-key https://sample-kv.vault.azure.net/keys/samplekey2/2d1ccd5c50234ea2a0858fe148b69cde
```

```
az load update \
    --name sample-resource \
    --resource-group sample-rg \
    --identity-type SystemAssigned,UserAssigned \
    --user-assigned "{'/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/sample-mi':{}}" \
    --encryption-key https://sample-kv.vault.azure.net/keys/samplekey2/2d1ccd5c50234ea2a0858fe148b69cde \
    --encryption-identity SystemAssigned
```
---
<br/>

### List Azure Load Testing resources ###

```
az load list \
    --resource-group sample-rg 
```

```
az load list
```
---
<br/>

### Show Azure Load Testing resource ###

```
az load show \
    --name sample-resource \
    --resource-group sample-rg 
```

```
az load show \
    --ids /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg/providers/Microsoft.LoadTestService/loadtests/sample-resource1 /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg2/providers/Microsoft.LoadTestService/loadtests/sample-resource2 
```
---
<br/>

### Delete Azure Load Testing resource ###

```
az load delete \
    --name sample-resource \
    --resource-group sample-rg 
```

```
az load delete \
    --ids /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg/providers/Microsoft.LoadTestService/loadtests/sample-resource1 /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg2/providers/Microsoft.LoadTestService/loadtests/sample-resource2 
```
---
<br/>
