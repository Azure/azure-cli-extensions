# Azure CLI Migration Module

This module provides server discovery and replication capabilities for Azure resources and workloads through Azure CLI commands, with special focus on Azure Local (Azure Stack HCI) migrations.

# Azure CLI Migrate Extension #
The Azure CLI extension for managing [Azure Migrate](https://aka.ms/azure-migrate) resources. 

## Install ##
You can install the extension by running:
``` sh
az extension add --name migrate --allow-preview True
```

## Usage ##
``` sh
az migrate --help
```

## Uninstall ##
You can see if the extension is installed by running `az --version` or `az extension list`. You can remove the extension by running:
``` sh
az extension remove --name migrate
```


## Features

- **Server discovery**: Discover servers from various sources
- **Replication management**: Initialize and create new replications for supported workloads

## Prerequisites

- Azure CLI 2.0+
- Valid Azure subscription
- Appropriate permissions for migration operations
- For Azure Local: Azure Stack HCI environment with proper networking

## Command Overview

The Azure CLI migrate module provides the following commands:

### Server Discovery
```bash
# Get discovered servers from Azure Migrate project
az migrate get-discovered-server \
  --resource-group myRG \
  --project-name myProject

# Get discovered servers with filtering
az migrate get-discovered-server \
  --resource-group myRG \
  --project-name myProject \
  --display-name "WebServer" \
  --source-machine-type VMware

# Get a specific discovered server by name
az migrate get-discovered-server \
  --resource-group myRG \
  --project-name myProject \
  --name machine-12345 \
  --appliance-name myAppliance
```

### Azure Local (Stack HCI) Replication Commands
```bash
# Initialize Azure Local replication infrastructure
az migrate local replication init \
  --resource-group myRG \
  --project-name myProject \
  --source-appliance-name sourceAppliance \
  --target-appliance-name targetAppliance

# Create a new replication using machine ID
az migrate local replication new \
  --machine-id "/subscriptions/xxx/resourceGroups/myRG/providers/Microsoft.Migrate/migrateprojects/myProject/machines/machine-001" \
  --target-storage-path-id "/subscriptions/xxx/resourceGroups/myRG/providers/Microsoft.AzureStackHCI/storageContainers/storage01" \
  --target-resource-group-id "/subscriptions/xxx/resourceGroups/targetRG" \
  --target-vm-name "MigratedVM" \
  --source-appliance-name sourceAppliance \
  --target-appliance-name targetAppliance \
  --target-virtual-switch-id "/subscriptions/xxx/resourceGroups/myRG/providers/Microsoft.AzureStackHCI/logicalnetworks/network01" \
  --os-disk-id "disk-0"

# Create a new replication using machine index
az migrate local replication new \
  --machine-index 1 \
  --project-name myProject \
  --resource-group myRG \
  --target-storage-path-id "/subscriptions/xxx/providers/Microsoft.AzureStackHCI/storageContainers/storage01" \
  --target-resource-group-id "/subscriptions/xxx/resourceGroups/targetRG" \
  --target-vm-name "MigratedVM" \
  --source-appliance-name sourceAppliance \
  --target-appliance-name targetAppliance \
  --target-virtual-switch-id "/subscriptions/xxx/providers/Microsoft.AzureStackHCI/logicalnetworks/network01" \
  --os-disk-id "disk-0"

# List all replicating servers
az migrate local replication list \
  --resource-group myRG \
  --project-name myProject

# Get details of a specific replicating server by ID
az migrate local replication get \
  --id "/subscriptions/xxx/resourceGroups/myRG/providers/Microsoft.DataReplication/replicationVaults/vault01/protectedItems/item01"

# Get details of a specific replicating server by name
az migrate local replication get \
  --name "item01" \
  --resource-group myRG \
  --project-name myProject

# Remove replication for a server
az migrate local replication remove \
  --target-object-id "/subscriptions/xxx/resourceGroups/myRG/providers/Microsoft.DataReplication/replicationVaults/vault01/protectedItems/item01"

# Get replication job details
az migrate local replication get-job \
  --job-id "/subscriptions/xxx/resourceGroups/myRG/providers/Microsoft.DataReplication/replicationVaults/vault01/jobs/job-12345" \
  --resource-group myRG \
  --project-name myProject
```

## Architecture

The migration module consists of several key components:

1. **Server Discovery**: Query and filter discovered servers from Azure Migrate projects
2. **Azure Local Migration**: Specialized support for Azure Stack HCI migration scenarios
3. **Replication Management**: Initialize, create, list, get, and remove replications
4. **Job Monitoring**: Track replication and migration job progress

## Common Workflows

### Setting up Azure Local Migration

```bash
# 1. Discover servers in your Azure Migrate project
az migrate get-discovered-server \
  --resource-group "migration-rg" \
  --project-name "azure-local-migration" \
  --source-machine-type VMware

# 2. Initialize Azure Local replication infrastructure
az migrate local replication init \
  --resource-group "migration-rg" \
  --project-name "azure-local-migration" \
  --source-appliance-name "vmware-appliance" \
  --target-appliance-name "azlocal-appliance"

# 3. Create replication for a specific server (using machine index from discovery)
az migrate local replication new \
  --machine-index 1 \
  --resource-group "migration-rg" \
  --project-name "azure-local-migration" \
  --target-vm-name "WebServer-Migrated" \
  --target-storage-path-id "/subscriptions/xxx/providers/Microsoft.AzureStackHCI/storageContainers/migration-storage" \
  --target-virtual-switch-id "/subscriptions/xxx/providers/Microsoft.AzureStackHCI/logicalnetworks/migration-network" \
  --target-resource-group-id "/subscriptions/xxx/resourceGroups/azure-local-vms" \
  --source-appliance-name "vmware-appliance" \
  --target-appliance-name "azlocal-appliance" \
  --os-disk-id "disk-0"

# 4. List all replicating servers
az migrate local replication list \
  --resource-group "migration-rg" \
  --project-name "azure-local-migration"

# 5. Get detailed information about a specific replication
az migrate local replication get \
  --name "replication-item-name" \
  --resource-group "migration-rg" \
  --project-name "azure-local-migration"

# 6. Monitor replication job progress
az migrate local replication get-job \
  --job-id "/subscriptions/xxx/resourceGroups/migration-rg/providers/Microsoft.DataReplication/replicationVaults/vault/jobs/job-id" \
  --resource-group "migration-rg" \
  --project-name "azure-local-migration"

# 7. Remove replication when migration is complete
az migrate local replication remove \
  --target-object-id "/subscriptions/xxx/resourceGroups/migration-rg/providers/Microsoft.DataReplication/replicationVaults/vault/protectedItems/item" \
  --force-remove
```

### Discovering and Filtering Servers

```bash
# 1. List all discovered servers
az migrate get-discovered-server \
  --resource-group "migration-rg" \
  --project-name "server-migration-2025"

# 2. Filter by display name
az migrate get-discovered-server \
  --resource-group "migration-rg" \
  --project-name "server-migration-2025" \
  --display-name "WebServer"

# 3. Filter by source machine type
az migrate get-discovered-server \
  --resource-group "migration-rg" \
  --project-name "server-migration-2025" \
  --source-machine-type VMware

# 4. Get a specific server by name and appliance
az migrate get-discovered-server \
  --resource-group "migration-rg" \
  --project-name "server-migration-2025" \
  --name "machine-12345" \
  --appliance-name "vmware-appliance-01"
```

## Command Reference

| Command | Description |
|---------|-------------|
| `az migrate get-discovered-server` | Retrieve discovered servers from an Azure Migrate project |
| `az migrate local replication init` | Initialize Azure Local replication infrastructure |
| `az migrate local replication new` | Create a new server replication |
| `az migrate local replication list` | List all replicating servers |
| `az migrate local replication get` | Get detailed information about a specific replication |
| `az migrate local replication remove` | Stop and remove replication for a server |
| `az migrate local replication get-job` | Get replication job details |

## Error Handling

The module includes comprehensive error handling for:

- Invalid project configurations
- Missing required parameters
- Resource not found scenarios
- Azure service connectivity problems
- Authentication and permission issues
- Replication state validation

## Troubleshooting

### Common Issues

**Server Discovery Issues**
- Confirm the appliance is properly configured
- Verify network connectivity from appliance to Azure
- Check that discovery is running on the appliance
- Use `az migrate get-discovered-server` to check for discovered servers

**Replication Initialization Issues**
- Ensure both source and target appliances are specified
- Verify appliances are properly configured and connected
- Check that the Azure Migrate project exists
- Ensure proper permissions on the resource group

**Replication Creation Issues**
- Verify the machine ID or index is correct
- Ensure all required parameters are provided (storage path, resource group, VM name, appliances)
- Check that the target storage container and logical network exist
- Verify the OS disk ID is correct (required parameter)

**Permission Errors**
- Ensure Azure Migrate Contributor role is assigned
- Verify subscription-level permissions for creating resources
- Check resource group permissions

**Azure Local Specific Issues**
- Verify Azure Stack HCI cluster is properly registered with Azure
- Ensure proper networking between source and Azure Local target
- Check that both source and target appliances are properly configured
- Verify storage containers and logical networks are properly set up in Azure Local
- Use `az migrate local replication init` to initialize infrastructure before creating replications

**Job Monitoring Issues**
- Ensure the job ID is the full ARM resource ID
- Verify the job exists in the specified vault
- Check that the resource group and project name are correct

## Contributing

When extending the migration module:

1. Follow Azure CLI command naming conventions
2. Implement proper error handling and validation
3. Add comprehensive help documentation
4. Include usage examples in help text
5. Update this README with new command examples
6. Ensure cross-platform PowerShell compatibility
7. Add appropriate parameter validation
8. Include integration tests for new commands

For more information on Azure Migrate, visit: https://docs.microsoft.com/azure/migrate/

## License

This project is licensed under the MIT License - see the LICENSE file for details.
