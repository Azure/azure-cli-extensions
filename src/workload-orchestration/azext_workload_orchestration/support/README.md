# Support Bundle Package

Diagnostic toolkit for the `az workload-orchestration support create-bundle` CLI command.

Collects Kubernetes cluster health data, container logs, prerequisite validation
checks, and WO-specific resource states into a ZIP bundle for troubleshooting
Day 0 (installation) and Day N (runtime) issues on 3rd-party clusters.

## Architecture

```
support/
├── __init__.py       # Public API — exports create_support_bundle()
├── bundle.py         # Orchestrator — wires everything together
├── consts.py         # Constants — thresholds, namespaces, folder names
├── utils.py          # Infrastructure — K8s client, safe API calls, file I/O
├── collectors.py     # Data collection — resources, logs, metrics
├── validators.py     # Health checks — 18 checks across 10 categories
└── README.md         # This file
```

### Data Flow

```
create_support_bundle()          # bundle.py — entry point
  │
  ├── get_kubernetes_client()    # utils.py — connect to cluster
  ├── create_bundle_directory()  # utils.py — create folder structure
  ├── detect_cluster_capabilities()  # utils.py — detect installed components
  │
  ├── run_all_checks()           # validators.py — 18 prerequisite checks
  │     ├── _check_k8s_version()
  │     ├── _check_node_readiness()
  │     ├── _check_dns_health()
  │     └── ... (18 total)
  │
  ├── collect_cluster_info()     # collectors.py — version, nodes, namespaces
  ├── collect_cluster_resources()    # collectors.py — SCs, CRDs, webhooks
  ├── validate_namespaces()      # collectors.py — skip invalid namespaces
  │
  ├── for each namespace:
  │     ├── collect_namespace_resources()  # pods, deployments, services, etc.
  │     ├── collect_container_logs()       # threaded log collection
  │     ├── collect_previous_logs()        # crash-looping pod logs
  │     ├── collect_resource_quotas()      # quotas & limit ranges
  │     └── collect_pvcs()                 # persistent volume claims
  │
  ├── collect_wo_components()    # collectors.py — Symphony, cert-manager, Gatekeeper
  ├── collect_metrics()          # collectors.py — node/pod metrics
  │
  ├── _compute_health_summary()  # bundle.py — score 0-100, status
  ├── write metadata.json        # bundle.py — full bundle metadata
  └── create_zip_bundle()        # utils.py — zip + cleanup
```

### Bundle Output Structure

```
wo-support-bundle-YYYYMMDD-HHMMSS.zip
├── metadata.json           # Bundle info, health summary, capabilities
├── cluster-info/
│   ├── cluster-info.json   # K8s version, nodes, namespaces
│   ├── capabilities.json   # Detected components (Symphony, cert-manager, etc.)
│   └── metrics.json        # Node/pod resource usage (if metrics-server)
├── checks/
│   ├── cluster-info--k8s-version.json
│   ├── node-health--node-readiness.json
│   └── ... (one file per check)
├── resources/
│   ├── cluster-resources.json        # StorageClasses, CRDs, webhooks, CSI
│   ├── kube-system-resources.json    # Pods, deployments, services per ns
│   ├── kube-system-quotas.json       # ResourceQuotas, LimitRanges
│   └── wo-components.json            # Symphony targets, ClusterIssuers
└── logs/
    ├── kube-system/
    │   ├── coredns-abc--coredns.log
    │   └── ...
    └── workloadorchestration/
        ├── symphony-api-xyz--symphony-api.log
        ├── symphony-api-xyz--symphony-api--previous.log  # crashed container
        └── ...
```

## Module Guide

### consts.py — Constants

All tunable values in one place. No business logic.

| Constant Group | Examples | Purpose |
|----------------|----------|---------|
| Bundle defaults | `DEFAULT_TAIL_LINES=1000`, `DEFAULT_API_TIMEOUT_SECONDS=30` | Collection behavior |
| Retry | `DEFAULT_MAX_RETRIES=3`, `DEFAULT_RETRY_BACKOFF_BASE=1.0` | API call resilience |
| Namespaces | `WO_NAMESPACE`, `DEFAULT_NAMESPACES`, `PROTECTED_NAMESPACES` | Which namespaces to collect |
| API groups | `API_GROUP_SYMPHONY`, `API_GROUP_CERT_MANAGER` | Capability detection |
| Thresholds | `MIN_CPU_CORES=2`, `MIN_MEMORY_GI=4`, `MIN_NODE_COUNT_PROD=3` | Prerequisite minimums |
| Folder names | `FOLDER_LOGS`, `FOLDER_CHECKS`, `FOLDER_RESOURCES` | Bundle directory layout |
| Status values | `STATUS_PASS`, `STATUS_FAIL`, `STATUS_WARN` | Check result statuses |

### utils.py — Infrastructure

Shared utilities used by collectors and validators.

| Function | Purpose |
|----------|---------|
| `get_kubernetes_client()` | Initialize K8s API clients from kubeconfig |
| `safe_api_call()` | Wrap any K8s API call with retry, timeout, and RBAC error detection |
| `create_bundle_directory()` | Create the bundle folder structure |
| `create_zip_bundle()` | Zip the bundle and clean up raw directory |
| `detect_cluster_capabilities()` | Detect installed components (Symphony, cert-manager, Gatekeeper, etc.) |
| `write_json()` / `write_text()` | Safe file writers (never crash on I/O errors) |
| `write_check_result()` | Write a check result to the checks/ folder |
| `parse_cpu()` / `parse_memory_gi()` | Parse K8s resource strings (`"3860m"` → `3.86`) |
| `format_bytes()` | Human-readable byte formatting |
| `check_disk_space()` | Pre-flight disk space check |

**Key pattern — `safe_api_call()`:**
```python
result, err = safe_api_call(
    core.list_namespaced_pod, namespace,
    description="list pods in kube-system",  # for error messages
    max_retries=3,                           # retries on 500/502/503/504
    timeout_seconds=30,                      # per-call timeout
)
if err:
    logger.warning("Failed: %s", err)
else:
    process(result)
```

### collectors.py — Data Collection

Gathers cluster state into the bundle directory.

| Function | What it collects | Output location |
|----------|-----------------|-----------------|
| `validate_namespaces()` | Pre-flight namespace existence check | (no file — filters list) |
| `collect_cluster_info()` | K8s version, nodes, namespaces | `cluster-info/cluster-info.json` |
| `collect_namespace_resources()` | Pods, Deployments, Services, DaemonSets, StatefulSets, ReplicaSets, Jobs, CronJobs, Ingresses, NetworkPolicies, ServiceAccounts, Events, ConfigMaps | `resources/{ns}-resources.json` |
| `collect_cluster_resources()` | StorageClasses, PVs, webhooks, CRDs, CSI drivers | `resources/cluster-resources.json` |
| `collect_container_logs()` | Container logs (threaded, with tail + truncation) | `logs/{ns}/{pod}--{container}.log` |
| `collect_previous_logs()` | Previous logs for crash-looping containers | `logs/{ns}/{pod}--{container}--previous.log` |
| `collect_wo_components()` | Symphony targets, ClusterIssuers, Gatekeeper templates | `resources/wo-components.json` |
| `collect_resource_quotas()` | ResourceQuotas, LimitRanges | `resources/{ns}-quotas.json` |
| `collect_pvcs()` | PersistentVolumeClaims | `resources/{ns}-pvcs.json` |
| `collect_metrics()` | Node/pod metrics (if metrics-server available) | `cluster-info/metrics.json` |

### validators.py — Health Checks

18 prerequisite checks organized in `run_all_checks()`.

| # | Check Name | Category | What it validates |
|---|------------|----------|-------------------|
| 1 | `k8s-version` | cluster-info | Server version ≥ 1.24.0 |
| 2 | `node-readiness` | node-health | All nodes Ready, no pressure conditions |
| 3 | `node-capacity` | node-health | CPU ≥ 2 cores, Memory ≥ 4Gi per node |
| 4 | `cluster-resources` | node-health | Total cluster CPU/memory |
| 5 | `dns-pods` | dns-health | CoreDNS pods running |
| 6 | `dns-resolution` | dns-health | External DNS resolution works |
| 7 | `default-storage-class` | storage | Default StorageClass exists |
| 8 | `csi-drivers` | storage | CSI drivers installed |
| 9 | `cert-manager-installed` | cert-manager | cert-manager pods running |
| 10 | `wo-namespace` | wo-components | workloadorchestration ns exists |
| 11 | `protected-namespace` | wo-components | WO ns is not a protected namespace |
| 12 | `wo-pods` | wo-components | All WO pods running |
| 13 | `wo-webhooks` | wo-components | Symphony webhooks configured |
| 14 | `policy-engines` | admission-controllers | Gatekeeper/Kyverno detected |
| 15 | `psa-labels` | admission-controllers | Pod Security Admission labels |
| 16 | `resource-quotas` | wo-components | Quota usage on WO namespace |
| 17 | `image-pull-secrets` | registry-access | Image pull secrets available |
| 18 | `proxy-settings` | wo-components | Proxy env vars in WO pods |

### bundle.py — Orchestrator

Main entry point. Wires collectors + validators together.

| Function | Purpose |
|----------|---------|
| `create_support_bundle()` | Main orchestration — called by CLI |
| `_compute_health_summary()` | Score 0-100 + HEALTHY/DEGRADED/CRITICAL |
| `_out()` | Console output (uses logger.warning per az CLI convention) |
| `_print_cluster_info()` | Format cluster info for console |
| `_print_capabilities()` | Format detected capabilities |
| `_print_check_results()` | Format check results with [PASS]/[FAIL] icons |

## How to Add a New Check

Adding a new prerequisite check takes 2 steps:

### Step 1: Write the check function in `validators.py`

```python
def _check_my_new_thing(clients, bundle_dir, cluster_info, capabilities):
    """Check that my new thing is properly configured."""
    core = clients["core_v1"]

    # Use safe_api_call for ALL K8s API calls
    result, err = safe_api_call(
        core.list_namespaced_pod, "my-namespace",
        description="list pods in my-namespace",
    )
    if err:
        return write_check_result(
            bundle_dir, CATEGORY_WO_COMPONENTS, "my-new-check",
            STATUS_WARN, f"Could not check: {err}"
        )

    # Your validation logic here
    pods = result.items
    if len(pods) >= 1:
        return write_check_result(
            bundle_dir, CATEGORY_WO_COMPONENTS, "my-new-check",
            STATUS_PASS, f"{len(pods)} pod(s) found"
        )
    else:
        return write_check_result(
            bundle_dir, CATEGORY_WO_COMPONENTS, "my-new-check",
            STATUS_FAIL, "No pods found — ensure my-thing is installed"
        )
```

**Rules for check functions:**
- Signature: `(clients, bundle_dir, cluster_info, capabilities)` — always the same 4 args
- Always use `safe_api_call()` — never call K8s APIs directly
- Always return `write_check_result()` — never return raw dicts
- Use `STATUS_PASS`, `STATUS_FAIL`, `STATUS_WARN`, or `STATUS_SKIP`
- Never raise exceptions — handle errors and return WARN/ERROR status

### Step 2: Register in `run_all_checks()`

Add one line to the `checks` list:

```python
checks = [
    (_check_k8s_version, "Kubernetes version compatibility"),
    # ... existing checks ...
    (_check_proxy_settings, "Proxy configuration"),
    (_check_my_new_thing, "My new thing"),           # ← ADD HERE
]
```

That's it. The check will automatically:
- Run during bundle creation
- Show [PASS]/[FAIL] in console output
- Write result to `checks/wo-components--my-new-check.json`
- Count toward the health summary score

## How to Add a New Resource Collector

### Namespace-scoped resource

Add to `collect_namespace_resources()` in `collectors.py`:

```python
# HorizontalPodAutoscalers
try:
    from kubernetes import client as _k8s_client
    autoscaling_v2 = _k8s_client.AutoscalingV2Api()
    result, err = safe_api_call(
        autoscaling_v2.list_namespaced_horizontal_pod_autoscaler, namespace,
        description=f"list HPAs in {namespace}"
    )
    if result:
        resources["hpas"] = [
            {"name": h.metadata.name, "min": h.spec.min_replicas, "max": h.spec.max_replicas}
            for h in result.items
        ]
except Exception as ex:
    logger.debug("Autoscaling API not available: %s", ex)
```

### Cluster-scoped resource

Add to `collect_cluster_resources()` in `collectors.py`.

## CLI Parameters

| Parameter | Python arg | Default | Description |
|-----------|-----------|---------|-------------|
| `--output-dir` / `-d` | `output_dir` | cwd | Where to save the zip |
| `--namespaces` | `namespaces` | kube-system, workloadorchestration, cert-manager | Namespaces to collect |
| `--tail-lines` | `tail_lines` | 1000 | Log lines per container |
| `--full-logs` | `full_logs` | False | Collect complete logs |
| `--skip-checks` | `skip_checks` | False | Skip prerequisite checks |
| `--skip-logs` | `skip_logs` | False | Skip log collection |
| `--kube-config` | `kube_config` | ~/.kube/config | Kubeconfig path |
| `--kube-context` | `kube_context` | current | K8s context name |

## Testing

```bash
# Run all 170 unit tests
cd azure-cli-extensions/src/workload-orchestration
python -m pytest azext_workload_orchestration/tests/test_support_bundle.py -v

# Run specific test class
python -m pytest ... -k "TestHealthSummary"

# Run with coverage
python -m pytest ... --cov=azext_workload_orchestration.support
```

Test file: `tests/test_support_bundle.py` (~2100 lines, 170 tests)

Tests mock the kubernetes client — no live cluster needed for unit tests.
