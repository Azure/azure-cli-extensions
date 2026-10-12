# Stateful workflow execution controls

Version **0.1.15** adds `az logicapp run wait/cancel/resubmit`. Existing
`run start/list/show` and action inspection retain their return contracts.
These controls do not author workflows, change shared configuration, or
automatically retry, repair, resume or orchestrate recovery.

## Targets and support

| Target/model | Wait | Cancel | Resubmit |
| --- | --- | --- | --- |
| Running local Standard Stateful host | Supported; owned Windows host verified | Supported; observed `Cancelled` verified | Supported; verified history association and distinct new execution verified |
| Deployed Standard Stateful `Microsoft.Web/sites` | Documented API; isolated ARM transport fixtures verified, no live Azure validation | Same | Same |
| Stateless, including debug run history | Rejected | Rejected before POST | Rejected before POST |
| Consumption, slots, hybrid, offline project path | Not exposed by these commands | Not exposed | Not exposed |

Use `--local --port 7071`, deployed `-g my-rg -n my-app`, or `--context dev`.
With no explicit target the existing active context is used. Target combinations
are validated exactly as for existing run commands: a context owns its port;
local/cloud flags cannot be mixed. `--host-key` applies only to a local target
and travels in `x-functions-key`, not the URL. No new subscription/tenant/slot
binding or third `--path` target is introduced.

The new transport uses the selected Azure CLI profile, cloud and subscription
for ARM authentication, acquiring a token from that profile for each request so
its credential cache can refresh during long observations. Authentication failure
stops observation; no failed request or mutation is replayed to refresh a token.
Credential acquisition failure before a cancellation/resubmission POST reports
`readFailed`, a null `action`, and `requestAcknowledged: false`: no mutation was
sent. A later credential failure while observing an acknowledged cancellation
keeps `cancelRequested` and its acknowledgement, with `observationFailed`.
Transport/receipt failures after a send begins remain uncertain; they are not
reclassified as a known unsent request.
Overall deadline expiry at a proven pre-send boundary (including credential
acquisition and transport setup) likewise clears the attempted action and reports
that no mutation was sent. Deadline expiry after HTTP invocation begins remains
uncertain. Pre-send expiry on a later observation never clears an acknowledged
cancellation.
It uses the documented `2024-11-01` Standard runtime
API version, without changing other commands' transport/version. It bounds
connect/read requests to five seconds or the remaining deadline, whichever is
shorter; reads check the monotonic deadline while consuming a size-limited
response. Request-scoped HTTP/HTTPS connection pools budget raw receives before
status/header/body buffering, including proxy CONNECT. Other Requests sessions
and the other runtime commands' transports are not changed. OS DNS resolution and cloud identity/token
acquisition are outside Requests' connect/read timeouts; the command rechecks
its monotonic deadline after those steps, but does not claim it can forcibly
interrupt them. Local requests ignore environment
HTTP proxies. TLS verification remains enabled for cloud requests. There are
no HTTP retries or redirects; service URLs are never navigated.
Specialized proxy pools are preserved rather than replaced with direct
connections. Non-HTTP proxy negotiation (for example, optional SOCKS transports)
is not qualified by these HTTP/HTTPS/CONNECT fixtures and is not claimed to be
forcibly deadline-interruptible; the budget is rechecked after socket setup.

Requests explicitly advertise `Accept-Encoding: identity`. Responses with other
content encodings are rejected before reading or decoding the body: decoded
streaming can otherwise hide wire traffic from deadline checks. Such a response
is a sanitized `invalidResponse`, not a successful acknowledgement. After a
mutation POST, the remote outcome can still be uncertain; the command never
retries that POST to recover an unreadable receipt.

## Invoke, then wait

```powershell
$started = az logicapp run start --local --workflow hello --trigger manual --payload-file .\payload.json | ConvertFrom-Json
if ($started.runId) {
    az logicapp run wait --local --workflow hello --run-id $started.runId --timeout 60 --interval 2
}
```

Only wait when invocation actually returned a run identity. Start can return
`AcceptedNewRunIdUnknown`; neither a missing ID nor an accepted trigger request
proves that a new run was indexed or completed. This increment deliberately
does not add `--wait` to start or change its output. No callback URL command is
needed for this verified management-trigger invocation path, so signed callback
retrieval is not added incidentally. It remains a separately scoped capability.

`--timeout` is a whole number from 1 to 86400 seconds (default 300);
`--interval` is from 1 to 300 seconds (default 5), no greater than timeout.
The deadline includes workflow metadata and subsequent observations.
`Running`, `Waiting`, `Paused` and `Suspended` remain observable until terminal
or timeout. Terminal states are `Succeeded`, `Failed`, `Cancelled`, `TimedOut`,
`Aborted`, `Faulted`, `Skipped` and `Ignored`, normalized case-insensitively.
Missing/unknown statuses, including `NotSpecified`, fail promptly rather than
being classified as success or polled forever.

A missing run fails immediately; there is no not-yet-indexed grace period.
Authorization, provider, malformed-response and request-timeout failures are
distinct machine-readable error kinds. A wait timeout **never cancels a run**.
Workflow `TimedOut` is a terminal workflow result, not the CLI's `waitTimedOut`.
Request and command budgets are rechecked at response EOF and after decoding,
including empty/late receipts. A receipt arriving after its budget is not reported
as an acknowledgement, and mutation POSTs are never retried automatically.

## Cancellation

```powershell
az logicapp run cancel --local --workflow hello --run-id RUN_ID --yes
az logicapp run cancel -g my-rg -n my-app --workflow hello --run-id RUN_ID --yes --wait --timeout 60 --interval 2
```

Confirmation warns about asynchronous cancellation and downstream effects.
After confirmation, the workflow kind and run status are checked again.
An already-terminal run is an `alreadyTerminal` / `unchanged` no-op, without
POST. A cancellation POST acknowledgement sets `requestAcknowledged: true`,
but is not proof of `Cancelled`.

Without `--wait`, one bounded readback reports `cancelled`, `pending`,
`terminalNotCancelled`, or an explicit observation failure. A pending receipt
exits zero because the request was acknowledged, **not** because cancellation
was completed. With `--wait`, only observed `Cancelled` meets the requested
terminal outcome. A competing completion such as `Succeeded` exits 4.

Cancellation does not undo side effects, guarantee in-flight actions stop, purge
history, disable a trigger, or change workflow configuration. A request with an
uncertain outcome is never retried automatically. Preflight and the post-confirmation
submission/readback each have a 60-second deadline, excluding human confirmation.
An optional wait begins after acknowledgement and uses `--timeout`.

## Resubmission

```powershell
$result = az logicapp run resubmit --context dev --workflow hello --run-id SOURCE_RUN_ID --yes | ConvertFrom-Json
if ($result.newRunId) {
    az logicapp run wait --context dev --workflow hello --run-id $result.newRunId --timeout 60 --interval 2
}
```

Resubmission creates a **new execution** and can repeat external side effects,
including when the original run is still active. It is not resume, rollback,
retry-an-action, or exactly-once recovery. It does not change the original run.
No historical definition or configuration is restored by this command; do not
assume a resubmission reproduces an earlier deployment's behavior.

The Standard API resubmits a **trigger history**, not a workflow run directly.
The command reads the selected run's trigger, examines at most ten pages of
100 retained histories, and selects only a fired history whose run reference
matches the selected workflow/run. It never assumes that a run ID is a history
ID. Both local relative run references and deployed site-qualified management
resource IDs are recognized. A deployed reference must match the selected site
as well as the exact workflow/run; a matching run name does not override a
conflicting resource ID. References are compared, never followed as URLs.
Execution responses reject duplicate JSON fields and nonfinite/overflowing
numbers. Body reads use bounded 64-KiB chunks; raw receive budgeting still bounds
buffer filling, and the 1-MiB payload limit and EOF/decode deadline checks remain.
Use optional `--trigger-history-id HISTORY_ID` to verify a known retained
history without the bounded search. Missing/expired history, an unsupported
page, ambiguous association, or a changed trigger/history fails before POST.
The association and Stateful kind are checked again after confirmation.

A valid 202 receipt reports `accepted`. `newRunId` is supplied only from a
validated, distinct `x-ms-workflow-run-id`; if it is absent, the outcome is
`acceptedNewRunIdUnknown` with a null ID. Location headers are neither followed
nor printed, and a new identity is never guessed by selecting the latest run.
Neither outcome proves a new execution completed. Preflight and post-confirmation
submission each have a 60-second deadline; no non-idempotent POST is retried.

## Agent-facing reports and exit codes

JSON is the normal command result, including on report exits; `--query`,
`--output table` and `--output tsv` still use Azure CLI formatting.

| Exit | Meaning |
| --- | --- |
| 0 | Wait observed `Succeeded`; cancel observed `Cancelled`, acknowledged pending, or an already-terminal no-op; resubmit acknowledged |
| 1 | Read/protocol/authorization/provider/unknown-status error, invalid model/options, or unverified mutation outcome |
| 2 | CLI observation or request deadline expired, never an implicit cancellation |
| 4 | Observed terminal run did not meet the requested outcome (`Succeeded` for wait; `Cancelled` after cancellation) |

Argument/target/confirmation failures use existing Azure CLI error formatting.
Operation reports use `schemaVersion: "1.0"`, `workflow`, `workflowKind`, `runId`,
`operation`, `action`, `status`, `terminal`, `outcome`, `requestAcknowledged`,
`runCorrelationId`, `requestCorrelationId`, `exitCode` and `error`.
`error` is null or a sanitized `{kind, message}` object, never raw provider prose.
Correlation values are exposed only when they have a service UUID shape;
unreported/unrecognized values are null. Resubmit adds `sourceRunId`,
`triggerName`, `triggerHistoryId`, `newRunId` and `newRunStatus` (null: not observed).
Its `runId`, `status` and run correlation describe the **source**, not the new run.

Reports omit authored inputs/outputs, workflow/action error payloads, signed
content/callback URLs and arbitrary response headers. Table output summarizes
identity, status, outcome, new identity, error kind and exit code. A nonzero
report exit happens only after normal formatting; do not infer success from
JSON availability, `terminal: true`, or a POST acknowledgement. No prose field
authorizes an agent to retry a mutation.

## Evidence and limits

First-party contracts:

- [Standard App Service runtime specification](https://github.com/Azure/azure-rest-api-specs/blob/main/specification/web/resource-manager/Microsoft.Web/AppService/stable/2024-11-01/WebApps.json):
  `WorkflowRuns_Get`, `WorkflowRuns_Cancel`, `WorkflowTriggerHistories_List/Get/Resubmit`.
  Cancel documents HTTP 200; resubmit documents HTTP 202. The implementation
  also handles empty asynchronous 202/204 cancellation acknowledgements truthfully.
- [Standard run get example](https://github.com/Azure/azure-rest-api-specs/blob/main/specification/web/resource-manager/Microsoft.Web/AppService/stable/2024-11-01/examples/WorkflowRuns_Get.json)
  and [resubmit example](https://github.com/Azure/azure-rest-api-specs/blob/main/specification/web/resource-manager/Microsoft.Web/AppService/stable/2024-11-01/examples/WorkflowTriggerHistories_Resubmit.json).
- [Monitor and rerun workflows](https://learn.microsoft.com/azure/logic-apps/monitor-logic-apps):
  Standard reruns support Stateful workflows, not Stateless workflows.

Windows Functions Core Tools 4.15.2 with the observed workflow bundle was used
on an owned temporary project and private random-port storage emulator.
This is observed compatibility, **not** a universal minimum-version assertion.
No live Azure operation, Linux/macOS runtime or hybrid deployment was validated.
