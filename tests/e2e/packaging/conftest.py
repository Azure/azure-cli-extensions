# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations

from pathlib import Path

import pytest

from .fixtures import load_fixtures


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


@pytest.fixture(scope="session")
def fixture_manifest(repo_root: Path) -> Path:
    return repo_root / "tests" / "e2e" / "packaging" / "fixtures" / "manifest.json"


@pytest.fixture(scope="session")
def packaging_fixtures(repo_root: Path, fixture_manifest: Path):
    return load_fixtures(repo_root=repo_root, manifest_path=fixture_manifest)


@pytest.fixture
def temp_extension_dir(tmp_path):
    return tmp_path / "azext"
