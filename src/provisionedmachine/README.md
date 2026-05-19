# Provisioned Machine

Manage Azure Stack HCI Edge Machines using the Azure CLI.

## Commands

| Command | Description |
|---------|-------------|
| `az provisionedmachine list` | List edge machines by subscription or resource group |
| `az provisionedmachine show` | Get details of a specific edge machine |
| `az provisionedmachine delete` | Delete an edge machine |

## Examples

### List all edge machines in a subscription

```bash
az provisionedmachine list
```

### List edge machines in a resource group

```bash
az provisionedmachine list -g myResourceGroup
```

### Show an edge machine

```bash
az provisionedmachine show -n myEdgeMachine -g myResourceGroup
```

### Delete an edge machine

```bash
az provisionedmachine delete -n myEdgeMachine -g myResourceGroup
```
