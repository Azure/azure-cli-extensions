# PRD: Azure Monitor Logs (Container Insights) CLI Enhancements

## 1. TL;DR

We are moving Azure Monitor Logs (Container Insights) onboarding off the legacy **addon profile** and onto the first-class **Azure Monitor Profile (AMP)**. This PRD covers the two onboarding commands in scope, closes AMP feature gaps (syslog port, Prometheus scraping, OTLP gRPC ports), removes an obsolete auth flag from the new path, and adds a deprecation warning on the legacy path.

**Two commands are in scope:**

| Command | Profile it configures | Direction |
|---|---|---|
| az aks enable-addons -a monitoring | Addon profile (addonProfiles.omsagent) | Legacy — keep working, start deprecating |
| az aks create/update --enable-azure-monitor-logs | Azure Monitor Profile (azureMonitorProfile.containerInsights) | Strategic — become the only supported way |

## 2. Problem & motivation

- `--enable-azure-monitor-logs` was meant to be the modern, AMP-based onboarding path, but it is **currently implemented on the legacy addon profile** — so today both commands write the same `omsagent` addon object. This blocks us from using AMP-only capabilities and from deprecating the addon.
- The AMP `containerInsights` schema already supports **syslog port** and **Prometheus scraping** controls, and the app-monitoring schema supports **OTLP gRPC ports**, but the CLI exposes none of them on the new path.
- The legacy **auth flag** (`--enable-msi-auth-for-monitoring`) is meaningless for AMP (which is managed-identity only), yet it is still accepted on the new path.
- The latest API version **removed** `disableCustomMetrics` from `containerInsights`, so it must not surface anywhere in the CLI.

## 3. Goals / Non-goals

**Goals**

- Make `--enable-azure-monitor-logs` write **only** the AMP profile.
- Reach parity + close gaps on the AMP path (syslog port, Prometheus scraping, OTLP gRPC).
- Remove the obsolete auth flag from the AMP path; warn about it on the legacy path.
- Keep `az aks enable-addons -a monitoring` working (backward compatible).
**Non-goals**

- Removing or breaking the legacy `enable-addons monitoring` command.
- Exposing `disableCustomMetrics` (removed from the API).
- Changes to metrics-only (Managed Prometheus) onboarding.

## 4. Background: the two profiles & their schema

### 4.1 Addon profile — set by `az aks enable-addons -a monitoring`

`properties.addonProfiles.omsagent`:

```json
{
  "enabled": true,
  "config": {
    "logAnalyticsWorkspaceResourceID": "<LA workspace ARM id>",
    "useAADAuth": "true" | "false"   // MSI auth vs legacy shared-key auth
  }
}
```

- Auth: supports **both** managed-identity (`useAADAuth=true`) and legacy shared-key (`useAADAuth=false`), driven by `--enable-msi-auth-for-monitoring`.

### 4.2 Azure Monitor Profile (AMP) — target of `--enable-azure-monitor-logs`

`properties.azureMonitorProfile` (latest API `2026-07-02-preview`):

```json
{
  "containerInsights": {
    "enabled": true,
    "logAnalyticsWorkspaceResourceId": "<LA workspace ARM id>",
    "syslogPort": 28330,                         // default 28330
    "disablePrometheusMetricsScraping": false,   // default false
    "containerNetworkLogs": "<value>"
    // NOTE: disableCustomMetrics was REMOVED in the latest API — do not use.
  },
  "appMonitoring": {
    "openTelemetryLogsAndTraces": { "enabled": true, "httpPort": 0, "grpcPort": 0 },
    "openTelemetryMetrics":       { "enabled": true, "httpPort": 0, "grpcPort": 0 }
  }
}
```

- Auth: **managed-identity only** — there is no shared-key/`useAADAuth` concept.

### 4.3 Current CLI coverage of the AMP schema

| AMP field | Flag today? |
|---|---|
| `containerInsights.enabled` | Yes (`--enable-azure-monitor-logs` / `--disable-azure-monitor-logs`) — *but writes the addon profile* |
| `containerInsights.logAnalyticsWorkspaceResourceId` | Yes (`--workspace-resource-id`) |
| `containerInsights.syslogPort` | **No** |
| `containerInsights.disablePrometheusMetricsScraping` | **No** |
| `appMonitoring.openTelemetry*.httpPort` | Yes (`--opentelemetry-metrics-port`, `--opentelemetry-logs-port`) |
| `appMonitoring.openTelemetry*.grpcPort` | **No** |

## 5. Requirements

| ID | Requirement | Priority |
|---|---|---|
| R0 | Add OTLP gRPC port overrides | P0 |
| R1 | `--enable-azure-monitor-logs` writes only the AMP profile | P0 |
| R2 | Remove legacy auth flag from `--enable-azure-monitor-logs` | P0 |
| R3 | Do not expose `disableCustomMetrics` (removed from API) | P0 |
| R4 | Add Prometheus-scraping + syslog-port controls to the AMP path | P0 |
| R5 | Warn when the legacy auth flag is used with `enable-addons monitoring` | P0 |

### R0 — OTLP gRPC port overrides

Today only the OTLP **HTTP** port is settable; the gRPC port cannot be overridden.

- Allow overriding the gRPC port for both OTLP signals:
  - metrics → `appMonitoring.openTelemetryMetrics.grpcPort`
  - logs & traces → `appMonitoring.openTelemetryLogsAndTraces.grpcPort`
- HTTP and gRPC ports are independently settable per signal; make the HTTP-vs-gRPC mapping unambiguous.
**Acceptance criteria**

- A gRPC override sets the corresponding `grpcPort`; unset leaves the server default.
- HTTP and gRPC ports settable independently for metrics and logs/traces.
- Values round-trip on `az aks update`.

### R1 — Switch `--enable-azure-monitor-logs` to the AMP profile only

**As an** AKS user, **when** I run `az aks create/update --enable-azure-monitor-logs`, **I want** it to configure `azureMonitorProfile.containerInsights` (and not the legacy `omsagent` addon), so onboarding uses the modern profile.

- Today the flag writes `addonProfiles.omsagent`; it must instead write only `azureMonitorProfile.containerInsights.enabled = true` (+ workspace id).
- `--disable-azure-monitor-logs` must disable via the AMP profile (`containerInsights.enabled = false`) and no longer depend on the addon object.
- **Container network logs move with it.** On the legacy addon path this is the `omsagent` config key `enableRetinaNetworkFlags` ("True"/"False"); it lines up with the AMP field `containerInsights.containerNetworkLogs` (enum `Enabled`/`Disabled`, default `Disabled`). The **same** `--enable-container-network-logs` / `--disable-container-network-logs` commands must set `containerInsights.containerNetworkLogs` accordingly (`Enabled` / `Disabled`) instead of the addon config key.
- The legacy `enable-addons monitoring` command is unaffected and keeps using the addon profile.
**Parity — all monitoring options must keep working on the new command**

Several legacy monitoring options are realized as **out-of-band ARM resources** (DCR / DCE / DCRA / AMPLS), not as `containerInsights` fields. They work today only because `--enable-azure-monitor-logs` writes the `omsagent` addon, and that provisioning is gated on the addon object existing. After the AMP switch, the **same** command must continue to honor them without the addon.

| Legacy flag | Configures | Post-switch requirement |
|---|---|---|
| `--workspace-resource-id` | Log Analytics workspace | → `containerInsights.logAnalyticsWorkspaceResourceId` |
| `--enable-syslog` | Syslog collection (DCR syslog data source) | Provision the same DCR data source |
| `--data-collection-settings` | DCR tuning (interval, namespaces, streams, `enableContainerLogV2`) | Apply the same DCR settings |
| `--enable-high-log-scale-mode` | High log scale (ingestion DCE) | Provision the same DCE |
| `--ampls-resource-id` | AMPLS private-link scope (private cluster, MSI) | Provision the same AMPLS links |
| `--enable/disable-container-network-logs` | Container network logs | → `containerInsights.containerNetworkLogs` (see above) |
| `--enable-msi-auth-for-monitoring` | Auth mode | **Dropped** — AMP is MSI-only (see R2) |

> The DCR/DCE/DCRA/AMPLS provisioning currently keys off the `omsagent` addon object; after the switch it must be driven off the AMP profile (workspace id from `containerInsights.logAnalyticsWorkspaceResourceId`) and must not require the addon to exist.

**Acceptance criteria**

- `--enable-azure-monitor-logs` results in `azureMonitorProfile.containerInsights.enabled=true` with the workspace id, and **no** `omsagent` addon entry authored by this flag.
- `--disable-azure-monitor-logs` sets `containerInsights.enabled=false`.
- `--enable-container-network-logs` sets `containerInsights.containerNetworkLogs="Enabled"` (and `--disable-container-network-logs` → `"Disabled"`); it no longer writes `enableRetinaNetworkFlags`.
- `--enable-syslog`, `--data-collection-settings`, `--enable-high-log-scale-mode`, and `--ampls-resource-id` produce the **same** DCR/DCE/DCRA/AMPLS artifacts on `--enable-azure-monitor-logs` as they do today on `--enable-addons monitoring`.
- That artifact provisioning no longer depends on the presence of the `omsagent` addon profile.
- `enable-addons -a monitoring` behavior is unchanged.

### R2 — Remove the legacy auth flag from `--enable-azure-monitor-logs`

The AMP profile is managed-identity only, so `--enable-msi-auth-for-monitoring` is meaningless here.

- `--enable-azure-monitor-logs` must not accept or honor `--enable-msi-auth-for-monitoring`.
- Passing them together returns a clear, actionable error.
- No `useAADAuth`/shared-key concept is written on the AMP path.
**Acceptance criteria**

- `--enable-azure-monitor-logs` works with no auth flag (MSI implicit).
- Combining the two flags errors out with a helpful message.

### R3 — Do not expose `disableCustomMetrics`

`containerInsights.disableCustomMetrics` was removed in the latest API version.

- No CLI flag maps to it; it must not appear in any request the CLI sends.
- Schema/reference docs must reflect its removal.
**Acceptance criteria**

- No CLI surface reads or writes `disableCustomMetrics`.

### R4 — Prometheus-scraping & syslog-port controls on the AMP path

Expose the two `containerInsights` controls that the schema already supports.

- A flag to toggle Prometheus metrics scraping → `containerInsights.disablePrometheusMetricsScraping`.
- A flag to set the syslog host port → `containerInsights.syslogPort` (integer; server default 28330 when unset).
- Available on `az aks create` and `az aks update` for the AMP path; both are updatable.
**Suggested flags**

| Flag | Type | Maps to | Notes |
|---|---|---|---|
| `--disable-prometheus-metrics-scraping` | switch | `disablePrometheusMetricsScraping = true` | default off (scraping on); mirrors the existing `--enable-…/--disable-…` metrics style |
| `--enable-prometheus-metrics-scraping` | switch | `disablePrometheusMetricsScraping = false` | to re-enable on `update`; mutually exclusive with the disable flag |
| `--syslog-port` | int | `syslogPort` | valid TCP port; unset ⇒ server default 28330 |

> Naming note: the pre-existing `--enable-syslog` (three-state) toggles legacy syslog **collection** and is distinct from the new `--syslog-port` host-port control.

**Example usage**

```bash
# Enable Azure Monitor logs (AMP), disable Prometheus scraping, custom syslog port
az aks create -g <rg> -n <cluster> \
  --enable-azure-monitor-logs \
  --disable-prometheus-metrics-scraping \
  --syslog-port 28331

# Later, re-enable scraping and change the port on an existing cluster
az aks update -g <rg> -n <cluster> \
  --enable-prometheus-metrics-scraping \
  --syslog-port 29000
```

**Acceptance criteria**

- The scraping flag sets/clears `disablePrometheusMetricsScraping`.
- The syslog-port flag sets `syslogPort` (validated as a TCP port); unset leaves the default.
- Both round-trip on `az aks update` without disturbing other monitoring settings.

### R5 — Deprecation warning on the legacy auth flag

**As an** AKS user, **when** I pass `--enable-msi-auth-for-monitoring` on `az aks enable-addons -a monitoring`, **I want** a warning that the flag is deprecated and that managed-identity auth (and `--enable-azure-monitor-logs`) is the recommended path.

- The command still succeeds (non-breaking); only a warning is added.
- Especially relevant when the flag is set to `false` (opting into legacy shared-key auth).
**Acceptance criteria**

- Warning shown once when the flag is explicitly provided; not shown when omitted.
- Command completes successfully; resulting `useAADAuth` value is unchanged.

## 6. Target end-state (the two commands)

| Command | Writes | Auth | Extra controls |
|---|---|---|---|
| `az aks enable-addons -a monitoring` | `addonProfiles.omsagent` | MSI or shared-key (**warns** on explicit legacy auth flag) | unchanged |
| `az aks create/update --enable-azure-monitor-logs` | `azureMonitorProfile.containerInsights` **only** | MSI only (**no** auth flag) | `--syslog-port`, Prometheus-scraping toggle, `--enable/disable-container-network-logs` (→ `containerNetworkLogs`); OTLP gRPC ports via OTLP flags |
