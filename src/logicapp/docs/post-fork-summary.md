# Extension improvements and remaining work

The upstream preview **1.0.0b1** contains the complete original extension and
the reviewed improvements through the historical **0.1.26** SDK-testing baseline.
It contributes **59 leaf commands**, 21 more than the original 38-command
extension, while preserving the 13 core-owned GA app, settings and ZIP deployment
commands. See [contribution provenance](contribution.md) for packaging,
attribution and qualification boundaries.

## Included improvements

Workflow discovery provides bounded inventory, authored-file show/export and
portable import. `workflow set` explicitly replaces a complete document; it
does not merge partial definitions or change Stateful/Stateless kind.
Replacement and standalone runtime validation share a completed-response gate.
Mutation requires acknowledgement of the nontransactional VFS boundary,
confirmation and exact strong-ETag rechecks. Compensation never overwrites a
newer or unowned revision.

Saved contexts support read-only inspection and guarded update/delete.
Storage and active selection follow `AZURE_CONFIG_DIR`; custom profiles do not
inherit another profile's targets. Explicit cloud contexts cannot silently
select a local authored project. Local lifecycle commands honor saved ports.
Omitted context-create ports normalize to 7071 through the real CLI parser
without relaxing strict explicit-port or stored-context validation.

`runtime doctor` performs bounded, conservative local readiness inspection,
not installation or execution. Runtime cleanup retains PID/birth-identity
ownership guards, distinguishes exited Windows objects from live processes,
and excludes only verified pre-existing stale-parent subtrees. An explicit
stop retry recovers a cleanup-pending receipt only after every recorded process
and consumer has exited and the port is idle. Publication and removal recheck
the exact receipt under a shared lock; ambiguity retains state.

Stateful execution has bounded wait, guarded cancellation, directly selected
`trigger history resubmit`, and genuine one-action `run resubmit --action`.
Action resubmission requires a completed source run and literal runtime
eligibility, rechecks stable selected execution evidence and never substitutes
trigger replay or enables a server feature. Acknowledgement is not completion,
service identities are never fabricated, and uncertain mutations are not retried.
Transport bounds raw reads and deadlines, rejects nonempty mutation receipts,
and preserves selected bearer authentication against netrc substitution without
disabling cloud proxies or CA bundles.

`connection managed create` separates connection `--name` from consuming
`--logic-app-name`. The deprecated legacy mode retains its original naming.
OAuth failure may retain ARM resources. Managed deletion requires the selected
site's principal and tenant, complete unambiguous policy inventory, and fresh
post-unlink ownership evidence. Missing/malformed continuations, duplicate policy
names, cross-tenant identities or unsafe resource coordinates cannot authorize
destructive cleanup. File compensation requires the acknowledged write revision,
not merely identical content.

The read-only testing foundation inspects explicit files and optional XML
metadata without evaluating MSBuild or running tests. Successful default
planning exits 0; `--strict` returns 4 for blocked execution gates. Both retain
`notExecuted`, immutable SDK gates and zero executed business tests. Closed
schema-2 reports record this policy. Supported schema-1 reports retain their
historical outcomes; supported producer versions remain readable after package
version changes. See [testing contracts](workflow-testing-foundation.md).

The separate native workflow adds source-only `test create` and explicitly
trusted `test run`. Scaffolds remain ignored/inconclusive until authored.
Every run requires SDK-terms and project-trust acknowledgements; restore is
separately opt-in. Locked SDK 1.0.3/engine 1.165.50/MSTest 4.0.2 and .NET 8
selection, bounded consistent TRX counts, ownership-checked cleanup and a
retained-process-receipt retry hold do not provide a sandbox or coverage
attestation. `results show` inspects original sanitized native JSON without
rerunning; raw TRX remains sensitive and local. Dedicated native test/state
directories and raw TRX are deployment-excluded; runtime/test colocation is
refused. Arbitrary trusted code can still write outside those boundaries.

## Qualification boundaries

Historical development evidence is not an upstream CI result or universal
platform qualification. Sequential cached Windows runtime trials exercised
selected execution and lifecycle paths; cloud transport, ownership and protocol
regressions also use synthetic fixtures. They do not establish live Azure,
all-platform, all-runtime or Python-version-matrix coverage.

Earlier multi-use-case trials established workflow processing only: Response
actions were skipped, so actual callback HTTP responses remain unqualified.
Workflow show encountered a host-key prerequisite; export was not exercised in
those trials. Doctor deliberately preserves unknowns. Nested static validation,
agent bootstrap guidance and callback-response improvements remain follow-ups,
not delivered features.

SDK adoption, restore/build/execution and terms remain outside the read-only
foundation; the separate native command requires explicit invocation approvals.
No SDK binary redistribution, assertion rewriting, automatic rerun, denied-egress
or complete platform/connector coverage is claimed. The SDK's typed top-level
output cast failure remains documented; workflow semantics are not rewritten
to hide it.
Contexts are shortcuts, not subscription/tenant bindings or effective-permission
proof. VFS, settings and ARM operations are not transactions. Public AI review,
maintainer approval, upstream CI, supported Python compatibility and effective
CODEOWNERS eligibility remain separate contribution gates.
