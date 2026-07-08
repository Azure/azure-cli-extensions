# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Parity tests for extension metadata produced without wheel 0.30.0.

Builds an extension wheel on the active toolchain, derives an `index.json`
entry via `azdev.operations.extensions.util.get_ext_metadata`, and diffs it against
the published entry in `src/index.json`. Differences are split into:

* schema_gaps    — fields present in the published entry but missing from
                   the candidate. Must be empty.
* acceptable_noise — known, documented differences (e.g. `generator`,
                     `test_requires`). Must match the allowlist below.
* real_bugs      — anything else. Allowed only when the source-tree version
                   is ahead of the latest published version.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
INDEX_PATH = REPO_ROOT / "src" / "index.json"


def _azdev_available() -> bool:
    try:
        return (
            importlib.util.find_spec("azdev.operations.extensions.util") is not None
            and importlib.util.find_spec("azdev.operations.extensions.metadata") is not None
        )
    except ModuleNotFoundError:
        return False


pytestmark = pytest.mark.e2e_packaging


# Kept independently from the prototype so drift between the two is caught.
# In sync with scripts/ci/test_index.py's _METADATA_NOISE_TOP_LEVEL.
ALLOWED_NOISE_TOP_LEVEL = {
    "generator", "metadata_version", "test_requires", "license_file",
    "description_content_type", "project_url",
}
# The whole python.details blob is informational wheel metadata not consumed by
# the extension index; ignore it rather than just document_names.
ALLOWED_NOISE_NESTED = {"extensions/python.details"}


@pytest.fixture(scope="module")
def azdev_metadata_api():
    if not _azdev_available():
        pytest.skip("azdev metadata module is not installed in this environment")

    from azdev.operations.extensions.util import get_ext_metadata

    return {"get_ext_metadata": get_ext_metadata}


def _build_wheel(ext_path: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            str(ext_path),
            "--no-deps",
            "-w",
            str(out_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    wheels = sorted(out_dir.glob("*.whl"))
    if not wheels:
        raise RuntimeError("No wheel was built for {}".format(ext_path))
    return wheels[-1]


def _load_latest_index_entry(extension_name: str):
    with INDEX_PATH.open(encoding="utf-8") as fh:
        index = json.load(fh)
    entries = index["extensions"].get(extension_name)
    if not entries:
        raise KeyError("Extension '{}' not found in src/index.json".format(extension_name))

    from packaging.version import parse as parse_version

    latest = max(entries, key=lambda e: parse_version(e["metadata"]["version"]))
    return latest["metadata"]


class _DiffReport:
    def __init__(self, extension, version):
        self.extension = extension
        self.version = version
        self.acceptable_noise = []
        self.schema_gaps = []
        self.real_bugs = []


def _is_ignored_key(path):
    if path and path[0] in ALLOWED_NOISE_TOP_LEVEL:
        return True
    for key in ALLOWED_NOISE_NESTED:
        if "/".join(path[: len(key.split("/"))]) == key:
            return True
    return False


def _walk_diff(candidate, golden, path, out):
    if isinstance(golden, dict) and isinstance(candidate, dict):
        for key in sorted(set(golden) | set(candidate)):
            _walk_diff(candidate.get(key), golden.get(key), path + (key,), out)
        return
    if candidate != golden:
        out.append(path)


def _path_present(root, parts):
    node = root
    for p in parts:
        if isinstance(node, dict) and p in node:
            node = node[p]
        else:
            return False
    return True


def _classify_diff(candidate, golden):
    report = _DiffReport(
        extension=str(golden.get("name", candidate.get("name", "?"))),
        version=str(golden.get("version", candidate.get("version", "?"))),
    )
    raw_diffs = []
    _walk_diff(candidate, golden, (), raw_diffs)

    for parts in raw_diffs:
        if _is_ignored_key(parts):
            report.acceptable_noise.append("/".join(parts) if parts else "(root)")
            continue

        path_text = "/".join(parts) if parts else "(root)"
        in_golden = _path_present(golden, parts)
        in_candidate = _path_present(candidate, parts)
        if in_golden and not in_candidate:
            # Present in the published index but missing from the candidate.
            report.schema_gaps.append(path_text)
        else:
            # A value mismatch, or a field the candidate adds that the index lacks.
            report.real_bugs.append(path_text)
    return report


def _run_or_skip(azdev_metadata_api, packaging_fixtures, fixture_name):
    fixture = next((f for f in packaging_fixtures if f.name == fixture_name), None)
    if fixture is None:
        pytest.skip("Fixture '{}' not enabled in manifest".format(fixture_name))

    get_ext_metadata = azdev_metadata_api["get_ext_metadata"]
    with tempfile.TemporaryDirectory(prefix="e2e-metadata-") as tmp:
        tmp_path = Path(tmp)
        try:
            wheel_path = _build_wheel(fixture.path, tmp_path / "wheel")
        except subprocess.CalledProcessError as exc:
            pytest.skip(
                "Could not build wheel for '{}': {}\nstdout:\n{}\nstderr:\n{}".format(
                    fixture_name, exc, exc.stdout or "", exc.stderr or ""
                )
            )
        # Anything beyond the build failing (metadata generation, index load,
        # diff classification) is a real regression and must surface as a
        # failure rather than a silent skip.
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir(parents=True, exist_ok=True)
        candidate = get_ext_metadata(str(extract_dir), str(wheel_path), fixture.name)
        golden = _load_latest_index_entry(candidate["name"])
        report = _classify_diff(candidate, golden)
        return candidate, report


@pytest.mark.parametrize("fixture_name", ["ssh"])
def test_candidate_has_no_missing_fields_vs_index(azdev_metadata_api, packaging_fixtures, fixture_name):
    _, report = _run_or_skip(azdev_metadata_api=azdev_metadata_api, packaging_fixtures=packaging_fixtures, fixture_name=fixture_name)
    assert report.schema_gaps == [], (
        "Candidate metadata is missing fields present in src/index.json: {}".format(
            report.schema_gaps
        )
    )


@pytest.mark.parametrize("fixture_name", ["ssh"])
def test_candidate_diff_is_only_allowlisted_noise(azdev_metadata_api, packaging_fixtures, fixture_name):
    _, report = _run_or_skip(azdev_metadata_api=azdev_metadata_api, packaging_fixtures=packaging_fixtures, fixture_name=fixture_name)
    for entry in report.acceptable_noise:
        top = entry.split("/", 1)[0]
        assert (
            top in ALLOWED_NOISE_TOP_LEVEL or entry in ALLOWED_NOISE_NESTED
        ), "Unexpected acceptable_noise key: {}".format(entry)


@pytest.mark.parametrize("fixture_name", ["ssh"])
def test_candidate_divergence_explained_by_version_skew(azdev_metadata_api, packaging_fixtures, fixture_name):
    candidate, report = _run_or_skip(azdev_metadata_api=azdev_metadata_api, packaging_fixtures=packaging_fixtures, fixture_name=fixture_name)
    if not report.real_bugs:
        return

    from packaging.version import parse as parse_version

    golden = _load_latest_index_entry(candidate["name"])
    candidate_v = parse_version(str(candidate["version"]))
    golden_v = parse_version(str(golden["version"]))
    if candidate_v != golden_v:
        return

    details = []
    for key in report.real_bugs:
        sub_c: object = candidate
        sub_g: object = golden
        for p in key.split("/"):
            sub_c = sub_c[p] if isinstance(sub_c, dict) and p in sub_c else None
            sub_g = sub_g[p] if isinstance(sub_g, dict) and p in sub_g else None
        details.append(
            "  {key}:\n    candidate: {c}\n    golden:    {g}".format(
                key=key,
                c=json.dumps(sub_c, sort_keys=True),
                g=json.dumps(sub_g, sort_keys=True),
            )
        )
    pytest.fail(
        "Candidate metadata diverges from src/index.json without version skew "
        "(candidate={cv}, golden={gv}):\n{detail}".format(
            cv=candidate_v, gv=golden_v, detail="\n".join(details)
        )
    )
