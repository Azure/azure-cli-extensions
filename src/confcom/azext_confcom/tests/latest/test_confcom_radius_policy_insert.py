# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Command-level tests for insert_policy_into_template.

Tests the core regex replacement that inserts base64-encoded policy strings
into bicep template ccePolicy annotation values.
"""

from azext_confcom.command.radius_policy_insert import insert_policy_into_template


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
