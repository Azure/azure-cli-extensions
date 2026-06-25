# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Command-level tests for containers_from_radius.

Uses golden sample files from samples/radius/:
- Each sample directory has app.bicep (input) and aci_container*.inc.rego (expected output)
- Tests parameterize over samples and container indices
- DeepDiff compares actual vs expected output
"""

import json
import pytest
import subprocess
import tempfile

from pathlib import Path
from deepdiff import DeepDiff

from azext_confcom.command.containers_from_radius import containers_from_radius
from azext_confcom.lib.templates import EVAL_FUNCS


TEST_DIR = Path(__file__).parent
CONFCOM_DIR = TEST_DIR.parent.parent.parent
SAMPLES_ROOT = CONFCOM_DIR / "samples" / "radius"


def _parse_deployment_template_via_bicep(_az_cli_command, template, parameters):
    """Compile a bicep file to ARM JSON using the bicep CLI."""
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
    """Use bicep CLI instead of Azure CLI for template parsing in tests."""
    fn = containers_from_radius
    original = fn.__globals__.get("parse_deployment_template")
    fn.__globals__["parse_deployment_template"] = _parse_deployment_template_via_bicep
    yield
    if original is not None:
        fn.__globals__["parse_deployment_template"] = original


# ---------------------------------------------------------------------------
# Golden sample tests
# ---------------------------------------------------------------------------

def _get_sample_containers(sample_dir: Path) -> list:
    """Get container indices for a sample based on golden files present."""
    indices = []
    for f in sample_dir.glob("aci_container*.inc.rego"):
        name = f.name.split(".")[0]
        if name == "aci_container":
            indices.append(0)
        elif name.startswith("aci_container_"):
            try:
                indices.append(int(name.split("_")[-1]))
            except ValueError:
                pass
    return sorted(indices) if indices else [0]


def _get_test_cases():
    """Generate test cases: (sample_name, platform, container_index)."""
    cases = []
    if not SAMPLES_ROOT.exists():
        return cases
    for sample_dir in SAMPLES_ROOT.iterdir():
        if not sample_dir.is_dir() or not (sample_dir / "app.bicep").exists():
            continue
        for idx in _get_sample_containers(sample_dir):
            cases.append((sample_dir.name, "aci", idx))
    return cases


@pytest.mark.parametrize(
    "sample_name, platform, container_index",
    _get_test_cases() or [pytest.param("skip", "aci", 0, marks=pytest.mark.skip(reason="No radius samples found"))],
    ids=lambda x: str(x) if not isinstance(x, tuple) else f"{x[0]}-{x[1]}-c{x[2]}",
)
def test_golden_sample(sample_name, platform, container_index):
    """Test containers_from_radius against golden output files."""
    if sample_name == "skip":
        pytest.skip("No radius samples found")

    sample_dir = SAMPLES_ROOT / sample_name
    template_path = sample_dir / "app.bicep"

    if container_index == 0:
        golden_path = sample_dir / f"{platform}_container.inc.rego"
    else:
        golden_path = sample_dir / f"{platform}_container_{container_index}.inc.rego"

    if not golden_path.exists():
        pytest.skip(f"Golden file not found: {golden_path}")

    with golden_path.open("r", encoding="utf-8") as f:
        expected = json.load(f)

    if "TODO" in expected:
        pytest.skip(f"Golden file is placeholder: {golden_path}")

    result = containers_from_radius(
        az_cli_command=None,
        template=str(template_path),
        parameters=[],
        container_index=container_index,
        platform=platform,
    )
    actual = json.loads(result)

    diff = DeepDiff(actual, expected, ignore_order=True)
    assert diff == {}, f"Mismatch for {sample_name}/{platform}/container_{container_index}:\n{diff}"


def test_index_out_of_range_raises_error():
    """Should raise IndexError when container_index exceeds available containers."""
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


def test_ignores_non_container_resources():
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

        result = containers_from_radius(
            az_cli_command=None,
            template=f.name,
            parameters=[],
            container_index=0,
            platform="aci",
        )
        parsed = json.loads(result)
        assert "alpine" in parsed.get("id", "")

        with pytest.raises(IndexError):
            containers_from_radius(
                az_cli_command=None,
                template=f.name,
                parameters=[],
                container_index=1,
                platform="aci",
            )
