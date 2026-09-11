# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Unit tests for prediagnostic telemetry functions in _precheckutils.py."""

from __future__ import annotations

import json
import os
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import azext_connectedk8s._constants as consts
import azext_connectedk8s._precheckutils as precheckutils

_REAL_ADD_CONNECTEDK8S_TELEMETRY_EVENT = (
    precheckutils.azext_utils.add_connectedk8s_telemetry_event
)


@pytest.fixture(autouse=True)
def _route_wrapped_events_to_test_telemetry(monkeypatch):
    monkeypatch.setattr(
        precheckutils.azext_utils,
        "add_connectedk8s_telemetry_event",
        lambda _cmd, properties: precheckutils.telemetry.add_extension_event(
            "connectedk8s", properties
        ),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _reset_globals():
    """Reset module-level globals to a clean state before each test."""
    precheckutils.diagnoser_output = []
    precheckutils.prediagnostic_job_execution_status = consts.Job_Status_Not_Started
    precheckutils.prediagnostic_entra_check = consts.Diagnostic_Check_Starting
    precheckutils.prediagnostic_crd_check = consts.Diagnostic_Check_Starting


def test_precheck_telemetry_helpers_forward_command_context(monkeypatch):
    cmd = MagicMock()
    add_event = MagicMock()
    monkeypatch.setattr(
        precheckutils.azext_utils,
        "add_connectedk8s_telemetry_event",
        add_event,
    )

    precheckutils.send_prediagnostic_job_execution_error_telemetry(cmd=cmd)
    precheckutils.send_prediagnostic_check_failure_telemetry(
        consts.Diagnostic_Check_Failed,
        consts.Diagnostic_Check_Passed,
        cmd=cmd,
    )
    precheckutils.send_post_diagnostic_precheck_failure_telemetry(
        "LinuxNodeExists", "No Linux nodes found", cmd=cmd
    )

    assert add_event.call_count == 3
    assert all(call.args[0] is cmd for call in add_event.call_args_list)


def test_fetch_diagnostic_checks_results_preserves_standardized_cli_error(monkeypatch):
    expected = precheckutils.AzCLIError("[AZK8S0502] HelmChartPullFailed")
    monkeypatch.setattr(
        precheckutils,
        "executing_cluster_diagnostic_checks_job",
        MagicMock(side_effect=expected),
    )

    with pytest.raises(precheckutils.AzCLIError) as raised:
        precheckutils.fetch_diagnostic_checks_results(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            "/usr/bin/helm",
            "/usr/bin/kubectl",
            None,
            None,
            "eastus",
            "",
            "",
            "",
            "",
            "AzureCloud",
            "/tmp/prechecks",
            True,
        )

    assert raised.value is expected


def test_executing_cluster_diagnostic_checks_job_preserves_chart_pull_error(
    monkeypatch,
):
    expected = precheckutils.AzCLIError("[AZK8S0502] HelmChartPullFailed")
    monkeypatch.setattr(
        precheckutils.azext_utils, "get_release_namespace", MagicMock(return_value=None)
    )
    monkeypatch.setattr(
        precheckutils.azext_utils,
        "get_mcr_path",
        MagicMock(return_value="mcr.microsoft.com"),
    )
    monkeypatch.setattr(
        precheckutils.azext_utils,
        "get_chart_path",
        MagicMock(side_effect=expected),
    )
    monkeypatch.setattr(precheckutils.config, "load_kube_config", MagicMock())
    cleanup_process = MagicMock()
    monkeypatch.setattr(precheckutils, "Popen", cleanup_process)

    with pytest.raises(precheckutils.AzCLIError) as raised:
        precheckutils.executing_cluster_diagnostic_checks_job(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            "/usr/bin/helm",
            "/usr/bin/kubectl",
            None,
            None,
            "eastus",
            "",
            "",
            "",
            "",
            "AzureCloud",
            "/tmp/prechecks",
            True,
        )

    assert raised.value is expected
    cleanup_process.assert_called_once()


def test_prediagnostics_helm_install_uses_standardized_error(monkeypatch):
    process = MagicMock(returncode=1)
    process.communicate.return_value = (
        b"",
        b"Error: injected Helm install failure",
    )
    monkeypatch.setattr(precheckutils, "Popen", MagicMock(return_value=process))
    arm_id = (
        "/subscriptions/sub/resourceGroups/rg/providers/"
        "Microsoft.Kubernetes/connectedClusters/cluster"
    )
    cmd = SimpleNamespace(cli_ctx=SimpleNamespace(data={"connectedk8s_arm_id": arm_id}))
    mock_telemetry = MagicMock()
    monkeypatch.setattr(precheckutils.azext_utils, "telemetry", mock_telemetry)
    monkeypatch.setattr(precheckutils, "telemetry", mock_telemetry)
    monkeypatch.setattr(
        precheckutils.azext_utils,
        "add_connectedk8s_telemetry_event",
        _REAL_ADD_CONNECTEDK8S_TELEMETRY_EVENT,
    )

    with pytest.raises(precheckutils.AzCLIError) as raised:
        precheckutils.helm_install_release_cluster_diagnostic_checks(
            cmd,
            "/tmp/chart",
            "eastus",
            "",
            "",
            "",
            "",
            "AzureCloud",
            None,
            None,
            "/usr/bin/helm",
            "mcr.microsoft.com",
        )

    assert str(raised.value).startswith("[AZK8S0607] PrediagnosticsHelmInstallFailed:")
    _, properties = mock_telemetry.add_extension_event.call_args.args
    assert properties["Context.Default.AzureCLI.errorCode"] == "AZK8S0607"
    assert properties["Context.Default.AzureCLI.resourceid"] == arm_id
    assert properties["Context.Default.AzureCLI.errorMessage"] == str(raised.value)
    assert mock_telemetry.set_exception.call_args.kwargs["summary"] == str(raised.value)
    mock_telemetry.set_user_fault.assert_not_called()


def test_prediagnostics_helm_install_sets_user_fault_once(monkeypatch):
    process = MagicMock(returncode=1)
    process.communicate.return_value = (b"", b"Error: forbidden")
    monkeypatch.setattr(precheckutils, "Popen", MagicMock(return_value=process))
    mock_telemetry = MagicMock()
    monkeypatch.setattr(precheckutils.azext_utils, "telemetry", mock_telemetry)
    monkeypatch.setattr(precheckutils, "telemetry", mock_telemetry)

    with pytest.raises(precheckutils.AzCLIError):
        precheckutils.helm_install_release_cluster_diagnostic_checks(
            MagicMock(),
            "/tmp/chart",
            "eastus",
            "",
            "",
            "",
            "",
            "AzureCloud",
            None,
            None,
            "/usr/bin/helm",
            "mcr.microsoft.com",
        )

    mock_telemetry.set_user_fault.assert_called_once_with()
    mock_telemetry.set_exception.assert_called_once()


def test_log_save_failure_reports_azk8s0606_with_command_context(monkeypatch):
    cmd = MagicMock()
    exception = OSError("write failed")
    add_event = MagicMock()
    set_exception = MagicMock()
    monkeypatch.setattr(
        precheckutils.azext_utils, "add_connectedk8s_telemetry_event", add_event
    )
    monkeypatch.setattr(precheckutils.telemetry, "set_exception", set_exception)

    precheckutils._report_prediagnostic_log_save_failure(cmd, exception)

    add_event.assert_called_once()
    event_cmd, properties = add_event.call_args.args
    assert event_cmd is cmd
    assert properties[consts.Telemetry_Error_Code_Key] == "AZK8S0606"
    assert "write failed" in properties[consts.Telemetry_Error_Message_Key]
    set_exception.assert_called_once_with(
        exception=exception,
        fault_type=consts.Cluster_Diagnostic_Checks_Job_Log_Save_Failed,
        summary=properties[consts.Telemetry_Error_Message_Key],
    )


def test_fetch_results_propagates_classified_azure_cli_error(monkeypatch):
    class ClassifiedError(Exception):
        pass

    monkeypatch.setattr(precheckutils, "AzCLIError", ClassifiedError)
    classified_error = ClassifiedError("[AZK8S0607] forbidden")

    def raise_classified_error(*_args, **_kwargs):
        raise classified_error

    monkeypatch.setattr(
        precheckutils,
        "executing_cluster_diagnostic_checks_job",
        raise_classified_error,
    )

    with pytest.raises(ClassifiedError) as exc_info:
        precheckutils.fetch_diagnostic_checks_results(
            cmd=MagicMock(),
            corev1_api_instance=MagicMock(),
            batchv1_api_instance=MagicMock(),
            helm_client_location="helm",
            kubectl_client_location="kubectl",
            kube_config=None,
            kube_context=None,
            location="eastus",
            http_proxy="",
            https_proxy="",
            no_proxy="",
            proxy_cert="",
            azure_cloud="AZUREPUBLICCLOUD",
            filepath_with_timestamp="/tmp/prediagnostics",
            storage_space_available=True,
        )

    assert exc_info.value is classified_error


def test_job_execution_propagates_helm_install_error_unchanged(monkeypatch):
    class ClassifiedError(Exception):
        pass

    monkeypatch.setattr(precheckutils, "AzCLIError", ClassifiedError)
    classified_error = ClassifiedError("[AZK8S0607] forbidden")
    monkeypatch.setattr(precheckutils.config, "load_kube_config", MagicMock())
    monkeypatch.setattr(
        precheckutils.azext_utils,
        "get_release_namespace",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(precheckutils.azext_utils, "get_mcr_path", lambda *_args: "mcr")
    monkeypatch.setattr(
        precheckutils.azext_utils, "get_chart_path", lambda *_args: "chart"
    )
    monkeypatch.setattr(precheckutils, "Popen", MagicMock())

    def raise_classified_error(*_args, **_kwargs):
        raise classified_error

    monkeypatch.setattr(
        precheckutils,
        "helm_install_release_cluster_diagnostic_checks",
        raise_classified_error,
    )

    with pytest.raises(ClassifiedError) as exc_info:
        precheckutils.executing_cluster_diagnostic_checks_job(
            cmd=MagicMock(),
            corev1_api_instance=MagicMock(),
            batchv1_api_instance=MagicMock(),
            helm_client_location="helm",
            kubectl_client_location="kubectl",
            kube_config=None,
            kube_context=None,
            location="eastus",
            http_proxy="",
            https_proxy="",
            no_proxy="",
            proxy_cert="",
            azure_cloud="AZUREPUBLICCLOUD",
            filepath_with_timestamp="/tmp/prediagnostics",
            storage_space_available=True,
        )

    assert exc_info.value is classified_error


# ---------------------------------------------------------------------------
# send_prediagnostic_job_execution_error_telemetry
# ---------------------------------------------------------------------------


class TestSendJobExecutionErrorTelemetry:
    def setup_method(self):
        _reset_globals()

    @patch("azext_connectedk8s._precheckutils.telemetry")
    def test_sends_event_with_correct_error_type(self, mock_telemetry):
        precheckutils.prediagnostic_job_execution_status = (
            consts.Job_Status_Execution_Failed
        )
        precheckutils.send_prediagnostic_job_execution_error_telemetry()

        mock_telemetry.add_extension_event.assert_called_once()
        args = mock_telemetry.add_extension_event.call_args
        assert args[0][0] == "connectedk8s"
        props = args[0][1]
        assert (
            props[consts.Telemetry_Onboarding_Error_Type_Key]
            == consts.Install_Prediagnostics_Job_Execution_Error_Fault_Type
        )

    @patch("azext_connectedk8s._precheckutils.telemetry")
    def test_message_includes_job_execution_status(self, mock_telemetry):
        precheckutils.prediagnostic_job_execution_status = (
            consts.Job_Status_Execution_Failed
        )
        precheckutils.send_prediagnostic_job_execution_error_telemetry()

        props = mock_telemetry.add_extension_event.call_args[0][1]
        msg = json.loads(props[consts.Telemetry_Onboarding_Error_Message_Key])
        assert msg["jobExecutionStatus"] == consts.Job_Status_Execution_Failed

    @patch("azext_connectedk8s._precheckutils.telemetry")
    def test_message_includes_reason_when_provided(self, mock_telemetry):
        precheckutils.prediagnostic_job_execution_status = (
            consts.Job_Status_Not_Completed
        )
        precheckutils.send_prediagnostic_job_execution_error_telemetry(
            reason="ImagePullBackOff"
        )

        props = mock_telemetry.add_extension_event.call_args[0][1]
        msg = json.loads(props[consts.Telemetry_Onboarding_Error_Message_Key])
        assert msg["reason"] == "ImagePullBackOff"

    @patch("azext_connectedk8s._precheckutils.telemetry")
    def test_message_omits_reason_when_empty(self, mock_telemetry):
        precheckutils.send_prediagnostic_job_execution_error_telemetry()

        props = mock_telemetry.add_extension_event.call_args[0][1]
        msg = json.loads(props[consts.Telemetry_Onboarding_Error_Message_Key])
        assert "reason" not in msg

    @patch("azext_connectedk8s._precheckutils.telemetry")
    def test_message_is_valid_json(self, mock_telemetry):
        precheckutils.send_prediagnostic_job_execution_error_telemetry(
            reason="ContainerCreating"
        )

        props = mock_telemetry.add_extension_event.call_args[0][1]
        msg = json.loads(props[consts.Telemetry_Onboarding_Error_Message_Key])
        assert isinstance(msg, dict)


# ---------------------------------------------------------------------------
# send_prediagnostic_check_failure_telemetry
# ---------------------------------------------------------------------------


class TestSendCheckFailureTelemetry:
    def setup_method(self):
        _reset_globals()

    @patch("azext_connectedk8s._precheckutils.telemetry")
    def test_sends_event_with_correct_error_type(self, mock_telemetry):
        precheckutils.send_prediagnostic_check_failure_telemetry(
            consts.Diagnostic_Check_Passed, consts.Diagnostic_Check_Passed
        )

        mock_telemetry.add_extension_event.assert_called_once()
        props = mock_telemetry.add_extension_event.call_args[0][1]
        assert (
            props[consts.Telemetry_Onboarding_Error_Type_Key]
            == consts.Install_Prediagnostics_Fault_Type
        )

    @patch("azext_connectedk8s._precheckutils.telemetry")
    def test_check_results_in_message(self, mock_telemetry):
        precheckutils.prediagnostic_entra_check = consts.Diagnostic_Check_Failed
        precheckutils.prediagnostic_crd_check = consts.Diagnostic_Check_Passed
        precheckutils.send_prediagnostic_check_failure_telemetry(
            consts.Diagnostic_Check_Passed, consts.Diagnostic_Check_Failed
        )

        props = mock_telemetry.add_extension_event.call_args[0][1]
        msg = json.loads(props[consts.Telemetry_Onboarding_Error_Message_Key])
        # msg is a list of component entries
        components = {entry["componentName"]: entry for entry in msg}
        assert components["dns"]["checkResult"] == consts.Diagnostic_Check_Passed
        assert (
            components["outboundConnectivity"]["checkResult"]
            == consts.Diagnostic_Check_Failed
        )
        assert components["entra"]["checkResult"] == consts.Diagnostic_Check_Failed
        assert components["crd"]["checkResult"] == consts.Diagnostic_Check_Passed

    @patch("azext_connectedk8s._precheckutils.telemetry")
    def test_entra_error_extracted_from_diagnoser_output(self, mock_telemetry):
        precheckutils.prediagnostic_entra_check = consts.Diagnostic_Check_Failed
        precheckutils.diagnoser_output = [
            "Some log line",
            "Error: Entra endpoint not reachable. Response code: 000",
        ]
        precheckutils.send_prediagnostic_check_failure_telemetry(
            consts.Diagnostic_Check_Passed, consts.Diagnostic_Check_Passed
        )

        props = mock_telemetry.add_extension_event.call_args[0][1]
        msg = json.loads(props[consts.Telemetry_Onboarding_Error_Message_Key])
        components = {entry["componentName"]: entry for entry in msg}
        assert "error" in components["entra"]
        assert "000" in components["entra"]["error"]

    @patch("azext_connectedk8s._precheckutils.telemetry")
    def test_dns_error_extracted_from_diagnoser_output(self, mock_telemetry):
        precheckutils.diagnoser_output = [
            "DNS error: resolution failed for test.example.com",
        ]
        precheckutils.send_prediagnostic_check_failure_telemetry(
            consts.Diagnostic_Check_Failed, consts.Diagnostic_Check_Passed
        )

        props = mock_telemetry.add_extension_event.call_args[0][1]
        msg = json.loads(props[consts.Telemetry_Onboarding_Error_Message_Key])
        components = {entry["componentName"]: entry for entry in msg}
        assert "error" in components["dns"]

    @patch("azext_connectedk8s._precheckutils.telemetry")
    def test_outbound_error_extracted_from_diagnoser_output(self, mock_telemetry):
        precheckutils.diagnoser_output = [
            "Outbound connectivity error: MCR not reachable",
        ]
        precheckutils.send_prediagnostic_check_failure_telemetry(
            consts.Diagnostic_Check_Passed, consts.Diagnostic_Check_Failed
        )

        props = mock_telemetry.add_extension_event.call_args[0][1]
        msg = json.loads(props[consts.Telemetry_Onboarding_Error_Message_Key])
        components = {entry["componentName"]: entry for entry in msg}
        assert "error" in components["outboundConnectivity"]

    @patch("azext_connectedk8s._precheckutils.telemetry")
    def test_multiline_error_trimmed_to_first_line(self, mock_telemetry):
        precheckutils.prediagnostic_entra_check = consts.Diagnostic_Check_Failed
        precheckutils.diagnoser_output = [
            "Error: Entra endpoint error line1\nline2\nline3",
        ]
        precheckutils.send_prediagnostic_check_failure_telemetry(
            consts.Diagnostic_Check_Passed, consts.Diagnostic_Check_Passed
        )

        props = mock_telemetry.add_extension_event.call_args[0][1]
        msg = json.loads(props[consts.Telemetry_Onboarding_Error_Message_Key])
        components = {entry["componentName"]: entry for entry in msg}
        assert "\n" not in components["entra"].get("error", "")
        assert "line1" in components["entra"].get("error", "")

    @patch("azext_connectedk8s._precheckutils.telemetry")
    def test_no_error_detail_when_checks_pass(self, mock_telemetry):
        precheckutils.prediagnostic_entra_check = consts.Diagnostic_Check_Passed
        precheckutils.prediagnostic_crd_check = consts.Diagnostic_Check_Passed
        precheckutils.send_prediagnostic_check_failure_telemetry(
            consts.Diagnostic_Check_Passed, consts.Diagnostic_Check_Passed
        )

        props = mock_telemetry.add_extension_event.call_args[0][1]
        msg = json.loads(props[consts.Telemetry_Onboarding_Error_Message_Key])
        components = {entry["componentName"]: entry for entry in msg}
        for entry in components.values():
            assert "error" not in entry

    @patch("azext_connectedk8s._precheckutils.telemetry")
    def test_non_error_lines_captured_as_fallback(self, mock_telemetry):
        """Lines mentioning entra without 'error'/'failed' are captured as fallback context."""
        precheckutils.prediagnostic_entra_check = consts.Diagnostic_Check_Failed
        precheckutils.diagnoser_output = [
            "Entra check: starting",
            "Entra Authentication Endpoint Connectivity Check Result : https://login.microsoftonline.com : 000",
        ]
        precheckutils.send_prediagnostic_check_failure_telemetry(
            consts.Diagnostic_Check_Passed, consts.Diagnostic_Check_Passed
        )

        props = mock_telemetry.add_extension_event.call_args[0][1]
        msg = json.loads(props[consts.Telemetry_Onboarding_Error_Message_Key])
        components = {entry["componentName"]: entry for entry in msg}
        # Fallback captures any matching line when no 'error'/'failed' line exists
        assert "error" in components["entra"]
        assert "Entra check: starting" in components["entra"]["error"]

    @patch("azext_connectedk8s._precheckutils.telemetry")
    def test_crd_error_extracted_from_diagnoser_output(self, mock_telemetry):
        precheckutils.prediagnostic_crd_check = consts.Diagnostic_Check_Failed
        precheckutils.diagnoser_output = [
            "CRD ownership error: extensionconfigs.clusterconfig.azure.com owned by another release",
        ]
        precheckutils.send_prediagnostic_check_failure_telemetry(
            consts.Diagnostic_Check_Passed, consts.Diagnostic_Check_Passed
        )

        props = mock_telemetry.add_extension_event.call_args[0][1]
        msg = json.loads(props[consts.Telemetry_Onboarding_Error_Message_Key])
        components = {entry["componentName"]: entry for entry in msg}
        assert "error" in components["crd"]

    @patch("azext_connectedk8s._precheckutils.telemetry")
    def test_precheck_summary_line_excluded_from_error_details(self, mock_telemetry):
        """The 'Precheck summary:' metadata line should not be captured as an error detail."""
        precheckutils.prediagnostic_outbound_check = consts.Diagnostic_Check_Failed
        precheckutils.diagnoser_output = [
            "Error: Outbound connectivity failed for: https://example.com (code=000, no HTTP response - likely firewall drop, proxy block, or network timeout)",
            "Precheck summary: jobExecutionStatus=NotCompleted; dnsCheck=Passed; outboundConnectivityCheck=Failed; entraCheck=NotApplicable; crdCheck=Passed",
        ]
        precheckutils.send_prediagnostic_check_failure_telemetry(
            consts.Diagnostic_Check_Passed, consts.Diagnostic_Check_Failed
        )

        props = mock_telemetry.add_extension_event.call_args[0][1]
        msg = json.loads(props[consts.Telemetry_Onboarding_Error_Message_Key])
        components = {entry["componentName"]: entry for entry in msg}
        # Should only contain the actual error, not the Precheck summary line
        assert "error" in components["outboundConnectivity"]
        assert "Precheck summary" not in components["outboundConnectivity"]["error"]
        assert "code=000" in components["outboundConnectivity"]["error"]
        assert "firewall drop" in components["outboundConnectivity"]["error"]


# ---------------------------------------------------------------------------
# send_post_diagnostic_precheck_failure_telemetry
# ---------------------------------------------------------------------------


class TestSendPostDiagnosticPrecheckFailureTelemetry:
    def setup_method(self):
        _reset_globals()

    @patch("azext_connectedk8s._precheckutils.telemetry")
    def test_sends_event_with_correct_error_type(self, mock_telemetry):
        precheckutils.send_post_diagnostic_precheck_failure_telemetry(
            "LinuxNodeExists", "No Linux nodes found"
        )

        mock_telemetry.add_extension_event.assert_called_once()
        props = mock_telemetry.add_extension_event.call_args[0][1]
        assert (
            props[consts.Telemetry_Onboarding_Error_Type_Key]
            == consts.Post_Diagnostic_Precheck_Fault_Type
        )

    @patch("azext_connectedk8s._precheckutils.telemetry")
    def test_message_includes_check_name_and_reason(self, mock_telemetry):
        precheckutils.send_post_diagnostic_precheck_failure_telemetry(
            "ClusterRoleBindings", "Insufficient permissions"
        )

        props = mock_telemetry.add_extension_event.call_args[0][1]
        msg = json.loads(props[consts.Telemetry_Onboarding_Error_Message_Key])
        assert msg["checkName"] == "ClusterRoleBindings"
        assert msg["reason"] == "Insufficient permissions"

    @patch("azext_connectedk8s._precheckutils.telemetry")
    def test_message_is_valid_json(self, mock_telemetry):
        precheckutils.send_post_diagnostic_precheck_failure_telemetry(
            "SomeCheck", "Some reason"
        )

        props = mock_telemetry.add_extension_event.call_args[0][1]
        msg = json.loads(props[consts.Telemetry_Onboarding_Error_Message_Key])
        assert isinstance(msg, dict)

    @patch("azext_connectedk8s._precheckutils.telemetry")
    def test_different_check_names_produce_separate_events(self, mock_telemetry):
        precheckutils.send_post_diagnostic_precheck_failure_telemetry(
            "LinuxNodeExists", "No nodes"
        )
        precheckutils.send_post_diagnostic_precheck_failure_telemetry(
            "ClusterRoleBindings", "No perms"
        )

        assert mock_telemetry.add_extension_event.call_count == 2
        calls = mock_telemetry.add_extension_event.call_args_list
        msg1 = json.loads(calls[0][0][1][consts.Telemetry_Onboarding_Error_Message_Key])
        msg2 = json.loads(calls[1][0][1][consts.Telemetry_Onboarding_Error_Message_Key])
        assert msg1["checkName"] == "LinuxNodeExists"
        assert msg2["checkName"] == "ClusterRoleBindings"


# ---------------------------------------------------------------------------
# fetch_diagnostic_checks_results log parsing
# ---------------------------------------------------------------------------


CONFORMANCE_PREDIAGNOSTIC_OUTPUT = """\
Thu Aug 20 19:11:59 UTC 2026 : Performing check: 1 of 5 - DNS and outbound connectivity
DNS Result:;; Got recursion not available from 10.89.0.10
;; Got recursion not available from 10.89.0.10
Server:		10.89.0.10
Address:	10.89.0.10#53

Name: kubernetes.default.svc.cluster.local
Address: 10.89.0.1
;; Got recursion not available from 10.89.0.10
Thu Aug 20 19:12:01 UTC 2026 : Performing check: 2 of 5 - Entra (Azure AD) authentication endpoint connectivity. This is a mandatory endpoint for Azure Arc authentication.
Entra endpoint connectivity check passed. Response Code: 200
Entra Authentication Endpoint Connectivity Check Result : https://login.microsoftonline.com : 200
Thu Aug 20 19:12:01 UTC 2026 : Performing check: 3 of 5 - Outbound connectivity for Cluster Connect Pre-check Endpoint. This is an optional endpoint required only for cluster-connect functionality
Warning - Cluster Connect Pre-check Endpoint https://eastus2euap.obo.arc.azure.com:8084/ is not reachable. Response Code : 404
Response Code - Outbound Network Connectivity Check for Cluster Connect : https://eastus2euap.obo.arc.azure.com:8084/ : 404
Warning - Cluster Connect Pre-check Endpoint https://eastus2euap.obo.arc.azure.com/ is not reachable. Response Code : 404
Response Code - Outbound Network Connectivity Check for Cluster Connect : https://eastus2euap.obo.arc.azure.com/ : 404
Thu Aug 20 19:12:03 UTC 2026 : Performing check: 4 of 5 - Outbound connectivity for MCR repo URL. This is a mandatory endpoint.
Outbound Network Connectivity Check for MCR Repo URL Result : mcr.microsoft.com : 200
Thu Aug 20 19:12:04 UTC 2026 : Performing check: 5 of 5 - CRD ownership validation
CRD extensionconfigs.clusterconfig.azure.com does not exist - OK (will be created during Arc installation)
CRD configsyncstatuses.clusterconfig.azure.com does not exist - OK (will be created during Arc installation)
All PreOnboading Diagnostic Checks passed successfully
"""


def _run_completed_prediagnostic_output(monkeypatch, output):
    def execute_job(*_args, **_kwargs):
        precheckutils.prediagnostic_job_execution_status = consts.Job_Status_Completed
        return output

    def parse_dns(log, _path, storage_available, _diagnoser_output):
        result = (
            consts.Diagnostic_Check_Passed
            if consts.DNS_Check_Result_String in log
            else consts.Diagnostic_Check_Incomplete
        )
        return result, storage_available

    def parse_outbound(log, _path, storage_available, _diagnoser_output, **_kwargs):
        result = (
            consts.Diagnostic_Check_Passed
            if consts.Outbound_Connectivity_Check_Result_String in log
            else consts.Diagnostic_Check_Incomplete
        )
        return result, storage_available

    monkeypatch.setattr(
        precheckutils, "executing_cluster_diagnostic_checks_job", execute_job
    )
    monkeypatch.setattr(precheckutils.azext_utils, "check_cluster_DNS", parse_dns)
    monkeypatch.setattr(
        precheckutils.azext_utils,
        "check_cluster_outbound_connectivity",
        parse_outbound,
    )

    result, _ = precheckutils.fetch_diagnostic_checks_results(
        cmd=MagicMock(),
        corev1_api_instance=MagicMock(),
        batchv1_api_instance=MagicMock(),
        helm_client_location="helm",
        kubectl_client_location="kubectl",
        kube_config=None,
        kube_context=None,
        location="eastus2euap",
        http_proxy="",
        https_proxy="",
        no_proxy="",
        proxy_cert="",
        azure_cloud="AZUREPUBLICCLOUD",
        filepath_with_timestamp="/tmp/prediagnostics",
        storage_space_available=True,
    )
    return result


def test_completed_job_parses_healthy_1_36_1_output(monkeypatch):
    result = _run_completed_prediagnostic_output(
        monkeypatch, CONFORMANCE_PREDIAGNOSTIC_OUTPUT
    )

    assert result == consts.Diagnostic_Check_Passed
    assert precheckutils.prediagnostic_dns_check == consts.Diagnostic_Check_Passed
    assert precheckutils.prediagnostic_outbound_check == consts.Diagnostic_Check_Passed
    assert precheckutils.prediagnostic_entra_check == consts.Diagnostic_Check_Passed
    assert precheckutils.prediagnostic_crd_check == consts.Diagnostic_Check_Passed


def test_completed_job_parses_conformance_stringified_bytes(monkeypatch):
    escaped_output = repr(CONFORMANCE_PREDIAGNOSTIC_OUTPUT.encode("utf-8"))
    print(f"Stringified Kubernetes log: {escaped_output}")

    result = _run_completed_prediagnostic_output(monkeypatch, escaped_output)

    assert (
        precheckutils.prediagnostic_dns_check,
        precheckutils.prediagnostic_outbound_check,
        precheckutils.prediagnostic_entra_check,
        precheckutils.prediagnostic_crd_check,
    ) == (
        consts.Diagnostic_Check_Passed,
        consts.Diagnostic_Check_Passed,
        consts.Diagnostic_Check_Passed,
        consts.Diagnostic_Check_Passed,
    )
    assert result == consts.Diagnostic_Check_Passed


def test_completed_job_parses_byte_output(monkeypatch):
    result = _run_completed_prediagnostic_output(
        monkeypatch, CONFORMANCE_PREDIAGNOSTIC_OUTPUT.encode("utf-8")
    )

    assert result == consts.Diagnostic_Check_Passed
    assert precheckutils.prediagnostic_dns_check == consts.Diagnostic_Check_Passed
    assert precheckutils.prediagnostic_outbound_check == consts.Diagnostic_Check_Passed
    assert precheckutils.prediagnostic_entra_check == consts.Diagnostic_Check_Passed
    assert precheckutils.prediagnostic_crd_check == consts.Diagnostic_Check_Passed


def test_normalize_container_log_preserves_text():
    container_log = "DNS Result: success\nOutbound Result: success\n"

    assert precheckutils.normalize_container_log(container_log) == container_log.strip()


def test_normalize_container_log_decodes_bytes():
    container_log = "DNS Result: success\nOutbound Result: success\n"

    assert (
        precheckutils.normalize_container_log(container_log.encode())
        == container_log.strip()
    )


def test_normalize_container_log_decodes_stringified_bytes():
    container_log = "DNS Result: success\nOutbound Result: success\n"

    assert (
        precheckutils.normalize_container_log(repr(container_log.encode()))
        == container_log.strip()
    )


def test_normalize_container_log_preserves_malformed_byte_literal():
    malformed_log = "b'not a complete byte literal"

    assert precheckutils.normalize_container_log(malformed_log) == malformed_log


def test_split_container_log_preserves_last_line_without_trailing_newline():
    container_log = "DNS Result: success\nOutbound Result: success"

    assert precheckutils.split_container_log(container_log) == [
        "DNS Result: success",
        "Outbound Result: success",
    ]


def test_split_container_log_handles_stringified_bytes():
    container_log = "DNS Result: success\nOutbound Result: success\n"

    assert precheckutils.split_container_log(repr(container_log.encode())) == [
        "DNS Result: success",
        "Outbound Result: success",
    ]


@pytest.mark.parametrize(
    ("reason", "expected_hint"),
    [
        ("ErrImagePull", "Verify connectivity to MCR and proxy settings"),
        ("ImagePullBackOff", "Verify connectivity to MCR and proxy settings"),
        ("CrashLoopBackOff", "Review the saved container logs"),
    ],
)
def test_incomplete_job_diagnostic_maps_waiting_reason(reason, expected_hint):
    pod = MagicMock()
    pod.status.container_statuses = [MagicMock()]
    pod.status.container_statuses[0].state.waiting.reason = reason
    pod.status.container_statuses[0].state.terminated = None

    diagnostic = precheckutils._get_incomplete_job_diagnostic(pod)

    assert f"Pod reason: {reason}" in diagnostic
    assert expected_hint in diagnostic


def test_incomplete_job_diagnostic_maps_unschedulable_pod():
    pod = MagicMock()
    pod.status.container_statuses = []
    pod.status.conditions = [
        MagicMock(type="PodScheduled", status="False", reason="Unschedulable")
    ]

    diagnostic = precheckutils._get_incomplete_job_diagnostic(pod)

    assert "Pod reason: Unschedulable" in diagnostic
    assert "Verify node resources, taints, and namespace quotas" in diagnostic


def test_incomplete_job_diagnostic_maps_oom_killed_container():
    pod = MagicMock()
    container_status = MagicMock()
    container_status.state.waiting = None
    container_status.state.terminated.reason = "OOMKilled"
    container_status.state.terminated.exit_code = 137
    pod.status.container_statuses = [container_status]

    diagnostic = precheckutils._get_incomplete_job_diagnostic(pod)

    assert "Pod reason: OOMKilled" in diagnostic
    assert "Ensure the cluster has sufficient memory" in diagnostic


def test_incomplete_job_diagnostic_maps_nonzero_exit_code():
    pod = MagicMock()
    container_status = MagicMock()
    container_status.state.waiting = None
    container_status.state.terminated.reason = "Error"
    container_status.state.terminated.exit_code = 2
    pod.status.container_statuses = [container_status]

    diagnostic = precheckutils._get_incomplete_job_diagnostic(pod)

    assert "Pod reason: Error (exit code 2)" in diagnostic
    assert "Review the saved container logs" in diagnostic


def test_incomplete_job_diagnostic_has_unknown_state_fallback():
    pod = MagicMock()
    pod.status.container_statuses = []
    pod.status.conditions = []
    pod.status.reason = None

    diagnostic = precheckutils._get_incomplete_job_diagnostic(pod)

    assert diagnostic == (
        "Review the saved pod description and container logs, then retry."
    )


def test_diagnostic_job_watch_uses_180_second_timeout(monkeypatch):
    _reset_globals()

    complete_condition = MagicMock(type="Complete", status="True")
    completed_job = MagicMock()
    completed_job.metadata.name = "cluster-diagnostic-checks-job"
    completed_job.status.failed = None
    completed_job.status.conditions = [complete_condition]
    watcher = MagicMock()
    watcher.stream.return_value = iter([{"object": completed_job}])

    batchv1_api = MagicMock()

    pod = MagicMock()
    pod.metadata.name = "cluster-diagnostic-checks-job-abc12"
    pod.metadata.creation_timestamp = "2026-08-21T23:02:22Z"
    corev1_api = MagicMock()
    corev1_api.list_namespaced_pod.return_value = MagicMock(items=[pod])
    corev1_api.read_namespaced_pod_log.return_value = "diagnostic output"

    cmd = MagicMock()
    cmd.cli_ctx.cloud.endpoints.active_directory = "https://login.microsoftonline.com"
    monkeypatch.setattr(precheckutils.watch, "Watch", lambda: watcher)
    monkeypatch.setattr(precheckutils.config, "load_kube_config", MagicMock())
    monkeypatch.setattr(precheckutils, "Popen", MagicMock())
    monkeypatch.setattr(
        precheckutils,
        "helm_install_release_cluster_diagnostic_checks",
        MagicMock(),
    )
    monkeypatch.setattr(
        precheckutils.azext_utils,
        "get_release_namespace",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        precheckutils.azext_utils,
        "get_mcr_path",
        lambda *_args: "mcr.microsoft.com",
    )
    monkeypatch.setattr(
        precheckutils.azext_utils, "get_chart_path", lambda *_args: "/fake/chart"
    )

    precheckutils.executing_cluster_diagnostic_checks_job(
        cmd=cmd,
        corev1_api_instance=corev1_api,
        batchv1_api_instance=batchv1_api,
        helm_client_location="helm",
        kubectl_client_location="kubectl",
        kube_config=None,
        kube_context=None,
        location="eastus",
        http_proxy="",
        https_proxy="",
        no_proxy="",
        proxy_cert="",
        azure_cloud="AZUREPUBLICCLOUD",
        filepath_with_timestamp="/tmp/prediagnostics",
        storage_space_available=False,
    )

    watcher.stream.assert_called_once_with(
        batchv1_api.list_namespaced_job,
        namespace="azure-arc-release",
        label_selector="",
        timeout_seconds=180,
    )
    batchv1_api.read_namespaced_job.assert_not_called()
    assert (
        precheckutils.prediagnostic_job_execution_status == consts.Job_Status_Completed
    )
