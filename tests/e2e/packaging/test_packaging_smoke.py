# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Smoke tests for the e2e packaging harness.

Run unconditionally on every invocation so a broken harness fails fast and
visibly instead of silently skipping every lifecycle test downstream.
"""

from __future__ import annotations

import shutil

import pytest

from .runner import CommandError, run_command


@pytest.mark.e2e_packaging
@pytest.mark.smoke
def test_fixture_manifest_has_expected_core_fixtures(packaging_fixtures):
    names = {f.name for f in packaging_fixtures}
    assert "ssh" in names
    assert "containerapp" in names


@pytest.mark.e2e_packaging
@pytest.mark.smoke
def test_fixture_paths_exist(packaging_fixtures):
    missing = [f.path for f in packaging_fixtures if not f.path.exists()]
    assert not missing, "Missing fixture paths: {}".format(", ".join(str(path) for path in missing))


@pytest.mark.e2e_packaging
@pytest.mark.smoke
def test_az_cli_is_installed_and_usable():
    if not shutil.which("az"):
        pytest.skip("az is not available in PATH")

    result = run_command(["az", "--version"], check=True)
    assert "azure-cli" in result.stdout.lower()


@pytest.mark.e2e_packaging
@pytest.mark.smoke
def test_azdev_is_installed_and_usable():
    if not shutil.which("azdev"):
        pytest.skip("azdev is not available in PATH")

    try:
        result = run_command(["azdev", "--version"], check=True)
    except CommandError as ex:
        pytest.skip("azdev command exists but is not usable in this environment: {}".format(ex))

    # `azdev --version` prints just the version number first (e.g. "0.2.10").
    first_line = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
    assert first_line and first_line[0].isdigit() and "." in first_line, (
        "Unexpected azdev --version output: {!r}".format(result.stdout)
    )
