# Contribution provenance and qualification

This contribution imports the complete Logic Apps Standard extension, not only
the later additions. Rohitha Hewawasam authored the original extension. The original
baseline is `4e50f12d52b13c25de0d90a6955f1fff2d5523f1`; the migration input is
staging commit `3dcef94c0e6856f8e2a3f74e44b7f6b903fa5446` (0.1.19).
Validated staging follow-up `3087a62f999debb4b0dec771b9424f62903959b2`
adds pre-send deadline reporting and strict Base64 continuation decoding.
Follow-up `db3389f47272a2d0cd6298c702f5153102a24fe9` requires managed deletion
to match the selected site's system principal and tenant using creation's shared
ActiveDirectory matcher. Missing or unrelated tenant evidence retains policies
and ARM resources; site and policy evidence are refreshed after verified unlink.
The reviewed follow-up baseline `1eaa335d635e62a41607b4c7d06acd4b96e49dfb`
(historical 0.1.23) includes all later feature and safety increments. These
preserve the original extension and add 19 leaves, for 57 total at that baseline.
The separately reviewed SDK follow-up below adds two further leaves. Upstream
packaging remains at the unpublished preview `1.0.0b1`; the version change does
not invalidate supported saved reports. The upstream contribution retains its
Python 3.10/Azure CLI 2.67.0 minimums, portable GA controls and style helpers
rather than copying staging packaging or machine-specific tests.

The stock-CLI additivity control is generated, not copied from a private
development machine. Each help control runs `python -m azure.cli ... --help`
using the test interpreter's installed CLI with empty temporary configuration,
extension and system-extension directories. Dynamic extension installation,
version checks and telemetry are disabled. This keeps the reference matched
to the CLI under test without requiring live Azure or a frozen help transcript.
Independent assertions pin the 13 existing GA leaves to the core App Service
loader, reject command overrides and preserve all 59 current extension leaves.

The extension-local guides distinguish historical staging evidence from release
qualification. Historical Windows loopback/runtime exercises do not establish
current upstream CI, live Azure, Linux/macOS, every Python version, universal
proxy behavior or repeatable native shutdown/timing reliability. Process cleanup
continues to require PID and original birth identity; unresolved children retain
non-signaling cleanup/storage guards.

The original workflow testing foundation remains read-only with zero executed
business tests. The separately reviewed SDK follow-up below adds source-only
scaffolding and explicit trusted native execution, not implicit approval from a
plan or saved report. No SDK DLL or redistribution permission is included.

Conditional VFS updates, whole-map app settings and ARM operations are not
transactions. Receipt uncertainty, selected-target validation, retention and
privacy contracts are preserved; live cloud validation requires separate scope.

The requested CODEOWNERS line contains exactly the five supplied email identities.
GitHub can match verified-account emails, but effective ownership requires
repository write access and cannot use Enterprise Managed User email identities.
Those account/access qualifications have not been verified. This contribution
does not grant permissions or add collaborators.

## Initial import qualification (historical)

The initial 0.1.19-based import was exercised on Windows with Python 3.12.12, Azure CLI
2.91.0, azdev 0.2.13 and Node.js 22.18.0. This is not a completed Python/platform
matrix or a claim about live Azure. These results predate the complete
0.1.23-based synchronization and do not qualify that later diff.

| Check | Result |
| --- | --- |
| `azdev style logicapp` | Passed pylint and flake8. |
| `azdev linter logicapp` | Passed command, argument, help and custom pylint rules. |
| `azdev verify license` | Passed repository license-header checks. |
| `azdev test logicapp --series --discover --no-exitfirst --pytest-args -q` | Passed 767 source tests. |
| `python -m pytest src\logicapp\azext_logicapp\tests\latest -q` | Passed 767 source tests and 1,749 subtests. |
| `python scripts\ci\test_index.py -q` | Passed 9 checks with the 2 CI-only network checks skipped; index unchanged. |
| Exact native-installed wheel, serial full suite | Passed 767 tests and 1,749 subtests; all production import origins remained under the isolated installation. |
| Source/wheel/installed production bytes | All 29 Python/metadata files matched; Python 3-only wheel and preview/minimum metadata checked. |
| Integrated tenant deletion/lifecycle regressions | Passed 108 tests and 355 subtests; both changed production ASTs matched the validated archive exactly. |
| Source and installed wheel on minimum CLI 2.67.0 / Python 3.12.7 | Each serial full suite passed 767 tests and 1,749 subtests, including GA and real parser/formatter controls; production import origins were verified throughout. This is not a platform/Python matrix. |

Source and installed suites ran serially without timing observers. An earlier
installed control refused one native Windows shim cleanup safely; its final
source and exact installed reruns passed without weakening PID/birth-identity
guards. Native timing/shutdown variability is therefore not claimed resolved.
Default temporary extraction also failed once before private temporary directories
were used; no global cleanup, configuration, PATH or installation changes were made.

Style adaptations use standard indentation formatting and extract bounded
foundation/report checks into helpers. Narrow annotations retain exact integer
type guards and small logging/transport protocol classes; no repository-wide
lint rules or regression checks were disabled.

## Reviewed synchronization qualification

The complete synchronization uses the reviewed 0.1.23 source baseline above,
not the earlier import's test results. All production modules were compared
against that immutable input. Differences are limited to retained upstream
report/testing helper extraction, explicit historical public report producers,
an equivalent CLI subscription-factory import, required parameter help and
escaped help markup. The portable GA controls and Python-only wheel contract
remain upstream-specific.

The current and minimum CLI runs use separate private configurations and
extension installations. Source and exact-wheel suites run serially because
the regression fixtures share a work directory. Windows Python 3.12.12/current
CLI 2.91.0 and Python 3.12.7/minimum CLI 2.67.0 are not a Python 3.10-3.14 or
cross-platform matrix.

| Synchronization check | Result |
| --- | --- |
| Complete current-CLI source suite, with production origins enforced | 853 tests / 2,332 subtests passed. |
| Complete current-CLI exact-installed suite, with production origins enforced | 853 tests / 2,332 subtests passed. |
| Complete minimum-CLI source suite, with production origins enforced | 853 tests / 2,332 subtests passed. |
| Complete minimum-CLI exact-installed suite, with production origins enforced | 853 tests / 2,332 subtests passed. |
| `azdev test logicapp --series --discover --no-exitfirst --pytest-args -q` | 853 source tests passed under the official runner. |
| Source/wheel/both native installations | All 30 production Python/metadata files byte-identical; preview/minimum/Python-only metadata and excluded test content checked. |
| `azdev style logicapp`, `azdev linter logicapp`, `azdev verify license` | Passed style, command/help/argument/custom rules and license headers. |
| `python scripts\ci\test_index.py -q` | 9 tests completed successfully (2 CI-only network checks skipped locally); no index edit. |
| `python scripts\ci\validate_external_source_urls.py --cached` | Passed staged external-source URL policy. |
| `azdev scan --confidence-level MEDIUM --directory-path src\logicapp --recursive --continue-on-failure` | No detected secrets; no added exclusions. |
| `python -m pip check`, tracked privacy and local Markdown links | Passed; no private input URLs/paths/artifacts published. |

The older public Azure Pipelines failure was inspected rather than treated as
green from development evidence. Its Linux Windows-API tests mocked
`sys.platform` without isolating executable discovery; the unit fixture now
supplies its synthetic PowerShell executable without changing native cleanup.
The reviewed timestamp parser also avoids the earlier Python 3.10 parsing gap.
The medium scanner's synthetic credentialed URL is now assembled from explicit
nonsecret test components, preserving identical runtime input, refusal checks
and no-network assertions; no scanner exclusion or privacy test was removed.
Old style/linter jobs compared unrelated main-branch files, including the index.
Those upstream CI diff-scope failures were not worked around by editing the
index or unrelated pipeline configuration.

## CI fixture portability follow-up

Public Azure Pipelines build 361672 exercised the synchronized code. Its Python
3.10, 3.12 and 3.14 jobs exposed a mocked-Windows unit fixture that still queried
the real native exit snapshot on Linux. The fixture now derives that snapshot
from its synthetic process map, including unknown and recycled birth identities.
A four-case regression checks that the fixture never calls native Windows APIs.
The native-call negative control reproduced all eight failing cases before the
repair; all 20 fixture methods passed afterward without a native call.
Production code, cleanup guards, package dependencies and preview version are
unchanged.

Current-CLI source and exact-installed full suites and the minimum-CLI source
full suite each passed 854 tests and 2,336 subtests. The official serial
`azdev test logicapp --series --discover --no-exitfirst --pytest-args -q`
runner passed 854 tests; `azdev style logicapp` and `azdev linter logicapp`
also passed. All 30 production Python/metadata files still match the previously
qualified wheel and both isolated installations.

The minimum-CLI exact-installed full follow-up is not qualified as green.
Separate runs encountered a native Windows cleanup sharing violation and a
context-store replacement access failure. An earlier minimum source run also
returned an unknown state from a one-second loopback probe. These failures were
retained, not hidden with retries or relaxed production guards. The minimum
source full rerun passed; the exact-installed lifecycle, affected context-store
and loopback controls passed together with 88 tests and 372 subtests. These
results do not establish native filesystem or timing stability.

The same public build's Python 3.11 and 3.13 jobs stopped earlier in an unrelated
Storage Sync recording/API-version mismatch. Its style/linter diff also included
unrelated main-branch index and Storage Sync changes that are absent from this
PR's file list. Neither those files nor pipeline diff selection were modified.

## Windows architecture dependency qualification

Both x86 and x64 Windows Azure CLI are preview installation targets. Psutil
[stopped publishing 32-bit wheels in 7.1.2](https://github.com/giampaolo/psutil/blob/release-7.2.2/HISTORY.rst#712);
32-bit Python remains supported upstream only through a source build. The
previous unbounded dependency selected 7.2.2 and failed ordinary x86 extension
installation because Microsoft C++ Build Tools were absent.

The preview therefore requires `psutil>=5.9.0,<7.1.2` on Windows and retains
`psutil>=5.9.0` elsewhere. This is a Windows-only ceiling, not a global exact pin.
The same ceiling applies to x64: real 32-bit Python under WOW64 reports `AMD64`,
so a `platform_machine` marker cannot reliably distinguish the architectures.
This intentionally keeps Windows resolution on an older release; future
dependency refreshes require a qualified x86 binary-delivery strategy rather
than silently introducing a compiler prerequisite.

Current CLI 2.91.0 x86 and x64 used the publisher's signed MSI payloads, extracted
read-only without running installer actions or modifying shared installations.
Both contained native Python 3.14.7 interpreters. Minimum CLI 2.67.0 used its
existing x64 Python 3.12.7 with private configuration and extension directories.
Ordinary `az extension add --source <wheel-path> --yes` succeeded in all three
environments and installed the matching psutil 7.1.1 publisher wheel without
binary-only flags, dependency suppression, constraints or a compiler. A package
mirror was used after a direct package-host TLS handshake failed; publisher
SHA256 hashes and all 30 installed psutil files were independently verified.
TLS verification was not disabled.

| Architecture qualification | Result |
| --- | --- |
| Current x86 source and exact-installed full suites | Each passed 855 tests / 2,366 subtests. |
| Current x64 source and exact-installed full suites | Each passed 855 tests / 2,366 subtests. |
| Minimum x64 source and exact-installed full suites | Each passed 855 tests / 2,366 subtests with the newly resolved dependency. |
| Source/wheel/all three installations | All 30 production Python/metadata files match; production and dependency import origins verified. |
| Wheel dependency markers | 30 Python/platform cases preserve the Windows ceiling, non-Windows range and 5.9.0 floor, including WOW64's `AMD64` result. |

Full suites ran serially. For tests only, the private MSI extractions used an
import-path bootstrap for repository/test dependencies because the MSI
interpreter ignores `PYTHONPATH`; it was removed afterward. No production API,
clock, process observation or ownership guard was patched by that bootstrap.

Separate native probes exercised actual CLI extension loading, PE machine type,
CIM/native birth-identity agreement, listener ownership and real cross-x86/x64
child discovery. Mismatched birth identities refused termination and unknown
birth identities remained nonowning; verified stops and held-handle exit
timestamps succeeded. Both the stock CLI-preloaded psutil 6.1.0 and explicitly
loaded extension psutil 7.1.1 were exercised in all three environments. An
extension dependency does not replace a module already loaded by CLI core.

These results add native architecture evidence, not live Azure/Functions/SDK
qualification or proof that earlier native filesystem/timing variability is
eliminated. On the preceding public fixture-only head, Azure Pipelines build
361916 also passed the five Linux Python 3.10-3.14 jobs, each with 849 tests,
2,336 subtests and five Windows-only skips. Its remaining style/linter failure
identified missing `logicapp` service metadata, addressed through the existing
service registry rather than changing CI selection or exclusions. Later heads
still require their own public CI and completed review.
The Linux/Python matrix and latest-head public review still require successful
upstream evidence.

Latest-head public AI review, current upstream CI/maintainer approval, supported
Python compatibility and effective CODEOWNERS eligibility remain independent
gates. Historical cached-runtime evidence does not close them. The contribution
stays draft while they are unresolved; no live Azure or SDK execution is implied.

### Reviewed local-context planning follow-up

The separately reviewed context-defaults change selects explicit `--path`, then
a named/active local context, then the current directory. Explicit paths bypass
implicit active contexts, but explicitly named cloud contexts are refused.
Relative report destinations use the selected project; absolute destinations and
optional test-project/results input semantics are unchanged. Planning does not
write contexts or create implicit reports/directories, and all SDK/business
execution gates remain closed.

Public packaging stays at unpublished **1.0.0b1**. Report validation preserves
schema-1 historical producers and adds historical schema-2 **0.1.24**. Public
schema-2 **1.0.0b1** accepts exactly its old or new fixed `input.options` guidance,
including after a future package-version change; mixed or arbitrary guidance is
rejected. The actual pre-change public input-error report was inspected unchanged
through the new source and all three native installed CLIs.

| Context follow-up qualification | Result |
| --- | --- |
| Current CLI 2.91.0 / Python 3.14.7 / Windows x86 complete source and exact-installed suites | Each passed 865 tests / 2,389 subtests. |
| Minimum CLI 2.67.0 / Python 3.12.7 / Windows x64 complete source and exact-installed suites | Each passed 865 tests / 2,389 subtests. |
| Current CLI 2.91.0 / Python 3.14.7 / Windows x64 changed regression files, source and exact-installed | Each passed 72 tests / 209 subtests. These are focused follow-up runs, not a rerun of the earlier complete architecture suites. |
| `azdev test logicapp --series --discover --no-exitfirst --pytest-args -q` | Passed all 865 source tests on the isolated Python 3.12.12 development environment. |
| Separate native installed CLI processes | 24 commands per environment: selection/profile isolation, cloud refusal, report destinations/guards, JSON/table/query/nonzero behavior and genuine historical report inspection. |
| Native ownership probes after test-bootstrap removal | Stock CLI-preloaded psutil 6.1.0 and explicit dependency-first 7.1.1 both passed cross-architecture birth/listener/refusal/stop/held-handle checks in all three environments. |
| Exact wheel and dependency bytes | All 30 production files match source/wheel/three fresh installations. All 30 installed psutil files match independently hash-verified publisher wheels. |

Suites ran serially with production origins enforced. The context wheel's fresh
installs resolved dependencies from the already verified local publisher wheels;
the earlier architecture qualification established unrestricted ordinary online
installation. The current embedded MSI interpreters required the same test-only
import-path bootstrap described above; it was removed after their suites.
No production APIs, clocks, process observations or guards were patched.

Native x86 CLI qualification also reproduced a pre-existing first-context
creation issue: omitting `--port` supplies Knack's wrapped default integer,
rejected by the existing exact-integer validator. The native planning probes
created contexts with explicit `--port`; this reviewed planning delta does not
fix the separately tracked creation issue. Earlier native filesystem variability,
full Windows Python/minimum-x86 coverage, latest-head public AI/CI, effective
ownership and live-runtime/SDK qualification remain independent limitations.

### SDK follow-up qualification

The SDK follow-up was qualified independently of the historical results above.
Current Windows CLI 2.91.0 x86/x64 used Python 3.14.7; minimum CLI 2.67.0 x64
used Python 3.12.7. Source and exact-installed suites ran serially with production
module origins enforced. The development environment used Python 3.12.12,
CLI 2.91.0 and azdev 0.2.13.

| SDK follow-up check | Result |
| --- | --- |
| Current x86 exact-installed, current x64 source/exact-installed, minimum x64 source/exact-installed full suites | Five serial runs each passed 892 tests / 2,463 subtests. |
| Current x86 source full suite | 891 passed / 2,463 subtests passed; one unchanged native Azurite-shim fixture failed during teardown with a Windows executable cleanup access error. This full run is not green. |
| `azdev test logicapp --series --discover --no-exitfirst --pytest-args -q` | All 892 source tests passed in the isolated development environment. |
| Focused SDK, historical report, feedback and actual-parser regressions | 99 tests / 279 subtests passed. |
| Reviewed native-report validator parity | 2,737 shape/type/record mutations agreed after normalizing only the intended producer mappings. Production AST inventory accounts for every reviewed module and upstream adaptation. |
| Real synthetic SDK execution | Source API and each of three exact-installed native CLIs passed four SDK assertions. Each installed run reported five selected, four executed/passed and one skipped; these counts are not business coverage or SDK-call attestation. |
| Separate native CLI contracts | 46 processes covered omitted-port context creation, cloud refusal, source-only scaffolding/no clobber, selected-context planning, approval refusal, query/table, native/history inspection, genuine failed/empty/build-failure/timeout outcomes, retained-receipt refusal and deployment boundaries. |
| Native ownership after test-bootstrap removal | All six stock-first/dependency-first probes passed across the three environments: native PE/pointer width, cross-architecture discovery, CIM/birth identity, listener ownership, unknown/mismatched refusal and verified stop/held-handle exit checks. |
| Exact package/dependency bytes | All 32 production files match source, wheel and three fresh installations; all 30 installed psutil files match independently hash-verified publisher wheels. |
| `azdev style logicapp`, `azdev linter logicapp`, `azdev verify license` | Passed without broad exclusions or weakened scalar/ownership checks. |
| `python scripts\ci\service_name.py` | Passed with all 59 extension leaves loaded and the existing service registration. |
| `python scripts\ci\validate_external_source_urls.py --cached`, `python scripts\ci\test_index.py -q` | Passed; index test ran nine tests with two CI-only broad-network skips. |
| `azdev scan --confidence-level MEDIUM --directory-path src\logicapp --recursive --continue-on-failure` | No detected secrets, no custom exclusions. Generated binary test artifacts emitted UTF-8 warnings; their binary contents were not parsed. |
| `python -m pip check`, tracked privacy/local-link checks, `git diff --check` | Passed. |

The Python 3-only wheel SHA256 is
`7f4c60255cfea5411ca19e07358ac33fb36966a065770035ed22b5c6012028ac`.
Fresh installs resolved the unchanged Windows dependency ceiling from verified
local publisher wheels; no compiler, dependency suppression or shared installation
changes were used. Temporary test import bootstraps were removed before the
real CLI/native ownership probes.

Native SDK trials used approved synthetic source and a copied, isolated package
cache, explicit per-invocation acknowledgements and separately requested restore.
They exercised SDK 1.0.3, engine 1.165.50, MSTest 4.0.2 and .NET SDK 8.0.426.
Genuine saved 0.1.25/0.1.26 native reports and a pre-context public 1.0.0b1
foundation report were inspected without rewriting their inputs. No retained
process receipts remained after the completed trials; runtime/test colocation
was refused while an ordinary runtime DLL remained in the deployment package.

The x86 source teardown failure and its original evidence were retained rather
than replaced by repeated full runs. A later exact-path process inspection found
no remaining fixture process and only that completed fixture directory was
cleaned, without signalling a process. This does not establish the error's root
cause or universal native filesystem stability. No production guard, deadline or
test exclusion was relaxed.

These are local qualification results, not latest-head public CI or completed
public AI review. No live Azure changes, SDK binary redistribution, universal
platform/connector coverage, denied egress or production readiness is claimed.
Human safety review and the existing public contribution gates remain required.

## Reviewed native SDK testing follow-up

The separately reviewed source input is
`ea68b867939845e7d7492e4d261eb77ff0d41d3e` (historical 0.1.26), following
the reviewed 0.1.24 context input. It adds source-only `test create`, explicit
`test run`, sanitized native-report inspection, default scaffold metadata
inspection, deployment test/state exclusions and colocation refusal, and a
retained-process-receipt retry hold. The complete extension now has 59 leaves
(the original 38 plus 21 additions); the 13 core-owned GA leaves remain separate.
The omitted-port context-create fix normalizes only the CLI boundary; storage
and explicit port validation remain strict.

Public packaging remains unpublished **1.0.0b1**, Python >=3.10 and Azure CLI
>=2.67.0. The existing Windows psutil ceiling, service registry, portable GA
controls, Linux-native fixture isolation and process ownership guards are
retained. Native report validation is extracted into bounded helpers for
upstream style rules, preserving exact scalar checks and closed evidence.

Supported foundation producers retain schema-1 0.1.17-0.1.21/public 1.0.0b1
and schema-2 0.1.22-0.1.26/public 1.0.0b1. Native execution JSON explicitly
retains 0.1.25, 0.1.26 and public 1.0.0b1, including after later package-version
changes. The unpublished public schema-2 producer spans exact old/new
`input.options` and `report.invalid` row catalogs; mixed or arbitrary row text is
rejected. Public schema-1 remains legacy-only. Saved counts and approvals are
historical, unauthenticated evidence, never authority for another run.

The native contract pins SDK 1.0.3, engine 1.165.50, MSTest 4.0.2 and net8.0.
Per-invocation terms and project-trust acknowledgements remain necessary,
and restore is separately opt-in. Native code is trusted, not sandboxed;
counts do not attest useful workflow coverage or SDK invocation. SDK telemetry
is not proven disabled by CLI opt-out. The known typed top-level-output cast
failure is documented rather than hidden by changing workflow semantics.
Human safety review, live/connector/platform qualification, SDK terms and
effective CODEOWNERS eligibility remain independent requirements.

## Official review repairs after the SDK port

The eight findings from official review 5573475117 were reproduced and repaired
separately from the historical 0.1.26 input. These repairs do not change that
historical source, the preview version, dependency markers, service registration,
GA ownership or closed historical report catalogs.

Callback details are HTML-escaped without changing their protocol values.
Accepted loopback requests have an absolute read deadline, and shutdown closes
the current client. Real idle, incomplete and continuously trickled requests,
normal GET/POST bodies and whole-flow timeout cleanup are covered without a live
provider or browser. Known trigger evidence takes precedence over generic
action metadata. Trigger-history rechecks retain stable identity, fired status,
execution/revision metadata and content hashes, but ignore rotated signed URLs.

Deployment refuses unreadable/invalid existing `.funcignore` files and aliased
ZIP/manifest destinations before writing. Case-equivalent local settings are
always secret files. Test-directory pruning requires declared test intent;
ambiguous state/project markers and runtime/test colocation fail explicitly.
Renamed test projects and restored/generated test artifacts remain excluded
without blanket-excluding ordinary production DLLs.

| Review-repair qualification | Result |
| --- | --- |
| `azdev test logicapp --series --discover --no-exitfirst --pytest-args -q` | 909 source tests passed, two unsupported Windows symlink cases skipped. |
| Exact-installed minimum CLI 2.67.0 / Python 3.12.7 x64 full suite | 909 passed, two symlink cases skipped, 2,503 subtests passed; production origins enforced. |
| Exact-installed current CLI 2.91.0 / Python 3.14.7 x86 and x64 review/replay regressions | Each passed 109 tests / 324 subtests, with the same two symlink skips. Real NTFS hardlink/junction and loopback deadline cases ran. These are focused final-wheel runs, not full current-architecture suites. |
| Actual installed deployment CLI processes | 21 cases across the three environments passed: ordinary runtime assemblies, mixed-case settings, invalid exclusions, state/project colocation refusal, existing hardlink-output preservation and query/table behavior. |
| `azdev style logicapp`, `azdev linter logicapp` | Passed; no broad exclusions or weakened guards. |
| Final source/wheel/three fresh private installations | All 32 production files match; no SDK/cache/native binary payloads. The unchanged dependency markers resolved publisher wheels. |

Final wheel SHA256:
`7ee39fbc41925e55dd9505f7ce66c54f6a4eb149d43d3040612edbdad1f811be`.
Full suites ran serially. Temporary test import bootstraps were removed.
A preliminary current-x64 installed full run reproduced the unchanged native
Azurite-shim teardown `WinError 5` (906 passed, one failed, two skipped).
That result is retained, not presented as green or replaced by full-run retries.
A fresh exact-path inspection found no fixture process before only that completed
fixture directory was removed; no process was signalled or ownership guard changed.
The final full source/minimum-installed passes do not establish universal Windows
filesystem stability, a full current-architecture matrix, live OAuth/SDK coverage
or completed latest-head public CI/AI review.
