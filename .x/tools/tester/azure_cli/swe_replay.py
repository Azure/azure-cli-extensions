# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""SWE replay environment for azure-cli-extensions checkouts."""

import posixpath

ENV = {"AZURE_CORE_COLLECT_TELEMETRY": "false"}
VERSION_OPTION = "SWE_REPLAY_EXTENSIONS_CLI_VERSION"

EGG_INFO_SCRIPT = (
    "import os, runpy, sys; os.chdir(sys.argv[1]); sys.argv = ['setup.py', 'egg_info']; "
    "runpy.run_path('setup.py', run_name='__main__')"
)

# The test SDK isn't published with the CLI, so install it from the matching release tag.
INSTALL_CLI = r"""
import json, subprocess, sys, urllib.request
pinned, merged_at, testsdk = sys.argv[1:4]
version = pinned
if not version:
    with urllib.request.urlopen("https://pypi.org/pypi/azure-cli/json", timeout=60) as response:
        releases = json.load(response)["releases"]
    dated = sorted(
        (min(f["upload_time_iso_8601"] for f in files), name)
        for name, files in releases.items()
        if files and all(part.isdigit() for part in name.split("."))
    )
    version = [name for uploaded, name in dated if not merged_at or uploaded <= merged_at][-1]
pip = [sys.executable, "-m", "pip", "install", "-q", "--disable-pip-version-check"]
subprocess.run(pip + [f"azure-cli=={version}"], check=True)
subprocess.run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--sparse", "--branch",
                f"azure-cli-{version}", "https://github.com/Azure/azure-cli.git", testsdk], check=True)
subprocess.run(["git", "-C", testsdk, "sparse-checkout", "set", "src/azure-cli-testsdk"], check=True)
subprocess.run(pip + [testsdk + "/src/azure-cli-testsdk"], check=True)
print(version)
"""


def pip_install(python, *args):
    return [python, "-m", "pip", "install", "-q", "--disable-pip-version-check", *args]


def cli_version(options):
    """azure-cli release to test extensions against; defaults to the one current at the fix."""
    value = str((options or {}).get(VERSION_OPTION) or "").strip()
    if value and not all(part.isdigit() for part in value.split(".")):
        raise ValueError(f"{VERSION_OPTION} must be a release version")
    return value


def environment(case, root, python, options=None):
    """A released azure-cli plus the tested extensions as dev extensions."""
    if case.get("test_framework") != "pytest":
        return None
    extensions = sorted({
        "/".join(test.split("::", 1)[0].split("/")[:2])
        for test in (*case.get("fail_to_pass", ()), *case.get("pass_to_pass", ()))
        if test.startswith("src/")
    })
    if not extensions:
        return None
    root = root.rstrip("/")
    parent = posixpath.dirname(root)
    venv = posixpath.join(parent, "venv")
    venv_python = posixpath.join(venv, "bin", "python")
    commands = [
        [python, "-m", "venv", venv],
        pip_install(venv_python, "pytest", "setuptools", "wheel"),
        [
            venv_python, "-c", INSTALL_CLI, cli_version(options),
            str(case.get("merged_at") or ""), posixpath.join(parent, "azure-cli"),
        ],
    ]
    for extension in extensions:
        commands.append(pip_install(venv_python, f"--editable={extension}"))
        commands.append([venv_python, "-c", EGG_INFO_SCRIPT, posixpath.join(root, extension)])
    # Never set this for azure-cli itself: its src/ packages would load as broken extensions.
    return {
        "commands": commands,
        "python": venv_python,
        "env": {**ENV, "AZURE_EXTENSION_DEV_SOURCES": posixpath.join(root, "src")},
    }
