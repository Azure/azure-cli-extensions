# Correlation ID Propagation — Scenario Walkthrough

This document traces the **runtime call flow** of `az connectedk8s proxy` after this PR, file-by-file, showing where the correlation id is born, where it gets stamped, and which downstream system reads it at each hop.

> **TL;DR:** one `uuid4` minted at command entry → stamped on the az-cli header bag → ARM honors it → also threaded as a kwarg through 6 function frames → stamped on every localhost `requests` call to arcProxy → arcProxy carries it into the Relay frame headers → ConnectedProxyAgent logs it to Geneva. Same GUID on every hop.

---

## Cast of files

| # | File | Role |
|---|---|---|
| 1 | `azext_connectedk8s/_constants.py` | Defines the canonical header name |
| 2 | `azext_connectedk8s/_utils.py` | Hosts the `ensure_correlation_id()` helper |
| 3 | `azext_connectedk8s/custom.py` | Entry point — `client_side_proxy_wrapper` mints + threads the id |
| 4 | `azext_connectedk8s/clientproxyhelper/_proxylogic.py` | High-level proxy steps (ARM credential fetch, register-to-proxy) |
| 5 | `azext_connectedk8s/clientproxyhelper/_utils.py` | Low-level HTTP helpers (`make_api_call_with_retries`, kid fetch, AT post) |
| 6 | _arcProxy (separate repo, build #9)_ | Reads the header, re-stamps on outbound relay frames |
| 7 | _ARM service (external)_ | Honors the client-supplied header and echoes it back |

---

## Sequence

### Step 1 — User runs the command

```bash
az connectedk8s proxy -n my-cluster -g my-rg
```

az-cli dispatches to:

**`custom.py :: client_side_proxy_wrapper(cmd, ...)`** *(line 3795)*

### Step 2 — Mint the session id (NEW)

**`custom.py` line 3808** calls into the helper:

```python
# custom.py
correlation_id = utils.ensure_correlation_id(cmd, log_prefix="Arc proxy")
```

→ control jumps to:

**`_utils.py :: ensure_correlation_id(cmd, log_prefix)`** *(line 62)*

```python
# _utils.py
headers = cmd.cli_ctx.data.setdefault("headers", {})       # ① grab or create header bag
existing = headers.get(consts.Correlation_Request_Id_Header)  # ② already set?
if existing:
    correlation_id = str(existing)                          # ③a reuse (idempotent)
else:
    correlation_id = str(uuid.uuid4())                      # ③b MINT NEW UUID
    headers[consts.Correlation_Request_Id_Header] = correlation_id  # ④ stamp on shared bag
telemetry.set_debug_info(...)                               # ⑤ log to az-cli telemetry
logger.warning("%s session correlationId: %s", ...)         # ⑥ surface to user terminal
return correlation_id                                       # ⑦ return for in-process plumbing
```

After this returns, **two things** are now true:

- `cmd.cli_ctx.data["headers"]` contains `{"x-ms-correlation-request-id": "<sid>"}` — the az-cli SDK pipeline will auto-forward this on every ARM call.
- The local variable `correlation_id` holds the same string, ready to be passed as a kwarg into the localhost code paths.

The user already sees:

```
WARNING: cli.azext_connectedk8s._utils: Arc proxy session correlationId: a9112c37-2c50-4fb7-9956-a17b527aacc1
```

### Step 3 — Hand off to the proxy main loop

**`custom.py` line 3961**: `client_side_proxy_wrapper` calls into the main lifecycle function, passing the new kwarg:

```python
# custom.py
client_side_proxy_main(
    cmd, ...,
    correlation_id=correlation_id,     # ← NEW kwarg
)
```

**`custom.py :: client_side_proxy_main(...)`** *(line 3971)* now has `correlation_id` in scope.

### Step 4 — First proxy start

**`custom.py` line 3987**: `client_side_proxy_main` calls `client_side_proxy(...)` for initial setup:

```python
# custom.py
hc_expiry, at_expiry, clientproxy_process = client_side_proxy(
    cmd, ...,
    correlation_id=correlation_id,     # ← threaded through
)
```

**`custom.py :: client_side_proxy(...)`** *(line 4044)* now has `correlation_id`.

### Step 5 — ARM call to list cluster credentials

Inside `client_side_proxy`, line **4061**:

```python
# custom.py
client_side_proxy_input = _proxylogic.get_cluster_user_credentials(
    cmd, client,
    resource_group_name, cluster_name, auth_method,
    correlation_id=correlation_id,    # ← threaded through
)
```

→ control jumps to:

**`_proxylogic.py :: get_cluster_user_credentials(...)`** *(line 78)*

```python
# _proxylogic.py
sdk_kwargs: dict[str, Any] = {}
if correlation_id:
    sdk_kwargs["headers"] = {
        consts.Correlation_Request_Id_Header: correlation_id,    # ← stamp on SDK call
    }

result = client.list_cluster_user_credential(
    resource_group_name, cluster_name, list_prop,
    **sdk_kwargs,                                                # ← header lands here
)
```

Now the **outbound ARM HTTPS request** carries:

```
POST https://management.azure.com/.../listClusterUserCredential?api-version=...
x-ms-correlation-request-id: a9112c37-2c50-4fb7-9956-a17b527aacc1
Authorization: Bearer ...
```

### Step 6 — ARM honors and echoes

External ARM service:

- Reads `x-ms-correlation-request-id` from the request.
- Uses it as the operation's correlation id internally.
- Writes a row to `AzureActivity` with `correlationId = "a9112c37-..."`.
- Returns the response with `x-ms-correlation-request-id: a9112c37-...` echoed back.

✅ Geneva-side ARM join now possible.

### Step 7 — Local proxy starts; register kubeconfig to it

After arcProxy.exe is spawned and listening on `localhost:47011` (the existing flow, unchanged), the CLI registers the kubeconfig + cluster details with it.

**`custom.py` line ~4090** (within `client_side_proxy`) calls:

```python
# custom.py
_proxylogic.post_register_to_proxy(
    data, token, ...,
    clientproxy_process=clientproxy_process,
    correlation_id=correlation_id,     # ← threaded through
)
```

**`_proxylogic.py :: post_register_to_proxy(...)`** *(line 105)* now passes it down:

```python
# _proxylogic.py
response = clientproxyutils.make_api_call_with_retries(
    "post", uri, data, tls_verify, ...,
    clientproxy_process,
    correlation_id=correlation_id,    # ← into the HTTP helper
)
```

### Step 8 — Stamp the localhost HTTP call

**`clientproxyhelper/_utils.py :: make_api_call_with_retries(...)`** *(line 79)*:

```python
# clientproxyhelper/_utils.py
headers = (
    {consts.Correlation_Request_Id_Header: correlation_id}    # ← build header dict
    if correlation_id else None
)
for i in range(consts.API_CALL_RETRIES):
    response = requests.request(
        method, uri, json=data, verify=tls_verify,
        headers=headers,                                      # ← stamp on POST to arcProxy
    )
```

Outbound on the wire (localhost):

```
POST https://localhost:47011/register
x-ms-correlation-request-id: a9112c37-2c50-4fb7-9956-a17b527aacc1
Content-Type: application/json
{ "kubeconfigs": [...], ... }
```

### Step 9 — arcProxy reads + propagates (build #9)

arcProxy (separate repo, already shipped):

1. Reads `x-ms-correlation-request-id` from the inbound localhost request.
2. Stores it as the **session** correlation id for the arcProxy process.
3. Logs `OutboundWSHeaders: ..., CorrelationID: a9112c37-...` when opening the WebSocket to Relay.
4. Logs `OutboundHTTPHeaders: ..., CorrelationID: a9112c37-..., ClientRequestID: <per-call>` on every inner HTTP redirect carried through the Relay WS frame.

✅ arcProxy logs (Kusto: `ArcProxyLogs`) now joinable.

### Step 10 — Token refresh loop (the long-running path)

Back in **`custom.py :: client_side_proxy_main`**, after the initial registration, the keep-alive loop iterates. On each iteration (every few minutes for ~26h+), if the token is about to expire, it calls back into the same proxy setup:

```python
# custom.py (inside the while True loop, line 4023)
flag, new_hc_expiry, new_at_expiry = client_side_proxy_main(
    ...,                       # recursive-ish refresh path
    correlation_id=correlation_id,    # ← same id reused for the LIFE of the session
)
```

→ same Steps 5–9 fire again with the **same** `a9112c37-...`. So a single 26-hour proxy session shows up as **one** correlation id across hundreds of ARM token refreshes and thousands of localhost HTTP frames.

### Step 11 — Operator queries Geneva

When something fails, the operator runs **one** Kusto query:

```kusto
union AzureActivity, ArcProxyLogs, ConnectAgentTraces
| where correlationId == "a9112c37-2c50-4fb7-9956-a17b527aacc1"
| order by TimeGenerated asc
```

…and gets the entire flow:

| Time | Source | What |
|---|---|---|
| t+0.00s | `AzureActivity` | ARM `listClusterUserCredential` (200 OK) |
| t+0.12s | `ArcProxyLogs` | `OutboundWSHeaders` — WS opened to Relay |
| t+0.15s | `ArcProxyLogs` | `OutboundHTTPHeaders` — `GET /api/v1/namespaces` |
| t+0.18s | `ConnectAgentTraces` | KAP authenticates user, returns 200 |
| t+0.92s | `ArcProxyLogs` | `OutboundHTTPHeaders` — `GET /api/v1/nodes` |
| t+0.95s | `ConnectAgentTraces` | KAP returns 403 (RBAC) — **here is the failure** |
| t+9h | `AzureActivity` | ARM token refresh (200) |
| t+26h | `ArcProxyLogs` | `ProxyError: context canceled` — TCP RST during refresh |

End-to-end timeline. No hand-stitching.

---

## Visual: call graph

```
az connectedk8s proxy
└── custom.py :: client_side_proxy_wrapper                          [line 3795]
     │
     ├─ utils.ensure_correlation_id(cmd, "Arc proxy")               [line 3808]  ★ MINT
     │   └─ _utils.py :: ensure_correlation_id                      [line 62]
     │        ├─ cli_ctx.data["headers"]["x-ms-correlation-request-id"] = uuid4()
     │        ├─ logger.warning("Arc proxy session correlationId: <sid>")
     │        └─ return correlation_id
     │
     └─ client_side_proxy_main(..., correlation_id=correlation_id)  [line 3961]
          │
          └─ client_side_proxy(..., correlation_id=correlation_id)  [line 3987]
               │
               ├─ _proxylogic.get_cluster_user_credentials          [line 4061]
               │   └─ client.list_cluster_user_credential(headers={...})  ★ ARM CALL
               │       (ARM honors + echoes; AzureActivity logs sid)
               │
               ├─ <spawn arcProxy.exe>                              [existing flow]
               │
               └─ _proxylogic.post_register_to_proxy                [line ~4090]
                    └─ _utils.make_api_call_with_retries
                         └─ requests.request(headers={"x-ms-correlation-request-id": sid})
                                  ★ LOCALHOST POST
                              │
                              ▼
                         arcProxy.exe (separate process, build #9)
                              ├─ reads inbound header → process-session sid
                              ├─ OutboundWSHeaders: CorrelationID=sid
                              └─ OutboundHTTPHeaders: CorrelationID=sid, ClientRequestID=<per-call>
                                          │
                                          ▼
                                     Azure Relay (byte pipe)
                                          │
                                          ▼
                                ConnectedProxyAgent (in cluster)
                                          ├─ reads sid from frame headers
                                          ├─ ConnectAgentTraces row: CorrelationId=sid
                                          └─ proxies to in-cluster KAP / kube-apiserver
```

---

## Two-tier id model on every localhost log line

After this PR + arcProxy build #9, every `OutboundHTTPHeaders` log line carries **two** ids:

| Header | Source | Cardinality | Use |
|---|---|---|---|
| `x-ms-correlation-request-id` | **CLI** (this PR) | **1 per session** | Broad pivot — find every event in the long-running proxy session |
| `x-ms-client-request-id` | **arcProxy** (build #9) | **1 per redirect** | Pinpoint pivot — find the one failed inner HTTP call inside a session |
| `x-ms-request-id` | **ARM / agent** | 1 per server-side request | Server-side correlation only |

This combination is what makes the 26-hour-session debug case tractable: one query gets you the whole session, and within it, each individual failed call has its own unique `ClientRequestID`.

---

## What did NOT change

For reviewer reassurance:

- No other `az connectedk8s` command. `ensure_correlation_id` is called from **one place** in production (`client_side_proxy_wrapper`).
- No SDK version bump.
- No vendored model files (`vendored_sdks/`).
- No change to spawn arguments, port allocation, proxy download logic, kubeconfig contents, helm charts, RBAC, or telemetry channels.
- No change to authentication, token acquisition, or the broker.
- `requests.request(...)` calls without `correlation_id` (none today — every call site got the kwarg) would still work: `headers=None` is the pre-PR behavior.

---

## Why the kwarg threading instead of one global

A `correlation_id: str | None = None` kwarg on each function in the call chain was deliberately chosen over a thread-local or module-level global because:

1. **Explicit data flow** — reviewers can trace where the id comes from and where it lands.
2. **Test-friendly** — every helper can be unit-tested with a fixed id passed in, no global state to reset between tests.
3. **Idiomatic Python** — modules in this codebase don't use thread-locals for request context.
4. **Adoption-friendly** — when other commands opt in (`connect`, `delete`, etc.), they pass their own id without colliding.
5. **`None` is safe** — every signature accepts `None` and silently skips header stamping, so any non-adopting code path is unchanged.

---

**End of walkthrough.** See [`correlation-id-propagation.md`](correlation-id-propagation.md) for the design rationale and [`test_correlation_id.py`](../azext_connectedk8s/tests/unittests/test_correlation_id.py) for the unit test coverage.
