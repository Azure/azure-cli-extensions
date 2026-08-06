# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import ast
import os
import sys
import unittest


def load_function(function_name):
    """Load a function from custom.py without importing the full Azure CLI runtime."""
    custom_path = os.path.join(
        os.path.dirname(__file__), '..', '..', 'custom.py'
    )
    with open(custom_path, 'r') as f:
        source = f.read()
    tree = ast.parse(source)
    func_source = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            func_source = ast.get_source_segment(source, node)
            break
    if func_source is None:
        raise ValueError(f"Function {function_name!r} not found in custom.py")
    namespace = {}
    exec(compile(func_source, custom_path, 'exec'), namespace)  # pylint: disable=exec-used
    return namespace[function_name]


from enum import Enum


class BastionSkuStub(Enum):
    Basic = "Basic"
    Standard = "Standard"
    Developer = "Developer"
    QuickConnect = "QuickConnect"
    Premium = "Premium"


def _is_sku_standard_or_higher(sku):
    allowed_skus = {BastionSkuStub.Standard.value, BastionSkuStub.Premium.value}
    return sku in allowed_skus


def _make_is_nativeclient_enabled():
    """Return a version of _is_nativeclient_enabled that uses local stubs."""
    custom_path = os.path.join(
        os.path.dirname(__file__), '..', '..', 'custom.py'
    )
    with open(custom_path, 'r') as f:
        source = f.read()
    tree = ast.parse(source)
    func_source = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == '_is_nativeclient_enabled':
            func_source = ast.get_source_segment(source, node)
            break
    namespace = {
        'BastionSku': BastionSkuStub,
        '_is_sku_standard_or_higher': _is_sku_standard_or_higher,
    }
    exec(compile(func_source, custom_path, 'exec'), namespace)  # pylint: disable=exec-used
    return namespace['_is_nativeclient_enabled']


_is_nativeclient_enabled = _make_is_nativeclient_enabled()


class TestIsNativeclientEnabled(unittest.TestCase):

    def test_developer_sku_returns_true(self):
        bastion = {'sku': {'name': 'Developer'}}
        self.assertTrue(_is_nativeclient_enabled(bastion))

    def test_standard_sku_with_tunneling_enabled(self):
        bastion = {'sku': {'name': 'Standard'}, 'enableTunneling': True}
        self.assertTrue(_is_nativeclient_enabled(bastion))

    def test_standard_sku_with_tunneling_disabled(self):
        bastion = {'sku': {'name': 'Standard'}, 'enableTunneling': False}
        self.assertFalse(_is_nativeclient_enabled(bastion))

    def test_standard_sku_without_tunneling_key_does_not_raise(self):
        # Regression test: should not raise KeyError when enableTunneling is absent
        bastion = {'sku': {'name': 'Standard'}}
        self.assertFalse(_is_nativeclient_enabled(bastion))

    def test_premium_sku_with_tunneling_enabled(self):
        bastion = {'sku': {'name': 'Premium'}, 'enableTunneling': True}
        self.assertTrue(_is_nativeclient_enabled(bastion))

    def test_premium_sku_without_tunneling_key_does_not_raise(self):
        # Regression test: should not raise KeyError when enableTunneling is absent
        bastion = {'sku': {'name': 'Premium'}}
        self.assertFalse(_is_nativeclient_enabled(bastion))

    def test_basic_sku_returns_false(self):
        bastion = {'sku': {'name': 'Basic'}, 'enableTunneling': True}
        self.assertFalse(_is_nativeclient_enabled(bastion))


if __name__ == '__main__':
    unittest.main()
