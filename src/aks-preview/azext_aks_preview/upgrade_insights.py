# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict
from textwrap import fill

from azure.cli.core.azclierror import InvalidArgumentValueError, RequiredArgumentMissingError
from azure.cli.core._output import set_output_format

from azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks.models import (
    AgentPoolGenerateUpgradeInsightsContent,
    ControlPlaneAndAgentPoolsGenerateUpgradeInsightsContent,
    ControlPlaneGenerateUpgradeInsightsContent,
    NodeImageGenerateUpgradeInsightsContent,
)

_MISSING_AGENT_POOL_RESULTS = "No agent-pool evaluation results were returned by the service."


def validate_upgrade_insights_create(namespace):
    _validate_targets(
        namespace.upgrade_type,
        getattr(namespace, "target_kubernetes_ver", None),
        getattr(namespace, "target_node_image_ver", None),
    )


def _validate_targets(upgrade_type, kubernetes_version, node_image_version):
    if upgrade_type == "NodeImage":
        if kubernetes_version is not None:
            raise InvalidArgumentValueError(
                "--target-kubernetes-ver cannot be used with --upgrade-type NodeImage."
            )
    else:
        if node_image_version is not None:
            raise InvalidArgumentValueError(
                "--target-node-image-ver requires --upgrade-type NodeImage."
            )
        if kubernetes_version is None:
            raise RequiredArgumentMissingError(
                "--target-kubernetes-ver is required for Kubernetes version evaluations."
            )
    for option, value in (
        ("--target-kubernetes-ver", kubernetes_version),
        ("--target-node-image-ver", node_image_version),
    ):
        if value is not None and not value.strip():
            raise InvalidArgumentValueError(f"{option} cannot be empty.")


def aks_upgrade_insights_create(
    cmd, client, resource_group_name, name, target_kubernetes_ver,
    upgrade_type="ControlPlaneAndAgentPools",
):
    _validate_targets(upgrade_type, target_kubernetes_ver, None)
    request_types = {
        "ControlPlane": ControlPlaneGenerateUpgradeInsightsContent,
        "ControlPlaneAndAgentPools": ControlPlaneAndAgentPoolsGenerateUpgradeInsightsContent,
    }
    if upgrade_type not in request_types:
        raise InvalidArgumentValueError(
            "Cluster evaluations support ControlPlane or ControlPlaneAndAgentPools."
        )
    body = request_types[upgrade_type](target_kubernetes_version=target_kubernetes_ver)
    insight = client.generate(resource_group_name, name, body)
    return _output_insights(cmd, insight.as_dict(), name)


def aks_upgrade_insights_show(cmd, client, resource_group_name, name, insight_name):
    insight = client.get(resource_group_name, name, insight_name)
    return _output_insights(cmd, insight.as_dict(), name)


def aks_upgrade_insights_list(cmd, client, resource_group_name, name):
    insights = [insight.as_dict() for insight in client.list(resource_group_name, name)]
    return _output_insights(cmd, insights, name, detailed=False)


def aks_nodepool_upgrade_insights_create(
    cmd, client, resource_group_name, cluster_name, nodepool_name,
    upgrade_type="AgentPool", target_kubernetes_ver=None, target_node_image_ver=None,
):
    _validate_targets(upgrade_type, target_kubernetes_ver, target_node_image_ver)
    if upgrade_type == "AgentPool":
        body = AgentPoolGenerateUpgradeInsightsContent(
            agent_pool_name=nodepool_name,
            target_kubernetes_version=target_kubernetes_ver,
        )
    elif upgrade_type == "NodeImage":
        body = NodeImageGenerateUpgradeInsightsContent(agent_pool_name=nodepool_name)
        if target_node_image_ver is not None:
            body.target_node_image_version = target_node_image_ver
    else:
        raise InvalidArgumentValueError("Node pool evaluations support AgentPool or NodeImage.")
    insight = client.generate(resource_group_name, cluster_name, body)
    return _output_insights(cmd, insight.as_dict(), cluster_name)


def aks_nodepool_upgrade_insights_show(
    cmd, client, resource_group_name, cluster_name, nodepool_name, insight_name,
):
    insight = client.get(resource_group_name, cluster_name, insight_name).as_dict()
    properties = insight["properties"]
    if (
        properties.get("upgradeType") not in ("AgentPool", "NodeImage")
        or (properties.get("agentPoolName") or "").lower() != nodepool_name.lower()
    ):
        raise InvalidArgumentValueError(
            f"Insight '{insight_name}' is not a single-pool insight for '{nodepool_name}'. "
            "Use 'az aks upgrade-insights show' to read cluster or combined insights."
        )
    return _output_insights(cmd, insight, cluster_name)


def _output_insights(cmd, result, cluster_name, detailed=True):
    options = set(cmd.cli_ctx.data.get("safe_params") or [])
    configured_output = cmd.cli_ctx.config.get("core", "output", fallback=None)
    if options.intersection(("--output", "-o", "--query")) or configured_output:
        return result

    insights = result if isinstance(result, list) else [result]
    reports = [format_upgrade_insight_report(item, cluster_name, detailed) for item in insights]
    report = "\n\n".join(reports) if reports else f"No stored upgrade insights for cluster: {cluster_name}"
    # TSV renders a scalar verbatim through the CLI's normal output and redirection path.
    set_output_format(cmd.cli_ctx, "tsv")
    return report


def _scopes(properties):
    upgrade_type = properties.get("upgradeType")
    if upgrade_type == "ControlPlaneAndAgentPools":
        scopes = [("ControlPlane", "", properties.get("controlPlane") or {})]
        scopes.extend(
            ("AgentPool", pool.get("agentPoolName") or "Unknown", pool)
            for pool in properties.get("agentPools") or []
        )
        if not properties.get("agentPools"):
            scopes.append(("AgentPool", "", {}))
        return scopes
    return [(upgrade_type, properties.get("agentPoolName") or "", properties)]


def _status(scope):
    evaluation = scope.get("evaluation") or {}
    return evaluation.get("status") or "Not evaluated"


def _readiness(properties):
    if properties.get("provisioningState") in ("Failed", "Canceled"):
        return "NOT EVALUATED"
    statuses = [_status(scope) for _, _, scope in _scopes(properties)]
    for status in ("Failed", "Warning"):
        if status in statuses:
            return status.upper()
    return "PASSED" if statuses and all(status == "Passed" for status in statuses) else "NOT EVALUATED"


def _field(lines, label, value, indent=""):
    if value is not None and value != "":
        lines.append(fill(
            f"{label}: {value}", width=100, initial_indent=indent,
            subsequent_indent=indent + "  ", break_long_words=False, break_on_hyphens=False,
        ))


def _format_issue(lines, issue, detailed):
    severity = issue.get("severity") or "Unknown severity"
    lines.append(f"    {severity.upper()}: {issue.get('issueType') or 'Unknown issue'}")
    _field(lines, "Issue", issue.get("message"), "      ")
    if not detailed:
        return
    for resource in issue.get("impactedResources") or []:
        identifier = resource.get("resourceId") or "/".join(
            part for part in (resource.get("namespace"), resource.get("name")) if part
        )
        _field(lines, "Affected resource", " ".join(
            part for part in (resource.get("resourceType"), identifier) if part
        ), "      ")
    for action in issue.get("recommendedActions") or []:
        _field(lines, "Recommended action", action.get("title"), "      ")
        _field(lines, "Details", action.get("details"), "        ")
        _field(lines, "Documentation", action.get("documentationLink"), "        ")


def format_upgrade_insight_report(insight, cluster_name, detailed=True):
    properties = insight["properties"]
    lines = [f"Upgrade readiness: {_readiness(properties)}", f"Cluster: {cluster_name}"]
    _field(lines, "Upgrade type", properties.get("upgradeType"))
    _field(lines, "Target Kubernetes version", properties.get("targetKubernetesVersion"))
    _field(lines, "Target node image version", properties.get("targetNodeImageVersion"))
    _field(lines, "Insight", insight.get("name"))
    _field(lines, "Evaluated at", properties.get("lastEvaluatedAt"))
    _field(lines, "Expires at", properties.get("expiresAt"))
    _field(lines, "Provisioning state", properties.get("provisioningState"))
    for upgrade_type, pool_name, scope in _scopes(properties):
        label = "Control plane" if upgrade_type == "ControlPlane" else f"Agent pool: {pool_name}"
        if upgrade_type == "AgentPool" and not pool_name:
            label = "Agent pools"
        if upgrade_type == "NodeImage":
            label += " (node image)"
        lines.extend(("", f"  {label} - {_status(scope).upper()}"))
        _field(lines, "Current Kubernetes version", scope.get("currentKubernetesVersion"), "    ")
        _field(lines, "Current node image version", scope.get("currentNodeImageVersion"), "    ")
        evaluation = scope.get("evaluation") or {}
        _field(lines, "Evaluated at", evaluation.get("evaluatedAt"), "    ")
        issues = evaluation.get("detectedIssues") or []
        if not issues:
            message = "No issues detected." if _status(scope) == "Passed" else "No issue details were returned."
            if upgrade_type == "AgentPool" and not pool_name:
                message = _MISSING_AGENT_POOL_RESULTS
            lines.append(f"    {message}")
        for issue in issues:
            _format_issue(lines, issue, detailed)
    return "\n".join(lines)


def aks_upgrade_insights_table_format(result):
    insights = result if isinstance(result, list) else [result]
    rows = []
    for insight in insights:
        properties = insight["properties"]
        for upgrade_type, pool_name, scope in _scopes(properties):
            evaluation = scope.get("evaluation") or {}
            for issue in evaluation.get("detectedIssues") or [{}]:
                rows.append(OrderedDict(
                    Name=insight.get("name"),
                    Scope=upgrade_type,
                    Pool=pool_name,
                    Target=properties.get("targetKubernetesVersion") or properties.get("targetNodeImageVersion"),
                    Status=_status(scope),
                    Severity=issue.get("severity"),
                    Issue=(
                        _MISSING_AGENT_POOL_RESULTS
                        if upgrade_type == "AgentPool" and not pool_name
                        else issue.get("message")
                    ),
                ))
    return rows
