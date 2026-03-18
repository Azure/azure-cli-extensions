# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument,import-outside-toplevel,too-many-locals

"""Prerequisite validators for the workload-orchestration support bundle feature.

Each check function has the same signature (clients, bundle_dir, cluster_info, capabilities)
for consistency. Not all checks use all arguments.
"""

from knack.log import get_logger

from azext_workload_orchestration.support.consts import (
    CATEGORY_CLUSTER_INFO,
    CATEGORY_NODE_HEALTH,
    CATEGORY_DNS_HEALTH,
    CATEGORY_STORAGE,
    CATEGORY_REGISTRY_ACCESS,
    CATEGORY_CERT_MANAGER,
    CATEGORY_WO_COMPONENTS,
    CATEGORY_ADMISSION_CONTROLLERS,
    CATEGORY_CONNECTIVITY,
    MIN_CPU_CORES,
    MIN_MEMORY_GI,
    MIN_NODE_COUNT_PROD,
    DNS_SERVICE_LABEL,
    WO_NAMESPACE,
    CERT_MANAGER_NAMESPACE,
    PROTECTED_NAMESPACES,
    STATUS_PASS,
    STATUS_FAIL,
    STATUS_WARN,
    STATUS_SKIP,
    STATUS_ERROR,
    PSA_LABEL_PREFIX,
)
from azext_workload_orchestration.support.utils import (
    safe_api_call,
    write_check_result,
    parse_cpu,
    parse_memory_gi,
)

logger = get_logger(__name__)


def run_all_checks(clients, bundle_dir, cluster_info, capabilities):
    """Run all prerequisite validation checks.

    Returns a list of check result dicts.
    """
    results = []

    checks = [
        (_check_k8s_version, "Kubernetes version compatibility"),
        (_check_node_readiness, "Node readiness"),
        (_check_node_capacity, "Node capacity (CPU/memory)"),
        (_check_cluster_resources, "Cluster-wide resource availability"),
        (_check_dns_health, "CoreDNS health"),
        (_check_dns_resolution, "DNS resolution"),
        (_check_default_storage_class, "Default StorageClass"),
        (_check_csi_drivers, "CSI drivers"),
        (_check_cert_manager, "cert-manager installation"),
        (_check_arc_dependencies, "Azure Arc dependencies"),
        (_check_wo_namespace, "WO namespace exists"),
        (_check_protected_namespace, "Protected namespace check"),
        (_check_wo_pods, "WO pods running"),
        (_check_wo_services_deployments, "WO services and deployments"),
        (_check_wo_webhooks, "WO webhook health"),
        (_check_admission_controllers, "Admission controller detection"),
        (_check_psa_labels, "Pod Security Admission labels"),
        (_check_resource_quotas, "Resource quotas on WO namespace"),
        (_check_image_pull_secrets, "Image pull secrets"),
        (_check_proxy_settings, "Proxy configuration"),
    ]

    for check_fn, description in checks:
        try:
            result = check_fn(clients, bundle_dir, cluster_info, capabilities)
            results.append(result)
            status_icon = {
                STATUS_PASS: "✓", STATUS_FAIL: "✗", STATUS_WARN: "⚠",
                STATUS_SKIP: "—", STATUS_ERROR: "!"
            }.get(result["status"], "?")
            logger.info("  %s %s: %s", status_icon, description, result["message"])
        except Exception as ex:  # pylint: disable=broad-exception-caught
            err_result = write_check_result(
                bundle_dir, "error", description.replace(" ", "-").lower(),
                STATUS_ERROR, f"Check crashed: {ex}"
            )
            results.append(err_result)
            logger.warning("  ! %s: crashed (%s)", description, ex)

    return results


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def _check_k8s_version(clients, bundle_dir, cluster_info, capabilities):
    """Check Kubernetes version is in supported range."""
    version_info = cluster_info.get("server_version", {})
    git_version = version_info.get("git_version", "unknown")

    try:
        major = int(version_info.get("major", "0").rstrip("+"))
        minor = int(version_info.get("minor", "0").rstrip("+"))
    except ValueError:
        return write_check_result(
            bundle_dir, CATEGORY_CLUSTER_INFO, "k8s-version",
            STATUS_WARN, f"Could not parse version: {git_version}"
        )

    # WO supports K8s 1.24+
    if major == 1 and minor >= 24:
        return write_check_result(
            bundle_dir, CATEGORY_CLUSTER_INFO, "k8s-version",
            STATUS_PASS, f"Kubernetes {git_version} is supported (>=1.24)"
        )

    return write_check_result(
        bundle_dir, CATEGORY_CLUSTER_INFO, "k8s-version",
        STATUS_FAIL, f"Kubernetes {git_version} may not be supported (require >=1.24)",
        details={"major": major, "minor": minor}
    )


def _check_node_readiness(clients, bundle_dir, cluster_info, capabilities):
    """Check all nodes are Ready with no pressure conditions."""
    nodes = cluster_info.get("nodes") or []
    if not nodes:
        return write_check_result(
            bundle_dir, CATEGORY_NODE_HEALTH, "node-readiness",
            STATUS_FAIL, "No nodes found in cluster"
        )

    not_ready = [n["name"] for n in nodes if n.get("ready") != "True"]
    pressure_nodes = []
    for n in nodes:
        conditions = n.get("conditions", {})
        pressures = [
            ctype for ctype in ("DiskPressure", "MemoryPressure", "PIDPressure")
            if conditions.get(ctype) == "True"
        ]
        if pressures:
            pressure_nodes.append({"node": n["name"], "pressures": pressures})

    if not_ready:
        return write_check_result(
            bundle_dir, CATEGORY_NODE_HEALTH, "node-readiness",
            STATUS_FAIL, f"{len(not_ready)} node(s) not Ready: {', '.join(not_ready)}",
            details={"not_ready": not_ready, "pressure_nodes": pressure_nodes}
        )

    if pressure_nodes:
        return write_check_result(
            bundle_dir, CATEGORY_NODE_HEALTH, "node-readiness",
            STATUS_WARN, f"{len(pressure_nodes)} node(s) have pressure conditions",
            details={"pressure_nodes": pressure_nodes}
        )

    node_count = len(nodes)
    msg = f"All {node_count} node(s) Ready, no pressure conditions"
    if node_count < MIN_NODE_COUNT_PROD:
        msg += f" (note: {node_count} nodes, recommend {MIN_NODE_COUNT_PROD}+ for production)"

    return write_check_result(
        bundle_dir, CATEGORY_NODE_HEALTH, "node-readiness",
        STATUS_PASS, msg
    )


def _check_node_capacity(clients, bundle_dir, cluster_info, capabilities):
    """Check nodes have minimum CPU and memory."""
    nodes = cluster_info.get("nodes") or []
    if not nodes:
        return write_check_result(
            bundle_dir, CATEGORY_NODE_HEALTH, "node-capacity",
            STATUS_SKIP, "No nodes to check"
        )

    low_cpu = []
    low_mem = []
    for n in nodes:
        cpu = parse_cpu(n.get("allocatable_cpu", "0"))
        mem = parse_memory_gi(n.get("allocatable_memory", "0"))
        if cpu < MIN_CPU_CORES:
            low_cpu.append(f"{n['name']} ({cpu:.1f} cores)")
        if mem < MIN_MEMORY_GI:
            low_mem.append(f"{n['name']} ({mem:.1f} Gi)")

    issues = []
    if low_cpu:
        issues.append(f"Low CPU: {', '.join(low_cpu)} (min {MIN_CPU_CORES} cores)")
    if low_mem:
        issues.append(f"Low memory: {', '.join(low_mem)} (min {MIN_MEMORY_GI} Gi)")

    if issues:
        return write_check_result(
            bundle_dir, CATEGORY_NODE_HEALTH, "node-capacity",
            STATUS_WARN, "; ".join(issues),
            details={"low_cpu": low_cpu, "low_mem": low_mem}
        )

    return write_check_result(
        bundle_dir, CATEGORY_NODE_HEALTH, "node-capacity",
        STATUS_PASS, f"All {len(nodes)} nodes meet minimum requirements (CPU>={MIN_CPU_CORES}, Mem>={MIN_MEMORY_GI}Gi)"
    )


def _check_dns_health(clients, bundle_dir, cluster_info, capabilities):
    """Check CoreDNS pods are running and DNS service exists."""
    core = clients["core_v1"]

    # Find DNS pods by label (works across most distros)
    result, err = safe_api_call(
        core.list_namespaced_pod, "kube-system",
        label_selector=DNS_SERVICE_LABEL,
        description="list DNS pods",
    )

    if err:
        return write_check_result(
            bundle_dir, CATEGORY_DNS_HEALTH, "dns-pods",
            STATUS_WARN, f"Could not check DNS pods: {err}"
        )

    dns_pods = result.items if result else []

    if not dns_pods:
        # Fallback: try searching by name pattern (OpenShift, RKE2, etc.)
        result, err = safe_api_call(
            core.list_namespaced_pod, "kube-system",
            description="list all kube-system pods for DNS fallback",
        )
        if result:
            dns_pods = [
                p for p in result.items
                if "dns" in p.metadata.name.lower()
                or "coredns" in p.metadata.name.lower()
            ]

    if not dns_pods:
        return write_check_result(
            bundle_dir, CATEGORY_DNS_HEALTH, "dns-pods",
            STATUS_FAIL, "No DNS pods found in kube-system (checked label k8s-app=kube-dns and name pattern)"
        )

    running = [p for p in dns_pods if p.status.phase == "Running"]
    if len(running) < len(dns_pods):
        not_running = [p.metadata.name for p in dns_pods if p.status.phase != "Running"]
        return write_check_result(
            bundle_dir, CATEGORY_DNS_HEALTH, "dns-pods",
            STATUS_WARN, f"{len(running)}/{len(dns_pods)} DNS pods Running (not running: {', '.join(not_running)})"
        )

    return write_check_result(
        bundle_dir, CATEGORY_DNS_HEALTH, "dns-pods",
        STATUS_PASS, f"{len(running)} DNS pod(s) Running"
    )


def _check_default_storage_class(clients, bundle_dir, cluster_info, capabilities):
    """Check a default StorageClass exists."""
    storage = clients["storage_v1"]
    result, err = safe_api_call(storage.list_storage_class, description="list storage classes")
    if err:
        return write_check_result(
            bundle_dir, CATEGORY_STORAGE, "default-storage-class",
            STATUS_WARN, f"Could not list StorageClasses: {err}"
        )

    from azext_workload_orchestration.support.consts import SC_DEFAULT_ANNOTATION_V1, SC_DEFAULT_ANNOTATION_BETA

    scs = result.items if result else []
    defaults = []
    for sc in scs:
        ann = sc.metadata.annotations or {}
        if ann.get(SC_DEFAULT_ANNOTATION_V1) == "true" or ann.get(SC_DEFAULT_ANNOTATION_BETA) == "true":
            defaults.append(sc.metadata.name)

    if not defaults:
        return write_check_result(
            bundle_dir, CATEGORY_STORAGE, "default-storage-class",
            STATUS_WARN, f"No default StorageClass found ({len(scs)} classes exist)",
            details={"storage_classes": [sc.metadata.name for sc in scs]}
        )

    return write_check_result(
        bundle_dir, CATEGORY_STORAGE, "default-storage-class",
        STATUS_PASS, f"Default StorageClass: {', '.join(defaults)}"
    )


def _check_cert_manager(clients, bundle_dir, cluster_info, capabilities):
    """Check cert-manager is installed and healthy."""
    if not capabilities.get("has_cert_manager"):
        return write_check_result(
            bundle_dir, CATEGORY_CERT_MANAGER, "cert-manager-installed",
            STATUS_FAIL, "cert-manager CRDs not found (cert-manager.io API group missing)"
        )

    core = clients["core_v1"]
    # Check pods in cert-manager namespace
    result, err = safe_api_call(
        core.list_namespaced_pod, CERT_MANAGER_NAMESPACE,
        description="list cert-manager pods",
    )

    if err or not result or not result.items:
        return write_check_result(
            bundle_dir, CATEGORY_CERT_MANAGER, "cert-manager-installed",
            STATUS_WARN, "cert-manager CRDs exist but no pods found in cert-manager namespace"
        )

    pods = result.items
    running = [p for p in pods if p.status.phase == "Running"]

    if len(running) < len(pods):
        return write_check_result(
            bundle_dir, CATEGORY_CERT_MANAGER, "cert-manager-installed",
            STATUS_WARN,
            f"cert-manager: {len(running)}/{len(pods)} pods Running",
            details={"pods": [{"name": p.metadata.name, "phase": p.status.phase} for p in pods]}
        )

    return write_check_result(
        bundle_dir, CATEGORY_CERT_MANAGER, "cert-manager-installed",
        STATUS_PASS, f"cert-manager healthy: {len(running)} pod(s) Running"
    )


# ---------------------------------------------------------------------------
# Azure Arc dependency checks
# ---------------------------------------------------------------------------

ARC_DEPENDENCY_NAMESPACES = ["azure-arc", "azure-extensions"]


def _check_arc_dependencies(clients, bundle_dir, cluster_info, capabilities):
    """Check that Azure Arc prerequisite namespaces and components exist."""
    namespaces = cluster_info.get("namespaces") or []
    ns_names = {ns["name"] for ns in namespaces}

    missing = [ns for ns in ARC_DEPENDENCY_NAMESPACES if ns not in ns_names]
    found = [ns for ns in ARC_DEPENDENCY_NAMESPACES if ns in ns_names]

    if missing and not found:
        return write_check_result(
            bundle_dir, CATEGORY_CONNECTIVITY, "arc-dependencies",
            STATUS_FAIL,
            f"Azure Arc namespaces missing: {', '.join(missing)}. "
            "WO requires an Arc-enabled cluster. Run 'az connectedk8s connect' first.",
        )

    if missing:
        return write_check_result(
            bundle_dir, CATEGORY_CONNECTIVITY, "arc-dependencies",
            STATUS_WARN,
            f"Partial Arc setup: found {', '.join(found)}, "
            f"missing {', '.join(missing)}",
            details={"found": found, "missing": missing},
        )

    # Check azure-arc namespace has healthy pods
    core = clients["core_v1"]
    result, err = safe_api_call(
        core.list_namespaced_pod, "azure-arc",
        description="list pods in azure-arc",
    )
    if err:
        return write_check_result(
            bundle_dir, CATEGORY_CONNECTIVITY, "arc-dependencies",
            STATUS_WARN, f"Arc namespaces exist but could not verify pods: {err}",
        )

    pods = result.items or []
    running = [p for p in pods if p.status.phase == "Running"]
    not_running = [p for p in pods if p.status.phase != "Running"]

    if not_running:
        names = [p.metadata.name for p in not_running[:5]]
        return write_check_result(
            bundle_dir, CATEGORY_CONNECTIVITY, "arc-dependencies",
            STATUS_WARN,
            f"Arc namespaces present, {len(running)} pod(s) Running, "
            f"{len(not_running)} not Running: {', '.join(names)}",
            details={"running": len(running), "not_running_pods": names},
        )

    return write_check_result(
        bundle_dir, CATEGORY_CONNECTIVITY, "arc-dependencies",
        STATUS_PASS,
        f"Azure Arc healthy: namespaces {', '.join(found)} present, "
        f"{len(running)} pod(s) Running",
    )


def _check_wo_namespace(clients, bundle_dir, cluster_info, capabilities):
    """Check the WO namespace exists."""
    namespaces = cluster_info.get("namespaces") or []
    wo_ns = [ns for ns in namespaces if ns["name"] == WO_NAMESPACE]

    if not wo_ns:
        return write_check_result(
            bundle_dir, CATEGORY_WO_COMPONENTS, "wo-namespace",
            STATUS_FAIL, f"Namespace '{WO_NAMESPACE}' not found"
        )

    return write_check_result(
        bundle_dir, CATEGORY_WO_COMPONENTS, "wo-namespace",
        STATUS_PASS, f"Namespace '{WO_NAMESPACE}' exists (status: {wo_ns[0]['status']})"
    )


def _check_wo_pods(clients, bundle_dir, cluster_info, capabilities):
    """Check WO pods are running."""
    core = clients["core_v1"]
    result, err = safe_api_call(
        core.list_namespaced_pod, WO_NAMESPACE,
        description="list WO pods",
    )

    if err:
        return write_check_result(
            bundle_dir, CATEGORY_WO_COMPONENTS, "wo-pods",
            STATUS_WARN, f"Could not list WO pods: {err}"
        )

    pods = result.items if result else []
    if not pods:
        return write_check_result(
            bundle_dir, CATEGORY_WO_COMPONENTS, "wo-pods",
            STATUS_FAIL, f"No pods found in {WO_NAMESPACE}"
        )

    running = [p for p in pods if p.status.phase == "Running"]
    not_running = [
        {"name": p.metadata.name, "phase": p.status.phase}
        for p in pods if p.status.phase != "Running"
    ]

    if not_running:
        return write_check_result(
            bundle_dir, CATEGORY_WO_COMPONENTS, "wo-pods",
            STATUS_WARN,
            f"{len(running)}/{len(pods)} WO pods Running",
            details={"not_running": not_running}
        )

    return write_check_result(
        bundle_dir, CATEGORY_WO_COMPONENTS, "wo-pods",
        STATUS_PASS, f"All {len(running)} WO pods Running"
    )


def _check_wo_services_deployments(clients, bundle_dir, cluster_info, capabilities):
    """Check WO services and deployments are healthy."""
    core = clients["core_v1"]
    apps = clients["apps_v1"]

    issues = []

    # Check deployments
    result, err = safe_api_call(
        apps.list_namespaced_deployment, WO_NAMESPACE,
        description=f"list deployments in {WO_NAMESPACE}",
    )
    if err:
        return write_check_result(
            bundle_dir, CATEGORY_WO_COMPONENTS, "wo-services-deployments",
            STATUS_WARN, f"Could not check WO deployments: {err}"
        )

    deployments = result.items or []
    dep_details = []
    for d in deployments:
        desired = d.spec.replicas or 0
        ready = d.status.ready_replicas or 0
        dep_details.append({
            "name": d.metadata.name,
            "desired": desired,
            "ready": ready,
        })
        if ready < desired:
            issues.append(f"Deployment {d.metadata.name}: {ready}/{desired} ready")

    # Check services
    result, err = safe_api_call(
        core.list_namespaced_service, WO_NAMESPACE,
        description=f"list services in {WO_NAMESPACE}",
    )
    svc_count = len(result.items) if result else 0

    if issues:
        return write_check_result(
            bundle_dir, CATEGORY_WO_COMPONENTS, "wo-services-deployments",
            STATUS_WARN,
            f"{len(deployments)} deployment(s), {svc_count} service(s) — "
            f"issues: {'; '.join(issues)}",
            details={"deployments": dep_details, "services": svc_count, "issues": issues},
        )

    return write_check_result(
        bundle_dir, CATEGORY_WO_COMPONENTS, "wo-services-deployments",
        STATUS_PASS,
        f"{len(deployments)} deployment(s) all healthy, {svc_count} service(s)",
        details={"deployments": dep_details, "services": svc_count},
    )


def _check_wo_webhooks(clients, bundle_dir, cluster_info, capabilities):
    """Check Symphony validating/mutating webhooks are configured."""
    admission = clients["admissionregistration_v1"]

    result, err = safe_api_call(
        admission.list_validating_webhook_configuration,
        description="list validating webhooks for WO check",
    )
    if err:
        return write_check_result(
            bundle_dir, CATEGORY_WO_COMPONENTS, "wo-webhooks",
            STATUS_WARN, f"Could not list webhooks: {err}"
        )

    vwcs = result.items if result else []
    symphony_vwc = [w for w in vwcs if "symphony" in w.metadata.name.lower()]

    if not symphony_vwc:
        return write_check_result(
            bundle_dir, CATEGORY_WO_COMPONENTS, "wo-webhooks",
            STATUS_WARN, "No Symphony validating webhook configurations found"
        )

    total_hooks = sum(len(w.webhooks or []) for w in symphony_vwc)
    fail_hooks = sum(
        1 for w in symphony_vwc for wh in (w.webhooks or []) if wh.failure_policy == "Fail"
    )

    return write_check_result(
        bundle_dir, CATEGORY_WO_COMPONENTS, "wo-webhooks",
        STATUS_PASS,
        f"Symphony webhooks configured: {total_hooks} hooks ({fail_hooks} with failurePolicy=Fail)",
        details={"configs": [w.metadata.name for w in symphony_vwc]}
    )


def _check_admission_controllers(clients, bundle_dir, cluster_info, capabilities):
    """Detect and report admission controllers."""
    detected = []
    if capabilities.get("has_gatekeeper"):
        detected.append("Gatekeeper")
    if capabilities.get("has_kyverno"):
        detected.append("Kyverno")
    if capabilities.get("has_openshift"):
        detected.append("OpenShift SCC")

    if not detected:
        return write_check_result(
            bundle_dir, CATEGORY_ADMISSION_CONTROLLERS, "policy-engines",
            STATUS_PASS, "No additional policy engines detected (Gatekeeper/Kyverno/OpenShift SCC)"
        )

    return write_check_result(
        bundle_dir, CATEGORY_ADMISSION_CONTROLLERS, "policy-engines",
        STATUS_PASS, f"Policy engines detected: {', '.join(detected)}",
        details={"engines": detected}
    )


def _check_psa_labels(clients, bundle_dir, cluster_info, capabilities):
    """Check PSA enforcement labels on WO-relevant namespaces."""
    namespaces = cluster_info.get("namespaces") or []
    enforced = []

    for ns in namespaces:
        if ns["name"] not in (WO_NAMESPACE, CERT_MANAGER_NAMESPACE, "default"):
            continue
        labels = ns.get("labels", {})
        enforce = labels.get(f"{PSA_LABEL_PREFIX}enforce")
        if enforce:
            enforced.append({"namespace": ns["name"], "level": enforce})

    if not enforced:
        return write_check_result(
            bundle_dir, CATEGORY_ADMISSION_CONTROLLERS, "psa-labels",
            STATUS_PASS, "No PSA enforce labels on WO-relevant namespaces"
        )

    restricted = [e for e in enforced if e["level"] == "restricted"]
    if restricted:
        return write_check_result(
            bundle_dir, CATEGORY_ADMISSION_CONTROLLERS, "psa-labels",
            STATUS_WARN,
            f"PSA enforce=restricted on: {', '.join(e['namespace'] for e in restricted)} "
            "(test pods may need explicit securityContext)",
            details={"enforced": enforced}
        )

    return write_check_result(
        bundle_dir, CATEGORY_ADMISSION_CONTROLLERS, "psa-labels",
        STATUS_PASS, f"PSA labels found but not restricted: {enforced}",
        details={"enforced": enforced}
    )


def _check_dns_resolution(clients, bundle_dir, cluster_info, capabilities):
    """Check DNS resolution works for internal and external names (client-side)."""
    import socket

    from azext_workload_orchestration.support.consts import DNS_EXTERNAL_HOST

    results_detail = {}

    # External DNS check (from the client machine running az cli)
    try:
        addr = socket.getaddrinfo(DNS_EXTERNAL_HOST, 443, socket.AF_INET)
        results_detail["external_dns"] = {
            "host": DNS_EXTERNAL_HOST, "resolved": True,
            "addresses": list({a[4][0] for a in addr}),
        }
    except (socket.gaierror, socket.timeout, OSError) as ex:
        results_detail["external_dns"] = {
            "host": DNS_EXTERNAL_HOST, "resolved": False, "error": str(ex),
        }
        return write_check_result(
            bundle_dir, CATEGORY_DNS_HEALTH, "dns-resolution",
            STATUS_WARN,
            f"Cannot resolve {DNS_EXTERNAL_HOST} from client (may be expected in air-gapped environments)",
            details=results_detail,
        )

    return write_check_result(
        bundle_dir, CATEGORY_DNS_HEALTH, "dns-resolution",
        STATUS_PASS,
        f"DNS resolution OK: {DNS_EXTERNAL_HOST} resolves from client",
        details=results_detail,
    )


def _check_resource_quotas(clients, bundle_dir, cluster_info, capabilities):
    """Check if resource quotas exist on the WO namespace that could limit pods."""
    core = clients["core_v1"]

    result, err = safe_api_call(
        core.list_namespaced_resource_quota, WO_NAMESPACE,
        description="list resource quotas on WO namespace",
    )

    if err:
        return write_check_result(
            bundle_dir, CATEGORY_WO_COMPONENTS, "resource-quotas",
            STATUS_SKIP, f"Could not check resource quotas: {err}"
        )

    quotas = result.items if result else []
    if not quotas:
        return write_check_result(
            bundle_dir, CATEGORY_WO_COMPONENTS, "resource-quotas",
            STATUS_PASS, f"No resource quotas on {WO_NAMESPACE} namespace"
        )

    # Check if any quota is near its limit
    warnings = []
    for rq in quotas:
        hard = rq.status.hard or {}
        used = rq.status.used or {}
        for resource, limit_str in hard.items():
            used_str = used.get(resource, "0")
            try:
                limit_val = float(limit_str)
                used_val = float(used_str)
                if limit_val > 0 and used_val / limit_val > 0.8:
                    warnings.append(f"{resource}: {used_str}/{limit_str} ({used_val / limit_val * 100:.0f}%)")
            except (ValueError, ZeroDivisionError):
                pass

    if warnings:
        return write_check_result(
            bundle_dir, CATEGORY_WO_COMPONENTS, "resource-quotas",
            STATUS_WARN,
            f"Resource quotas >80% utilized on {WO_NAMESPACE}: {'; '.join(warnings)}",
            details={"quotas": [rq.metadata.name for rq in quotas], "warnings": warnings}
        )

    return write_check_result(
        bundle_dir, CATEGORY_WO_COMPONENTS, "resource-quotas",
        STATUS_PASS,
        f"{len(quotas)} resource quota(s) on {WO_NAMESPACE}, all within limits"
    )


def _check_cluster_resources(clients, bundle_dir, cluster_info, capabilities):
    """Check cluster-wide aggregate CPU and memory against minimums."""
    nodes = cluster_info.get("nodes") or []
    if not nodes:
        return write_check_result(
            bundle_dir, CATEGORY_NODE_HEALTH, "cluster-resources",
            STATUS_SKIP, "No nodes to check"
        )

    total_cpu = 0.0
    total_mem = 0.0
    for n in nodes:
        total_cpu += parse_cpu(n.get("allocatable_cpu", "0"))
        total_mem += parse_memory_gi(n.get("allocatable_memory", "0"))

    issues = []
    if total_cpu < MIN_CPU_CORES:
        issues.append(f"Total CPU {total_cpu:.1f} cores < {MIN_CPU_CORES} minimum")
    if total_mem < MIN_MEMORY_GI:
        issues.append(f"Total memory {total_mem:.1f}Gi < {MIN_MEMORY_GI}Gi minimum")

    if issues:
        return write_check_result(
            bundle_dir, CATEGORY_NODE_HEALTH, "cluster-resources",
            STATUS_WARN, "; ".join(issues),
            details={"total_cpu": round(total_cpu, 2), "total_memory_gi": round(total_mem, 2)}
        )

    return write_check_result(
        bundle_dir, CATEGORY_NODE_HEALTH, "cluster-resources",
        STATUS_PASS,
        f"Cluster total: {total_cpu:.1f} CPU cores, {total_mem:.1f}Gi memory "
        f"across {len(nodes)} node(s)",
        details={"total_cpu": round(total_cpu, 2), "total_memory_gi": round(total_mem, 2)}
    )


def _check_protected_namespace(clients, bundle_dir, cluster_info, capabilities):
    """Check that the WO namespace is not a protected system namespace."""
    if WO_NAMESPACE in PROTECTED_NAMESPACES or \
       WO_NAMESPACE.startswith("kube-") or \
       WO_NAMESPACE.startswith("azure-"):
        return write_check_result(
            bundle_dir, CATEGORY_WO_COMPONENTS, "protected-namespace",
            STATUS_FAIL,
            f"WO namespace '{WO_NAMESPACE}' is a protected/system namespace",
            details={"protected_namespaces": PROTECTED_NAMESPACES}
        )

    return write_check_result(
        bundle_dir, CATEGORY_WO_COMPONENTS, "protected-namespace",
        STATUS_PASS,
        f"WO namespace '{WO_NAMESPACE}' is not a protected system namespace"
    )


def _check_csi_drivers(clients, bundle_dir, cluster_info, capabilities):
    """Check for installed CSI drivers."""
    storage = clients["storage_v1"]
    result, err = safe_api_call(storage.list_csi_driver, description="list CSI drivers")

    if err:
        return write_check_result(
            bundle_dir, CATEGORY_STORAGE, "csi-drivers",
            STATUS_SKIP, f"Could not list CSI drivers: {err}"
        )

    drivers = result.items if result else []
    if not drivers:
        return write_check_result(
            bundle_dir, CATEGORY_STORAGE, "csi-drivers",
            STATUS_WARN, "No CSI drivers found in cluster"
        )

    driver_names = [d.metadata.name for d in drivers]
    return write_check_result(
        bundle_dir, CATEGORY_STORAGE, "csi-drivers",
        STATUS_PASS, f"{len(drivers)} CSI driver(s): {', '.join(driver_names)}",
        details={"drivers": driver_names}
    )


def _check_image_pull_secrets(clients, bundle_dir, cluster_info, capabilities):
    """Check for image pull secrets across relevant namespaces."""
    core = clients["core_v1"]
    pull_secrets = {}

    for ns in [WO_NAMESPACE, CERT_MANAGER_NAMESPACE]:
        result, _err = safe_api_call(
            core.list_namespaced_secret, ns,
            field_selector="type=kubernetes.io/dockerconfigjson",
            description=f"list pull secrets in {ns}",
        )
        if result and result.items:
            pull_secrets[ns] = [s.metadata.name for s in result.items]

    if pull_secrets:
        parts = [f"{ns}: {', '.join(names)}" for ns, names in pull_secrets.items()]
        return write_check_result(
            bundle_dir, CATEGORY_REGISTRY_ACCESS, "image-pull-secrets",
            STATUS_PASS, f"Image pull secrets found: {'; '.join(parts)}",
            details={"secrets": pull_secrets}
        )

    return write_check_result(
        bundle_dir, CATEGORY_REGISTRY_ACCESS, "image-pull-secrets",
        STATUS_PASS,
        "No image pull secrets in WO namespaces (using default service account credentials)"
    )


def _check_proxy_settings(clients, bundle_dir, cluster_info, capabilities):
    """Check for HTTP proxy configuration in WO pods."""
    core = clients["core_v1"]
    result, err = safe_api_call(
        core.list_namespaced_pod, WO_NAMESPACE,
        description="list WO pods for proxy check",
    )

    if err or not result or not result.items:
        return write_check_result(
            bundle_dir, CATEGORY_WO_COMPONENTS, "proxy-settings",
            STATUS_SKIP, f"Could not check proxy settings: {err or 'no pods found'}"
        )

    proxy_vars = ("HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY",
                  "http_proxy", "https_proxy", "no_proxy")
    pods_with_proxy = []

    for pod in result.items:
        for container in (pod.spec.containers or []):
            for env in (container.env or []):
                if env.name in proxy_vars:
                    pods_with_proxy.append({
                        "pod": pod.metadata.name,
                        "container": container.name,
                        "var": env.name,
                        "value": env.value or "(from ref)",
                    })

    if pods_with_proxy:
        return write_check_result(
            bundle_dir, CATEGORY_WO_COMPONENTS, "proxy-settings",
            STATUS_WARN,
            f"Proxy env vars found in {len(pods_with_proxy)} container(s) — "
            "verify proxy allows access to mcr.microsoft.com",
            details={"proxy_configs": pods_with_proxy}
        )

    return write_check_result(
        bundle_dir, CATEGORY_WO_COMPONENTS, "proxy-settings",
        STATUS_PASS, "No proxy environment variables in WO pods"
    )
