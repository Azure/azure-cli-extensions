# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""The engine's SWE replay harness builds extension environments from this package."""

from pathlib import Path

import pytest

from x_engineering_agent.release_evaluation.swe_replay.dataset import ReplayCase
from x_engineering_agent.release_evaluation.swe_replay.harness import repository_environment
from x_engineering_agent.repository import testing

REPOSITORY = "Azure/azure-cli-extensions"
PACKAGE = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def pinned(monkeypatch, tmp_path):
    testing.pin(monkeypatch, tmp_path, testing.local(PACKAGE, REPOSITORY))


def case(*tests):
    return ReplayCase(
        id="c", repository=REPOSITORY, issue_number=1, base_sha="0" * 40, issue={},
        fail_to_pass=tests, pass_to_pass=("src/aks-preview/azext_aks_preview/tests/test_b.py::test_b",),
        metadata={"merged_at": "2025-01-02T00:00:00Z"},
    )


def test_released_cli_with_tested_extensions_as_dev_sources(monkeypatch):
    monkeypatch.delenv("SWE_REPLAY_EXTENSIONS_CLI_VERSION", raising=False)
    environment = repository_environment(
        case("src/containerapp/azext_containerapp/tests/test_a.py::test_a"), Path("/w/c/repo"), "py",
    )
    assert environment.python == "/w/c/venv/bin/python"
    install = environment.commands[2]
    assert install[3:] == ["", "2025-01-02T00:00:00Z", "/w/c/azure-cli"]
    editable = [argv[-1] for argv in environment.commands if argv[-1].startswith("--editable=")]
    assert editable == ["--editable=src/aks-preview", "--editable=src/containerapp"]
    assert environment.env == {
        "AZURE_CORE_COLLECT_TELEMETRY": "false", "AZURE_EXTENSION_DEV_SOURCES": "/w/c/repo/src",
    }


def test_pinned_cli_version_option(monkeypatch):
    monkeypatch.setenv("SWE_REPLAY_EXTENSIONS_CLI_VERSION", "2.70.0")
    environment = repository_environment(case(), Path("/w/c/repo"), "py")
    assert environment.commands[2][3] == "2.70.0"


def test_invalid_cli_version_is_rejected(monkeypatch):
    monkeypatch.setenv("SWE_REPLAY_EXTENSIONS_CLI_VERSION", "latest")
    with pytest.raises(Exception, match="SWE_REPLAY_EXTENSIONS_CLI_VERSION"):
        repository_environment(case(), Path("/w/c/repo"), "py")
