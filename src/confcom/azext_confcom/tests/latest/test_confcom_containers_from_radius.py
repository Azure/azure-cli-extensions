# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Tests for containers_from_radius and radius_policy_insert commands.

Uses golden sample files from official Radius project samples:
https://github.com/radius-project/samples

Test structure follows test_confcom_containers_from_image.py pattern:
- Each sample directory has app.bicep (input) and aci_container.inc.rego (expected output)
- Tests parameterize over samples and platforms
- DeepDiff compares actual vs expected output
"""

import json
import re
import pytest
import tempfile

from contextlib import redirect_stdout
from io import StringIO
from itertools import product
from pathlib import Path
from deepdiff import DeepDiff

from azext_confcom.command.containers_from_radius import containers_from_radius
from azext_confcom.command.radius_policy_insert import radius_policy_insert


TEST_DIR = Path(__file__).parent
CONFCOM_DIR = TEST_DIR.parent.parent.parent
SAMPLES_ROOT = CONFCOM_DIR / "samples" / "radius"


# =============================================================================
# containers_from_radius golden sample tests
# =============================================================================

def _get_sample_containers(sample_dir: Path) -> list:
    """
    Get list of container indices for a sample based on golden files present.
    
    Files like aci_container.inc.rego -> index 0
    Files like aci_container_1.inc.rego -> index 1
    """
    indices = []
    for f in sample_dir.glob("aci_container*.inc.rego"):
        name = f.stem  # e.g., "aci_container" or "aci_container_1"
        if name == "aci_container":
            indices.append(0)
        elif name.startswith("aci_container_"):
            try:
                idx = int(name.split("_")[-1])
                indices.append(idx)
            except ValueError:
                pass
    return sorted(indices) if indices else [0]


def _get_test_cases():
    """Generate test cases: (sample_dir, platform, container_index)"""
    cases = []
    if not SAMPLES_ROOT.exists():
        return cases
    
    for sample_dir in SAMPLES_ROOT.iterdir():
        if not sample_dir.is_dir():
            continue
        if not (sample_dir / "app.bicep").exists():
            continue
        
        indices = _get_sample_containers(sample_dir)
        for platform in ["aci"]:
            for idx in indices:
                cases.append((sample_dir.name, platform, idx))
    
    return cases


@pytest.mark.parametrize(
    "sample_name, platform, container_index",
    _get_test_cases() or [pytest.param("skip", "aci", 0, marks=pytest.mark.skip(reason="No radius samples found"))],
    ids=lambda x: str(x) if not isinstance(x, tuple) else f"{x[0]}-{x[1]}-c{x[2]}"
)
def test_containers_from_radius(sample_name: str, platform: str, container_index: int):
    """
    Test containers_from_radius against golden output files.
    
    Golden files are generated from official Radius samples with pinned image SHAs.
    """
    if sample_name == "skip":
        pytest.skip("No radius samples found")
    
    sample_dir = SAMPLES_ROOT / sample_name
    template_path = sample_dir / "app.bicep"
    
    # Determine golden file name based on index
    if container_index == 0:
        golden_path = sample_dir / f"{platform}_container.inc.rego"
    else:
        golden_path = sample_dir / f"{platform}_container_{container_index}.inc.rego"
    
    if not golden_path.exists():
        pytest.skip(f"Golden file not found: {golden_path}")
    
    with golden_path.open("r", encoding="utf-8") as f:
        expected = json.load(f)
    
    # Skip placeholder files
    if "TODO" in expected:
        pytest.skip(f"Golden file is placeholder: {golden_path}")
    
    # Run containers_from_radius
    result = containers_from_radius(
        az_cli_command=None,
        template=str(template_path),
        parameters=[],
        container_index=container_index,
        platform=platform,
    )
    
    actual = json.loads(result)
    
    diff = DeepDiff(
        actual,
        expected,
        ignore_order=True,
    )
    assert diff == {}, f"Mismatch for {sample_name}/{platform}/container_{container_index}:\n{diff}"


# =============================================================================
# radius_policy_insert tests
# =============================================================================

class TestRadiusPolicyInsert:
    """Tests for the radius_policy_insert command."""
    
    def test_replaces_first_ccepolicy_in_bicep(self):
        """Should replace the first ccePolicy placeholder with encoded policy."""
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
        policy = "test-policy-base64"
        result = radius_policy_insert(
            az_cli_command=None,
            policy=policy,
            template=template,
            policy_index=0,
        )
        
        assert "'microsoft.containerinstance.virtualnode.ccepolicy': 'test-policy-base64'" in result
    
    def test_replaces_nth_ccepolicy_by_index(self):
        """Should replace the nth ccePolicy when policy_index > 0."""
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
        policy = "replacement"
        result = radius_policy_insert(
            az_cli_command=None,
            policy=policy,
            template=template,
            policy_index=1,
        )
        
        # First should be unchanged, second should be replaced
        assert "'microsoft.containerinstance.virtualnode.ccepolicy': 'first'" in result
        assert "'microsoft.containerinstance.virtualnode.ccepolicy': 'replacement'" in result
        assert "'microsoft.containerinstance.virtualnode.ccepolicy': 'second'" not in result
    
    def test_preserves_quote_style(self):
        """Should preserve single vs double quote style."""
        template_single = "{ 'microsoft.containerinstance.virtualnode.ccepolicy': '' }"
        template_double = '{ "microsoft.containerinstance.virtualnode.ccepolicy": "" }'
        
        result_single = radius_policy_insert(None, "policy", template_single, 0)
        result_double = radius_policy_insert(None, "policy", template_double, 0)
        
        assert "'" in result_single and "'policy'" in result_single
        assert '"' in result_double and '"policy"' in result_double
    
    def test_no_change_when_index_out_of_range(self):
        """Should return unchanged template when index exceeds matches."""
        template = "{ 'microsoft.containerinstance.virtualnode.ccepolicy': '' }"
        result = radius_policy_insert(None, "policy", template, 99)
        assert result == template
    
    def test_handles_ccePolicy_key_variations(self):
        """Should match ccePolicy in different annotation key formats."""
        # Direct ccePolicy key
        template1 = "{ ccePolicy: '' }"
        result1 = radius_policy_insert(None, "p1", template1, 0)
        assert "ccePolicy: 'p1'" in result1
        
        # Full annotation key (case-insensitive)
        template2 = "{ 'Microsoft.ContainerInstance.VirtualNode.CcePolicy': '' }"
        result2 = radius_policy_insert(None, "p2", template2, 0)
        assert "'p2'" in result2


# =============================================================================
# containers_from_radius edge case tests
# =============================================================================

class TestContainersFromRadiusEdgeCases:
    """Edge case tests for containers_from_radius."""
    
    def test_index_out_of_range_raises_error(self):
        """Should raise IndexError when container_index exceeds available containers."""
        # Create a minimal bicep with one container
        template_content = """
extension radius

resource c 'Applications.Core/containers@2023-10-01-preview' = {
  name: 'test'
  properties: {
    container: {
      image: 'alpine:latest'
    }
  }
}
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bicep', delete=False) as f:
            f.write(template_content)
            f.flush()
            
            with pytest.raises(IndexError, match="out of range"):
                containers_from_radius(
                    az_cli_command=None,
                    template=f.name,
                    parameters=[],
                    container_index=99,
                    platform="aci",
                )
    
    def test_ignores_non_container_resources(self):
        """Should only extract from Applications.Core/containers resources."""
        template_content = """
extension radius

resource app 'Applications.Core/applications@2023-10-01-preview' = {
  name: 'myapp'
}

resource container 'Applications.Core/containers@2023-10-01-preview' = {
  name: 'mycontainer'
  properties: {
    container: {
      image: 'alpine:latest'
    }
  }
}
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bicep', delete=False) as f:
            f.write(template_content)
            f.flush()
            
            # Should find exactly 1 container (not the application)
            result = containers_from_radius(
                az_cli_command=None,
                template=f.name,
                parameters=[],
                container_index=0,
                platform="aci",
            )
            
            parsed = json.loads(result)
            assert "alpine" in parsed.get("id", "")
            
            # Index 1 should fail
            with pytest.raises(IndexError):
                containers_from_radius(
                    az_cli_command=None,
                    template=f.name,
                    parameters=[],
                    container_index=1,
                    platform="aci",
                )
