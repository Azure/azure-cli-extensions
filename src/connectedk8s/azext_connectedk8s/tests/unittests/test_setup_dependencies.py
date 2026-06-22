# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import ast
from pathlib import Path


def _load_dependencies():
    setup_path = Path(__file__).resolve().parents[4] / "setup.py"
    setup_ast = ast.parse(setup_path.read_text(encoding="utf-8"))

    for node in setup_ast.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "DEPENDENCIES":
                    return ast.literal_eval(node.value)

    raise AssertionError("DEPENDENCIES was not found in setup.py")


def test_jsonschema_dependency_is_pinned_below_4_18():
    jsonschema_dependency = next(
        (
            dependency
            for dependency in _load_dependencies()
            if dependency.startswith("jsonschema")
        ),
        None,
    )
    assert jsonschema_dependency is not None
    assert jsonschema_dependency.startswith("jsonschema<4.18")
