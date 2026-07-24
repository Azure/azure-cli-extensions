#!/usr/bin/env python
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import ast
import builtins
import os
import textwrap
import types
import unittest
from unittest import mock


def _extract_function(func_name):
    src_path = os.path.join(os.path.dirname(__file__), "..", "..", "custom.py")
    src_path = os.path.normpath(src_path)
    with open(src_path, "r", encoding="utf-8") as handle:
        source = handle.read()

    tree = ast.parse(source, filename=src_path)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            namespace = {"SSH_EXTENSION_VERSION": "0.1.3"}
            func_source = ast.get_source_segment(source, node)
            exec(compile(textwrap.dedent(func_source), src_path, "exec"), namespace)  # pylint: disable=exec-used
            return namespace[func_name]

    raise ValueError(f"Function {func_name!r} not found in {src_path}")


class BastionCustomCommandUnitTest(unittest.TestCase):
    def _patch_azure_modules(self, version):
        validation_error = type("ValidationError", (Exception,), {})
        extension_module = types.ModuleType("azure.cli.core.extension")
        extension_module.get_extension = lambda _: types.SimpleNamespace(version=version)

        azclierror_module = types.ModuleType("azure.cli.core.azclierror")
        azclierror_module.ValidationError = validation_error

        core_module = types.ModuleType("azure.cli.core")
        core_module.extension = extension_module
        core_module.azclierror = azclierror_module

        cli_module = types.ModuleType("azure.cli")
        cli_module.core = core_module

        azure_module = types.ModuleType("azure")
        azure_module.cli = cli_module

        modules = {
            "azure": azure_module,
            "azure.cli": cli_module,
            "azure.cli.core": core_module,
            "azure.cli.core.extension": extension_module,
            "azure.cli.core.azclierror": azclierror_module,
        }
        return validation_error, mock.patch.dict("sys.modules", modules)

    def test_test_extension_does_not_import_pkg_resources(self):
        test_extension = _extract_function("_test_extension")
        validation_error, module_patch = self._patch_azure_modules("0.1.3")
        test_extension.__globals__["ValidationError"] = validation_error

        original_import = builtins.__import__

        def guarded_import(name, *args, **kwargs):
            if name == "pkg_resources":
                raise AssertionError("pkg_resources should not be imported")
            return original_import(name, *args, **kwargs)

        with module_patch, mock.patch("builtins.__import__", side_effect=guarded_import):
            test_extension("ssh")

    def test_test_extension_rejects_older_extension_versions(self):
        test_extension = _extract_function("_test_extension")
        validation_error, module_patch = self._patch_azure_modules("0.1.2")
        test_extension.__globals__["ValidationError"] = validation_error

        with module_patch, self.assertRaisesRegex(validation_error, "version >= 0.1.3"):
            test_extension("ssh")


if __name__ == "__main__":
    unittest.main()
