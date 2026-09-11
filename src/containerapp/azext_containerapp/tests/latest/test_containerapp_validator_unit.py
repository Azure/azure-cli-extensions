# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import ast
import textwrap
import unittest


def _extract_constants():
    """Load ACR_IMAGE_SUFFIXES from _constants.py without importing the full package."""
    constants_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..", "_constants.py")
    )
    ns = {}
    with open(constants_path, "r", encoding="utf-8") as f:
        exec(compile(f.read(), constants_path, "exec"), ns)  # pylint: disable=exec-used
    return ns


def _extract_function(func_name):
    """Extract a function from _utils_validation.py source using ast, avoiding import of azure.cli deps."""
    src_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..", "_utils_validation.py")
    )
    with open(src_path, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source, filename=src_path)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            func_source = ast.get_source_segment(source, node)
            ns = {**_extract_constants()}
            exec(compile(textwrap.dedent(func_source), src_path, "exec"), ns)  # pylint: disable=exec-used
            return ns[func_name]
    raise ValueError(f"Function {func_name!r} not found in {src_path}")


class TestIsAcrRegistry(unittest.TestCase):
    """Unit tests for is_acr_registry() — verifies all ACR sovereign cloud domains are recognized."""

    def setUp(self):
        self.is_acr_registry = _extract_function("is_acr_registry")

    # Standard Azure Public cloud
    def test_azurecr_io_is_acr(self):
        self.assertTrue(self.is_acr_registry("myregistry.azurecr.io"))

    def test_azurecr_io_with_path_is_acr(self):
        self.assertTrue(self.is_acr_registry("myregistry.azurecr.io/myimage:latest"))

    # US Government cloud (the original bug report)
    def test_azurecr_us_is_acr(self):
        self.assertTrue(self.is_acr_registry("myregistry.azurecr.us"))

    def test_azurecr_us_with_path_is_acr(self):
        self.assertTrue(self.is_acr_registry("myregistry.azurecr.us/myimage:latest"))

    # Azure China cloud
    def test_azurecr_cn_is_acr(self):
        self.assertTrue(self.is_acr_registry("myregistry.azurecr.cn"))

    def test_azurecr_cn_with_path_is_acr(self):
        self.assertTrue(self.is_acr_registry("myregistry.azurecr.cn/myimage:latest"))

    # Non-ACR registries should return False
    def test_dockerhub_is_not_acr(self):
        self.assertFalse(self.is_acr_registry("docker.io"))

    def test_dockerhub_image_is_not_acr(self):
        self.assertFalse(self.is_acr_registry("docker.io/library/nginx:latest"))

    def test_ghcr_is_not_acr(self):
        self.assertFalse(self.is_acr_registry("ghcr.io/myorg/myimage:latest"))

    def test_mcr_is_not_acr(self):
        self.assertFalse(self.is_acr_registry("mcr.microsoft.com/azure-cli:latest"))

    def test_custom_registry_is_not_acr(self):
        self.assertFalse(self.is_acr_registry("my-private-registry.example.com"))

    # Edge cases
    def test_none_is_not_acr(self):
        self.assertFalse(self.is_acr_registry(None))

    def test_empty_string_is_not_acr(self):
        self.assertFalse(self.is_acr_registry(""))

    def test_totally_fake_domain_is_not_acr(self):
        self.assertFalse(self.is_acr_registry("totally-fake-registry.com"))


if __name__ == '__main__':
    unittest.main()
