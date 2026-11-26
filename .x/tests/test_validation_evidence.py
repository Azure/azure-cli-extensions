# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Test evidence for Azure CLI extension changes under this package's validation binding."""

import base64
import importlib
import json
import sys
import types
from pathlib import Path

import pytest
import yaml

from x_engineering_agent.tools.copilot import evidence, validation


PACKAGE = Path(__file__).resolve().parents[1]
TOOLS = PACKAGE / "tools"
_module = sys.modules.get("repository_tools")
if _module is None:
    _module = types.ModuleType("repository_tools")
    _module.__path__ = [str(TOOLS)]
    sys.modules["repository_tools"] = _module
elif str(TOOLS) not in _module.__path__:
    _module.__path__.append(str(TOOLS))
checks = importlib.import_module("repository_tools.validation.checks")


@pytest.fixture(autouse=True)
def bound(monkeypatch):
    """Bind this package's validation settings and checks as the pinned job handoff does."""
    profile = yaml.safe_load((PACKAGE / "x.yml").read_text(encoding="utf-8"))["profile"]
    monkeypatch.setattr(validation, "_BINDING", {
        "repository": "Azure/azure-cli-extensions",
        "settings": profile.get("validation") or {},
        "live_test": bool(profile.get("live_test")),
    })
    monkeypatch.setattr(validation, "_CHECKS", checks)


EXTENSION = "src/example/azext_example"
SOURCE = f"{EXTENSION}/custom.py"
TEST = f"{EXTENSION}/tests/latest/test_custom.py"


def _write(root, name, text):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _unit_test(body):
    return (
        "import unittest\n\n"
        "from azext_example.custom import add, other\n\n\n"
        "class CustomTests(unittest.TestCase):\n"
        f"    def test_behaviour(self):\n        {body}\n"
    )


def _validate(monkeypatch, root, repository, changed, base):
    """Run the validator in-process with a supervisor-style base snapshot."""
    home = root.parent / "home"
    home.mkdir(exist_ok=True)
    monkeypatch.setenv("HOME", str(home))
    snapshot = home / "validation-base.json"
    snapshot.write_text(json.dumps({"files": {
        name: None if text is None else base64.b64encode(text.encode()).decode()
        for name, text in base.items()
    }}))
    monkeypatch.setenv("X_AGENT_VALIDATION_BASE_JSON", str(snapshot))
    monkeypatch.delenv("X_AGENT_VALIDATION_EVIDENCE_TESTS_JSON", raising=False)
    paths = validation.candidate_paths(root, json.dumps(changed))
    return validation.validate(repository, root, paths)


@pytest.fixture
def repo(tmp_path):
    root = (tmp_path / "repo").resolve()
    _write(root, f"{EXTENSION}/__init__.py", "")
    _write(root, f"{EXTENSION}/tests/__init__.py", "")
    _write(root, f"{EXTENSION}/tests/latest/__init__.py", "")
    return root


BASE_SOURCE = (
    "def add(a, b):\n"
    "    return a - b\n\n\n"
    "def other():\n"
    "    return 1\n"
)
FIXED_SOURCE = BASE_SOURCE.replace("a - b", "a + b")


@pytest.mark.parametrize(("changed", "base", "kind", "fails_on_base"), [
    ([SOURCE, TEST], {SOURCE: BASE_SOURCE, TEST: None}, evidence.NEW_TEST, True),
    ([SOURCE], {SOURCE: BASE_SOURCE.replace("a - b", "a + b + 0")}, evidence.EXISTING_TEST, False),
], ids=["new-test-fails-on-base", "existing-test-covers-change"])
def test_test_covering_the_change_is_evidence(monkeypatch, repo, changed, base, kind, fails_on_base):
    _write(repo, SOURCE, FIXED_SOURCE)
    _write(repo, TEST, _unit_test("self.assertEqual(add(1, 2), 3)"))

    receipt = _validate(monkeypatch, repo, "Azure/azure-cli-extensions", changed, base)

    result = receipt["test_evidence"]
    assert receipt["status"] == "passed"
    assert result["kind"] == kind
    assert result["fails_on_base"] is fails_on_base
    assert result["tests"] == [f"{TEST}::CustomTests::test_behaviour"]
    assert result["covered_lines"] == {SOURCE: "2"}
    assert receipt["unit_test_coverage"] is True
    if kind == evidence.NEW_TEST:
        assert result["base_comparison"] == "run"
        assert result["line_coverage"] == "measured"
        assert result["changed_lines"] == {SOURCE: "2"}
        assert receipt["unit_tests"]["executed"] == 1


SCENARIO_TEST = (
    "from azure.cli.testsdk import ScenarioTest\n\n\n"
    "class CustomScenarioTest(ScenarioTest):\n"
    "    def test_live(self):\n        pass\n"
)


@pytest.mark.parametrize(("test_text", "changed", "base"), [
    (_unit_test("self.assertEqual(other(), 1)"), [SOURCE, TEST], {SOURCE: BASE_SOURCE, TEST: None}),
    (_unit_test("self.assertEqual(other(), 1)"), [SOURCE], {SOURCE: BASE_SOURCE}),
    (None, [SOURCE], {SOURCE: BASE_SOURCE}),
    (SCENARIO_TEST, [SOURCE], {SOURCE: BASE_SOURCE}),
], ids=["new-test-passes-on-base", "existing-test-misses-change", "no-tests", "scenario-test-only"])
def test_code_change_without_real_test_evidence_needs_evidence(monkeypatch, repo, test_text, changed, base):
    _write(repo, SOURCE, FIXED_SOURCE)
    if test_text:
        _write(repo, TEST, test_text)

    receipt = _validate(monkeypatch, repo, "Azure/azure-cli-extensions", changed, base)

    assert receipt["status"] == "needs-test-evidence"
    assert receipt["test_evidence"]["kind"] == evidence.NONE
    assert receipt["unit_test_coverage"] is False


def test_docs_only_change_is_exempt_with_justification(monkeypatch, repo):
    _write(repo, "src/example/HISTORY.rst", "1.0.1\n+++++\n* Fix\n")
    _write(repo, "src/example/README.md", "Docs\n")
    _write(repo, f"{EXTENSION}/_help.py", "helps = {}\n")

    receipt = _validate(
        monkeypatch, repo, "Azure/azure-cli-extensions",
        ["src/example/HISTORY.rst", "src/example/README.md", f"{EXTENSION}/_help.py"],
        {"src/example/HISTORY.rst": "", "src/example/README.md": None, f"{EXTENSION}/_help.py": "helps = 1\n"},
    )

    result = receipt["test_evidence"]
    assert receipt["status"] == "passed"
    assert result["kind"] == evidence.EXEMPT
    assert "documentation (1 file)" in result["justification"]
    assert "help text (1 file)" in result["justification"]
    assert "release notes (1 file)" in result["justification"]
    assert receipt["unit_tests"]["executed"] == 0
