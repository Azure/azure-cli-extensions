# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import sys
from unittest.mock import MagicMock

import pytest
from azure.cli.core.azclierror import (
    ClientRequestError,
    CLIInternalError,
    ManualInterrupt,
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
import azext_connectedk8s._constants as consts
import azext_connectedk8s._errors as errors
import azext_connectedk8s.clientproxyhelper._binaryutils as proxybinaryutils
from azext_connectedk8s import custom
from azext_connectedk8s.clientproxyhelper._enums import ProxyStatus


class ClassifiedError(Exception):
    pass


def _reporter(monkeypatch, module):
    report = MagicMock(return_value=ClassifiedError("classified"))
    monkeypatch.setattr(module.utils, "report_connectedk8s_error", report)
    return report


def _cmd():
    cmd = MagicMock()
    cmd.cli_ctx.data = {"safe_params": []}
    return cmd


def test_client_proxy_legacy_fault_types_resolve_to_08xx_errors():
    assert (
        errors.get_error_by_fault_type(consts.Create_CSPExe_Fault_Type)
        is errors.CLIENT_PROXY_DOWNLOAD_FAILED
    )
    assert (
        errors.get_error_by_fault_type(consts.Remove_Config_Fault_Type)
        is errors.CLIENT_PROXY_CONFIG_CREATE_FAILED
    )


def test_proxy_download_failure_uses_azk8s0800(monkeypatch):
    cmd = _cmd()
    cmd.cli_ctx.cloud.endpoints.active_directory = "https://login.example"
    report = _reporter(monkeypatch, proxybinaryutils)
    monkeypatch.setattr(
        proxybinaryutils, "_get_client_operating_system", lambda: "linux"
    )
    monkeypatch.setattr(proxybinaryutils, "_get_client_architeture", lambda: "amd64")
    monkeypatch.setattr(
        proxybinaryutils, "_get_proxy_install_dir", lambda _: "/tmp/clientproxy"
    )
    monkeypatch.setattr(proxybinaryutils, "_get_proxy_filename", lambda *_: "arc-proxy")
    monkeypatch.setattr(
        proxybinaryutils.os.path, "isfile", MagicMock(return_value=False)
    )
    monkeypatch.setattr(proxybinaryutils.os.path, "isdir", MagicMock(return_value=True))
    monkeypatch.setattr(proxybinaryutils, "glob", MagicMock(return_value=[]))
    monkeypatch.setattr(proxybinaryutils.utils, "get_mcr_path", lambda _: "mcr.test")
    oras_client = MagicMock()
    oras_client.pull.side_effect = RuntimeError("download failed")
    monkeypatch.setattr(
        proxybinaryutils.oras.client, "OrasClient", MagicMock(return_value=oras_client)
    )

    with pytest.raises(ClassifiedError):
        proxybinaryutils.install_client_side_proxy(cmd, None)

    assert report.call_args.args[:2] == (cmd, errors.CLIENT_PROXY_DOWNLOAD_FAILED)


def test_proxy_install_validation_failure_uses_azk8s0800(monkeypatch):
    cmd = _cmd()
    report = _reporter(monkeypatch, proxybinaryutils)
    monkeypatch.setattr(
        proxybinaryutils, "_get_client_operating_system", lambda: "linux"
    )
    monkeypatch.setattr(proxybinaryutils, "_get_client_architeture", lambda: "amd64")
    monkeypatch.setattr(
        proxybinaryutils, "_get_proxy_install_dir", lambda _: "/tmp/clientproxy"
    )
    monkeypatch.setattr(proxybinaryutils, "_get_proxy_filename", lambda *_: "arc-proxy")
    monkeypatch.setattr(
        proxybinaryutils.os.path, "isfile", MagicMock(return_value=False)
    )
    monkeypatch.setattr(proxybinaryutils.os.path, "isdir", MagicMock(return_value=True))
    monkeypatch.setattr(proxybinaryutils, "glob", MagicMock(return_value=[]))
    monkeypatch.setattr(
        proxybinaryutils, "_download_proxy_from_MCR", MagicMock(return_value=None)
    )
    monkeypatch.setattr(
        proxybinaryutils,
        "_check_proxy_installation",
        MagicMock(side_effect=CLIInternalError("missing executable")),
    )

    with pytest.raises(ClassifiedError):
        proxybinaryutils.install_client_side_proxy(cmd, None)

    assert report.call_args.args[:2] == (cmd, errors.CLIENT_PROXY_DOWNLOAD_FAILED)
    assert report.call_args.kwargs["fault_type"] == consts.Create_CSPExe_Fault_Type


def test_proxy_port_failure_uses_azk8s0801(monkeypatch):
    cmd = _cmd()
    add_event = MagicMock()
    set_user_fault = MagicMock()
    monkeypatch.setattr(custom.utils, "add_connectedk8s_telemetry_event", add_event)
    monkeypatch.setattr(custom.telemetry, "set_user_fault", set_user_fault)
    monkeypatch.setattr(custom.telemetry, "set_exception", MagicMock())
    monkeypatch.setattr(
        custom.utils, "set_connected_cluster_arm_id_telemetry_context", MagicMock()
    )
    monkeypatch.setattr(
        custom, "send_cloud_telemetry", MagicMock(return_value="AzureCloud")
    )
    monkeypatch.setattr(
        custom,
        "Profile",
        MagicMock(
            return_value=MagicMock(
                get_subscription=MagicMock(return_value={"tenantId": "tenant"})
            )
        ),
    )
    monkeypatch.setattr(custom.utils, "ensure_correlation_id", MagicMock())
    monkeypatch.setattr(
        custom.clientproxyutils,
        "check_if_port_is_open",
        MagicMock(side_effect=[False, False, True]),
    )

    with pytest.raises(ClientRequestError) as ex:
        custom.client_side_proxy_wrapper(cmd, MagicMock(), "resource-group", "cluster")

    assert "[AZK8S0801] ClientProxyPortInUse" in str(ex.value)
    assert ex.value.recommendations
    set_user_fault.assert_called_once_with()
    assert add_event.call_args.args[1][consts.Telemetry_Error_Code_Key] == "AZK8S0801"


def test_proxy_config_failure_uses_azk8s0803(monkeypatch):
    cmd = _cmd()
    report = _reporter(monkeypatch, custom)
    monkeypatch.setattr(
        custom.utils, "set_connected_cluster_arm_id_telemetry_context", MagicMock()
    )
    monkeypatch.setattr(
        custom, "send_cloud_telemetry", MagicMock(return_value="AzureCloud")
    )
    monkeypatch.setattr(
        custom,
        "Profile",
        MagicMock(
            return_value=MagicMock(
                get_subscription=MagicMock(return_value={"tenantId": "tenant"})
            )
        ),
    )
    monkeypatch.setattr(custom.utils, "ensure_correlation_id", MagicMock())
    monkeypatch.setattr(
        custom.clientproxyutils, "check_if_port_is_open", MagicMock(return_value=False)
    )
    monkeypatch.setattr(
        custom.clientproxyutils, "check_process", MagicMock(return_value=False)
    )
    monkeypatch.setattr(
        custom.proxybinaryutils,
        "install_client_side_proxy",
        MagicMock(return_value="/tmp/clientproxy/arc-proxy"),
    )
    monkeypatch.setattr(custom.utils, "get_metadata", MagicMock(return_value={}))
    monkeypatch.setattr("builtins.open", MagicMock(side_effect=OSError("write failed")))

    with pytest.raises(ClassifiedError):
        custom.client_side_proxy_wrapper(
            cmd, MagicMock(), "resource-group", "cluster", token="token"
        )

    assert report.call_args.args[:2] == (
        cmd,
        errors.CLIENT_PROXY_CONFIG_CREATE_FAILED,
    )


def test_proxy_start_failure_uses_azk8s0802(monkeypatch):
    cmd = _cmd()
    report = _reporter(monkeypatch, custom)
    monkeypatch.setattr(custom, "get_subscription_id", MagicMock(return_value="sub"))
    monkeypatch.setattr(custom, "Popen", MagicMock(side_effect=OSError("start failed")))

    with pytest.raises(ClassifiedError):
        custom.client_side_proxy(
            cmd,
            "tenant",
            MagicMock(),
            "resource-group",
            "cluster",
            ProxyStatus.FirstRun,
            ["arc-proxy"],
            consts.CLIENT_PROXY_PORT,
            consts.API_SERVER_PORT,
            False,
            token="token",
        )

    assert report.call_args.args[:2] == (cmd, errors.CLIENT_PROXY_START_FAILED)


def test_cluster_credentials_failure_preserves_arm_error_handling(monkeypatch):
    cmd = _cmd()
    monkeypatch.setattr(custom, "get_subscription_id", MagicMock(return_value="sub"))
    client = MagicMock()
    client.list_cluster_user_credential.side_effect = RuntimeError("ARM failed")
    process = MagicMock()
    handled_error = ClassifiedError("ARM error")
    arm_exception_handler = MagicMock(side_effect=handled_error)
    monkeypatch.setattr(custom.utils, "arm_exception_handler", arm_exception_handler)

    with pytest.raises(ClassifiedError):
        custom.client_side_proxy(
            cmd,
            "tenant",
            client,
            "resource-group",
            "cluster",
            ProxyStatus.HCTokenRefresh,
            ["arc-proxy"],
            consts.CLIENT_PROXY_PORT,
            consts.API_SERVER_PORT,
            False,
            token="token",
            clientproxy_process=process,
        )

    process.terminate.assert_called_once_with()
    handler_args = arm_exception_handler.call_args.args
    assert isinstance(handler_args[0], RuntimeError)
    assert handler_args[1:] == (
        consts.Get_Credentials_Failed_Fault_Type,
        "Unable to list cluster user credentials",
    )


def test_externally_closed_proxy_uses_azk8s0804(monkeypatch):
    cmd = _cmd()
    add_event = MagicMock()
    monkeypatch.setattr(custom.utils, "add_connectedk8s_telemetry_event", add_event)
    monkeypatch.setattr(custom.telemetry, "set_exception", MagicMock())
    process = MagicMock()
    monkeypatch.setattr(
        custom,
        "client_side_proxy",
        MagicMock(return_value=(100, 100, process)),
    )
    monkeypatch.setattr(custom.time, "sleep", MagicMock())
    monkeypatch.setattr(
        custom.clientproxyutils,
        "check_if_csp_is_running",
        MagicMock(return_value=False),
    )

    with pytest.raises(ManualInterrupt) as ex:
        custom.client_side_proxy_main(
            cmd,
            "tenant",
            MagicMock(),
            "resource-group",
            "cluster",
            ["arc-proxy"],
            consts.CLIENT_PROXY_PORT,
            consts.API_SERVER_PORT,
            False,
        )

    assert "[AZK8S0804] ClientProxyClosed" in str(ex.value)
    assert add_event.call_args.args[1][consts.Telemetry_Error_Code_Key] == "AZK8S0804"
