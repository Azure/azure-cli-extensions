# Logic Apps Standard CLI extension

Preview Azure CLI extension for local and runtime-backed Logic Apps Standard developer workflows.

**Preview - for evaluation and development.** Commands, parameters, and output
formats may change between releases. Production readiness has not been
established; use non-production resources for evaluation. Some commands modify
deployed workflows, connections, and identities; preview does not mean sandboxed
or read-only.

Preview status applies only to this extension's new commands, not the existing
core-owned `az logicapp` app-management, app-settings, and ZIP-deployment commands,
which are not overridden.

## Install the preview

Requires Azure CLI 2.67.0 or newer and Python 3.10 or newer. Install a locally
built wheel with `az extension add --source <wheel-path> --allow-preview true`.
Source publication is handled by the upstream release pipeline after merge;
this contribution does not manually change the extension index.

Both 32-bit and 64-bit Windows Azure CLI are intended installation targets.
Windows uses `psutil>=5.9.0,<7.1.2`: later releases stopped publishing 32-bit
wheels and otherwise require Microsoft C++ Build Tools during extension
installation. The same bound applies to x64 because a 32-bit interpreter under
WOW64 can also report `AMD64`; an architecture marker is not reliable.
Non-Windows installations retain `psutil>=5.9.0`. This dependency choice does
not qualify every Python/platform combination or change runtime ownership guards.

The complete extension contributes 59 leaves, preserving core `az logicapp`
app management, app settings and ZIP deployment. Rohitha authored the original
extension; subsequent staging work adds 21 leaves and safety repairs. See the
[contribution provenance and qualification boundaries](docs/contribution.md).
Declared Python support is not a claim that every platform/version or live
Azure scenario has been exercised.

## Original developer workflow

```powershell
az logicapp project create --path .\orders --workflow hello
az logicapp workflow validate --path .\orders --workflow hello
az logicapp deployment package --path .\orders --output-path .\orders.zip
```

The original capabilities remain part of this contribution:

| Command group | Purpose |
| --- | --- |
| `project create`, `workflow create/validate` | Initialize local Standard files, import an authored workflow and inspect supported authoring checks. |
| `dependency check/install/uninstall` | Inspect or explicitly manage selected developer tools without modifying global PATH. |
| `runtime start/show/stop` | Manage owned local hosts and shared CLI-owned storage with PID/birth-identity guards. |
| `connector`, `connector operation` | Inspect built-in runtime connector and trigger/action catalogs. |
| `connector managed`, `connector managed operation` | Inspect the ARM managed connector catalog. |
| `connection create/list/show/test/delete` | Author local wiring or manage deployed connections, with explicit targeting, authentication and retention limits. |
| `connection acl`, `identity` | Inspect/manage access policies and assigned identities; these do not prove the caller's effective RBAC. |
| `run start/list/show`, `run action` | Invoke and inspect supported runtime executions and recorded action content. |
| `context create/use`, `deployment package` | Select saved target shortcuts and package local files; core ZIP deployment remains separate. |

Use each group's `--help` for target and confirmation requirements. Local
dependency/runtime commands are explicit operations, not part of validation
or the testing foundation. Never put secret values in `--parameter` or
`--app-setting`; local connection secrets are read from standard input.

## Create, plan and run local workflow tests

`test create` scaffolds native SDK/MSTest source. The separate `test run`
explicitly builds/runs an authored test project, with restore separately opt-in:

```powershell
az logicapp test create --path .\App --workflow Orders
# Review trigger.json, mock external operations and author business assertions.
# Remove the Ignore attribute and inconclusive guard only after that review.
az logicapp test plan --path .\App --workflow Orders
az logicapp test run --path .\App --workflow Orders --accept-sdk-terms --trust-project --restore
az logicapp test run --path .\App --workflow Orders --accept-sdk-terms --trust-project --report-path .\Reports\native.json
az logicapp test results show --result-file .\App\Reports\native.json
```

The starter is **not a passing business test**: it is ignored/inconclusive until
authored. `create` refuses existing output directories and never restores or
runs code. `run` requires a .NET 8 SDK and per-invocation SDK-terms/project-trust
acknowledgements; `--restore` is a separate opt-in. The CLI includes no SDK
binaries or redistribution permission. Native code, build targets and imports
can execute arbitrary operations and contact services: **this is not a sandbox**.
Private caches and mocked actions do not establish denied egress or coverage.
Native counts do not attest SDK invocation or useful workflow assertions.

The qualified dependency contract is SDK 1.0.3, engine 1.165.50, MSTest 4.0.2
and net8.0. Empty/entirely skipped suites are not passes. Sanitized reports
contain bounded native counts; raw local TRX can contain sensitive values and
is never exported by `results show`. Deployment packaging excludes dedicated
native test/state directories and raw TRX, and refuses runtime/test colocation;
inspect the manifest because arbitrary test code can write elsewhere.
See the [native SDK workflow and its known output-cast limitation](docs/workflow-testing-foundation.md#native-sdk-workflow-since-0125).
Existing read-only planning remains separate.

## Inspect workflow testing readiness (without running tests)

```powershell
az logicapp test plan --path .\App --workflow Orders --output json
az logicapp test plan --path .\App --workflow Orders --strict --output json
az logicapp test plan --path .\App --workflow Orders --test-project .\Tests\App.csproj --report-path .\Reports\plan.json
az logicapp context create --name development --path .\App --port 7079 --use
az logicapp test plan --workflow Orders --output json
az logicapp test plan --context development --workflow Orders --report-path .\Reports\plan.json
az logicapp test results show --result-file .\App\Reports\plan.json --workflow-file .\App\Orders\workflow.json
```

This remains the **SDK-ready foundation introduced in 0.1.17**. Explicit local files, bounded
top-level authoring/literal-reference checks and XML metadata inspection do not
execute workflows, evaluate MSBuild or resolve dependencies. Since **0.1.22**,
successful planning exits `0`; `--strict` exits `4` for blocked execution gates.
Neither means tests passed: both preserve immutable SDK gates, `notExecuted`
markers and zero executed business tests. Other diagnostic errors remain nonzero.
New reports use closed schema 2.0 with an explicit exit policy; supported older
schema-1 reports retain their original outcomes. Default stdout only; optional reports require an existing directory,
and overwrites require `--force`. `results show` accepts closed foundation
preflight or sanitized native execution JSON, not raw SDK/TRX output; exit `0` means inspected, not tests
passed. Planning now defaults to the named/active local project's path, then the
current directory. Explicit `--path` overrides that path and bypasses an implicit
active context; an explicitly named cloud context is refused. Relative report
destinations use the selected project and absolute destinations remain unchanged.
No implicit report or output directory is created. Optional test-project and
results-inspection input paths remain relative to the shell's current directory.
No cloud target, install, generation, host or SDK run is involved in planning.
See [testing foundation contracts](docs/workflow-testing-foundation.md)
for schema, exit codes, sensitive input limits and deferred adoption approval.

## Inspect and maintain saved targets

`context create/use` already saves local path/port or cloud resource group/app
shortcuts. `context list/show/update/delete` manages those saved targets only,
not Azure resources. List/show is read-only; editing an active target requires
confirmation or `--yes`, and deleting it clears selection without choosing
another target. Contexts do not bind subscription/tenant or store credentials.
See [saved target management](docs/context-management.md) for JSON shapes,
partial edits, deliberate type changes, storage and concurrency boundaries.
Stores and active selection follow `AZURE_CONFIG_DIR`; custom profiles never
inherit the default profile's active target. Bare local runtime lifecycle
commands honor saved ports. File-authoring commands reject explicit cloud
contexts instead of falling through to another local project.
Local context creation defaults to port 7071 when `--port` is omitted. Explicit
ports and stored values retain strict integer/range validation.

## Create managed connections with distinct names

```powershell
az logicapp connection managed create -g my-rg --logic-app-name my-app --name blobProd --connector azureblob -l eastus --auth-mode managed-identity
az logicapp connection managed create -g my-rg --logic-app-name my-app --name outlook --connector office365 -l eastus --auth-mode oauth
az logicapp connection managed create --path .\App --name outlook --connector office365 --auth-mode oauth
az logicapp connection managed create --context development --name outlook --connector office365 --auth-mode oauth
```

`--name` names the connection; `--logic-app-name` names its consuming site.
The existing guarded identity/OAuth creation and conservative recovery remain
unchanged. OAuth timeout/failure may retain connection/access-policy resources;
inspect the reported state before retrying. Legacy
`connection create --managed-api -n APP --connection-name CONNECTION` remains
available, with a deprecation warning and its original interpretation throughout
this preview. Removing it requires an announced breaking change, not a silent
flip of `--name`.

### Managed connections for local projects

A managed connection is still an Azure `Microsoft.Web/connections` resource
when its consuming workflow runs locally. No deployed Logic App is required.
Use an explicit `--path`, a named local `--context`, or the active local context.
Contexts remain path/port bookmarks; they do not store subscription or resource
group metadata.

The project must have `host.json` and an unencrypted `local.settings.json` with
string-valued `Values`. Add the non-secret Azure scope to the existing `Values`
object (do not replace unrelated settings):

```json
{
  "WORKFLOWS_SUBSCRIPTION_ID": "11111111-1111-1111-1111-111111111111",
  "WORKFLOWS_RESOURCE_GROUP_NAME": "dev-connections-rg",
  "WORKFLOWS_LOCATION_NAME": "eastus"
}
```

Explicit `--subscription`, `--resource-group` and `--location` override the
corresponding project values for that command only. Azure CLI resolves an
explicit subscription name/ID through its signed-in accounts; a saved project
subscription must be a UUID. Configured resource-group defaults do not override
local settings or a saved cloud context; they still apply to an explicit deployed
`--logic-app-name` target. The command does not call `az account set`, change
the context, or rewrite the project's scope settings. Without an explicit
subscription it requires `WORKFLOWS_SUBSCRIPTION_ID`, not the default CLI account.
Missing/invalid scope, malformed/encrypted settings, unsafe file paths and
unsupported local identity combinations fail before creating a connection.
Full connector resource IDs must match the selected subscription and location.
Azure login and rights to create/use the API connection are still required.

Local creation supports connector backend `--auth-mode raw`,
`service-principal` and `oauth`, including the existing secret-on-stdin and
browser-consent flows. Separately, it requests a **seven-day development
runtime key** from Azure. The key is saved only in
`local.settings.json` as `NAME-connectionKey`; `connections.json` contains
`Raw`/`Key` authentication with an `@appsetting('NAME-connectionKey')` reference.
The command does not print the key or grant a deployed app access. Local
`--auth-mode managed-identity` and `--user-assigned-identity` are refused;
these require the existing deployed-app path. Never use a development key as
production authentication; expiry requires an explicit new key operation, not
an automatic workflow retry. See Microsoft's
[local versus deployed authentication guidance](https://learn.microsoft.com/azure/logic-apps/devops-deployment-single-tenant-azure-logic-apps#authentication).

Existing Azure resources, local entries or key settings require `--force`.
Other connection classes, entries and settings are preserved. Tracked
`local.settings.json` is refused before credentials are created, and a local
ignore rule is added before saving a key. If Git cannot establish tracked
status, the result says `trackedByGit: null`; inspect source-control protection
yourself. Do not publish `local.settings.json`, private temporary state, provider
errors or `--debug` output. Deployment packaging excludes the local settings and
`.azurelogicapps` private state; review the manifest before deploying.

Local publication first establishes final Git ignore rules for both
`local.settings.json` and `.azurelogicapps/`, before writing any secret staging
contents. Leftover private staging files remain ignored if cleanup fails.
It then stages private files, rechecks the original file snapshots,
and uses a bounded advisory lock under `.azurelogicapps` plus individual atomic
file replacements. This is **not a multi-file transaction or CAS against
noncooperating editors**. A failure after Azure creation can leave the connection
or credentials changed and local files partially updated. No Azure resources
are deleted, no automatic file rollback is attempted, and no mutation is
retried. Inspect the retained resource and local files before deliberately
retrying. Deployed creation retains its identity/access-policy and conditional
remote-file behavior; legacy `connection create --managed-api` is deployed-only.

## Execute and control Stateful runs

```powershell
$started = az logicapp run start --local --workflow hello --trigger manual | ConvertFrom-Json
az logicapp run wait --local --workflow hello --run-id $started.runId --timeout 60 --interval 2
az logicapp run cancel --local --workflow hello --run-id RUN_ID --yes --wait --timeout 60 --interval 2
az logicapp trigger history resubmit -g my-rg -n my-app --workflow hello --trigger manual --history-name HISTORY_ID --yes
az logicapp run resubmit --local --workflow hello --run-id COMPLETED_RUN_ID --action Send_HTTP --yes
```

Only wait if start returned a real run ID. The same saved/active target contexts
apply. Stateful controls reject Stateless workflows, including debug history.
Wait is bounded and never cancels implicitly. Cancel reports requested/pending
versus observed `Cancelled`; it does not undo side effects. Trigger-history
resubmit directly verifies an explicit retained fired history without a source
run read or history search and requests a **new execution**, not resume or
exactly-once recovery; it can duplicate side effects. Missing new IDs are
reported honestly, and non-idempotent requests are never automatically retried.
Action-level `run resubmit` instead requires one executed action in a completed
source run and literal runtime `canResubmit=true`, which action inspection now
exposes as a nullable Boolean. The runtime uses retained results and the source
definition version; selected/dependent actions can repeat effects with current
settings and connections. The CLI rechecks stable run/action evidence after
confirmation, never enables the feature, and never substitutes trigger replay.
Its service-backed new run identity must be observed separately with `run wait`.

Agent-facing sanitized JSON/table/query results are emitted before nonzero
report exits: `0` for the expected observation or acknowledged request/no-op,
`2` for a CLI deadline, `4` for another terminal outcome, and `1` for observation
or protocol errors. Workflow `TimedOut` is distinct from a CLI wait deadline.
See [execution contracts and support matrix](docs/workflow-execution.md).
Existing start contracts and GA app-management commands are unchanged.

## Investigate a failed run

Existing `run show` and `run action list/show/show-content` expose a run's failed
step and recorded reason. Start with action metadata; retrieve recorded outputs
only when needed and authorized. A failed HTTP action can have no metadata error
but a useful response body, while an expression failure can have an error and no
outputs at all. A skipped dependency is not necessarily the failing action.
Inspection exit `0` means read success, not workflow success. Default URI
redaction does not guarantee provider errors or payloads are secret-free.
See the [locally exercised failure-diagnosis flow](docs/failure-diagnosis.md)
for PowerShell commands, expected evidence and qualification limits.

## Discover and export a workflow

```powershell
az logicapp workflow list --local --port 7071 --output table
az logicapp workflow show --local --workflow hello
az logicapp workflow export --local --workflow hello --output-path .\download\hello\workflow.json
az logicapp workflow validate --path .\download --workflow hello
az logicapp workflow create --path .\existing-project --workflow imported --file .\download\hello\workflow.json
```

Use `-g my-rg -n my-app` instead of `--local` for a deployed Standard app, or use
`--context dev` for a saved target. Without explicit target flags the active
context is used. A context owns its port, so `--context` cannot be mixed with
`--port`, `--local`, `-g`, or `-n`. `--host-key` is accepted for a local host or
local context and is sent as a header, never embedded in a URL. These commands
require a running/reachable runtime; there is no offline `--path` discovery mode.

List returns `value` entries with `name`, `kind`, `state`, and `health`, plus
`nextContinuationToken`. Missing optional state/health are null. `--max-items`
and `--next-token` (alias `--continuation-token`) page the name-sorted complete
inventory client-side; service continuation pages are collected first. Tokens
are offsets, not snapshots: changes between calls can shift page boundaries.
Each traversal is limited to 100 service pages and 10,000 accumulated entries,
independently of `--max-items`; exceeding either limit fails without a partial
inventory. These logical limits are not per-response byte or absolute HTTP-time
budgets.
CLI continuation offsets must be non-negative JSON integers; malformed, ambiguous,
nonfinite, fractional, boolean or string offsets are rejected before inventory reads.
The Base64 alphabet is checked before JSON decoding; whitespace, punctuation
and control characters cannot silently alias a valid offset token.
Show returns those metadata fields plus `workflow`, the complete authored
`workflow.json` object, and `etag` for editing-session guards. Export's result also
includes the source `etag`; the exported file remains the authored workflow only.
Table output omits the definition and ETag.

Export preserves the actual Stateful/Stateless kind, expressions, definition and
authored configuration. It writes one explicit `.json` destination outside the
filesystem root, publishing a complete file atomically. Existing regular files
require `--force`; directories and symbolic links are rejected. Missing or
malformed definitions and unknown kinds fail instead of becoming empty exports.

**This is not a full app backup.** Export does not download host configuration,
settings, connections, credentials or artifacts, and does not resolve expressions.
Definitions themselves can contain authored sensitive literals; protect and
review the output before committing or sharing it. Referenced dependencies must
be supplied separately for the imported workflow to run.

Core `az logicapp` already manages app resources, cloud app settings and ZIP
deployment. See the [capability investigation and roadmap](docs/cli-capability-investigation.md)
for that existing coverage and the remaining workflow lifecycle work.

## Set or delete one existing workflow

```powershell
$saved = az logicapp workflow export --local --workflow hello --output-path .\backup\hello.json | ConvertFrom-Json
# Prepare a complete edited workflow.json separately; retain the backup.
az logicapp workflow set --local --workflow hello --file .\edited\workflow.json --if-match $saved.etag --allow-non-atomic --yes
az logicapp workflow delete --local --workflow hello --allow-non-atomic
```

The same local, deployed `-g/-n`, and saved-context targets apply. Set replaces
the **complete authored workflow.json**, not a bare definition or partial patch.
It requires the existing Stateful/Stateless kind, static validation and target
runtime definition preflight. Missing/unreadable/unsupported workflows are not
created or silently replaced. There is no kind conversion in this command.
The preview's former `workflow update` name is removed; `set` explicitly means
complete replacement, not selective update or graph merging.
Standalone `workflow validate --with-runtime` and replacement share the same
completed 200/204 response gate. An unfinished 202 or error/malformed envelope
cannot claim completed runtime-template coverage or authorize a write.

Both mutations read the current strong ETag, confirm the target unless `--yes`
is supplied, recheck after confirmation and use an **exact** `If-Match`. Optional
`--if-match` binds an operation to the revision obtained during an earlier
show/export, catching edits made while you were authoring. Omitting it still
checks the revision read by this command. Wildcards, weak ETags and `--force`
bypasses are not supported. Identical update input is validated without a write.

**`--allow-non-atomic` is required, even with `--yes`.** The runtime's file API
is not transactional: ETag checks do not cover every race, an interrupted upload
can leave partial content, and a concurrent deletion can cause PUT to recreate
the file. This was verified against a real local runtime and the first-party
implementation. Coordinate writers and retain an export; no CLI flag can turn
these primitives into a guaranteed transaction.

Set verifies the acknowledged write revision and exact bytes. A mismatched
file is conditionally restored only when the current revision can be attributed
to that write. Newer or missing files are not blindly restored; unexpected
creation, missing receipts, unreadable verification and uncertain request
outcomes return explicit errors with recovery guidance. Conditional recovery
itself remains subject to VFS's platform limits, not a guaranteed rollback.

Delete removes **only `<workflow>\workflow.json`**, confirms a file-plane 404,
and leaves its directory, sibling files, other workflows, app settings,
connections, artifacts and identities intact. It neither cancels runs nor
purges history. A recreated file is not deleted again automatically.

Mutation results contain `workflow`, `workflowKind`, `action`, `etag` and
`verification` (`fileReadback` for updated/unchanged, `fileNotFound` for deleted).
They do not echo the definition or resolve credentials. Runtime reload/removal
is asynchronous: file verification is not proof of workflow execution or reload
completion. Read-only/run-from-package hosts can reject writes; use the existing
ZIP deployment flow rather than bypassing those restrictions.

## Enable or disable one deployed workflow

```powershell
az logicapp workflow disable -g my-rg -n my-app --workflow hello --allow-non-atomic
az logicapp workflow enable --context production --workflow hello --allow-non-atomic --yes
```

These commands support **deployed Standard Stateful and Stateless workflows**.
The active or named context must be a cloud target, or supply both `-g/-n`.
They verify workflow existence/kind/state before reading or changing settings.
The caller needs permission to read runtime metadata, list app settings and
update app settings; app identity and connection ACLs do not grant these rights.
Definitions, connections, artifacts and run history are not edited. They do not
invoke whole-app stop/start/restart.

The documented state mechanism is `Workflows.<workflow-name>.FlowState`, with
`Enabled` or `Disabled`, through the App Service settings API. **The API replaces
the entire settings map, not only that key.** Other values, including secrets
and Key Vault references, are retained from the in-memory snapshot. Both actions
require confirmation (unless `--yes`) and **`--allow-non-atomic` even with `--yes`**.
Coordinate all app-settings writers: preflight snapshot checks detect changes
during confirmation, but cannot prevent lost unrelated updates between the last
read and PUT. Readback cannot prove no concurrent value was overwritten.
There is no invented ETag guard, automatic retry or rollback of unrelated settings.
App settings updates can have platform hosting/reload effects.

Results distinguish verified configuration from observed runtime state:
`workflow`, `workflowKind`, `action` (`configured` or `unchanged`),
`requestedState`, `configuredState`, `runtimeState`, `runtimeConvergence`,
`runtimeObservationError`, and `verification: appSettingsReadback`.
After an acknowledged and verified write, one runtime read reports `converged`
(metadata matches), `pending` (metadata differs), or `unknown` (runtime read
failed, with an explicit `notFound`, `unauthorized` or `unavailable` category).
Pending/unknown results include a warning. **Converged is not proof of drained
runs or quiescent dispatchers.** There is no polling/wait flag or hard command
deadline; the unchanged request uses two HTTP calls, the changed request at most
seven. Malformed metadata, uncertain write receipts or unverifiable settings are
errors, not success-shaped defaults. Inspect configuration and workflow state
before retrying an uncertain operation.

If already explicitly configured, the command does not write or prompt, even
when runtime propagation is pending. An absent setting is not silently presented
as an explicit Enabled setting: enable writes that value. No raw settings,
snapshots, signed URLs or provider error bodies are returned, written to files,
or logged by these commands, including their REST helper under `--debug`.

Disabling stops new ordinary workflow instances/triggers after propagation;
**existing in-progress/pending runs continue**. It is not cancellation, history
purging or trigger reset. Enabling may process accumulated trigger backlog.

**Live local enable/disable is unsupported.** A real Functions 4.15.2 workflow
host rejects the guessed state-action routes for both workflow kinds. `--local`
and local contexts therefore fail before any requests, prompts, file edits or
restarts. For local development, the documented companion procedure is to set
`Workflows.<name>.FlowState` in `local.settings.json` under `Values`, then restart
your own host. This is startup configuration, not a live runtime state API.
Consumption, hybrid hosts and deployment slots are not additional supported
targets of these commands.

## Diagnose a local runtime without changing it

```powershell
az logicapp runtime doctor --path .\orders --output json
az logicapp runtime doctor --context orders-local --output table
```

Doctor is a **read-only local-environment preflight**, not a workflow business
test or cloud diagnostic. It checks project shape, selected child-environment
tools, cached bundle evidence, literal setting/parameter references, configured
loopback storage and verified runtime ownership/status. It does not install,
download, repair, start/stop services, rewrite files or change the active context.
Credentials, raw server/subprocess output and configuration values are omitted.

**Exact tool/bundle compatibility is a required unknown.** An otherwise
responsive local project normally exits **`2`**, even with observed Running host
metadata; that is uncertainty, not proof the project is broken or healthy.
Required failures exit `1`; `0` requires no required failures/unknowns and still
does not prove business correctness. `--strict` also makes optional problems exit
`2`. Findings are formatted as JSON/table and support `--query` before diagnostic
nonzero exits, so preserve stdout in CI. A stopped host can be acceptable offline;
unreachable configured local storage remains a required failure.

See the [runtime doctor contract](docs/runtime-doctor.md) for complete
coverage, local/context flags, conservative expression/compatibility boundaries
and per-probe timeouts. Doctor does not add trigger, cloud-diagnostic or log-stream
features.

## Lifecycle safety

Managed connection creation couples the ARM resource, its access policy, and the
app's `connections.json` entry. Failed creation/update retains ARM connections
and access policies: even an acknowledged unconditional upsert after preflight
absence does not prove exclusive rollback ownership. No automatic ARM deletion
or policy replay is attempted. Authentication or granted access may have changed;
inspect retained state and deliberately recover it before retrying. Guarded
File-entry restoration requires a completed write receipt with a strong ETag
and a current file still at that exact owned revision. A lost response or a
newer revision retains the file for manual recovery, even if the selected entry
has identical content. `--force` is not a concurrency guarantee; ARM reads omit some credentials.
Unreadable or malformed existing connection files are not silently replaced.

Managed connection creation and deployed connection removal require an existing
`connections.json` with a usable strong VFS ETag. Creation checks this before ARM
mutations; missing/unversioned/weak files fail closed instead of attempting an
unqualified create-only write. Publication and removal send the exact ETag from
their latest reread; restoration additionally requires that revision to match
the completed publication receipt. A revision conflict (`412`)
does not trigger a wildcard retry or authorize ARM cleanup; a rejected
publication does not adopt another writer's identical entry for restoration.
Prepare/deploy the authored file and verify the provider returns strong revisions
before retrying. These conditional requests still depend on the provider honoring
VFS preconditions and are not a universal transaction or concurrency lock.
Workflow-state metadata and app-settings snapshots, receipts and readback reject
duplicate/nonfinite JSON before settings mutation or verification.
Connection snapshots and authored/remote workflow JSON reject duplicate object
members, nonfinite constants and floating-point overflow before mutation. Invalid
bytes are preserved rather than silently normalized on a whole-file rewrite.
Offline authoring/validation and testing preflight share this strict decoding
boundary; ordinary finite, unambiguous JSON remains supported.
Managed creation also requires an existing selected policy to match the selected
ActiveDirectory principal's object and tenant IDs, checked before forced connection
update and again before ACL publication. `--force` cannot replace unrelated access.
Those observations are not atomic ARM preconditions.
Connection snapshot/readback/recovery comparisons and workflow set no-op
detection preserve JSON scalar types: booleans, integers and floating-point
numbers are not interchangeable. Object member ordering remains insignificant.
Managed deletion performs read-only ARM ownership preflight before unlinking the
selected file entry, so known malformed/unavailable evidence cannot first break
its wiring. ARM mutations still follow verified unlink and fresh ownership/shared
reference checks. Later failures may leave the entry removed and ARM resources
retained; this is not a cross-resource transaction or permission to replay old files.

Connection-file publication requires a completed VFS receipt and readback of the
selected entry. Deletion must observe the entry's removal before revoking access
or deleting an ARM connection. Unfinished receipts or missing/mismatched readback
stop cleanup; this is an observation gate, not a transaction or concurrency lock.

Connection deletion uses the identity in the actual connection entry, not every
identity assigned to the app. User-assigned managed identities may be shared:
their access policies and connection resources are retained, even with
`--keep-resource`. Only demonstrably exclusive system-assigned identity access is
removed automatically: the policy must name the selected site's system principal
and tenant, with ActiveDirectory type and complete, matching identity fields.
The site's tenant is not inferred from the CLI login. Missing/malformed tenant
evidence or the same object ID in another tenant retains that policy and the ARM
connection; other verified exclusive policies may still be revoked on a shared
connection. Both site and policy evidence are refreshed after verified unlink.
Exact or case-equivalent duplicate access-policy names are checked before
ownership classification: every affected policy and the ARM connection are
retained, even when one duplicate matches the selected principal. An incomplete
or unsafe-name collection cannot authorize any ACL cleanup: an escaped alias
could contradict an otherwise valid name. Printable single-child names are
quoted by the shared automatic/explicit ACL route builder; path, query, fragment,
percent escapes, control characters and dot segments are rejected. Other uniquely
named verified policies may still be revoked from a complete duplicate-bearing
collection; duplicate content is not identity uniqueness.
Retained resources include an explanatory reason.
Before any managed-cleanup ARM request or file unlink, the authored connection
ID must be a canonical relative `Microsoft.Web/connections` resource ID in the
selected subscription and resource group. Absolute URLs, malformed IDs and
cross-scope references refuse without changing the wiring, including with
`--keep-resource`. Manage cross-scope resources explicitly instead.

Local runtime ownership is verified with PID and process creation time on
Windows, Linux, and macOS. Unknown or recycled process identities are never
stopped. Foreground and background runtimes both retain shared CLI-owned Azurite
while they are alive. Managed tools are made available through child-process
environments without changing global `PATH`; `LA_DEPENDENCIES_PATH` selects the
managed dependency root.

The 0.1.18 audit hardens Windows tree cleanup using original creation identities,
revalidation and an identity-checked process object at signaling time. Malformed
ownership records and unresolved descendants retain cleanup/storage guards
instead of being treated as absent. These protections do not certify Linux/macOS
behavior or establish ownership against arbitrary manual record writers.

The 0.1.19 second audit also validates root identity and ancestry when first
adopting descendants. Unknown children remain cleanup/storage guards without
authorizing signals. Doctor bounds HTTP receives before buffering; execution
requests identity encoding and rejects compressed bodies before decoding.

Static workflow validation reports invalid trigger shapes as structured
findings and continues independent action/reference checks.

## Offline regression tests

From the repository root, with Azure CLI's Python packages available:

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src\logicapp'
python -m unittest discover -s src\logicapp\azext_logicapp\tests\latest -p 'test_*regressions.py'
python -m pytest src\logicapp\azext_logicapp\tests\latest
```

The standalone regression tests use `unittest` and faithful local fakes; no Azure
resources are created or deleted. The existing suite additionally requires
`pytest`, `pytest-subtests`, and `azure-cli-testsdk`. Additivity checks require the
extension installed in an isolated extension directory. They generate stock help
controls using the same interpreter/CLI, empty temporary configuration and
extension directories, disabled telemetry and disabled dynamic installation.
No private baseline directory or externally supplied help fixture is required.
The pinned 13 GA command names, core loader ownership, collision checks and
55-command extension surface remain independently asserted.

For upstream qualification, also run `azdev style logicapp`, `azdev test logicapp`,
`azdev linter logicapp`, and `python scripts\ci\test_index.py -q` from an isolated
development environment. Run source and installed-wheel suites serially because
the offline scenarios share a test scratch directory.

Committed CLI contract regressions load the source through Azure CLI's development
extension mechanism and exercise real parsing, JSON/query/table formatting and
diagnostic exits with guarded operations. Wheel contract tests build locally with
`setuptools`/`wheel` (no download or dependency install), verify production bytes,
version and `psutil` metadata, and reject packaged tests/bytecode. These are tests
of the CLI, not business tests of authored workflows.
