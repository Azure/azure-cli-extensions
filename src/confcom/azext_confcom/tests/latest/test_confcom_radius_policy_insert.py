# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Command-level tests for insert_policy_into_template.

Tests the core regex replacement that inserts base64-encoded policy strings
into bicep template ccePolicy annotation values.
"""

import tempfile

from azext_confcom.command.radius_policy_insert import insert_policy_into_template
from azext_confcom.lib.serialization import (
  PRERELEASE_COMMON_ENFORCEMENT_POINTS,
  PRERELEASE_WINDOWS_ENFORCEMENT_POINTS,
  WINDOWS_ENFORCEMENT_POINTS,
  policy_deserialize,
  policy_serialize,
)


def test_replaces_first_ccepolicy_in_bicep():
    """Should replace the first ccePolicy placeholder with the policy string."""
    template = """
resource container 'Applications.Core/containers@2023-10-01-preview' = {
  properties: {
    extensions: [
      {
        kind: 'kubernetesMetadata'
        annotations: {
          'microsoft.containerinstance.virtualnode.ccepolicy': ''
        }
      }
    ]
  }
}
"""
    result = insert_policy_into_template("test-policy-base64", template, 0)
    assert "'microsoft.containerinstance.virtualnode.ccepolicy': 'test-policy-base64'" in result


def test_replaces_nth_ccepolicy_by_index():
    """Should replace only the nth ccePolicy when container_index > 0."""
    template = """
resource c1 'Applications.Core/containers@2023-10-01-preview' = {
  properties: {
    extensions: [{
      annotations: { 'microsoft.containerinstance.virtualnode.ccepolicy': 'first' }
    }]
  }
}

resource c2 'Applications.Core/containers@2023-10-01-preview' = {
  properties: {
    extensions: [{
      annotations: { 'microsoft.containerinstance.virtualnode.ccepolicy': 'second' }
    }]
  }
}
"""
    result = insert_policy_into_template("replacement", template, 1)

    assert "'microsoft.containerinstance.virtualnode.ccepolicy': 'first'" in result
    assert "'microsoft.containerinstance.virtualnode.ccepolicy': 'replacement'" in result
    assert "'microsoft.containerinstance.virtualnode.ccepolicy': 'second'" not in result


def test_preserves_single_quote_style():
    """Should preserve single quotes around the value."""
    template = "{ 'microsoft.containerinstance.virtualnode.ccepolicy': '' }"
    result = insert_policy_into_template("policy", template, 0)
    assert "'policy'" in result


def test_preserves_double_quote_style():
    """Should preserve double quotes around the value."""
    template = '{ "microsoft.containerinstance.virtualnode.ccepolicy": "" }'
    result = insert_policy_into_template("policy", template, 0)
    assert '"policy"' in result


def test_no_change_when_index_out_of_range():
    """Should return unchanged template when index exceeds matches."""
    template = "{ 'microsoft.containerinstance.virtualnode.ccepolicy': '' }"
    result = insert_policy_into_template("policy", template, 99)
    assert result == template


def test_matches_direct_cce_policy_key():
    """Should match a bare ccePolicy key (not in annotation string)."""
    template = "{ ccePolicy: '' }"
    result = insert_policy_into_template("p1", template, 0)
    assert "ccePolicy: 'p1'" in result


def test_matches_case_insensitive_annotation():
    """Should match ccePolicy regardless of casing in the annotation key."""
    template = "{ 'Microsoft.ContainerInstance.VirtualNode.CcePolicy': '' }"
    result = insert_policy_into_template("p2", template, 0)
    assert "'p2'" in result


def test_serialization_preserves_allowed_log_providers():
    policy_text = """package policy
allowed_log_providers := ["Microsoft-Windows-Provider"]
mount_cims := data.framework.mount_cims
"""
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as policy_file:
        policy_file.write(policy_text)
        policy_file.flush()
        result = policy_serialize(policy_deserialize(policy_file.name))

    assert 'allowed_log_providers := [\n  "Microsoft-Windows-Provider"\n]' in result


def test_serialization_uses_windows_enforcement_points():
    policy_text = """package policy
api_version := "0.12.0"
mount_cims := data.framework.mount_cims
"""
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as policy_file:
        policy_file.write(policy_text)
        policy_file.flush()
        result = policy_serialize(policy_deserialize(policy_file.name))

    for name in WINDOWS_ENFORCEMENT_POINTS + PRERELEASE_WINDOWS_ENFORCEMENT_POINTS:
        assert f"{name} := data.framework.{name}" in result


def test_serialization_omits_windows_enforcement_points_for_linux():
    policy_text = "package policy\nmount_device := data.framework.mount_device\n"
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as policy_file:
        policy_file.write(policy_text)
        policy_file.flush()
        result = policy_serialize(policy_deserialize(policy_file.name))

    for name in PRERELEASE_COMMON_ENFORCEMENT_POINTS:
        assert f"{name} := data.framework.{name}" not in result
    for name in (
      "allow_log_provider_dropping",
      "allow_registry_changes_dropping",
      "allowed_log_providers",
    ):
      assert f"{name} :=" not in result
    for name in WINDOWS_ENFORCEMENT_POINTS:
        assert f"{name} := data.framework.{name}" not in result


def test_serialization_uses_prerelease_linux_enforcement_points():
    policy_text = """package policy
api_version := "0.12.0"
mount_device := data.framework.mount_device
"""
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as policy_file:
        policy_file.write(policy_text)
        policy_file.flush()
        result = policy_serialize(policy_deserialize(policy_file.name))

    for name in PRERELEASE_COMMON_ENFORCEMENT_POINTS:
        assert f"{name} := data.framework.{name}" in result


def test_serialization_preserves_mapped_directories_and_registry_changes():
    policy_text = """package policy
api_version := "0.12.0"
framework_version := "0.5.0"
containers := [
  {
    "registry_changes": {
      "add_values": [],
      "delete_keys": []
    }
  }
]
mapped_directories := [
  {
    "container_path": "C:\\\\data",
    "read_only": true
  }
]
mount_cims := data.framework.mount_cims
"""
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as policy_file:
        policy_file.write(policy_text)
        policy_file.flush()
        policy = policy_deserialize(policy_file.name)
        result = policy_serialize(policy)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as result_file:
        result_file.write(result)
        result_file.flush()
        round_tripped_policy = policy_deserialize(result_file.name)

    assert policy.mapped_directories == [
        {"container_path": "C:\\data", "read_only": True}
    ]
    assert policy.containers[0].registry_changes == {
        "add_values": [],
        "delete_keys": [],
    }
    assert '"registry_changes": {' in result
    assert "mapped_directories := [" in result
    assert round_tripped_policy.mapped_directories == policy.mapped_directories
    assert (
        round_tripped_policy.containers[0].registry_changes
        == policy.containers[0].registry_changes
    )
