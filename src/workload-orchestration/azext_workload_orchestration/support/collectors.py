# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Data collectors for the workload-orchestration support bundle feature.

Responsible for gathering cluster information, resource descriptions, and
container logs into the bundle directory structure.
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from knack.log import get_logger

from azext_workload_orchestration.support.consts import (
    DEFAULT_TAIL_LINES,
    DEFAULT_MAX_LOG_SIZE_BYTES,
    FOLDER_LOGS,
    FOLDER_RESOURCES,
    FOLDER_CLUSTER_INFO,
    WO_NAMESPACE,
)
from azext_workload_orchestration.support.utils import (
    safe_api_call,
    write_json,
    write_text,
    create_namespace_log_dir,
    format_bytes,
)

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Namespace validation (pre-flight)
# ---------------------------------------------------------------------------

def validate_namespaces(clients, namespaces):
    """Validate that requested namespaces exist on the cluster.

    Returns (valid_namespaces, skipped_namespaces) where skipped_namespaces
    is a list of (namespace, reason) tuples.
    """
    core = clients["core_v1"]
    valid = []
    skipped = []

    for ns in namespaces:
        result, err = safe_api_call(
            core.read_namespace, ns,
            description=f"validate namespace '{ns}'",
            max_retries=1,
        )
        if result:
            if result.status and result.status.phase == "Terminating":
                skipped.append((ns, "namespace is terminating"))
                logger.warning("Namespace '%s' is terminating, skipping", ns)
            else:
                valid.append(ns)
        else:
            skipped.append((ns, err or "namespace not found"))
            logger.warning("Namespace '%s' not found, skipping: %s", ns, err)

    return valid, skipped


# ---------------------------------------------------------------------------
# Cluster info collection
# ---------------------------------------------------------------------------

def collect_cluster_info(clients, bundle_dir):
    """Collect basic cluster information (version, nodes, namespaces)."""
    info = {}

    # Kubernetes version
    version_client = clients["version"]
    result, err = safe_api_call(version_client.get_code, description="get server version")
    if result:
        info["server_version"] = {
            "major": result.major,
            "minor": result.minor,
            "git_version": result.git_version,
            "platform": result.platform,
        }

    # Node summary
    core = clients["core_v1"]
    result, err = safe_api_call(core.list_node, description="list nodes")
    if result:
        nodes = []
        for node in result.items:
            status = node.status
            conditions_list = [
                {"type": c.type, "status": c.status, "reason": c.reason, "message": c.message}
                for c in (status.conditions or [])
            ]
            conditions = {c.type: c.status for c in (status.conditions or [])}
            alloc = status.allocatable or {}
            nodes.append({
                "name": node.metadata.name,
                "ready": conditions.get("Ready", "Unknown"),
                "roles": _get_node_roles(node),
                "os": node.status.node_info.os_image if status.node_info else "unknown",
                "container_runtime": status.node_info.container_runtime_version if status.node_info else "unknown",
                "kubelet_version": status.node_info.kubelet_version if status.node_info else "unknown",
                "allocatable_cpu": alloc.get("cpu", "0"),
                "allocatable_memory": alloc.get("memory", "0"),
                "taints": [
                    {"key": t.key, "effect": t.effect, "value": t.value}
                    for t in (node.spec.taints or [])
                ],
                "conditions": conditions,
                "conditions_detail": conditions_list,
            })
        info["nodes"] = nodes
        info["node_count"] = len(nodes)

    # Namespace list
    result, err = safe_api_call(core.list_namespace, description="list namespaces")
    if result:
        info["namespaces"] = [
            {
                "name": ns.metadata.name,
                "status": ns.status.phase,
                "labels": dict(ns.metadata.labels or {}),
            }
            for ns in result.items
        ]

    write_json(os.path.join(bundle_dir, FOLDER_CLUSTER_INFO, "cluster-info.json"), info)
    logger.info("Collected cluster info: %d nodes, %d namespaces",
                info.get("node_count", 0), len(info.get("namespaces", [])))
    return info


def _get_node_roles(node):
    """Extract node roles from labels."""
    roles = []
    for label, value in (node.metadata.labels or {}).items():
        if label.startswith("node-role.kubernetes.io/"):
            roles.append(label.split("/")[-1])
    return roles if roles else ["<none>"]


# ---------------------------------------------------------------------------
# Resource collection
# ---------------------------------------------------------------------------

def collect_namespace_resources(clients, bundle_dir, namespace):
    """Collect resource descriptions for a given namespace."""
    core = clients["core_v1"]
    apps = clients["apps_v1"]
    resources = {}

    # Pods
    result, err = safe_api_call(
        core.list_namespaced_pod, namespace, description=f"list pods in {namespace}"
    )
    if result:
        resources["pods"] = [
            {
                "name": p.metadata.name,
                "phase": p.status.phase,
                "ready": _pod_ready_count(p),
                "restarts": _pod_restart_count(p),
                "node": p.spec.node_name,
                "containers": _get_container_details(p),
            }
            for p in result.items
        ]

    # Deployments
    result, err = safe_api_call(
        apps.list_namespaced_deployment, namespace, description=f"list deployments in {namespace}"
    )
    if result:
        resources["deployments"] = [
            {
                "name": d.metadata.name,
                "replicas": d.spec.replicas,
                "ready_replicas": d.status.ready_replicas or 0,
                "available_replicas": d.status.available_replicas or 0,
            }
            for d in result.items
        ]

    # Services
    result, err = safe_api_call(
        core.list_namespaced_service, namespace, description=f"list services in {namespace}"
    )
    if result:
        resources["services"] = [
            {
                "name": s.metadata.name,
                "type": s.spec.type,
                "cluster_ip": s.spec.cluster_ip,
                "ports": [
                    {"port": p.port, "target_port": str(p.target_port), "protocol": p.protocol}
                    for p in (s.spec.ports or [])
                ],
            }
            for s in result.items
        ]

    # DaemonSets
    result, err = safe_api_call(
        apps.list_namespaced_daemon_set, namespace, description=f"list daemonsets in {namespace}"
    )
    if result:
        resources["daemonsets"] = [
            {
                "name": ds.metadata.name,
                "desired": ds.status.desired_number_scheduled,
                "ready": ds.status.number_ready,
            }
            for ds in result.items
        ]

    # StatefulSets
    result, err = safe_api_call(
        apps.list_namespaced_stateful_set, namespace,
        description=f"list statefulsets in {namespace}"
    )
    if result:
        resources["statefulsets"] = [
            {
                "name": ss.metadata.name,
                "replicas": ss.spec.replicas,
                "ready_replicas": ss.status.ready_replicas or 0,
            }
            for ss in result.items
        ]

    # Events
    result, err = safe_api_call(
        core.list_namespaced_event, namespace, description=f"list events in {namespace}"
    )
    if result:
        resources["events"] = [
            {
                "type": e.type,
                "reason": e.reason,
                "message": e.message,
                "involved_object": f"{e.involved_object.kind}/{e.involved_object.name}",
                "count": e.count,
                "last_timestamp": str(e.last_timestamp) if e.last_timestamp else None,
            }
            for e in result.items
        ]

    # ConfigMaps (names only, not data — could contain secrets)
    result, err = safe_api_call(
        core.list_namespaced_config_map, namespace, description=f"list configmaps in {namespace}"
    )
    if result:
        resources["configmaps"] = [
            {"name": cm.metadata.name, "data_keys": list((cm.data or {}).keys())}
            for cm in result.items
        ]

    # ReplicaSets
    result, err = safe_api_call(
        apps.list_namespaced_replica_set, namespace,
        description=f"list replicasets in {namespace}"
    )
    if result:
        resources["replicasets"] = [
            {
                "name": rs.metadata.name,
                "replicas": rs.spec.replicas,
                "ready_replicas": rs.status.ready_replicas or 0,
                "available_replicas": rs.status.available_replicas or 0,
                "owner": _get_owner_ref(rs),
            }
            for rs in result.items
        ]

    # Jobs
    try:
        from kubernetes import client as _k8s_client
        batch_v1 = _k8s_client.BatchV1Api()
        result, err = safe_api_call(
            batch_v1.list_namespaced_job, namespace,
            description=f"list jobs in {namespace}"
        )
        if result:
            resources["jobs"] = [
                {
                    "name": j.metadata.name,
                    "active": j.status.active or 0,
                    "succeeded": j.status.succeeded or 0,
                    "failed": j.status.failed or 0,
                    "completions": j.spec.completions,
                    "start_time": str(j.status.start_time) if j.status.start_time else None,
                    "completion_time": str(j.status.completion_time) if j.status.completion_time else None,
                }
                for j in result.items
            ]

        # CronJobs
        result, err = safe_api_call(
            batch_v1.list_namespaced_cron_job, namespace,
            description=f"list cronjobs in {namespace}"
        )
        if result:
            resources["cronjobs"] = [
                {
                    "name": cj.metadata.name,
                    "schedule": cj.spec.schedule,
                    "suspend": cj.spec.suspend,
                    "active_jobs": len(cj.status.active or []),
                    "last_schedule": str(cj.status.last_schedule_time) if cj.status.last_schedule_time else None,
                    "last_successful": str(cj.status.last_successful_time) if cj.status.last_successful_time else None,
                }
                for cj in result.items
            ]
    except Exception as ex:
        logger.debug("Batch API not available for %s: %s", namespace, ex)

    # Ingresses
    try:
        from kubernetes import client as _k8s_client
        networking_v1 = _k8s_client.NetworkingV1Api()
        result, err = safe_api_call(
            networking_v1.list_namespaced_ingress, namespace,
            description=f"list ingresses in {namespace}"
        )
        if result:
            resources["ingresses"] = [
                {
                    "name": ing.metadata.name,
                    "class_name": ing.spec.ingress_class_name,
                    "rules_count": len(ing.spec.rules or []),
                    "tls_count": len(ing.spec.tls or []),
                    "hosts": [r.host for r in (ing.spec.rules or []) if r.host],
                }
                for ing in result.items
            ]

        # NetworkPolicies
        result, err = safe_api_call(
            networking_v1.list_namespaced_network_policy, namespace,
            description=f"list network policies in {namespace}"
        )
        if result:
            resources["network_policies"] = [
                {
                    "name": np.metadata.name,
                    "pod_selector": dict(np.spec.pod_selector.match_labels or {}) if np.spec.pod_selector and np.spec.pod_selector.match_labels else {},
                    "policy_types": np.spec.policy_types or [],
                    "ingress_rules": len(np.spec.ingress or []) if np.spec.ingress else 0,
                    "egress_rules": len(np.spec.egress or []) if np.spec.egress else 0,
                }
                for np in result.items
            ]
    except Exception as ex:
        logger.debug("Networking API not available for %s: %s", namespace, ex)

    # ServiceAccounts
    result, err = safe_api_call(
        core.list_namespaced_service_account, namespace,
        description=f"list service accounts in {namespace}"
    )
    if result:
        resources["service_accounts"] = [
            {
                "name": sa.metadata.name,
                "secrets_count": len(sa.secrets or []) if sa.secrets else 0,
                "image_pull_secrets": [
                    ips.name for ips in (sa.image_pull_secrets or [])
                ],
            }
            for sa in result.items
        ]

    filepath = os.path.join(bundle_dir, FOLDER_RESOURCES, f"{namespace}-resources.json")
    write_json(filepath, resources)
    pod_count = len(resources.get("pods", []))
    logger.info("Collected resources for %s: %d pods, %d resource types",
                namespace, pod_count, len(resources))
    return resources


def _get_owner_ref(resource):
    """Extract owner reference (controller) for a resource."""
    refs = resource.metadata.owner_references or []
    if refs:
        return {"kind": refs[0].kind, "name": refs[0].name}
    return None


def _get_container_details(pod):
    """Extract container status details for a pod."""
    details = []
    statuses = {cs.name: cs for cs in (pod.status.container_statuses or [])}
    for c in (pod.spec.containers or []):
        cs = statuses.get(c.name)
        info = {"name": c.name}
        if cs:
            info["ready"] = cs.ready
            info["restart_count"] = cs.restart_count
            # Extract current state
            if cs.state:
                if cs.state.running:
                    info["state"] = "running"
                elif cs.state.waiting:
                    info["state"] = "waiting"
                    info["reason"] = cs.state.waiting.reason
                    info["message"] = cs.state.waiting.message
                elif cs.state.terminated:
                    info["state"] = "terminated"
                    info["reason"] = cs.state.terminated.reason
                    info["exit_code"] = cs.state.terminated.exit_code
            # Extract last state (previous run)
            if cs.last_state and cs.last_state.terminated:
                info["last_terminated_reason"] = cs.last_state.terminated.reason
                info["last_exit_code"] = cs.last_state.terminated.exit_code
        details.append(info)
    return details


def _pod_ready_count(pod):
    """Return 'ready/total' string for a pod."""
    containers = pod.spec.containers or []
    total = len(containers)
    ready = sum(
        1 for cs in (pod.status.container_statuses or []) if cs.ready
    )
    return f"{ready}/{total}"


def _pod_restart_count(pod):
    """Return total restart count across all containers."""
    return sum(cs.restart_count for cs in (pod.status.container_statuses or []))


# ---------------------------------------------------------------------------
# Cluster-scoped resource collection
# ---------------------------------------------------------------------------

def collect_cluster_resources(clients, bundle_dir):
    """Collect cluster-scoped resources (StorageClasses, CRDs, webhooks, PVs)."""
    cluster = {}

    # StorageClasses
    storage = clients["storage_v1"]
    result, err = safe_api_call(storage.list_storage_class, description="list storage classes")
    if result:
        from azext_workload_orchestration.support.consts import (
            SC_DEFAULT_ANNOTATION_V1, SC_DEFAULT_ANNOTATION_BETA,
        )
        cluster["storage_classes"] = [
            {
                "name": sc.metadata.name,
                "provisioner": sc.provisioner,
                "is_default": _is_default_sc(sc),
                "reclaim_policy": sc.reclaim_policy,
            }
            for sc in result.items
        ]

    # PersistentVolumes
    core = clients["core_v1"]
    result, err = safe_api_call(core.list_persistent_volume, description="list PVs")
    if result:
        cluster["persistent_volumes"] = [
            {
                "name": pv.metadata.name,
                "capacity": dict(pv.spec.capacity or {}),
                "status": pv.status.phase,
                "storage_class": pv.spec.storage_class_name,
                "claim": f"{pv.spec.claim_ref.namespace}/{pv.spec.claim_ref.name}" if pv.spec.claim_ref else None,
            }
            for pv in result.items
        ]

    # Validating Webhooks
    admission = clients["admissionregistration_v1"]
    result, err = safe_api_call(
        admission.list_validating_webhook_configuration,
        description="list validating webhooks",
    )
    if result:
        cluster["validating_webhooks"] = [
            {
                "name": w.metadata.name,
                "webhook_count": len(w.webhooks or []),
                "failure_policies": list({wh.failure_policy for wh in (w.webhooks or [])}),
            }
            for w in result.items
        ]

    # Mutating Webhooks
    result, err = safe_api_call(
        admission.list_mutating_webhook_configuration,
        description="list mutating webhooks",
    )
    if result:
        cluster["mutating_webhooks"] = [
            {
                "name": w.metadata.name,
                "webhook_count": len(w.webhooks or []),
                "failure_policies": list({wh.failure_policy for wh in (w.webhooks or [])}),
            }
            for w in result.items
        ]

    # CRDs (names only — full JSON is huge)
    custom = clients["custom_objects"]
    result, err = safe_api_call(
        custom.list_cluster_custom_object,
        "apiextensions.k8s.io", "v1", "customresourcedefinitions",
        description="list CRDs",
    )
    if result:
        cluster["crds"] = [
            {
                "name": crd.get("metadata", {}).get("name", "unknown"),
                "group": crd.get("spec", {}).get("group", "unknown"),
            }
            for crd in result.get("items", [])
        ]

    # CSI Drivers
    result, err = safe_api_call(storage.list_csi_driver, description="list CSI drivers")
    if result:
        cluster["csi_drivers"] = [
            {
                "name": d.metadata.name,
                "attach_required": d.spec.attach_required if d.spec else None,
            }
            for d in result.items
        ]

    filepath = os.path.join(bundle_dir, FOLDER_RESOURCES, "cluster-resources.json")
    write_json(filepath, cluster)
    logger.info("Collected cluster resources: %d SCs, %d webhooks, %d CRDs, %d CSI drivers",
                len(cluster.get("storage_classes", [])),
                len(cluster.get("validating_webhooks", [])) + len(cluster.get("mutating_webhooks", [])),
                len(cluster.get("crds", [])),
                len(cluster.get("csi_drivers", [])))
    return cluster


def _is_default_sc(sc):
    """Check if a StorageClass is the default (v1 or beta annotation)."""
    from azext_workload_orchestration.support.consts import (
        SC_DEFAULT_ANNOTATION_V1, SC_DEFAULT_ANNOTATION_BETA,
    )
    ann = sc.metadata.annotations or {}
    return (
        ann.get(SC_DEFAULT_ANNOTATION_V1) == "true"
        or ann.get(SC_DEFAULT_ANNOTATION_BETA) == "true"
    )


# ---------------------------------------------------------------------------
# Container log collection
# ---------------------------------------------------------------------------

def collect_container_logs(clients, bundle_dir, namespace, tail_lines=DEFAULT_TAIL_LINES,
                           max_workers=5, log_timeout=None):
    """Collect container logs for all pods in a namespace.

    Uses threading for parallel log fetching. Returns count of logs collected.
    """
    from azext_workload_orchestration.support.consts import DEFAULT_LOG_TIMEOUT_SECONDS

    per_log_timeout = log_timeout or DEFAULT_LOG_TIMEOUT_SECONDS
    core = clients["core_v1"]
    result, err = safe_api_call(
        core.list_namespaced_pod, namespace, description=f"list pods for logs in {namespace}"
    )
    if not result:
        logger.warning("Could not list pods in %s: %s", namespace, err)
        return 0

    ns_log_dir = create_namespace_log_dir(bundle_dir, namespace)

    # Build list of (pod_name, container_name) to collect
    targets = []
    for pod in result.items:
        for container in (pod.spec.containers or []):
            targets.append((pod.metadata.name, container.name))

    if not targets:
        return 0

    collected = 0

    def _fetch_log(pod_name, container_name):
        log_result, log_err = safe_api_call(
            core.read_namespaced_pod_log,
            pod_name, namespace,
            container=container_name,
            tail_lines=tail_lines,
            _preload_content=True,
            description=f"logs {namespace}/{pod_name}/{container_name}",
        )
        if log_result is not None:
            # Truncate if exceeds max size
            log_text = log_result
            if len(log_text.encode("utf-8", errors="replace")) > DEFAULT_MAX_LOG_SIZE_BYTES:
                lines = log_text.splitlines()
                truncated = []
                size = 0
                for line in reversed(lines):
                    size += len(line.encode("utf-8", errors="replace")) + 1
                    if size > DEFAULT_MAX_LOG_SIZE_BYTES:
                        break
                    truncated.insert(0, line)
                log_text = f"[TRUNCATED to last {len(truncated)} lines]\n" + "\n".join(truncated)

            filepath = os.path.join(ns_log_dir, f"{pod_name}--{container_name}.log")
            write_text(filepath, log_text)
            return True
        return False

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_fetch_log, pod, container): (pod, container)
            for pod, container in targets
        }
        for future in as_completed(futures, timeout=per_log_timeout * len(targets)):
            pod, container = futures[future]
            try:
                if future.result(timeout=per_log_timeout):
                    collected += 1
            except TimeoutError:
                logger.debug("Timeout collecting log for %s/%s", pod, container)
            except Exception as ex:
                logger.debug("Failed to collect log for %s/%s: %s", pod, container, ex)

    logger.info("Collected %d/%d container logs in %s", collected, len(targets), namespace)
    return collected


# ---------------------------------------------------------------------------
# WO-specific collection
# ---------------------------------------------------------------------------

def collect_wo_components(clients, bundle_dir, capabilities):
    """Collect WO-specific resources: Symphony CRDs, cert-manager status, etc."""
    wo_info = {}
    custom = clients["custom_objects"]

    # Symphony targets (if symphony is installed)
    if capabilities.get("has_symphony"):
        result, err = safe_api_call(
            custom.list_namespaced_custom_object,
            "fabric.symphony", "v1", WO_NAMESPACE, "targets",
            description="list Symphony targets",
        )
        if result:
            wo_info["symphony_targets"] = [
                {
                    "name": t.get("metadata", {}).get("name", "unknown"),
                    "status": t.get("status", {}).get("provisioningStatus", {}).get("status", "unknown"),
                }
                for t in result.get("items", [])
            ]

    # cert-manager ClusterIssuers (if cert-manager is installed)
    if capabilities.get("has_cert_manager"):
        result, err = safe_api_call(
            custom.list_cluster_custom_object,
            "cert-manager.io", "v1", "clusterissuers",
            description="list ClusterIssuers",
        )
        if result:
            wo_info["cluster_issuers"] = [
                {
                    "name": ci.get("metadata", {}).get("name", "unknown"),
                    "ready": _cert_issuer_ready(ci),
                }
                for ci in result.get("items", [])
            ]

    # Gatekeeper constraints (if gatekeeper is installed)
    if capabilities.get("has_gatekeeper"):
        result, err = safe_api_call(
            custom.list_cluster_custom_object,
            "templates.gatekeeper.sh", "v1", "constrainttemplates",
            description="list Gatekeeper ConstraintTemplates",
        )
        if result:
            wo_info["gatekeeper_templates"] = [
                {"name": t.get("metadata", {}).get("name", "unknown")} for t in result.get("items", [])
            ]

    filepath = os.path.join(bundle_dir, FOLDER_RESOURCES, "wo-components.json")
    write_json(filepath, wo_info)
    return wo_info


def _cert_issuer_ready(issuer):
    """Check if a cert-manager issuer is Ready."""
    conditions = issuer.get("status", {}).get("conditions", [])
    for c in conditions:
        if c.get("type") == "Ready":
            return c.get("status") == "True"
    return False


# ---------------------------------------------------------------------------
# Previous container logs (crash-looping pods)
# ---------------------------------------------------------------------------

def collect_previous_logs(clients, bundle_dir, namespace, tail_lines=DEFAULT_TAIL_LINES):
    """Collect previous container logs for pods that have restarted.

    Only collects previous logs for containers with restart_count > 0.
    Returns count of previous logs collected.
    """
    core = clients["core_v1"]
    result, err = safe_api_call(
        core.list_namespaced_pod, namespace,
        description=f"list pods for previous logs in {namespace}",
    )
    if not result:
        return 0

    ns_log_dir = create_namespace_log_dir(bundle_dir, namespace)
    collected = 0

    for pod in result.items:
        for cs in (pod.status.container_statuses or []):
            if cs.restart_count and cs.restart_count > 0:
                log_result, log_err = safe_api_call(
                    core.read_namespaced_pod_log,
                    pod.metadata.name, namespace,
                    container=cs.name,
                    tail_lines=tail_lines,
                    previous=True,
                    _preload_content=True,
                    description=f"previous logs {namespace}/{pod.metadata.name}/{cs.name}",
                )
                if log_result:
                    filepath = os.path.join(
                        ns_log_dir, f"{pod.metadata.name}--{cs.name}--previous.log"
                    )
                    try:
                        write_text(filepath, log_result)
                        collected += 1
                    except OSError as ex:
                        logger.warning("Failed to write previous log %s: %s", filepath, ex)

    if collected:
        logger.info("Collected %d previous container logs in %s", collected, namespace)
    return collected


# ---------------------------------------------------------------------------
# Resource quotas and limit ranges
# ---------------------------------------------------------------------------

def collect_resource_quotas(clients, bundle_dir, namespace):
    """Collect ResourceQuotas and LimitRanges for a namespace."""
    core = clients["core_v1"]
    quota_data = {}

    # ResourceQuotas
    result, err = safe_api_call(
        core.list_namespaced_resource_quota, namespace,
        description=f"list resource quotas in {namespace}",
    )
    if result and result.items:
        quota_data["resource_quotas"] = [
            {
                "name": rq.metadata.name,
                "hard": dict(rq.status.hard or {}) if rq.status else {},
                "used": dict(rq.status.used or {}) if rq.status else {},
            }
            for rq in result.items
        ]

    # LimitRanges
    result, err = safe_api_call(
        core.list_namespaced_limit_range, namespace,
        description=f"list limit ranges in {namespace}",
    )
    if result and result.items:
        quota_data["limit_ranges"] = [
            {
                "name": lr.metadata.name,
                "limits": [
                    {
                        "type": lim.type,
                        "default": dict(lim.default or {}),
                        "default_request": dict(lim.default_request or {}),
                        "max": dict(getattr(lim, "max", None) or {}),
                        "min": dict(getattr(lim, "min", None) or {}),
                    }
                    for lim in (lr.spec.limits or [])
                ],
            }
            for lr in result.items
        ]

    if quota_data:
        filepath = os.path.join(bundle_dir, FOLDER_RESOURCES, f"{namespace}-quotas.json")
        write_json(filepath, quota_data)

    return quota_data


# ---------------------------------------------------------------------------
# Metrics (kubectl top equivalent)
# ---------------------------------------------------------------------------

def collect_metrics(clients, bundle_dir, capabilities):
    """Collect node and pod metrics if metrics-server is available."""
    if not capabilities.get("has_metrics"):
        logger.info("Metrics API not available, skipping metrics collection")
        return {}

    custom = clients["custom_objects"]
    metrics = {}

    # Node metrics
    result, err = safe_api_call(
        custom.list_cluster_custom_object,
        "metrics.k8s.io", "v1beta1", "nodes",
        description="get node metrics",
    )
    if result:
        metrics["node_metrics"] = [
            {
                "name": n.get("metadata", {}).get("name", "unknown"),
                "cpu": n.get("usage", {}).get("cpu", "0"),
                "memory": n.get("usage", {}).get("memory", "0"),
            }
            for n in result.get("items", [])
        ]

    # Pod metrics (WO namespace)
    result, err = safe_api_call(
        custom.list_namespaced_custom_object,
        "metrics.k8s.io", "v1beta1", WO_NAMESPACE, "pods",
        description="get WO pod metrics",
    )
    if result:
        metrics["wo_pod_metrics"] = [
            {
                "name": p.get("metadata", {}).get("name", "unknown"),
                "containers": [
                    {
                        "name": c.get("name", "unknown"),
                        "cpu": c.get("usage", {}).get("cpu", "0"),
                        "memory": c.get("usage", {}).get("memory", "0"),
                    }
                    for c in p.get("containers", [])
                ],
            }
            for p in result.get("items", [])
        ]

    if metrics:
        filepath = os.path.join(bundle_dir, FOLDER_CLUSTER_INFO, "metrics.json")
        write_json(filepath, metrics)
        logger.info("Collected metrics: %d nodes, %d WO pods",
                    len(metrics.get("node_metrics", [])),
                    len(metrics.get("wo_pod_metrics", [])))

    return metrics


# ---------------------------------------------------------------------------
# PersistentVolumeClaims per namespace
# ---------------------------------------------------------------------------

def collect_pvcs(clients, bundle_dir, namespace):
    """Collect PVC information for a namespace."""
    core = clients["core_v1"]
    result, err = safe_api_call(
        core.list_namespaced_persistent_volume_claim, namespace,
        description=f"list PVCs in {namespace}",
    )
    if not result or not result.items:
        return []

    pvcs = [
        {
            "name": pvc.metadata.name,
            "status": pvc.status.phase,
            "capacity": dict(pvc.status.capacity or {}) if pvc.status.capacity else {},
            "storage_class": pvc.spec.storage_class_name,
            "access_modes": pvc.spec.access_modes,
            "volume_name": pvc.spec.volume_name,
        }
        for pvc in result.items
    ]

    filepath = os.path.join(bundle_dir, FOLDER_RESOURCES, f"{namespace}-pvcs.json")
    write_json(filepath, pvcs)
    return pvcs
