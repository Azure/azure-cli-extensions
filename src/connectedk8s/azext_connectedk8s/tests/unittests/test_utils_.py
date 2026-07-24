# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from azext_connectedk8s._utils import (
    _build_helm_timeout_telemetry_properties,
    _collect_timeout_diagnostics_from_events,
    _collect_timeout_diagnostics_from_pods,
    _resolve_helm_timeout_classification,
    get_advanced_helm_timeout_fault_type,
    get_mcr_path,
    is_helm_timeout_error,
    process_helm_error_detail,
    redact_sensitive_fields_from_string,
    remove_rsa_private_key,
    scrub_proxy_url,
)


def test_remove_rsa_private_key():
    input_text = "Error: -----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA7\n-----END RSA PRIVATE KEY-----"
    expected_output = "Error: [RSA PRIVATE KEY REMOVED]"
    assert remove_rsa_private_key(input_text) == expected_output

    input_text_no_key = "Error: No RSA key here"
    assert remove_rsa_private_key(input_text_no_key) == input_text_no_key


def test_scrub_proxy_url_with_url():
    input_text = "text with proxy URL http://proxy:pass@example.com:8080 in it"
    expected_output = (
        "text with proxy URL http://[REDACTED]:[REDACTED]@example.com:8080 in it"
    )
    assert scrub_proxy_url(input_text) == expected_output


def test_scrub_proxy_url_without_url():
    input_text = "text without proxy URL"
    assert scrub_proxy_url(input_text) == input_text


def test_process_helm_error_detail():
    input_text = (
        "Some text\n-----BEGIN RSA PRIVATE KEY-----\nkey\n-----END RSA PRIVATE KEY-----\n"
        "with proxy URL http://proxy:pass@example.com:8080 in it"
    )
    expected_output = (
        "Some text\n[RSA PRIVATE KEY REMOVED]\n"
        "with proxy URL http://[REDACTED]:[REDACTED]@example.com:8080 in it"
    )
    assert process_helm_error_detail(input_text) == expected_output


def test_process_helm_error_detail_no_changes():
    input_text = "Some text without RSA key or proxy URL"
    assert process_helm_error_detail(input_text) == input_text


def test_redact_sensitive_fields_from_string():
    input_text = "username: admin\npassword: secret\ntoken: abc123"
    expected_output = "username: [REDACTED]\npassword: [REDACTED]\ntoken: [REDACTED]"
    assert redact_sensitive_fields_from_string(input_text) == expected_output

    input_text_no_sensitive = "No sensitive data here"
    assert (
        redact_sensitive_fields_from_string(input_text_no_sensitive)
        == input_text_no_sensitive
    )

    input_text_partial = "username: user1\nhello_data: safe\npassword: mypass"
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


if __name__ == "__main__":
    pytest.main()
