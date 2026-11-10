# Investigate a failed workflow run

The existing `run show` and `run action list/show/show-content` commands can
identify a failed action and inspect its recorded reason. No new diagnosis
command, workflow engine, logging service or testing SDK is required. These
commands inspect a **normal runtime execution**, not a mocked business-test run.

## Start with metadata

Use the same target, workflow and exact run ID throughout. The following
PowerShell commands inspect an existing run on a local host; replace the values
with your own. Alternatively use `$target = @("--context", "my-local")`, or a
deployed target such as `@("--resource-group", "my-rg", "--name", "my-app")`.
Do not combine saved-context and explicit target flags.

```powershell
$target = @("--local", "--port", "7071")
$workflow = "process-order"
$runId = "YOUR_RUN_ID"

az logicapp run show @target --workflow $workflow --run-id $runId --output json

az logicapp run action list @target --workflow $workflow --run-id $runId --output json `
  --query "value[].{action:action,status:status,code:code,error:error.message}"

az logicapp run action list @target --workflow $workflow --run-id $runId --output json `
  --query "value[?status=='Failed'].{action:action,status:status,code:code,error:error.message}"
```

The first action listing provides context; the second highlights failures.
`Skipped` can mean a dependency did not meet its `runAfter` condition, not that
the skipped action itself failed. A failed scope/loop can summarize a failure
inside it rather than identify the leaf cause. Follow `nextContinuationToken`
with `--next-token` when paging; a query filters only the returned page.
An empty failed-action projection is not proof of success.

Select the returned action name, not a guessed name:

```powershell
$action = "Convert_amount"
az logicapp run action show @target --workflow $workflow --run-id $runId --action $action --output json
```

Inspect `status`, `code`, `error.code`, `error.message`, and any `retryHistory`.
The action's `code` and the provider's `error.code` can differ. Errors need not
have recorded outputs: an invalid input expression can fail before a response
exists. Missing outputs are unavailable evidence, not a successful action.

**Protect the evidence.** Content-link URIs are redacted by default, but provider
error text, retry details and recorded payloads are not guaranteed secret-free.
An error can echo input data or a credential-bearing URL. Avoid
`--show-content-urls`, `--debug`, automatic payload collection and unchecked
sharing of command output. Review and redact even metadata before publishing it.

## Read recorded content only when necessary and authorized

An HTTP action can be `Failed` with `code: BadRequest` and `error: null`; the
service's useful rejection message can be in its recorded response body:

```powershell
$action = "Call_backend"
az logicapp run action show-content @target --workflow $workflow --run-id $runId `
  --action $action --content outputs --max-bytes 4096 --output json
```

This explicitly retrieves potentially sensitive data. Obtain permission to read
the payload, use the smallest useful size and do not archive it by default.
When the result is complete, its `body` can contain `statusCode`, response
headers and a nested service `body`. The CLI does not interpret that service's
error contract or prescribe a repair automatically.

`--max-bytes` limits the returned payload and requests an HTTP byte range.
The sender may buffer a larger response if the endpoint ignores that range;
this is **not a hard download-size, memory or observation-time budget**.
If `truncated` is true, `body` is partial text, not trustworthy complete JSON.
No outputs link produces an explicit error directing you back to action
metadata; it is not an instruction to retry the workflow or retrieve inputs.
Reading inputs with `--content inputs` requires the same sensitive-data review.

## Keep command success separate from workflow success

`run show` and action inspection exit `0` when the requested read succeeds,
even when the recorded run/action is `Failed`. Content retrieval success means
the payload was read, not that the workflow or service request succeeded.
A successful Functions dispatcher invocation/log line also does not establish
that the entire workflow succeeded.

For a supported **Stateful** run that has not yet completed:

```powershell
az logicapp run wait @target --workflow $workflow --run-id $runId --timeout 60 --interval 1 --output json
$waitExit = $LASTEXITCODE
```

Wait exits `0` on observed `Succeeded`, `4` on a different terminal outcome,
`2` on its observation deadline, and `1` on an observation/protocol error.
Its structured result is printed before the nonzero exit. A wait deadline never
cancels the run. Do not treat a read/authentication failure as business failure,
or use a wait timeout as a reason to invoke again.

If you invoke a workflow separately, use only the new run ID actually returned
by `run start`. An accepted request without an identified run is not permission
to substitute the latest run from a list. Correcting an input and invoking again
creates a new execution and can duplicate side effects; it does not repair the
original run. Confirmation and support boundaries for cancellation/resubmission
are documented in [workflow execution](workflow-execution.md).

## What was actually exercised

The installed **0.1.19** wheel was exercised with 28 actual CLI calls against
owned local Stateful workflows on Windows, using existing Core Tools **4.15.2**,
Node **22.18.0**, and a privately copied cached Workflows bundle **1.170.91**.
Azurite used private storage/ports with telemetry disabled; the HTTP action
called only an owned loopback service. No tools/SDK were restored or installed.

| Scenario | Observed evidence | Next useful step |
| --- | --- | --- |
| `Convert_amount` received `"not-a-number"` | Run `Failed`; action `Failed`/`BadRequest`, with `error.code: InvalidTemplate` and a message that `int` could not convert the value. No outputs were recorded. | Inspect action metadata and correct the supplied value/authoring contract, not a missing output. |
| `Call_backend` received `-1` | Run `Failed`; action `Failed`/`BadRequest`, but metadata `error` was null. Recorded outputs contained HTTP 400 and `DiagnosticDemoRejected`: "Diagnostic demo: amount must be positive." | Inspect the explicitly retrieved response body and address the service's validation rule. |
| Success-dependent `After_success` in both failures | `Skipped`/`ActionSkipped`. | Investigate the preceding failed action, not the skipped dependency. |
| Both workflows invoked separately with `7` | New runs `Succeeded`, all actions `Succeeded`, and the failed-action query returned an empty list. | This confirms the two synthetic corrections only, not general workflow correctness. |

JSON/query/table projections and the real wait exit `4` were exercised; subsequent
successful inspection exited `0`. Authored files and user-global configuration,
contexts, runtime records and installed extension were unchanged. Owned helpers
were cleaned up. Windows shutdown initially retained a conservative private
ownership record; an independent observer after runner exit verified the original
process identities were gone and removed only those private stale records.
A recycled PID was not signaled. This is not universal shutdown qualification.

This is local normal-run evidence, **not live Azure, Linux/macOS, arbitrary
connector, nested-loop or SDK qualification**, and not a completely offline/
telemetry-free host guarantee. No official testing SDK was executed or enabled;
the [testing foundation](workflow-testing-foundation.md) retains `notExecuted`
business-test markers.

## When this basic flow is insufficient

Trigger failures, nested scopes/iterations, retries/request histories, secured or
expired content and incomplete running histories can require additional evidence.
The CLI has no complete traversal, curated diagnosis export or log-streaming
surface. For deployed problems, use the hosting service's logs and Azure Monitor/
Application Insights with appropriate authorization and redaction. For local
host/configuration problems use [runtime doctor](runtime-doctor.md), whose
environment observations do not certify workflow business behavior. Missing or
inconclusive evidence must remain an unknown reason, not an invented root cause.
