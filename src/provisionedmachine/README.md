# Provisioned Machine

> **Preview** — This extension is currently in public preview (`1.0.0b5`).

Manage Azure Stack HCI Edge Machines using the Azure CLI.

## Installation

```bash
az extension add --name provisionedmachine
```

To update an existing installation:

```bash
az extension update --name provisionedmachine
```

## Commands

| Command | Description |
|---------|-------------|
| `az provisionedmachine create` | Create a new provisioned machine |
| `az provisionedmachine list` | List edge machines by subscription or resource group |
| `az provisionedmachine show` | Get details of a specific edge machine |
| `az provisionedmachine show-status` | Show lifecycle status of a provisioned machine |
| `az provisionedmachine delete` | Delete an edge machine |
| `az provisionedmachine install-os` | Install OS on a provisioned machine |
| `az provisionedmachine reset-os` | Reset OS on a provisioned machine |
| `az provisionedmachine os-image list` | List available OS images for provisioning |
| `az provisionedmachine ssh-cert-create` | Create a short-lived SSH certificate for device authentication |

## Examples

### Create a provisioned machine

```bash
# AzureLinux
az provisionedmachine create -n myProvisionedMachine -g myResourceGroup \
  --location eastus \
  --voucher-file ./ownership-voucher.pem \
  --site-id "/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.ExtendedLocation/customLocations/<site>" \
  --os-image-type AzureLinux \
  --ssh-public-key "ssh-rsa AAAAB3..."

# HCI
az provisionedmachine create -n myProvisionedMachine -g myResourceGroup \
  --location eastus \
  --voucher-file ./ownership-voucher.pem \
  --site-id "/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.ExtendedLocation/customLocations/<site>" \
  --os-image-type HCI \
  --key-vault-secret-id "/subscriptions/.../secrets/mySecret"
```

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

### Show lifecycle status of a provisioned machine

```bash
az provisionedmachine show-status -n myProvisionedMachine -g myResourceGroup
```

### Show lifecycle status in table format

```bash
az provisionedmachine show-status -n myProvisionedMachine -g myResourceGroup -o table
```

### List available OS images

```bash
az provisionedmachine os-image list --os-image-type HCI
az provisionedmachine os-image list --location australiaeast --os-image-type AzureLinux -o table
```

### Install OS on a provisioned machine

```bash
# AzureLinux (auto-selects latest version when --os-image-version is not specified)
az provisionedmachine install-os -g myResourceGroup -n myProvisionedMachine --os-image-type AzureLinux --ssh-public-key "ssh-rsa AAAAB3..."

# HCI (auto-selects latest version when --os-image-version is not specified)
az provisionedmachine install-os -g myResourceGroup -n myProvisionedMachine --os-image-type HCI --key-vault-secret-id "/subscriptions/.../secrets/mySecret"

# HCI with a specific version
az provisionedmachine install-os -g myResourceGroup -n myProvisionedMachine --os-image-type HCI --os-image-version 10.2504.0.64 --key-vault-secret-id "/subscriptions/.../secrets/mySecret"
```

### Reset OS on a provisioned machine

```bash
az provisionedmachine reset-os -n myProvisionedMachine -g myResourceGroup
```

### Delete an edge machine

```bash
az provisionedmachine delete -n myEdgeMachine -g myResourceGroup
az provisionedmachine delete -n myEdgeMachine -g myResourceGroup --yes  # skip confirmation prompt
```

### Create an SSH certificate (default output paths)

```bash
az provisionedmachine ssh-cert-create \
    --vault-name myKeyVault \
    --resource-id /subscriptions/.../providers/Microsoft.AzureStackHCI/edgeMachines/myDevice
```

### Create an SSH certificate (custom output paths)

```bash
az provisionedmachine ssh-cert-create \
    --vault-name myKeyVault \
    --resource-id /subscriptions/.../providers/Microsoft.AzureStackHCI/edgeMachines/myDevice \
    --private-key-path ~/.ssh/device_key \
    --cert-path ~/.ssh/device_cert.pub
```
