# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from datetime import datetime, timezone

# pylint: disable=import-error,no-name-in-module
import requests
from azure.cli.core.azclierror import (
    CLIError,
    FileOperationError,
    InvalidArgumentValueError,
    ValidationError,
)

from ._local import dependencies_root, managed_subdir, bundle_install_root, dependency_environment, INSTALLABLE_KINDS

# INSTALLABLE_KINDS is defined in _local and re-exported here, which is where callers
# expect it. Keeping one definition is what stops 'dependency check' reporting a kind as
# uninstallable while 'dependency install' happily installs it.
#
# The .NET SDK stays report-only: its only vendor-supported install route is a remote
# script, and azure-cli has no precedent for running one on a user's machine. Azurite
# was originally excluded for a similar reason, but that reasoning came from VS Code,
# where the Azurite extension supplies it. A CLI user has no such extension, and local
# runs need a storage emulator, so refusing left them with nothing to fall back on.

_REFUSALS = {
    "dotnet": (
        "The .NET SDK is not installed by this CLI. Its only vendor-supported install route is the "
        "remote script at https://dot.net/v1/dotnet-install.sh (.ps1 on Windows), and running a remote "
        "script is outside what this command will do. Install it from https://dotnet.microsoft.com/download, "
        "or let Visual Studio Code's Azure Logic Apps extension install it, then re-run "
        "'az logicapp dependency check'."
    ),
}

# Used when the upstream version feed cannot be reached. Matching the versions the
# VS Code extension pins keeps a shared dependency folder on one version.
PINNED_VERSIONS = {
    "core-tools": "4.0.7030",
    "node": "24.15.0",
    "azurite": "3.35.0",
}

BUNDLE_ID = "Microsoft.Azure.Functions.ExtensionBundle.Workflows"
BUNDLE_BASE_URL = "https://cdn.functions.azure.com/public"
CORE_TOOLS_RELEASES_API = "https://api.github.com/repos/Azure/azure-functions-core-tools/releases/latest"
NODE_DIST_INDEX = "https://nodejs.org/dist/index.json"
NPM_REGISTRY = "https://registry.npmjs.org/"

# Azurite declares engines.node >= 22. npm honours that only as a warning, so without
# this check an install would "succeed" and then fail the first time Azurite is run.
AZURITE_MIN_NODE_MAJOR = 22

MANIFEST_NAME = ".logicapps-integrity.json"

_METADATA_TIMEOUT = 30
_DOWNLOAD_TIMEOUT = 300
_NPM_TIMEOUT = 900
_CHUNK = 1024 * 256


def _os_tag(kind):
    """Platform token used in each publisher's download URLs.

    Node.js publishes macOS builds as 'darwin'; Functions Core Tools publishes the
    same platform as 'osx'. They are not interchangeable.
    """
    system = platform.system().lower()
    if system == "windows":
        return "win"
    if system == "darwin":
        return "darwin" if kind == "node" else "osx"
    if system == "linux":
        return "linux"
    raise ValidationError("Unsupported operating system for dependency install: {}".format(platform.system()))


def _arch_tag():
    machine = platform.machine().lower()
    if machine in ("amd64", "x86_64", "x64"):
        return "x64"
    if machine in ("arm64", "aarch64"):
        return "arm64"
    raise ValidationError(
        "Unsupported CPU architecture for dependency install: {}. "
        "Only x64 and arm64 builds are published.".format(platform.machine())
    )


def _get_json(url, token=None):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "token {}".format(token)
    response = requests.get(url, headers=headers, timeout=_METADATA_TIMEOUT)
    response.raise_for_status()
    return response.json()


def resolve_version(kind, version=None, gh_token=None):
    """Return (version, source) where source records how the version was chosen.

    An explicit --version always wins. Otherwise the publisher's feed is asked, and
    a pinned fallback is used when it cannot be reached -- GitHub rate limits are
    common enough on shared CI addresses that failing the install would be worse.
    """
    if version:
        return version, "explicit"

    if kind == "bundle":
        try:
            index = _get_json("{}/ExtensionBundles/{}/index.json".format(BUNDLE_BASE_URL, BUNDLE_ID))
            if isinstance(index, list) and index:
                return str(index[-1]), "feed"
        except (requests.RequestException, ValueError):
            pass
        raise CLIError(
            "Could not resolve the latest extension bundle version from {}. "
            "Pass --version to choose one explicitly.".format(BUNDLE_BASE_URL)
        )

    if kind == "core-tools":
        try:
            latest = _get_json(CORE_TOOLS_RELEASES_API, token=gh_token)
            tag = (latest or {}).get("tag_name")
            if tag:
                return str(tag).lstrip("v"), "feed"
        except (requests.RequestException, ValueError):
            pass
        return PINNED_VERSIONS["core-tools"], "pinned-fallback"

    try:
        index = _get_json(NODE_DIST_INDEX)
        for entry in index or []:
            if entry.get("lts"):
                return str(entry["version"]).lstrip("v"), "feed"
    except (requests.RequestException, ValueError, KeyError):
        pass
    return PINNED_VERSIONS["node"], "pinned-fallback"


def build_download_url(kind, version):
    os_tag = _os_tag(kind)
    arch = _arch_tag()
    if kind == "core-tools":
        return "https://github.com/Azure/azure-functions-core-tools/releases/download/{v}/Azure.Functions.Cli.{o}-{a}.{v}.zip".format(v=version, o=os_tag, a=arch)
    if kind == "node":
        suffix = "zip" if os_tag == "win" else "tar.gz"
        return "https://nodejs.org/dist/v{v}/node-v{v}-{o}-{a}.{s}".format(v=version, o=os_tag, a=arch, s=suffix)
    return "{b}/ExtensionBundles/{i}/{v}/{i}.{v}_any-any.zip".format(b=BUNDLE_BASE_URL, i=BUNDLE_ID, v=version)


def expected_sha256(kind, url):
    """Publisher-published checksum for the archive, or None to skip verification.

    Node.js ships SHASUMS256.txt beside the artifact and Core Tools ship a .sha2
    sidecar. The extension bundle publishes neither, so it is verified by size only.
    An unreachable checksum is non-blocking: it downgrades to no verification rather
    than failing an otherwise good install.
    """
    try:
        if kind == "node":
            shasums_url = url.rsplit("/", 1)[0] + "/SHASUMS256.txt"
            body = requests.get(shasums_url, timeout=_METADATA_TIMEOUT).text
            wanted = url.rsplit("/", 1)[1]
            for line in body.splitlines():
                parts = line.strip().split()
                if len(parts) == 2 and parts[1] == wanted and len(parts[0]) == 64:
                    return parts[0].lower()
        elif kind == "core-tools":
            body = requests.get(url + ".sha2", timeout=_METADATA_TIMEOUT).text
            token = body.strip().split()[0] if body.strip() else ""
            if len(token) == 64:
                return token.lower()
    except (requests.RequestException, IndexError):
        return None
    return None


def _download(url, dest):
    declared = None
    written = 0
    try:
        with requests.get(url, stream=True, timeout=_DOWNLOAD_TIMEOUT) as response:
            if response.status_code == 404:
                raise CLIError("Download not found: {}. Check --version.".format(url))
            response.raise_for_status()
            declared = response.headers.get("Content-Length")
            written = 0
            with open(dest, "wb") as handle:
                for chunk in response.iter_content(chunk_size=_CHUNK):
                    if chunk:
                        handle.write(chunk)
                        written += len(chunk)
    except requests.RequestException as ex:
        raise CLIError("Failed to download {}: {}".format(url, ex)) from ex
    if declared and written != int(declared):
        raise CLIError(
            "Download from {} was truncated: expected {} bytes, got {}.".format(url, declared, written)
        )
    return written


def _sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(_CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_within(base, target):
    base = os.path.abspath(base)
    target = os.path.abspath(target)
    return target == base or target.startswith(base + os.sep)


def _safe_extract(archive_path, target):
    """Extract a zip or tar.gz, refusing entries that escape the target directory.

    Archive entries can carry '..' segments or absolute paths, and both zipfile and
    tarfile will happily write outside the destination if asked to.
    """
    if archive_path.endswith(".zip"):
        with zipfile.ZipFile(archive_path) as archive:
            for name in archive.namelist():
                if not _is_within(target, os.path.join(target, name)):
                    raise CLIError("Refusing to extract entry outside the target directory: {}".format(name))
            archive.extractall(target)
        return

    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive.getmembers():
            if member.issym() or member.islnk():
                link_target = os.path.join(target, os.path.dirname(member.name), member.linkname)
                if not _is_within(target, link_target):
                    raise CLIError("Refusing to extract link pointing outside the target directory: {}".format(member.name))
            if not _is_within(target, os.path.join(target, member.name)):
                raise CLIError("Refusing to extract entry outside the target directory: {}".format(member.name))
        archive.extractall(target)


def _flatten_container(target):
    """Hoist a single top-level folder's contents up one level.

    Node and Core Tools archives wrap everything in one versioned directory; the
    detector in _local.py looks for the executable directly under the dependency
    folder, so that wrapper has to go.
    """
    entries = os.listdir(target)
    if len(entries) != 1:
        return
    container = os.path.join(target, entries[0])
    if not os.path.isdir(container):
        return
    for name in os.listdir(container):
        shutil.move(os.path.join(container, name), os.path.join(target, name))
    os.rmdir(container)


def _mark_executable(target):
    if os.name == "nt":
        return
    for root, _, files in os.walk(target):
        for name in files:
            path = os.path.join(root, name)
            if os.path.splitext(name)[1] in ("", ".sh"):
                try:
                    os.chmod(path, os.stat(path).st_mode | 0o111)
                except OSError:
                    pass


def manifest_path(target):
    return os.path.join(target, MANIFEST_NAME)


def write_manifest(target, kind, version, source_url):
    """Record what this CLI put on disk.

    This file is what makes 'dependency uninstall' safe: it is the only evidence
    that the CLI, rather than the user or VS Code, created the folder's contents.
    """
    files = []
    for root, _, names in os.walk(target):
        for name in names:
            if root == target and name == MANIFEST_NAME:
                continue
            full = os.path.join(root, name)
            files.append({
                "path": os.path.relpath(full, target).replace(os.sep, "/"),
                "size": os.path.getsize(full)
            })
    manifest = {
        "dependencyName": kind,
        "version": version,
        "sourceUrl": source_url,
        "createdAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "installedBy": "az logicapp dependency install",
        "fileCount": len(files),
        "files": sorted(files, key=lambda item: item["path"])
    }
    with open(manifest_path(target), "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
    return manifest


def read_manifest(target):
    path = manifest_path(target)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def verify_manifest(target):
    """Report which recorded files are now missing or a different size."""
    manifest = read_manifest(target)
    if not manifest:
        return None
    problems = []
    for entry in manifest.get("files", []):
        full = os.path.join(target, entry["path"].replace("/", os.sep))
        if not os.path.isfile(full):
            problems.append({"path": entry["path"], "issue": "missing"})
        elif os.path.getsize(full) != entry["size"]:
            problems.append({"path": entry["path"], "issue": "size-mismatch"})
    return {"fileCount": manifest.get("fileCount", 0), "problems": problems, "intact": not problems}


def _assert_not_in_use(target, verb="replace"):
    """Refuse to touch a folder that something is still holding open.

    Renaming is the same operation the change would start with, so this probes the
    exact failure rather than guessing. On Windows an open handle anywhere under the
    folder makes it fail; elsewhere it generally succeeds and the change is safe.

    This refuses rather than terminating the holder, matching how 'runtime stop'
    declines to kill processes this CLI did not start.
    """
    if not os.path.isdir(target):
        return
    probe = target + ".inuse-probe"
    try:
        os.rename(target, probe)
        os.rename(probe, target)
    except OSError as ex:
        raise ValidationError(
            "Cannot {} {} because a process is still using it. "
            "Stop any running runtime first -- 'az logicapp runtime stop --all' stops hosts this CLI "
            "started -- then re-run this command.".format(verb, target)
        ) from ex


def install_target(kind, version, root=None):
    root = root or dependencies_root()
    if kind == "bundle":
        return os.path.join(bundle_install_root(), version)
    return os.path.join(root, managed_subdir(kind))


def _resolve_npm(root=None):
    """Locate npm, preferring the Node.js this CLI manages over any copy on PATH.

    A CLI-installed Node.js is deliberately not added to PATH, so a user who just ran
    'dependency install --kind node' has an npm that searching PATH alone never finds.
    """
    managed = os.path.join(root or dependencies_root(), managed_subdir("node") or "")
    search = [item for item in (managed, os.path.join(managed, "bin")) if os.path.isdir(item)]
    if search:
        found = shutil.which("npm", path=os.pathsep.join(search))
        if found:
            return found
    return shutil.which("npm")


def _run_npm(npm, args, timeout=_NPM_TIMEOUT):
    """Run npm, returning (succeeded, combined output).

    stderr is folded into stdout because npm splits a single failure across both, and
    the whole thing is surfaced to the user when an install fails.
    """
    try:
        completed = subprocess.run(  # pylint: disable=subprocess-run-check
            [npm] + list(args),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            shell=False,
            timeout=timeout,
            env=dependency_environment(npm))
    except subprocess.TimeoutExpired:
        return False, "npm did not finish within {} seconds.".format(timeout)
    except OSError as ex:
        return False, str(ex)
    return completed.returncode == 0, completed.stdout or ""


def _npm_node_major(npm):
    """Major version of the Node.js that runs this npm, or None if it cannot be read.

    'npm --versions' prints a JavaScript object literal rather than JSON, so the node
    entry is matched directly instead of being parsed.
    """
    ok, output = _run_npm(npm, ["--versions"], timeout=_METADATA_TIMEOUT)
    if not ok:
        return None
    match = re.search(r"node:\s*'?v?(\d+)", output)
    return int(match.group(1)) if match else None


def _resolve_azurite_version(npm, registry, version):
    if version:
        return version, "explicit"
    ok, output = _run_npm(
        npm, ["view", "azurite@latest", "version", "--registry", registry], timeout=_METADATA_TIMEOUT)
    if ok:
        for line in reversed((output or "").strip().splitlines()):
            candidate = line.strip()
            if re.match(r"^\d+\.\d+\.\d+", candidate):
                return candidate, "feed"
    return PINNED_VERSIONS["azurite"], "pinned-fallback"


def _azurite_package_dir(base):
    """Where npm unpacked the azurite package: Windows and Unix global layouts differ."""
    for candidate in (os.path.join(base, "node_modules", "azurite"),
                      os.path.join(base, "lib", "node_modules", "azurite")):
        if os.path.isdir(candidate):
            return candidate
    return None


def _azurite_launcher(base):
    """The launcher find_tool will look for, searched exactly the way find_tool does.

    Checking this rather than npm's exit code is what makes a reported success mean
    'dependency check will now find Azurite'.
    """
    search = [item for item in (base, os.path.join(base, "bin")) if os.path.isdir(item)]
    if not search:
        return None
    return shutil.which("azurite", path=os.pathsep.join(search))


def _installed_azurite_version(package_dir, fallback):
    try:
        with open(os.path.join(package_dir, "package.json"), "r", encoding="utf-8") as handle:
            return str(json.load(handle).get("version") or fallback)
    except (OSError, ValueError):
        return fallback


def _install_azurite(version=None, root=None, source_url=None, force=False):
    """Install Azurite from the npm registry into the managed dependency folder.

    Azurite is published only through npm and declares twenty runtime dependencies, so
    unlike Node.js and Core Tools there is no self-contained archive to download and
    unpack -- the dependency tree has to be resolved. npm does that, and verifies every
    tarball it fetches against the integrity hash in the registry metadata as it goes.

    '--global --prefix <dir>' confines the whole install to that folder: nothing reaches
    a global prefix, the user's PATH, or their project.
    """
    npm = _resolve_npm(root)
    if not npm:
        raise ValidationError(
            "Azurite is installed from the npm registry, and npm could not be found. Install Node.js "
            "first with 'az logicapp dependency install --kind node' (npm ships with it), or install "
            "Node.js from https://nodejs.org, then re-run this command."
        )

    node_major = _npm_node_major(npm)
    if node_major is not None and node_major < AZURITE_MIN_NODE_MAJOR:
        raise ValidationError(
            "Azurite requires Node.js {} or later, but the npm at {} runs on Node.js {}. Install a "
            "current Node.js with 'az logicapp dependency install --kind node', then re-run this "
            "command.".format(AZURITE_MIN_NODE_MAJOR, npm, node_major)
        )

    # The publisher's registry by default, rather than whatever this machine's npm config
    # points at. Node.js and Core Tools are fetched from their publisher too, and an
    # internal mirror that does not carry azurite is the usual reason the documented
    # 'npm install -g azurite' route fails with a 401. --source-url takes another registry.
    registry = source_url or NPM_REGISTRY

    resolved_version, version_source = _resolve_azurite_version(npm, registry, version)
    target = install_target("azurite", resolved_version, root)

    existing = read_manifest(target)
    if existing and not force and existing.get("version") == resolved_version:
        state = verify_manifest(target)
        if state and state["intact"]:
            return {
                "kind": "azurite",
                "version": resolved_version,
                "versionSource": version_source,
                "path": target,
                "sourceUrl": registry,
                "state": "already-installed",
                "checksumVerified": None,
                "fileCount": state["fileCount"]
            }

    if existing is None and os.path.isdir(target) and os.listdir(target) and not force:
        return {
            "kind": "azurite",
            "version": resolved_version,
            "versionSource": version_source,
            "path": target,
            "sourceUrl": registry,
            "state": "already-present-not-cli-managed",
            "checksumVerified": None,
            "fileCount": None,
            "message": "{} already exists and was not installed by this CLI, so it was left alone. "
                       "Use --force to replace it with a fresh install.".format(target)
        }

    _assert_not_in_use(target)

    temp_dir = tempfile.mkdtemp(prefix="az-logicapp-dep-")
    staging = os.path.join(temp_dir, "azurite")
    try:
        os.makedirs(staging, exist_ok=True)
        ok, output = _run_npm(npm, [
            "install", "azurite@{}".format(resolved_version),
            "--global",
            "--prefix", staging,
            "--registry", registry,
            "--no-audit",
            "--no-fund",
            "--loglevel", "error",
        ])
        if not ok:
            raise CLIError(
                "Installing Azurite with npm failed. Nothing was written to {}.\n\n{}\n\n"
                "If your machine reaches npm through a proxy, set HTTPS_PROXY and re-run. To install "
                "from a different registry, pass --source-url with its URL.".format(
                    target, (output or "").strip())
            )

        package_dir = _azurite_package_dir(staging)
        launcher = _azurite_launcher(staging)
        if not package_dir or not launcher:
            raise CLIError(
                "npm reported success but no runnable Azurite was found under {}. Nothing was "
                "written to {}.\n\n{}".format(staging, target, (output or "").strip())
            )
        resolved_version = _installed_azurite_version(package_dir, resolved_version)

        _mark_executable(staging)

        if os.path.isdir(target):
            shutil.rmtree(target)
        parent = os.path.dirname(target)
        if parent:
            os.makedirs(parent, exist_ok=True)
        shutil.move(staging, target)

        manifest = write_manifest(target, "azurite", resolved_version, registry)
    except OSError as ex:
        raise FileOperationError("Failed to install azurite: {}".format(ex)) from ex
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return {
        "kind": "azurite",
        "version": resolved_version,
        "versionSource": version_source,
        "path": target,
        # npm checks every tarball against the registry's integrity hash. That is only a
        # publisher guarantee when the registry is the publisher's own.
        "checksumVerified": not source_url,
        "sourceUrl": registry,
        "state": "installed",
        "fileCount": manifest["fileCount"]
    }


def install_dependency(kind, version=None, root=None, source_url=None, gh_token=None, force=False):
    """Download, verify, extract and record one dependency. Returns a report row."""
    if kind in _REFUSALS:
        raise InvalidArgumentValueError(_REFUSALS[kind])
    if kind not in INSTALLABLE_KINDS:
        raise InvalidArgumentValueError("Unknown dependency kind '{}'.".format(kind))

    if kind == "azurite":
        return _install_azurite(version=version, root=root, source_url=source_url, force=force)

    if source_url:
        resolved_version = version or "custom"
        version_source = "explicit" if version else "unknown"
        url = source_url
    else:
        resolved_version, version_source = resolve_version(kind, version, gh_token)
        url = build_download_url(kind, resolved_version)

    target = install_target(kind, resolved_version, root)

    existing = read_manifest(target)
    if existing and not force and existing.get("version") == resolved_version:
        state = verify_manifest(target)
        if state and state["intact"]:
            return {
                "kind": kind,
                "version": resolved_version,
                "versionSource": version_source,
                "path": target,
                "sourceUrl": url,
                "state": "already-installed",
                "checksumVerified": None,
                "fileCount": state["fileCount"]
            }

    # Someone else's copy -- Core Tools downloads bundles here, and VS Code shares this
    # root. Taking it over would stamp our manifest on files we did not place, and a later
    # uninstall would then delete something the user had before this CLI ran.
    if existing is None and os.path.isdir(target) and os.listdir(target) and not force:
        return {
            "kind": kind,
            "version": resolved_version,
            "versionSource": version_source,
            "path": target,
            "sourceUrl": url,
            "state": "already-present-not-cli-managed",
            "checksumVerified": None,
            "fileCount": None,
            "message": "{} already exists and was not installed by this CLI, so it was left alone. "
                       "Use --force to replace it with a fresh download.".format(target)
        }

    _assert_not_in_use(target)

    temp_dir = tempfile.mkdtemp(prefix="az-logicapp-dep-")
    archive_name = "{}.{}".format(kind, "zip" if url.endswith(".zip") else "tar.gz")
    archive_path = os.path.join(temp_dir, archive_name)
    try:
        _download(url, archive_path)

        wanted = None if source_url else expected_sha256(kind, url)
        checksum_verified = False
        if wanted:
            actual = _sha256_of(archive_path)
            if actual.lower() != wanted.lower():
                raise CLIError(
                    "Checksum verification failed for {}: expected SHA256 {} but got {}. "
                    "The download was discarded.".format(kind, wanted, actual)
                )
            checksum_verified = True

        staging = os.path.join(temp_dir, "extracted")
        os.makedirs(staging, exist_ok=True)
        _safe_extract(archive_path, staging)
        _flatten_container(staging)
        _mark_executable(staging)

        if os.path.isdir(target):
            shutil.rmtree(target)
        parent = os.path.dirname(target)
        if parent:
            os.makedirs(parent, exist_ok=True)
        shutil.move(staging, target)

        manifest = write_manifest(target, kind, resolved_version, url)
    except OSError as ex:
        raise FileOperationError("Failed to install {}: {}".format(kind, ex)) from ex
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return {
        "kind": kind,
        "version": resolved_version,
        "versionSource": version_source,
        "path": target,
        "sourceUrl": url,
        "state": "installed",
        "checksumVerified": checksum_verified,
        "fileCount": manifest["fileCount"]
    }


def uninstall_dependency(kind, root=None):
    """Remove only material this CLI recorded installing.

    A folder with no manifest is left untouched. It may be a hand-installed tool or
    one Visual Studio Code put there, and the shared dependency root (D122) makes
    that likely rather than hypothetical.
    """
    if kind in _REFUSALS:
        raise InvalidArgumentValueError(_REFUSALS[kind])
    if kind not in INSTALLABLE_KINDS:
        raise InvalidArgumentValueError("Unknown dependency kind '{}'.".format(kind))

    root = root or dependencies_root()
    if kind == "bundle":
        candidates = []
        bundle_root = bundle_install_root()
        if os.path.isdir(bundle_root):
            candidates = [os.path.join(bundle_root, name) for name in sorted(os.listdir(bundle_root))]
    else:
        candidates = [os.path.join(root, managed_subdir(kind))]

    removed = []
    for target in candidates:
        manifest = read_manifest(target)
        if not manifest:
            continue
        if manifest.get("installedBy") != "az logicapp dependency install":
            continue
        _assert_not_in_use(target, verb="remove")
        try:
            shutil.rmtree(target)
        except OSError as ex:
            raise FileOperationError("Failed to remove {}: {}".format(target, ex)) from ex
        removed.append({"path": target, "version": manifest.get("version"), "fileCount": manifest.get("fileCount", 0)})

    if not removed:
        return {
            "kind": kind,
            "state": "not-cli-managed",
            "removed": [],
            "message": "Nothing installed by this CLI was found for '{}'. Anything present was installed "
                       "by you or by Visual Studio Code and has been left alone.".format(kind)
        }
    return {"kind": kind, "state": "removed", "removed": removed, "message": None}


def refusal_message(kind):
    return _REFUSALS.get(kind)
