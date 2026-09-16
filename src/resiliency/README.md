# Azure CLI Resiliency Extension

The Azure CLI Resiliency extension provides commands to manage Azure Resilience Management resources, including disaster recovery drills, goal assignments, recovery plans, and usage plans.

## Installation

```bash
az extension add --name resiliency
```

## Usage

```bash
# Show help for all resiliency commands
az resiliency --help

# Manage drills
az resiliency drill create --service-group-name <name> --drill-name <name> --location <location>
az resiliency drill list --service-group-name <name>
az resiliency drill show --service-group-name <name> --drill-name <name>

# Manage goal assignments
az resiliency goal-assignment create --service-group-name <name> --goal-assignment-name <name>
az resiliency goal-assignment list --service-group-name <name>

# Manage recovery plans
az resiliency recovery-plan create --service-group-name <name> --recovery-plan-name <name>
az resiliency recovery-plan list --service-group-name <name>

# Manage usage plans
az resiliency usage-plan create --resource-group <rg> --usage-plan-name <name> --plan-type Standard --location <location>
az resiliency usage-plan list

# Check operation status
az resiliency operation-status show --location <location> --operation-id <id>
```

## Command Groups

| Group | Description |
|---|---|
| `az resiliency drill` | Manage disaster recovery drills, drill runs, and drill resources |
| `az resiliency goal-assignment` | Manage resilience goal assignments and goal resources |
| `az resiliency operation-status` | Check the status of long-running operations |
| `az resiliency recovery-plan` | Manage recovery plans, failover, reprotect, and recovery jobs |
| `az resiliency unified-resilience-item` | View unified resilience items |
| `az resiliency usage-plan` | Manage usage plans and enrollments |

## API Version

This extension supports API version `2026-09-30-preview` for `Microsoft.AzureResilienceManagement`.

## Documentation

For more information, see the [Azure Resilience Management documentation](https://learn.microsoft.com/en-us/azure/resilience/).
