# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Deterministic review policy this package contributes for Azure/azure-cli-extensions."""

import importlib
import sys
import types
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parents[1]
TOOLS = PACKAGE / "tools"
module = sys.modules.get("repository_tools")
if module is None:
    module = types.ModuleType("repository_tools")
    module.__path__ = [str(TOOLS)]
    sys.modules["repository_tools"] = module
elif str(TOOLS) not in module.__path__:
    module.__path__.append(str(TOOLS))

analysis = importlib.import_module("repository_tools.reviewer.policy.analysis")

REPOSITORY = "Azure/azure-cli-extensions"


def _change(filename, patch=""):
    additions = sum(1 for line in patch.splitlines() if line.startswith("+") and not line.startswith("+++"))
    return {"filename": filename, "patch": patch, "additions": additions, "deletions": 0}


def _assert_release_artifact_blocks(changes, production, summary):
    findings, target = analysis._release_artifact_check(
        REPOSITORY, {"title": "Fix ssh port"}, changes, production, "fork/repo", "abc123",
    )

    assert any(summary in finding["summary"] for finding in findings)
    assert all(finding["severity"] == "blocking" and finding["tool"] == "release-artifact"
               for finding in findings)
    assert target["tool"] == "release-artifact"
    assert findings[0]["url"].startswith("https://github.com/fork/repo/blob/abc123/")


_SSH_COMMAND = _change(
    "src/ssh/azext_ssh/commands.py", "@@ -1 +1,2 @@\n+    g.custom_command('connect', 'ssh_connect')\n",
)


@pytest.mark.parametrize(("changes", "summary"), [
    ([_SSH_COMMAND], "without a release note"),
    ([_SSH_COMMAND, _change("src/aks-preview/HISTORY.rst", "@@ -1 +1,2 @@\n+* Fix ssh port\n")],
     "not placed with every affected component: ssh"),
], ids=["no-history", "history-in-wrong-component"])
def test_release_artifact_findings_block(changes, summary):
    _assert_release_artifact_blocks(changes, [_SSH_COMMAND], summary)


def test_analyze_review_tools_reports_every_tool_status_and_hides_patches():
    secret_line = "+    c.argument('token', help='do-not-leak-patch-text')"
    production = _change("src/ssh/azext_ssh/_params.py", f"@@ -1 +1,2 @@\n{secret_line}\n")
    test_change = _change("src/ssh/azext_ssh/tests/latest/test_ssh.py", "@@ -1 +1,2 @@\n+    assert True\n")

    result = analysis.analyze_review_tools(REPOSITORY, {"title": "Fix ssh token"}, [production, test_change])

    statuses = {check["tool"]: check["status"] for check in result["checks"]}
    assert set(statuses) == set(analysis.TOOL_TITLES)
    assert statuses["release-artifact"] == "finding"
    assert statuses["test-strength"] == "finding"
    assert statuses["user-intent"] == "review"
    assert statuses["generated-ownership"] == "not_applicable"
    assert result["finding_count"] == len(result["findings"]) == 2
    assert "do-not-leak-patch-text" not in repr(result)
