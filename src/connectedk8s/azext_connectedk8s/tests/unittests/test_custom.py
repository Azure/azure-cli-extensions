# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import sys
from types import SimpleNamespace
from typing import Dict, Optional
from unittest.mock import MagicMock, create_autospec

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from kubernetes.client.models import (
    V1Node,
    V1NodeList,
    V1NodeSpec,
    V1ObjectMeta,
)

import azext_connectedk8s._constants as consts
from azext_connectedk8s import custom
from azext_connectedk8s.custom import (
    _get_kubernetes_client_locations,
    _telemetry_catch_all,
    add_arc_proxy_skip_range_endpoints,
    get_arc_proxy_skip_range_endpoints,
    get_kubernetes_distro,
    get_kubernetes_infra,
    has_arc_proxy_skip_range_endpoints,
    remove_arc_proxy_skip_range_endpoints,
    resolve_arc_proxy_bypass,
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


def test_enable_features_reports_custom_locations_enable_failed(monkeypatch):
    cmd = _cmd_without_arm_id()
    connected_cluster = SimpleNamespace(kind=None, private_link_state="Disabled")
    client = MagicMock()
    client.get.return_value = connected_cluster
    monkeypatch.setattr(
        custom.utils, "validate_custom_token", MagicMock(return_value=(False, None))
    )
    monkeypatch.setattr(custom, "get_subscription_id", MagicMock(return_value="sub"))
    monkeypatch.setattr(
        custom,
        "check_cl_registration_and_get_oid",
        MagicMock(return_value=(False, "")),
    )
    mock_telemetry = MagicMock()
    monkeypatch.setattr(custom.utils, "telemetry", mock_telemetry)

    with pytest.raises(custom.CLIInternalError) as raised:
        custom.enable_features(
            cmd,
            client,
            "resource-group",
            "cluster",
            ["custom-locations"],
        )

    assert str(raised.value).startswith("[AZK8S0700] CustomLocationsEnableFailed:")
    _assert_standardized_telemetry(
        mock_telemetry, custom.errors.CUSTOM_LOCATIONS_ENABLE_FAILED, False
    )
    _, properties = mock_telemetry.add_extension_event.call_args.args
    assert properties[custom.consts.Connected_Cluster_Arm_Id_Telemetry_Property] == (
        "/subscriptions/sub/resourceGroups/resource-group/providers/"
        "Microsoft.Kubernetes/connectedClusters/cluster"
    )


def test_get_custom_locations_oid_reports_empty_result(monkeypatch):
    cmd = _cmd_without_arm_id()
    graph_client = MagicMock()
    graph_client.service_principal_list.return_value = []
    monkeypatch.setattr(
        custom, "graph_client_factory", MagicMock(return_value=graph_client)
    )
    mock_telemetry = MagicMock()
    monkeypatch.setattr(custom.utils, "telemetry", mock_telemetry)

    oid = custom.get_custom_locations_oid(cmd, None)

    assert oid == ""
    _, properties = mock_telemetry.add_extension_event.call_args.args
    assert properties["Context.Default.AzureCLI.errorCode"] == "AZK8S0701"
    assert (
        properties["Context.Default.AzureCLI.errorFaultType"]
        == custom.consts.Custom_Locations_OID_Fetch_Fault_Type_CLOid_None
    )
    mock_telemetry.add_extension_event.assert_called_once()
    mock_telemetry.set_exception.assert_called_once()
    mock_telemetry.set_user_fault.assert_not_called()


def test_get_custom_locations_oid_reports_exception_and_uses_manual_oid(monkeypatch):
    cmd = _cmd_without_arm_id()
    expected_error = RuntimeError("Microsoft Graph request failed")
    monkeypatch.setattr(
        custom, "graph_client_factory", MagicMock(side_effect=expected_error)
    )
    mock_telemetry = MagicMock()
    monkeypatch.setattr(custom.utils, "telemetry", mock_telemetry)

    oid = custom.get_custom_locations_oid(cmd, "manual-oid")

    assert oid == "manual-oid"
    _, properties = mock_telemetry.add_extension_event.call_args.args
    assert properties["Context.Default.AzureCLI.errorCode"] == "AZK8S0701"
    assert (
        properties["Context.Default.AzureCLI.errorFaultType"]
        == custom.consts.Custom_Locations_OID_Fetch_Fault_Type_Exception
    )
    assert mock_telemetry.set_exception.call_args.kwargs["exception"] is expected_error
    mock_telemetry.add_extension_event.assert_called_once()
    mock_telemetry.set_exception.assert_called_once()
    mock_telemetry.set_user_fault.assert_not_called()


def test_check_cl_registration_reports_standardized_error(monkeypatch):
    cmd = _cmd_without_arm_id()
    expected_error = RuntimeError("provider registration request failed")
    monkeypatch.setattr(
        custom, "resource_providers_client", MagicMock(side_effect=expected_error)
    )
    mock_telemetry = MagicMock()
    monkeypatch.setattr(custom.utils, "telemetry", mock_telemetry)

    enabled, oid = custom.check_cl_registration_and_get_oid(cmd, None, "sub")

    assert enabled is False
    assert oid == ""
    _, properties = mock_telemetry.add_extension_event.call_args.args
    assert properties["Context.Default.AzureCLI.errorCode"] == "AZK8S0702"
    assert mock_telemetry.set_exception.call_args.kwargs["exception"] is expected_error
    mock_telemetry.add_extension_event.assert_called_once()
    mock_telemetry.set_exception.assert_called_once()
    mock_telemetry.set_user_fault.assert_not_called()


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


# ---------------- Tests for get_arc_proxy_skip_range_endpoints ----------------
def _proxy_cmd(active_directory="https://login.microsoftonline.com"):
    cmd = MagicMock()
    cmd.cli_ctx.cloud.endpoints.active_directory = active_directory
    return cmd


def test_arc_endpoints_public_cloud():
    assert get_arc_proxy_skip_range_endpoints(_proxy_cmd()) == [
        ".his.arc.azure.com",
        ".dp.kubernetesconfiguration.azure.com",
        ".guestconfiguration.azure.com",
    ]


@pytest.mark.parametrize(
    "active_directory,suffix",
    [
        ("https://login.chinacloudapi.cn", "cn"),
        ("https://login.microsoftonline.us", "us"),
        ("https://login.microsoftonline.microsoft.scloud", "microsoft.scloud"),
        ("https://login.microsoftonline.eaglex.ic.gov", "eaglex.ic.gov"),
    ],
    ids=["china", "usgov", "ussec", "usnat"],
)
def test_arc_endpoints_follow_the_cloud(active_directory, suffix):
    # Sovereign clouds only change the domain the endpoints are built on.
    assert get_arc_proxy_skip_range_endpoints(_proxy_cmd(active_directory)) == [
        f".his.arc.azure.{suffix}",
        f".dp.kubernetesconfiguration.azure.{suffix}",
        f".guestconfiguration.azure.{suffix}",
    ]


# ---------------- Tests for add_arc_proxy_skip_range_endpoints ----------------
ARC_SKIP_RANGE = (
    ".his.arc.azure.com"
    ",.dp.kubernetesconfiguration.azure.com"
    ",.guestconfiguration.azure.com"
)


@pytest.mark.parametrize(
    "no_proxy,expected",
    [
        ("", ARC_SKIP_RANGE),
        ("10.0.0.0/8", "10.0.0.0/8," + ARC_SKIP_RANGE),
        (
            "  10.0.0.0/8 , 192.168.0.0/16 ",
            "10.0.0.0/8,192.168.0.0/16," + ARC_SKIP_RANGE,
        ),
        (ARC_SKIP_RANGE, ARC_SKIP_RANGE),
        (
            ".HIS.ARC.AZURE.COM",
            (
                ".HIS.ARC.AZURE.COM"
                ",.dp.kubernetesconfiguration.azure.com"
                ",.guestconfiguration.azure.com"
            ),
        ),
    ],
    ids=["empty", "keeps-entry", "strips-whitespace", "already-present", "any-case"],
)
def test_add_arc_endpoints(no_proxy, expected):
    assert add_arc_proxy_skip_range_endpoints(_proxy_cmd(), no_proxy) == expected


# ---------------- Tests for has_arc_proxy_skip_range_endpoints ----------------
@pytest.mark.parametrize(
    "no_proxy,expected",
    [
        ("", False),
        ("10.0.0.0/8", False),
        ("eastus.his.arc.azure.com", False),
        (".his.arc.azure.cn", False),
        (ARC_SKIP_RANGE, True),
        ("10.0.0.0/8, .guestconfiguration.azure.com", True),
        (".HIS.ARC.AZURE.COM", True),
    ],
    ids=[
        "empty",
        "unrelated",
        "narrower-customer-entry",
        "another-cloud",
        "all-three",
        "one-of-them",
        "any-case",
    ],
)
def test_has_arc_endpoints(no_proxy, expected):
    assert has_arc_proxy_skip_range_endpoints(_proxy_cmd(), no_proxy) is expected


# ---------------- Tests for remove_arc_proxy_skip_range_endpoints ----------------
@pytest.mark.parametrize(
    "no_proxy,expected",
    [
        ("", ""),
        ("10.0.0.0/8", "10.0.0.0/8"),
        (ARC_SKIP_RANGE, ""),
        ("10.0.0.0/8," + ARC_SKIP_RANGE, "10.0.0.0/8"),
        (".HIS.ARC.AZURE.COM,10.0.0.0/8", "10.0.0.0/8"),
        ("eastus.his.arc.azure.com," + ARC_SKIP_RANGE, "eastus.his.arc.azure.com"),
    ],
    ids=[
        "empty",
        "nothing-to-remove",
        "all-three",
        "keeps-entry",
        "any-case",
        "keeps-narrower-customer-entry",
    ],
)
def test_remove_arc_endpoints(no_proxy, expected):
    assert remove_arc_proxy_skip_range_endpoints(_proxy_cmd(), no_proxy) == expected


# ---------------- Tests for resolve_arc_proxy_bypass ----------------
def _resolve(monkeypatch, no_proxy="", add="", clear="", cluster="", announce=True):
    # Autospec so a call that does not match the real signature fails here instead of
    # silently passing, which is how a missing 'cmd' argument once reached the CLI.
    helm = create_autospec(
        custom.get_all_helm_values, return_value={"global": {"noProxy": cluster}}
    )
    monkeypatch.setattr(custom, "get_all_helm_values", helm)
    result = resolve_arc_proxy_bypass(
        _proxy_cmd(),
        no_proxy,
        add,
        clear,
        "azure-arc",
        None,
        None,
        "helm",
        announce_applied=announce,
    )
    return result, helm


def test_resolve_leaves_the_skip_range_alone_when_the_update_says_nothing(monkeypatch):
    result, helm = _resolve(monkeypatch, cluster=ARC_SKIP_RANGE)
    assert result is None
    assert helm.called is False


@pytest.mark.parametrize(
    "keyword", ["Arc", " aRc "], ids=["exact", "any-case-and-spaces"]
)
def test_resolve_add_merges_into_the_current_skip_range(monkeypatch, keyword):
    result, _ = _resolve(monkeypatch, add=keyword, cluster="10.0.0.0/8")
    assert result == "10.0.0.0/8," + ARC_SKIP_RANGE


def test_resolve_add_applies_once_when_the_keyword_is_repeated(monkeypatch):
    result, _ = _resolve(monkeypatch, add="Arc,Arc", cluster="10.0.0.0/8")
    assert result == "10.0.0.0/8," + ARC_SKIP_RANGE


def test_resolve_add_applies_arc_when_combined_with_the_extension_keyword(monkeypatch):
    result, _ = _resolve(
        monkeypatch, add="Arc,Microsoft.AzureMonitor.Containers", cluster="10.0.0.0/8"
    )
    assert result == "10.0.0.0/8," + ARC_SKIP_RANGE


def test_resolve_ignores_the_extension_keyword_on_its_own(monkeypatch):
    # The two keywords control separate settings, so asking for the Container Insights
    # bypass on its own must leave the skip range untouched.
    result, helm = _resolve(monkeypatch, add="Microsoft.AzureMonitor.Containers")
    assert result is None
    assert helm.called is False


def test_resolve_add_does_not_duplicate_an_endpoint_the_user_typed(monkeypatch):
    # The customer can list one of our endpoints in --proxy-skip-range and still ask for
    # the bypass. It is not added twice, and their casing is left as they wrote it.
    result, helm = _resolve(
        monkeypatch, no_proxy=".his.ARC.azure.com,10.0.0.0/8", add="Arc"
    )
    assert result == (
        ".his.ARC.azure.com,10.0.0.0/8"
        ",.dp.kubernetesconfiguration.azure.com"
        ",.guestconfiguration.azure.com"
    )
    assert helm.called is False


def test_resolve_add_on_a_cluster_with_no_skip_range(monkeypatch):
    monkeypatch.setattr(custom, "get_all_helm_values", MagicMock(return_value={}))
    result = resolve_arc_proxy_bypass(
        _proxy_cmd(), "", "Arc", "", "azure-arc", None, None, "helm"
    )
    assert result == ARC_SKIP_RANGE


def test_resolve_add_with_a_new_skip_range_does_not_read_the_cluster(monkeypatch):
    # The new skip range replaces the old one outright, so there is nothing to merge.
    result, helm = _resolve(monkeypatch, no_proxy="192.168.0.0/16", add="Arc")
    assert result == "192.168.0.0/16," + ARC_SKIP_RANGE
    assert helm.called is False


def test_resolve_announces_the_bypass_when_it_is_applied(monkeypatch, capsys):
    _resolve(monkeypatch, add="Arc", cluster="10.0.0.0/8")
    assert consts.Proxy_Bypass_Arc_Applied_Message in capsys.readouterr().out


def test_resolve_leaves_the_announcement_to_connect(monkeypatch, capsys):
    # connect announces the bypass before it reaches the resolver, so the resolver stays
    # quiet instead of reporting the same thing twice in one command.
    result, _ = _resolve(monkeypatch, add="Arc", cluster="10.0.0.0/8", announce=False)
    assert result == "10.0.0.0/8," + ARC_SKIP_RANGE
    assert consts.Proxy_Bypass_Arc_Applied_Message not in capsys.readouterr().out


def test_resolve_clear_removes_only_the_arc_endpoints(monkeypatch):
    result, _ = _resolve(
        monkeypatch, clear="Arc", cluster="10.0.0.0/8," + ARC_SKIP_RANGE
    )
    assert result == "10.0.0.0/8"


def test_resolve_clear_leaves_a_cluster_without_the_bypass_alone(monkeypatch):
    result, _ = _resolve(monkeypatch, clear="Arc", cluster="10.0.0.0/8")
    assert result is None


def test_resolve_clear_uses_the_new_skip_range_as_the_base(monkeypatch):
    # --proxy-skip-range replaces the skip range, so the clear applies to what the
    # command ends up with rather than to the skip range being replaced.
    result, helm = _resolve(
        monkeypatch,
        no_proxy="192.168.0.0/16",
        clear="Arc",
        cluster="10.0.0.0/8," + ARC_SKIP_RANGE,
    )
    assert result == "192.168.0.0/16"
    assert helm.called is True


def test_resolve_clear_removes_the_endpoints_typed_into_the_new_skip_range(monkeypatch):
    result, _ = _resolve(
        monkeypatch,
        no_proxy="192.168.0.0/16," + ARC_SKIP_RANGE,
        clear="Arc",
        cluster="10.0.0.0/8," + ARC_SKIP_RANGE,
    )
    assert result == "192.168.0.0/16"


def test_resolve_clear_removes_the_endpoints_even_when_only_the_range_has_them(
    monkeypatch,
):
    # Nothing to clear on the cluster, but the customer typed the endpoints into the new
    # skip range, so honouring the clear still has to strip them.
    result, _ = _resolve(
        monkeypatch,
        no_proxy="192.168.0.0/16," + ARC_SKIP_RANGE,
        clear="Arc",
        cluster="10.0.0.0/8",
    )
    assert result == "192.168.0.0/16"


def test_resolve_clear_with_a_new_skip_range_that_has_nothing_to_remove(monkeypatch):
    warning = MagicMock()
    monkeypatch.setattr(custom.logger, "warning", warning)
    result, _ = _resolve(
        monkeypatch, no_proxy="192.168.0.0/16", clear="Arc", cluster="10.0.0.0/8"
    )
    assert result is None
    warning.assert_called_once_with(consts.Proxy_Bypass_Arc_Nothing_To_Clear_Warning)


def test_resolve_reapplies_the_bypass_when_the_skip_range_changes(monkeypatch):
    # --proxy-skip-range replaces the whole skip range, so a cluster that has the bypass
    # keeps it instead of silently losing the endpoints.
    result, _ = _resolve(
        monkeypatch, no_proxy="192.168.0.0/16", cluster="10.0.0.0/8," + ARC_SKIP_RANGE
    )
    assert result == "192.168.0.0/16," + ARC_SKIP_RANGE


def test_resolve_reports_the_carry_over_even_when_it_stays_quiet(monkeypatch):
    # Only the announcement is silenced, so a connect that changes the skip range still
    # reports the bypass it carried over.
    warning = MagicMock()
    monkeypatch.setattr(custom.logger, "warning", warning)
    result, _ = _resolve(
        monkeypatch,
        no_proxy="192.168.0.0/16",
        cluster="10.0.0.0/8," + ARC_SKIP_RANGE,
        announce=False,
    )
    assert result == "192.168.0.0/16," + ARC_SKIP_RANGE
    warning.assert_called_once_with(consts.Proxy_Bypass_Arc_Preserved_Warning)


def test_resolve_skip_range_change_without_the_bypass_stays_untouched(monkeypatch):
    result, _ = _resolve(monkeypatch, no_proxy="192.168.0.0/16", cluster="10.0.0.0/8")
    assert result is None
