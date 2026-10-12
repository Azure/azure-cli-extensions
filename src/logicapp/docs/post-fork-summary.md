# Post-fork summary and remaining work

## Where we are now

The staging extension progressed from Rohitha's original extension to **0.1.19**.
This guide records historical staging work, not current upstream CI evidence.
Upstream packaging uses preview **1.0.0b1**; see
[contribution provenance](contribution.md) for the migration baseline and limits.
The extension has **55 leaf commands**:
17 additional commands beyond the 38-command safety baseline. Existing Azure
CLI commands are preserved rather than replaced.

The upstream review branch builds on that consolidated fork snapshot. Its
review follow-up recognizes deployed site-qualified run references without
loosening selected-site/workflow/run association checks or changing the fork's
canonical branch.
Following the second upstream AI review, connection publication, removal and
selected-entry restoration also use exact fresh strong VFS revisions. The
user-approved policy requires an existing strongly versioned `connections.json`:
missing/weak revisions fail closed, and managed creation checks before ARM
mutations. Revision conflicts are never retried unconditionally and cannot
authorize ARM cleanup. Provider precondition enforcement and cross-resource
atomicity remain qualification limits.
The third review follow-up rejects duplicate/nonfinite JSON before file rewrites
or execution interpretation and uses buffered execution reads without dropping
raw receive, size, EOF or decode deadline guards.
The fourth review follow-up makes removal readback strict as well and treats a
missing file as unverifiable before ARM cleanup. Each execution request obtains
the selected profile's current token, allowing refresh during long observations
without replaying a failed request.
The fifth review follow-up also strictly decodes workflow-state metadata and
every app-settings snapshot/receipt before mutation or verification. Active
local contexts accept ephemeral host keys like named local contexts; cloud
contexts still reject them and keys are never stored.
The sixth review follow-up applies the same strict decoder at the shared
site-runtime JSON receipt boundary, preventing duplicate metadata/validation
fields from being discarded before workflow discovery and mutation guards.
Valid finite JSON, case-distinct keys and empty receipt contracts remain supported.
The seventh review follow-up strictly decodes ARM identity/access-policy responses
before destructive ownership decisions and rejects malformed authored workflow
JSON on the runtime-validation reread before POST.
The eighth review follow-up refuses existing policies belonging to another
principal before forced updates and rechecks before ACL publication. Inventory
traversal uses the user-selected limits of 100 pages and 10,000 entries, failing
explicitly without partial results; these are logical traversal limits, not
per-response byte or absolute network-time budgets.
The ninth review follow-up preserves scalar types in connection snapshot,
readback/removal and recovery comparisons, and in workflow no-op detection.
Boolean/integer/float changes can no longer authorize overwriting concurrent
metadata or silently skip an authored edit. Shared paging rejects malformed,
nonfinite, noninteger and deeply nested offsets as ordinary CLI argument errors.
The tenth follow-up performs ARM ownership preflight before managed connection
unlink. Initial malformed/unavailable evidence preserves the selected file entry;
cleanup still uses fresh evidence after verified unlink, so new sharing blocks
resource deletion. Late failures can leave the entry removed with ARM retained,
without replaying stale files or claiming a cross-resource transaction.
The eleventh follow-up applies the shared type-preserving comparison to complete
context-store snapshot rechecks and no-op decisions. Type-only concurrent changes
in unknown store/record/target metadata are conflicts, while reordered identical
object members remain no-ops without replacing file bytes.
The twelfth review's summary-only follow-up distinguishes unsent credential
failures from acknowledged cancellation observation failures, strictly decodes
doctor host receipts/authored JSON, and rejects conflicting inventory continuation
fields/query aliases without following service URLs or returning partial results.
The thirteenth follow-up carries proven pre-send deadline state through execution
reports without clearing acknowledged cancellation or claiming post-send certainty.
CLI continuation envelopes validate their Base64 alphabet before JSON decoding.

The practical result is a more reliable, agent-friendly loop:
**inspect workflows, author changes, manage saved targets, check a local
environment, invoke/observe/recover supported runs, and inspect testing readiness**.
The CLI still does **not** run mocked workflow business tests. Its testing
foundation is preparation and report inspection, not a new workflow engine,
embedded AI, or a completed test runner.

The feature increments and audits were completed before this upstream PR was
opened. No live Azure resources were changed during the audit, and
the user's global extension/configuration/contexts/runtime records were not
upgraded or rewritten. New release wheels were installed only in isolated
validation directories.

## What we fixed in the original feature

| Area | Fix or improvement | Practical impact |
| --- | --- | --- |
| Managed connection failures | Preserve pre-existing resources, reject malformed connection files, and guard restoration of the caller's `connections.json` entry. The audit further removes unsafe automatic ARM compensation, as described below. | A failed operation no longer assumes it can delete another writer's connection or replay an ACL snapshot. |
| Shared identities/connections | Respect the actual connection identity and retain shared user-assigned identity access/resources instead of treating every identity on an app as exclusively owned. | Less risk of breaking another app when removing a connection. |
| Process ownership | Verify PID plus creation identity instead of trusting a PID alone; refuse unknown/stale identities. | Reduces the risk of stopping an unrelated process after Windows recycles a PID. |
| Managed dependency environment | Make selected Core Tools and dependencies visible to child processes without changing global `PATH`. | Local startup can use the compatible managed installation without altering the user's shell/tool setup. |
| Foreground runtime bookkeeping | Track foreground ownership and retain shared CLI-owned Azurite while runtimes still need it. | Exiting one runtime does not incorrectly tear down another runtime's storage. |
| VFS/file recovery | Preserve unrelated configuration entries, reject unreadable/malformed input, and detect changed target entries during guarded recovery. | Failures are less likely to overwrite somebody else's configuration. Remote file recovery is still not a universal transaction. |
| Static validation | Report malformed trigger shapes as structured findings and continue independent checks. | Agents receive useful findings instead of an unhandled exception that hides other problems. |

## What we added

| Increment | New capability | What it enables and what it does not promise |
| --- | --- | --- |
| 0.1.12 | `workflow list`, `show`, `export` | Discover workflows, inspect metadata/authored definitions and export one workflow. This is not a complete app backup. |
| 0.1.13 | `workflow update`, `delete` | Guarded changes to existing same-kind workflows, with explicit non-atomic risk acknowledgement where required. No implicit deployed creation or kind conversion. |
| Combined 0.1.14 | `workflow enable`, `disable` | Persist deployed Standard workflow FlowState and report one runtime observation separately. No promise of dispatcher quiescence, draining runs or cancellation. Live local transitions remain unsupported/gated. |
| Combined 0.1.14 | `runtime doctor` | Read-only local tool/configuration/storage/host/ownership preflight. It neither repairs the environment nor certifies workflow business behavior. Required exact tool/bundle compatibility remains unknown; otherwise responsive projects normally exit 2. |
| 0.1.15 | `run wait`, `cancel`, `resubmit` | Bounded Stateful Standard observation and confirmed recovery. Timeout does not cancel; cancellation acknowledgement is not final cancellation; resubmit verifies retained trigger-history association and never guesses a new run ID. |
| 0.1.16 | `context list`, `show`, `update`, `delete` | Complete management of the original extension's saved target shortcuts, alongside existing create/use. Active deletion confirms and clears selection without choosing a replacement. Contexts are not credentials, subscriptions, tenants, or deployed environments. |
| 0.1.17 | `test plan`, `test results show` | Bounded local authoring/reference/test-project declaration inspection, explicit optional report saving, closed sanitized reports and explicit workflow-file drift inspection. Every business-test count remains zero and SDK restore/execution remain blocked. |

## Cross-cutting improvements

Commands intended for automation expose stable structured output, inherited
JSON/table/query formatting, meaningful diagnostic exits, and explicit target,
confirmation and uncertainty boundaries. Nonzero reports are formatted before
exit rather than being discarded. Acknowledged requests, observed outcomes,
configured state, runtime observations and unavailable evidence are kept distinct.

Saved-context writers share bounded advisory locking, snapshot checks and atomic
replacement. This protects cooperating current writers, not arbitrary old/manual
writers or every filesystem. Corrupt active stores fail instead of silently
selecting the current directory; original no-context offline authoring defaults
remain.

Execution uses a dedicated bounded authenticated transport without redirects or
mutation retries. SDK test adoption remains a separate policy decision:
declaring a package is not installing it, inspecting a report is not passing a
test, and mocks do not establish a security/network sandbox.

Help, the extension README and focused guides explain these boundaries. The
[capability investigation](cli-capability-investigation.md) distinguishes
implemented extension functions, existing Azure CLI companions, unfinished work
and unsupported platform behavior. Existing connector trigger/action discovery
and configured-trigger inspection are not duplicated.

## What the post-fork audit found and fixed

Two agents reviewed correctness and behavioral coverage across all **11
post-fork commits through 0.1.17**. Repairs and regressions are consolidated in
0.1.18.

| Finding | Repair | Why it matters |
| --- | --- | --- |
| Connection rollback could delete a competing writer's resource after a rejected write or an acknowledged unconditional upsert. ACL deletion/replay had the same ownership problem. | Retain ARM resources and ACLs after failures; attempt only guarded file restoration. Report possible changed authentication/access and manual recovery. | Avoids destructive compensation based on an absence check or acknowledgement that cannot prove exclusive ownership. |
| Execution budgets were not checked at empty/late response EOF or after decoding. | Recheck request and overall deadlines at both boundaries, without POST retry. | Late receipts are not incorrectly reported as timely acknowledgements. |
| Context JSON accepted overflowing numbers and exposed recursion failures. | Reject nonfinite numbers and excessive nesting with sanitized errors; preserve invalid bytes. | Corruption does not become silent selection/defaulting or an unhandled parser failure. |
| Case-duplicate workflow metadata was chosen by insertion order. | Reject equal or contradictory ambiguous fields before downstream mutations/confirmation. | Prevents an ambiguous kind/state from authorizing a write. |
| Malformed continuation URLs leaked a raw parsing exception. | Return a sanitized service/protocol error. | Inventory failure is explicit and automation-friendly. |
| Malformed runtime/child ownership records could raise raw errors or remove storage guards. | Validate known record shapes, refuse corrupt ownership and retain uncertain cleanup/shared-storage state. | Missing ownership proof is not treated as permission to stop or release shared infrastructure. |
| Tree termination trusted descendant PIDs and could re-adopt a recycled root PID. | Carry original creation identities through snapshot/revalidation/signaling, including the saved root identity. | Replacement processes are rejected rather than adopted as the caller's process. Portable check-to-signal races and manual record writers remain qualification limits. |
| Coverage relied too heavily on direct functions and session-only smoke scripts. | Add committed real-CLI parser/format/exit-hook and offline wheel-content/version/dependency tests, plus race/failure regressions. | Protects packaging and the command interface agents actually use, not just internal helper behavior. |
| Report cleanup can fail after a complete destination was published. | Make exit 6 explicitly mean publication or cleanup failure; test fsync, concurrent destination creation and post-publication cleanup. | An agent knows to inspect the destination before retrying rather than assuming nothing was written. |

**Important tradeoff:** failed managed connection operations can now leave
resources, changed authentication or granted ACL access requiring deliberate
manual recovery. An unconditional ARM upsert offers no verified exclusive
compensation ownership, so automatically deleting/replaying that state is unsafe.
Another read cannot close this race. There is no invented conditional-delete
guarantee or silent rollback-success claim.

## What the second audit found and fixed

A fresh independent correctness pass and targeted parent review found additional
ownership and incomplete-observation defects. Version 0.1.19 repairs them without
adding commands or relaxing the SDK testing gates.

| Finding | Repair | Why it matters |
| --- | --- | --- |
| Child discovery could cross a recycled root or child PID and adopt an unrelated process's new birth identity. | Revalidate the saved root after enumeration and prove descendant ancestry/birth ordering; unknown candidates retain non-signaling cleanup/storage guards. | Stops observation from manufacturing termination authority. Portable check-to-signal races are still not eliminated. |
| Doctor buffered HTTP reads could renew idle timeouts while headers/body bytes trickled; error bodies could also claim `Running`. | Budget raw receives before buffering; check the final inspection budget and accept host-state enums only from HTTP 200. | Slow or unsuccessful probes cannot certify a running host. |
| Execution header/proxy buffering and compressed bodies could consume wire bytes without returning control to deadline checks. | Use request-scoped HTTP/HTTPS pools to budget raw receives, including proxy CONNECT; request identity encoding and reject compressed bodies before decoding. Preserve TLS verification and unrelated Requests sessions. | Keeps buffering/decoding from hiding elapsed time; a POST with an unreadable receipt remains uncertain and is not retried. |
| Connection file writes could report success after unfinished receipts or without observing the selected entry. Deletion then authorized ARM cleanup while the file still referenced the connection. | Require completed receipts and selected-entry readback before wiring success or destructive cleanup. Preserve ARM/ACL state on creation failures. | Prevents cleanup based on an unverified unlink. Readback is an observation gate, not CAS or a universal transaction. |
| Empty asynchronous runtime-validation receipts were treated as completed workflow validation. | Preserve the validation HTTP status and reject unfinished receipts before confirmation or workflow publication. | Acknowledged validation requests no longer authorize a workflow replacement before validation completes. |

Protocol receipt cases are synthetic local/cloud fixtures, not a claim about
their live Azure frequency. Slow-body/header and compressed-response regressions
exercise actual, fully cleaned loopback socket readers rather than only fake
chunk iterators. Native TLS fixtures verify both trusted synthetic certificates
and rejection of untrusted ones; proxy/header trickling shares the request budget.

## Verification and remaining qualification limits

The current upstream review source passed **765 tests and 1,749 subtests**,
including all six genuine stock CLI additivity checks, six new resubmission
regressions, eight connection revision-policy/race regressions and eight strict
JSON/buffered execution regressions, five removal-readback/token-refresh regressions
and four strict workflow-state/active-context-key regressions. Three further
shared runtime-receipt regressions cover local/cloud metadata, validation and
finite/empty response compatibility.
Three additional regressions cover ARM identity/access-policy decoding before
destructive ownership decisions and strict authored runtime-validation input.
Eight further regressions cover selected-policy type/object/tenant matching,
malformed identity fields, case-compatible identities, a policy changed during
consent, actual page/item thresholds and over-budget rejection before conversion.
Nine more regressions cover type-preserving scalar/nested comparisons, mapping
order and absent sentinels, deep iterative comparisons, selected-entry publication
and removal conflicts, recovery preserving unrelated types, real type-only workflow
edits, and malformed/overflowing/depth-failed CLI paging offsets.
Three new regressions cover initial ARM preflight preserving the complete file,
fresh post-unlink sharing evidence and late invalid evidence retaining ARM without
stale-file replay.
Three further context regressions cover 60 actual-file concurrent type changes
across all writers and metadata locations, 12 proposed type-only changes that must
publish, and reordered identical snapshots that must preserve the original bytes.
Seven additional regressions cover prepared-transport pre-send/post-acknowledgement
credential failures, strict host/configuration JSON, and local/cloud continuation
conflicts plus matching decoded tokens against only the selected endpoint.
Five further regressions cover pre-send credential/setup/entry deadlines, expired
network setup budgets, retained post-acknowledgement state and strict Base64
alphabet rejection with valid offset/paging round trips.
Five further regressions cover tenant-aware managed deletion: missing/malformed
policy tenants, incomplete site principal/tenant evidence without login fallback,
case-compatible complete matches, the same object ID in another tenant, and
site/policy tenant changes after verified unlink. Creation and deletion share the
same ActiveDirectory principal/object/tenant matcher; unrelated or unverified
policies and their ARM connection remain retained.
Selected-site full IDs, foreign/conflicting references, automatic
and explicit history lookup, confirmation-time changes, local references and
the actual prepared Requests transport are covered. All **29 packaged
source/metadata files** matched the fresh review wheel and isolated installation.
An installed-wheel run passed the **complete latest suite:
765 tests and 1,749 subtests**, with production imports confirmed beneath the
isolated installation and all six genuine GA additivity checks included.
Both current complete suites passed without timing observers or changes to native
requests, budgets or assertions. Earlier eleventh-round uninstrumented native
controls remained intermittent, as recorded below.
Source and installed suites were run serially because offline scenarios share a
`.test-work` directory.
Conditional publication/removal/restoration conflicts preserve concurrent
unrelated changes, block ARM cleanup and do not adopt another writer's identical
entry. Missing/invalid revisions are rejected; missing-file creation is gated.
Duplicate members, nonfinite constants and numeric overflow fail before connection
or workflow publication. Maximum-size valid execution responses use 64-KiB chunks
with fewer than 64 clock checks; owned native socket regressions still exercise
raw receive, proxy/header, TLS, EOF and decoding deadline behavior. Removal readback
rejects ambiguous/nonfinite/missing files before ARM cleanup. Repeated cloud polls
obtain current selected-profile tokens; acquisition failure or elapsed command
budgets block further sending rather than reusing stale credentials or replaying
mutations. Whole-map settings responses and workflow-state metadata reject
duplicate/nonfinite JSON at preflight, confirmation, receipt/readback and runtime
observation boundaries. Named/active local contexts accept ephemeral host keys;
cloud/missing contexts and stray ports remain gated. Shared runtime receipts
reject ambiguous metadata/validation before mutation while preserving valid
finite JSON and empty responses. Initial invalid ARM ownership JSON preserves
the entry as well as resources/ACLs; late invalid evidence retains resources
after verified file unlink. Ambiguous local runtime-validation input causes no
POST and no runtime-template success claim. Selected policy identity mismatches
block forced updates; a change during consent blocks ACL publication and retains
the acknowledged connection without unsafe compensation. Inventory traversal
allows exactly 100 pages and 10,000 entries and rejects overruns without returning
partial results. Type-distinct concurrent metadata cannot authorize entry removal,
publication or recovery; type-only authored workflow edits are not false no-ops.
Current focused identity/offline coverage passed **292 tests
and 182 subtests**. Four changed Python files compiled; filtered error-level lint
had no actionable findings.
The precisely recorded context-manager inference exclusions include the tested
workflow-state private logging contexts; this is not an unfiltered lint claim.

The fourteenth follow-up's in-memory negative control failed 41 mutation-safety
cases with the prior tenant-blind delete plan; production bytes were unchanged.
Its first full source attempt exposed the older principal-ID-only mock target in
the removal-publication fixture. That fixture now supplies the complete principal
and tenant expected by the renamed helper; assertions and production guards were
not weakened. The failed log is retained, and both final complete serial suites
passed without native timing observers.

The thirteenth follow-up passed 760 tests and 1,697 subtests in both complete
serial source/installed suites, with focused coverage of 118 tests and 390
subtests and five compiled Python files.
The twelfth follow-up passed 755 tests and 1,653 subtests in both complete serial
source/installed suites, with focused coverage of 155 tests and 419 subtests and
six compiled Python files.
The twelfth follow-up's negative control failed 26 regression subcases with the
previous source loaded only in memory; current source bytes remained unchanged.
Initial focused attempts exposed two mutable-report lint inference warnings and
a test expectation that incorrectly required an absolute cloud URL at the CLI
sender seam. Those assertions were corrected without weakening production guards.
The first full source attempt passed all non-GA tests but failed four GA checks
because its fresh extension directory did not contain the wheel. Installing the
exact new wheel privately restored genuine extension discovery; all six GA checks
and both complete serial suites then passed. Failed logs are retained.

The eleventh follow-up passed **748 tests and 1,595 subtests** in source and in
an installed run with a read-only timing observer on one loopback fixture. Its
focused context/type-comparison coverage passed 48 tests and 174 subtests, with
two compiled Python files.
The eleventh follow-up's new type-change regressions intentionally failed all
72 cases when the old Python-equality behavior was restored in memory; the
production source was not changed for that negative check.
Initial uninstrumented installed controls hit loopback deadline/status assertions
and the unchanged Windows shim's conservative retained-process result. All three
initial failures passed a targeted rerun, and a complete timing-observed suite
passed, but subsequent uninstrumented controls still showed native variability.
The last control retained a private shim record and hit a locked executable during
fixture cleanup. An independent observer subsequently verified all three recorded
PIDs absent before removing only that private fixture directory; no process was
signaled. Failed logs and the record snapshot are preserved. Runtime/doctor code
and test guards were not relaxed; the exact source of the native variability was
not established and universal Windows timing/shutdown reliability is not claimed.

The tenth follow-up passed **745 tests and 1,523 subtests** in both complete
source and serial installed suites. Its focused deletion/lifecycle/identity
coverage passed 117 tests and 303 subtests, with three compiled Python files.
The tenth follow-up's initial focused run exposed an accidentally changed
successful-deletion helper assertion and an outdated malformed-identity assertion.
Both expectations were corrected without changing production guards; the failed
log is retained.

The ninth follow-up passed **742 tests and 1,519 subtests** in both complete
source and serial installed suites. Its focused comparison/connection/workflow/
paging coverage passed 171 tests and 513 subtests, with nine compiled Python files.
The ninth follow-up's initial installed full run hit an access-denied atomic
state replacement in the unchanged native Windows shim fixture. A targeted rerun
reported conservative cleanup-pending; the original launcher PID was subsequently
observed gone. The final serial complete installed rerun passed all 742 tests and
1,519 subtests without code or guard changes. Both failed logs are retained;
these observations do not establish universal Windows shutdown reliability.
Initial focused assertions also incorrectly assumed byte-for-byte preservation
of the input's formatting and a specific JSON decoder recursion threshold. The
fixtures now verify the actual upload bytes/input preservation and explicitly
exercise invalid nested offsets and injected decoding-depth failures.

The eighth upstream review follow-up passed **733 tests and 1,478 subtests** in
both complete source and serial installed suites. Its focused coverage passed
116 tests and 354 subtests, with six compiled Python files.

The seventh upstream review follow-up passed **725 tests and 1,464 subtests** in
both complete source and serial installed suites. Its focused coverage passed
355 tests and 355 subtests, with five compiled Python files.
The eighth follow-up's first focused attempt exposed a consent-change test's
incorrect exception expectation and an OAuth fixture that answered policy GETs
with a connection envelope. Both fixtures were corrected without weakening the
production identity guards; that failed log is retained, not final validation.

The sixth upstream review follow-up passed **722 tests and 1,441 subtests** in
both the source and serial installed complete suites, with two compiled Python
files. Its first concurrent source/installed attempt had two shared-directory
Windows file-lock failures. These runner failures are retained, not claimed as
source failures or final verification.

The fifth upstream review follow-up passed **719 tests and 1,401 subtests**.
Its 29-file wheel separately passed 299 tests and 806 subtests; focused fifth-round
coverage passed 105 tests and 297 subtests with five compiled Python files.

The fourth upstream review follow-up passed **715 tests and 1,354 subtests**.
Its 29-file wheel separately passed 194 tests and 509 subtests; focused fourth-round
coverage passed 144 tests and 416 subtests.

The third upstream review follow-up passed **710 tests and 1,340 subtests**.
Its 29-file wheel separately passed 189 tests and 495 subtests. Twelve changed
Python files compiled with no actionable filtered error-level lint findings.

The second upstream review follow-up passed **702 tests and 1,300 subtests**.
Its 28-file wheel separately passed 114 tests and 275 subtests for connection
lifecycle, workflow guards and CLI contracts before the strict JSON follow-up.

The first upstream review follow-up passed **694 tests and 1,261 subtests** before
the additional connection guards. Its installed wheel passed 75 execution/CLI
contract tests and 196 subtests. These are earlier review snapshots.

The pre-review combined tip passed **688 tests and 1,227 subtests**, including
the five added failure-diagnosis regressions. The second audit's earlier 0.1.19
snapshot passed **683 tests and 1,227 subtests**. Its six genuine
stock CLI additivity checks also passed against that historical installed wheel,
whose **28 packaged source/metadata files** matched the then-current source.
That installed-wheel validation
passed five real-CLI contract tests, 194 focused receipt/validation/identity/
streaming regressions and 22 foundation CLI scenarios. The foundation smoke
guarded zero network/process/context calls; the separate transport fixtures
used only owned, cleaned loopback listeners and synthetic credentials.

The second audit's 17 changed Python files compiled. Error-level lint had no actionable findings
after precisely recorded bundled-bytecode import and tested context-manager/
mutable-report inference exclusions. The full suite retained one dependency
deprecation warning from bundled dateutil, not a source failure. No global
configuration/context/runtime/extension state changed and SDK tests were not run.

The first audit's complete latest suite passed **647 tests and 1,096 subtests**, including
the genuine stock CLI additivity checks. All six additivity checks also passed
against the final installed 0.1.18 wheel. All **27 packaged module/metadata
files** matched source bytes. Installed real-CLI contract checks and the 22-case
foundation smoke passed, with the latter guarding zero network/process/context
calls after suppressing unrelated dynamic extension lookup.

Seventeen changed Python files compiled. Feasible error-level lint had no
remaining actionable findings after explicitly recorded bundled-bytecode,
tested context-manager and mutable-report inference exclusions. This is not an
unfiltered lint-clean claim. Global-state hash checks and whitespace checks passed.

This is meaningful regression coverage, **not proof of 100% coverage or universal
correctness**. Cloud behaviors in the audit use fixtures, native signal races
are simulated, and no live Azure/Linux/macOS qualification or official SDK
business-test execution is claimed. Historical local execution smoke is useful
evidence for its tested setup, not a certification of every tool/bundle/platform.

## Unfinished work and its impact

Basic [usable failure diagnosis](failure-diagnosis.md) now has an exercised
existing-command flow: a real local invalid expression exposed its provider
reason without outputs; a rejected HTTP request exposed its reason in recorded
outputs despite null metadata error. Both left the dependent action skipped and
both succeeded in new runs with corrected inputs. The 28 installed-CLI calls
changed no authored/global files or SDK gates. Owned-helper cleanup was verified
separately after Windows conservatively retained private shutdown records; no
replacement PID was signaled. This is narrow Windows/local Stateful evidence,
not the deeper diagnostic capability below or broad release qualification.

These are remaining capabilities, not additional implementation authorization.
Order below emphasizes the agent author/test/debug loop rather than promising
every item as the next release.

| Remaining work | Current gap or prerequisite | Impact when completed |
| --- | --- | --- |
| Adopt and qualify a real workflow business-test backend | Official SDK use/data/update terms need publisher/legal clarification and explicit approval; qualify runner/report APIs, platform/kind matrix, .NET support horizon and enforceable code/network isolation. An independently approved narrow local-runtime fallback is an alternative, not generic connector mocking. | Agents could evaluate workflow behavior against assertions instead of stopping at authoring preflight. |
| Fixtures, mocks, scaffolding and test generation | No test projects/cases are generated, mocks executed, native verdicts parsed, or assertions revised. Definition/run generation requires verified designer/host metadata and support; no universal offline generation endpoint is established. | Reduces the work needed to create reproducible tests and iterate safely on failures. |
| Deep run/trigger diagnostics and log evidence | Basic top-level failure inspection is exercised in the linked guide. Rich trigger-history failures, nested scopes, loop iterations, retries, request histories, correlation/time filtering, curated evidence export and log streaming remain missing. Cloud diagnosis/telemetry integration should reuse Azure Monitor/hosting companions. | Extends the demonstrated simple action diagnosis to nested, trigger-level and production failures with richer evidence. |
| Deeper semantic/effective-input validation | Nested graph semantics, expressions/cycles, connector contracts and effective settings/parameter/connection resolution are incomplete. | Catches more defects before deployment or invocation and makes preflight findings more trustworthy. |
| Complete existing-app download/import and drift reconciliation | Single-workflow export does not include a coherent host/configuration/connections/assets snapshot. Secret handling, conflict rules and safe import recovery need decisions. | Enables a real local/cloud round trip, backups and controlled edits to existing apps. |
| Intentional deployed workflow creation and supported version surfaces | Current update/delete work only on existing same-kind definitions; app creation is not workflow creation. | Allows agents to introduce new deployed workflows explicitly instead of relying on undocumented file writes or accidental creation. |
| Environment/configuration management | Coherent parameters, host/local/workflow settings, connection parameterization, environment overlays and drift checks are missing. Core cloud app-setting commands already exist. | Makes the same workflow portable between development, test and production with fewer hand-edited files and clearer effective inputs. |
| Production delivery orchestration | Higher-level preflight, environment preparation, deployment status, post-deploy verification and supported recovery are missing; compose existing ZIP/hosting commands. Standard nonproduction slots are read-only with dispatcher off, so do not promise unsupported blue-green/A-B workflow execution. | Turns packaging/deployment primitives into an understandable, repeatable release process. |
| Connection lifecycle and orphan reconciliation | Existing-connection reuse, updates/reauthorization, safe unlinking, useful auth metadata and reconciliation of wiring/ARM resources/retained failed operations are incomplete. | Reduces credential/wiring mistakes and the manual cleanup cost of conservative failure handling. |
| Useful callback retrieval and support-checked trigger recovery | Workflow-specific HTTP callback retrieval, firing diagnostics and supported reset are deferred. Existing management invocation did not need callback retrieval; connector catalogs already discover trigger/action operations. | Supports workflows that genuinely need callback endpoints or trigger-specific recovery without duplicating discovery. |
| Broader execution recovery and models | Action-level reruns, richer recovery orchestration and broader Stateless/history behavior require documented per-platform support; current controls are Stateful-gated. | Extends recovery beyond whole-run resubmission where the platform actually supports it. |
| Expanded saved-target binding | Subscription/tenant/slot binding, rename, migration/bulk handling and synchronization are not implemented. Current shortcuts inherit CLI login/subscription. | Makes multi-environment/multi-account automation more reproducible and less dependent on global CLI selection. |
| Workflow-aware permissions and secret integration | Effective RBAC/endpoint authorization diagnosis, keys/rotation and Key Vault integration remain incomplete; identity/ACL presence alone is not caller authorization. Reuse existing Azure commands. | Explains access failures and improves secure configuration without duplicating the Azure infrastructure CLI. |
| Artifacts and custom-code lifecycle | First-class management/build/testing for maps, schemas, assemblies, rules, connectors and custom code is missing; packaging alone is not lifecycle support. | Supports more complex applications and validates their non-workflow dependencies. |
| Consumption, B2B/integration-account and hybrid composition | Standard is the first target. Compose existing `az logic` companions and separately assess hybrid hosting rather than claiming parity. | Broadens useful coverage without misleading users about model-specific capabilities. |
| Live-cloud, portable and release qualification | Authorized live Azure, Linux/macOS, supported tool/bundle matrices, cloud failure/race scenarios and repeatable release CI/distribution remain future work. The global user installation is still unchanged. | Establishes where the CLI can be relied on outside the current isolated Windows/fake-cloud validation setup. |

The highest-value missing loop is **real business tests plus curated diagnostics**:
an agent can currently make supported edits and observe supported executions,
but cannot yet automatically prove the intended workflow behavior and inspect
every detailed failure through one complete CLI workflow.

## Related guides

[Capability matrix and roadmap](cli-capability-investigation.md),
[execution controls](workflow-execution.md),
[saved contexts](context-management.md),
[runtime doctor](runtime-doctor.md), and
[testing foundation](workflow-testing-foundation.md).
