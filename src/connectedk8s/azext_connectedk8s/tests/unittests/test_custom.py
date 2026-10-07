# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import os
import sys
from base64 import b64decode, b64encode
from copy import deepcopy
from types import SimpleNamespace
from typing import Dict, Optional
from unittest.mock import MagicMock, create_autospec

import pytest
from azure.cli.core.azclierror import (
    ArgumentUsageError,
    AzCLIError,
    FileOperationError,
    MutuallyExclusiveArgumentError,
    RequiredArgumentMissingError,
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
    assert report_error.call_args.kwargs["operation"] == "command"
    assert report_error.call_args.kwargs["details"] == "failed"
    assert isinstance(report_error.call_args.kwargs["exception"], RuntimeError)


@pytest.mark.parametrize(
    "handler",
    [
        custom.create_connectedk8s,
        custom.update_connected_cluster,
        custom.upgrade_agents,
        custom.delete_connectedk8s,
        custom.enable_features,
        custom.disable_features,
        custom.list_connectedk8s,
        custom.get_connectedk8s,
        custom.client_side_proxy_wrapper,
        custom.troubleshoot,
    ],
)
def test_registered_command_handlers_use_telemetry_catch_all(handler):
    assert hasattr(handler, "__wrapped__")


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


def test_enable_features_reports_invalid_argument_value(monkeypatch):
    cmd = _cmd_without_arm_id()
    client = MagicMock()
    client.get.return_value = SimpleNamespace(kind=None, private_link_state="Enabled")
    monkeypatch.setattr(
        custom.utils, "validate_custom_token", MagicMock(return_value=(False, None))
    )
    monkeypatch.setattr(custom, "get_subscription_id", lambda _cli_ctx: "sub")
    monkeypatch.setattr(
        custom.utils,
        "check_features_to_update",
        MagicMock(return_value=(True, False, False)),
    )
    mock_telemetry = MagicMock()
    monkeypatch.setattr(custom.utils, "telemetry", mock_telemetry)

    with pytest.raises(custom.InvalidArgumentValueError) as raised:
        custom.enable_features(
            cmd, client, "resource-group", "cluster", ["cluster-connect"]
        )

    assert str(raised.value).startswith("[AZK8S0100] InvalidArgumentValue:")
    _assert_standardized_telemetry(
        mock_telemetry, custom.errors.INVALID_ARGUMENT_VALUE, True
    )


@pytest.mark.parametrize(
    "https_proxy,disable_proxy,error,exception_type",
    [
        (
            "",
            False,
            custom.errors.UPDATE_NO_PARAMETERS,
            RequiredArgumentMissingError,
        ),
        (
            "https://proxy.example",
            True,
            custom.errors.UPDATE_PROXY_PARAMETER_CONFLICT,
            MutuallyExclusiveArgumentError,
        ),
    ],
    ids=["no-parameters", "proxy-conflict"],
)
def test_update_reports_standardized_parameter_errors(
    monkeypatch, https_proxy, disable_proxy, error, exception_type
):
    cmd = _cmd_without_arm_id()
    client = MagicMock()
    client.get.return_value = SimpleNamespace(kind=None)
    monkeypatch.setattr(
        custom, "send_cloud_telemetry", MagicMock(return_value="AzureCloud")
    )
    monkeypatch.setattr(custom, "set_kube_config", lambda value: value)
    monkeypatch.setattr(custom, "escape_proxy_settings", lambda value: value)
    monkeypatch.setattr(custom.utils, "get_subscription_id", lambda _cli_ctx: "sub")
    monkeypatch.setattr(
        custom,
        "add_config_protected_settings",
        MagicMock(return_value=({}, {}, {})),
    )
    mock_telemetry = MagicMock()
    monkeypatch.setattr(custom.utils, "telemetry", mock_telemetry)

    with pytest.raises(exception_type) as raised:
        custom.update_connected_cluster(
            cmd,
            client,
            "resource-group",
            "cluster",
            https_proxy=https_proxy,
            disable_proxy=disable_proxy,
        )

    assert str(raised.value).startswith(f"[{error.code}] {error.name}:")
    _assert_standardized_telemetry(mock_telemetry, error, True)


def test_proxy_cert_path_reports_not_found(monkeypatch):
    mock_telemetry = MagicMock()
    monkeypatch.setattr(custom.utils, "telemetry", mock_telemetry)
    monkeypatch.setattr(custom.os.path, "exists", MagicMock(return_value=False))

    with pytest.raises(custom.InvalidArgumentValueError) as raised:
        custom._validate_proxy_cert_path(_cmd_without_arm_id(), "missing-cert.pem")

    assert str(raised.value).startswith("[AZK8S0103] ProxyCertificatePathNotFound:")
    assert "missing-cert.pem" in str(raised.value)
    _assert_standardized_telemetry(
        mock_telemetry, custom.errors.PROXY_CERT_PATH_NOT_FOUND, True
    )


def test_private_link_scope_location_reports_mismatch(monkeypatch):
    mock_telemetry = MagicMock()
    monkeypatch.setattr(custom.utils, "telemetry", mock_telemetry)

    with pytest.raises(custom.ArgumentUsageError) as raised:
        custom._validate_private_link_scope_location(
            _cmd_without_arm_id(), "westus", "eastus"
        )

    assert str(raised.value).startswith("[AZK8S0105] PrivateLinkScopeLocationMismatch:")
    _assert_standardized_telemetry(
        mock_telemetry, custom.errors.PRIVATE_LINK_SCOPE_LOCATION_MISMATCH, True
    )


@pytest.mark.parametrize(
    "gateway_resource_id",
    [
        "not-an-arm-id",
        "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/account",
    ],
    ids=["malformed", "wrong-resource-type"],
)
def test_gateway_resource_id_reports_invalid_id(monkeypatch, gateway_resource_id):
    mock_telemetry = MagicMock()
    monkeypatch.setattr(custom.utils, "telemetry", mock_telemetry)

    with pytest.raises(custom.InvalidArgumentValueError) as raised:
        custom._validate_gateway_resource_id(_cmd_without_arm_id(), gateway_resource_id)

    assert str(raised.value).startswith("[AZK8S0106] InvalidGatewayArmId:")
    _assert_standardized_telemetry(
        mock_telemetry, custom.errors.INVALID_GATEWAY_ARM_ID, True
    )


def test_gateway_resource_id_accepts_arc_gateway(monkeypatch):
    mock_telemetry = MagicMock()
    monkeypatch.setattr(custom.utils, "telemetry", mock_telemetry)
    gateway_resource_id = (
        "/subscriptions/00000000-0000-0000-0000-000000000000/"
        "resourceGroups/rg/providers/Microsoft.HybridCompute/gateways/gateway"
    )

    custom._validate_gateway_resource_id(_cmd_without_arm_id(), gateway_resource_id)

    mock_telemetry.add_extension_event.assert_not_called()
    mock_telemetry.set_exception.assert_not_called()


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


def test_private_key_injection_patches_existing_secret(monkeypatch):
    api_instance = MagicMock()
    api_instance.create_namespaced_secret.side_effect = ApiException(status=409)
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

    custom.utils.inject_onboarding_private_key_secret("private-key")

    api_instance.patch_namespaced_secret.assert_called_once()
    name, namespace, body = api_instance.patch_namespaced_secret.call_args.args
    assert name == consts.Onboarding_PrivateKey_Secret_Name
    assert namespace == consts.Arc_Namespace
    assert body.string_data == {
        consts.Onboarding_PrivateKey_Secret_Data_Key: "private-key"
    }
    assert body.metadata.labels == {"app.kubernetes.io/managed-by": "Helm"}
    assert body.metadata.annotations["meta.helm.sh/release-name"] == (
        consts.Helm_Release_Name
    )
    api_instance.replace_namespaced_secret.assert_not_called()


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
    api.patch_namespaced_secret.assert_not_called()


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
GATEWAY_RESOURCE_ID = (
    "/subscriptions/00000000-0000-0000-0000-000000000000/"
    "resourceGroups/rg/providers/Microsoft.HybridCompute/gateways/gateway"
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
    # Presence alone does not establish ownership.
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


# ---------------- Tests for resolve_arc_proxy_bypass ----------------
def _arc_release_values(result):
    no_proxy, encoded_state = result
    namespace, key = consts.Proxy_Bypass_Arc_Helm_Value.split(".")
    return {
        "global": {"noProxy": no_proxy},
        namespace: {key: None if encoded_state == "null" else encoded_state},
    }


def _owned_arc_values(user_no_proxy):
    return _arc_release_values(
        custom.build_arc_proxy_bypass_settings(_proxy_cmd(), user_no_proxy)
    )


def _assert_arc_result(result, no_proxy, user_no_proxy):
    assert result is not None
    assert result[0] == no_proxy
    assert json.loads(b64decode(result[1], validate=True)) == {
        "userNoProxy": user_no_proxy,
        "noProxy": no_proxy,
    }


def _resolve(
    monkeypatch,
    no_proxy=None,
    add="",
    clear="",
    cluster=None,
    owned_range=None,
    announce=True,
):
    values = (
        {"global": {"noProxy": cluster or ""}}
        if owned_range is None
        else _owned_arc_values(owned_range)
    )
    if cluster is not None:
        values["global"]["noProxy"] = cluster
    helm = create_autospec(custom.get_all_helm_values, return_value=values)
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
    result, helm = _resolve(monkeypatch, owned_range="10.0.0.0/8")
    assert result is None
    helm.assert_not_called()


@pytest.mark.parametrize(
    "keyword",
    ["Arc", " aRc ", "Arc,Arc", "Arc,Microsoft.AzureMonitor.Containers"],
)
def test_resolve_add_merges_into_the_current_skip_range(monkeypatch, keyword):
    result, _ = _resolve(monkeypatch, add=keyword, cluster="10.0.0.0/8")
    _assert_arc_result(result, "10.0.0.0/8," + ARC_SKIP_RANGE, "10.0.0.0/8")


def test_resolve_ignores_the_extension_keyword_on_its_own(monkeypatch):
    result, helm = _resolve(monkeypatch, add="Microsoft.AzureMonitor.Containers")
    assert result is None
    helm.assert_not_called()


@pytest.mark.parametrize(
    "skip_range,expected",
    [
        (".his.arc.azure.com", ARC_SKIP_RANGE),
        (
            ".his.arc.azure.com,.dp.kubernetesconfiguration.azure.com",
            ARC_SKIP_RANGE,
        ),
        (ARC_SKIP_RANGE, ARC_SKIP_RANGE),
        (
            ".his.ARC.azure.com,10.0.0.0/8,.HIS.ARC.AZURE.COM",
            (
                ".his.ARC.azure.com,10.0.0.0/8,"
                ".dp.kubernetesconfiguration.azure.com,.guestconfiguration.azure.com"
            ),
        ),
    ],
)
def test_resolve_overlap_is_deduplicated_warned_and_preserved_on_clear(
    monkeypatch, skip_range, expected
):
    warning = MagicMock()
    monkeypatch.setattr(custom.logger, "warning", warning)
    result, helm = _resolve(monkeypatch, no_proxy=skip_range, add="Arc")
    _assert_arc_result(result, expected, skip_range)
    warning.assert_called_once_with(consts.Proxy_Bypass_Arc_Overlap_Warning)

    helm.return_value = _arc_release_values(result)
    cleared = resolve_arc_proxy_bypass(
        _proxy_cmd(), None, "", "Arc", "azure-arc", None, None, "helm"
    )
    assert cleared == (skip_range, "null")


def test_resolve_add_on_a_cluster_with_no_skip_range(monkeypatch):
    monkeypatch.setattr(custom, "get_all_helm_values", MagicMock(return_value={}))
    result = resolve_arc_proxy_bypass(
        _proxy_cmd(), None, "Arc", "", "azure-arc", None, None, "helm"
    )
    _assert_arc_result(result, ARC_SKIP_RANGE, "")


def test_resolve_add_with_a_new_range_replaces_only_the_range(monkeypatch):
    result, helm = _resolve(
        monkeypatch, no_proxy="192.168.0.0/16", add="Arc", owned_range="10.0.0.0/8"
    )
    _assert_arc_result(result, "192.168.0.0/16," + ARC_SKIP_RANGE, "192.168.0.0/16")
    helm.assert_called_once()


def test_resolve_announces_the_bypass_when_it_is_applied(monkeypatch, capsys):
    _resolve(monkeypatch, add="Arc", cluster="10.0.0.0/8")
    out = capsys.readouterr().out
    assert ARC_APPLIED_MESSAGE in out
    assert "--clear-proxy-bypass Arc" in out


def test_resolve_leaves_the_announcement_to_connect(monkeypatch, capsys):
    result, _ = _resolve(monkeypatch, add="Arc", cluster="10.0.0.0/8", announce=False)
    _assert_arc_result(result, "10.0.0.0/8," + ARC_SKIP_RANGE, "10.0.0.0/8")
    assert ARC_APPLIED_MESSAGE not in capsys.readouterr().out


def test_resolve_clear_reports_the_disabled_arc_contribution(monkeypatch, capsys):
    _resolve(monkeypatch, clear="Arc", owned_range="10.0.0.0/8")
    assert ARC_CLEARED_MESSAGE in capsys.readouterr().out


@pytest.mark.parametrize(
    "skip_range",
    ["", "10.0.0.0/8"],
)
def test_resolve_clear_keeps_the_saved_skip_range(monkeypatch, skip_range):
    result, _ = _resolve(monkeypatch, clear="Arc", owned_range=skip_range)
    assert result == (skip_range, "null")


@pytest.mark.parametrize(
    "cluster",
    ["", "10.0.0.0/8", ".his.arc.azure.com", ARC_SKIP_RANGE],
)
def test_resolve_clear_without_ownership_does_not_remove_matching_entries(
    monkeypatch, cluster
):
    warning = MagicMock()
    monkeypatch.setattr(custom.logger, "warning", warning)
    result, _ = _resolve(monkeypatch, clear="Arc", cluster=cluster)
    assert result is None
    warning.assert_called_once_with(consts.Proxy_Bypass_Arc_Nothing_To_Clear_Warning)


@pytest.mark.parametrize("skip_range", ["", "192.168.0.0/16", ARC_SKIP_RANGE])
def test_resolve_clear_keeps_all_entries_in_a_new_skip_range(monkeypatch, skip_range):
    result, _ = _resolve(
        monkeypatch,
        no_proxy=skip_range,
        clear="Arc",
        owned_range="10.0.0.0/8",
    )
    assert result == (skip_range, "null")


def test_resolve_clear_without_ownership_leaves_new_range_to_the_normal_path(
    monkeypatch,
):
    result, _ = _resolve(
        monkeypatch,
        no_proxy="192.168.0.0/16," + ARC_SKIP_RANGE,
        clear="Arc",
        cluster="10.0.0.0/8",
    )
    assert result is None


@pytest.mark.parametrize(
    "skip_range,expected",
    [("", ARC_SKIP_RANGE), ("192.168.0.0/16", "192.168.0.0/16," + ARC_SKIP_RANGE)],
)
def test_resolve_range_replacement_preserves_enabled_arc(
    monkeypatch, skip_range, expected
):
    result, _ = _resolve(monkeypatch, no_proxy=skip_range, owned_range="10.0.0.0/8")
    _assert_arc_result(result, expected, skip_range)


def test_resolve_reports_the_carry_over_even_when_it_stays_quiet(monkeypatch):
    warning = MagicMock()
    monkeypatch.setattr(custom.logger, "warning", warning)
    result, _ = _resolve(
        monkeypatch, no_proxy="192.168.0.0/16", owned_range="10.0.0.0/8", announce=False
    )
    _assert_arc_result(result, "192.168.0.0/16," + ARC_SKIP_RANGE, "192.168.0.0/16")
    warning.assert_called_once_with(ARC_PRESERVED_WARNING)


@pytest.mark.parametrize(
    "cluster", ["10.0.0.0/8", ".his.arc.azure.com", ARC_SKIP_RANGE]
)
def test_resolve_replacement_does_not_infer_ownership_from_endpoints(
    monkeypatch, cluster
):
    warning = MagicMock()
    monkeypatch.setattr(custom.logger, "warning", warning)
    result, _ = _resolve(monkeypatch, no_proxy="192.168.0.0/16", cluster=cluster)
    assert result is None
    warning.assert_not_called()


def test_resolve_add_records_ownership_when_all_endpoints_already_exist(monkeypatch):
    result, _ = _resolve(monkeypatch, add="Arc", cluster=ARC_SKIP_RANGE)
    _assert_arc_result(result, ARC_SKIP_RANGE, ARC_SKIP_RANGE)


def test_resolve_repeated_add_does_not_transfer_arc_entries_to_the_skip_range(
    monkeypatch,
):
    result, _ = _resolve(monkeypatch, add="Arc", owned_range="10.0.0.0/8")
    _assert_arc_result(result, "10.0.0.0/8," + ARC_SKIP_RANGE, "10.0.0.0/8")


def test_resolve_replacement_then_clear_does_not_restore_previous_overlap(monkeypatch):
    result, helm = _resolve(
        monkeypatch, no_proxy="1.1.1.1", owned_range=".his.arc.azure.com"
    )
    _assert_arc_result(result, "1.1.1.1," + ARC_SKIP_RANGE, "1.1.1.1")
    helm.return_value = _arc_release_values(result)
    cleared = resolve_arc_proxy_bypass(
        _proxy_cmd(), None, "", "Arc", "azure-arc", None, None, "helm"
    )
    assert cleared == ("1.1.1.1", "null")
    helm.return_value = _arc_release_values(cleared)
    assert (
        resolve_arc_proxy_bypass(
            _proxy_cmd(), None, "", "Arc", "azure-arc", None, None, "helm"
        )
        is None
    )


@pytest.mark.parametrize(
    "skip_range",
    ["", "10.0.0.0/8,192.168.0.0/16", "true", "null", "123", "{example}", r"a\b"],
)
def test_arc_ownership_record_round_trips_without_a_state_version(skip_range):
    result = custom.build_arc_proxy_bypass_settings(_proxy_cmd(), skip_range)
    state = json.loads(b64decode(result[1], validate=True))
    assert set(state) == {"userNoProxy", "noProxy"}
    assert state["userNoProxy"] == skip_range
    assert "," not in result[1]
    assert "\\" not in result[1]
    assert (
        custom.get_arc_proxy_bypass_user_range(
            _proxy_cmd(), _arc_release_values(result), result[0]
        )
        == skip_range
    )


@pytest.mark.parametrize("namespace_value", [None, {}, {"arcProxyBypass": None}])
def test_missing_or_cleared_arc_record_is_not_an_error(namespace_value):
    assert (
        custom.get_arc_proxy_bypass_user_range(
            _proxy_cmd(), {"connectedk8sCli": namespace_value}, ARC_SKIP_RANGE
        )
        is None
    )


@pytest.mark.parametrize("encoded", ["", "not-base64", "e30=", True])
def test_malformed_arc_ownership_is_not_treated_as_absent(encoded):
    with pytest.raises(ValidationError, match=r"\[AZK8S0107\]"):
        custom.get_arc_proxy_bypass_user_range(
            _proxy_cmd(),
            {"connectedk8sCli": {"arcProxyBypass": encoded}},
            ARC_SKIP_RANGE,
        )


@pytest.mark.parametrize(
    "record",
    [
        [],
        {"userNoProxy": "1.1.1.1"},
        {"userNoProxy": False, "noProxy": ARC_SKIP_RANGE},
        {"userNoProxy": "", "noProxy": None},
        {"userNoProxy": "", "noProxy": ARC_SKIP_RANGE, "unknown": True},
    ],
)
def test_arc_ownership_requires_the_expected_string_fields(record):
    encoded = b64encode(json.dumps(record).encode("utf-8")).decode("ascii")
    with pytest.raises(ValidationError, match=r"\[AZK8S0107\]"):
        custom.get_arc_proxy_bypass_user_range(
            _proxy_cmd(),
            {"connectedk8sCli": {"arcProxyBypass": encoded}},
            ARC_SKIP_RANGE,
        )


def test_arc_ownership_rejects_an_invalid_namespace():
    with pytest.raises(ValidationError, match=r"\[AZK8S0107\]"):
        custom.get_arc_proxy_bypass_user_range(
            _proxy_cmd(), {"connectedk8sCli": "invalid"}, ARC_SKIP_RANGE
        )


@pytest.mark.parametrize(
    "action", [{"no_proxy": "2.2.2.2"}, {"add": "Arc"}, {"clear": "Arc"}]
)
def test_resolve_rejects_stale_ownership(monkeypatch, action):
    with pytest.raises(ValidationError, match="does not match"):
        _resolve(
            monkeypatch,
            owned_range="1.1.1.1",
            cluster="2.2.2.2," + ARC_SKIP_RANGE,
            **action,
        )


def test_arc_ownership_comparison_ignores_order_case_and_whitespace():
    values = _owned_arc_values("1.1.1.1")
    current = " , ".join(reversed(values["global"]["noProxy"].upper().split(",")))
    current += ",1.1.1.1"
    assert (
        custom.get_arc_proxy_bypass_user_range(_proxy_cmd(), values, current)
        == "1.1.1.1"
    )


@pytest.mark.parametrize(
    "no_proxy,add,clear",
    [(None, "Arc", ""), ("1.1.1.1", "", ""), (None, "", "Arc")],
)
def test_resolve_preserves_helm_read_errors(monkeypatch, no_proxy, add, clear):
    expected = AzCLIError("Helm values could not be read")
    monkeypatch.setattr(custom, "get_all_helm_values", MagicMock(side_effect=expected))
    with pytest.raises(AzCLIError) as raised:
        resolve_arc_proxy_bypass(
            _proxy_cmd(), no_proxy, add, clear, "azure-arc", None, None, "helm"
        )
    assert raised.value is expected


def test_arc_ownership_error_is_registered():
    assert (
        custom.errors.ERROR_CATALOG["AZK8S0107"]
        is custom.errors.PROXY_BYPASS_STATE_INVALID
    )
    assert (
        custom.errors.FAULT_TYPE_CATALOG[consts.Proxy_Bypass_Arc_State_Fault_Type]
        is custom.errors.PROXY_BYPASS_STATE_INVALID
    )


@pytest.mark.parametrize("explicit", [False, True])
def test_empty_proxy_range_is_only_written_when_explicit(explicit):
    settings, protected, redacted = custom.add_config_protected_settings(
        "", "", "", "", None, None, None, no_proxy_explicit=explicit
    )
    if explicit:
        assert settings == {"proxy": {}}
        assert protected == {"proxy": {"no_proxy": ""}}
        assert redacted == {"proxy": {"no_proxy": "redacted:proxy:no_proxy"}}
    else:
        assert settings == protected == redacted == {}


@pytest.fixture
def proxy_command_environment(monkeypatch):
    cluster = SimpleNamespace(
        kind=None,
        id="/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Kubernetes/connectedClusters/cluster",
        name="cluster",
        location="eastus",
        distribution="generic",
        infrastructure="generic",
        agent_version="1.35.3",
        agent_public_key_certificate="test-public-key",
        identity=SimpleNamespace(principal_id="test-principal"),
    )
    dp_payload = SimpleNamespace()
    helm_dp = {"repositoryPath": "example.invalid/arc:1.35.3", "helmValuesContent": {}}
    custom_results = {
        "send_cloud_telemetry": "AZUREPUBLICCLOUD",
        "get_subscription_id": "sub",
        "get_config_dp_endpoint": ("https://dp.example", "stable"),
        "load_kube_config": None,
        "check_kube_connection": "v1.31.0",
        "check_arm64_node": False,
        "check_linux_node": True,
        "check_aks_cluster": False,
        "get_kubernetes_distro": "generic",
        "get_kubernetes_infra": "generic",
        "_get_kubernetes_client_locations": ("kubectl", "helm"),
        "get_helm_client_location": "helm",
        "cf_resource_groups": MagicMock(),
        "connected_cluster_exists": False,
        "resource_group_exists": True,
        "crd_cleanup_force_delete": None,
        "_generate_key_pair": MagicMock(),
        "get_public_key": "test-public-key",
        "get_private_key": "test-private-key",
        "check_cl_registration_and_get_oid": (False, None),
        "validate_release_namespace": "azure-arc",
        "get_all_helm_values": {},
        "get_cc_resource": cluster,
        "update_connected_cluster_internal": cluster,
        "put_cc_resource": (dp_payload, cluster),
        "poll_for_agent_state": (True, cluster),
        "check_operation_support": None,
    }
    utils_results = {
        "validate_custom_token": (False, "eastus"),
        "set_connected_cluster_arm_id_telemetry_context": None,
        "check_provider_registrations": None,
        "get_values_file": None,
        "get_metadata": {},
        "validate_node_api_response": MagicMock(),
        "can_create_clusterrolebindings": True,
        "add_connectedk8s_telemetry_event": None,
        "validate_connect_rp_location": None,
        "get_release_namespace": None,
        "get_helm_values": helm_dp,
        "health_check_dp": True,
        "get_helm_registry": helm_dp["repositoryPath"],
        "get_chart_path": "chart",
        "inject_onboarding_private_key_secret": None,
        "helm_install_release": None,
        "helm_update_agent": None,
        "update_gateway_cluster_link": None,
    }
    for module, results in [(custom, custom_results), (custom.utils, utils_results)]:
        for name, result in results.items():
            monkeypatch.setattr(
                module,
                name,
                create_autospec(getattr(module, name), return_value=result),
            )
    api = MagicMock()
    api.read_namespaced_config_map.return_value = SimpleNamespace(
        data={
            "AZURE_RESOURCE_GROUP": "rg",
            "AZURE_RESOURCE_NAME": "cluster",
            "AZURE_ARC_AUTOUPDATE": "false",
        }
    )
    monkeypatch.setattr(custom.kube_client, "CoreV1Api", MagicMock(return_value=api))
    monkeypatch.setattr(custom.telemetry, "add_extension_event", MagicMock())
    monkeypatch.setattr(
        custom.containerinsightsutils,
        "sync_container_insights_proxy_bypass_configmap",
        MagicMock(),
    )
    monkeypatch.setattr(
        custom.containerinsightsutils,
        "remove_container_insights_proxy_bypass_configmap",
        MagicMock(),
    )
    monkeypatch.setenv("AZURE_LOCAL_DISCONNECTED", "true")
    for name in ("HELMREGISTRY", "HELMREPONAME", "HELMREPOURL"):
        monkeypatch.delenv(name, raising=False)
    return SimpleNamespace(
        cmd=_proxy_cmd(),
        client=MagicMock(get=MagicMock(return_value=cluster)),
        cluster=cluster,
        dp_payload=dp_payload,
        helm_dp=helm_dp,
    )


def _assert_arc_helm_payload(payload, no_proxy, user_no_proxy):
    assert payload["global.noProxy"] == no_proxy.replace(",", r"\,").replace("/", r"\/")
    _assert_arc_result(
        (no_proxy, payload[consts.Proxy_Bypass_Arc_Helm_Value]), no_proxy, user_no_proxy
    )


def _assert_proxy_configuration_has_no_ownership(environment):
    configurations = environment.dp_payload.arc_agentry_configurations
    assert len(configurations) == 1
    assert configurations[0].feature == "proxy"
    assert configurations[0].protected_settings == {
        "no_proxy": "redacted:proxy:no_proxy"
    }


@pytest.mark.parametrize("no_proxy", ["", "1.1.1.1"])
def test_update_with_only_protected_no_proxy_keeps_the_no_parameters_error(
    proxy_command_environment, no_proxy
):
    env = proxy_command_environment
    with pytest.raises(
        RequiredArgumentMissingError, match=r"\[AZK8S0101\] UpdateNoParameters"
    ):
        custom.update_connected_cluster(
            env.cmd,
            env.client,
            "rg",
            "cluster",
            configuration_protected_settings={"proxy": {"no_proxy": no_proxy}},
        )
    custom.get_all_helm_values.assert_not_called()
    custom.load_kube_config.assert_not_called()
    custom.update_connected_cluster_internal.assert_not_called()
    custom.put_cc_resource.assert_not_called()
    custom.utils.helm_update_agent.assert_not_called()


def test_update_generic_proxy_settings_with_other_options_keep_existing_processing(
    proxy_command_environment,
):
    env = proxy_command_environment
    env.helm_dp["helmValuesContent"]["global.noProxy"] = "redacted:proxy:no_proxy"
    custom.update_connected_cluster(
        env.cmd,
        env.client,
        "rg",
        "cluster",
        auto_upgrade="false",
        configuration_protected_settings={"proxy": {"no_proxy": "1.1.1.1"}},
    )
    payload = custom.utils.helm_update_agent.call_args.args[3]
    assert payload["global.noProxy"] == "1.1.1.1"
    assert consts.Proxy_Bypass_Arc_Helm_Value not in payload
    custom.get_all_helm_values.assert_not_called()


@pytest.mark.parametrize("command", ["connect", "update"])
@pytest.mark.parametrize("no_proxy", ["", "1.1.1.1"])
def test_proxy_commands_keep_other_protected_settings_with_arc(
    proxy_command_environment, command, no_proxy
):
    env = proxy_command_environment
    http_proxy = "http://proxy.example:8080"
    env.helm_dp["helmValuesContent"]["global.httpProxy"] = "redacted:proxy:http_proxy"
    handler = (
        custom.create_connectedk8s
        if command == "connect"
        else custom.update_connected_cluster
    )
    handler(
        env.cmd,
        env.client,
        "rg",
        "cluster",
        no_proxy=no_proxy,
        add_proxy_bypass="Arc",
        configuration_protected_settings={"proxy": {"http_proxy": http_proxy}},
    )
    payload = (
        custom.utils.helm_install_release.call_args.args[16]
        if command == "connect"
        else custom.utils.helm_update_agent.call_args.args[3]
    )
    expected = no_proxy + "," + ARC_SKIP_RANGE if no_proxy else ARC_SKIP_RANGE
    _assert_arc_helm_payload(payload, expected, no_proxy)
    assert payload["global.httpProxy"] == http_proxy
    configurations = env.dp_payload.arc_agentry_configurations
    assert len(configurations) == 1
    assert configurations[0].feature == "proxy"
    assert configurations[0].protected_settings == {
        "http_proxy": "redacted:proxy:http_proxy",
        "no_proxy": "redacted:proxy:no_proxy",
    }


@pytest.mark.parametrize("dp_returns_proxy", [False, True])
@pytest.mark.parametrize(
    "arguments,skip_range",
    [
        ({}, ""),
        ({"no_proxy": "10.0.0.0/8,1.1.1.1"}, "10.0.0.0/8,1.1.1.1"),
        (
            {
                "no_proxy": "1.1.1.1",
                "configuration_protected_settings": {"proxy": {"no_proxy": "2.2.2.2"}},
            },
            "1.1.1.1",
        ),
        ({"no_proxy": ARC_SKIP_RANGE}, ARC_SKIP_RANGE),
    ],
)
def test_connect_sends_arc_ownership_and_effective_range_to_helm(
    proxy_command_environment, arguments, skip_range, dp_returns_proxy
):
    env = proxy_command_environment
    if dp_returns_proxy:
        env.helm_dp["helmValuesContent"]["global.noProxy"] = "redacted:proxy:no_proxy"
    result = custom.create_connectedk8s(
        env.cmd,
        env.client,
        "rg",
        "cluster",
        add_proxy_bypass="Arc",
        **deepcopy(arguments),
    )
    assert result is env.cluster
    payload = custom.utils.helm_install_release.call_args.args[16]
    expected = (
        ARC_SKIP_RANGE
        if skip_range in ("", ARC_SKIP_RANGE)
        else skip_range + "," + ARC_SKIP_RANGE
    )
    _assert_arc_helm_payload(payload, expected, skip_range)
    _assert_proxy_configuration_has_no_ownership(env)
    custom.get_all_helm_values.assert_not_called()
    custom.utils.helm_update_agent.assert_not_called()


def test_connect_does_not_claim_arc_endpoints_supplied_only_in_the_range(
    proxy_command_environment,
):
    env = proxy_command_environment
    env.helm_dp["helmValuesContent"]["global.noProxy"] = "redacted:proxy:no_proxy"
    custom.create_connectedk8s(
        env.cmd, env.client, "rg", "cluster", no_proxy=ARC_SKIP_RANGE
    )
    payload = custom.utils.helm_install_release.call_args.args[16]
    assert payload["global.noProxy"] == ARC_SKIP_RANGE.replace(",", r"\,")
    assert consts.Proxy_Bypass_Arc_Helm_Value not in payload
    custom.get_all_helm_values.assert_not_called()


@pytest.mark.parametrize(
    "arguments,expected",
    [
        ({"no_proxy": "1.1.1.1"}, "1.1.1.1"),
        ({"no_proxy": "10.0.0.0/8"}, r"10.0.0.0\/8"),
    ],
)
def test_update_replaces_manual_arc_endpoints_normally(
    proxy_command_environment, arguments, expected
):
    env = proxy_command_environment
    custom.get_all_helm_values.return_value = {"global": {"noProxy": ARC_SKIP_RANGE}}
    env.helm_dp["helmValuesContent"]["global.noProxy"] = "redacted:proxy:no_proxy"
    custom.update_connected_cluster(
        env.cmd, env.client, "rg", "cluster", **deepcopy(arguments)
    )
    payload = custom.utils.helm_update_agent.call_args.args[3]
    assert payload["global.noProxy"] == expected
    assert consts.Proxy_Bypass_Arc_Helm_Value not in payload


@pytest.mark.parametrize("command", ["update", "gateway-reconnect"])
@pytest.mark.parametrize(
    "arguments,skip_range",
    [
        ({"no_proxy": "10.0.0.0/8,1.1.1.1"}, "10.0.0.0/8,1.1.1.1"),
        ({"no_proxy": "1.1.1.1", "add_proxy_bypass": "Arc"}, "1.1.1.1"),
        (
            {
                "no_proxy": "1.1.1.1",
                "configuration_protected_settings": {"proxy": {"no_proxy": "2.2.2.2"}},
            },
            "1.1.1.1",
        ),
        ({"add_proxy_bypass": "Arc"}, "192.168.0.0/16"),
    ],
)
def test_existing_cluster_preserves_arc_while_replacing_the_range(
    proxy_command_environment, command, arguments, skip_range
):
    env = proxy_command_environment
    custom.get_all_helm_values.return_value = _owned_arc_values("192.168.0.0/16")
    env.helm_dp["helmValuesContent"]["global.noProxy"] = "redacted:proxy:no_proxy"
    if command == "gateway-reconnect":
        custom.utils.get_release_namespace.return_value = "azure-arc"
        custom.connected_cluster_exists.return_value = True
        result = custom.create_connectedk8s(
            env.cmd,
            env.client,
            "rg",
            "cluster",
            gateway_resource_id=GATEWAY_RESOURCE_ID,
            **deepcopy(arguments),
        )
    else:
        result = custom.update_connected_cluster(
            env.cmd, env.client, "rg", "cluster", **deepcopy(arguments)
        )
    assert result is env.cluster
    expected = skip_range + "," + ARC_SKIP_RANGE if skip_range else ARC_SKIP_RANGE
    payload = custom.utils.helm_update_agent.call_args.args[3]
    _assert_arc_helm_payload(payload, expected, skip_range)
    _assert_proxy_configuration_has_no_ownership(env)
    custom.get_all_helm_values.assert_called_once_with(
        env.cmd, "azure-arc", None, None, "helm"
    )
    custom.utils.helm_install_release.assert_not_called()


@pytest.mark.parametrize(
    "saved_range,arguments,expected",
    [
        ("", {}, ""),
        ("1.1.1.1", {}, "1.1.1.1"),
        (".his.arc.azure.com", {}, ".his.arc.azure.com"),
        (ARC_SKIP_RANGE, {}, ARC_SKIP_RANGE),
        ("1.1.1.1", {"no_proxy": ARC_SKIP_RANGE}, ARC_SKIP_RANGE),
        ("1.1.1.1", {"no_proxy": ""}, "1.1.1.1"),
    ],
)
def test_update_clear_writes_the_remaining_range_and_null_ownership(
    proxy_command_environment, saved_range, arguments, expected
):
    env = proxy_command_environment
    custom.get_all_helm_values.return_value = _owned_arc_values(saved_range)
    custom.update_connected_cluster(
        env.cmd,
        env.client,
        "rg",
        "cluster",
        clear_proxy_bypass="Arc",
        **deepcopy(arguments),
    )
    payload = custom.utils.helm_update_agent.call_args.args[3]
    assert payload["global.noProxy"] == expected.replace(",", r"\,")
    assert payload[consts.Proxy_Bypass_Arc_Helm_Value] == "null"
    _assert_proxy_configuration_has_no_ownership(env)


@pytest.mark.parametrize("skip_range", [None, "1.1.1.1", ARC_SKIP_RANGE])
def test_clear_without_arc_ownership_does_not_cancel_other_updates(
    proxy_command_environment, skip_range
):
    env = proxy_command_environment
    custom.get_all_helm_values.return_value = {"global": {"noProxy": ARC_SKIP_RANGE}}
    if skip_range is not None:
        env.helm_dp["helmValuesContent"]["global.noProxy"] = "redacted:proxy:no_proxy"
    custom.update_connected_cluster(
        env.cmd,
        env.client,
        "rg",
        "cluster",
        clear_proxy_bypass="Arc",
        add_proxy_bypass="Microsoft.AzureMonitor.Containers",
        tags={"purpose": "test"},
        no_proxy=skip_range or "",
    )
    custom.update_connected_cluster_internal.assert_called_once()
    custom.utils.helm_update_agent.assert_called_once()
    custom.containerinsightsutils.sync_container_insights_proxy_bypass_configmap.assert_called_once_with(
        custom.kube_client.CoreV1Api.return_value, True, cmd=env.cmd
    )
    payload = custom.utils.helm_update_agent.call_args.args[3]
    assert consts.Proxy_Bypass_Arc_Helm_Value not in payload
    if skip_range is None:
        assert "global.noProxy" not in payload
    else:
        assert payload["global.noProxy"] == skip_range.replace(",", r"\,")


@pytest.mark.parametrize(
    "arguments",
    [
        {"http_proxy": "http://proxy.example:8080"},
        {"disable_proxy": True},
        {"auto_upgrade": "false"},
        {"clear_proxy_bypass": "Microsoft.AzureMonitor.Containers"},
    ],
)
def test_unrelated_update_does_not_read_or_rewrite_arc_ownership(
    proxy_command_environment, arguments
):
    env = proxy_command_environment
    custom.get_all_helm_values.return_value = _owned_arc_values("1.1.1.1")
    custom.update_connected_cluster(env.cmd, env.client, "rg", "cluster", **arguments)
    custom.get_all_helm_values.assert_not_called()
    payload = custom.utils.helm_update_agent.call_args.args[3]
    assert "global.noProxy" not in payload
    assert consts.Proxy_Bypass_Arc_Helm_Value not in payload
    if arguments.get("disable_proxy"):
        assert payload["global.isProxyEnabled"] == "False"


@pytest.mark.parametrize("command", ["update", "gateway-reconnect"])
@pytest.mark.parametrize("failure", ["malformed", "mismatch", "read"])
def test_arc_ownership_failure_stops_before_helm_changes(
    proxy_command_environment, command, failure
):
    env = proxy_command_environment
    values = _owned_arc_values("1.1.1.1")
    if failure == "malformed":
        values["connectedk8sCli"]["arcProxyBypass"] = "invalid"
    elif failure == "mismatch":
        values["global"]["noProxy"] = "2.2.2.2," + ARC_SKIP_RANGE
    else:
        custom.get_all_helm_values.side_effect = custom.CLIInternalError(
            "[AZK8S0509] HelmValuesGetFailed"
        )
    custom.get_all_helm_values.return_value = values
    with pytest.raises(AzCLIError, match=r"\[AZK8S0(107|509)\]"):
        if command == "gateway-reconnect":
            custom.utils.get_release_namespace.return_value = "azure-arc"
            custom.connected_cluster_exists.return_value = True
            custom.create_connectedk8s(
                env.cmd,
                env.client,
                "rg",
                "cluster",
                no_proxy="1.1.1.1",
                gateway_resource_id=GATEWAY_RESOURCE_ID,
                tags={"purpose": "test"},
            )
        else:
            custom.update_connected_cluster(
                env.cmd,
                env.client,
                "rg",
                "cluster",
                no_proxy="1.1.1.1",
                tags={"purpose": "test"},
            )
    if command == "update":
        custom.update_connected_cluster_internal.assert_called_once_with(
            env.cmd, env.client, "rg", "cluster", {"purpose": "test"}, None, None, None
        )
    else:
        custom.update_connected_cluster_internal.assert_not_called()
    custom.put_cc_resource.assert_not_called()
    custom.utils.update_gateway_cluster_link.assert_not_called()
    custom.utils.helm_update_agent.assert_not_called()
    custom.utils.helm_install_release.assert_not_called()


@pytest.mark.parametrize(
    "arguments",
    [
        {"tags": {"purpose": "test"}},
        {"azure_hybrid_benefit": "False", "no_proxy": "1.1.1.1"},
    ],
)
def test_arm_update_keeps_original_order_when_kubernetes_is_unreachable(
    proxy_command_environment, arguments
):
    env = proxy_command_environment
    expected = ValidationError("[AZK8S0202] KubernetesConnectivityFailed")
    custom.check_kube_connection.side_effect = expected
    with pytest.raises(ValidationError) as raised:
        custom.update_connected_cluster(
            env.cmd, env.client, "rg", "cluster", **arguments
        )
    assert raised.value is expected
    custom.update_connected_cluster_internal.assert_called_once_with(
        env.cmd,
        env.client,
        "rg",
        "cluster",
        arguments.get("tags"),
        None,
        None,
        arguments.get("azure_hybrid_benefit"),
    )
    custom.get_all_helm_values.assert_not_called()
    custom.put_cc_resource.assert_not_called()
    custom.utils.helm_update_agent.assert_not_called()


def test_non_gateway_reconnect_still_rejects_adding_arc(proxy_command_environment):
    env = proxy_command_environment
    custom.utils.get_release_namespace.return_value = "azure-arc"
    custom.connected_cluster_exists.return_value = True
    with pytest.raises(ArgumentUsageError, match="reconnect"):
        custom.create_connectedk8s(
            env.cmd, env.client, "rg", "cluster", add_proxy_bypass="Arc"
        )
    custom.put_cc_resource.assert_not_called()
    custom.utils.helm_update_agent.assert_not_called()


def test_arm_only_hybrid_benefit_update_does_not_need_proxy_or_helm(
    proxy_command_environment,
):
    env = proxy_command_environment
    result = custom.update_connected_cluster(
        env.cmd, env.client, "rg", "cluster", azure_hybrid_benefit="False"
    )
    assert result is env.cluster
    custom.update_connected_cluster_internal.assert_called_once()
    custom.load_kube_config.assert_not_called()
    custom.get_all_helm_values.assert_not_called()
    custom.utils.helm_update_agent.assert_not_called()


@pytest.mark.parametrize("skip_range", ["", "10.0.0.0/8,.HIS.ARC.AZURE.COM"])
def test_manual_upgrade_carries_arc_ownership_and_other_helm_values(
    proxy_command_environment, monkeypatch, skip_range
):
    env = proxy_command_environment
    values = _owned_arc_values(skip_range)
    values["unrelated"] = {"setting": "preserved"}
    custom.utils.get_release_namespace.return_value = "azure-arc"
    custom.connected_cluster_exists.return_value = True
    get_values = MagicMock(returncode=0)
    get_values.communicate.return_value = (json.dumps(values).encode("ascii"), b"")
    upgrade = MagicMock(returncode=0)
    upgrade.communicate.return_value = (b"{}", b"")
    popen = MagicMock(side_effect=[get_values, upgrade])
    monkeypatch.setattr(custom, "Popen", popen)

    custom.upgrade_agents(env.cmd, env.client, "rg", "cluster")

    command = popen.call_args_list[1].args[0]
    assert "--atomic" in command
    assert "unrelated.setting=preserved" in command
    encoded = values["connectedk8sCli"]["arcProxyBypass"]
    assert f"{consts.Proxy_Bypass_Arc_Helm_Value}={encoded}" in command
    no_proxy = values["global"]["noProxy"].replace(",", r"\,").replace("/", r"\/")
    assert f"global.noProxy={no_proxy}" in command
    custom.get_all_helm_values.assert_not_called()
