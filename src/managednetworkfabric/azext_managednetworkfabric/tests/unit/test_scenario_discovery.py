# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import ast
from collections import Counter
from pathlib import Path


SCENARIO_DIRECTORY = Path(__file__).resolve().parents[1] / "latest"


def test_scenario_callbacks_have_unique_names():
    duplicates = []
    for path in sorted(SCENARIO_DIRECTORY.glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        names = Counter(
            node.name
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name.startswith("call_scenario")
        )
        duplicates.extend(
            f"{path.name}:{name}" for name, count in names.items() if count > 1
        )
    assert not duplicates, f"Overwritten scenario callbacks: {duplicates}"


def test_scenario_callbacks_are_reachable_from_test_methods():
    unreachable = []
    for path in sorted(SCENARIO_DIRECTORY.glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        functions = {
            node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)
        }
        pending = [
            method
            for cls in tree.body
            if isinstance(cls, ast.ClassDef)
            for method in cls.body
            if isinstance(method, ast.FunctionDef) and method.name.startswith("test_")
        ]
        reachable = set()
        while pending:
            for node in ast.walk(pending.pop()):
                if not isinstance(node, ast.Call) or not isinstance(
                    node.func, ast.Name
                ):
                    continue
                name = node.func.id
                if name in functions and name not in reachable:
                    reachable.add(name)
                    pending.append(functions[name])
        unreachable.extend(
            f"{path.name}:{name}"
            for name in functions
            if name.startswith("call_scenario") and name not in reachable
        )
    assert (
        not unreachable
    ), f"Scenario callbacks without test entry points: {unreachable}"
