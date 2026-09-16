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

## Complete Command Reference

### `az resiliency drill`

| Command | Description |
|---|---|
| `az resiliency drill create` | Create a drill |
| `az resiliency drill delete` | Delete a drill |
| `az resiliency drill list` | List drills |
| `az resiliency drill show` | Show a drill |
| `az resiliency drill update` | Update a drill |
| `az resiliency drill wait` | Wait for a drill operation to complete |
| `az resiliency drill add-or-update-resource` | Add or update a resource in a drill |
| `az resiliency drill end` | End a drill |
| `az resiliency drill resync-readiness-check` | Resync the readiness check for a drill |
| `az resiliency drill start` | Start a drill |
| `az resiliency drill validate-for-execution` | Validate a drill for execution |

### `az resiliency drill drill-resource`

| Command | Description |
|---|---|
| `az resiliency drill drill-resource list` | List drill resources |
| `az resiliency drill drill-resource show` | Show a drill resource |

### `az resiliency drill drill-run`

| Command | Description |
|---|---|
| `az resiliency drill drill-run add-note` | Add a note to a drill run |
| `az resiliency drill drill-run fail-over` | Fail over a drill run |
| `az resiliency drill drill-run generate-report` | Generate a report for a drill run |
| `az resiliency drill drill-run list` | List drill runs |
| `az resiliency drill drill-run list-report-download-url` | List report download URLs for a drill run |
| `az resiliency drill drill-run mark-as-complete` | Mark a drill run as complete |
| `az resiliency drill drill-run reprotect` | Reprotect a drill run |
| `az resiliency drill drill-run resume` | Resume a drill run |
| `az resiliency drill drill-run show` | Show a drill run |

### `az resiliency drill drill-run drill-run-resource`

| Command | Description |
|---|---|
| `az resiliency drill drill-run drill-run-resource list` | List drill run resources |
| `az resiliency drill drill-run drill-run-resource show` | Show a drill run resource |

### `az resiliency drill identity`

| Command | Description |
|---|---|
| `az resiliency drill identity assign` | Assign an identity to a drill |
| `az resiliency drill identity remove` | Remove an identity from a drill |
| `az resiliency drill identity show` | Show the identity of a drill |
| `az resiliency drill identity wait` | Wait for an identity operation to complete |

### `az resiliency goal-assignment`

| Command | Description |
|---|---|
| `az resiliency goal-assignment create` | Create a goal assignment |
| `az resiliency goal-assignment delete` | Delete a goal assignment |
| `az resiliency goal-assignment list` | List goal assignments |
| `az resiliency goal-assignment show` | Show a goal assignment |
| `az resiliency goal-assignment update` | Update a goal assignment |
| `az resiliency goal-assignment wait` | Wait for a goal assignment operation to complete |
| `az resiliency goal-assignment recommend-capacity` | Get capacity recommendations for a goal assignment |
| `az resiliency goal-assignment refresh-goal-resource` | Refresh goal resources for a goal assignment |
| `az resiliency goal-assignment update-goal-resource` | Update goal resources for a goal assignment |

### `az resiliency goal-assignment goal-resource`

| Command | Description |
|---|---|
| `az resiliency goal-assignment goal-resource list` | List goal resources |
| `az resiliency goal-assignment goal-resource show` | Show a goal resource |

### `az resiliency operation-status`

| Command | Description |
|---|---|
| `az resiliency operation-status show` | Show the status of a long-running operation |

### `az resiliency recovery-plan`

| Command | Description |
|---|---|
| `az resiliency recovery-plan create` | Create a recovery plan |
| `az resiliency recovery-plan delete` | Delete a recovery plan |
| `az resiliency recovery-plan list` | List recovery plans |
| `az resiliency recovery-plan show` | Show a recovery plan |
| `az resiliency recovery-plan update` | Update a recovery plan |
| `az resiliency recovery-plan wait` | Wait for a recovery plan operation to complete |
| `az resiliency recovery-plan check-readiness` | Check readiness of a recovery plan |
| `az resiliency recovery-plan failover` | Failover a recovery plan |
| `az resiliency recovery-plan failover-commit` | Commit a failover for a recovery plan |
| `az resiliency recovery-plan finalize` | Finalize a recovery plan |
| `az resiliency recovery-plan reprotect` | Reprotect a recovery plan |
| `az resiliency recovery-plan test-failover` | Test failover for a recovery plan |
| `az resiliency recovery-plan test-failover-cleanup` | Clean up a test failover |
| `az resiliency recovery-plan update-resource` | Update resources in a recovery plan |
| `az resiliency recovery-plan validate-for-failover` | Validate a recovery plan for failover |
| `az resiliency recovery-plan validate-for-failover-commit` | Validate a recovery plan for failover commit |
| `az resiliency recovery-plan validate-for-operation` | Validate a recovery plan for an operation |
| `az resiliency recovery-plan validate-for-reprotect` | Validate a recovery plan for reprotect |
| `az resiliency recovery-plan validate-for-test-failover` | Validate a recovery plan for test failover |
| `az resiliency recovery-plan validate-for-test-failover-cleanup` | Validate a recovery plan for test failover cleanup |

### `az resiliency recovery-plan identity`

| Command | Description |
|---|---|
| `az resiliency recovery-plan identity assign` | Assign an identity to a recovery plan |
| `az resiliency recovery-plan identity remove` | Remove an identity from a recovery plan |
| `az resiliency recovery-plan identity show` | Show the identity of a recovery plan |
| `az resiliency recovery-plan identity wait` | Wait for an identity operation to complete |

### `az resiliency recovery-plan recovery-job`

| Command | Description |
|---|---|
| `az resiliency recovery-plan recovery-job cancel` | Cancel a recovery job |
| `az resiliency recovery-plan recovery-job list` | List recovery jobs |
| `az resiliency recovery-plan recovery-job resume` | Resume a recovery job |
| `az resiliency recovery-plan recovery-job retry` | Retry a recovery job |
| `az resiliency recovery-plan recovery-job show` | Show a recovery job |

### `az resiliency recovery-plan recovery-job recovery-job-resource`

| Command | Description |
|---|---|
| `az resiliency recovery-plan recovery-job recovery-job-resource list` | List recovery job resources |
| `az resiliency recovery-plan recovery-job recovery-job-resource show` | Show a recovery job resource |

### `az resiliency recovery-plan recovery-resource`

| Command | Description |
|---|---|
| `az resiliency recovery-plan recovery-resource list` | List recovery resources |
| `az resiliency recovery-plan recovery-resource show` | Show a recovery resource |

### `az resiliency unified-resilience-item`

| Command | Description |
|---|---|
| `az resiliency unified-resilience-item list` | List unified resilience items |
| `az resiliency unified-resilience-item show` | Show a unified resilience item |

### `az resiliency usage-plan`

| Command | Description |
|---|---|
| `az resiliency usage-plan create` | Create a usage plan |
| `az resiliency usage-plan delete` | Delete a usage plan |
| `az resiliency usage-plan list` | List usage plans |
| `az resiliency usage-plan show` | Show a usage plan |
| `az resiliency usage-plan update` | Update a usage plan |
| `az resiliency usage-plan wait` | Wait for a usage plan operation to complete |

### `az resiliency usage-plan enrollment`

| Command | Description |
|---|---|
| `az resiliency usage-plan enrollment create` | Create a usage plan enrollment |
| `az resiliency usage-plan enrollment delete` | Delete a usage plan enrollment |
| `az resiliency usage-plan enrollment list` | List usage plan enrollments |
| `az resiliency usage-plan enrollment show` | Show a usage plan enrollment |
| `az resiliency usage-plan enrollment update` | Update a usage plan enrollment |
| `az resiliency usage-plan enrollment wait` | Wait for an enrollment operation to complete |

## API Version

This extension supports API version `2026-09-30-preview` for `Microsoft.AzureResilienceManagement`.

## Documentation

For more information, see the [Azure Resilience Management documentation](https://learn.microsoft.com/en-us/azure/resilience/).
