# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Offline playback of recorded ScenarioTests and read-only recordings (D4b)."""

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


REPOSITORY = "Azure/azure-cli-extensions"
EXTENSION = "src/example/azext_example"
SOURCE = f"{EXTENSION}/custom.py"
SCENARIO = f"{EXTENSION}/tests/latest/test_example_scenario.py"
RECORDINGS = f"{EXTENSION}/tests/latest/recordings"

# Mimics azure-cli-testsdk: replays recordings/<method>.yaml; without a recording it
# falls back to a live call; a request the recording lacks raises the vcr error.
SDK = '''
import os
import socket
import sys
import unittest


class CannotOverwriteExistingCassetteException(Exception):
    pass


class ScenarioTest(unittest.TestCase):
    def setUp(self):
        module = sys.modules[type(self).__module__].__file__
        path = os.path.join(os.path.dirname(module), "recordings", self._testMethodName + ".yaml")
        if not os.path.exists(path):
            socket.getaddrinfo("management.azure.com", 443)
        with open(path) as handle:
            self.recorded = handle.read().strip()
        if self.recorded == "network":
            socket.create_connection(("management.azure.com", 443), timeout=1)
        if self.recorded == "mismatch":
            raise CannotOverwriteExistingCassetteException("Can't overwrite existing cassette")
'''

BASE_SOURCE = (
    "def add(a, b):\n"
    "    return a + b\n\n\n"
    "def other():\n"
    "    return 1\n"
)


def _scenario(*methods):
    body = "".join(
        f"    def {name}(self):\n        {assertion}\n\n" for name, assertion in methods
    )
    return (
        "from azext_example.custom import add, other\n"
        "from .sdk import ScenarioTest\n\n\n"
        f"class ExampleScenarioTest(ScenarioTest):\n{body}"
    )


ADD_TEST = ("test_add", "self.assertEqual(add(1, 2), int(self.recorded))")
OTHER_TEST = ("test_other", "self.assertEqual(other(), int(self.recorded))")


def _write(root, name, text):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = (tmp_path / "repo").resolve()
    for name in (f"{EXTENSION}/__init__.py", f"{EXTENSION}/tests/__init__.py",
                 f"{EXTENSION}/tests/latest/__init__.py"):
        _write(root, name, "")
    _write(root, f"{EXTENSION}/tests/latest/sdk.py", SDK)
    _write(root, SOURCE, BASE_SOURCE)
    _write(root, SCENARIO, _scenario(ADD_TEST, OTHER_TEST))
    _write(root, f"{RECORDINGS}/test_add.yaml", "3\n")
    _write(root, f"{RECORDINGS}/test_other.yaml", "1\n")
    monkeypatch.setenv("X_AGENT_VALIDATION_RECORDING_SCOPES_JSON", json.dumps(["src/example"]))
    monkeypatch.delenv("X_AGENT_VALIDATION_RERECORD", raising=False)
    return root


def _validate(monkeypatch, root, changed, base):
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
    return validation.validate(REPOSITORY, root, paths)


def _key(method):
    return f"{SCENARIO}::ExampleScenarioTest::{method}"


def test_seeded_behaviour_regression_fails_validation_only_when_recordings_ship(monkeypatch, repo):
    _write(repo, SOURCE, BASE_SOURCE.replace("a + b", "a - b"))

    with pytest.raises(RuntimeError, match="behaviour regression") as error:
        _validate(monkeypatch, repo, [SOURCE], {SOURCE: BASE_SOURCE})
    assert _key("test_add") in str(error.value)

    monkeypatch.delenv("X_AGENT_VALIDATION_RECORDING_SCOPES_JSON")
    receipt = _validate(monkeypatch, repo, [SOURCE], {SOURCE: BASE_SOURCE})
    assert receipt["status"] == "needs-test-evidence"
    assert receipt["playback_tests"]["executed"] == 0


def test_passing_playback_test_covering_changed_lines_is_existing_evidence(monkeypatch, repo):
    base = BASE_SOURCE.replace("a + b", "a + b + 0")

    receipt = _validate(monkeypatch, repo, [SOURCE], {SOURCE: base})

    playback = receipt["playback_tests"]
    assert receipt["status"] == "passed"
    assert playback["status"] == "passed"
    assert playback["executed"] == 2
    assert playback["files"] == [SCENARIO]
    assert receipt["needs_recording"] is False
    assert receipt["unit_tests"]["executed"] == 0
    result = receipt["test_evidence"]
    assert result["kind"] == evidence.EXISTING_TEST
    assert result["covered_lines"] == {SOURCE: "2"}
    assert _key("test_add") in result["tests"]


@pytest.mark.parametrize(("case", "field", "method", "needs_recording"), [
    ("new-test", "needs_recording", "test_new", True),
    ("network", "needs_recording", "test_other", True),
    ("mismatch", "needs_recording", "test_other", True),
    ("2", "preexisting_failures", "test_other", False),
], ids=["new-test-without-recording", "network-attempt", "recording-mismatch", "fails-on-base"])
def test_playback_failures_are_attributed_not_called_regressions(
    monkeypatch, repo, case, field, method, needs_recording,
):
    base = {SOURCE: BASE_SOURCE.replace("a + b", "a + b + 0")}
    changed = [SOURCE]
    if case == "new-test":
        base[SCENARIO] = _scenario(ADD_TEST, OTHER_TEST)
        changed.append(SCENARIO)
        _write(repo, SCENARIO, _scenario(
            ADD_TEST, OTHER_TEST, ("test_new", "self.assertEqual(add(2, 2), 4)"),
        ))
    else:
        _write(repo, f"{RECORDINGS}/test_other.yaml", f"{case}\n")

    receipt = _validate(monkeypatch, repo, changed, base)

    playback = receipt["playback_tests"]
    assert playback[field] == [_key(method)]
    assert receipt["needs_recording"] is needs_recording
    if case == "new-test":
        assert playback["executed"] == 2
        assert _key("test_new") not in playback.get("preexisting_failures", [])
    else:
        assert receipt["status"] == "passed"


def test_validator_rejects_recording_changes_unless_rerecording(monkeypatch, repo):
    recording = f"{RECORDINGS}/test_add.yaml"
    base = BASE_SOURCE.replace("a + b", "a + b + 0")
    with pytest.raises(ValueError, match="read-only test recordings"):
        _validate(monkeypatch, repo, [SOURCE, recording], {SOURCE: base, recording: "3\n"})

    monkeypatch.setenv("X_AGENT_VALIDATION_RERECORD", "1")
    receipt = _validate(monkeypatch, repo, [SOURCE, recording], {SOURCE: base, recording: "3\n"})
    assert receipt["playback_tests"]["status"] == "passed"
