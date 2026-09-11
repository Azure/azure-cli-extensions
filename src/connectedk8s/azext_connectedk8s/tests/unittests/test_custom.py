# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import sys
from types import SimpleNamespace
from typing import Dict, Optional
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from kubernetes.client.models import (
    V1Node,
    V1NodeList,
    V1NodeSpec,
    V1ObjectMeta,
)

from azext_connectedk8s import custom
from azext_connectedk8s.custom import (
    _get_kubernetes_client_locations,
    _telemetry_catch_all,
    expand_proxy_skip_range_keywords,
    get_kubernetes_distro,
    get_kubernetes_infra,
)


def test_get_kubernetes_client_locations_preserves_az_cli_error(monkeypatch):
    expected = custom.AzCLIError("[AZK8S0515] HelmClientError")
    monkeypatch.setattr(
        custom,
        "get_kubectl_client_location",
        MagicMock(return_value="/usr/bin/kubectl"),
    )
    monkeypatch.setattr(
        custom, "get_helm_client_location", MagicMock(side_effect=expected)
    )

    with pytest.raises(custom.AzCLIError) as raised:
        _get_kubernetes_client_locations(MagicMock(), "AzureCloud")

    assert raised.value is expected


def test_telemetry_catch_all_uses_keyword_cmd(monkeypatch):
    class ReportedError(Exception):
        pass

    cmd = MagicMock()
    cmd.cli_ctx = MagicMock()
    report_error = MagicMock(return_value=ReportedError("reported"))
    monkeypatch.setattr(custom.utils, "report_connectedk8s_error", report_error)

    @_telemetry_catch_all
    def command(*, cmd):
        raise RuntimeError("failed")

    with pytest.raises(ReportedError):
        command(cmd=cmd)

    assert report_error.call_args.args[0] is cmd


def _cmd_without_arm_id():
    return SimpleNamespace(cli_ctx=SimpleNamespace(data={}))


def _assert_standardized_telemetry(mock_telemetry, error, user_fault):
    _, properties = mock_telemetry.add_extension_event.call_args.args
    assert properties["Context.Default.AzureCLI.errorCode"] == error.code
    assert properties["Context.Default.AzureCLI.errorName"] == error.name
    assert properties["Context.Default.AzureCLI.errorFaultType"] == error.fault_type
    assert (
        mock_telemetry.set_exception.call_args.kwargs["summary"]
        == properties["Context.Default.AzureCLI.errorMessage"]
    )
    mock_telemetry.add_extension_event.assert_called_once()
    mock_telemetry.set_exception.assert_called_once()
    if user_fault:
        mock_telemetry.set_user_fault.assert_called_once_with()
    else:
        mock_telemetry.set_user_fault.assert_not_called()


@pytest.mark.parametrize("operation", ["create", "update"])
def test_agent_state_timeout_reports_real_standardized_error(monkeypatch, operation):
    mock_telemetry = MagicMock()
    monkeypatch.setattr(custom.utils, "telemetry", mock_telemetry)

    error = custom._agent_state_timeout_error(_cmd_without_arm_id(), operation)

    assert isinstance(error, custom.CLIInternalError)
    assert str(error).startswith("[AZK8S0506] AgentStateTimeout:")
    assert f"during {operation}" in str(error)
    _assert_standardized_telemetry(
        mock_telemetry, custom.errors.AGENT_STATE_TIMEOUT, False
    )


def test_key_pair_generation_reports_real_standardized_error(monkeypatch):
    monkeypatch.setattr(
        custom.RSA,
        "generate",
        MagicMock(side_effect=RuntimeError("key generation failed")),
    )
    mock_telemetry = MagicMock()
    monkeypatch.setattr(custom.utils, "telemetry", mock_telemetry)

    with pytest.raises(custom.CLIInternalError) as raised:
        custom._generate_key_pair(_cmd_without_arm_id())

    assert str(raised.value).startswith("[AZK8S0507] KeyPairGenerationFailed:")
    assert "key generation failed" in str(raised.value)
    _assert_standardized_telemetry(
        mock_telemetry, custom.errors.KEY_PAIR_GENERATION_FAILED, False
    )


def test_cleanup_stale_arc_agents_passes_aligned_arguments(monkeypatch):
    cmd = _cmd_without_arm_id()
    cleanup_crds = MagicMock()
    delete_agents = MagicMock()
    monkeypatch.setattr(custom, "crd_cleanup_force_delete", cleanup_crds)
    monkeypatch.setattr(custom.utils, "delete_arc_agents", delete_agents)

    custom._cleanup_stale_arc_agents(
        cmd,
        "/usr/bin/kubectl",
        "/tmp/kubeconfig",
        "context",
        "azure-arc",
        "/usr/bin/helm",
        True,
    )

    cleanup_crds.assert_called_once_with(
        cmd, "/usr/bin/kubectl", "/tmp/kubeconfig", "context"
    )
    delete_agents.assert_called_once_with(
        "azure-arc",
        "/tmp/kubeconfig",
        "context",
        "/usr/bin/helm",
        True,
        True,
        cmd=cmd,
    )


def test_validate_release_namespace_reports_real_standardized_error(monkeypatch):
    monkeypatch.setattr(
        custom.utils, "get_release_namespace", MagicMock(return_value=None)
    )
    mock_telemetry = MagicMock()
    monkeypatch.setattr(custom.utils, "telemetry", mock_telemetry)

    with pytest.raises(custom.ClientRequestError) as raised:
        custom.validate_release_namespace(
            _cmd_without_arm_id(),
            MagicMock(),
            "cluster",
            "resource-group",
            None,
            None,
            "/usr/bin/helm",
        )

    assert str(raised.value).startswith("[AZK8S0508] ReleaseNamespaceNotFound:")
    assert "has not been onboarded" in str(raised.value)
    _assert_standardized_telemetry(
        mock_telemetry, custom.errors.RELEASE_NAMESPACE_NOT_FOUND, True
    )


@pytest.mark.parametrize(
    "helm_error, expected_user_fault",
    [("Error: values failed", False), ("Error: forbidden", True)],
)
def test_get_all_helm_values_reports_real_standardized_error(
    monkeypatch, helm_error, expected_user_fault
):
    process = MagicMock(returncode=1)
    process.communicate.return_value = (b"", helm_error.encode("ascii"))
    monkeypatch.setattr(custom, "Popen", MagicMock(return_value=process))
    mock_telemetry = MagicMock()
    monkeypatch.setattr(custom.utils, "telemetry", mock_telemetry)

    with pytest.raises(custom.CLIInternalError) as raised:
        custom.get_all_helm_values(
            _cmd_without_arm_id(), "azure-arc", None, None, "/usr/bin/helm"
        )

    assert str(raised.value).startswith("[AZK8S0509] HelmValuesGetFailed:")
    assert helm_error in str(raised.value)
    _assert_standardized_telemetry(
        mock_telemetry,
        custom.errors.HELM_VALUES_GET_FAILED,
        expected_user_fault,
    )


def test_validate_cluster_connect_disable_preserves_helm_values_error(monkeypatch):
    expected = custom.CLIInternalError("[AZK8S0509] HelmValuesGetFailed")
    monkeypatch.setattr(custom, "get_all_helm_values", MagicMock(side_effect=expected))

    with pytest.raises(custom.CLIInternalError) as raised:
        custom._validate_cluster_connect_disable(
            _cmd_without_arm_id(),
            "azure-arc",
            None,
            None,
            "/usr/bin/helm",
            False,
        )

    assert raised.value is expected


def test_get_helm_client_location_reports_real_agc_not_installed_error(
    monkeypatch,
):
    monkeypatch.setattr(custom.shutil, "which", MagicMock(return_value=None))
    mock_telemetry = MagicMock()
    monkeypatch.setattr(custom.utils, "telemetry", mock_telemetry)

    with pytest.raises(custom.CLIInternalError) as raised:
        custom.get_helm_client_location(_cmd_without_arm_id(), azure_cloud="ussec")

    assert str(raised.value).startswith("[AZK8S0510] HelmNotInstalled:")
    assert "AGC environment" in str(raised.value)
    _assert_standardized_telemetry(
        mock_telemetry, custom.errors.HELM_NOT_INSTALLED, True
    )


def create_node(
    provider_id: Optional[str] = None,
    labels: Optional[Dict[str, str]] = None,
    annotations: Optional[Dict[str, str]] = None,
) -> V1Node:
    spec = V1NodeSpec(provider_id=provider_id)
    metadata = V1ObjectMeta(labels=labels or {}, annotations=annotations or {})
    return V1Node(spec=spec, metadata=metadata)


@pytest.mark.parametrize(
    "provider_id, expected",
    [
        ("k3s://node1", "k3s"),
        ("kind://node1", "kind"),
        ("azure://node1", "azure"),
        ("gce://node1", "gcp"),
        ("aws://node1", "aws"),
        ("unknown://node1", "unknown"),
        (None, "generic"),
    ],
)
def test_get_kubernetes_infra(provider_id, expected):
    node = create_node(provider_id) if provider_id is not None else None
    api_response = V1NodeList(items=[node]) if node else None
    assert get_kubernetes_infra(api_response) == expected


def test_empty_items():
    api_response = V1NodeList(items=[])
    assert get_kubernetes_infra(api_response) == "generic"


def test_invalid_provider_id():
    node = create_node(None)
    api_response = V1NodeList(items=[node])
    assert get_kubernetes_infra(api_response) == "None"


# --------------------- Tests for get_kubernetes_distro ---------------------
@pytest.mark.parametrize(
    "labels, annotations, provider_id, expected",
    [
        ({"node.openshift.io/os_id": "rhcos"}, {}, None, "openshift"),
        ({"kubernetes.azure.com/node-image-version": "2022.11.01"}, {}, None, "aks"),
        ({"cloud.google.com/gke-nodepool": "default-pool"}, {}, None, "gke"),
        ({"cloud.google.com/gke-os-distribution": "cos"}, {}, None, "gke"),
        ({"eks.amazonaws.com/nodegroup": "nodegroup-1"}, {}, None, "eks"),
        ({"minikube.k8s.io/version": "v1.25.0"}, {}, None, "minikube"),
        ({}, {"node.aksedge.io/distro": "aks_edge_k3s"}, None, "aks_edge_k3s"),
        ({}, {"node.aksedge.io/distro": "aks_edge_k8s"}, None, "aks_edge_k8s"),
        ({}, {}, "kind://node1", "kind"),
        ({}, {}, "k3s://node1", "k3s"),
        ({}, {"rke.cattle.io/external-ip": "192.168.1.1"}, None, "rancher_rke"),
        ({}, {"rke.cattle.io/internal-ip": "10.0.0.1"}, None, "rancher_rke"),
        ({}, {}, None, "generic"),
    ],
)
def test_get_kubernetes_distro(labels, annotations, provider_id, expected):
    node = create_node(provider_id=provider_id, labels=labels, annotations=annotations)
    api_response = V1NodeList(items=[node])
    assert get_kubernetes_distro(api_response) == expected


def test_distro_empty_items():
    api_response = V1NodeList(items=[])
    assert get_kubernetes_distro(api_response) == "generic"


def test_distro_invalid_metadata():
    node = create_node(provider_id="aws://node1", labels=None, annotations=None)
    api_response = V1NodeList(items=[node])
    assert get_kubernetes_distro(api_response) == "generic"


# --------------------- Tests for expand_proxy_skip_range_keywords ---------------------
def _proxy_cmd(active_directory="https://login.microsoftonline.com"):
    cmd = MagicMock()
    cmd.cli_ctx.cloud.endpoints.active_directory = active_directory
    return cmd


ARC_PUBLIC = (
    ".his.arc.azure.com,"
    ".dp.kubernetesconfiguration.azure.com,"
    ".guestconfiguration.azure.com"
)


def test_expand_arc_keyword_public_cloud():
    assert expand_proxy_skip_range_keywords(_proxy_cmd(), "Arc") == ARC_PUBLIC


@pytest.mark.parametrize("keyword", ["Arc", "arc", "ARC", " aRc "])
def test_expand_arc_keyword_is_case_and_space_insensitive(keyword):
    assert expand_proxy_skip_range_keywords(_proxy_cmd(), keyword) == ARC_PUBLIC


def test_expand_arc_keyword_preserves_other_entries():
    out = expand_proxy_skip_range_keywords(_proxy_cmd(), "Arc,10.0.0.0/16,.svc")
    assert out == ARC_PUBLIC + ",10.0.0.0/16,.svc"


def test_expand_arc_keyword_china_cloud():
    cmd = _proxy_cmd("https://login.chinacloudapi.cn")
    out = expand_proxy_skip_range_keywords(cmd, "Arc")
    assert out == (
        ".his.arc.azure.cn,"
        ".dp.kubernetesconfiguration.azure.cn,"
        ".guestconfiguration.azure.cn"
    )


def test_expand_arc_keyword_usgov_cloud():
    cmd = _proxy_cmd("https://login.microsoftonline.us")
    out = expand_proxy_skip_range_keywords(cmd, "Arc")
    assert out == (
        ".his.arc.azure.us,"
        ".dp.kubernetesconfiguration.azure.us,"
        ".guestconfiguration.azure.us"
    )


def test_expand_arc_keyword_ussec_cloud():
    cmd = _proxy_cmd("https://login.microsoftonline.microsoft.scloud")
    out = expand_proxy_skip_range_keywords(cmd, "Arc")
    assert out == (
        ".his.arc.azure.microsoft.scloud,"
        ".dp.kubernetesconfiguration.azure.microsoft.scloud,"
        ".guestconfiguration.azure.microsoft.scloud"
    )


def test_expand_arc_keyword_usnat_cloud():
    cmd = _proxy_cmd("https://login.microsoftonline.eaglex.ic.gov")
    out = expand_proxy_skip_range_keywords(cmd, "Arc")
    assert out == (
        ".his.arc.azure.eaglex.ic.gov,"
        ".dp.kubernetesconfiguration.azure.eaglex.ic.gov,"
        ".guestconfiguration.azure.eaglex.ic.gov"
    )


def test_expand_no_keyword_returns_unchanged():
    val = "10.0.0.0/16,.svc,localhost"
    assert expand_proxy_skip_range_keywords(_proxy_cmd(), val) == val


def test_expand_empty_returns_unchanged():
    assert expand_proxy_skip_range_keywords(_proxy_cmd(), "") == ""


def test_expand_arc_keyword_deduplicates():
    out = expand_proxy_skip_range_keywords(_proxy_cmd(), "Arc,Arc")
    assert out == ARC_PUBLIC


def test_expand_arc_keyword_dedups_case_insensitive_endpoint():
    # A user endpoint differing only in case is not duplicated in NO_PROXY.
    out = expand_proxy_skip_range_keywords(_proxy_cmd(), "Arc, .his.ARC.azure.com")
    assert out == ARC_PUBLIC
