# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Pre-publication gates this package's hooks contribute for Azure/azure-cli-extensions."""

from pathlib import Path

import pytest

from x_engineering_agent.repository import testing
from x_engineering_agent.tools.copilot import prepublication

REPOSITORY = "Azure/azure-cli-extensions"
PACKAGE = Path(__file__).resolve().parents[1]
EXT = "src/ssh"
VALIDATION = {"status": "passed", "reports": [{"status": "passed", "lint": {
    "flake8": {"status": "passed"}, "pylint": {"status": "passed"}}}]}
PARAMS_BASE = (
    "def load_arguments(self, _):\n"
    "    with self.argument_context('ssh vm') as c:\n"
    "        c.argument('top', help='Maximum results.')\n"
)
_PARAMS = f"{EXT}/azext_ssh/_params.py"
_HISTORY = f"{EXT}/HISTORY.rst"
_HEAD = {_PARAMS: PARAMS_BASE + "        c.argument('port', help='Port.')\n", _HISTORY: "1.0.1\n+ Add port\n1.0.0\n"}


@pytest.fixture(autouse=True)
def pinned(monkeypatch, tmp_path):
    testing.pin(monkeypatch, tmp_path, testing.local(PACKAGE, REPOSITORY))


def _job():
    return {"id": "a" * 64, "repository": REPOSITORY, "title": "[SSH] Add port",
            "base_branch": "main", "source_kind": "issue"}


def _evaluate(base, head):
    return prepublication.evaluate_candidate(_job(), base, head, read_file=head.get, validation=VALIDATION)


def _status(record, gate):
    return next(item["status"] for item in record["checks"] if item["gate"] == gate)


def test_release_needs_version_bump_and_leaves_index_alone():
    record = _evaluate({_PARAMS: PARAMS_BASE, _HISTORY: "1.0.0\n", "src/index.json": "{}\n"},
                       {**_HEAD, "src/index.json": '{"a": 1}\n'})
    assert _status(record, "release-artifact") == "blocked" and record["status"] == "blocked"
    summaries = " ".join(item["summary"] for item in record["findings"] if item["gate"] == "release-artifact")
    assert "VERSION" in summaries and "src/index.json" in summaries


def test_bumped_release_passes():
    record = _evaluate({_PARAMS: PARAMS_BASE, _HISTORY: "1.0.0\n", f"{EXT}/setup.py": "VERSION = '1.0.0'\n"},
                       {**_HEAD, f"{EXT}/setup.py": "VERSION = '1.0.1'\n"})
    assert _status(record, "release-artifact") == "passed"


def test_hand_edit_of_vendored_sdk_is_blocked():
    path = f"{EXT}/azext_ssh/vendored_sdks/ssh/_client.py"
    record = prepublication.evaluate_candidate(
        _job(), {path: "x = 1\n"}, {path: "x = 2\n"}, read_file={}.get, validation=VALIDATION,
    )
    assert record["status"] == "blocked"
    assert any(item["gate"] == "generated-ownership" for item in record["findings"])
