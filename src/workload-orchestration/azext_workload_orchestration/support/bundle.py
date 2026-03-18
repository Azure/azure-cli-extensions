# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines,too-many-statements,too-many-branches
# pylint: disable=too-many-locals,too-many-arguments,too-many-positional-arguments
# pylint: disable=broad-exception-caught,consider-using-f-string
# pylint: disable=import-outside-toplevel,raise-missing-from
# pylint: disable=unused-argument,unspecified-encoding

"""Main orchestration for the support bundle command."""

import os
import time
from datetime import datetime, timezone

from knack.log import get_logger

from azext_workload_orchestration.support.consts import (
    DEFAULT_NAMESPACES,
    DEFAULT_TAIL_LINES,
    STATUS_PASS,
    STATUS_FAIL,
    STATUS_WARN,
    FOLDER_CLUSTER_INFO,
)
from azext_workload_orchestration.support.utils import (
    get_kubernetes_client,
    create_bundle_directory,
    create_zip_bundle,
    detect_cluster_capabilities,
    write_json,
    format_bytes,
    check_disk_space,
)

logger = get_logger(__name__)


def create_support_bundle(cmd,
                          bundle_name=None,
                          output_dir=None,
                          namespaces=None,
                          tail_lines=None,
                          full_logs=False,
                          skip_checks=False,
                          skip_logs=False,
                          kube_config=None,
                          kube_context=None):
    """Create a support bundle for troubleshooting workload orchestration issues."""
    from azure.cli.core.azclierror import CLIError
    from azext_workload_orchestration.support.collectors import (
        collect_cluster_info,
        collect_namespace_resources,
        collect_cluster_resources,
        collect_container_logs,
        collect_wo_components,
        collect_previous_logs,
        collect_resource_quotas,
        collect_metrics,
        collect_pvcs,
        validate_namespaces,
        collect_network_config,
        collect_all_events,
    )
    from azext_workload_orchestration.support.validators import run_all_checks

    start_time = time.time()
    namespaces = namespaces or DEFAULT_NAMESPACES
    tail = None if full_logs else (tail_lines or DEFAULT_TAIL_LINES)
    errors = []

    # --- Step 1: Initialize K8s clients ---
    _out("")
    _out("Connecting to Kubernetes cluster...")
    clients = get_kubernetes_client(kube_config=kube_config, kube_context=kube_context)

    # Show connection details
    ctx = clients.get("context_info", {})
    _out("  Context:    %s", ctx.get("context", "unknown"))
    _out("  Cluster:    %s", ctx.get("cluster", "unknown"))

    # Verify we can actually reach the cluster
    try:
        version_result = clients["version"].get_code()
        _out("  Connected:  Kubernetes %s", version_result.git_version)
    except Exception as ex:
        raise CLIError(
            f"Cannot reach Kubernetes cluster: {ex}. "
            f"Context '{ctx.get('context', '?')}' may be stale or the "
            "cluster may be unreachable. Try running "
            "'az aks get-credentials' to refresh."
        )

    # --- Step 2: Create bundle directory ---
    try:
        bundle_dir, bundle_name = create_bundle_directory(output_dir, bundle_name)
    except Exception as ex:
        raise CLIError(
            f"Failed to create bundle directory: {ex}. "
            f"Check that the output directory '{output_dir or os.getcwd()}' exists "
            "and you have write permissions."
        )

    # Pre-flight: check disk space
    ok, free = check_disk_space(output_dir or os.getcwd(), 100 * 1024 * 1024)
    if not ok:
        _out("  [WARN] Low disk space (%s free). Bundle may fail.", format_bytes(free))

    # --- Step 3: Collect cluster info ---
    cluster_info = {}
    _out("")
    _out("Collecting cluster information...")
    try:
        cluster_info = collect_cluster_info(clients, bundle_dir)
        _print_cluster_info(cluster_info)
    except Exception as ex:
        err_msg = "Step 3 - Collect cluster info failed: %s" % ex
        errors.append(err_msg)
        _out("  [ERROR] %s", err_msg)

    # --- Step 4: Detect capabilities ---
    capabilities = {}
    try:
        capabilities = detect_cluster_capabilities(clients)
        write_json(
            os.path.join(bundle_dir, FOLDER_CLUSTER_INFO, "capabilities.json"),
            capabilities,
        )
        _print_capabilities(capabilities)
    except Exception as ex:
        err_msg = "Step 4 - Detect capabilities failed: %s" % ex
        errors.append(err_msg)
        _out("  [ERROR] %s", err_msg)

    # --- Step 4b: Collect cluster-wide events ---
    try:
        all_events = collect_all_events(clients, bundle_dir)
        if all_events:
            warning_count = sum(1 for e in all_events if e["type"] == "Warning")
            _out("  Events:   %d total (%d warnings)", len(all_events), warning_count)
    except Exception as ex:
        err_msg = "Step 4b - Collect cluster events failed: %s" % ex
        errors.append(err_msg)
        _out("  [ERROR] %s", err_msg)

    # --- Step 5: Run prerequisite checks ---
    check_results = []
    if not skip_checks:
        _out("")
        _out("Running prerequisite checks...")
        _out("-" * 58)
        try:
            check_results = run_all_checks(clients, bundle_dir, cluster_info, capabilities)
            _print_check_results(check_results)
        except Exception as ex:
            err_msg = "Step 5 - Prerequisite checks failed: %s" % ex
            errors.append(err_msg)
            _out("  [ERROR] %s", err_msg)

    # --- Step 6: Collect cluster-scoped resources ---
    _out("")
    _out("Collecting resources...")
    try:
        cluster_res = collect_cluster_resources(clients, bundle_dir)
        sc_count = len(cluster_res.get("storage_classes", []))
        wh_count = len(cluster_res.get("validating_webhooks", [])) + len(cluster_res.get("mutating_webhooks", []))
        crd_count = len(cluster_res.get("crds", []))
        _out("  Cluster-scoped: %d StorageClasses, %d webhooks, %d CRDs", sc_count, wh_count, crd_count)
    except Exception as ex:
        err_msg = "Step 6 - Collect cluster-scoped resources failed: %s" % ex
        errors.append(err_msg)
        _out("  [ERROR] %s", err_msg)

    # --- Step 6b: Validate namespaces exist ---
    skipped_ns = []
    try:
        namespaces, skipped_ns = validate_namespaces(clients, namespaces)
        if skipped_ns:
            for ns, reason in skipped_ns:
                _out("  [SKIP] Namespace '%s': %s", ns, reason)
        if not namespaces:
            _out("  [WARN] No valid namespaces to collect resources from")
    except Exception as ex:
        err_msg = "Step 6b - Namespace validation failed: %s" % ex
        errors.append(err_msg)
        _out("  [ERROR] %s (proceeding with original list)", err_msg)

    # --- Step 7: Collect per-namespace resources ---
    for ns in namespaces:
        try:
            ns_res = collect_namespace_resources(clients, bundle_dir, ns)
            collect_resource_quotas(clients, bundle_dir, ns)
            collect_pvcs(clients, bundle_dir, ns)
            pod_count = len(ns_res.get("pods", []))
            dep_count = len(ns_res.get("deployments", []))
            svc_count = len(ns_res.get("services", []))
            job_count = len(ns_res.get("jobs", []))
            parts = ["%d pods" % pod_count, "%d deployments" % dep_count,
                     "%d services" % svc_count]
            if job_count:
                parts.append("%d jobs" % job_count)
            rs_count = len(ns_res.get("replicasets", []))
            if rs_count:
                parts.append("%d replicasets" % rs_count)
            _out("  %s: %s", ns, ", ".join(parts))
        except Exception as ex:
            err_msg = "Step 7 - Collect namespace '%s' resources failed: %s" % (ns, ex)
            errors.append(err_msg)
            _out("  [ERROR] %s", err_msg)

    # --- Step 8: Collect WO-specific components ---
    try:
        wo_res = collect_wo_components(clients, bundle_dir, capabilities)
        if wo_res:
            parts = []
            if "symphony_targets" in wo_res:
                parts.append("%d Symphony targets" % len(wo_res["symphony_targets"]))
            if "cluster_issuers" in wo_res:
                parts.append("%d ClusterIssuers" % len(wo_res["cluster_issuers"]))
            if "gatekeeper_templates" in wo_res:
                parts.append("%d Gatekeeper templates" % len(wo_res["gatekeeper_templates"]))
            if parts:
                _out("  WO components: %s", ", ".join(parts))
    except Exception as ex:
        err_msg = "Step 8 - Collect WO components failed: %s" % ex
        errors.append(err_msg)
        _out("  [ERROR] %s", err_msg)

    # --- Step 8b: Collect metrics ---
    try:
        metrics = collect_metrics(clients, bundle_dir, capabilities)
        if metrics:
            nm = len(metrics.get("node_metrics", []))
            pm = len(metrics.get("wo_pod_metrics", []))
            _out("  Metrics: %d node(s), %d WO pod(s)", nm, pm)
    except Exception as ex:
        err_msg = "Step 8b - Collect metrics failed: %s" % ex
        errors.append(err_msg)
        _out("  [ERROR] %s", err_msg)

    # --- Step 8c: Collect network configuration ---
    try:
        net_info = collect_network_config(clients, bundle_dir)
        if net_info:
            parts = []
            if net_info.get("kube_proxy_config"):
                parts.append("kube-proxy config")
            ep_count = len(net_info.get("endpoint_slices", []))
            if ep_count:
                parts.append("%d endpoint slices" % ep_count)
            svc_count = len(net_info.get("external_services", []))
            if svc_count:
                parts.append("%d external services" % svc_count)
            if parts:
                _out("  Network: %s", ", ".join(parts))
    except Exception as ex:
        err_msg = "Step 8c - Collect network config failed: %s" % ex
        errors.append(err_msg)
        _out("  [ERROR] %s", err_msg)

    # --- Step 9: Collect container logs ---
    total_logs = 0
    total_prev = 0
    if not skip_logs:
        _out("")
        _out("Collecting container logs%s...",
             "" if full_logs else " (tail=%d lines)" % tail)
        for ns in namespaces:
            try:
                count = collect_container_logs(clients, bundle_dir, ns, tail_lines=tail)
                total_logs += count
                prev = collect_previous_logs(clients, bundle_dir, ns, tail_lines=tail)
                total_prev += prev
                extra = " + %d previous" % prev if prev else ""
                _out("  %s: %d logs%s", ns, count, extra)
            except Exception as ex:
                err_msg = "Step 9 - Collect logs for namespace '%s' failed: %s" % (ns, ex)
                errors.append(err_msg)
                _out("  [ERROR] %s", err_msg)

    # --- Step 10: Write bundle metadata ---
    elapsed = time.time() - start_time
    health_summary = _compute_health_summary(check_results, errors)
    metadata = {
        "bundle_name": bundle_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "collection_time_seconds": round(elapsed, 1),
        "health_summary": health_summary,
        "namespaces_collected": namespaces,
        "namespaces_skipped": [{"name": ns, "reason": r} for ns, r in skipped_ns] if skipped_ns else None,
        "tail_lines": tail,
        "full_logs": full_logs,
        "skip_checks": skip_checks,
        "skip_logs": skip_logs,
        "total_logs_collected": total_logs,
        "total_previous_logs": total_prev,
        "check_count": len(check_results),
        "capabilities": capabilities,
        "cluster_version": cluster_info.get("server_version", {}).get("git_version", "unknown"),
        "node_count": cluster_info.get("node_count", 0),
        "errors": errors if errors else None,
    }
    write_json(os.path.join(bundle_dir, "metadata.json"), metadata)

    # --- Step 10b: Write checks summary ---
    if check_results:
        from azext_workload_orchestration.support.consts import FOLDER_CHECKS
        checks_summary = {
            "total": len(check_results),
            "passed": sum(1 for c in check_results if c.get("status") == STATUS_PASS),
            "failed": sum(1 for c in check_results if c.get("status") == STATUS_FAIL),
            "warned": sum(1 for c in check_results if c.get("status") == STATUS_WARN),
            "skipped": sum(1 for c in check_results if c.get("status") == "SKIP"),
            "errored": sum(1 for c in check_results if c.get("status") == "ERROR"),
            "checks": [
                {
                    "name": c.get("check_name", "unknown"),
                    "category": c.get("category", "unknown"),
                    "status": c.get("status", "UNKNOWN"),
                    "message": c.get("message", ""),
                }
                for c in check_results
            ],
        }
        write_json(os.path.join(bundle_dir, FOLDER_CHECKS, "summary.json"), checks_summary)

    # --- Step 10c: Write human-readable summary ---
    _write_summary_md(bundle_dir, bundle_name, cluster_info, capabilities,
                      check_results, namespaces, total_logs, total_prev, errors)

    # --- Step 11: Create zip ---
    zip_path = create_zip_bundle(bundle_dir, bundle_name, output_dir)

    try:
        zip_size = os.path.getsize(zip_path)
    except OSError as ex:
        err_msg = "Failed to read zip file size: %s" % ex
        errors.append(err_msg)
        _out("  [ERROR] %s", err_msg)
        zip_size = 0

    # --- Final summary ---
    passed = sum(1 for c in check_results if c.get("status") == STATUS_PASS)
    failed = sum(1 for c in check_results if c.get("status") == STATUS_FAIL)
    warned = sum(1 for c in check_results if c.get("status") == STATUS_WARN)

    _out("")
    _out("=" * 58)
    if errors:
        _out("  Support bundle created with %d error(s)", len(errors))
    else:
        _out("  Support bundle created successfully!")
    _out("")
    _out("  File:   %s", zip_path)
    _out("  Size:   %s", format_bytes(zip_size))
    _out("  Time:   %.1fs", elapsed)
    _out("")
    if check_results:
        _out("  Checks: %d passed, %d failed, %d warnings", passed, failed, warned)
    if not skip_logs:
        log_msg = "  Logs:   %d container logs" % total_logs
        if total_prev:
            log_msg += " + %d previous" % total_prev
        _out(log_msg)
    if errors:
        _out("")
        _out("  Errors:")
        for err in errors:
            _out("    - %s", err)
    _out("=" * 58)
    _out("")

    return {
        "bundle_path": zip_path,
        "bundle_size": zip_size,
        "bundle_size_human": format_bytes(zip_size),
        "collection_time_seconds": round(elapsed, 1),
        "logs_collected": total_logs,
        "previous_logs_collected": total_prev,
        "checks_run": len(check_results),
        "checks_passed": passed,
        "checks_failed": failed,
        "checks_warned": warned,
        "errors": errors if errors else None,
    }


def _compute_health_summary(check_results, errors):
    """Compute a health summary from check results.

    Returns a dict with check counts and collection error count.
    """
    if not check_results:
        return {
            "checks_total": 0,
            "checks_passed": 0,
            "checks_failed": 0,
            "checks_warned": 0,
            "collection_errors": len(errors) if errors else 0,
        }

    return {
        "checks_total": len(check_results),
        "checks_passed": sum(1 for c in check_results if c.get("status") == STATUS_PASS),
        "checks_failed": sum(1 for c in check_results if c.get("status") == STATUS_FAIL),
        "checks_warned": sum(1 for c in check_results if c.get("status") == STATUS_WARN),
        "collection_errors": len(errors) if errors else 0,
    }


def _append_namespace_resources(bundle_dir, namespaces, lines):
    """Append per-namespace resource counts to summary lines."""
    import json
    for ns in namespaces:
        res_file = os.path.join(bundle_dir, "resources", ns, "resources.json")
        if not os.path.exists(res_file):
            continue
        try:
            with open(res_file, "r") as f:
                res_data = json.load(f)
            parts = [
                f"{len(items)} {key}"
                for key, items in res_data.items()
                if isinstance(items, list) and items
            ]
            if parts:
                lines.append(f"**{ns}:** {', '.join(parts)}")
                lines.append("")
        except Exception:  # pylint: disable=broad-exception-caught
            pass


def _append_wo_components(bundle_dir, lines):
    """Append WO component details to summary lines."""
    import json
    wo_file = os.path.join(bundle_dir, "resources", "cluster", "wo-components.json")
    if not os.path.exists(wo_file):
        return
    try:
        with open(wo_file, "r") as f:
            wo_data = json.load(f)
        if not wo_data:
            return
        lines.append("### WO Components")
        lines.append("")
        for key, items in wo_data.items():
            if not isinstance(items, list):
                continue
            label = key.replace("_", " ").title()
            lines.append(f"- **{label}:** {len(items)}")
            for item in items:
                name = item.get("name", "?")
                _status = item.get("status", item.get("ready", "?"))
                lines.append(f"  - `{name}` — {_status}")
        lines.append("")
    except Exception:  # pylint: disable=broad-exception-caught
        pass


def _write_summary_md(bundle_dir, bundle_name, cluster_info, capabilities,
                      check_results, namespaces, total_logs, total_prev, errors):
    # pylint: disable=too-many-branches
    """Write a comprehensive SUMMARY.md at the bundle root.

    This is the single file a DRI opens first — it summarizes everything
    in the bundle: cluster state, check results, collected resources, errors.
    """
    from azext_workload_orchestration.support.utils import write_text

    lines = []
    lines.append("# WO Support Bundle — Summary Report")
    lines.append("")

    sv = cluster_info.get("server_version", {})
    _ctx_name = cluster_info.get("context", "unknown")  # noqa: F841
    lines.append("## Cluster Overview")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|-------|-------|")
    lines.append(f"| **Bundle** | `{bundle_name}` |")
    lines.append(f"| **Kubernetes Version** | {sv.get('git_version', 'unknown')} |")
    lines.append(f"| **Platform** | {sv.get('platform', 'unknown')} |")
    lines.append(f"| **Node Count** | {cluster_info.get('node_count', 0)} |")
    lines.append(f"| **Namespace Count** | {len(cluster_info.get('namespaces', []))} |")
    lines.append(f"| **Namespaces Collected** | {', '.join(namespaces)} |")

    # Detected capabilities
    detected = [k.replace("has_", "") for k, v in capabilities.items() if v]
    not_detected = [k.replace("has_", "") for k, v in capabilities.items() if not v]
    lines.append(f"| **Components Detected** | {', '.join(detected) if detected else 'none'} |")
    if not_detected:
        lines.append(f"| **Not Detected** | {', '.join(not_detected)} |")
    lines.append("")

    # Nodes
    nodes = cluster_info.get("nodes", [])
    if nodes:
        lines.append("## Nodes")
        lines.append("")
        lines.append("| Name | Ready | Roles | CPU | Memory | Runtime | Kubelet |")
        lines.append("|------|-------|-------|-----|--------|---------|---------|")
        for n in nodes:
            ready = "✅ Yes" if n.get("ready") == "True" else "❌ No"
            roles = ", ".join(n.get("roles", ["<none>"]))
            lines.append(
                f"| {n['name']} | {ready} | {roles} "
                f"| {n.get('allocatable_cpu', '?')} "
                f"| {n.get('allocatable_memory', '?')} "
                f"| {n.get('container_runtime', '?')} "
                f"| {n.get('kubelet_version', '?')} |"
            )

        # Node conditions (pressure, etc.)
        has_issues = False
        for n in nodes:
            conditions = n.get("conditions", {})
            for cond, val in conditions.items():
                if cond != "Ready" and val == "True":
                    if not has_issues:
                        lines.append("")
                        lines.append("### ⚠️ Node Conditions")
                        lines.append("")
                        has_issues = True
                    lines.append(f"- **{n['name']}**: {cond} = True")

        # Taints
        tainted = [n for n in nodes if n.get("taints")]
        if tainted:
            lines.append("")
            lines.append("### Node Taints")
            lines.append("")
            for n in tainted:
                for t in n["taints"]:
                    lines.append(
                        f"- **{n['name']}**: `{t.get('key', '?')}="
                        f"{t.get('value', '')}:{t.get('effect', '?')}`"
                    )
        lines.append("")

    # Checks — the main section
    if check_results:
        passed = sum(1 for c in check_results if c.get("status") == STATUS_PASS)
        failed = sum(1 for c in check_results if c.get("status") == STATUS_FAIL)
        warned = sum(1 for c in check_results if c.get("status") == STATUS_WARN)

        lines.append("## Prerequisite Checks")
        lines.append("")
        lines.append(f"> **{passed} passed, {failed} failed, {warned} warnings** "
                     f"(out of {len(check_results)} total)")
        lines.append("")

        # Failed checks first (most important)
        failed_checks = [c for c in check_results if c.get("status") == STATUS_FAIL]
        if failed_checks:
            lines.append("### ❌ Failed Checks (Action Required)")
            lines.append("")
            for c in failed_checks:
                lines.append(f"- **{c.get('check_name', '?')}** ({c.get('category', '?')}): {c.get('message', '')}")
            lines.append("")

        # Warnings
        warn_checks = [c for c in check_results if c.get("status") == STATUS_WARN]
        if warn_checks:
            lines.append("### ⚠️ Warnings")
            lines.append("")
            for c in warn_checks:
                lines.append(f"- **{c.get('check_name', '?')}** ({c.get('category', '?')}): {c.get('message', '')}")
            lines.append("")

        # Full table
        lines.append("### All Checks")
        lines.append("")
        lines.append("| Status | Check | Category | Details |")
        lines.append("|--------|-------|----------|---------|")

        status_icons = {
            STATUS_PASS: "✅ PASS",
            STATUS_FAIL: "❌ FAIL",
            STATUS_WARN: "⚠️ WARN",
            "SKIP": "⏭️ SKIP",
            "ERROR": "💥 ERROR",
        }
        for c in check_results:
            icon = status_icons.get(c.get("status"), c.get("status", "?"))
            name = c.get("check_name", "unknown")
            cat = c.get("category", "")
            msg = c.get("message", "").replace("|", "\\|")
            lines.append(f"| {icon} | {name} | {cat} | {msg} |")
        lines.append("")

    # Data collected
    lines.append("## Data Collected")
    lines.append("")
    lines.append("| Item | Count |")
    lines.append("|------|-------|")
    lines.append(f"| Container logs | {total_logs} |")
    if total_prev:
        lines.append(f"| Previous logs (crash-looping pods) | {total_prev} |")
    lines.append(f"| Namespaces collected | {len(namespaces)} |")
    lines.append(f"| Prerequisite checks | {len(check_results)} |")
    lines.append("")

    # Per-namespace resource counts (read from collected files)
    lines.append("### Resources Per Namespace")
    lines.append("")
    _append_namespace_resources(bundle_dir, namespaces, lines)

    # WO components
    _append_wo_components(bundle_dir, lines)

    # Errors
    if errors:
        lines.append("## ⚠️ Collection Errors")
        lines.append("")
        lines.append("The following errors occurred during bundle collection. "
                     "The bundle was still generated but may be missing some data.")
        lines.append("")
        for err in errors:
            lines.append(f"- {err}")
        lines.append("")

    # Bundle contents guide
    lines.append("## How to Read This Bundle")
    lines.append("")
    lines.append("| File/Folder | What's Inside |")
    lines.append("|-------------|---------------|")
    lines.append("| 📄 `SUMMARY.md` | This file — start here |")
    lines.append("| 📄 `metadata.json` | Bundle parameters, timestamps, capabilities |")
    lines.append("| 📁 `checks/` | Individual check results (JSON) + `summary.json` |")
    lines.append("| 📁 `cluster-info/` | K8s version, node details, namespace list, metrics |")
    lines.append("| 📁 `resources/` | Per-namespace resource descriptions, cluster-scoped resources, network config |")
    lines.append("| 📁 `logs/` | Container logs organized by `namespace/pod--container.log` |")
    lines.append("")
    lines.append("### Quick Troubleshooting")
    lines.append("")
    lines.append("1. **Check failed?** → Look at the ❌ Failed Checks section above")
    lines.append("2. **Pod crashing?** → Check `logs/<namespace>/<pod>--<container>--previous.log`")
    lines.append("3. **WO not working?** → Check `resources/wo-components.json` and `logs/workloadorchestration/`")
    lines.append("4. **Network issues?** → Check `resources/network-config.json`")
    lines.append("5. **Storage issues?** → Check `resources/cluster-resources.json` (storage_classes, csi_drivers)")
    lines.append("")

    write_text(os.path.join(bundle_dir, "SUMMARY.md"), "\n".join(lines))


def _out(msg, *args):
    """Print a line to console via logger.warning (az CLI convention)."""
    if args:
        logger.warning(msg, *args)
    else:
        logger.warning(msg)


def _print_cluster_info(cluster_info):
    """Print cluster overview to console."""
    sv = cluster_info.get("server_version", {})
    version = sv.get("git_version", "unknown")
    node_count = cluster_info.get("node_count", 0)
    ns_count = len(cluster_info.get("namespaces", []))

    _out("")
    _out("  Cluster:    Kubernetes %s", version)
    _out("  Nodes:      %d", node_count)
    _out("  Namespaces: %d", ns_count)

    # Show node details
    for node in cluster_info.get("nodes", []):
        cpu = node.get("allocatable_cpu", "?")
        mem = node.get("allocatable_memory", "?")
        ready = node.get("ready", "?")
        roles = ", ".join(node.get("roles", ["<none>"]))
        _status = "Ready" if ready == "True" else "NOT READY"  # noqa: F841
        _out("  %s  %s  [%s]  cpu=%s  mem=%s",
             "  " if ready == "True" else "! ", node["name"], roles, cpu, mem)


def _print_capabilities(capabilities):
    """Print detected capabilities."""
    detected = [k.replace("has_", "") for k, v in capabilities.items() if v]
    if detected:
        _out("  Detected:   %s", ", ".join(detected))


def _print_check_results(check_results):
    """Print each check result with status icon."""
    status_icons = {
        STATUS_PASS: "[PASS]",
        STATUS_FAIL: "[FAIL]",
        STATUS_WARN: "[WARN]",
        "SKIP": "[SKIP]",
        "ERROR": "[ERR!]",
    }

    for c in check_results:
        icon = status_icons.get(c.get("status"), "[????]")
        name = c.get("check_name", "unknown")
        msg = c.get("message", "")
        _out("  %s  %-25s  %s", icon, name, msg)

    passed = sum(1 for c in check_results if c.get("status") == STATUS_PASS)
    failed = sum(1 for c in check_results if c.get("status") == STATUS_FAIL)
    warned = sum(1 for c in check_results if c.get("status") == STATUS_WARN)
    _out("-" * 58)
    _out("  %d passed, %d failed, %d warnings", passed, failed, warned)
