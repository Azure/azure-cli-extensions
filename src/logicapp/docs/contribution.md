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
preserve the original extension and add 19 leaves, for 57 total. Upstream
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
loader, reject command overrides and preserve all 57 extension leaves.

The extension-local guides distinguish historical staging evidence from release
qualification. Historical Windows loopback/runtime exercises do not establish
current upstream CI, live Azure, Linux/macOS, every Python version, universal
proxy behavior or repeatable native shutdown/timing reliability. Process cleanup
continues to require PID and original birth identity; unresolved children retain
non-signaling cleanup/storage guards.

Workflow test commands remain a read-only foundation. All business tests are
`notExecuted` with zero executed counts. SDK licensing, use/data/update terms,
restore/build/discovery/execution, platform/network isolation and native report
qualification remain unresolved. No SDK DLL, installation, EULA acceptance or
business-test runner is included.

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
The Linux/Python matrix and latest-head public review still require successful
upstream evidence.

Latest-head public AI review, current upstream CI/maintainer approval, supported
Python compatibility and effective CODEOWNERS eligibility remain independent
gates. Historical cached-runtime evidence does not close them. The contribution
stays draft while they are unresolved; no live Azure or SDK execution is implied.
