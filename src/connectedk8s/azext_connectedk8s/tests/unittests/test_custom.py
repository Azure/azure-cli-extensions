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
from azure.cli.core.azclierror import (
    ArgumentUsageError,
    AzCLIError,
    FileOperationError,
    ValidationError,
)
from kubernetes.client.exceptions import ApiException

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
    validate_arc_proxy_bypass_clear,
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


def test_telemetry_catch_all_does_not_report_classified_error_twice(monkeypatch):
    expected = custom.AzCLIError("[AZK8S0400] ConnectedClusterCreateFailed")
    report_error = MagicMock()
    monkeypatch.setattr(custom.utils, "report_connectedk8s_error", report_error)

    @_telemetry_catch_all
    def command():
        raise expected

    with pytest.raises(custom.AzCLIError) as raised:
        command()

    assert raised.value is expected
    report_error.assert_not_called()


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


def test_load_kube_config_forwards_command_context(monkeypatch):
    cmd = MagicMock()
    expected = ValidationError("reported")
    report_error = MagicMock(return_value=expected)
    monkeypatch.setattr(
        custom.config,
        "load_kube_config",
        MagicMock(side_effect=RuntimeError("invalid kubeconfig")),
    )
    monkeypatch.setattr(custom.utils, "report_connectedk8s_error", report_error)

    with pytest.raises(ValidationError) as raised:
        custom.load_kube_config(None, None, False, cmd=cmd)

    assert raised.value is expected
    assert report_error.call_args.args[0] is cmd
    assert report_error.call_args.kwargs["user_fault"] is True
    assert report_error.call_args.kwargs["details"] == "invalid kubeconfig"


def test_check_kube_connection_forwards_command_context(monkeypatch):
    cmd = MagicMock()
    api_instance = MagicMock()
    api_instance.get_code.side_effect = RuntimeError("cluster unreachable")
    exception_handler = MagicMock(side_effect=ValidationError("reported"))
    monkeypatch.setattr(
        custom.kube_client, "VersionApi", MagicMock(return_value=api_instance)
    )
    monkeypatch.setattr(custom.utils, "kubernetes_exception_handler", exception_handler)

    with pytest.raises(ValidationError):
        custom.check_kube_connection(cmd=cmd)

    assert exception_handler.call_args.kwargs["cmd"] is cmd


def test_private_key_injection_forwards_command_context(monkeypatch):
    cmd = MagicMock()
    api_instance = MagicMock()
    api_instance.create_namespaced_secret.side_effect = ApiException(status=403)
    exception_handler = MagicMock(side_effect=ValidationError("reported"))
    monkeypatch.setattr(
        custom.utils,
        "ensure_arc_namespace_with_helm_metadata",
        MagicMock(),
    )
    monkeypatch.setattr(
        custom.utils.kube_client,
        "CoreV1Api",
        MagicMock(return_value=api_instance),
    )
    monkeypatch.setattr(custom.utils, "kubernetes_exception_handler", exception_handler)

    with pytest.raises(ValidationError):
        custom.utils.inject_onboarding_private_key_secret("private-key", cmd=cmd)

    assert exception_handler.call_args.kwargs["cmd"] is cmd


def test_namespace_cleanup_transient_lookup_failure_is_not_reported(monkeypatch):
    cmd = MagicMock()
    api_instance = MagicMock()
    api_instance.list_namespace.side_effect = [
        RuntimeError("cluster unreachable"),
        MagicMock(items=[]),
    ]
    exception_handler = MagicMock()
    sleep = MagicMock()
    monkeypatch.setattr(
        custom.utils.kube_client,
        "CoreV1Api",
        MagicMock(return_value=api_instance),
    )
    monkeypatch.setattr(custom.utils, "kubernetes_exception_handler", exception_handler)
    monkeypatch.setattr(custom.utils.time, "sleep", sleep)

    custom.utils.ensure_namespace_cleanup(cmd)

    exception_handler.assert_not_called()
    sleep.assert_not_called()


def test_namespace_cleanup_reports_persistent_lookup_failure_without_raising(
    monkeypatch,
):
    cmd = MagicMock()
    lookup_error = RuntimeError("cluster unreachable")
    api_instance = MagicMock()
    api_instance.list_namespace.side_effect = lookup_error
    exception_handler = MagicMock()
    monkeypatch.setattr(
        custom.utils.kube_client,
        "CoreV1Api",
        MagicMock(return_value=api_instance),
    )
    monkeypatch.setattr(custom.utils, "kubernetes_exception_handler", exception_handler)
    monkeypatch.setattr(custom.utils.time, "sleep", MagicMock())
    monkeypatch.setattr(
        custom.utils.time,
        "time",
        MagicMock(side_effect=[0, 0, 181, 181]),
    )

    custom.utils.ensure_namespace_cleanup(cmd)

    exception_handler.assert_called_once()
    assert exception_handler.call_args.args[0] is lookup_error
    assert exception_handler.call_args.kwargs["raise_error"] is False
    assert exception_handler.call_args.kwargs["cmd"] is cmd


@pytest.fixture
def onboarding_access_context(monkeypatch):
    cmd = MagicMock()
    cmd.cli_ctx.data = {}
    cmd.cli_ctx.cloud.endpoints.resource_manager = "https://management.azure.com"
    telemetry = MagicMock()
    monkeypatch.setattr(custom, "telemetry", telemetry)
    monkeypatch.setattr(custom.utils, "telemetry", telemetry)
    monkeypatch.setattr(custom.precheckutils, "telemetry", telemetry)
    for name, value in {
        "get_subscription_id": "subscription",
        "send_cloud_telemetry": "AzureCloud",
        "set_kube_config": "kubeconfig",
        "get_config_dp_endpoint": ("endpoint", "stable"),
        "get_kubectl_client_location": "kubectl",
        "get_helm_client_location": "helm",
    }.items():
        monkeypatch.setattr(custom, name, MagicMock(return_value=value))
    for name, value in {
        "validate_custom_token": (False, "eastus"),
        "check_provider_registrations": None,
        "get_values_file": None,
        "get_metadata": {},
    }.items():
        monkeypatch.setattr(custom.utils, name, MagicMock(return_value=value))
    monkeypatch.setattr(custom.config, "load_kube_config", MagicMock())
    version_api = MagicMock()
    version_api.get_code.return_value.git_version = "v1.30.0"
    monkeypatch.setattr(
        custom.kube_client, "VersionApi", MagicMock(return_value=version_api)
    )
    core_api = MagicMock()
    monkeypatch.setattr(
        custom.kube_client, "CoreV1Api", MagicMock(return_value=core_api)
    )
    permission = MagicMock(return_value=False)
    monkeypatch.setattr(custom.utils, "can_create_clusterrolebindings", permission)
    helm_install = MagicMock()
    monkeypatch.setattr(custom.utils, "helm_install_release", helm_install)
    return SimpleNamespace(
        cmd=cmd,
        telemetry=telemetry,
        core_api=core_api,
        permission=permission,
        helm_install=helm_install,
        version_api=version_api,
    )


@pytest.mark.parametrize("node_os", ["linux", "windows"])
@pytest.mark.parametrize("permission", [False, "Unknown"])
def test_onboarding_permission_failure_emits_one_fault(
    onboarding_access_context, node_os, permission
):
    ctx = onboarding_access_context
    ctx.core_api.list_node.return_value = V1NodeList(
        items=[create_node(labels={"kubernetes.io/os": node_os})]
    )
    ctx.permission.return_value = permission

    with pytest.raises(ValidationError, match="ClusterRoleBindingCreateForbidden"):
        custom.create_connectedk8s(
            ctx.cmd,
            MagicMock(),
            "rg",
            "cluster",
            infrastructure="azure_stack_hci",
            distribution="aks_edge_k3s",
        )

    ctx.telemetry.set_exception.assert_called_once()
    fault = ctx.telemetry.set_exception.call_args.kwargs
    assert (
        fault["fault_type"]
        == custom.consts.Cannot_Create_ClusterRoleBindings_Fault_Type
    )
    ctx.permission.assert_called_once()
    ctx.helm_install.assert_not_called()
    properties = ctx.telemetry.add_extension_event.call_args.args[1]
    assert properties[custom.consts.Telemetry_Error_Code_Key] == (
        custom.errors.CLUSTER_ROLE_BINDING_CREATE_FORBIDDEN.code
    )
    assert properties[
        custom.consts.Connected_Cluster_Arm_Id_Telemetry_Property
    ].endswith("/connectedClusters/cluster")
    warning_events = [
        call.args[1]
        for call in ctx.telemetry.add_extension_event.call_args_list
        if custom.consts.Telemetry_Warning_Code_Key in call.args[1]
    ]
    assert len(warning_events) == (0 if node_os == "linux" else 1)


@pytest.mark.parametrize("failure_point", ["kubeconfig", "connectivity"])
def test_onboarding_cluster_access_failure_is_not_reported_twice(
    onboarding_access_context, monkeypatch, failure_point
):
    ctx = onboarding_access_context
    if failure_point == "kubeconfig":
        monkeypatch.setattr(
            custom.config,
            "load_kube_config",
            MagicMock(side_effect=RuntimeError("invalid kubeconfig")),
        )
    else:
        ctx.version_api.get_code.side_effect = ApiException(status=403)

    with pytest.raises(AzCLIError):
        custom.create_connectedk8s(ctx.cmd, MagicMock(), "rg", "cluster")

    ctx.telemetry.set_exception.assert_called_once()
    ctx.core_api.list_node.assert_not_called()
    ctx.permission.assert_not_called()
    ctx.helm_install.assert_not_called()
    properties = ctx.telemetry.add_extension_event.call_args.args[1]
    assert properties[custom.consts.Telemetry_Error_Exception_Type_Key] == (
        "RuntimeError" if failure_point == "kubeconfig" else "ApiException"
    )
    if failure_point == "connectivity":
        assert properties[custom.consts.Telemetry_Error_Http_Status_Code_Key] == 403


@pytest.mark.parametrize("status", [401, 403, 404, 429, 500])
def test_private_key_failure_retains_status_and_emits_one_fault(monkeypatch, status):
    cmd = SimpleNamespace(cli_ctx=SimpleNamespace(data={}))
    telemetry = MagicMock()
    monkeypatch.setattr(custom.utils, "telemetry", telemetry)
    monkeypatch.setattr(custom, "telemetry", telemetry)
    monkeypatch.setattr(
        custom.utils, "ensure_arc_namespace_with_helm_metadata", MagicMock()
    )
    api = MagicMock()
    api.create_namespaced_secret.side_effect = ApiException(status=status)
    monkeypatch.setattr(
        custom.utils.kube_client, "CoreV1Api", MagicMock(return_value=api)
    )

    @_telemetry_catch_all
    def inject(cmd):
        custom.utils.inject_onboarding_private_key_secret("private-key", cmd=cmd)

    with pytest.raises(AzCLIError):
        inject(cmd)

    telemetry.set_exception.assert_called_once()
    properties = telemetry.add_extension_event.call_args.args[1]
    assert properties[custom.consts.Telemetry_Error_Http_Status_Code_Key] == status
    assert (
        properties[custom.consts.Telemetry_Error_Exception_Type_Key] == "ApiException"
    )
    assert properties[custom.consts.Telemetry_Error_Fault_Type_Key] == (
        custom.errors.KUBERNETES_PRIVATE_KEY_INJECTION_FAILED.fault_type
    )
    api.replace_namespaced_secret.assert_not_called()


@pytest.mark.parametrize("check", ["aks", "proxy"])
def test_kubeconfig_lookup_error_keeps_command_context(monkeypatch, check):
    arm_id = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Kubernetes/connectedClusters/cluster"
    cmd = SimpleNamespace(
        cli_ctx=SimpleNamespace(
            data={custom.consts.Connected_Cluster_Arm_Id_Telemetry_Context_Key: arm_id}
        )
    )
    telemetry = MagicMock()
    monkeypatch.setattr(custom.utils, "telemetry", telemetry)
    monkeypatch.setattr(
        custom,
        "KubeConfigMerger",
        MagicMock(side_effect=RuntimeError("invalid kubeconfig")),
    )
    with pytest.raises(FileOperationError):
        if check == "aks":
            custom.check_aks_cluster("kubeconfig", None, cmd=cmd)
        else:
            custom.check_proxy_kubeconfig("kubeconfig", None, "hash", cmd=cmd)

    telemetry.set_exception.assert_called_once()
    properties = telemetry.add_extension_event.call_args.args[1]
    assert (
        properties[custom.consts.Connected_Cluster_Arm_Id_Telemetry_Property] == arm_id
    )


def test_merge_kubernetes_configurations_does_not_rereport_az_cli_error(monkeypatch):
    expected = FileOperationError("already reported")
    report_error = MagicMock()
    monkeypatch.setattr(
        custom,
        "load_kubernetes_configuration",
        MagicMock(side_effect=expected),
    )
    monkeypatch.setattr(custom.utils, "report_connectedk8s_error", report_error)

    with pytest.raises(FileOperationError) as raised:
        custom.merge_kubernetes_configurations("existing", "addition", False)

    assert raised.value is expected
    report_error.assert_not_called()


def test_client_side_proxy_does_not_rereport_merge_az_cli_error(monkeypatch):
    expected = FileOperationError("already reported")
    process = MagicMock()
    response = MagicMock()
    response.text = '{"kubeconfigs": [{"value": "YXBpVmVyc2lvbjogdjE="}]}'

    monkeypatch.setattr(custom, "get_subscription_id", MagicMock(return_value="sub"))
    monkeypatch.setattr(custom, "Popen", MagicMock(return_value=process))
    monkeypatch.setattr(
        custom.proxylogic,
        "get_cluster_user_credentials",
        MagicMock(return_value=MagicMock()),
    )
    monkeypatch.setattr(
        custom.clientproxyutils,
        "prepare_clientproxy_data",
        MagicMock(return_value={"hybridConnectionConfig": {"expirationTime": 123}}),
    )
    monkeypatch.setattr(
        custom.proxylogic,
        "post_register_to_proxy",
        MagicMock(return_value=response),
    )
    monkeypatch.setattr(
        custom, "print_or_merge_credentials", MagicMock(side_effect=expected)
    )
    telemetry = MagicMock()
    monkeypatch.setattr(custom, "telemetry", telemetry)

    with pytest.raises(FileOperationError) as raised:
        custom.client_side_proxy(
            MagicMock(),
            "tenant",
            MagicMock(),
            "rg",
            "cluster",
            custom.ProxyStatus.FirstRun,
            ["clientproxy"],
            47010,
            47011,
            False,
            token="token",
        )

    assert raised.value is expected
    process.terminate.assert_called_once()
    telemetry.set_exception.assert_not_called()


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

ARC_ENDPOINTS_TEXT = ", ".join(ARC_SKIP_RANGE.split(","))
ARC_APPLIED_MESSAGE = consts.Proxy_Bypass_Arc_Applied_Message.format(
    endpoints=ARC_ENDPOINTS_TEXT
)
ARC_CLEARED_MESSAGE = consts.Proxy_Bypass_Arc_Cleared_Message.format(
    endpoints=ARC_ENDPOINTS_TEXT
)
ARC_PRESERVED_WARNING = consts.Proxy_Bypass_Arc_Preserved_Warning.format(
    endpoints=ARC_ENDPOINTS_TEXT
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


@pytest.mark.parametrize(
    "no_proxy,expected",
    [
        ("", False),
        ("10.0.0.0/8", False),
        (".his.arc.azure.com", False),
        ("10.0.0.0/8,.his.arc.azure.com,.guestconfiguration.azure.com", False),
        (ARC_SKIP_RANGE, True),
        ("10.0.0.0/8," + ARC_SKIP_RANGE, True),
        (ARC_SKIP_RANGE.upper(), True),
    ],
    ids=[
        "empty",
        "unrelated",
        "one-of-them",
        "two-of-them",
        "all-three",
        "keeps-entry",
        "any-case",
    ],
)
def test_has_every_arc_endpoint(no_proxy, expected):
    # The bypass always writes every endpoint, so only the full set marks it as applied.
    assert (
        has_arc_proxy_skip_range_endpoints(_proxy_cmd(), no_proxy, require_all=True)
        is expected
    )


def test_has_arc_endpoints_without_a_skip_range():
    # The CLI sends an empty string when --proxy-skip-range is left out, so this only
    # guards the helper against a caller that passes nothing at all.
    cmd = _proxy_cmd()
    assert has_arc_proxy_skip_range_endpoints(cmd, None) is False
    assert has_arc_proxy_skip_range_endpoints(cmd, None, require_all=True) is False


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


# ---------------- Tests for validate_arc_proxy_bypass_clear ----------------
@pytest.mark.parametrize(
    "no_proxy",
    [
        ".his.arc.azure.com",
        ".guestconfiguration.azure.com,10.0.0.0/8",
        ".his.arc.azure.com,.dp.kubernetesconfiguration.azure.com",
        ARC_SKIP_RANGE,
        "10.0.0.0/8," + ARC_SKIP_RANGE,
        ".HIS.ARC.AZURE.COM",
        " .his.arc.azure.com ",
    ],
    ids=[
        "one-endpoint",
        "one-endpoint-beside-a-customer-entry",
        "two-endpoints",
        "all-three",
        "all-three-beside-a-customer-entry",
        "any-case",
        "surrounding-spaces",
    ],
)
def test_validate_clear_refuses_a_skip_range_holding_arc_endpoints(no_proxy):
    # The skip range the caller typed has to survive, so the overlap is refused however many
    # endpoints it holds. The full set too, since it cannot be told from an applied bypass.
    with pytest.raises(ArgumentUsageError):
        validate_arc_proxy_bypass_clear(_proxy_cmd(), no_proxy, "Arc")


@pytest.mark.parametrize(
    "clear",
    ["Arc", " aRc ", "Arc,Microsoft.AzureMonitor.Containers"],
    ids=["exact", "any-case-and-spaces", "beside-the-extension-keyword"],
)
def test_validate_clear_refuses_however_the_keyword_is_written(clear):
    with pytest.raises(ArgumentUsageError):
        validate_arc_proxy_bypass_clear(_proxy_cmd(), ARC_SKIP_RANGE, clear)


@pytest.mark.parametrize(
    "no_proxy,clear",
    [
        ("", "Arc"),
        (None, "Arc"),
        ("10.0.0.0/8", "Arc"),
        ("eastus.his.arc.azure.com", "Arc"),
        (ARC_SKIP_RANGE, ""),
        (ARC_SKIP_RANGE, "Microsoft.AzureMonitor.Containers"),
    ],
    ids=[
        "clearing-on-its-own",
        "no-skip-range-at-all",
        "skip-range-without-arc-endpoints",
        "narrower-customer-entry",
        "nothing-cleared",
        "only-the-extension-cleared",
    ],
)
def test_validate_clear_allows_everything_else(no_proxy, clear):
    # Only the overlap is refused, so clearing on its own keeps working.
    assert validate_arc_proxy_bypass_clear(_proxy_cmd(), no_proxy, clear) is None


def test_validate_clear_recommends_the_order_that_works():
    # Setting the skip range first re-applies the bypass, so the order has to be named.
    with pytest.raises(ArgumentUsageError) as raised:
        validate_arc_proxy_bypass_clear(_proxy_cmd(), ARC_SKIP_RANGE, "Arc")
    assert (
        consts.Proxy_Bypass_Arc_Clear_Conflict_Recommendation
        in raised.value.recommendations
    )


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
    out = capsys.readouterr().out
    # The endpoints are named in the message, so each one has to appear as written.
    assert ARC_APPLIED_MESSAGE in out
    for endpoint in ARC_SKIP_RANGE.split(","):
        assert endpoint in out
    # The flag was dropped from this message, so it must not creep back in.
    assert "--proxy-skip-range" not in out


def test_resolve_leaves_the_announcement_to_connect(monkeypatch, capsys):
    # connect announces this itself once it knows the agents are updated, so the
    # resolver stays quiet rather than reporting the same thing twice.
    result, _ = _resolve(monkeypatch, add="Arc", cluster="10.0.0.0/8", announce=False)
    assert result == "10.0.0.0/8," + ARC_SKIP_RANGE
    assert ARC_APPLIED_MESSAGE not in capsys.readouterr().out


def test_resolve_clear_names_the_endpoints_it_removes(monkeypatch, capsys):
    # Clearing reports the same endpoints the bypass named when it was applied.
    _resolve(monkeypatch, clear="Arc", cluster="10.0.0.0/8," + ARC_SKIP_RANGE)
    out = capsys.readouterr().out
    assert ARC_CLEARED_MESSAGE in out
    for endpoint in ARC_SKIP_RANGE.split(","):
        assert endpoint in out


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


def test_resolve_clear_keeps_an_endpoint_the_customer_listed(monkeypatch):
    # One endpoint on its own is not the bypass this CLI applies, so the clear leaves it
    # for the customer to remove through --proxy-skip-range.
    warning = MagicMock()
    monkeypatch.setattr(custom.logger, "warning", warning)
    result, _ = _resolve(
        monkeypatch, clear="Arc", cluster="10.0.0.0/8,.his.arc.azure.com"
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
    # The warning names the endpoints it kept, rather than describing them.
    warning.assert_called_once_with(ARC_PRESERVED_WARNING)
    for endpoint in ARC_SKIP_RANGE.split(","):
        assert endpoint in ARC_PRESERVED_WARNING


def test_resolve_skip_range_change_without_the_bypass_stays_untouched(monkeypatch):
    result, _ = _resolve(monkeypatch, no_proxy="192.168.0.0/16", cluster="10.0.0.0/8")
    assert result is None


def test_resolve_skip_range_change_keeps_an_endpoint_the_customer_listed(monkeypatch):
    # One endpoint on its own is not the bypass this CLI applies, so the skip range is
    # stored as it was typed rather than widened into the full set.
    warning = MagicMock()
    monkeypatch.setattr(custom.logger, "warning", warning)
    result, _ = _resolve(
        monkeypatch,
        no_proxy="192.168.0.0/16,.his.arc.azure.com",
        cluster="10.0.0.0/8,.his.arc.azure.com",
    )
    assert result is None
    assert warning.called is False
