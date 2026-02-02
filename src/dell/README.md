# Azure CLI Dell Extension

The Azure CLI Dell Extension provides commands to manage Dell.Storage filesystem resources.

## Install

```bash
az extension add --name dell
```

## Usage

### Create a Dell filesystem

```bash
az dell filesystem create \
    --resource-group myResourceGroup \
    --filesystem-name myFilesystem \
    --location "East US" \
    --delegated-subnet-id "/subscriptions/.../subnets/mySubnet" \
    --delegated-subnet-cidr "10.0.0.0/24" \
    --marketplace '{"marketplace-subscription-id":"...","plan-id":"...","offer-id":"...","publisher-id":"dellemc"}' \
    --user '{"email":"user@example.com"}' \
    --encryption '{"encryption-type":"Microsoft-managed keys (MMK)"}'
```

### List Dell filesystems

```bash
az dell filesystem list --resource-group myResourceGroup
```

### Show a Dell filesystem

```bash
az dell filesystem show --resource-group myResourceGroup --filesystem-name myFilesystem
```

### Delete a Dell filesystem

```bash
az dell filesystem delete --resource-group myResourceGroup --filesystem-name myFilesystem
```

### Wait for operation completion

```bash
az dell filesystem wait --resource-group myResourceGroup --filesystem-name myFilesystem --created
```