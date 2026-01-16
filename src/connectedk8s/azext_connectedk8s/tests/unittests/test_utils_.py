# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from azext_connectedk8s._utils import (
    get_mcr_path,
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


if __name__ == "__main__":
    pytest.main()
