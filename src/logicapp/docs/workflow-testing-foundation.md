# Workflow testing foundation (introduced in 0.1.17)

This increment implements **local preflight and report inspection**, not a
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

The context-creation example deliberately supplies `--port`. Native CLI 2.91.0
x86 qualification reproduced an existing omitted-port defect: Knack supplies a
wrapped default integer that the current context validator refuses. This planning
follow-up does not fix that separately tracked defect; an explicit integer port
works without relaxing the validator.

Select an existing local Standard project and one workflow directory; an explicit
Stateful/Stateless kind is required. These are project-file defaults, not
cloud/local-runtime execution targets or login requirements. Inherited Azure CLI
output/query/subscription flags do not turn this command into a cloud operation.
There is no `test run`,
`prepare`, `generate`, SDK acceptance flag or policy file that enables execution.

## Bounded read-only inspection

Default `plan` writes nothing: no directory, context, cache, runtime state,
fixture, dependency, result store or temporary file. It reads only the selected
`host.json`, `<workflow>\workflow.json`, optional explicit `.csproj`, and project
configuration files needed for recognized literal references. Local-context
selection additionally reads the selected CLI profile's context store when
needed. Optional `--test-project` keeps its existing input-file semantics:
relative paths are resolved from the shell's current directory, not discovered
or inferred from the selected project. No recursive
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

## `results show` is not a native SDK results parser

Only **saved supported schema-1 and schema-2 foundation preflight reports** are accepted. Native SDK output,
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
and validator support. Schema 2.0 accepts the fixed **0.1.22**, **0.1.23**, **0.1.24** and
current public **1.0.0b1** producers and requires
the explicit `planning`/`strict` policy with its matching outcome and exit.
Schema 1.0 does not accept that new field or a rewritten `planned`/exit-0 result;
old clients likewise reject schema 2.0 rather than misreading its new semantics.
The changed `input.options` guidance uses the selected producer's exact catalog.
Historical schema-1 public **1.0.0b1** retains its old guidance. Because the
unpublished public preview version remains **1.0.0b1** across this follow-up,
schema-2 reports from that producer accept exactly its old or new guidance
variant; arbitrary text and mixed message/recommendation variants are rejected.
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

## SDK adoption remains a separate approval

All current reports retain `sdkAdoption: unresolved`, `sdkRestore: blocked`,
`sdkExecution: blocked`, platform qualification/network isolation `unknown`.
No declared Boolean, metadata, `--force`, successful local regression or report
inspection can clear them. This implementation did not restore, load, execute,
bundle, generate or redistribute the test SDK.

The [SDK documentation](https://learn.microsoft.com/en-us/azure/logic-apps/testing-framework/automated-test-sdk)
and [1.0.3 package license](https://www.nuget.org/packages/Microsoft.Azure.Workflows.WebJobs.Tests.Extension/1.0.3/License)
describe separate use/redistribution/data/update terms requiring publisher/legal
clarification. The generator's MIT source license is not the SDK binary license.
External restore does not settle those terms. Mocking is not sandboxing:
MSBuild/test/custom code may execute arbitrary code or contact external services.

**Proposed next increment, not authorized here:** obtain adoption clarification
and separately approve a pinned native SDK/engine/toolchain/runner qualification
with synthetic fixtures and verified network/data/side-effect restrictions.
Only a subsequently implemented, verified native evidence adapter can report
real test verdicts/TRX/action evidence. No later phase, SDK runner, local-runtime
integration test, full logging framework or phase-2 completion is claimed.
