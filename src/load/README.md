# Azure CLI Load Extension #
This is an extension to Azure CLI to create and manage Azure Load testing resources.

## How to use ##

Install this extension using the below CLI command
```
az extension add --name load
```

## Included Features ##


### Create Azure load testing resource ###

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
    --tags type=testing type=infra
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

### Update Azure load testing resource/resources ###

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
    --encryption-key https://sample-kv.vault.azure.net/keys/samplekey2/2d1ccd5c50234ea2a0858fe148b69cde
    --encryption-identity SystemAssigned
```
