# Local runtime doctor

`az logicapp runtime doctor` is a **read-only, local-environment preflight**, not a
workflow business test. It explains detected prerequisites and uncertainty without
installing, starting, stopping, repairing, downloading, decrypting, or rewriting
anything. It does not change the active context.

**An otherwise responsive project normally exits `2`, not `0`: exact
tool/bundle compatibility remains a required unknown.** Unknown is neither a
detected failure nor a healthy certification. Preserve the findings before
interpreting the exit code.

```powershell
az logicapp runtime doctor --path .\orders --output json
az logicapp runtime doctor --path .\orders --port 7071 --output table
az logicapp runtime doctor --context orders-local --probe-timeout 2
```

With no `--path`, a named or active **local** context supplies the project path and
port. Without a context, the current directory and port 7071 are used. An explicit
path overrides the active context; explicit paths do not load the context store.
`--context` cannot be combined with `--path` or `--port`. Cloud contexts are refused.
An explicitly empty context is invalid, not an omitted selection; it cannot
silently fall back to an active context or bypass those target conflicts.
Cloud flags such as `--resource-group`, `--name`, and `--host-key` are unsupported.
There is no Azure account lookup, cloud diagnostic, log streaming, or telemetry.

## Findings and exit codes

The JSON report has `schemaVersion: "1.0"`, `scope`, `readOnly`, `target`,
`environmentHealth`, `businessBehavior: "not-tested"`, `coverage`, `summary`, `exitCode`, and
`findings`. Each finding has a stable `check` identifier, `status`, `required`,
`reason`, `recommendation`, and a bounded, curated `evidence` object.
`pass`, `warn`, `fail`, `unknown`, and `skipped` are distinct. `skipped` never means
that a probe succeeded. Workflow check identifiers use sorted inventory indexes;
their evidence identifies the workflow name. Coverage records unevaluated phases
when a target is invalid, and explicitly excludes cloud/business testing.
Table findings include selected paths/versions, ports and missing reference names,
as well as an explicit skipped business-behavior row.

| Exit | Meaning |
| --- | --- |
| 0 | No required failures or unknown checks; not a guarantee of business correctness. |
| 1 | At least one required failure, including invalid target/configuration or absent required tool/storage listener. |
| 2 | No required failure, but at least one required unknown; also optional warnings, failures or unknowns with `--strict`. |

JSON/table formatting and `--query` run normally **before** a diagnostic nonzero
exit, so CI can preserve stdout. Parse/CLI argument errors retain Azure CLI's normal
error behavior. `--strict` does not turn an intentionally skipped stopped-host
probe into failure. By default a stopped host is acceptable for offline preflight;
unreachable **configured local storage** remains a required failure.

## What is checked

- Tool paths selected by runtime launch, not an arbitrary installed version:
  PATH-first Functions discovery and the shared runtime child environment for
  Node/.NET; Azurite's separately selected launcher and its own child Node path.
  Version-only child processes run in the executable directory, never project code.
  `.ps1`-only launchers and failed/unrecognized version probes remain unknown.
  No npm installer, audit, update, or registry request runs. The .NET SDK is
  reported as optional: SDK compilation is not performed by this command.
- `host.json`, `local.settings.json`, direct child workflow files, and optional
  `connections.json`/`parameters.json`. JSON object shape, host schema, worker
  setting, string-valued unencrypted settings, project parameter entries, and
  existing basic workflow structure checks are evaluated. The definition must
  include an actions object; missing/null actions fail, while an explicit empty
  object is valid. This is not full schema
  validation, connector validation, expression evaluation, or business testing.
  Files above 4 MiB, content deeper than 128 levels, and encrypted settings remain
  unknown, without decryption. Duplicate members, nonstandard JSON constants and
  overflowing numbers fail.
- Missing literal `@appsetting('NAME')` and `@parameters('NAME')` references are
  reported **by name only**. Inherited app-setting names, workflow parameter
  defaults, and project parameter assignments are considered. Arbitrary ordinary text, `@@` escapes, composite,
  interpolated, escaped-name, and dynamic expressions are not interpreted as
  definite missing references; unresolved expression forms and case-variant
  reference names remain unknown rather than falsely missing.
- The Workflows bundle configuration and the user's Functions cache. Only
  `[N.*, M.0.0)` ranges are interpreted. A matching cache entry must contain
  `bin/extensions.json`. Cache presence is **not** bundle load evidence. Missing
  cache or bundle configuration overrides remain unknown and no download occurs.
- Configured storage ports on literal loopback only. `UseDevelopmentStorage=true`
  uses 10000/10001/10002. Custom connection strings must explicitly declare all
  Blob/Queue/Table endpoints with HTTP and `localhost`, `127.0.0.1`, or `::1`.
  Endpoints are probed at their loopback origin, without account paths, keys,
  authentication, query strings, environment proxies, redirects, or DNS lookups.
  Mixed local/remote, proxy overrides, HTTPS, identity-based, malformed, and
  implicit cloud endpoints remain unknown and **no storage endpoint is contacted**.
  An inherited storage value is considered when no project value exists. Different
  project/environment storage values remain unknown, with no endpoint probes,
  rather than asserting which value a particular Core Tools version will prefer.
  Azurite service banners are evidence of service identity, not authentication,
  data-plane correctness, or CLI ownership. An occupied port proves neither
  Azurite nor Functions.
- The selected loopback host port and `/admin/host/status`. A `Running` observation
  requires HTTP 200 within the probe budget; error-response bodies do not certify
  a running host. Duplicate/nonfinite/overflowing JSON receipts establish no host
  state, including conflicting duplicate `state` members. That observation
  only passes the optional host check when the saved PID/creation identity matches
  the selected project and that verified process (or verified recorded child)
  owns a listener on the port. A recycled/stale/unknown PID remains unowned.
  No process is ever labeled safe to terminate. Storage ownership records are
  independent identity evidence, not proof that a port belongs to that process.

`--probe-timeout` accepts 1-10 seconds (default 2) per socket/HTTP/version probe.
HTTP probes share one monotonic budget across connection, headers, body reads
and final JSON inspection. Raw receives use the remaining budget before HTTP
buffering, so trickled headers/bodies cannot repeatedly renew an idle timeout.
An expired body observation retains an already observed HTTP status but reports
no host state. This is not a whole-command deadline or permission to repair.
There is no retry/poll loop. HTTP status, recognized host-state enums, recognized
Azurite identity, selected tool paths/versions, rule identifiers, and missing
reference names are the only probe/configuration evidence returned. Configuration
values, connection strings, raw subprocess output, server bodies, exception
messages/stack traces, and complete process/environment records are never returned.

## Compatibility is deliberately conservative

[Logic Apps Standard prerequisites](https://learn.microsoft.com/azure/logic-apps/create-standard-workflows-visual-studio-code)
identify Core Tools, Node.js, and .NET and delegate correct versions to the VS Code
extension. [Functions local tooling documentation](https://learn.microsoft.com/azure/azure-functions/functions-run-local)
distinguishes GA Core Tools v4 from preview CLI v5. Doctor checks the Core Tools
major, but neither an installed version nor an available bundle certifies an exact
Core Tools/Node/.NET/Workflows-bundle pairing. The pairing check therefore remains
**unknown**, even when configuration and optional live host observations pass;
this version normally exits 2 on a project with no detected failure.
Do not interpret this as a broken project, or treat unknown as healthy.

In particular, one successful local launch with Core Tools 4.15.2 is not evidence
of a global 4.15.2 minimum. Doctor does not invent one, download metadata, or run a
host to certify compatibility. Separately starting and observing a local host can
add operational evidence, but does not establish workflow business correctness.
