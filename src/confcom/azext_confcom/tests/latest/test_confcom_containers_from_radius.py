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
import subprocess
import tempfile

from contextlib import redirect_stdout
from io import StringIO
from itertools import product
from pathlib import Path
from deepdiff import DeepDiff

from azext_confcom.command.containers_from_radius import containers_from_radius
from azext_confcom.command.radius_policy_insert import radius_policy_insert
from azext_confcom.lib.deployments import EVAL_FUNCS


TEST_DIR = Path(__file__).parent
CONFCOM_DIR = TEST_DIR.parent.parent.parent
SAMPLES_ROOT = CONFCOM_DIR / "samples" / "radius"


def _parse_deployment_template_via_bicep(_az_cli_command, template, parameters):
    """Compile a bicep file to ARM JSON using the bicep CLI.

    This avoids the need for a live Azure CLI context in tests.
    """
    result = subprocess.run(
        ["bicep", "build", template, "--stdout"],
        capture_output=True, text=True, check=True,
    )
    arm = json.loads(result.stdout)
    for eval_func in EVAL_FUNCS:
        arm = eval_func(arm, {})
    return arm


@pytest.fixture(autouse=True)
def _patch_parse_deployment_template():
    """Use bicep CLI instead of Azure CLI for template parsing in tests.

    Patches through __globals__ to handle module reloads performed by the
    session-scoped wheel-building conftest.
    """
    fn = containers_from_radius
    original = fn.__globals__.get("parse_deployment_template")
    fn.__globals__["parse_deployment_template"] = _parse_deployment_template_via_bicep
    yield
    if original is not None:
        fn.__globals__["parse_deployment_template"] = original


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
        # Strip both .inc.rego suffixes to get the base name
        name = f.name.split(".")[0]  # e.g., "aci_container" or "aci_container_1"
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


# =============================================================================
# _map_* function unit tests
# =============================================================================

from azext_confcom.command.containers_from_radius import (
    _map_command,
    _map_working_dir,
    _map_env_rules,
    _map_connection_env_rules,
    _map_volume_mounts,
    _map_exec_processes,
)


class TestMapCommand:
    """Unit tests for _map_command."""

    def test_no_overrides_returns_none(self):
        assert _map_command({}, ["/bin/sh"]) is None

    def test_command_replaces_image_entrypoint(self):
        result = _map_command({"command": ["/app/run"]}, ["/bin/sh"])
        assert result == ["/app/run"]

    def test_command_with_args(self):
        result = _map_command({"command": ["/app/run"], "args": ["--verbose"]}, ["/bin/sh"])
        assert result == ["/app/run", "--verbose"]

    def test_args_only_appends_to_image(self):
        result = _map_command({"args": ["--debug"]}, ["/bin/sh", "-c"])
        assert result == ["/bin/sh", "-c", "--debug"]

    def test_args_only_with_empty_image_command(self):
        result = _map_command({"args": ["start"]}, [])
        assert result == ["start"]

    def test_empty_command_is_not_none(self):
        """An explicit empty command list is a valid override."""
        result = _map_command({"command": []}, ["/bin/sh"])
        assert result == []


class TestMapWorkingDir:
    """Unit tests for _map_working_dir."""

    def test_returns_none_when_absent(self):
        assert _map_working_dir({}) is None

    def test_returns_value(self):
        assert _map_working_dir({"workingDir": "/app"}) == "/app"

    def test_empty_string_returns_none(self):
        assert _map_working_dir({"workingDir": ""}) is None


class TestMapEnvRules:
    """Unit tests for _map_env_rules."""

    def test_empty_env(self):
        assert _map_env_rules({}) == []

    def test_plain_value(self):
        result = _map_env_rules({"env": {"MY_VAR": {"value": "hello"}}})
        assert result == [{"pattern": "MY_VAR=hello", "strategy": "string", "required": False}]

    def test_value_from_secret(self):
        result = _map_env_rules({"env": {"SECRET": {"valueFrom": {"secretRef": {}}}}})
        assert result == [{"pattern": "SECRET=.+", "strategy": "re2", "required": False}]

    def test_mixed_values(self):
        result = _map_env_rules({"env": {
            "A": {"value": "1"},
            "B": {"valueFrom": {"secretRef": {}}},
        }})
        assert len(result) == 2
        patterns = {r["pattern"] for r in result}
        assert "A=1" in patterns
        assert "B=.+" in patterns

    def test_kubernetes_list_format(self):
        """Sidecar containers use Kubernetes [{name, value}] format."""
        result = _map_env_rules({"env": [
            {"name": "FOO", "value": "bar"},
            {"name": "BAZ", "value": "qux"},
        ]})
        assert len(result) == 2
        patterns = {r["pattern"] for r in result}
        assert "FOO=bar" in patterns
        assert "BAZ=qux" in patterns

    def test_kubernetes_list_with_value_from(self):
        result = _map_env_rules({"env": [
            {"name": "SECRET", "valueFrom": {"secretKeyRef": {"name": "s", "key": "k"}}},
        ]})
        assert result == [{"pattern": "SECRET=.+", "strategy": "re2", "required": False}]


class TestMapConnectionEnvRules:
    """Unit tests for _map_connection_env_rules."""

    def test_no_connections(self):
        assert _map_connection_env_rules({}) == []

    def test_single_connection(self):
        result = _map_connection_env_rules({"connections": {"db": {"source": "x"}}})
        assert result == [{
            "pattern": "CONNECTIONS_DB_.+=.+", "strategy": "re2", "required": True,
        }]

    def test_multiple_connections(self):
        result = _map_connection_env_rules({"connections": {
            "redis": {"source": "a"},
            "sql": {"source": "b"},
        }})
        names = {r["pattern"].split("_")[1] for r in result}
        assert names == {"REDIS", "SQL"}

    def test_disable_default_env_vars(self):
        """Connections with disableDefaultEnvVars should be skipped."""
        result = _map_connection_env_rules({"connections": {
            "db": {"source": "a"},
            "metrics": {"source": "b", "disableDefaultEnvVars": True},
        }})
        assert len(result) == 1
        assert "DB" in result[0]["pattern"]

    def test_all_disabled(self):
        result = _map_connection_env_rules({"connections": {
            "a": {"source": "x", "disableDefaultEnvVars": True},
        }})
        assert result == []


class TestMapVolumeMounts:
    """Unit tests for _map_volume_mounts."""

    def test_no_volumes(self):
        assert _map_volume_mounts({}) == []

    def test_ephemeral_volume_is_writable(self):
        """Ephemeral volumes should be writable by default."""
        result = _map_volume_mounts({"volumes": {
            "tmp": {"kind": "ephemeral", "mountPath": "/tmp", "managedStore": "memory"},
        }})
        assert len(result) == 1
        assert "ro" not in result[0]["options"]
        assert result[0]["destination"] == "/tmp"
        assert result[0]["source"] == "ephemeral://tmp"

    def test_persistent_volume_default_readonly(self):
        """Persistent volumes default to read-only per the Radius spec."""
        result = _map_volume_mounts({"volumes": {
            "data": {"kind": "persistent", "mountPath": "/data", "source": "vol.id"},
        }})
        assert "ro" in result[0]["options"]
        assert result[0]["source"] == "vol.id"

    def test_persistent_volume_with_permission_write(self):
        """API reference uses 'permission' field."""
        result = _map_volume_mounts({"volumes": {
            "data": {"kind": "persistent", "mountPath": "/data", "source": "v", "permission": "write"},
        }})
        assert "ro" not in result[0]["options"]

    def test_persistent_volume_with_rbac_write(self):
        """Human-readable docs use 'rbac' field."""
        result = _map_volume_mounts({"volumes": {
            "data": {"kind": "persistent", "mountPath": "/data", "source": "v", "rbac": "write"},
        }})
        assert "ro" not in result[0]["options"]

    def test_persistent_volume_permission_read(self):
        result = _map_volume_mounts({"volumes": {
            "cfg": {"kind": "persistent", "mountPath": "/cfg", "source": "v", "permission": "read"},
        }})
        assert "ro" in result[0]["options"]

    def test_ephemeral_explicit_read(self):
        """Ephemeral volume can be explicitly set to read-only."""
        result = _map_volume_mounts({"volumes": {
            "ro_tmp": {"kind": "ephemeral", "mountPath": "/ro", "managedStore": "disk", "permission": "read"},
        }})
        assert "ro" in result[0]["options"]

    def test_multiple_volumes(self):
        result = _map_volume_mounts({"volumes": {
            "a": {"kind": "ephemeral", "mountPath": "/a", "managedStore": "memory"},
            "b": {"kind": "persistent", "mountPath": "/b", "source": "vol"},
        }})
        assert len(result) == 2


class TestMapExecProcesses:
    """Unit tests for _map_exec_processes."""

    def test_no_probes(self):
        assert _map_exec_processes({}) == []

    def test_exec_liveness_probe(self):
        result = _map_exec_processes({"livenessProbe": {"kind": "exec", "command": "ls"}})
        assert result == [{"command": ["ls"], "signals": []}]

    def test_exec_readiness_probe(self):
        result = _map_exec_processes({"readinessProbe": {"kind": "exec", "command": ["cat", "/tmp/ready"]}})
        assert result == [{"command": ["cat", "/tmp/ready"], "signals": []}]

    def test_both_probes(self):
        result = _map_exec_processes({
            "livenessProbe": {"kind": "exec", "command": "live"},
            "readinessProbe": {"kind": "exec", "command": "ready"},
        })
        assert len(result) == 2

    def test_httpget_probe_ignored(self):
        """Only exec probes generate exec_processes."""
        result = _map_exec_processes({
            "livenessProbe": {"kind": "httpGet", "containerPort": 8080, "path": "/health"},
        })
        assert result == []

    def test_tcp_probe_ignored(self):
        result = _map_exec_processes({
            "readinessProbe": {"kind": "tcp", "containerPort": 3000},
        })
        assert result == []

    def test_exec_probe_without_command_ignored(self):
        result = _map_exec_processes({"livenessProbe": {"kind": "exec"}})
        assert result == []
