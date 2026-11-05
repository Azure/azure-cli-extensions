# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import importlib
import sys
import types
from pathlib import Path

import pytest
from x_engineering_agent.tools.copilot import validation


PACKAGE = Path(__file__).resolve().parents[1]
TOOLS = PACKAGE / "tools"
module = sys.modules.get("repository_tools")
if module is None:
    module = types.ModuleType("repository_tools")
    module.__path__ = [str(TOOLS)]
    sys.modules["repository_tools"] = module
elif str(TOOLS) not in module.__path__:
    module.__path__.append(str(TOOLS))

checks = importlib.import_module("repository_tools.validation.checks")
REPOSITORY = "Azure/azure-cli-extensions"


@pytest.fixture(autouse=True)
def bound(monkeypatch):
    """Bind this package's hooks the way the pinned job handoff does."""
    monkeypatch.setattr(validation, "_BINDING", {
        "repository": REPOSITORY, "settings": {"playback": True}, "live_test": True,
    })
    monkeypatch.setattr(validation, "_CHECKS", checks)


def test_validation_exports_engine_hooks():
    assert {"unit_test_scope", "python_roots", "generation_source_checks"} <= set(vars(checks))
    assert validation._generation_source_hook("Azure/aaz") is checks.generation_source_checks
    assert validation._generation_source_hook(REPOSITORY) is None


def _unit_test(path, class_name):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "import unittest\n\n"
        f"class {class_name}(unittest.TestCase):\n"
        "    pass\n",
        encoding="utf-8",
    )
    return path


def test_extension_validation_selects_directly_changed_test(tmp_path):
    extension = tmp_path / "src/example"
    changed = _unit_test(extension / "tests/latest/test_regression.py", "RegressionTests")
    _unit_test(extension / "tests/latest/test_unrelated.py", "UnrelatedTests")

    assert validation.python_unit_files("Azure/azure-cli-extensions", tmp_path, [changed]) == [changed]
