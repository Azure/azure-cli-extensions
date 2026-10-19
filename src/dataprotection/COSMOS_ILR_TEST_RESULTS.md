# Cosmos DB item-level recovery: implementation and test evidence

## Verdict

**Offline implementation and native-command transport checks pass. Live acceptance
is pending explicit test-resource/cost approval. Keep the PR draft.**

Scope is Azure Cosmos DB for NoSQL **database/container** recovery, not individual
documents or Cosmos-native point-in-time recovery. No new public flags, generated
models, API upgrade, selective backup, Cosmos CRR/CSR, rename or overwrite support
is introduced.

## Environment and provenance

- Date: 2026-10-19.
- Upstream baseline: `ebea488892f255360e25bc481fc3f01fd5990334`.
- Extension: `dataprotection` 1.14.0; same-region restore API remains `2026-06-01`.
- Executed locally on Windows, CPython 3.13.13 and Azure CLI/core 2.86.0.
- Source discovery was verified against this checkout. The built wheel was also
  installed in a separate private extension directory, with development-source
  discovery disabled and its import path/version independently verified.
- No global CLI/extension installation, cached Azure account, token, live Azure
  HTTP, role assignment, source-data change or resource provisioning was used for
  the offline feature tests.

## Changed boundaries

| Area | Behavior |
| --- | --- |
| `manual/cosmosdb.py` | Cosmos-only selector/configuration/target/identity validation and schema-aware permission-input handling |
| Manifest and criteria dispatch | Enable Cosmos ILR with one `GenericRestoreDatasourceCriteria`, one object-valued resource-list selector and the exact ordered identifiers |
| Existing configuration command | Reuse `--resource-identifiers`; preserve case, spaces, Unicode and literal punctuation; reject 0/51 entries, malformed names, exact duplicates and exact database/child overlaps |
| Existing item initializer | Revalidate edited JSON; require VaultStore recovery-point construction and an alternate account-shaped target; reject BI lookup inputs and foreign Blob criteria locally |
| Full initializer | Preserve valid `RestoreTargetInfo` without criteria; reject supplied Cosmos selection rather than silently ignoring it |
| Cosmos restore identity | Preserve omission and UAMI-alone inference; reject explicit false without UAMI and true with UAMI; edited request identities must already contain a valid explicit Boolean |
| Cosmos restore permission preparation | Reconcile the request-selected UAMI, match attached ARM IDs case-insensitively, reject ambiguous/missing principals and mismatches before role writes; accept known client/wire aliases without mutating caller maps |
| Compatibility | Other workloads retain shared identity/conversion behavior; populated PostgreSQL credentials/sets, Blob/ADLS criteria, AKS configuration and eSAN multi-selector semantics are not redefined |

The identity restrictions are intentionally Cosmos-scoped and also apply to
Cosmos full initialization. An identity-omitted request retains the existing
permission helper's flag/SAMI selection; that helper does **not** insert identity
details into the request or establish the service's default identity.

## Executed results

| Layer | Result | Evidence boundary |
| --- | --- | --- |
| New offline contract/permission/regression tests | **819 passed** | Parameterized helpers and actual permission boundaries; forbidden unmocked IO |
| New public-command transport tests | **21 passed, 131 subtests passed** | Real public parser → manual command → AAZ → serialized `HttpRequest`; synthetic responses, not Azure acceptance |
| Same two suites from the privately installed wheel | **840 passed, 131 subtests passed** | Packaged code imported instead of source |
| Existing completed regression modules | **85 passed, 24 existing skips** | Policy, configurations, Cosmos full/backup initialization, AKS enable-backup, eSAN, job, RP, Resource Guard and restorable-time-range; live-only tests excluded |
| Untouched-upstream comparison | **11 existing modules completed with matching outcomes** | Separate detached baseline, same libraries and enforced playback-only setup |
| Four other existing recorded modules | **Incomplete on both revisions** | Per-module 25-second deadline on both feature and untouched baseline; not passes |
| Repository index checks | **7 passed, 2 existing CI-only skips** | `python scripts/ci/test_index.py -q`; no index change |
| Wheel build | **Passed** | Local setup-based wheel build; standard isolated `build` frontend unavailable in this runtime |
| Syntax/help/whitespace | **Passed** | Touched Python parses with Python 3.10 grammar; all 35 manual help YAML entries parse; `git diff --check` |
| Standard `azdev style dataprotection` | **Blocked** | Development environment lacks `azure_cli_diff_tool`/lint dependencies; package downloads fail TLS handshake; not reported green |
| Linux/macOS and additional Python/CLI CI versions | **Not executed** | Remain CI gates |
| Live native backup/restore and exact-data verification | **Not executed** | Approved subscription/targets/roles/cost scope unavailable; no service completion claim |

The four incomplete recorded modules are
`test_dataprotection_backup_instance_create_and_delete`,
`test_dataprotection_backup_instance_operations`,
`test_dataprotection_backup_instance_restore` and
`test_dataprotection_backup_vault`. Early replay attempts also exposed API-version
cassette mismatches. Recordings and assertions were not rewritten to conceal
these failures, and no fallback to live requests was allowed. This is **not** a
claim that the complete pre-existing suite is green.

### Exact commands exercised by the native harness

- `az dataprotection backup-instance initialize-restoreconfig`.
- `az dataprotection backup-instance restore initialize-for-item-recovery`.
- `az dataprotection backup-instance restore initialize-for-data-recovery`.
- `az dataprotection backup-instance update-msi-permissions --operation Restore`.
- `az dataprotection backup-instance validate-for-restore`.
- `az dataprotection backup-instance restore trigger`.
- Existing restore-as-files construction, name/identity aliases and public help.

Configuration/request arguments are exercised inline and through UTF-8 `@file`
input, using snake_case client objects and supported known camelCase aliases.
Expected bodies are independently authored, not computed with the production
converter. Validation sends exactly one `restoreRequestObject` envelope to
`/validateRestore`; trigger sends the raw request to `/restore`. Both assert
API `2026-06-01`, canonical discriminators, plural keys, `resourceID`, matching
account URI and absence of unnecessary Cosmos auth/set objects. Both 202/no-wait
and synchronous 200 paths are covered without mocking request construction.

The matrix includes 1/50/51 selectors, all 65 Unicode `Cc` controls in both name
segments, database/container/mixed/case-distinct selections, malformed/mutated
configs, explicit false/empty foreign arguments, identity aliases/mismatches,
declined confirmation, inherited-role idempotence and exact selected principal/
scope. Successful local construction and local rejection assert zero credential
discovery and zero HTTP sends.

Existing CRR wrappers/API `2025-07-01` are tested using PostgreSQL Flexible Server
restore-as-files with a coherent secondary-region target, **not Cosmos CRR**.
Resource Guard full-operation URI, auxiliary-tenant forwarding and no-wait
behavior are retained. Bearer-policy-generated authorization headers are outside
the mocked send boundary and are not claimed as verified here.

### Reproduce feature tests

In the repository's configured Azure CLI development/test environment:

```text
python -m pytest -q src/dataprotection/azext_dataprotection/tests/latest/test_dataprotection_cosmosdb_restore.py src/dataprotection/azext_dataprotection/tests/latest/test_dataprotection_cosmosdb_commands.py
python scripts/ci/test_index.py -q
```

The new suites install their own fail-closed network/token mocks; no Azure login
is needed. Broader recorded regression runs additionally used an external,
uncommitted runner to force VCR `record_mode=none`, block sockets and avoid
recording/credential fallback. The legacy SDK's live-only decorator checks the
truthiness of its environment string: **unset** `AZURE_TEST_RUN_LIVE` rather than
assuming a literal `False` string excludes live-only tests.

Local XML/log bundles and the baseline comparison remain private outside the
repository. They contain no credentials and are not a substitute for CI results.
The local `pkginfo` 1.8.2 reader does not expose the version from modern
Metadata-Version 2.4; wheel discovery and version 1.14.0 were checked separately
with `importlib.metadata`. No product metadata/parser workaround was introduced.

## Remaining live acceptance gate

Use separately approved test resources, a committed VaultStore recovery point,
and a different existing empty compatible NoSQL target for each restore. Do not
reuse populated PowerShell targets, change source data, attach identities, alter
retention/network/vault safeguards, or delete resources without separate approval.

| Case | Selection / identity | Expected baseline DB/container/document counts |
| --- | --- | --- |
| Full baseline | No ILR config; SAMI | 3 / 7 / 14 |
| Single container | `db1/cont1`; SAMI | 1 / 1 / 2 |
| Database | `db2`; SAMI | 1 / 2 / 4 |
| Mixed | `db1/col1`, `db1/col2`, `db2`; SAMI | 2 / 4 / 8 |
| Sibling containers | `db1/col1`, `db1/col2`; SAMI | 1 / 2 / 4 |
| Multiple databases | `db1`, `db2`; SAMI | 2 / 6 / 12 |
| Selected attached UAMI | `db1/cont1`; explicit UAMI | 1 / 1 / 2 |

These are **planned expectations**, not executed CLI results. Persist a durable
submission intent before each trigger; submit once; save and reconcile the exact
returned job; wait for terminal `Completed`; then independently verify the frozen
RP-projected inventory, partition keys, document values, nested content/array
order, excluded siblings/databases, post-backup exclusions and unchanged source.
Do not start another case while an earlier outcome is ambiguous.

Validation-only acceptance is not restore completion or proof of selector
membership. Known reference service-validation gaps remain separate from local
syntax checks. There is no live certification here of the 50-selector boundary,
punctuation/mixed-case availability, other Cosmos APIs or other regions. Live
accounts, continuous backup and retained vault data may remain billable; cleanup
requires a separately approved lifecycle.