# Azure Resilience Management CLI Team Testing Guide

This guide divides all 92 `az resilience` commands into independent test areas. It
is intended for handoff to feature teams testing API version
`2026-08-31-preview`.

## How to read the tables

- **CLI-required** lists arguments enforced by the generated command parser.
- **Scenario inputs and effect** lists optional arguments and inputs that the
  service may require for a useful scenario.
- `--operation-id` must be a new caller-generated GUID for every action.
- Add `--no-wait` to a long-running command to return immediately instead of
  waiting for completion.
- List commands accept `--top` to limit the page and `--skip-token` to continue
  from a service-provided token when those arguments are exposed.
- Wait commands require one condition such as `--created`, `--updated`,
  `--deleted`, `--exists`, or `--custom`; use `--interval` and `--timeout` to
  control polling.
- Resource names used by child `show` and action commands must come from their
  corresponding parent response or `list` command.

## Shared test setup

```powershell
$serviceGroup = "<service-group-name>"
$resourceGroup = "<resource-group-name>"
$usagePlan = "<usage-plan-name>"
$operationId = [guid]::NewGuid().Guid
```

Before feature testing:

1. Select a subscription and cloud that supports the preview API.
2. Register `Microsoft.AzureResilienceManagement` and providers used by the
   protected resources.
3. Grant the tester and managed identities the required permissions.
4. Create a usage plan and enroll the service group.
5. Add representative resources to the service group.
6. Do not run concurrent actions against the same drill or recovery plan.

## Team assignment summary

| Team package | Command count | Primary responsibility |
|---|---:|---|
| Platform onboarding | 12 | Usage plans and service-group enrollment |
| Goals | 17 | Goal templates, assignments, recommendations, and resources |
| Drills | 28 | Drill definition, identity, execution, runs, and reports |
| Recovery operations (RO) | 33 | Recovery plans, identity, actions, jobs, and resources |
| Unified inventory | 2 | Aggregated resilience discovery |
| **Total** | **92** | |

## Team 1: Platform onboarding

Create the usage plan before enrollment. Delete enrollments before deleting the
plan. The service currently expects `global` for the usage-plan location.

| CLI | CLI-required | Scenario inputs and effect |
|---|---|---|
| `az resilience usage-plan create` | `--resource-group`, `--usage-plan-name`, `--location` | `--plan-type Basic|Standard` selects the plan tier; `--tags` adds ARM metadata; use `--location global`. |
| `az resilience usage-plan show` | `--resource-group`, `--usage-plan-name` | Read-only verification of properties and provisioning state. |
| `az resilience usage-plan list` | None | `--resource-group` changes scope from subscription to one resource group; pagination controls page size/continuation. |
| `az resilience usage-plan update` | `--resource-group`, `--usage-plan-name` | `--plan-type` sends a tier change; `--tags` replaces/updates resource tags. |
| `az resilience usage-plan delete` | `--resource-group`, `--usage-plan-name` | `--yes` skips confirmation; `--no-wait` returns before deletion completes. Remove enrollments first. |
| `az resilience usage-plan wait` | `--resource-group`, `--usage-plan-name`, wait condition | Polls until the selected condition; `--interval` and `--timeout` tune polling. |
| `az resilience usage-plan enrollment create` | `--resource-group`, `--usage-plan-name`, `--enrollment-name` | `--service-group-id` associates `/providers/Microsoft.Management/serviceGroups/<name>`; although optional in the CLI schema, it is needed for a useful enrollment. |
| `az resilience usage-plan enrollment show` | `--resource-group`, `--usage-plan-name`, `--enrollment-name` | Read-only verification of the service-group association. |
| `az resilience usage-plan enrollment list` | `--resource-group`, `--usage-plan-name` | Lists enrolled service groups; pagination controls page traversal. |
| `az resilience usage-plan enrollment update` | `--resource-group`, `--usage-plan-name`, `--enrollment-name` | `--service-group-id` changes the associated service group; `--no-wait` returns immediately. |
| `az resilience usage-plan enrollment delete` | `--resource-group`, `--usage-plan-name`, `--enrollment-name` | `--yes` skips confirmation; `--no-wait` returns immediately. |
| `az resilience usage-plan enrollment wait` | `--resource-group`, `--usage-plan-name`, `--enrollment-name`, wait condition | Polls enrollment provisioning or deletion state. |

### Platform acceptance flow

`usage-plan create` -> `usage-plan show/list` -> `enrollment create` ->
`enrollment show/list/update` -> `enrollment delete` -> `usage-plan delete`.

## Team 2: Goals

Create a goal template before a goal assignment. Goal resources appear after the
assignment is evaluated or refreshed.

### Goal templates

| CLI | CLI-required | Scenario inputs and effect |
|---|---|---|
| `az resilience goal-template create` | `--service-group-name`, `--goal-template-name` | `--goal-type Resiliency` identifies the goal; `--require-high-availability` and `--require-disaster-recovery` enable those evaluations; regional RPO/RTO arguments set ISO 8601 targets such as `PT15M`. |
| `az resilience goal-template show` | `--service-group-name`, `--goal-template-name` | Read-only verification of the template. |
| `az resilience goal-template list` | `--service-group-name` | `--top` limits results; `--skip-token` continues a page. |
| `az resilience goal-template update` | `--service-group-name`, `--goal-template-name` | Goal type, HA/DR requirements, and regional RPO/RTO arguments change the corresponding policy targets; `--no-wait` returns immediately. |
| `az resilience goal-template delete` | `--service-group-name`, `--goal-template-name` | `--yes` skips confirmation; delete assignments referencing the template first. |
| `az resilience goal-template wait` | `--service-group-name`, `--goal-template-name`, wait condition | Polls the selected resource condition. |

### Goal assignments and resources

| CLI | CLI-required | Scenario inputs and effect |
|---|---|---|
| `az resilience goal-assignment create` | `--service-group-name`, `--goal-assignment-name` | `--goal-assignment-type Resiliency` selects assignment behavior; `--goal-template-id` links the template; `--require-zonal-resiliency` enables zonal evaluation; `--service-level-resources` links SLI/SLO ARM IDs. Type and template are needed for the normal scenario even though the CLI schema marks them optional. |
| `az resilience goal-assignment show` | `--service-group-name`, `--goal-assignment-name` | Read-only verification of assignment and evaluation state. |
| `az resilience goal-assignment list` | `--service-group-name` | `--top` limits results; `--skip-token` continues a page. |
| `az resilience goal-assignment update` | `--service-group-name`, `--goal-assignment-name` | Supplying type, template ID, zonal requirement, or service-level resources changes only those assignment settings; `--no-wait` returns immediately. |
| `az resilience goal-assignment delete` | `--service-group-name`, `--goal-assignment-name` | `--yes` skips confirmation; `--no-wait` returns immediately. |
| `az resilience goal-assignment wait` | `--service-group-name`, `--goal-assignment-name`, wait condition | Polls assignment provisioning or deletion. |
| `az resilience goal-assignment recommend-capacity` | `--service-group-name`, `--goal-assignment-name`, `--resource-ids` | Requests capacity recommendations only for the supplied ARM resource IDs. |
| `az resilience goal-assignment refresh-goal-resource` | `--service-group-name`, `--goal-assignment-name` | Re-runs resource discovery and goal evaluation after membership or configuration changes. |
| `az resilience goal-assignment update-goal-resource` | `--service-group-name`, `--goal-assignment-name`, `--resources` | Each resource can change HA/DR/zonal participation and attestation. User confirmations require `confirmation-status` and `solution-display-name`; exclusion or attestation fields affect recommendation evaluation. |
| `az resilience goal-assignment goal-resource list` | `--service-group-name`, `--goal-assignment-name` | Lists discovered/evaluated resources; pagination controls page traversal. |
| `az resilience goal-assignment goal-resource show` | `--service-group-name`, `--goal-assignment-name`, `--goal-resource-name` | Shows one resource name returned by `goal-resource list`. |

### Goals acceptance flow

`goal-template create` -> `goal-assignment create` -> `refresh-goal-resource` ->
`goal-resource list/show` -> `recommend-capacity` ->
`update-goal-resource` -> update commands -> cleanup.

## Team 3: Drills

A drill requires enrolled service-group resources and identities with access to
Chaos, monitoring, recovery, and protected resources used by the scenario.

### Drill definition, resources, and identity

| CLI | CLI-required | Scenario inputs and effect |
|---|---|---|
| `az resilience drill create` | `--service-group-name`, `--drill-name` | Supply exactly one of `--regional` or `--zonal` to select drill type. `--system-assigned`/`--user-assigned` attach identities. `--drill-asset-properties` selects subscription, region, and optional resource group. Chaos, health-model, SLI, monitoring, and recovery-plan objects enable those integrations. `--rbac-setup-mode` chooses automated built-in/custom roles or manual setup. |
| `az resilience drill show` | `--service-group-name`, `--drill-name` | Read-only verification of configuration and readiness. |
| `az resilience drill list` | `--service-group-name` | `--top` limits results; `--skip-token` continues a page. |
| `az resilience drill update` | `--service-group-name`, `--drill-name` | Supplied regional, asset, Chaos, monitoring, RBAC, recovery-plan, or SLI settings replace those portions. Do not run while executing. The current generated update path is affected by the missing read-visible `drillType` defect. |
| `az resilience drill delete` | `--service-group-name`, `--drill-name` | Deletes a non-running drill; `--yes` skips confirmation and `--no-wait` returns immediately. |
| `az resilience drill wait` | `--service-group-name`, `--drill-name`, wait condition | Polls drill provisioning or deletion. |
| `az resilience drill add-or-update-resource` | `--service-group-name`, `--drill-name`, `--operation-id`, `--fault-duration-in-min` | `--resource-lists` includes, updates, or excludes resources. Custom faults need fault name and script resource ID; overridden faults need fault name, fault URN, and target resource ID. `--force-inclusion-and-update` overrides normal inclusion behavior. |
| `az resilience drill resync-readiness-check` | `--service-group-name`, `--drill-name`, `--operation-id` | Re-evaluates readiness after resources, RBAC, or configuration changes. |
| `az resilience drill validate-for-execution` | `--service-group-name`, `--drill-name`, `--operation-id` | `--validate-for-execution-properties` narrows/configures validation when supplied; otherwise validates the configured drill. |
| `az resilience drill drill-resource list` | `--service-group-name`, `--drill-name` | Lists resources participating in the drill; pagination controls page traversal. |
| `az resilience drill drill-resource show` | `--service-group-name`, `--drill-name`, `--drill-resource-name` | Shows one name returned by `drill-resource list`. |
| `az resilience drill identity assign` | `--service-group-name`, `--drill-name` | `--system-assigned` enables the system identity; `--user-assigned` adds identity resource IDs. At least one identity option is needed for a meaningful assignment. |
| `az resilience drill identity remove` | `--service-group-name`, `--drill-name` | `--system-assigned` removes the system identity; `--user-assigned` removes selected IDs. Do not remove identities while running. |
| `az resilience drill identity show` | `--service-group-name`, `--drill-name` | Read-only identity verification. |
| `az resilience drill identity wait` | `--service-group-name`, `--drill-name`, wait condition | Polls identity update state. |

### Drill execution, runs, and reports

| CLI | CLI-required | Scenario inputs and effect |
|---|---|---|
| `az resilience drill start` | `--service-group-name`, `--drill-name`, `--operation-id`, `--mode` | Starts a validated drill in the selected execution mode; capture the returned drill-run GUID. |
| `az resilience drill end` | `--service-group-name`, `--drill-name`, `--operation-id`, `--attestation`, `--attestation-notes` | Ends the active drill and records the tester's attestation and notes. |
| `az resilience drill drill-run list` | `--service-group-name`, `--drill-name` | Lists runs; pagination traverses additional pages. |
| `az resilience drill drill-run show` | `--service-group-name`, `--drill-name`, `--drill-run-name` | Shows one run GUID returned by start/list. |
| `az resilience drill drill-run add-note` | `--service-group-name`, `--drill-name`, `--drill-run-name`, `--operation-id` | `--notes` appends tester/operator context to the run. |
| `az resilience drill drill-run fail-over` | `--service-group-name`, `--drill-name`, `--drill-run-name`, `--operation-id` | `--auto-failover Enable|Disable` controls pausing for manual input. `--failover-properties` supplies direction plus source locations, optional selected resource IDs, and execution user consent. |
| `az resilience drill drill-run mark-as-complete` | `--service-group-name`, `--drill-name`, `--drill-run-name`, `--operation-id`, `--drill-run-stage` | Marks the specified manual stage complete so orchestration can continue. |
| `az resilience drill drill-run resume` | `--service-group-name`, `--drill-name`, `--drill-run-name`, `--operation-id` | Resumes a paused run. |
| `az resilience drill drill-run reprotect` | `--service-group-name`, `--drill-name`, `--drill-run-name`, `--operation-id` | `--reprotect-properties` selects/configures resources for reprotection after failover. |
| `az resilience drill drill-run generate-report` | `--service-group-name`, `--drill-name`, `--drill-run-name`, `--operation-id` | Generates a report after sufficient run data exists. |
| `az resilience drill drill-run list-report-download-url` | `--service-group-name`, `--drill-name`, `--drill-run-name`, `--operation-id` | `--format` selects the requested report representation and returns temporary download URLs. |
| `az resilience drill drill-run drill-run-resource list` | `--service-group-name`, `--drill-name`, `--drill-run-name` | Lists resources processed by the run; pagination traverses pages. |
| `az resilience drill drill-run drill-run-resource show` | `--service-group-name`, `--drill-name`, `--drill-run-name`, `--drill-run-resource-name` | Shows one run resource returned by the list command. |

### Drills acceptance flow

Create -> identity/RBAC -> add resources -> resync readiness -> validate -> start ->
run actions -> end -> generate/download report -> inspect resources -> delete.

## Team 4: Recovery operations (RO)

Recovery commands are stateful. Run the matching `validate-for-*` command before
the destructive action and wait for each recovery job to finish.

### Recovery-plan definition, resources, and identity

| CLI | CLI-required | Scenario inputs and effect |
|---|---|---|
| `az resilience recovery-plan create` | `--service-group-name`, `--recovery-plan-name` | The normal service scenario also needs `--plan-type Regional|Zonal`, `--plan-description`, and `--recovery-groups-setting`. The default group requires description, unique GUID, and order; actions require name and timeout. `--system-assigned`/`--user-assigned` attach identities. |
| `az resilience recovery-plan show` | `--service-group-name`, `--recovery-plan-name` | Read-only verification of configuration and readiness. |
| `az resilience recovery-plan list` | `--service-group-name` | `--top` limits results; `--skip-token` continues a page. |
| `az resilience recovery-plan update` | `--service-group-name`, `--recovery-plan-name` | `--plan-description` changes text; `--recovery-groups-setting` replaces orchestration groups/actions. The current generated update path is affected by the missing read-visible `planType` defect. |
| `az resilience recovery-plan delete` | `--service-group-name`, `--recovery-plan-name` | Deletes an idle plan; `--yes` skips confirmation and `--no-wait` returns immediately. |
| `az resilience recovery-plan wait` | `--service-group-name`, `--recovery-plan-name`, wait condition | Polls plan provisioning or deletion. |
| `az resilience recovery-plan check-readiness` | `--service-group-name`, `--recovery-plan-name`, `--operation-id` | Re-evaluates whether the plan, resources, identities, and permissions are ready. |
| `az resilience recovery-plan update-resource` | `--service-group-name`, `--recovery-plan-name`, `--operation-id` | `--resources-to-update` adds/changes entries with resource ID and protection type; `--resources-to-remove` removes existing recovery-resource IDs. |
| `az resilience recovery-plan recovery-resource list` | `--service-group-name`, `--recovery-plan-name` | Lists resources attached/discovered for the plan; pagination traverses pages. |
| `az resilience recovery-plan recovery-resource show` | `--service-group-name`, `--recovery-plan-name`, `--recovery-resource-name` | Shows one resource GUID returned by the list command. |
| `az resilience recovery-plan identity assign` | `--service-group-name`, `--recovery-plan-name` | `--system-assigned` enables the system identity; `--user-assigned` adds identity resource IDs. |
| `az resilience recovery-plan identity remove` | `--service-group-name`, `--recovery-plan-name` | `--system-assigned` removes the system identity; `--user-assigned` removes selected IDs. The plan must be idle. |
| `az resilience recovery-plan identity show` | `--service-group-name`, `--recovery-plan-name` | Read-only identity verification. |
| `az resilience recovery-plan identity wait` | `--service-group-name`, `--recovery-plan-name`, wait condition | Polls identity update state. |

### Recovery validation and execution

For failover request objects, `source-locations` and
`execution-configurations.user-consent` are required when the object is supplied.
`selected-resource-ids` restricts execution; omitting it processes all qualified
resources in the source locations.

| CLI | CLI-required | Scenario inputs and effect |
|---|---|---|
| `az resilience recovery-plan validate-for-operation` | `--service-group-name`, `--recovery-plan-name`, `--operation-id`, `--operation-name` | Runs generic validation for `Failover`, `FailoverCommit`, `Reprotect`, `TestFailover`, or `TestFailoverCleanup`. |
| `az resilience recovery-plan validate-for-failover` | `--service-group-name`, `--recovery-plan-name`, `--operation-id`, `--failover-direction` | `--failover-request-properties` supplies source locations, consent, and optional selected resources without executing failover. |
| `az resilience recovery-plan failover` | `--service-group-name`, `--recovery-plan-name`, `--operation-id`, `--failover-direction` | Same request object as validation; executes production failover and creates a recovery job. |
| `az resilience recovery-plan validate-for-failover-commit` | `--service-group-name`, `--recovery-plan-name`, `--operation-id` | Checks whether a completed failover can be committed. |
| `az resilience recovery-plan failover-commit` | `--service-group-name`, `--recovery-plan-name`, `--operation-id` | Commits a successfully completed failover. |
| `az resilience recovery-plan validate-for-reprotect` | `--service-group-name`, `--recovery-plan-name`, `--operation-id` | `--reprotect-request-properties` selects/configures resources for validation. |
| `az resilience recovery-plan reprotect` | `--service-group-name`, `--recovery-plan-name`, `--operation-id` | `--reprotect-request-properties` selects/configures resources and executes reprotection. |
| `az resilience recovery-plan validate-for-test-failover` | `--service-group-name`, `--recovery-plan-name`, `--operation-id`, `--failover-direction` | Validates a non-production failover using optional selected resources in the request object. |
| `az resilience recovery-plan test-failover` | `--service-group-name`, `--recovery-plan-name`, `--operation-id`, `--failover-direction` | Executes the validated non-production failover and creates a recovery job. |
| `az resilience recovery-plan validate-for-test-failover-cleanup` | `--service-group-name`, `--recovery-plan-name`, `--operation-id` | Checks whether test-created resources can be cleaned up. |
| `az resilience recovery-plan test-failover-cleanup` | `--service-group-name`, `--recovery-plan-name`, `--operation-id` | `--comments` records operator context while cleaning test-failover resources. |
| `az resilience recovery-plan finalize` | `--service-group-name`, `--recovery-plan-name`, `--operation-id` | Finalizes a completed recovery workflow after all required stages. |

### Recovery jobs and job resources

| CLI | CLI-required | Scenario inputs and effect |
|---|---|---|
| `az resilience recovery-plan recovery-job list` | `--service-group-name`, `--recovery-plan-name` | Lists jobs created by recovery actions; pagination traverses pages. |
| `az resilience recovery-plan recovery-job show` | `--service-group-name`, `--recovery-plan-name`, `--recovery-job-name` | Shows one job GUID returned by an action/list command. |
| `az resilience recovery-plan recovery-job cancel` | `--service-group-name`, `--recovery-plan-name`, `--recovery-job-name`, `--operation-id` | Cancels a cancellable job; `--description` records operator input/reason. |
| `az resilience recovery-plan recovery-job resume` | `--service-group-name`, `--recovery-plan-name`, `--recovery-job-name`, `--operation-id` | Resumes a paused/waiting job; `--description` supplies operator input. |
| `az resilience recovery-plan recovery-job retry` | `--service-group-name`, `--recovery-plan-name`, `--recovery-job-name`, `--operation-id` | Retries a failed job only when the service marks it retryable. |
| `az resilience recovery-plan recovery-job recovery-job-resource list` | `--service-group-name`, `--recovery-plan-name`, `--recovery-job-name` | Lists resources processed by the job; pagination traverses pages. |
| `az resilience recovery-plan recovery-job recovery-job-resource show` | `--service-group-name`, `--recovery-plan-name`, `--recovery-job-name`, `--recovery-job-resource-name` | Shows one job-resource GUID returned by the list command. |

### Recovery acceptance flows

Production: create -> identity -> update resources -> readiness -> validate failover ->
failover -> inspect job -> validate/commit -> validate/reprotect -> finalize.

Test: validate test failover -> test failover -> inspect job/resources -> validate
cleanup -> cleanup -> finalize.

## Team 5: Unified inventory

| CLI | CLI-required | Scenario inputs and effect |
|---|---|---|
| `az resilience unified-resilience-item list` | `--service-group-name` | `--top` limits results and `--skip-token` continues a page. The service group must contain discoverable resources. |
| `az resilience unified-resilience-item show` | `--service-group-name`, `--unified-resilience-item-name` | Shows one item name returned by the list command. |

## Test result template

Each team should return one row per command, including commands blocked by resource
state or service defects.

| CLI | Inputs/scenario | HTTP/result | Verdict | Job/resource ID | Notes or bug |
|---|---|---|---|---|---|
| Full tested command | Minimal/optional variant used | Status and key response | Pass/Fail/Blocked | ID if created | Reproduction details |

Use these verdicts consistently:

- **Pass**: CLI request and service behavior match the specification.
- **Fail - CLI**: parsing, serialization, polling, or output is incorrect while
  equivalent REST succeeds.
- **Fail - service**: equivalent CLI and REST requests fail in the service.
- **Blocked**: prerequisite resource, permission, feature registration, or
  lifecycle state is unavailable.

## Known issues that should not be counted as new team regressions

- Drill read/update generation is affected by `drillType` being create-only in
  the current TypeSpec visibility.
- Recovery-plan show/update generation is affected by `planType` being
  create-only in the current TypeSpec visibility.
- Some actions require specific service lifecycle states and cannot be tested
  successfully by calling them out of sequence.

For exact shorthand syntax and enum values, run the command with `--help` from the
same wheel being tested. Generic Azure CLI arguments such as `--output`, `--query`,
`--debug`, and `--subscription` are intentionally omitted from the tables.
