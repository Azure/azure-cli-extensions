# Azure CLI Cloudhsm Extension #
This is an extension to Azure CLI to manage Cloudhsm resources.

## Installation

Install this extension using the CLI command:
```bash
az extension add --name cloudhsm
```

## Sample Usage

### Prerequisites
- Azure subscription
- Resource group
- Storage account with blob container (for backup/restore operations)
- User-assigned managed identity (for backup/restore operations)

### 1. Create a CloudHSM Cluster

#### Basic CloudHSM creation:
```bash
az cloudhsm create \
    --resource-group myResourceGroup \
    --name myCloudHSM \
    --location eastus2 \
    --sku Standard_B1 \
    --tags Department=Security Environment=Production
```

#### CloudHSM with user-assigned managed identity:
```bash
az cloudhsm create \
    --resource-group myResourceGroup \
    --name myCloudHSM \
    --location eastus2 \
    --sku Standard_B1 \
    --domain-name-label-scope TenantReuse \
    --mi-user-assigned /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myIdentity \
    --tags Department=Security Environment=Production
```

#### Available SKUs:
- `Standard_B1` (default)


### 2. List CloudHSM Clusters

#### List all CloudHSM clusters in subscription:
```bash
az cloudhsm list
```

#### List CloudHSM clusters in a specific resource group:
```bash
az cloudhsm list --resource-group myResourceGroup
```

### 3. Show CloudHSM Details

```bash
az cloudhsm show \
    --resource-group myResourceGroup \
    --name myCloudHSM
```

### 4. Update CloudHSM

```bash
az cloudhsm update \
    --resource-group myResourceGroup \
    --name myCloudHSM \
    --tags Department=Security Environment=Production Updated=true
```

### 5. Backup Operations

#### Start a backup:
```bash
az cloudhsm backup start \
    --resource-group myResourceGroup \
    --cluster-name myCloudHSM \
    --blob-container-uri "https://mystorageaccount.blob.core.windows.net/backups"
```

### 6. Restore Operations

#### Start a restore from backup:
```bash
az cloudhsm restore start \
    --resource-group myResourceGroup \
    --cluster-name myCloudHSM \
    --backup-id cloudhsm-0e35c989-c582-4b3c-958d-596e4c4fe133 \
    --blob-container-uri "https://mystorageaccount.blob.core.windows.net/backups"
```

### 7. Delete CloudHSM

```bash
az cloudhsm delete \
    --resource-group myResourceGroup \
    --name myCloudHSM \
```

## Common Scenarios

### Scenario 1: Setup CloudHSM with Backup Strategy
```bash
# 1. Create CloudHSM
az cloudhsm create \
    --resource-group myResourceGroup \
    --name myCloudHSM \
    --location eastus2 \
    --sku Standard_B1

# 2. Start initial backup
az cloudhsm backup start \
    --resource-group myResourceGroup \
    --cluster-name myCloudHSM \
    --blob-container-uri "https://mystorageaccount.blob.core.windows.net/backups"
```

### Scenario 2: Disaster Recovery
```bash
# 1. Create new CloudHSM cluster
az cloudhsm create \
    --resource-group myDRResourceGroup \
    --name myDRCloudHSM \
    --location westus2 \
    --sku Standard_B1

# 2. Restore from backup
az cloudhsm restore start \
    --resource-group myDRResourceGroup \
    --cluster-name myDRCloudHSM \
    --backup-id your-backup-id \
    --blob-container-uri "https://mystorageaccount.blob.core.windows.net/backups"
```

## Best Practices

1. **Regular backups** to protect against data loss
2. **Monitor operations** to track the status of long-running operations
3. **Tag resources** for better organization and cost management
4. **Store backups** in geo-redundant storage for disaster recovery

## Additional Resources

- [Azure CloudHSM Documentation](https://docs.microsoft.com/azure/cloud-hsm)
- [Azure CLI Documentation](https://docs.microsoft.com/cli/azure/)
- [Azure Storage Documentation](https://docs.microsoft.com/azure/storage/)