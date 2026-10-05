# Azure CLI Resiliency Extension

The Azure CLI Resiliency extension provides commands to manage Azure Resilience Management resources, including disaster recovery drills, goal assignments, recovery plans, and usage plans.

## Installation

```bash
az extension add --name resilience
```

## Usage

```bash
# Show help for all resiliency commands
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

## Complete Command Reference

### `az resilience drill`

| Command | Description |
|---|---|
| `az resilience drill create` | Create a drill |
| `az resilience drill delete` | Delete a drill |
| `az resilience drill list` | List drills |
| `az resilience drill show` | Show a drill |
| `az resilience drill update` | Update a drill |
| `az resilience drill wait` | Wait for a drill operation to complete |
| `az resilience drill add-or-update-resource` | Add or update a resource in a drill |
| `az resilience drill end` | End a drill |
| `az resilience drill resync-readiness-check` | Resync the readiness check for a drill |
| `az resilience drill start` | Start a drill |
| `az resilience drill validate-for-execution` | Validate a drill for execution |

### `az resilience drill drill-resource`

| Command | Description |
|---|---|
| `az resilience drill drill-resource list` | List drill resources |
| `az resilience drill drill-resource show` | Show a drill resource |

### `az resilience drill drill-run`

| Command | Description |
|---|---|
| `az resilience drill drill-run add-note` | Add a note to a drill run |
| `az resilience drill drill-run fail-over` | Fail over a drill run |
| `az resilience drill drill-run generate-report` | Generate a report for a drill run |
| `az resilience drill drill-run list` | List drill runs |
| `az resilience drill drill-run list-report-download-url` | List report download URLs for a drill run |
| `az resilience drill drill-run mark-as-complete` | Mark a drill run as complete |
| `az resilience drill drill-run reprotect` | Reprotect a drill run |
| `az resilience drill drill-run resume` | Resume a drill run |
| `az resilience drill drill-run show` | Show a drill run |

### `az resilience drill drill-run drill-run-resource`

| Command | Description |
|---|---|
| `az resilience drill drill-run drill-run-resource list` | List drill run resources |
| `az resilience drill drill-run drill-run-resource show` | Show a drill run resource |

### `az resilience drill identity`

| Command | Description |
|---|---|
| `az resilience drill identity assign` | Assign an identity to a drill |
| `az resilience drill identity remove` | Remove an identity from a drill |
| `az resilience drill identity show` | Show the identity of a drill |
| `az resilience drill identity wait` | Wait for an identity operation to complete |

### `az resilience goal-assignment`

| Command | Description |
|---|---|
| `az resilience goal-assignment create` | Create a goal assignment |
| `az resilience goal-assignment delete` | Delete a goal assignment |
| `az resilience goal-assignment list` | List goal assignments |
| `az resilience goal-assignment show` | Show a goal assignment |
| `az resilience goal-assignment update` | Update a goal assignment |
| `az resilience goal-assignment wait` | Wait for a goal assignment operation to complete |
| `az resilience goal-assignment recommend-capacity` | Recommend capacity for a goal assignment |
| `az resilience goal-assignment refresh-goal-resource` | Refresh goal resources for a goal assignment |
| `az resilience goal-assignment update-goal-resource` | Update goal resources for a goal assignment |

### `az resilience goal-assignment goal-resource`

| Command | Description |
|---|---|
| `az resilience goal-assignment goal-resource list` | List goal resources |
| `az resilience goal-assignment goal-resource show` | Show a goal resource |

### `az resilience operation-status`

| Command | Description |
|---|---|
| `az resilience operation-status show` | Show the status of an operation |

### `az resilience recovery-plan`

| Command | Description |
|---|---|
| `az resilience recovery-plan create` | Create a recovery plan |
| `az resilience recovery-plan delete` | Delete a recovery plan |
| `az resilience recovery-plan list` | List recovery plans |
| `az resilience recovery-plan show` | Show a recovery plan |
| `az resilience recovery-plan update` | Update a recovery plan |
| `az resilience recovery-plan wait` | Wait for a recovery plan operation to complete |
| `az resilience recovery-plan check-readiness` | Check the readiness of a recovery plan |
| `az resilience recovery-plan failover` | Failover a recovery plan |
| `az resilience recovery-plan failover-commit` | Commit a failover for a recovery plan |
| `az resilience recovery-plan finalize` | Finalize a recovery plan |
| `az resilience recovery-plan reprotect` | Reprotect a recovery plan |
| `az resilience recovery-plan test-failover` | Test failover for a recovery plan |
| `az resilience recovery-plan test-failover-cleanup` | Clean up a test failover |
| `az resilience recovery-plan update-resource` | Update resources in a recovery plan |
| `az resilience recovery-plan validate-for-failover` | Validate a recovery plan for failover |
| `az resilience recovery-plan validate-for-failover-commit` | Validate a recovery plan for failover commit |
| `az resilience recovery-plan validate-for-operation` | Validate a recovery plan for an operation |
| `az resilience recovery-plan validate-for-reprotect` | Validate a recovery plan for reprotect |
| `az resilience recovery-plan validate-for-test-failover` | Validate a recovery plan for test failover |
| `az resilience recovery-plan validate-for-test-failover-cleanup` | Validate a recovery plan for test failover cleanup |

### `az resilience recovery-plan identity`

| Command | Description |
|---|---|
| `az resilience recovery-plan identity assign` | Assign an identity to a recovery plan |
| `az resilience recovery-plan identity remove` | Remove an identity from a recovery plan |
| `az resilience recovery-plan identity show` | Show the identity of a recovery plan |
| `az resilience recovery-plan identity wait` | Wait for an identity operation to complete |

### `az resilience recovery-plan recovery-job`

| Command | Description |
|---|---|
| `az resilience recovery-plan recovery-job cancel` | Cancel a recovery job |
| `az resilience recovery-plan recovery-job list` | List recovery jobs |
| `az resilience recovery-plan recovery-job resume` | Resume a recovery job |
| `az resilience recovery-plan recovery-job retry` | Retry a recovery job |
| `az resilience recovery-plan recovery-job show` | Show a recovery job |

### `az resilience recovery-plan recovery-job recovery-job-resource`

| Command | Description |
|---|---|
| `az resilience recovery-plan recovery-job recovery-job-resource list` | List recovery job resources |
| `az resilience recovery-plan recovery-job recovery-job-resource show` | Show a recovery job resource |

### `az resilience recovery-plan recovery-resource`

| Command | Description |
|---|---|
| `az resilience recovery-plan recovery-resource list` | List recovery resources |
| `az resilience recovery-plan recovery-resource show` | Show a recovery resource |

### `az resilience unified-resilience-item`

| Command | Description |
|---|---|
| `az resilience unified-resilience-item list` | List unified resilience items |
| `az resilience unified-resilience-item show` | Show a unified resilience item |

### `az resilience usage-plan`

| Command | Description |
|---|---|
| `az resilience usage-plan create` | Create a usage plan |
| `az resilience usage-plan delete` | Delete a usage plan |
| `az resilience usage-plan list` | List usage plans |
| `az resilience usage-plan show` | Show a usage plan |
| `az resilience usage-plan update` | Update a usage plan |
| `az resilience usage-plan wait` | Wait for a usage plan operation to complete |

### `az resilience usage-plan enrollment`

| Command | Description |
|---|---|
| `az resilience usage-plan enrollment create` | Create a usage plan enrollment |
| `az resilience usage-plan enrollment delete` | Delete a usage plan enrollment |
| `az resilience usage-plan enrollment list` | List usage plan enrollments |
| `az resilience usage-plan enrollment show` | Show a usage plan enrollment |
| `az resilience usage-plan enrollment update` | Update a usage plan enrollment |
| `az resilience usage-plan enrollment wait` | Wait for an enrollment operation to complete |

## API Version

This extension supports API version `2026-10-01` (stable GA) for `Microsoft.AzureResilienceManagement`.

## Documentation

For more information, see the [Azure Resiliency documentation](https://learn.microsoft.com/en-us/azure/resilience/).
