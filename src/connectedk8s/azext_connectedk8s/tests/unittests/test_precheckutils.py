# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Unit tests for prediagnostic telemetry functions in _precheckutils.py."""

from __future__ import annotations

import json
import os
import sys
from unittest.mock import MagicMock, patch

# Stub out heavy dependencies before importing the module under test.
# The _precheckutils module imports kubernetes, azure.cli.core, knack, etc. at module level.
# In lightweight test environments (no full CLI installed), we inject MagicMock stubs into
# sys.modules so the import succeeds. In full azdev CI, the real modules are already loaded
# and setdefault() leaves them untouched.
_STUBS = {
    "kubernetes": MagicMock(),
    "kubernetes.config": MagicMock(),
    "kubernetes.watch": MagicMock(),
    "kubernetes.client": MagicMock(),
    "kubernetes.client.models": MagicMock(),
    "azure": MagicMock(),
    "azure.cli": MagicMock(),
    "azure.cli.core": MagicMock(),
    "azure.cli.core.telemetry": MagicMock(),
    "azure.cli.core.azclierror": MagicMock(),
    "azure.cli.core.commands": MagicMock(),
    "azure.cli.core.commands.client_factory": MagicMock(),
    "azure.cli.core.util": MagicMock(),
    "azure.cli.core._config": MagicMock(),
    "azure.core": MagicMock(),
    "azure.core.exceptions": MagicMock(),
    "azure.mgmt": MagicMock(),
    "azure.mgmt.core": MagicMock(),
    "azure.mgmt.core.tools": MagicMock(),
    "msrest": MagicMock(),
    "msrestazure": MagicMock(),
    "knack": MagicMock(),
    "knack.log": MagicMock(),
    "knack.help_files": MagicMock(),
    "knack.util": MagicMock(),
    "knack.cli": MagicMock(),
    "knack.config": MagicMock(),
    "knack.prompting": MagicMock(),
    "knack.commands": MagicMock(),
    "knack.arguments": MagicMock(),
    "knack.events": MagicMock(),
    # Stub the sibling module to avoid its transitive imports
    "azext_connectedk8s._utils": MagicMock(),
}
_ORIGINAL_MODULES = {mod: sys.modules.get(mod) for mod in _STUBS}
for mod, stub in _STUBS.items():
    sys.modules.setdefault(mod, stub)

# Make process_helm_error_detail a transparent passthrough so telemetry message assertions work.
# Only patch if this is our MagicMock stub — if the real module is already loaded (e.g. in full
# azdev CI), patching it here would permanently mutate its attribute on the shared module object.
_utils_stub = sys.modules.get("azext_connectedk8s._utils")
if isinstance(_utils_stub, MagicMock):
    _utils_stub.process_helm_error_detail = lambda x: x

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import azext_connectedk8s._constants as consts  # noqa: E402
import azext_connectedk8s._precheckutils as precheckutils  # noqa: E402

for mod, original_module in _ORIGINAL_MODULES.items():
    if original_module is None:
        sys.modules.pop(mod, None)
    else:
        sys.modules[mod] = original_module

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _reset_globals():
    """Reset module-level globals to a clean state before each test."""
    precheckutils.diagnoser_output = []
    precheckutils.prediagnostic_job_execution_status = consts.Job_Status_Not_Started
    precheckutils.prediagnostic_entra_check = consts.Diagnostic_Check_Starting
    precheckutils.prediagnostic_crd_check = consts.Diagnostic_Check_Starting


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
