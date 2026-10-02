# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""End-to-end packaging lifecycle tests.

Exercises the full build + install + remove flow for selected extension
fixtures, on both the `pip` / `az` and `azdev` surfaces, against whatever
wheel and setuptools versions are installed in the active env.
"""

from __future__ import annotations

import json
import importlib.util
import shutil
import sys
import zipfile
from email.parser import BytesParser
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from .fixtures import PackagingFixture
from .runner import CommandError, run_command


def _get_fixture(packaging_fixtures, name: str) -> PackagingFixture:
    for fixture in packaging_fixtures:
        if fixture.name == name:
            return fixture
    raise AssertionError("Fixture '{}' was not found in packaging manifest".format(name))


@lru_cache(maxsize=1)
def _ensure_wheel_available() -> None:
    run_command([sys.executable, "-m", "pip", "install", "wheel"])


def _build_wheel(ext_path: Path, wheel_dir: Path, no_build_isolation: bool = False, check: bool = True):
    _ensure_wheel_available()

    wheel_dir.mkdir(parents=True, exist_ok=True)

    # Copy the fixture into the test tmp dir so the build cannot mutate the
    # source tree or hit file locks left by an editable install of the same
    # extension in the active env.
    source_copy = wheel_dir.parent / ("src_" + ext_path.name)
    if source_copy.exists():
        shutil.rmtree(source_copy, ignore_errors=True)
    shutil.copytree(
        ext_path,
        source_copy,
        ignore=shutil.ignore_patterns("build", "dist", "*.egg-info", "__pycache__"),
    )

    # --no-cache-dir bypasses pip's user-scoped wheel cache so each run
    # exercises a real build. --use-pep517 forces the PEP 517 build interface
    # so older pip defaults do not fall back to legacy `setup.py bdist_wheel`,
    # which would bypass build isolation.
    command = [
        sys.executable,
        "-m",
        "pip",
        "wheel",
        str(source_copy),
        "--no-deps",
        "--no-cache-dir",
        "--use-pep517",
        "-w",
        str(wheel_dir),
    ]
    if no_build_isolation:
        command.insert(5, "--no-build-isolation")

    result = run_command(command, check=check)
    wheels = sorted(wheel_dir.glob("*.whl"))
    return result, wheels


def _has_azure_cli_core() -> bool:
    try:
        return importlib.util.find_spec("azure.cli.core") is not None
    except ModuleNotFoundError:
        return False


def _read_ml_wheel_metadata(wheel_path):
    with zipfile.ZipFile(wheel_path) as wheel:
        metadata_files = [name for name in wheel.namelist() if name.endswith(".dist-info/METADATA")]
        assert len(metadata_files) == 1
        package_metadata = BytesParser().parsebytes(wheel.read(metadata_files[0]))
        extension_metadata = json.loads(wheel.read("azext_mlv2/azext_metadata.json"))
    return package_metadata, extension_metadata


@pytest.fixture(scope="module")
def ml_metadata_wheel(packaging_fixtures, tmp_path_factory):
    fixture = _get_fixture(packaging_fixtures, "machinelearningservices")
    source_metadata = fixture.path / "azext_mlv2" / "azext_metadata.json"
    wheel_dir = tmp_path_factory.mktemp("ml-metadata") / "wheels"
    _, wheels = _build_wheel(
        fixture.path, wheel_dir, no_build_isolation=fixture.requires_build_isolation_off
    )
    assert len(wheels) == 1
    source_copy = wheel_dir.parent / ("src_" + fixture.path.name)
    assert (source_copy / "azext_mlv2" / "azext_metadata.json").read_bytes() == source_metadata.read_bytes()
    return wheels[0]


@pytest.fixture(scope="module")
def ml_metadata_install(ml_metadata_wheel, tmp_path_factory):
    if not _has_azure_cli_core():
        pytest.skip("azure.cli.core is not available in this environment")

    root = tmp_path_factory.mktemp("ml-metadata-install")
    extension_dir = root / "extensions"
    installed_dir = extension_dir / "ml"
    run_command([
        sys.executable, "-m", "pip", "install", "--target",
        str(installed_dir), str(ml_metadata_wheel),
    ])
    return installed_dir, {
        "AZURE_CONFIG_DIR": str(root / "config"),
        "AZURE_EXTENSION_DIR": str(extension_dir),
        "AZURE_EXTENSION_SYS_DIR": str(root / "system-extensions"),
        "AZURE_EXTENSION_DEV_SOURCES": "",
        "AZURE_EXTENSION_USE_DYNAMIC_INSTALL": "no",
        "AZURE_CORE_COLLECT_TELEMETRY": "no",
    }


@pytest.mark.e2e_packaging
def test_ml_metadata_matches_package_identity(ml_metadata_wheel):
    package_metadata, extension_metadata = _read_ml_wheel_metadata(ml_metadata_wheel)
    assert package_metadata["Name"] == "ml"
    assert package_metadata["Version"]
    assert extension_metadata["name"] == package_metadata["Name"]
    assert extension_metadata["version"] == package_metadata["Version"]
    assert "azext.minCliCoreVersion" in extension_metadata


@pytest.mark.e2e_packaging
def test_ml_metadata_supports_legacy_reader(ml_metadata_wheel, ml_metadata_install):
    from azure.cli.core.extension import WheelExtension

    package_metadata, _ = _read_ml_wheel_metadata(ml_metadata_wheel)
    installed_dir, _ = ml_metadata_install
    # pkginfo 1.8.2 leaves name/version unset for Metadata-Version: 2.4.
    unreadable_metadata = SimpleNamespace(name=None, version=None)
    with patch("azure.cli.core.extension.pkginfo.Wheel", return_value=unreadable_metadata):
        extension = WheelExtension("ml", str(installed_dir))
        assert extension.version == package_metadata["Version"]
        assert extension.metadata["name"] == "ml"


@pytest.mark.e2e_packaging
@pytest.mark.parametrize(
    "arguments,version_path",
    [
        (["extension", "show", "--name", "ml"], ["version"]),
        (["version"], ["extensions", "ml"]),
    ],
)
def test_ml_metadata_cli_reports_version(ml_metadata_wheel, ml_metadata_install, arguments, version_path):
    package_metadata, _ = _read_ml_wheel_metadata(ml_metadata_wheel)
    _, env = ml_metadata_install
    result = run_command(
        [sys.executable, "-m", "azure.cli", *arguments, "--output", "json"], env=env
    )
    value = json.loads(result.stdout)
    for key in version_path:
        value = value[key]
    assert value == package_metadata["Version"]


@pytest.mark.e2e_packaging
def test_ml_metadata_refreshes_on_incremental_build(ml_metadata_wheel, tmp_path):
    source_copy = ml_metadata_wheel.parent.parent / "src_machinelearningservices"
    run_command(
        [
            sys.executable, "setup.py", "egg_info", "--tag-build", ".dev1",
            "bdist_wheel", "--dist-dir", str(tmp_path),
        ],
        cwd=source_copy,
    )
    wheels = list(tmp_path.glob("*.whl"))
    assert len(wheels) == 1
    package_metadata, extension_metadata = _read_ml_wheel_metadata(wheels[0])
    assert package_metadata["Version"].endswith(".dev1")
    assert extension_metadata["version"] == package_metadata["Version"]


# Stderr fragments azdev emits when no extension repo is configured.
_AZDEV_NOT_CONFIGURED_PATTERNS = (
    "please run `azdev setup`",
    "extension repo path is empty",
    "unable to retrieve extensions repo path",
)


def _is_azdev_not_configured(ex: CommandError) -> bool:
    stderr = (ex.result.stderr or "").lower()
    return any(p in stderr for p in _AZDEV_NOT_CONFIGURED_PATTERNS)


def _azdev_setup_skip_message() -> str:
    repo = Path(__file__).resolve().parents[3]
    return (
        "azdev is installed but no extension repo is configured. "
        "Run: azdev setup -r \"{}\"".format(repo)
    )


def _require_azdev_ready_or_skip() -> None:
    if not shutil.which("azdev"):
        pytest.skip("azdev is not available in PATH")

    try:
        run_command(["azdev", "--version"], check=True)
    except CommandError as ex:
        pytest.skip("azdev command exists but is not usable in this environment: {}".format(ex))

    # `azdev extension list` does not require the extensions-repo config, so
    # use a command that does: a dry-run `extension add` against a synthetic
    # name. The repo-path check fires before the extension lookup, so an
    # unconfigured azdev exits with a recognizable message regardless of
    # whether the probe name exists.
    probe = run_command(
        ["azdev", "extension", "add", "__azdev_setup_probe__"], check=False
    )
    if probe.returncode != 0:
        stderr = (probe.stderr or "").lower()
        if any(p in stderr for p in _AZDEV_NOT_CONFIGURED_PATTERNS):
            pytest.skip(_azdev_setup_skip_message())

    # Confirm extension list itself works (catches azdev installs that pass
    # --version but choke later).
    try:
        run_command(["azdev", "extension", "list"], check=True)
    except CommandError as ex:
        if _is_azdev_not_configured(ex):
            pytest.skip(_azdev_setup_skip_message())
        pytest.skip(
            "azdev is not usable for extension operations in this environment: {}".format(ex)
        )


@pytest.mark.e2e_packaging
@pytest.mark.smoke
def test_extension_wheel_builds_without_wheel_pin(packaging_fixtures, tmp_path):
    """Build the ssh extension via `pip wheel --use-pep517` on the active toolchain."""
    ssh_fixture = _get_fixture(packaging_fixtures, "ssh")
    _, wheels = _build_wheel(ssh_fixture.path, tmp_path / "wheelhouse")
    assert wheels, "No wheel produced for '{}'".format(ssh_fixture.path)
    wheel_path = wheels[-1] # get the latest wheel
    assert wheel_path.name.endswith(".whl")
    assert "ssh" in wheel_path.name.lower()


@pytest.mark.e2e_packaging
@pytest.mark.slow
def test_az_extension_lifecycle_add_show_list_remove(packaging_fixtures, tmp_path, temp_extension_dir):
    """Add a built wheel via `az extension add`, verify it, then remove it."""
    if not shutil.which("az"):
        pytest.skip("az is not available in PATH")

    ssh_fixture = _get_fixture(packaging_fixtures, "ssh")
    _, wheels = _build_wheel(ssh_fixture.path, tmp_path / "wheelhouse")
    assert wheels, "No wheel produced for '{}'".format(ssh_fixture.path)
    wheel_path = wheels[-1]

    temp_extension_dir.mkdir(parents=True, exist_ok=True)
    env = {"AZURE_EXTENSION_DIR": str(temp_extension_dir)}
    installed_dir = temp_extension_dir / "ssh"

    run_command(["az", "extension", "add", "--source", str(wheel_path), "--yes"], env=env)

    # Assert on AZURE_EXTENSION_DIR contents rather than `az extension list`:
    # an `azdev setup -r <repo>` editable install of any extension leaks into
    # `az extension list` regardless of AZURE_EXTENSION_DIR.
    assert installed_dir.exists(), (
        "Expected `az extension add` to create {} but it does not exist".format(installed_dir)
    )

    show_result = run_command(
        ["az", "extension", "show", "--name", "ssh", "--output", "json"], env=env
    )
    show_payload = json.loads(show_result.stdout)
    assert show_payload.get("name") == "ssh"

    run_command(["az", "extension", "remove", "--name", "ssh"], env=env)

    assert not installed_dir.exists(), (
        "Expected `az extension remove` to delete {} but it still exists".format(installed_dir)
    )


@pytest.mark.e2e_packaging
@pytest.mark.slow
def test_self_importing_setup_py_fails_under_default_build_isolation(packaging_fixtures, tmp_path):
    """`containerapp/setup.py` self-imports before the wheel is built, so it
    must fail under default build isolation with a ModuleNotFoundError.
    """
    containerapp_fixture = _get_fixture(packaging_fixtures, "containerapp")
    result, _ = _build_wheel(
        containerapp_fixture.path,
        tmp_path / "wheelhouse-default-isolation",
        no_build_isolation=False,
        check=False,
    )

    assert result.returncode != 0, "Expected containerapp build to fail with default isolation"
    combined_output = (result.stdout + "\n" + result.stderr).lower()
    assert "azext_containerapp" in combined_output or "modulenotfounderror" in combined_output


@pytest.mark.e2e_packaging
@pytest.mark.slow
def test_self_importing_setup_py_builds_with_no_build_isolation_workaround(packaging_fixtures, tmp_path):
    """Same fixture as the previous test, but with `--no-build-isolation` it builds."""
    if not _has_azure_cli_core():
        pytest.skip("azure.cli.core is not available in this environment")

    containerapp_fixture = _get_fixture(packaging_fixtures, "containerapp")
    _, wheels = _build_wheel(
        containerapp_fixture.path,
        tmp_path / "wheelhouse-no-build-isolation",
        no_build_isolation=True,
        check=True,
    )

    assert wheels, "Expected containerapp wheel to be produced with --no-build-isolation"


@pytest.mark.e2e_packaging
@pytest.mark.slow
def test_azdev_extension_lifecycle_add_show_list_remove(packaging_fixtures, temp_extension_dir):
    """Add, show, list and remove an extension via `azdev extension ...`."""
    _require_azdev_ready_or_skip()

    temp_extension_dir.mkdir(parents=True, exist_ok=True)
    env = {"AZURE_EXTENSION_DIR": str(temp_extension_dir)}

    ssh_fixture = _get_fixture(packaging_fixtures, "ssh")

    def _azdev_install_state(name: str) -> str:
        result = run_command(["azdev", "extension", "list", "-o", "json"], env=env)
        entries = json.loads(result.stdout)
        match = next((e for e in entries if e.get("name") == name), None)
        assert match is not None, "Extension '{}' not found in azdev extension list".format(name)
        return match.get("install") or ""

    # Ensure clean state before this test starts.
    run_command(["azdev", "extension", "remove", ssh_fixture.name], env=env, check=False)

    run_command(["azdev", "extension", "add", ssh_fixture.name], env=env)

    show_result = run_command(["azdev", "extension", "show", "--mod-name", ssh_fixture.name], env=env)
    assert ssh_fixture.name in (show_result.stdout + show_result.stderr).lower()

    assert _azdev_install_state(ssh_fixture.name), (
        "Expected '{}' to be installed after `azdev extension add`".format(ssh_fixture.name)
    )

    run_command(["azdev", "extension", "remove", ssh_fixture.name], env=env)

    assert not _azdev_install_state(ssh_fixture.name), (
        "Expected '{}' to be uninstalled after `azdev extension remove`".format(ssh_fixture.name)
    )


@pytest.mark.e2e_packaging
@pytest.mark.slow
def test_azdev_extension_build_produces_wheel(packaging_fixtures, tmp_path):
    """Build an extension wheel via `azdev extension build`.

    Exercises azdev's own build path (decoupled from `wheel==0.30.0`), as
    opposed to the direct `pip wheel` build covered elsewhere.
    """
    _require_azdev_ready_or_skip()

    ssh_fixture = _get_fixture(packaging_fixtures, "ssh")
    dist_dir = tmp_path / "azdev-dist"

    run_command(["azdev", "extension", "build", ssh_fixture.name, "--dist-dir", str(dist_dir)])

    wheels = sorted(dist_dir.glob("*.whl"))
    assert wheels, "Expected `azdev extension build` to produce a wheel in {}".format(dist_dir)
    assert any("ssh" in wheel.name.lower() for wheel in wheels), (
        "Expected an ssh wheel from `azdev extension build`, found: {}".format(
            [wheel.name for wheel in wheels]
        )
    )
