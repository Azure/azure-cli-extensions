# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

import os
import time
from datetime import datetime, timezone

from knack.log import get_logger

from azext_workload_orchestration.support.consts import (
    DEFAULT_NAMESPACES,
    DEFAULT_TAIL_LINES,
    DEFAULT_TIMEOUT_SECONDS,
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
            "health_status": health_summary.get("overall_status", "UNKNOWN"),
            "health_score": health_summary.get("health_score", 0),
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
    if health_summary:
        _out("  Health: %s (score: %d/100)", health_summary["overall_status"], health_summary["health_score"])
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
    """Compute an overall health summary from check results.

    Returns a dict with overall_status (HEALTHY/DEGRADED/CRITICAL/UNKNOWN),
    health_score (0-100), and category breakdown.
    """
    if not check_results:
        return {
            "overall_status": "UNKNOWN",
            "health_score": 0,
            "reason": "No checks were run",
        }

    total = len(check_results)
    passed = sum(1 for c in check_results if c.get("status") == STATUS_PASS)
    failed = sum(1 for c in check_results if c.get("status") == STATUS_FAIL)
    warned = sum(1 for c in check_results if c.get("status") == STATUS_WARN)

    # Health score: PASS=100%, WARN=50%, FAIL=0%
    score = int(round(((passed * 100) + (warned * 50)) / total)) if total else 0

    if failed == 0 and warned == 0:
        status = "HEALTHY"
    elif failed == 0 and warned > 0:
        status = "DEGRADED"
    elif failed <= 2:
        status = "DEGRADED"
    else:
        status = "CRITICAL"

    # Bump to CRITICAL if there were collection errors
    if errors and status != "CRITICAL":
        status = "DEGRADED"

    return {
        "overall_status": status,
        "health_score": score,
        "checks_total": total,
        "checks_passed": passed,
        "checks_failed": failed,
        "checks_warned": warned,
        "collection_errors": len(errors) if errors else 0,
    }


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
        status = "Ready" if ready == "True" else "NOT READY"
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
