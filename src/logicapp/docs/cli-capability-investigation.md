# Logic Apps CLI capability investigation and incremental roadmap

Investigation date: **2026-10-08**. Baseline: extension **0.1.11** at
`a7f9a669c08ae6a212a2fe5073d15b6726890982`. The baseline registers **38 extension
leaf commands** in `src/logicapp/azext_logicapp/commands.py`. Version 0.1.12 adds
three read-only workflow leaves (41 total); 0.1.13 adds guarded update/delete
(43 total); combined 0.1.14 adds deployed enable/disable and read-only local
runtime doctor (46 total); 0.1.15 adds Stateful wait/cancel/resubmit
(49 total); 0.1.16 adds saved-context list/show/update/delete (53 total);
0.1.17 adds local testing preflight/report inspection (**55 total**).
Version 0.1.18 audits and hardens the combined features without adding leaves.
Version 0.1.19 applies the second audit's receipt/readback, child-adoption and
HTTP streaming-budget repairs, also without adding leaves or enabling SDK tests.
These do not complete the workflow lifecycle or
the wider roadmap.
The baseline's connection, identity, runtime
ownership, dependency environment, and validation safety fixes remain in place.
Connection compensation is now conservative: failed ARM upserts retain resources
and ACLs for manual inspection because neither preflight absence nor an
acknowledgement proves exclusive rollback ownership. Guarded file restoration
remains, but no automatic ARM deletion or policy replay is promised.

The first combined audit covers all 11 post-fork commits through 0.1.17 and applies
targeted correctness/coverage repairs in 0.1.18. The complete latest suite passed
**647 tests and 1,096 subtests**; all six genuine stock CLI 2.67 additivity checks
also passed against the final isolated installed wheel. Its 27 packaged
module/metadata files match source bytes. Actual CLI parser/output/diagnostic-exit
contracts and 22 installed foundation smoke cases passed. Shared user-global
configuration, contexts, runtime records and installed extension were unchanged.
This is not 100% coverage, live Azure or Linux/macOS qualification, nor SDK
execution. See the [post-fork summary and remaining work](post-fork-summary.md).

The second audit's final 0.1.19 suite passed **683 tests and 1,227 subtests**;
all six GA checks passed against the installed wheel, whose 28 packaged
source/metadata files matched source. Five actual-CLI contract tests, 194
installed focused regressions and 22 foundation scenarios passed. Raw HTTP,
HTTPS and proxy CONNECT fixtures cover slow headers/body reads and TLS trust;
they are not live Azure or universal proxy/platform qualification. SDK execution
and user-global installation remain unchanged.

Basic [failure diagnosis using existing commands](failure-diagnosis.md) was
exercised separately with installed 0.1.19 against real local Stateful expression
and HTTP failures, plus successful corrected-input runs. This completes a narrow
top-level inspection recipe, not deeper diagnostic traversal, cloud qualification,
log streaming or SDK business-test execution.

## Scope and completion criteria

Standard is the first target. Assess each **operation x hosting model x
local/cloud target**, rather than interpreting every missing extension leaf as a
missing Azure capability. Classify coverage as **extension**, **existing companion
command**, **not yet implemented**, or **platform unsupported**. A supported
operation is complete when a documented CLI command or documented companion
command reaches it without requiring users to discover an undocumented `az rest`
request. Existing portal/VS Code features establish user tasks, not proof that a
guessed API is supported on every target.

This is a command-line developer/operations experience, not a promise to replace
visual designers. Runtime-native and Azure-managed connectors have different
authentication and lifecycle requirements. Human OAuth consent remains necessary
where the provider requires it. Hybrid deployment is a distinct hosting model,
not another alias for a local developer host.

## Existing coverage at the assessed baseline

Core Azure CLI already owns `az logicapp create/delete/list/show/start/stop/restart/
scale/update`, `az logicapp config appsettings list/set/delete`, and
`az logicapp deployment source config-zip` [1]. Standard global flags such as
`--output`, `--query`, and `--subscription` are inherited from Azure CLI. Resource
CRUD, cloud app settings, ZIP deployment, and output filtering are therefore
**not universally missing**. App-resource stop/start is distinct from disabling
or enabling one workflow inside a Standard app [3].

| User task | Baseline extension coverage | Target / remaining gap |
| --- | --- | --- |
| Start a project and author workflows | `project create`; `workflow create`, including authored `--file`; `workflow validate` | Local project files. Only create/validate existed in the workflow group. |
| Check/install developer dependencies | `dependency check/install/uninstall` | Local tools; explicit restrictions and publisher/source behavior remain relevant. |
| Run a local host | `runtime start/show/stop` | Local runtime and optional shared Azurite, with ownership verification. Not a production host doctor or log-streaming experience. |
| Discover connector capabilities | Built-in `connector list/show`, `connector operation list/show`; managed equivalents | Running local/deployed host for built-ins; ARM location catalog for managed connectors. |
| Create and inspect connections | Local `connection create`; managed cloud create; deployed `list/show/test/delete` | Wiring and ARM resources are coupled but distinct. Update/reauthorize/adopt/unlink/reconcile tasks remain incomplete. |
| Manage connection ACLs and app identities | `connection acl list/show/add/remove`; `identity assign/show/remove` | Connection access and app identity are not equivalent to the caller's service RBAC or endpoint authorization. |
| Invoke and inspect executions | `run start/list/show`; `run action list/show/show-content` | Basic invocation/inspection exists. No wait/watch/cancel/resubmit or complete recovery surface. |
| Build a deployment artifact | `deployment package` | Deterministic ZIP and manifest; partial artifact coverage, not first-class maps/schemas/code lifecycle. Core ZIP upload already exists. |
| Save/select a target | `context create/use` | Local path/port or cloud resource group/app. No list/show/edit/delete or saved subscription/tenant/slot binding. |
| Trigger lifecycle | No separate trigger command group; connector operation list already accepts `--kind trigger/action/all` | Connector trigger catalog discovery already exists. Since 0.1.12, workflow show also exposes authored configured triggers. Workflow-specific callback retrieval, firing histories and supported reset remain gaps; do not duplicate catalog discovery. |

## Gaps organized by user task

| Capability | What the user needs to accomplish | Gap and classification |
| --- | --- | --- |
| Workflow lifecycle | Find workflows, read/download definitions, safely create/update/delete deployed workflows, toggle one workflow, inspect supported versions | Inventory/read/download are addressed by slice 1; guarded update/delete by slice 2, subject to explicit VFS limits; deployed state controls by slice 3, subject to settings-map/propagation limits. Live local state controls are **platform unsupported**; documented startup configuration is a companion. Intentional deployed creation/version surfaces remain **not yet implemented**; app CRUD does not substitute for them. |
| Trigger lifecycle | Inspect configured triggers, obtain HTTP callback URLs, invoke inputs with correct trigger semantics, investigate failed firings, reset state where supported | Connector operation catalog discovery is **implemented**, including trigger/action/all filtering; workflow show exposes authored configured triggers. Workflow-specific callback retrieval, firing histories/failures and supported reset are **not yet implemented**. Validate support per trigger/host; do not imply every trigger can be invoked or reset identically. |
| Execution and recovery | Wait/watch with timeout, cancel/resubmit, perform supported action-level reruns, retain stable correlation | Stateful bounded wait/cancel/trigger replay began in **0.1.15**. **0.1.21** separates direct trigger-history replay from genuine one-action run resubmission, requiring positive runtime eligibility. The sequential cached Windows action fixture is verified; broader graph/platform/cloud recovery remains unqualified, not fabricated. |
| Deep diagnostics | Filter by time/correlation, inspect trigger inputs/outputs, loop iterations/repetitions/nested scopes/retries/request histories, export diagnostics, stream logs, configure telemetry/alerts/retention | Basic run/action read and 0.1.14's read-only local environment doctor exist. Rich workflow traversal/export, cloud diagnosis and log streaming are **not yet implemented**; Azure Monitor and hosting tools are **existing companions**, not functionality to duplicate. |
| Existing-app round trip | Download/import a complete app, diff local/cloud state, reconcile drift without accidental overwrites | **Not yet implemented**. Single workflow export is not whole-app download [4]. Host configuration, connections, settings and artifacts need an explicit secret and conflict policy. |
| Production delivery | Preflight, environment configuration, deployment/status orchestration, post-deploy verification, supported slot swaps and artifact rollback | Packaging and core ZIP deployment exist [1,5]. Higher-level orchestration is **not yet implemented**. Slot operations have existing companions and strict platform limits [6]. |
| Configuration | Manage `parameters.json`, host/local/workflow settings and environment overlays; parameterize connections; detect drift | Cloud app settings already have core commands. Local configuration/overlays and coherent resolution are **not yet implemented**. |
| Connections | Update/reauthorize, use an existing connection, unlink without deleting shared state, inspect auth metadata/dynamic values, reconcile wiring with ARM inventory/orphans | Creation/read/test/delete/ACL are partial coverage; remaining tasks are **not yet implemented**. Preserve shared-identity safety. |
| Security | Diagnose effective permissions; manage supported endpoint auth/access controls, keys/rotation and Key Vault references | App identity and connection ACL exist. Caller RBAC is separate; use **existing Azure companions** where possible. Workflow-aware diagnosis/integration is **not yet implemented**. |
| Automated workflow tests | Use official test SDK and mock metadata, generate tests from a definition/run, execute in CI and publish reports | **Read-only SDK-ready foundation implemented in 0.1.17**: local `test plan` and foundation-only `test results show`. SDK adoption/restore/execution remain blocked. Native generation/business test execution are **not implemented** [7,8]. CLI Python regressions are not tests of users' workflows. |
| Validation depth | Validate nested graphs, expressions/contracts and actual setting/connection resolution | Current static validation checks shape and top-level `runAfter`, with offline reference warnings. It is not a complete semantic validator. Runtime-backed validation is partial coverage, not a substitute for workflow tests. |
| Artifacts and custom code | Manage/build/test maps, schemas, assemblies, rules, connectors, custom code and project types | Packaging files is partial coverage. First-class lifecycle is **not yet implemented**, with existing integration-account companions for some cloud artifacts [2,9]. |
| Target consistency | Inspect/edit/delete saved targets; make local/file/runtime/cloud meanings explicit | Saved context list/show/update/delete are **implemented in 0.1.16**, alongside original create/use. These are shortcut management only: inherited global `--subscription` remains unbound, and subscription/tenant/slot expansion is not implemented. Extension leaves have no `--slot`. Offline `--path` is not a third discovery target in slice 1. |
| Broader platform scope | Operate Consumption workflows, integration accounts/B2B and hybrid deployments coherently | Compose **existing `az logic`** commands [2] for Consumption/integration accounts rather than duplicating them. Standard hybrid hosting requires separate assessment [10]. |
| Hosting and infrastructure | Provision networking/storage/hosting, RBAC and monitoring | Reuse documented Azure infrastructure commands. Do not duplicate the entire Azure CLI inside this extension. |

### Deployment-slot boundary

The current Standard slots documentation [6] says nonproduction slots are
read-only and their dispatcher is off: **workflows execute only in production**.
Traffic distribution, A/B testing, pre-swap product execution verification, and
blue-green deployment are unsupported. Do not promise those scenarios merely
because Functions supports slots.

Slot creation already has `az functionapp deployment slot create`, identity
assignment has `az functionapp identity assign --slot`, ZIP deployment has core
`az logicapp deployment source config-zip --slot`, and swapping has
`az functionapp deployment slot swap`. The missing extension feature is coherent
workflow-aware targeting/orchestration, not the existence of all slot CLI commands.

## Prioritized roadmap

Deliver each phase-1 step separately. Read-only workflow discovery comes before mutations;
each mutation needs its own validated API/hosting support, concurrency/conflict,
confirmation, failure-recovery and shared-state policy.

The user endorsed reprioritizing the next increment toward **execution controls**
on 2026-10-08. Connector trigger catalog discovery already exists, and workflow
show exposes the authored configured trigger; do not duplicate either surface.
Include workflow-specific HTTP callback retrieval where it helps invocation,
support-gate trigger semantics and recovery, and defer a separate trigger
inventory/schema surface. Place trigger-history/failure diagnostics with deeper
troubleshooting. This is roadmap ordering, not authorization to implement the
later increment as part of the current release. Version 0.1.15 implements the
bounded Stateful execution slice; callback retrieval was unnecessary for the
verified existing management-trigger invocation and remains unimplemented.

| Phase | Increment | Implementation status |
| --- | --- | --- |
| 1.1 | Workflow list/show/single-workflow export | **Implemented in 0.1.12**, bounded contract below. |
| 1.2 | Guarded workflow update/delete; separately assess supported deployed creation | **Implemented in 0.1.13**, with non-transactional platform limits below. Intentional deployed creation is not implemented. |
| 1.3 | Enable/disable an individual workflow | **Implemented in 0.1.14 for deployed Standard**, with explicit settings-map/propagation limits below. Live local transitions are gated. |
| 1.4 | Execution invoke/wait/watch/timeout/cancel/resubmit, with useful HTTP callback retrieval | **Bounded Stateful wait/cancel/resubmit implemented in 0.1.15**, reusing existing invocation/inspection. Stateless is gated, callback retrieval and general recovery orchestration remain unimplemented. |
| 1.5 | Trigger-history/failure and deeper execution troubleshooting | Planned with deep diagnostics. Defer separate workflow trigger inventory/schema; existing connector catalog and workflow show already cover discovery tasks. |
| 1.6 | Runtime doctor/logs | **Read-only local doctor implemented in combined 0.1.14**, bounded contract below. Cloud diagnostics and log streaming remain unimplemented. |
| 1.7 | Full app download/import | Not implemented. Decide secret policy and local/cloud conflict behavior first. |
| Parallel | Saved-target context list/show/update/delete | **Implemented in 0.1.16**. Read-only inspection, validated partial edits, explicit kind transitions and confirmed shortcut-only deletion. No subscription/tenant binding expansion or resource deletion. |
| Bounded foundation | Local workflow test preflight and report inspection | **Implemented in 0.1.17**. Closed versioned reports, limited authoring/XML inspection, no tests executed. SDK policy/qualification gates remain blocked/unknown; no phase-2 completion claim. |
| 2 | Environments, delivery orchestration, official workflow test SDK, deep diagnostics | Planned; compose existing settings/ZIP/Monitor commands. Respect slot limitations. |
| 3 | Broader models, B2B/integration-account composition, hybrid deployment | Planned; assess support per operation and hosting model. |

For the 0.1.15 execution increment, see the [execution support matrix and
agent-facing report contract](workflow-execution.md). It uses Standard
`Microsoft.Web/sites` runtime APIs, verifies trigger-history/run association
before resubmit, never treats acknowledgement as completion, and preserves
0.1.14 workflow state/doctor boundaries. No trigger catalog duplication,
action-level rerun, trigger-history diagnostic command or test SDK was added.

The user separately authorized saved-target management after confirming that
`context create/use` already existed in the original extension. Version 0.1.16
implements that bounded slice and aggregates the completed 0.1.15 execution
baseline. See [context management contracts](context-management.md) for sorted
JSON/table inspection, named/active selection, partial updates, explicit complete
kind transitions and native advisory-lock/atomic-publication limits. Editing an
active target requires confirmation or `--yes`; deleting it atomically clears
selection without silently choosing a substitute. Runtime commands then require
an explicit target or deliberate selection; existing no-context offline
current-directory defaults remain. No credentials, resources, subscription or
tenant bindings, migrations, bulk deletion, rename or context synchronization
were added. Later roadmap increments remain unimplemented.

The user selected the separately bounded **SDK-ready CLI foundation**, not SDK
adoption, restore or native execution. Version 0.1.17 supplies explicit local
`test plan` and `test results show`; see [testing foundation contracts](workflow-testing-foundation.md).
Reports distinguish static authoring findings from input/protocol failures and
policy blocks. Successful report inspection means inspected, never testsPassed.
SDK/engine/runner/platform/network qualification and use/data/update terms remain
unresolved. No project scaffolding, generation, native runner, SDK download/load,
local-runtime integration execution or automatic later increment is authorized
or implemented.

## Slice 1: implemented read-only contract

`az logicapp workflow list/show/export` address either a running local host using
`--local [--port] [--host-key]`, a deployed Standard app using `-g/-n`, or a named
`--context` (falling back to the active context when no target is supplied).
Explicit local/cloud/context coordinates are mutually exclusive. A context owns
its saved port; do not supply `--port` with `--context`. A local context accepts a
host key, while cloud targets reject local-only port/key flags.

List returns `{value, nextContinuationToken}`, with stable item fields
`name`, `kind`, `state`, and `health`. Missing optional state/health are null, not
invented defaults. Inventory is sorted by name after collecting any supported
service continuation pages. `--max-items` and `--next-token` (alias
`--continuation-token`) then apply **client-side offset paging**. Each request
rereads the inventory; this is not snapshot isolation, and concurrent workflow
changes can shift page boundaries.
Conflicting service continuation fields or recognized query-token aliases fail
without a partial inventory or follow-up request; matching decoded values remain
supported. The service URL is never followed.
CLI continuation envelopes validate the Base64 alphabet before JSON decoding;
punctuation, whitespace and control characters cannot silently alias a valid
offset token.

Show reads metadata followed by the supported file-plane `workflow.json`, and
returns `{name, kind, state, health, workflow}` (plus `etag` since 0.1.13).
`workflow` is the authored file object, not a guessed reconstruction from trigger
summaries. Table output exposes
only name/kind/state/health. File reads preserve local `x-functions-key` behavior
and cloud ARM authorization. Advertised upstream definition URLs are not followed.

Export writes exactly one workflow to an explicit `--output-path` `.json` file
outside the filesystem root. It preserves actual kind (Stateful/Stateless),
definition, expressions and authored runtime configuration; unknown kinds,
missing definitions, conflicting metadata/file kinds and malformed responses
fail explicitly. It does not invent Stateful defaults. Existing regular files
require `--force`; directories and symbolic-link destinations are rejected.
A same-directory temporary file is flushed before atomic publication, with
non-clobber publication when force is absent and cleanup on failure.

Only metadata and the selected workflow file are read. No cloud state is created,
and host configuration, `local.settings.json`, app credentials, `connections.json`
and app artifacts are not downloaded. **Workflow definitions themselves can
contain author-written sensitive literals**: export preserves them, does not
resolve or redact expressions, and does not guarantee secret-free output.
Secure the destination and review it before committing or sharing it.

The export can be validated using existing `workflow validate` and imported into
an existing local project using `workflow create --file`. A file referencing
settings, connections or other artifacts still needs those dependencies; this is
not a portable, fully configured application backup.

### Evidence and limitations

Implementation was grounded in the real local runtime metadata/VFS response and
first-party file-plane client usage [11]. The metadata GET returns
`name`, `kind`, `isDisabled`, trigger summaries and health, **not the full
definition**. Runtime inventory can be an array; ARM-style envelopes also require
explicit casing/shape handling. App Service's separate workflow resource APIs
document `properties.flowState/health/files` [12,13]; do not confuse that resource
plane with the runtime proxy route.

Focused regressions exercise actual observed metadata, cloud/local URLs and auth,
target flags/contexts, casing/envelopes, service and CLI paging, errors, force/race
safety, artifact round trips, and sensitive-literal handling. Validation uses an
isolated wheel/extension/config directory and a real owned local host; no installed
user extension, global context, or unrelated host is modified. Cloud coverage uses
ARM request fakes; **no live Azure validation or mutation is authorized**. The
historical external GA help baseline is unavailable; additivity uses a genuine
stock installed Azure CLI 2.67 baseline, not fabricated expected help.

Slice 1 verification on 2026-10-08:

- Focused discovery regressions: **26 passed**. All standalone safety/discovery
  regressions: **117 passed** using `python -m unittest discover -s
  src\logicapp\azext_logicapp\tests\latest -p 'test_*regressions.py' -q`.
- Complete offline/additivity/regression suite: **380 passed, 254 subtests passed**,
  including all six additivity checks, using `python -m pytest
  src\logicapp\azext_logicapp\tests\latest -p isolated_test_state -q`. The
  session-only plugin isolates context/runtime records; environment variables
  select the isolated extension/config directories and stock GA help baseline.
- Built/installed **0.1.12** into a session-only extension directory. Actual CLI
  commands against a real owned Functions 4.15.2 local host verified both kinds,
  JSON/table output, saved context, paging alias, export/nonforce/force behavior,
  static validation, import round trip, missing-workflow exit 3 without a file,
  flag errors, and execution of the starter workflow. The host was stopped.
- Installed CLI cloud-mode list/show/export passed with **five ARM GET fakes**.
  No live Azure operation was performed. Global ownership/context records and
  the user's installed extension were unchanged; external Azurite was neither
  claimed nor stopped.
- Compilation, error-level Pylint and `git diff --check` passed. Pylint ran under
  a source-capable Python with external import/name checks excluded because the
  bundled Azure CLI ships bytecode-only dependencies; this is not a full
  dependency-source type check.

## Slice 2: guarded update/delete, not transactions

Version 0.1.13 adds full-document replacement (now `workflow set --file`,
formerly `workflow update --file`) and `workflow delete`, using the
same running-local, deployed and saved-context targets as discovery. Both
require **`--allow-non-atomic`** plus target confirmation (or `--yes`). Neither
provides an ETag bypass. Optional `--if-match` uses the revision returned by
show/export to guard an editing session; even without it, the command uses the
exact strong ETag read during its own operation.

Update requires a complete authored file with the existing Stateful/Stateless
kind. Static checks reuse the existing validator's payload checks, followed by
target-runtime definition validation before writing. There is no default kind,
bare-definition merge, intentional creation, kind conversion or shared config
mutation. After confirmation it rereads the existing snapshot and performs a
conditional file PUT. An unchanged input is validated without a write.

A successful update requires the expected update receipt, write ETag, and exact
file-byte readback at that revision. If readback mismatches and the current file
can be attributed to this acknowledged write, recovery conditionally restores
the original bytes and verifies them. A newer revision is not overwritten; a
missing file is not blindly recreated for rollback. Unknown request outcomes,
missing receipts/ETags, failed readback, unexpected creation and failed recovery
are reported as errors, never success-shaped fallbacks.

Delete conditionally removes only `<workflow>/workflow.json`, verifies a
file-plane 404, and retains the directory, sibling files, shared settings,
connections, artifacts, identities and other workflows. It does not cancel
active runs, purge history or delete the app resource. Deletion verification
does not retry against a recreated file.

### Confirmed platform boundary

A real Functions 4.15.2 local host returned strong file ETags, rejected stale
PUT/DELETE with HTTP 412, validated an incoming definition through
`workflows/<name>/validate`, and removed a workflow from runtime inventory after
deleting its definition while retaining a sibling file and another workflow.
However, **PUT on a missing file returned HTTP 201 even with an old exact
If-Match**. The first-party VFS implementation [14,15] checks ETags only when it
believes the file already exists, then writes using a truncating file stream.
Its precondition check and write/delete are not a transaction.

Consequently these are **guarded mutations, not strict atomic compare-and-swap
or guaranteed rollback**. The explicit acknowledgement is required rather than
pretending every race/partial upload can be prevented. Coordinate deployments
and other writers; retain a protected export before updating/deleting. If a
concurrent deletion causes an unexpected create receipt, the command fails and
reports that the target may have been recreated; it does not delete that file
blindly. Conditional restoration has the same server limits.

Results report `verification: fileReadback` or `fileNotFound`, not proof of
completed runtime reload or execution. No workflow is invoked automatically to
verify a production change. Read-only/run-from-package hosts may reject writes;
use documented deployment companions rather than weakening auth or bypassing
the hosting restriction. Existing files that cannot be read as supported
workflow.json documents are not silently replaced. Full transactional mutation is **platform unsupported
by this verified VFS primitive**, not merely a missing CLI flag.

The required update-validation preflight also checks its HTTP completion receipt.
An empty asynchronous HTTP 202 is not completed validation: it fails before
confirmation or publication, without inventing a validation polling protocol.

Raw VFS operations now retain the same local host-key/error translation and
cloud ARM authorization as JSON requests. Existing connection callers retain
their prior default wildcard write behavior; the new workflow mutations always
provide an exact revision explicitly. Raw uploads use a byte stream because the
Azure CLI request helper otherwise reparses and reserializes JSON even with an
octet-stream content type. This behavior was reproduced with the installed CLI,
corrected, and covered through the real request helper; byte verification and
conditional restoration do not depend on mocks skipping that transformation.

### Slice 2 verification

Verification on 2026-10-08, using the same isolated Python/package/config setup
described for slice 1:

- **36 new mutation regressions**; **153 standalone regressions passed** using
  `python -m unittest discover -s src\logicapp\azext_logicapp\tests\latest
  -p 'test_*regressions.py' -q`. Coverage includes exact ETags, validation,
  acknowledgement/confirmation, target/auth behavior, races, uncertain receipts,
  guarded restoration, Stateless configuration, secrets and raw body bytes.
- Complete offline/additivity/regression suite: **416 passed, 299 subtests
  passed**, including all six stock CLI additivity checks, using
  `python -m pytest src\logicapp\azext_logicapp\tests\latest
  -p isolated_test_state -q`. An initial Windows fixture cleanup hit a transient
  executable-file lock; both its isolated rerun and the final full suite passed.
- Built and installed **0.1.13** in a session-only extension directory. Actual
  installed CLI commands against an owned Functions 4.15.2 host and a private
  Azurite on random ports verified Stateful/Stateless updates, saved local
  context, export/show ETags, stale-delete rejection, required acknowledgement,
  unchanged no-op, nested runtime-validation rejection without writes, kind
  conversion rejection, exact readback, authored literal/configuration
  preservation, execution of the updated starter workflow, and file-only delete.
  External inventory polling confirmed eventual workflow removal while sibling,
  shared and another workflow's files stayed unchanged.
- Installed cloud-mode update/delete passed through **11 faithful ARM request
  fakes**, including conditional PUT/DELETE and validation. **No live Azure
  operation was performed**; deployed behavior still needs authorized live
  verification. The user's installed extension and global context/runtime
  records were unchanged. Both owned host and private emulator were stopped;
  no external emulator was claimed or stopped.
- Compilation, error-level Pylint and `git diff --check` passed. The same
  bytecode-only dependency/import-check limitations from slice 1 apply.

That verification completes only phase 1.2's guarded existing-workflow
update/delete, not triggers, run recovery or the later phases.

## Slice 3: individual workflow state, not whole-app lifecycle

Version 0.1.14 adds public `workflow enable` and `workflow disable` for deployed
**Standard Stateful and Stateless workflows**, using explicit `-g/-n`, a named
cloud context, or the active cloud context. It preserves the shared target
validation rules and does not register or replace any core app lifecycle command.
Consumption, hybrid hosts and deployment slots are not newly supported targets.

### Authoritative API and local boundary

The documented mechanism [16] is the app setting
`Workflows.<workflowName>.FlowState = Enabled | Disabled`.
The commands use the supported App Service application-settings APIs [17,18]:

```text
POST <site-resource-id>/config/appsettings/list?api-version=2018-11-01
PUT  <site-resource-id>/config/appsettings?api-version=2018-11-01
     {"properties": <complete string dictionary>}
```

These return HTTP 200 StringDictionary envelopes. The public workflow resource
API is not evidence of a separate Standard state-action API; Consumption
`Microsoft.Logic/workflows/enable|disable` does not establish a Standard route.
No settings ETag or transactional compare-and-swap guarantee is invented.

An owned real Functions **4.15.2** workflow host rejected the guessed live local
`POST /runtime/webhooks/workflow/api/management/workflows/<name>/enable|disable`
routes for both kinds with 404 `InvalidFlowExtensionRequestRoute`.
Public commands therefore reject local hosts/contexts **before requests, prompts,
file edits or restarts**. The documented local companion is to set FlowState
under `local.settings.json.Values` and restart one's own host. Setting Disabled
before startup was verified to report `isDisabled: true` for both kinds; that
does not create a live local state-transition API.

### Safety, verification and actual semantics

The commands establish supported workflow existence/kind/state before reading
settings. The caller needs runtime-read, app-settings-list and
app-settings-write permissions; app identity and connector ACLs are distinct.
Unknown kinds/state, malformed metadata/settings, duplicate case-insensitive
settings keys or masked values fail without resending guessed data.

**PUT replaces the full app settings map.** Only the selected FlowState value
is intentionally changed; all other values, including credentials and Key Vault
references, are retained from an in-memory snapshot. Both actions require
confirmation (or `--yes`) and **`--allow-non-atomic` independently of `--yes`**.
The metadata and complete settings are checked again after confirmation.
Those checks catch intervening changes but **cannot prevent a lost unrelated
update between the final read and PUT**. Even an exact receipt and readback
cannot prove no concurrent value was overwritten. Coordinate all settings
writers. No automatic retry, unconditional recovery or rollback of unrelated
settings is performed. App-settings changes may have hosting/reload effects.
Definitions, shared connection wiring, artifacts and history are not modified.

After a valid receipt and exact configuration readback, one runtime observation
reports a stable result:
`{workflow, workflowKind, action, requestedState, configuredState, runtimeState,
runtimeConvergence, runtimeObservationError, verification}`.
`action` is `configured` or `unchanged`; `verification` is
`appSettingsReadback`. `runtimeConvergence` is `converged` when metadata matches,
`pending` when it differs, or `unknown` when the observation request fails,
with explicit `notFound`, `unauthorized` or `unavailable` category. Pending and
unknown results include warnings. Malformed post-write metadata is an error,
not a success-shaped unknown fallback. Uncertain receipts or unverifiable
configuration return errors with explicit outcome uncertainty.

Already explicitly configured requests use two HTTP calls without PUT or
confirmation, even if runtime propagation is pending. Absent settings are not
presented as explicit Enabled configuration. A changed operation uses at most
seven HTTP calls; there is no polling helper, wait flag or claimed hard deadline
for the inherited REST transport. Results and errors do not expose raw settings,
snapshots, signed URLs or provider error bodies. Sensitive request/response
logging is suppressed at the actual Azure CLI REST logger, even under `--debug`,
and restored after each request. No snapshot files are created.

As documented for Standard [3], disabling stops new ordinary workflow
instances/triggers after propagation while **existing in-progress/pending runs
continue**. It is not cancellation, run-history purging or trigger-state reset.
Enabling may process accumulated trigger backlog. Neither command calls app
stop/start/restart. Matching metadata is **not** proof of drained runs or that
every dispatcher is quiescent.

Verification on 2026-10-08, before runtime-doctor integration:

- **31 focused state regressions; 184 standalone regressions passed**, using
  `python -m unittest discover -s src\logicapp\azext_logicapp\tests\latest
  -p 'test_*regressions.py' -q`. Cases cover both models, ARM/case-variant
  envelopes, local/slot/input/auth gates, snapshot races, ambiguous writes,
  exact configuration readback, pending/unknown observations, no-op behavior,
  secrets/Key Vault references and actual CLI REST-helper debug suppression.
- Full latest suite: **447 tests and 352 subtests passed**, including all six
  genuine stock Azure CLI 2.67 additivity checks, using
  `python -m pytest src\logicapp\azext_logicapp\tests\latest
  -p isolated_test_state -q`.
- Built and installed the **0.1.14 wheel** only in a session extension directory.
  Actual installed commands on an owned Functions 4.15.2 host with private
  random-port Azurite verified **eight local rejection cases** across both
  workflow kinds and explicit/context targets. Project files, enabled metadata,
  list/show/export behavior and runtime ownership remained intact.
- Installed cloud-mode commands exercised **35 faithful HTTP request fakes**
  through the real CLI REST helper, with five whole-map PUTs. They verified
  Stateful/Stateless configured/converged, pending, unknown, context/active target,
  missing acknowledgement, no-op and uncertain-provider-receipt behavior,
  retained unrelated values and private output under `--debug`.
  **No live Azure operation was performed**; authorized deployed verification
  remains a limitation. The user's global extension/context/runtime records
  stayed unchanged, and both owned processes were stopped.
- Error-level Pylint, compilation and `git diff --check` passed. External
  dependency import/name checks remain excluded for the bundled bytecode-only
  CLI distribution, as in earlier slices.

The independent runtime-doctor increment is integrated below. State verification
alone does not complete the combined release, triggers, recovery or later roadmap
work.

## Parallel increment: read-only local runtime doctor

Combined 0.1.14 includes `az logicapp runtime doctor`, integrated from sibling
commit `449d19af23cdeceadabc5a79cd88088141015c96` after the enable/disable slice was
verified and committed. It is a **local-environment preflight**, not a repair
operation, cloud diagnostic or workflow business test.

It reports curated findings for project JSON/shape, selected child-environment
tools and versions, bundle cache/configuration, literal setting/parameter
references, configured literal-loopback storage, and host PID/creation/listener
identity plus optional `/admin/host/status`. No Azure lookup, configuration
rewrite, install/download, start/stop, credentials or storage data-plane request
is performed. Secrets, raw server/subprocess output and complete process/settings
records do not appear in findings.

**Exact tool/bundle compatibility remains a required `unknown`.** A responsive
Functions 4.15.2 host and matching cache do not certify an exact supported
tool/bundle combination. An otherwise responsive evaluated project normally exits
**`2`**, not `0`. Unknown is distinct from a required failure (`1`) and from
healthy certification. `0` means no required failures/unknowns, still not
business correctness; `--strict` also makes optional problems exit `2`.
JSON/table findings and `--query` are formatted **before** diagnostic nonzero
exits. A stopped host may be acceptable offline, but unavailable configured
local storage remains a required failure. See the
[full runtime doctor contract](runtime-doctor.md) for local/context targeting,
unresolved expression/configuration boundaries and per-probe timeouts.

This completes the bounded local doctor, not phase 1.6's log-streaming/cloud
diagnostic work. **Execution controls, including useful HTTP callback retrieval,
are the next workflow increment** under the user-endorsed prioritization.
No trigger, run recovery, deployment or full-app download feature was added.

### Combined 0.1.14 verification

Verification on 2026-10-08 after integrating both surfaces:

- **67 focused tests and 100 subtests passed** for
  `test_workflow_state_regressions.py` and `test_runtime_doctor.py`.
- Complete latest suite: **483 tests and 402 subtests passed**, including all six
  genuine stock CLI 2.67 additivity checks, with
  `python -m pytest src\logicapp\azext_logicapp\tests\latest
  -p isolated_test_state -q`. The final standalone state/safety suite had
  **184 regressions passed** before integration.
- Built and installed the combined **0.1.14 wheel** in a fresh session-only
  extension directory. The installed state harness again passed eight local
  gates and 35 faithful cloud HTTP fakes, including real REST-helper debug
  privacy and preservation of unrelated settings.
- Ran the unchanged sibling doctor smoke harness against the combined installed
  wheel, relocating only its artifacts into this session. An owned Functions
  **4.15.2** host and private random-port Azurite verified JSON/table/query
  findings on exits `1`/`2`, required compatibility unknown despite a verified
  Running host, local-context routing, missing literal references, stale/unowned
  runtime evidence, strict mode, secret omission and unchanged project/state/
  environment snapshots. Exit `0` formatting/event cleanup was checked with an
  **explicit synthetic report fixture**, not presented as observed compatibility
  certification.
- Both smoke harnesses verified unchanged global user extension/context/runtime
  records and cleaned up only their own host/emulator/server processes.
  **No live Azure operation or PR was performed.** Deployed state changes still
  require authorized live verification.
- Combined error-level Pylint, compilation and `git diff --check` passed, with the
  previously stated external bytecode-only dependency import/name-check limits.

## Verified first-party references

The baseline investigation used these sources; relevant implementation and slot
contracts were rechecked on 2026-10-08. Service documentation can change, so verify
the next increment's support and response shapes before implementing it.

1. [Core `az logicapp` command inventory](https://learn.microsoft.com/en-us/cli/azure/logicapp?view=azure-cli-latest).
2. [`az logic`: Consumption and integration-account commands](https://learn.microsoft.com/en-us/cli/azure/logic?view=azure-cli-latest).
3. [Manage workflows in the portal](https://learn.microsoft.com/en-us/azure/logic-apps/manage-logic-apps-with-azure-portal).
4. [Export a complete Standard app to VS Code](https://learn.microsoft.com/en-us/azure/logic-apps/export-standard-logic-app-to-visual-studio-code).
5. [Standard DevOps/deployment model](https://learn.microsoft.com/en-us/azure/logic-apps/devops-deployment-single-tenant-azure-logic-apps).
6. [Standard deployment slots: CLI companions and limitations](https://learn.microsoft.com/en-us/azure/logic-apps/set-up-deployment-slots).
7. [Official automated workflow test SDK](https://learn.microsoft.com/en-us/azure/logic-apps/testing-framework/automated-test-sdk).
8. [Generate workflow unit tests from runs](https://learn.microsoft.com/en-us/azure/logic-apps/testing-framework/create-unit-tests-standard-workflow-runs-visual-studio-code).
9. [Enterprise integration/B2B](https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-enterprise-integration-overview).
10. [Standard hybrid deployment requirements](https://learn.microsoft.com/en-us/azure/logic-apps/set-up-standard-workflows-hybrid-deployment-requirements).
11. [First-party Standard designer VFS client (`relativePath=1`, API 2018-11-01)](https://github.com/Azure/LogicAppsUX/blob/main/apps/Standalone/src/designer/app/AzureLogicAppsDesigner/Services/vfsService.ts).
12. [App Service workflow inventory envelope](https://learn.microsoft.com/en-us/rest/api/appservice/web-apps/list-workflows?view=rest-appservice-2024-11-01).
13. [App Service workflow resource/file envelope](https://learn.microsoft.com/en-us/rest/api/appservice/web-apps/get-workflow?view=rest-appservice-2024-11-01).
14. [Functions host VFS implementation: conditional checks, receipts and file writes](https://github.com/Azure/azure-functions-host/blob/dev/src/WebJobs.Script.WebHost/Management/VirtualFileSystem.cs).
15. [Kudu VFS ETag contract](https://github.com/projectkudu/kudu/wiki/REST-API#vfs).
16. [Documented Standard/local FlowState setting](https://learn.microsoft.com/en-us/azure/logic-apps/edit-app-settings-host-settings).
17. [App Service list application settings, API 2018-11-01](https://learn.microsoft.com/en-us/rest/api/appservice/web-apps/list-application-settings?view=rest-appservice-2018-11-01).
18. [App Service update application settings, API 2018-11-01](https://learn.microsoft.com/en-us/rest/api/appservice/web-apps/update-application-settings?view=rest-appservice-2018-11-01).
