# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Run this package's engine hooks through the X Engineering Agent broker."""

from pathlib import Path

import pytest

from x_engineering_agent.repository import testing

REPOSITORY = "Azure/azure-cli-extensions"
PACKAGE = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def pinned(monkeypatch, tmp_path):
    testing.pin(monkeypatch, tmp_path, testing.local(PACKAGE, REPOSITORY))


DIRECTORIES = {
    ("Azure", "azure-cli", "src/azure-cli/azure/cli/command_modules"): {"vm", "network", "storage"},
    ("Azure", "azure-cli-extensions", "src"): {"containerapp", "aks-preview"},
}


@pytest.fixture(autouse=True)
def offline_directories(monkeypatch):
    from x_engineering_agent.tools.targets import discovery

    def listing(owner, repo, path, branch, token=None):
        return set(DIRECTORIES[(owner, repo, path)])

    monkeypatch.setattr(discovery, "_list_repo_dirs", listing)


def hook(name, *args, **kwargs):
    return testing.hook(REPOSITORY, name, *args, **kwargs)


def test_targets_follow_extension_layout():
    target = hook("infer_target", "az containerapp up fails", ["src/containerapp/azext_containerapp/custom.py"])
    assert target["name"] == "containerapp"
    assert hook("resolve_target", "containerapp")["name"] == "containerapp"


def test_titles_use_cli_style():
    title = hook("pr_title", component="containerapp", issue_number=1, command="az containerapp up", summary="Fix up")
    assert title.startswith("[")
    assert "containerapp" in title.lower()
    assert hook("pr_format_guidance", component="containerapp", issue_number=1)
    assert hook("execution_instructions")


def test_codegen_guidance_targets_extensions():
    assert isinstance(hook("codegen_guidance", "containerapp"), str)


def test_changed_tests_and_failures():
    files = ["src/containerapp/azext_containerapp/tests/latest/test_containerapp_commands.py"]
    assert hook("changed_test_files", files)
    failed = hook("extract_failed_tests", "FAILED src/x/tests/latest/test_a.py::Test::test_b - boom")
    assert failed


def test_readiness_without_generated_output_requires_no_validation():
    pr = {"body": "", "head": {"sha": "a" * 40, "repo": {"full_name": "fork/azure-cli-extensions"}}}
    changes = [{"filename": "src/containerapp/azext_containerapp/custom.py", "status": "modified"}]
    assert hook("readiness_policy", pr, changes) == {"blocked": None, "validation_required": False}


def test_definitions_reference_existing_engine_helpers_and_tools():
    assert testing.definition_problems(testing.local(PACKAGE, REPOSITORY)) == []


@pytest.mark.parametrize(("files", "expected"), [
    (["src/storage-preview/azext_storage_preview/custom.py"], ("extension", ["storage-preview"])),
    (["src/storage-preview/azext_storage_preview/tests/latest/test_blob.py"], (None, [])),
    (["README.md"], (None, [])),
], ids=["extension-source", "tests-only", "root-docs"])
def test_source_only_changes_resolve_extension_live_test_scope(files, expected):
    kind, names = hook("live_test_source_targets", files)
    assert (kind, list(names)) == expected
