# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile
import unittest
import yaml


class SimpleNamespace:
    """Minimal namespace mock for validator tests."""
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def _get_validate_test_id():
    """Import validate_test_id directly from validators module."""
    import ast
    import types

    validators_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "data_plane", "utils", "validators.py"
    )
    with open(validators_path, "r", encoding="UTF-8") as f:
        source = f.read()

    # Extract only the functions we need without the full module-level imports
    # by executing the full source in a sandboxed namespace with mocked imports
    import sys
    import re as re_mod

    mock_azure_error = type(
        "InvalidArgumentValueError", (Exception,), {}
    )
    mock_file_error = type("FileOperationError", (Exception,), {})

    class MockLogger:
        def debug(self, *a, **kw): pass
        def info(self, *a, **kw): pass
        def warning(self, *a, **kw): pass
        def error(self, *a, **kw): pass

    # Build fake modules to satisfy imports
    import types as types_mod

    def make_module(name, attrs=None):
        mod = types_mod.ModuleType(name)
        if attrs:
            for k, v in attrs.items():
                setattr(mod, k, v)
        return mod

    # Minimal stubs for modules used by validators
    azure_cli_core_azclierror = make_module(
        "azure.cli.core.azclierror",
        {"InvalidArgumentValueError": mock_azure_error,
         "FileOperationError": mock_file_error}
    )
    azure_cli_core_params = make_module(
        "azure.cli.core.commands.parameters",
        {"get_subscription_locations": lambda cmd: []}
    )
    azure_mgmt_core_tools = make_module(
        "azure.mgmt.core.tools",
        {"is_valid_resource_id": lambda rid: True}
    )

    # Import constants and models from real modules
    import importlib.util

    def import_from_path(mod_name, rel_path):
        full_path = os.path.normpath(os.path.join(
            os.path.dirname(validators_path), rel_path
        ))
        spec = importlib.util.spec_from_file_location(mod_name, full_path)
        mod = importlib.util.module_from_spec(spec)
        return mod, spec

    # We need constants and models available under .constants and .models
    constants_mod, constants_spec = import_from_path(
        "azext_load.data_plane.utils.constants",
        "constants.py"
    )
    # constants.py imports models.py
    models_path = os.path.normpath(os.path.join(
        os.path.dirname(validators_path), "models.py"
    ))
    models_spec_obj = importlib.util.spec_from_file_location(
        "azext_load.data_plane.utils.models", models_path
    )
    models_mod = importlib.util.module_from_spec(models_spec_obj)
    sys.modules["azext_load.data_plane.utils.models"] = models_mod
    models_spec_obj.loader.exec_module(models_mod)
    constants_spec.loader.exec_module(constants_mod)
    sys.modules["azext_load.data_plane.utils.constants"] = constants_mod

    # Stub out vendored sdk module
    vendored_stub = make_module(
        "azext_load.vendored_sdks.loadtesting.models",
        {
            "NotificationEventType": type("NotificationEventType", (), {}),
            "TestRunStatus": type("TestRunStatus", (), {}),
            "PassFailTestResult": type("PassFailTestResult", (), {}),
        }
    )
    sys.modules.setdefault(
        "azext_load.vendored_sdks.loadtesting.models", vendored_stub
    )

    # Stub utils (circular import avoidance)
    utils_stub = make_module(
        "azext_load.data_plane.utils.utils",
        {}
    )
    sys.modules.setdefault(
        "azext_load.data_plane.utils.utils", utils_stub
    )

    # Stub azure hierarchy
    for mod_name in [
        "azure", "azure.cli", "azure.cli.core",
        "azure.cli.core.azclierror", "azure.cli.core.commands",
        "azure.cli.core.commands.parameters",
        "azure.mgmt", "azure.mgmt.core", "azure.mgmt.core.tools",
    ]:
        sys.modules.setdefault(mod_name, make_module(mod_name))

    sys.modules["azure.cli.core.azclierror"] = azure_cli_core_azclierror
    sys.modules["azure.cli.core.commands.parameters"] = azure_cli_core_params
    sys.modules["azure.mgmt.core.tools"] = azure_mgmt_core_tools

    knack_log = make_module("knack.log", {"get_logger": lambda _: MockLogger()})
    sys.modules.setdefault("knack", make_module("knack"))
    sys.modules["knack.log"] = knack_log

    # Stub utils module inline so '.' imports work
    utils_inline = make_module(
        "azext_load.data_plane.utils",
        {"utils": utils_stub}
    )
    sys.modules.setdefault("azext_load.data_plane.utils", utils_inline)

    # Now load validators
    spec = importlib.util.spec_from_file_location(
        "azext_load.data_plane.utils.validators", validators_path
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    return mod.validate_test_id, mock_azure_error


class TestValidateTestIdFromYaml(unittest.TestCase):

    def setUp(self):
        self.validate_test_id, self.InvalidArgumentValueError = _get_validate_test_id()

    def _make_yaml_file(self, content):
        """Write YAML content to a temp file and return its path."""
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        )
        tmp.write(content)
        tmp.flush()
        tmp.close()
        return tmp.name

    def test_test_id_required_when_not_in_cli_or_yaml(self):
        """Error raised when test_id is absent from both CLI arg and YAML."""
        ns = SimpleNamespace(test_id=None)
        with self.assertRaises(self.InvalidArgumentValueError):
            self.validate_test_id(ns)

    def test_test_id_required_when_yaml_missing_key(self):
        """Error raised when YAML config file exists but has no testId key."""
        yaml_file = self._make_yaml_file("displayName: mytest\n")
        try:
            ns = SimpleNamespace(test_id=None, load_test_config_file=yaml_file)
            with self.assertRaises(self.InvalidArgumentValueError):
                self.validate_test_id(ns)
        finally:
            os.unlink(yaml_file)

    def test_test_id_read_from_yaml(self):
        """test_id is set from testId in YAML when CLI arg is absent."""
        yaml_content = "testId: my-yaml-test-id\ndisplayName: mytest\n"
        yaml_file = self._make_yaml_file(yaml_content)
        try:
            ns = SimpleNamespace(test_id=None, load_test_config_file=yaml_file)
            self.validate_test_id(ns)
            self.assertEqual(ns.test_id, "my-yaml-test-id")
        finally:
            os.unlink(yaml_file)

    def test_cli_test_id_takes_precedence_over_yaml(self):
        """CLI-provided test_id is used even when YAML also has testId."""
        yaml_content = "testId: yaml-test-id\ndisplayName: mytest\n"
        yaml_file = self._make_yaml_file(yaml_content)
        try:
            ns = SimpleNamespace(test_id="cli-test-id", load_test_config_file=yaml_file)
            self.validate_test_id(ns)
            self.assertEqual(ns.test_id, "cli-test-id")
        finally:
            os.unlink(yaml_file)

    def test_test_id_validates_format(self):
        """Invalid test_id value (uppercase) raises InvalidArgumentValueError."""
        yaml_content = "testId: InvalidTestID\n"
        yaml_file = self._make_yaml_file(yaml_content)
        try:
            ns = SimpleNamespace(test_id=None, load_test_config_file=yaml_file)
            with self.assertRaises(self.InvalidArgumentValueError):
                self.validate_test_id(ns)
        finally:
            os.unlink(yaml_file)

    def test_valid_cli_test_id_passes(self):
        """A valid CLI test_id passes validation without error."""
        ns = SimpleNamespace(test_id="valid-test-id-123")
        self.validate_test_id(ns)  # Should not raise
        self.assertEqual(ns.test_id, "valid-test-id-123")


if __name__ == "__main__":
    unittest.main()
