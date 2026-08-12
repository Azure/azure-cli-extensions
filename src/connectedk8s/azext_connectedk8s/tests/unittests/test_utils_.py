# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock
from urllib.parse import urlunsplit

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

if isinstance(sys.modules.get("azext_connectedk8s._utils"), MagicMock):
    sys.modules.pop("azext_connectedk8s._utils", None)

_STUBS = {
    "azure": MagicMock(),
    "azure.cli": MagicMock(),
    "azure.cli.core": MagicMock(),
    "azure.cli.core.azclierror": MagicMock(),
    "azure.cli.core.commands": MagicMock(),
    "azure.cli.core.commands.client_factory": MagicMock(),
    "azure.cli.core.util": MagicMock(),
    "azure.core": MagicMock(),
    "azure.core.exceptions": MagicMock(),
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
    "kubernetes": MagicMock(),
    "kubernetes.client": MagicMock(),
    "kubernetes.client.rest": MagicMock(),
    "msrest": MagicMock(),
    "msrest.exceptions": MagicMock(),
    "azext_connectedk8s._client_factory": MagicMock(),
}
for mod, stub in _STUBS.items():
    sys.modules.setdefault(mod, stub)

from azure.cli.core.azclierror import (  # noqa: E402
    ArgumentUsageError,
    CLIInternalError,
    FileOperationError,
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
    RequiredArgumentMissingError,
    ValidationError,
)

import azext_connectedk8s._errors as errors_module  # noqa: E402
import azext_connectedk8s._utils as utils_module  # noqa: E402
from azext_connectedk8s._errors import ArcError  # noqa: E402
from azext_connectedk8s._utils import (  # noqa: E402
    HelmTimeoutReport,
    _build_helm_timeout_telemetry_properties,
    _collect_timeout_diagnostics_from_events,
    _collect_timeout_diagnostics_from_pods,
    _resolve_helm_timeout_classification,
    build_helm_timeout_report,
    check_cluster_DNS,
    get_advanced_helm_timeout_fault_type,
    get_mcr_path,
    is_helm_timeout_error,
    process_helm_error_detail,
    redact_sensitive_fields_from_string,
    remove_rsa_private_key,
    report_connectedk8s_error,
    report_helm_timeout_error,
    scrub_proxy_url,
    should_use_secret_injection_flow,
)


def _build_test_proxy_url(username, password):
    # Avoid storing credential-shaped URLs in the test source.
    credentials = f"{username}:{password}"
    return urlunsplit(("http", f"{credentials}@example.com:8080", "", "", ""))


def test_remove_rsa_private_key():
    _header = "-----BEGIN " + "RSA PRIVATE KEY" + "-----"
    _footer = "-----END " + "RSA PRIVATE KEY" + "-----"
    input_text = f"Error: {_header}\nFAKE_KEY_DATA_FOR_TESTING\n{_footer}"
    expected_output = "Error: [RSA PRIVATE KEY REMOVED]"
    assert remove_rsa_private_key(input_text) == expected_output

    input_text_no_key = "Error: No RSA key here"
    assert remove_rsa_private_key(input_text_no_key) == input_text_no_key


def test_scrub_proxy_url_with_url():
    proxy_url = _build_test_proxy_url("proxy", "pass")
    redacted_proxy_url = _build_test_proxy_url("[REDACTED]", "[REDACTED]")
    input_text = f"text with proxy URL {proxy_url} in it"
    expected_output = f"text with proxy URL {redacted_proxy_url} in it"
    assert scrub_proxy_url(input_text) == expected_output


def test_scrub_proxy_url_without_url():
    input_text = "text without proxy URL"
    assert scrub_proxy_url(input_text) == input_text


def test_process_helm_error_detail():
    _header = "-----BEGIN " + "RSA PRIVATE KEY" + "-----"
    _footer = "-----END " + "RSA PRIVATE KEY" + "-----"
    proxy_url = _build_test_proxy_url("proxy", "pass")
    redacted_proxy_url = _build_test_proxy_url("[REDACTED]", "[REDACTED]")
    input_text = (
        f"Some text\n{_header}\nkey\n{_footer}\n"
        f"with proxy URL {proxy_url} in it"
    )
    expected_output = (
        "Some text\n[RSA PRIVATE KEY REMOVED]\n"
        f"with proxy URL {redacted_proxy_url} in it"
    )
    assert process_helm_error_detail(input_text) == expected_output


def test_process_helm_error_detail_no_changes():
    input_text = "Some text without RSA key or proxy URL"
    assert process_helm_error_detail(input_text) == input_text


def test_redact_sensitive_fields_from_string():
    sensitive_fields = ("user" + "name", "pass" + "word", "to" + "ken")
    input_text = "\n".join(f"{field}: test-value" for field in sensitive_fields)
    expected_output = "username: [REDACTED]\npassword: [REDACTED]\ntoken: [REDACTED]"
    assert redact_sensitive_fields_from_string(input_text) == expected_output

    input_text_no_sensitive = "No sensitive data here"
    assert (
        redact_sensitive_fields_from_string(input_text_no_sensitive)
        == input_text_no_sensitive
    )

    input_text_partial = "\n".join(
        (
            f"{sensitive_fields[0]}: test-value",
            "hello_data: safe",
            f"{sensitive_fields[1]}: test-value",
        )
    )
    expected_output_partial = (
        "username: [REDACTED]\nhello_data: safe\npassword: [REDACTED]"
    )
    assert (
        redact_sensitive_fields_from_string(input_text_partial)
        == expected_output_partial
    )


def test_get_mcr_path():
    input_active_directory = "login.microsoftonline.com"
    expected_output = "mcr.microsoft.com"
    assert get_mcr_path(input_active_directory) == expected_output

    input_active_directory = "login.microsoftonline.us"
    expected_output = "mcr.microsoft.com"
    assert get_mcr_path(input_active_directory) == expected_output

    input_active_directory = "login.chinacloudapi.cn"
    expected_output = "mcr.microsoft.com"
    assert get_mcr_path(input_active_directory) == expected_output

    input_active_directory = "https://login.microsoftonline.microsoft.foo"
    expected_output = "mcr.microsoft.foo"
    assert get_mcr_path(input_active_directory) == expected_output

    input_active_directory = "https://login.microsoftonline.some.cloud.bar"
    expected_output = "mcr.microsoft.some.cloud.bar"
    assert get_mcr_path(input_active_directory) == expected_output


def test_is_helm_timeout_error():
    assert is_helm_timeout_error("Error: timed out waiting for the condition")
    assert is_helm_timeout_error("context deadline exceeded")
    assert not is_helm_timeout_error("Error: forbidden")


def test_collect_timeout_diagnostics_from_pods_image_pull_and_crashloop():
    pods = [
        SimpleNamespace(
            metadata=SimpleNamespace(name="config-agent-123"),
            status=SimpleNamespace(
                phase="Pending",
                init_container_statuses=None,
                container_statuses=[
                    SimpleNamespace(
                        name="config-agent",
                        ready=False,
                        restart_count=0,
                        state=SimpleNamespace(
                            waiting=SimpleNamespace(
                                reason="ImagePullBackOff",
                                message="failed to pull image",
                            )
                        ),
                    )
                ],
            ),
        ),
        SimpleNamespace(
            metadata=SimpleNamespace(name="clusteridentityoperator-123"),
            status=SimpleNamespace(
                phase="Running",
                init_container_statuses=None,
                container_statuses=[
                    SimpleNamespace(
                        name="clusteridentityoperator",
                        ready=False,
                        restart_count=4,
                        state=SimpleNamespace(
                            waiting=SimpleNamespace(
                                reason="CrashLoopBackOff",
                                message="back-off restarting failed container",
                            )
                        ),
                    )
                ],
            ),
        ),
    ]

    evidence, classifications = _collect_timeout_diagnostics_from_pods(pods)

    assert "ImagePullFailure" in classifications
    assert "CrashLoopBackOff" in classifications
    assert any("ImagePullBackOff" in item for item in evidence)
    assert any("CrashLoopBackOff" in item for item in evidence)


def test_collect_timeout_diagnostics_from_events_cluster_constraints():
    events = [
        SimpleNamespace(
            type="Warning",
            reason="FailedScheduling",
            message="0/3 nodes are available: 3 Insufficient cpu.",
            involved_object=SimpleNamespace(name="clusteridentityoperator-123"),
            last_timestamp="2026-07-01T00:00:00Z",
            event_time=None,
            metadata=SimpleNamespace(creation_timestamp=None),
        )
    ]

    evidence, classifications = _collect_timeout_diagnostics_from_events(events)

    assert "ClusterResourceOrSchedulingConstraint" in classifications
    assert any("Insufficient cpu" in item for item in evidence)


def test_collect_timeout_diagnostics_from_events_missing_kap_secret_is_key_sync():
    events = [
        SimpleNamespace(
            type="Warning",
            reason="FailedMount",
            message=(
                'MountVolume.SetUp failed for volume "kube-aad-proxy-tls" : '
                'secret "kube-aad-proxy-certificate" not found'
            ),
            involved_object=SimpleNamespace(name="kube-aad-proxy-123"),
            last_timestamp="2026-07-01T00:00:00Z",
            event_time=None,
            metadata=SimpleNamespace(creation_timestamp=None),
        )
    ]

    evidence, classifications = _collect_timeout_diagnostics_from_events(events)

    assert "KeyPairOrIdentityCertificateSync" in classifications
    assert "MissingKubeAadProxyCertificateSecret" in classifications
    assert any("kube-aad-proxy-certificate" in item for item in evidence)


def test_build_helm_timeout_telemetry_properties_marks_classifications():
    properties = _build_helm_timeout_telemetry_properties(
        {"ImagePullFailure", "CrashLoopBackOff"},
        evidence_count=2,
        diagnostics_status="Collected",
        helm_operation="install",
    )

    assert properties["Context.Default.AzureCLI.helmTimeout"] == "true"
    assert properties["Context.Default.AzureCLI.helmOperation"] == "install"
    assert (
        properties["Context.Default.AzureCLI.helmTimeoutClassification"]
        == "ImagePullFailure"
    )
    assert properties["Context.Default.AzureCLI.helmTimeoutEvidenceCount"] == "2"
    assert properties["Context.Default.AzureCLI.helmTimeoutImagePullFailure"] == "true"
    assert (
        properties["Context.Default.AzureCLI.helmTimeoutGenericHelmTimeout"] == "false"
    )
    assert (
        properties["Context.Default.AzureCLI.helmTimeoutPendingOrUnschedulable"]
        == "false"
    )


def test_resolve_helm_timeout_classification_priority():
    assert (
        _resolve_helm_timeout_classification(
            {"ImagePullFailure", "KeyPairOrIdentityCertificateSync"}
        )
        == "ImagePullFailure"
    )
    assert (
        _resolve_helm_timeout_classification(
            {"ImagePullFailure", "PendingOrUnschedulable"}
        )
        == "ImagePullFailure"
    )
    assert (
        _resolve_helm_timeout_classification(
            {
                "ClusterResourceOrSchedulingConstraint",
                "KeyPairOrIdentityCertificateSync",
            }
        )
        == "PendingOrUnschedulable"
    )
    assert (
        _resolve_helm_timeout_classification({"CrashLoopBackOff"})
        == "GenericHelmTimeout"
    )


def test_get_advanced_helm_timeout_fault_type_from_error_message():
    error_message = (
        "context deadline exceeded\n\n"
        "Read-only cluster checks after Helm timeout:\n"
        "[AZK8S0309] Azure Arc agent identity/certificate sync did not finish "
        "before the Helm timeout."
    )

    assert (
        get_advanced_helm_timeout_fault_type(error_message)
        == "helm-timeout-cluster-identity-error"
    )


@pytest.mark.parametrize(
    "release_train,agent_version,expected",
    [
        # Stable train, agents older than 1.35.3 must use the legacy flow
        # (helm value injection) to avoid zeroing out the secret.
        ("stable", "1.35.2", False),
        ("stable", "1.34.9", False),
        ("stable", "1.20.0", False),
        ("STABLE", "1.14.0", False),
        # Stable train at or above the cutoff uses the secure flow.
        ("stable", "1.35.3", True),
        ("stable", "1.36.2", True),
        ("stable", "2.0.0", True),
        # Preview train uses 1.35.3-preview as the cutoff (same scheme).
        ("preview", "1.34.0", False),
        ("preview", "1.35.2-preview", False),
        ("preview", "1.35.3-preview", True),
        ("preview", "1.36.0-preview", True),
        ("PREVIEW", "1.20.0", False),
        # Dev-suffixed agent versions always use the secure flow, regardless of
        # the release train DP attributed them to.
        ("preview", "0.2.5738-dev", True),
        ("stable", "0.2.6689-dev", True),
        ("STABLE", "1.34.0-DEV", True),
        (None, "0.2.5738-dev", True),
        # Missing version on a gated train -> safe default (legacy flow).
        ("stable", None, False),
        ("preview", "", False),
        # Missing release train defaults to "stable".
        (None, "1.34.0", False),
        (None, "1.35.3", True),
        # Unparseable version on a gated train -> safe default (legacy flow).
        ("stable", "not-a-version", False),
    ],
)
def test_should_use_secret_injection_flow(release_train, agent_version, expected):
    assert (
        should_use_secret_injection_flow(release_train, agent_version) is expected
    )


def test_arc_error_requires_code_name_message_and_fault_type():
    valid = {
        "code": "AZK8S0009",
        "name": "TestError",
        "message": "Test message.",
        "fault_type": "test-error",
    }
    for field in valid:
        invalid = valid.copy()
        invalid[field] = ""
        with pytest.raises(ValueError):
            ArcError(**invalid)


def test_arc_error_formats_optional_tsg_link():
    error = ArcError(
        code="AZK8S0009",
        name="TestError",
        message="Test message: {details}",
        fault_type="test-error",
        tsg_link="https://aka.ms/connectedk8s-test",
    )

    assert error.format(details="details") == (
        "[AZK8S0009] TestError: Test message: details\n"
        "Troubleshooting: https://aka.ms/connectedk8s-test"
    )


def test_error_catalog_contains_allocated_codes_and_fault_type_aliases():
    expected_codes = {
        *(f"AZK8S{code:04d}" for code in range(1, 4)),
        *(f"AZK8S{code:04d}" for code in range(100, 107)),
        *(f"AZK8S{code:04d}" for code in range(200, 209)),
        *(f"AZK8S{code:04d}" for code in range(300, 310)),
        *(f"AZK8S{code:04d}" for code in range(400, 410)),
        *(f"AZK8S{code:04d}" for code in range(500, 515)),
        *(f"AZK8S{code:04d}" for code in range(600, 608)),
        *(f"AZK8S{code:04d}" for code in range(700, 703)),
        *(f"AZK8S{code:04d}" for code in range(800, 806)),
    }
    assert set(errors_module.ERROR_CATALOG) == expected_codes
    assert (
        errors_module.get_error("AZK8S0805")
        is errors_module.CLUSTER_CREDENTIALS_GET_FAILED
    )
    assert (
        errors_module.get_error_by_fault_type(
            errors_module.consts.Custom_Locations_OID_Fetch_Fault_Type_CLOid_None
        )
        is errors_module.CUSTOM_LOCATIONS_OID_FETCH_FAILED
    )
    assert (
        errors_module.get_error_by_fault_type(
            errors_module.consts.Get_Helm_Values_Failed
        )
        is errors_module.HELM_VALUES_GET_FAILED
    )


def test_error_catalog_codes_use_standard_format():
    assert all(
        len(error.code) == 9
        and error.code.startswith("AZK8S")
        and error.code[5:].isdigit()
        for error in errors_module.ALL_ERRORS
    )
    with pytest.raises(ValueError):
        ArcError(
            code="INVALID",
            name="InvalidCode",
            message="Invalid code.",
            fault_type="invalid-code",
        )


def test_error_catalog_fault_types_are_stable_identifiers():
    assert all(
        "{" not in fault_type and "}" not in fault_type
        for error in errors_module.ALL_ERRORS
        for fault_type in error.all_fault_types
    )


def test_non_fatal_catalog_entries_do_not_build_cli_exceptions():
    with pytest.raises(ValueError, match="non-raising diagnostic error"):
        errors_module.DNS_NXDOMAIN.as_error()


def test_error_catalog_uses_proposed_exception_classes():
    non_default_classes = {
        "AZK8S0003": InvalidArgumentValueError,
        "AZK8S0100": InvalidArgumentValueError,
        "AZK8S0101": RequiredArgumentMissingError,
        "AZK8S0102": MutuallyExclusiveArgumentError,
        "AZK8S0103": InvalidArgumentValueError,
        "AZK8S0104": InvalidArgumentValueError,
        "AZK8S0105": ArgumentUsageError,
        "AZK8S0106": InvalidArgumentValueError,
        "AZK8S0200": FileOperationError,
        "AZK8S0203": ValidationError,
        "AZK8S0403": ArgumentUsageError,
        "AZK8S0404": ArgumentUsageError,
        "AZK8S0405": ArgumentUsageError,
        "AZK8S0406": ValidationError,
        "AZK8S0408": ValidationError,
        "AZK8S0602": ValidationError,
        "AZK8S0603": ValidationError,
        "AZK8S0803": FileOperationError,
    }
    non_raising_codes = {
        "AZK8S0301",
        "AZK8S0302",
        "AZK8S0303",
        "AZK8S0304",
        "AZK8S0305",
        "AZK8S0306",
        "AZK8S0307",
        "AZK8S0308",
        "AZK8S0606",
    }

    for code, error in errors_module.ERROR_CATALOG.items():
        if code in non_raising_codes:
            assert error.az_error_cls is None
        else:
            assert error.az_error_cls is non_default_classes.get(code, CLIInternalError)


def test_report_connectedk8s_error_uses_same_message_and_includes_arm_id(
    monkeypatch,
):
    class TestCLIError(Exception):
        pass

    error = ArcError(
        code="AZK8S0009",
        name="TestError",
        message="Test message: {details}",
        fault_type="test-error",
        az_error_cls=TestCLIError,
    )
    arm_id = (
        "/subscriptions/sub/resourceGroups/rg/providers/"
        "Microsoft.Kubernetes/connectedClusters/cluster"
    )
    cmd = SimpleNamespace(cli_ctx=SimpleNamespace(data={"connectedk8s_arm_id": arm_id}))
    mock_telemetry = MagicMock()
    monkeypatch.setattr(utils_module, "telemetry", mock_telemetry)

    reported_error = report_connectedk8s_error(
        cmd,
        error,
        exception=RuntimeError("underlying"),
        user_fault=True,
        details="details",
    )

    expected_message = "[AZK8S0009] TestError: Test message: details"
    assert isinstance(reported_error, TestCLIError)
    assert str(reported_error) == expected_message
    event_name, properties = mock_telemetry.add_extension_event.call_args.args
    assert event_name == "connectedk8s"
    assert properties["Context.Default.AzureCLI.resourceid"] == arm_id
    assert properties["Context.Default.AzureCLI.errorCode"] == "AZK8S0009"
    assert properties["Context.Default.AzureCLI.errorFaultType"] == "test-error"
    assert properties["Context.Default.AzureCLI.errorName"] == "TestError"
    assert properties["Context.Default.AzureCLI.errorMessage"] == expected_message
    assert mock_telemetry.set_exception.call_args.kwargs["summary"] == expected_message
    mock_telemetry.set_user_fault.assert_called_once_with()


def test_build_helm_timeout_report_preserves_failed_diagnostics(monkeypatch):
    telemetry_properties = _build_helm_timeout_telemetry_properties(
        set(), 0, "Failed", "install"
    )
    monkeypatch.setattr(
        utils_module,
        "_collect_arc_agent_timeout_diagnostics",
        lambda: ("Unable to collect diagnostics", telemetry_properties),
    )

    report = build_helm_timeout_report(
        "context deadline exceeded", helm_operation="install"
    )

    assert report is not None
    assert report.error.code == "AZK8S0514"
    assert report.error.name == "HelmTimeout"
    assert report.details == (
        "Helm command output:\ncontext deadline exceeded\n\n"
        "Post-timeout diagnostics:\nUnable to collect diagnostics"
    )


def test_report_helm_timeout_error_uses_one_message_for_console_and_telemetry(
    monkeypatch,
):
    class TestCLIError(Exception):
        pass

    error = ArcError(
        code="AZK8S0009",
        name="TestTimeout",
        message="Timeout occurred.\n{details}",
        fault_type="test-timeout",
        az_error_cls=TestCLIError,
    )
    report = HelmTimeoutReport(
        error=error,
        details="Helm command output:\ncontext deadline exceeded",
        telemetry_properties={
            "Context.Default.AzureCLI.helmTimeoutClassification": "GenericHelmTimeout"
        },
        user_fault=False,
    )
    cmd = SimpleNamespace(cli_ctx=SimpleNamespace(data={}))
    mock_telemetry = MagicMock()
    monkeypatch.setattr(utils_module, "telemetry", mock_telemetry)

    reported_error = report_helm_timeout_error(cmd, report)

    expected_message = (
        "[AZK8S0009] TestTimeout: Timeout occurred.\n"
        "Helm command output:\ncontext deadline exceeded"
    )
    assert str(reported_error) == expected_message
    _, properties = mock_telemetry.add_extension_event.call_args.args
    assert properties["Context.Default.AzureCLI.errorMessage"] == expected_message
    assert (
        properties["Context.Default.AzureCLI.onboardingErrorMessage"]
        == expected_message
    )
    assert mock_telemetry.set_exception.call_args.kwargs["summary"] == expected_message
    mock_telemetry.add_extension_event.assert_called_once()
    mock_telemetry.set_exception.assert_called_once()


if __name__ == "__main__":
    pytest.main()


class TestCheckClusterDNS:
    def _run(self, dns_log):
        diagnoser_output = []
        result, _ = check_cluster_DNS(
            dns_log,
            os.path.join(os.path.dirname(__file__), "tmp_dns"),
            False,
            diagnoser_output,
        )
        return result, diagnoser_output

    def test_nxdomain_detected(self):
        log = "DNS Result: ** server can't find kubernetes.default.svc.cluster.local: NXDOMAIN"
        result, diag = self._run(log)
        assert result == "Failed"
        assert "type=NXDOMAIN" in diag[0]

    def test_servfail_detected(self):
        log = "DNS Result: ;; Got SERVFAIL reply from 10.96.0.10\n** server can't find kubernetes.default.dns.podman: SERVFAIL"
        result, diag = self._run(log)
        assert result == "Failed"
        assert "type=SERVFAIL" in diag[0]

    def test_timeout_detected(self):
        log = "DNS Result: ;; connection timed out; no servers could be reached"
        result, diag = self._run(log)
        assert result == "Failed"
        assert "type=no-servers-reachable" in diag[0]

    def test_passed(self):
        log = (
            "DNS Result: Name: kubernetes.default.svc.cluster.local\nAddress: 10.96.0.1"
        )
        result, diag = self._run(log)
        assert result == "Passed"
        assert diag == []
