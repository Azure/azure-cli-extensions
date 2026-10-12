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
Subsequent staging features and safety repairs preserve its original 38 leaves
and add 17 leaves, for 55 total. Upstream packaging starts at preview `1.0.0b1`.

The stock-CLI additivity control is generated, not copied from a private
development machine. Each help control runs `python -m azure.cli ... --help`
using the test interpreter's installed CLI with empty temporary configuration,
extension and system-extension directories. Dynamic extension installation,
version checks and telemetry are disabled. This keeps the reference matched
to the CLI under test without requiring live Azure or a frozen help transcript.
Independent assertions pin the 13 existing GA leaves to the core App Service
loader, reject command overrides and preserve all 55 extension leaves.

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

## Local upstream qualification

The migrated preview was exercised on Windows with Python 3.12.12, Azure CLI
2.91.0, azdev 0.2.13 and Node.js 22.18.0. This is not a completed Python/platform
matrix or a claim about live Azure.

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
