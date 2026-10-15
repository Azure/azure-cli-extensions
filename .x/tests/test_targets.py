# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import importlib
import sys
import types
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
TOOLS = PACKAGE / "tools"
module = sys.modules.get("repository_tools")
if module is None:
    module = types.ModuleType("repository_tools")
    module.__path__ = [str(TOOLS)]
    sys.modules["repository_tools"] = module
elif str(TOOLS) not in module.__path__:
    module.__path__.append(str(TOOLS))

targets = importlib.import_module("repository_tools.fixer.azure_cli.targets")


def test_unresolved_extension_issue_remains_unknown(monkeypatch):
    monkeypatch.setattr(
        targets,
        "resolve_target",
        lambda name, token=None: {"kind": "unknown", "name": name, "repo": None},
    )

    assert targets.infer_target(
        text="Unresolved extension issue",
        pr_files=[],
    ) == {
        "kind": "unknown",
        "name": None,
        "repo": None,
    }
