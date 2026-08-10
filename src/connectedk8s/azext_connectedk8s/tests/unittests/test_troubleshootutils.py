# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from azext_connectedk8s import _troubleshootutils as troubleshootutils
from azext_connectedk8s import _constants as consts
from azext_connectedk8s import _errors as errors


def _failed_helm_process(error: bytes) -> MagicMock:
    process = MagicMock()
    process.returncode = 1
    process.communicate.return_value = (b"", error)
    return process


def test_executing_diagnoser_job_records_helm_failure_without_raising(monkeypatch):
    monkeypatch.setattr(
        troubleshootutils,
        "Popen",
        MagicMock(return_value=_failed_helm_process(b"Error: forbidden")),
    )
    report_diagnostic = MagicMock(return_value="[AZK8S0509] Helm failure")
    monkeypatch.setattr(
        troubleshootutils.azext_utils,
        "report_connectedk8s_diagnostic",
        report_diagnostic,
    )
    troubleshootutils.diagnoser_output.clear()

    result = troubleshootutils.executing_diagnoser_job(
        MagicMock(),
        MagicMock(),
        "diagnostics.txt",
        True,
        "/tmp",
        "helm",
        "kubectl",
        "azure-arc",
        consts.Diagnostic_Check_Passed,
        None,
        None,
    )

    assert result is None
    assert troubleshootutils.diagnoser_output == [
        "[AZK8S0509] Helm failure\n"
    ]
    assert report_diagnostic.call_args.args[1] is errors.HELM_VALUES_GET_FAILED
    assert report_diagnostic.call_args.kwargs["user_fault"] is True


def test_security_policy_check_records_helm_failure_without_overwriting(
    monkeypatch,
):
    monkeypatch.setattr(
        troubleshootutils,
        "Popen",
        MagicMock(
            return_value=_failed_helm_process(
                b"Error: timed out waiting for the condition"
            )
        ),
    )
    report_diagnostic = MagicMock(return_value="[AZK8S0509] Helm failure")
    monkeypatch.setattr(
        troubleshootutils.azext_utils,
        "report_connectedk8s_diagnostic",
        report_diagnostic,
    )
    telemetry_exception = MagicMock()
    monkeypatch.setattr(
        troubleshootutils.telemetry, "set_exception", telemetry_exception
    )
    troubleshootutils.diagnoser_output.clear()

    result = troubleshootutils.check_probable_cluster_security_policy(
        MagicMock(),
        "helm",
        "azure-arc",
        None,
        None,
    )

    assert result == consts.Diagnostic_Check_Incomplete
    assert troubleshootutils.diagnoser_output == [
        "[AZK8S0509] Helm failure\n"
    ]
    assert report_diagnostic.call_args.args[1] is errors.HELM_VALUES_GET_FAILED
    assert report_diagnostic.call_args.kwargs["user_fault"] is True
    telemetry_exception.assert_not_called()
