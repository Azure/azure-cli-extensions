# Azure CLI Resilience Extension

The Azure CLI Resilience extension provides commands to manage Azure Resilience Management resources, including disaster recovery drills, goal assignments, recovery plans, and usage plans.

## Installation

```bash
az extension add --name resilience
```

## Usage

```bash
# Show help for all resilience commands
az resilience --help

# Manage drills
az resilience drill create --service-group-name <name> --drill-name <name> --location <location>
az resilience drill list --service-group-name <name>
az resilience drill show --service-group-name <name> --drill-name <name>

# Manage goal assignments
az resilience goal-assignment create --service-group-name <name> --goal-assignment-name <name>
az resilience goal-assignment list --service-group-name <name>

# Manage recovery plans
az resilience recovery-plan create --service-group-name <name> --recovery-plan-name <name>
az resilience recovery-plan list --service-group-name <name>

# Manage usage plans
az resilience usage-plan create --resource-group <rg> --usage-plan-name <name> --plan-type Standard --location <location>
az resilience usage-plan list

# Check operation status
az resilience operation-status show --location <location> --operation-id <id>
```

## Command Groups

| Group | Description |
|---|---|
| `az resilience drill` | Manage disaster recovery drills, drill runs, and drill resources |
| `az resilience goal-assignment` | Manage resilience goal assignments and goal resources |
| `az resilience operation-status` | Check the status of long-running operations |
| `az resilience recovery-plan` | Manage recovery plans, failover, reprotect, and recovery jobs |
| `az resilience unified-resilience-item` | View unified resilience items |
| `az resilience usage-plan` | Manage usage plans and enrollments |

## API Version

This extension supports API version `2026-09-30-preview` for `Microsoft.AzureResilienceManagement`.

## Documentation

For more information, see the [Azure Resilience Management documentation](https://learn.microsoft.com/en-us/azure/resilience/).
