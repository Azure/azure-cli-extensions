# Azure CLI Azure Resilience Management Extension

This extension provides commands for managing Azure Resilience Management
resources through the `az resilience` command group.

## Install

```bash
az extension add --name azure-resilience-management
```

## Command groups

| Group | Description |
|--|--|
| `az resilience drill` | Manage resilience drills and their execution lifecycle |
| `az resilience drill drill-resource` | Inspect resources associated with a drill |
| `az resilience drill drill-run` | Manage and inspect drill runs and reports |
| `az resilience drill drill-run drill-run-resource` | Inspect resources associated with a drill run |
| `az resilience drill identity` | Manage the managed identity for a drill |
| `az resilience goal-assignment` | Manage resilience goal assignments and recommendations |
| `az resilience goal-assignment goal-resource` | Inspect resources associated with a goal assignment |
| `az resilience goal-template` | Manage reusable resilience goal templates |
| `az resilience recovery-plan` | Manage recovery plans and recovery operations |
| `az resilience recovery-plan identity` | Manage the managed identity for a recovery plan |
| `az resilience recovery-plan recovery-job` | Inspect and control recovery jobs |
| `az resilience recovery-plan recovery-job recovery-job-resource` | Inspect resources associated with a recovery job |
| `az resilience recovery-plan recovery-resource` | Inspect resources associated with a recovery plan |
| `az resilience unified-resilience-item` | Inspect aggregated resilience information |
| `az resilience usage-plan` | Manage usage plans and enrollments |
| `az resilience usage-plan enrollment` | Manage usage plan enrollments |

## Complete command list

The extension provides the following 92 commands.

### Drill

```text
az resilience drill add-or-update-resource
az resilience drill create
az resilience drill delete
az resilience drill drill-resource list
az resilience drill drill-resource show
az resilience drill drill-run add-note
az resilience drill drill-run drill-run-resource list
az resilience drill drill-run drill-run-resource show
az resilience drill drill-run fail-over
az resilience drill drill-run generate-report
az resilience drill drill-run list
az resilience drill drill-run list-report-download-url
az resilience drill drill-run mark-as-complete
az resilience drill drill-run reprotect
az resilience drill drill-run resume
az resilience drill drill-run show
az resilience drill end
az resilience drill identity assign
az resilience drill identity remove
az resilience drill identity show
az resilience drill identity wait
az resilience drill list
az resilience drill resync-readiness-check
az resilience drill show
az resilience drill start
az resilience drill update
az resilience drill validate-for-execution
az resilience drill wait
```

### Goal assignment

```text
az resilience goal-assignment create
az resilience goal-assignment delete
az resilience goal-assignment goal-resource list
az resilience goal-assignment goal-resource show
az resilience goal-assignment list
az resilience goal-assignment recommend-capacity
az resilience goal-assignment refresh-goal-resource
az resilience goal-assignment show
az resilience goal-assignment update
az resilience goal-assignment update-goal-resource
az resilience goal-assignment wait
```

### Goal template

```text
az resilience goal-template create
az resilience goal-template delete
az resilience goal-template list
az resilience goal-template show
az resilience goal-template update
az resilience goal-template wait
```

### Recovery plan

```text
az resilience recovery-plan check-readiness
az resilience recovery-plan create
az resilience recovery-plan delete
az resilience recovery-plan failover
az resilience recovery-plan failover-commit
az resilience recovery-plan finalize
az resilience recovery-plan identity assign
az resilience recovery-plan identity remove
az resilience recovery-plan identity show
az resilience recovery-plan identity wait
az resilience recovery-plan list
az resilience recovery-plan recovery-job cancel
az resilience recovery-plan recovery-job list
az resilience recovery-plan recovery-job recovery-job-resource list
az resilience recovery-plan recovery-job recovery-job-resource show
az resilience recovery-plan recovery-job resume
az resilience recovery-plan recovery-job retry
az resilience recovery-plan recovery-job show
az resilience recovery-plan recovery-resource list
az resilience recovery-plan recovery-resource show
az resilience recovery-plan reprotect
az resilience recovery-plan show
az resilience recovery-plan test-failover
az resilience recovery-plan test-failover-cleanup
az resilience recovery-plan update
az resilience recovery-plan update-resource
az resilience recovery-plan validate-for-failover
az resilience recovery-plan validate-for-failover-commit
az resilience recovery-plan validate-for-operation
az resilience recovery-plan validate-for-reprotect
az resilience recovery-plan validate-for-test-failover
az resilience recovery-plan validate-for-test-failover-cleanup
az resilience recovery-plan wait
```

### Unified resilience item

```text
az resilience unified-resilience-item list
az resilience unified-resilience-item show
```

### Usage plan

```text
az resilience usage-plan create
az resilience usage-plan delete
az resilience usage-plan enrollment create
az resilience usage-plan enrollment delete
az resilience usage-plan enrollment list
az resilience usage-plan enrollment show
az resilience usage-plan enrollment update
az resilience usage-plan enrollment wait
az resilience usage-plan list
az resilience usage-plan show
az resilience usage-plan update
az resilience usage-plan wait
```

## Prerequisites

Before running service-group scoped commands:

- Select a subscription and cloud whose Resource Manager endpoint supports API version
	`2026-08-31-preview`.
- Use an existing Microsoft Management service group and grant the caller the required
	Azure Resilience Management permissions at that scope.
- Register resource providers used by the scenario, such as
	`Microsoft.AzureResilienceManagement`, `Microsoft.ManagedIdentity`,
	`Microsoft.Chaos`, `Microsoft.Automation`, and the providers of protected resources.
- Create user-assigned managed identities and grant them access to target, monitoring,
	Chaos, recovery, or Automation resources as required by the selected workflow.
- Create a usage plan and enroll the service group before creating drills or recovery
	plans. The caller needs `Microsoft.AzureResilienceManagement/usagePlans/enrollments/write`.

Commands that accept `--operation-id` require a new caller-generated GUID for each
operation:

```powershell
$operationId = [guid]::NewGuid().Guid
```

Wait for each parent resource and long-running action to finish before starting another
operation on the same resource. Child names such as drill-run, recovery-job, and resource
names must be obtained from the corresponding `list`, `show`, or action response.

## Command reference

The tables below cover every generated command. Parameters in braces describe required
members of a structured argument. For example,
`--drill-asset-properties {region,subscription}` means that both `region` and
`subscription` are required when that object is supplied. Run a command with `--help`
for optional parameters, accepted enum values, shorthand syntax, and generic Azure CLI
arguments.

### Usage plans and enrollments

| Command | Required parameters | Purpose and prerequisites |
|--|--|--|
| `usage-plan create` | `--resource-group`, `--usage-plan-name`, `--location` | Create a subscription/resource-group scoped plan. Specify `--plan-type Basic` or `Standard`; the service currently uses `global` as the location. |
| `usage-plan delete` | `--resource-group`, `--usage-plan-name` | Delete an existing plan after its enrollments are removed. |
| `usage-plan list` | None | List plans by subscription; optionally filter with `--resource-group`. |
| `usage-plan show` | `--resource-group`, `--usage-plan-name` | Get an existing plan. |
| `usage-plan update` | `--resource-group`, `--usage-plan-name` | Update mutable plan properties such as tags. |
| `usage-plan wait` | `--resource-group`, `--usage-plan-name`, one wait condition | Wait for `--created`, `--updated`, `--deleted`, `--exists`, or a custom condition. |
| `usage-plan enrollment create` | `--resource-group`, `--usage-plan-name`, `--enrollment-name`, `--service-group-id` | Enroll an existing service group in an existing plan. The service-group ID has the form `/providers/Microsoft.Management/serviceGroups/<name>`. |
| `usage-plan enrollment delete` | `--resource-group`, `--usage-plan-name`, `--enrollment-name` | Remove an existing enrollment. |
| `usage-plan enrollment list` | `--resource-group`, `--usage-plan-name` | List enrollments under an existing plan. |
| `usage-plan enrollment show` | `--resource-group`, `--usage-plan-name`, `--enrollment-name` | Get an existing enrollment. |
| `usage-plan enrollment update` | `--resource-group`, `--usage-plan-name`, `--enrollment-name` | Update an enrollment; supply `--service-group-id` when changing its association. |
| `usage-plan enrollment wait` | `--resource-group`, `--usage-plan-name`, `--enrollment-name`, one wait condition | Wait for an enrollment state. |

### Goal templates

| Command | Required parameters | Purpose and prerequisites |
|--|--|--|
| `goal-template create` | `--service-group-name`, `--goal-template-name` | Create a template. Supply `--goal-type Resiliency`; HA/DR requirements and ISO 8601 RPO/RTO values are optional scenario settings. |
| `goal-template delete` | `--service-group-name`, `--goal-template-name` | Delete a template that is not referenced by an assignment. |
| `goal-template list` | `--service-group-name` | List templates in a service group. |
| `goal-template show` | `--service-group-name`, `--goal-template-name` | Get an existing template. |
| `goal-template update` | `--service-group-name`, `--goal-template-name` | Update mutable goal, HA/DR, RPO, or RTO settings. |
| `goal-template wait` | `--service-group-name`, `--goal-template-name`, one wait condition | Wait for a template state. |

### Goal assignments and resources

| Command | Required parameters | Purpose and prerequisites |
|--|--|--|
| `goal-assignment create` | `--service-group-name`, `--goal-assignment-name`, `--goal-assignment-type`, `--goal-template-id` | Assign an existing template. Each supplied `--service-level-resources` item requires `service-level-indicator-resource-id`. |
| `goal-assignment delete` | `--service-group-name`, `--goal-assignment-name` | Delete an existing assignment. |
| `goal-assignment list` | `--service-group-name` | List assignments in a service group. |
| `goal-assignment recommend-capacity` | `--service-group-name`, `--goal-assignment-name`, `--resource-ids` | Request capacity recommendations for ARM resource IDs under an existing assignment. |
| `goal-assignment refresh-goal-resource` | `--service-group-name`, `--goal-assignment-name` | Refresh discovery and evaluation of goal resources. |
| `goal-assignment show` | `--service-group-name`, `--goal-assignment-name` | Get an existing assignment. |
| `goal-assignment update` | `--service-group-name`, `--goal-assignment-name` | Update template, type, zonal requirement, or service-level resources. Preserve required assignment properties. |
| `goal-assignment update-goal-resource` | `--service-group-name`, `--goal-assignment-name`, `--resources` | Update discovered goal resources. Confirmation entries require `confirmation-status` and `solution-display-name`. |
| `goal-assignment wait` | `--service-group-name`, `--goal-assignment-name`, one wait condition | Wait for an assignment state. |
| `goal-assignment goal-resource list` | `--service-group-name`, `--goal-assignment-name` | List resources discovered for an assignment. |
| `goal-assignment goal-resource show` | `--service-group-name`, `--goal-assignment-name`, `--goal-resource-name` | Get a goal-resource name returned by `goal-resource list`. |

### Drills

| Command | Required parameters | Purpose and prerequisites |
|--|--|--|
| `drill create` | `--service-group-name`, `--drill-name`, one of `--regional` or `--zonal` | Create a drill in an enrolled service group. Chaos identities require `{type,user-assigned-identity}`; drill assets require `{region,subscription}`. Monitoring and recovery-plan objects have scenario-specific identity and resource-ID requirements. |
| `drill delete` | `--service-group-name`, `--drill-name` | Delete an existing non-running drill. |
| `drill list` | `--service-group-name` | List drills in a service group. |
| `drill show` | `--service-group-name`, `--drill-name` | Get an existing drill. |
| `drill update` | `--service-group-name`, `--drill-name` | Update mutable drill settings while the drill is not running. |
| `drill wait` | `--service-group-name`, `--drill-name`, one wait condition | Wait for a drill state. |
| `drill add-or-update-resource` | `--service-group-name`, `--drill-name`, `--operation-id`, `--fault-duration-in-min` | Add, update, or exclude drill resources. Included/updated entries require a drill-resource `id`; custom faults require `fault-name` and `script-resource-id`, while overridden faults require `fault-name`, `fault-urn`, and `target-resource-id`. |
| `drill resync-readiness-check` | `--service-group-name`, `--drill-name`, `--operation-id` | Re-evaluate readiness after resources or permissions change. |
| `drill validate-for-execution` | `--service-group-name`, `--drill-name`, `--operation-id` | Validate that a provisioned drill is ready to start. |
| `drill start` | `--service-group-name`, `--drill-name`, `--operation-id`, `--mode` | Start a ready drill. Capture the returned drill-run name. |
| `drill end` | `--service-group-name`, `--drill-name`, `--operation-id`, `--attestation`, `--attestation-notes` | End a running drill and record its attestation. |
| `drill drill-resource list` | `--service-group-name`, `--drill-name` | List resources included in an existing drill. |
| `drill drill-resource show` | `--service-group-name`, `--drill-name`, `--drill-resource-name` | Get a drill-resource name returned by `drill-resource list`. |
| `drill identity assign` | `--service-group-name`, `--drill-name`, identity option | Assign `--system-assigned` and/or `--user-assigned` identities to an existing drill. |
| `drill identity remove` | `--service-group-name`, `--drill-name`, identity option | Remove selected identities from an existing non-running drill. |
| `drill identity show` | `--service-group-name`, `--drill-name` | Show the drill identity. |
| `drill identity wait` | `--service-group-name`, `--drill-name`, one wait condition | Wait for the drill identity resource. |

### Drill runs

| Command | Required parameters | Purpose and prerequisites |
|--|--|--|
| `drill drill-run list` | `--service-group-name`, `--drill-name` | List runs for an existing drill. |
| `drill drill-run show` | `--service-group-name`, `--drill-name`, `--drill-run-name` | Get a run returned by `drill-run list` or `drill start`. |
| `drill drill-run add-note` | `--service-group-name`, `--drill-name`, `--drill-run-name`, `--operation-id` | Add a note to an existing run; supply the optional note body as required by the scenario. |
| `drill drill-run fail-over` | `--service-group-name`, `--drill-name`, `--drill-run-name`, `--operation-id`, failover request | Fail over a running drill. The request requires `failover-direction`, `source-locations`, and `user-consent`. |
| `drill drill-run generate-report` | `--service-group-name`, `--drill-name`, `--drill-run-name`, `--operation-id` | Generate a report after the run has sufficient execution data. |
| `drill drill-run list-report-download-url` | `--service-group-name`, `--drill-name`, `--drill-run-name`, `--operation-id` | Obtain download URLs after report generation completes. |
| `drill drill-run mark-as-complete` | `--service-group-name`, `--drill-name`, `--drill-run-name`, `--operation-id`, `--drill-run-stage` | Complete the current manual stage of a run. |
| `drill drill-run reprotect` | `--service-group-name`, `--drill-name`, `--drill-run-name`, `--operation-id` | Reprotect resources after a supported failover stage. |
| `drill drill-run resume` | `--service-group-name`, `--drill-name`, `--drill-run-name`, `--operation-id` | Resume a paused run. |
| `drill drill-run drill-run-resource list` | `--service-group-name`, `--drill-name`, `--drill-run-name` | List resources processed by a run. |
| `drill drill-run drill-run-resource show` | `--service-group-name`, `--drill-name`, `--drill-run-name`, `--drill-run-resource-name` | Get a run-resource name returned by the corresponding list command. |

### Recovery plans

| Command | Required parameters | Purpose and prerequisites |
|--|--|--|
| `recovery-plan create` | `--service-group-name`, `--recovery-plan-name`, `--plan-type`, `--plan-description`, `--recovery-groups-setting` | Create a plan in an enrolled service group. `recovery-groups-setting.default-group` requires `description`, `group-unique-id`, and `order-id`; every pre/post action requires `name` and `timeout-in-minutes`. |
| `recovery-plan delete` | `--service-group-name`, `--recovery-plan-name` | Delete a plan with no active recovery job. |
| `recovery-plan list` | `--service-group-name` | List recovery plans in a service group. |
| `recovery-plan show` | `--service-group-name`, `--recovery-plan-name` | Get an existing plan. |
| `recovery-plan update` | `--service-group-name`, `--recovery-plan-name` | Update description or recovery-group settings while no operation is active. |
| `recovery-plan wait` | `--service-group-name`, `--recovery-plan-name`, one wait condition | Wait for a recovery-plan state. |
| `recovery-plan check-readiness` | `--service-group-name`, `--recovery-plan-name`, `--operation-id` | Start a readiness evaluation. |
| `recovery-plan update-resource` | `--service-group-name`, `--recovery-plan-name`, `--operation-id`, update request | Add/update entries that include `type` and `resource-id`, or remove existing recovery-resource IDs. |
| `recovery-plan validate-for-operation` | `--service-group-name`, `--recovery-plan-name`, `--operation-id`, `--operation-name` | Validate one of `Failover`, `FailoverCommit`, `Reprotect`, `TestFailover`, or `TestFailoverCleanup`. |
| `recovery-plan validate-for-failover` | `--service-group-name`, `--recovery-plan-name`, `--operation-id`, `--failover-direction`, failover request | Validate failover; request requires `source-locations` and `user-consent`. |
| `recovery-plan validate-for-test-failover` | `--service-group-name`, `--recovery-plan-name`, `--operation-id`, `--failover-direction`, failover request | Validate test failover with source locations and user consent. |
| `recovery-plan validate-for-failover-commit` | `--service-group-name`, `--recovery-plan-name`, `--operation-id` | Validate commit after a completed failover. |
| `recovery-plan validate-for-reprotect` | `--service-group-name`, `--recovery-plan-name`, `--operation-id` | Validate reprotection in a compatible post-failover state. |
| `recovery-plan validate-for-test-failover-cleanup` | `--service-group-name`, `--recovery-plan-name`, `--operation-id` | Validate cleanup after test failover. |
| `recovery-plan failover` | `--service-group-name`, `--recovery-plan-name`, `--operation-id`, `--failover-direction`, failover request | Execute validated failover. The request requires `source-locations` and `user-consent`. |
| `recovery-plan test-failover` | `--service-group-name`, `--recovery-plan-name`, `--operation-id`, `--failover-direction`, failover request | Execute a validated test failover. |
| `recovery-plan failover-commit` | `--service-group-name`, `--recovery-plan-name`, `--operation-id` | Commit a successfully completed failover. |
| `recovery-plan reprotect` | `--service-group-name`, `--recovery-plan-name`, `--operation-id` | Reprotect resources after failover. |
| `recovery-plan test-failover-cleanup` | `--service-group-name`, `--recovery-plan-name`, `--operation-id` | Clean up resources created by test failover. |
| `recovery-plan finalize` | `--service-group-name`, `--recovery-plan-name`, `--operation-id` | Finalize a completed recovery workflow. |
| `recovery-plan recovery-resource list` | `--service-group-name`, `--recovery-plan-name` | List resources discovered or added to a plan. |
| `recovery-plan recovery-resource show` | `--service-group-name`, `--recovery-plan-name`, `--recovery-resource-name` | Get a recovery-resource name returned by the corresponding list command. |
| `recovery-plan identity assign` | `--service-group-name`, `--recovery-plan-name`, identity option | Assign `--system-assigned` and/or `--user-assigned` identities to an idle plan. |
| `recovery-plan identity remove` | `--service-group-name`, `--recovery-plan-name`, identity option | Remove selected identities from an idle plan. |
| `recovery-plan identity show` | `--service-group-name`, `--recovery-plan-name` | Show the recovery-plan identity. |
| `recovery-plan identity wait` | `--service-group-name`, `--recovery-plan-name`, one wait condition | Wait for the recovery-plan identity resource. |

### Recovery jobs

| Command | Required parameters | Purpose and prerequisites |
|--|--|--|
| `recovery-plan recovery-job list` | `--service-group-name`, `--recovery-plan-name` | List jobs produced by recovery-plan actions. |
| `recovery-plan recovery-job show` | `--service-group-name`, `--recovery-plan-name`, `--recovery-job-name` | Get a job returned by `recovery-job list` or an action. |
| `recovery-plan recovery-job cancel` | `--service-group-name`, `--recovery-plan-name`, `--recovery-job-name`, `--operation-id` | Cancel a job whose current state supports cancellation. |
| `recovery-plan recovery-job resume` | `--service-group-name`, `--recovery-plan-name`, `--recovery-job-name`, `--operation-id` | Resume a paused or waiting job. |
| `recovery-plan recovery-job retry` | `--service-group-name`, `--recovery-plan-name`, `--recovery-job-name`, `--operation-id` | Retry a failed job that the service marks retryable. |
| `recovery-plan recovery-job recovery-job-resource list` | `--service-group-name`, `--recovery-plan-name`, `--recovery-job-name` | List resources processed by a recovery job. |
| `recovery-plan recovery-job recovery-job-resource show` | `--service-group-name`, `--recovery-plan-name`, `--recovery-job-name`, `--recovery-job-resource-name` | Get a job-resource name returned by the corresponding list command. |

### Unified resilience items

| Command | Required parameters | Purpose and prerequisites |
|--|--|--|
| `unified-resilience-item list` | `--service-group-name` | List aggregated resilience items. The caller needs service-specific read authorization and the service group must contain discoverable resources. |
| `unified-resilience-item show` | `--service-group-name`, `--unified-resilience-item-name` | Get an item name returned by `unified-resilience-item list`. |

## Usage examples

Set reusable values and create a client-generated operation ID:

```powershell
$serviceGroup = "MyServiceGroup"
$subscriptionId = az account show --query id --output tsv
$operationId = [guid]::NewGuid().Guid
```

Create a usage plan and enroll the service group:

```bash
az resilience usage-plan create \
	--resource-group MyResourceGroup \
	--usage-plan-name MyUsagePlan \
	--location global \
	--plan-type Standard

az resilience usage-plan enrollment create \
	--resource-group MyResourceGroup \
	--usage-plan-name MyUsagePlan \
	--enrollment-name MyEnrollment \
	--service-group-id /providers/Microsoft.Management/serviceGroups/MyServiceGroup
```

Create a goal template and assignment:

```bash
az resilience goal-template create \
	--service-group-name MyServiceGroup \
	--goal-template-name MyGoalTemplate \
	--goal-type Resiliency \
	--require-high-availability Required \
	--regional-recovery-time-objective PT30M

az resilience goal-assignment create \
	--service-group-name MyServiceGroup \
	--goal-assignment-name MyGoalAssignment \
	--goal-assignment-type Resiliency \
	--goal-template-id /providers/Microsoft.Management/serviceGroups/MyServiceGroup/providers/Microsoft.AzureResilienceManagement/goalTemplates/MyGoalTemplate
```

Create a minimal recovery plan with a default recovery group:

```powershell
$groupId = [guid]::NewGuid().Guid
$groups = "{defaultGroup:{description:DefaultGroup,groupUniqueId:$groupId,orderId:0}}"

az resilience recovery-plan create `
	--service-group-name $serviceGroup `
	--recovery-plan-name MyRecoveryPlan `
	--plan-type Regional `
	--plan-description "My recovery plan" `
	--recovery-groups-setting $groups
```

Validate a failover request before executing it:

```powershell
$operationId = [guid]::NewGuid().Guid
$request = "{sourceLocations:[eastus],executionConfigurations:{userConsent:Allowed}}"

az resilience recovery-plan validate-for-failover `
	--service-group-name $serviceGroup `
	--recovery-plan-name MyRecoveryPlan `
	--operation-id $operationId `
	--failover-direction FromSpecificLocations `
	--failover-request-properties $request
```

List goal templates for a service group:

```bash
az resilience goal-template list --service-group-name MyServiceGroup
```

List drills for a service group:

```bash
az resilience drill list --service-group-name MyServiceGroup
```

Show a recovery plan:

```bash
az resilience recovery-plan show \
	--service-group-name MyServiceGroup \
	--recovery-plan-name MyRecoveryPlan
```

List usage plans in the current subscription or in a resource group:

```bash
az resilience usage-plan list
az resilience usage-plan list --resource-group MyResourceGroup
```

Clean up child resources before their parents:

```bash
az resilience goal-assignment delete \
	--service-group-name MyServiceGroup \
	--goal-assignment-name MyGoalAssignment \
	--yes

az resilience goal-template delete \
	--service-group-name MyServiceGroup \
	--goal-template-name MyGoalTemplate \
	--yes
```

For the complete command and argument reference, run:

```bash
az resilience --help
az resilience <command-group> --help
```