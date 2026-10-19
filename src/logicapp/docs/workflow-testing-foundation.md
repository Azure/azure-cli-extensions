# Workflow testing foundation (introduced in 0.1.17)

## Native SDK workflow (since 0.1.25)

`test create -> test plan -> test run -> test results show` now supports native
C#/MSTest projects using the **Microsoft Logic Apps Tests SDK**, not a CLI WDL
simulator. Planning remains strictly read-only and preserves the older
foundation protocol below; its blocked SDK fields do not become execution
permission. `run` has a separate versioned execution record and explicit
per-invocation approvals.

```powershell
az logicapp test create --context development --workflow Orders
az logicapp test plan --context development --workflow Orders
# Author and review the generated C# tests and trigger fixture before enabling them.
az logicapp test run --context development --workflow Orders --accept-sdk-terms --trust-project --restore
az logicapp test run --context development --workflow Orders --accept-sdk-terms --trust-project --report-path .\Reports\native.json
az logicapp test results show --result-file .\App\Reports\native.json --workflow-file .\App\Orders\workflow.json
```

All three project commands use explicit `--path`, otherwise a named/active local
context, otherwise CWD. Named cloud contexts remain refused even with a path.
Relative `--output-path` and `--report-path` use the selected project; explicit
`--test-project`, `--nuget-config` and results-inspection inputs use shell CWD.
Windows drive-relative outputs are refused.

### Source-only scaffolding

The default new directory is `Tests/<workflow>` under the local project.
`create` refuses existing directories rather than adopting, merging or
overwriting them. It writes `Workflow.Tests.csproj`, `WorkflowTests.cs`,
`trigger.json`, `global.json`, `NuGet.Config` and `.gitignore`; no SDK binary,
credential, connection, setting or parameter values are copied. Multiple
triggers require explicit `--trigger`. The project links/copies the **current
selected workflow** at build time, rather than treating a stale generated
definition as the test subject.

The starter is ignored and begins with an inconclusive guard, before the SDK
call. Fill in synthetic trigger data, mock external operations using
`ActionMock`, and author meaningful business assertions before removing both
guards. A successful workflow status alone is not business coverage. Tests can
assert native action outputs, for example
`Assert.AreEqual(3, result.Actions["Calculate"].Outputs.Value<int>());` for an
authored integer Compose scenario. The CLI never infers expected business
values or silently modifies assertions to obtain a pass. Ordinary C#/MSTest
authoring remains available; no new JSON scenario/assertion language is required.

`plan` discovers the default scaffold's `.csproj` when present. It inspects XML
only, including exact bracketed package versions. This is not executable test
discovery, import evaluation or approval to restore.

### Context defaults and report compatibility (0.1.26)

Version 0.1.26 also repairs omitted `context create --port` handling at the CLI
boundary without relaxing stored-context validation. Supported 0.1.25 native
and preflight JSON remains inspectable with its original finding catalog and
historical counts; saved approval flags never authorize a new native invocation.

### Deployment boundary

`deployment package` omits an entire dedicated directory with declared native
test intent: an unconditional literal `IsTestProject=true` or a direct SDK
package reference in a `.csproj`. Renamed and existing test projects are
recognized without running MSBuild. A marker named `Workflow.Tests.csproj` or
`.logicapp-test-state` alone is insufficient; conflicting declarations or
mixed production/test projects are refused. Thus fixtures,
source, restored SDK packages, raw results and test `bin`/`obj` output under that
boundary do not enter the deployment ZIP. Raw `.trx` files elsewhere are also
excluded, case-insensitively. Ordinary runtime assemblies are not blanket-excluded.

If test sources/state share the deployment root, contain `host.json` or
`workflow.json`, or contain runtime `.dll`/`.exe` files outside the dedicated
test artifact directories (`bin`, `obj`, `fixtures`, `TestResults` and
`.logicapp-test-state`), packaging refuses rather than silently remove runtime
content. Move tests to a dedicated directory. The CLI does not edit the root
`.funcignore`, and generated `.gitignore` is not deployment policy. Arbitrary
trusted test/build code can write outside these known boundaries: inspect the
package manifest and use `.funcignore` or external directories for other private
fixtures/artifacts. This is not universal sensitive-data detection.

Only an absent `.funcignore` means no user exclusions. An existing unreadable,
non-file or invalid UTF-8 ignore file stops packaging before output is written.
`local.settings.json` is always excluded case-insensitively, including nested
copies, independent of content-pattern secret scanning. ZIP and manifest paths
must identify distinct files; normalized paths and existing filesystem aliases
are checked before either destination is overwritten, even with `--force`.

### Explicit execution and dependencies

Review the [SDK 1.0.3 license](https://www.nuget.org/packages/Microsoft.Azure.Workflows.WebJobs.Tests.Extension/1.0.3/License),
including internal-use restrictions, redistribution/commercial-use restrictions,
data collection and updates. The CLI's MIT license does not license the SDK.
Obtain publisher/legal clarification where needed. `--accept-sdk-terms` records
the caller's acknowledgement for **this invocation**, not approval inferred
from a saved report, context, previous run or `--force`. No SDK redistribution
or installation into the Azure CLI Python environment is performed.

`--trust-project` separately acknowledges executable restore/build targets,
imports and test code. The CLI suppresses implicit ancestor Directory.Build
props/targets, but does not validate the entire build graph or sandbox explicit
imports, SDK/package targets, custom tasks or test code. Mocking is not a
network firewall. No denied-egress, credential isolation from the operating
system, connector certification or live-Azure qualification is claimed.

The qualified package combination is SDK **1.0.3**, engine **1.165.50** and
MSTest **4.0.2**, targeting **net8.0**. Scaffolding pins exact NuGet versions,
selects SDK **8.0.426** with latest-patch roll-forward, and creates a source
configuration that clears inherited feeds and selects official NuGet.
Execution requires a selected .NET 8 SDK; the target framework alone does not
select that SDK in an existing project. .NET 8 support ends **2026-11-10**.
Future toolchain/engine/runner combinations require separate qualification.
Matching a lockfile is not a dependency-security audit or binary attestation.

`--restore` explicitly allows restore using a reviewed `--nuget-config`,
otherwise the `NuGet.Config` beside the test project. Existing lockfiles use
locked mode; a new restore creates `packages.lock.json` for review. Commit that
lockfile, not package binaries. Without `--restore`, both build and test use
`--no-restore`; missing/unqualified dependency evidence fails rather than
silently downloading. An existing native MSTest project can skip `create` via
`--test-project`, with its own reviewed .NET selection/configuration and the
same locked-version contract.

Home, NuGet packages/HTTP cache, Azure configuration and temporary directories
are project-private under `.logicapp-test-state`. Credential/plugin/startup-hook
environment variables and inherited user feed configuration are not passed
through. Native environment variables use an essential-platform allowlist;
proxy/credential environment configuration is not inherited. Explicit
configuration may still contain secrets and is executable/trusted input.
CLI telemetry opt-out **does not establish that SDK telemetry is disabled**.
No global tool, package, context or configuration changes are requested.

Build/test are serialized for cooperating CLI invocations by the existing
advisory file-lock mechanism beside the selected `.csproj`. `--timeout` bounds
the combined native toolchain/restore/build/test work (default 300 seconds,
1-3600); identity-checked cleanup can take additional time. The runner reuses
the existing launched-process/descendant identity safeguards. It records
observed owned descendants, never stops processes by name, and retains
`process-<step>.json` with an explicit cleanup-pending result when safe cleanup
cannot complete. A later invocation refuses new native work while a prior
process receipt remains in that test project's run state, even if its contents
are malformed. Receipt contents never authorize automatic signalling or
deletion; inspect/reconcile retained ownership evidence before retrying.
Historical run directories and raw TRX without process receipts do not block
new work. This is not process containment: a deliberately detached or
short-lived, unobserved descendant can escape observation. Use a dedicated
container/VM for stronger isolation.

### Native results and exit codes

Native stdout/stderr is discarded, not raw-echoed or exported in JSON.
For restore/build failures, inspect the reviewed project/configuration with
native tooling in an appropriately isolated environment for detailed diagnosis.
The raw TRX is retained locally at
`<test-directory>/.logicapp-test-state/runs/<invocationId>/native.trx`.
It can contain fixtures, outputs, assertion messages, stack traces and paths:
review it as sensitive before sharing. Generated `.gitignore` excludes native
state and build outputs; existing projects must protect their own artifacts.

The CLI accepts only bounded, DTD-free, completed MSTest TRX with consistent
per-test outcomes/counters. Missing, oversized, aborted, contradictory or
unsupported nested results cannot become a partial pass. Entirely skipped
scaffolds and zero discovery are non-passing even when `dotnet test` exits 0.
Passing native test counts do **not** prove that arbitrary C# called the SDK,
executed the selected workflow or asserted useful behavior. Reports always
retain `workflowExecution: notAttested`, `businessCoverage: notAttested` and
`externalIsolation: notProvided`.

| Exit | Native execution meaning |
| --- | --- |
| 0 | `nativeTestsPassed`, with at least one executed/passed native test, or successful report inspection. Inspect skipped counts and coverage too. |
| 1 | Native test failures, including assertion failures or exceptions. Not a business root-cause diagnosis. |
| 2 | Toolchain, dependency, restore, build, runner or native-results error. |
| 3 | Invalid/unsafe/missing local input. |
| 4 | Missing terms or project-trust acknowledgement; no native execution. |
| 5 | Observed selected-input drift, or explicit workflow identity mismatch during inspection. |
| 6 | Explicit report publication failure; inspect the destination before retrying. |
| 7 | Zero executed tests, including an entirely skipped scaffold. |
| 8 | Native invocation deadline expired; no complete verdict. |
| 9 | Safe tracked-process cleanup could not complete; ownership receipt retained. |
| 130 | Interrupted invocation; no complete verdict. |

Original `test run` JSON uses closed `reportType: logicapp-sdk-test`,
`schemaVersion: "1.0"`, with fixed provenance/catalog, permission flags,
selected workflow/project hashes, selected-input stability, native step exits,
counts and explicit coverage limits. Source/configuration bytes are not
exported. Bounded test-tree inputs are compared before/after execution; build
outputs/native state are excluded, and the lockfile is compared separately
after restore. This detects observed drift, not all effective build inputs,
external imports, change-then-revert races or concurrent binary replacement.

Optional sanitized `--report-path` is stdout-only by default, relative to the
selected project, with an existing parent and no clobbering of existing reports
or input aliases. `results show` accepts original closed execution JSON, not
raw TRX. It preserves source outcome/exit and native counts as **historical**
evidence under `phase: inspection`, never reruns, and follows no embedded
artifact path. Schema/provenance checks are not signatures; JSON is unauthenticated
data and cannot authorize later execution. Inspection output is not a new
execution report.

### Qualification and known native SDK limitation

Private synthetic Windows x64 qualification exercised real SDK execution for
Stateful and Stateless workflows, distinct trigger/mocked HTTP values and
meaningful action-output assertions. Mocked HTTP actions did not connect to an
owned loopback listener. Deliberately incorrect assertions produced genuine
native failures, and zero/ignored native tests were not treated as passes.
This is not a complete OS/architecture/connector or live-workflow matrix.

SDK **1.0.3** with engine **1.165.50** also reproduced an
`InvalidCastException` when mapping a valid nonempty typed top-level workflow
output into SDK result definitions. The failing synthetic definition and native
evidence were retained. The CLI does **not** remove outputs, rewrite workflow
semantics, patch SDK binaries or manufacture a pass around that failure.
Affected authored tests fail through the native runner; action-output assertions
were separately qualified. Publisher fixes require new qualification.

## Read-only foundation contract

The original foundation increment implements **local preflight and report inspection**, not a
workflow test runner. It provides deterministic, noninteractive tools for agents
to inspect authored inputs and identify the next restricted action. A valid
definition, declared package or successful report inspection is never a business
test pass. Every response states `executionState: notExecuted`,
`businessTests: notExecuted`, and zero executed/passed/failed **business tests**.
Errors/warnings count inspection findings, not native tests.

## Commands

```powershell
az logicapp test plan --path .\App --workflow Orders --output json
az logicapp test plan --path .\App --workflow Orders --strict --output json
az logicapp test plan --path .\App --workflow Orders --test-project .\Tests\App.csproj --report-path .\Reports\plan.json
az logicapp context create --name development --path .\App --port 7079 --use
az logicapp test plan --workflow Orders --output json
az logicapp test plan --context development --workflow Orders --report-path .\Reports\plan.json
az logicapp test results show --result-file .\App\Reports\plan.json --output table
az logicapp test results show --result-file .\App\Reports\plan.json --workflow-file .\App\Orders\workflow.json --query "{source:inspection.sourceOutcome,identity:inspection.workflowIdentity,execution:executionState}"
```

`--workflow` is required. The local project is selected by explicit `--path`,
otherwise the named `--context` or active local context, otherwise the current
directory. An explicit `--path` bypasses the active context. An explicitly named
context is still validated; a cloud `--context` is refused even with `--path`,
rather than silently selecting a different local target. A cloud active context
without an explicit local path is also refused. Context selection uses the
current Azure CLI configuration profile; isolated profiles do not inherit a
global active context. Planning does not create or change a context.
CLI argument and context resolution errors are reported by Azure CLI before a
preflight document is available; the report's diagnostic exit policy applies
only after local project selection succeeds.

Local `context create` now defaults to port 7071 when `--port` is omitted.
The CLI boundary normalizes that omitted value without relaxing the strict
stored-context validator or accepting boolean, floating-point or string ports.

Select an existing local Standard project and one workflow directory; an explicit
Stateful/Stateless kind is required. These are project-file defaults, not
cloud/local-runtime execution targets or login requirements. Inherited Azure CLI
output/query/subscription flags do not turn this command into a cloud operation.
The read-only plan itself has no `prepare`/`generate` or SDK acceptance flag.
The separate native `test run` workflow above requires its own approvals and
does not reinterpret a successful plan as permission or execution evidence.

## Bounded read-only inspection

Default `plan` writes nothing: no directory, context, cache, runtime state,
fixture, dependency, result store or temporary file. It reads only the selected
`host.json`, `<workflow>\workflow.json`, optional explicit `.csproj`, and project
configuration files needed for recognized literal references. Local-context
selection additionally reads the selected CLI profile's context store when
needed. Optional `--test-project` keeps its existing input-file semantics:
relative paths are resolved from the shell's current directory, not discovered
or inferred from the selected project. Since 0.1.25, omitting it also permits one
bounded read of the known default scaffold project when present. No recursive
inventory, home/tool/package/credential search, remote schema or NuGet query,
subprocess, executable test discovery, assembly import, host launch or network
probe occurs. Missing files are findings, not generated defaults.

Inputs must be local regular files with no symbolic-link/reparse components.
UNC/device/alternate-stream paths are refused. Each file is capped at 1 MiB;
JSON/XML inspection is limited to depth 48 and 20,000 nodes. JSON requires unique
keys, finite numbers and UTF-8 (a UTF-8 BOM is accepted). XML DTD/entity
declarations are rejected; imports and referenced paths are never followed.
The commands fail closed rather than partially accepting oversized inputs.

The existing authored-document validator supplies **limited top-level** shape,
trigger-kind and `runAfter` checks. An additional known `$schema` URI check does
not download or validate the full remote schema. Nested graphs, expression
semantics, cycles, connector contracts, runtime validation and business behavior
remain explicitly unchecked. Standard kind inspection is not SDK kind/platform
certification. Unknown kinds are not converted to Stateful.

Recognized literal `appsetting('NAME')`, `parameters('NAME')`, and connection
`connectionName`/`referenceName` strings in recognized top-level ServiceProvider/
ApiConnection operation fields are checked only for local declaration presence.
Workflow parameter default declarations can satisfy a literal parameter reference
without an external parameters file. These are heuristics, not expression or effective-value resolution:
references can occur in ordinary text, and alternate syntax may be unchecked.
Encrypted settings, dynamic references and `$connections` expressions remain
unknown. Parameter default **values**, value types and credential validity are not tested.
No configuration values, reference names, expression literals, arbitrary XML,
parser exception text or signed URLs are exported. Findings use generic JSON
pointers where available; individual action/key names are deliberately omitted.
Workflow identifiers supplied on the command line are retained as identifiers:
do not use secret values as workflow names.

Optional `.csproj` inspection reports only direct unconditional literal
`TargetFramework` (`net8.0`, `net9.0`, `net10.0`) and one exact numeric SDK
`PackageReference Version`. SDK-style implicit imports remain unchecked.
Explicit imports, conditions, properties/items/metadata interpolation,
targets/tasks and project references make effective metadata unknown; none are
evaluated. Test sources, mock fixtures, assertions, lockfiles, resolved graphs,
runner/TRX support and installed tools are **not inspected**. A declaration is
not an installed or qualified fact. The `1.0.3` recommendation is a researched
candidate, not proof that any package is installed or certified. Actual SDK
assets target net8.0; computed net10 compatibility and an installed .NET 10 SDK
would not establish native execution compatibility. .NET 8 support ends
2026-11-10; later toolchain adoption requires explicit qualification.

Exact selected workflow and `.csproj` bytes receive SHA-256 identities marked
`restricted-source`. Host/settings/connections/parameters receive no exported
hashes; low-entropy configuration values are not declassified by hashing.
Inspected inputs are reread before reporting and marked stale on observed
changes/removal. This is an observation, not a filesystem snapshot or an atomic
multi-file transaction; later changes and change-then-revert races can escape
observation. Effective build/configuration/test input identity is not claimed.

## Versioned protocol and exits

Since 0.1.22, the closed protocol is `reportType: logicapp-test-foundation`,
`schemaVersion: "2.0"`, with `exitPolicy: planning` (default) or `strict`.
It contains a UUID invocation ID, `phase`, constrained
producer/CLI provenance, workflow name/kind/definition hash, role-based input
identities, coverage, declared-versus-uninspected dependencies, immutable
SDK/policy/capability gates, finding counts, stable rule/category/severity/source
and generic `jsonPointer` locations. Text comes from a fixed rule catalog, not
untrusted file contents. There are no raw native artifacts or action payloads.
The precise closed shape and rule catalog are in `_test_report.py`.

| Exit | Meaning for this increment |
| --- | --- |
| 0 | Successful ordinary `plan` generation (`outcome: planned`), or `results show` inspection (`outcome: inspected`). **Not tests passed.** |
| 1 | Definite authored-definition/literal-declaration issue found by `plan`. |
| 3 | Input/read/parse or report-protocol error. Not a business failure. |
| 4 | `plan --strict` completed inspection but SDK adoption/restore/execution remain blocked (`outcome: blocked`). Also the historical successful-plan result in schema 1.0. |
| 5 | Observed input change during inspection, or explicit definition identity mismatch. |
| 6 | Explicit report destination/publication or temporary cleanup failure; stdout still contains the report. |

Azure CLI argument parsing keeps its normal exit behavior (for example `2` for
unrecognized arguments). Once a valid command invocation begins, JSON/table/
query formatting completes before a report's diagnostic nonzero exit.
Within `plan`, precedence is publication error, stale, input error, authoring
error, then planning success or strict policy blocked. Always read `gates` and coverage too: a reported authoring
error never clears the immutable SDK gate. No plan invocation reports test pass.
Ordinary planning success separates a generated plan from permission to execute.
Use `--strict` when a shell/CI step must fail on the unresolved execution gates.
It does not make static checks more complete, execute tests, or accept SDK terms.
Input, authoring, stale and publication errors take precedence in both modes.

## Explicit report writes

`--report-path` is optional and the only write boundary. Its parent must already
exist and be outside the filesystem root. A relative report path is now resolved
against the selected local project, including an explicit `--path`; absolute
report paths remain unchanged. For example, selecting `C:\Apps\Orders` with
`--report-path .\Reports\plan.json` selects `C:\Apps\Orders\Reports\plan.json`,
regardless of the shell's current directory. This intentionally changes relative
report-path resolution from earlier builds, which used the current directory.
No report is saved unless `--report-path` is supplied, and missing output
directories are not created. Windows drive-relative paths such as `C:plan.json`
are refused; use a fully qualified path or a path relative to the selected project.

The destination must be a `.json`
regular file or absent; existing files require `--force`. Inputs, hard links to
inputs, reserved workflow/config filenames, directories and linked components
cannot be overwritten. `--force` without `--report-path` is invalid.

Invalid/blocked/stale plans can be saved for inspection when the destination is
valid. A same-directory temporary file is flushed/fsynced and published
atomically; non-force publication does not clobber a concurrent existing file.
Owned temporary files are removed in `finally`. Publication failure is explicit;
the original destination is preserved on failed replacement. A cleanup failure
can occur after publication and still reports exit 6. Rechecks are not a
universal CAS guarantee against adversarial concurrent filesystem writers.
After exit 6, inspect the destination before retrying: a complete report may
already have been published even though temporary cleanup failed. Its saved
preflight outcome is not the subsequent publication/cleanup outcome on stdout.
Use an agent-owned trusted output directory. Reports are sanitized, but source
identities and workflow identifiers may still be sensitive; review before sharing.

## Foundation report inspection is not raw native SDK/TRX parsing

This foundation branch accepts **saved supported schema-1 and schema-2 foundation preflight reports**. Raw native SDK output,
TRX, legacy/invented reports, execute-phase reports, unknown versions/fields,
duplicate keys, nonfinite numbers, inconsistent counters/hashes/gates and
arbitrary finding text are rejected without echoing their contents. Both schemas are closed:
unknown fields are rejected rather than raw-echoed as forward-compatible data.
A future version/adapter requires its own explicit validator.
Inspection accepts otherwise-valid schema-1 reports with the exact fixed
producer provenance from the explicitly supported **0.1.17-0.1.21** releases
and the earlier public **1.0.0b1** preview
and the fixed rule catalog. A package-version bump alone does not invalidate
these reports; unknown producer versions still require explicit qualification
and validator support. Schema 2.0 accepts the fixed **0.1.22**, **0.1.23**, **0.1.24**,
**0.1.25**, **0.1.26** and
current public **1.0.0b1** producers and requires
the explicit `planning`/`strict` policy with its matching outcome and exit.
Schema 1.0 does not accept that new field or a rewritten `planned`/exit-0 result;
old clients likewise reject schema 2.0 rather than misreading its new semantics.
The changed `input.options` and `report.invalid` guidance uses the selected
producer's exact catalog. Explicit historical producer lists freeze these
catalogs independently of later version changes.
Historical schema-1 public **1.0.0b1** retains its old guidance. Because the
unpublished public preview version remains **1.0.0b1** across this follow-up,
schema-2 reports from that producer accept exactly its old or new whole-row
guidance variants; arbitrary text and mixed message/recommendation rows are rejected.
Later producers do not inherit the legacy variant merely from a version bump.
Supported older reports retain their recorded
provenance, not a claim of current-input freshness or executed tests.

A valid document is still **untrusted and unsigned**. Fixed producer text and
schema checks do not authenticate its author or prove it was produced by this
CLI. `authenticity: notAttested` is retained; foundation documents cannot encode
a native pass at all. Reports/logs/fixtures are data, never agent instructions.

Successful inspection produces a fresh invocation with `phase: inspection`,
`outcome: inspected`, and original findings. `inspection.sourceInvocationId`,
`sourceOutcome` and `sourceExitCode` retain the historical plan result. A schema-2
report also retains the source `exitPolicy`; inspecting a strict report returns
0 for the read, with source exit 4 still recorded. Schema-1 inspection stays
schema 1.0 and does not invent a policy field. Inspection does not reclassify
historical blocked plans as successful plans.
No embedded file path, artifact URL or command is followed. The only optional
extra read is an explicitly supplied `--workflow-file`; exact byte comparison
reports `matches`, `changed`, `unavailable` or `notChecked`. A match is definition
identity only, not test/source/configuration currency or a native verdict.
No auto-rerun or fixture/golden/assertion mutation occurs.

## Foundation records never grant SDK adoption approval

All foundation reports retain `sdkAdoption: unresolved`, `sdkRestore: blocked`,
`sdkExecution: blocked`, platform qualification/network isolation `unknown`.
No declared Boolean, metadata, `--force`, successful local regression or report
inspection can clear them. The read-only foundation never restores, loads or
executes the SDK. The separate native workflow above requires its own explicit
invocation approvals; SDK binaries are not bundled or redistributed.

The [SDK documentation](https://learn.microsoft.com/en-us/azure/logic-apps/testing-framework/automated-test-sdk)
and [1.0.3 package license](https://www.nuget.org/packages/Microsoft.Azure.Workflows.WebJobs.Tests.Extension/1.0.3/License)
describe separate use/redistribution/data/update terms requiring publisher/legal
clarification. The generator's MIT source license is not the SDK binary license.
External restore does not settle those terms. Mocking is not sandboxing:
MSBuild/test/custom code may execute arbitrary code or contact external services.

The native workflow above implements a separately approved pinned
SDK/engine/toolchain/runner increment. It does not grant approval through
foundation records, claim denied-egress execution or certify connectors,
live-runtime integration, arbitrary business coverage or complete phase-2 scope.
