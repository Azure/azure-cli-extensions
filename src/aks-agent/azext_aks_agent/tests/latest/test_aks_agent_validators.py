# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# This test module was renamed to avoid name collision with 'acs' module tests.
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

import azext_aks_agent._validators as validators
from azure.cli.core.azclierror import InvalidArgumentValueError


class TestValidateParamYamlFile(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.valid_yaml_file = os.path.join(self.temp_dir, "valid.yaml")
        self.invalid_yaml_file = os.path.join(self.temp_dir, "invalid.yaml")
        self.readonly_yaml_file = os.path.join(self.temp_dir, "readonly.yaml")
        self.nonexistent_file = os.path.join(self.temp_dir, "nonexistent.yaml")

        # Create valid YAML file
        with open(self.valid_yaml_file, 'w') as f:
            f.write("key1: value1\nkey2:\n  - item1\n  - item2\n")

        # Create invalid YAML file
        with open(self.invalid_yaml_file, 'w') as f:
            f.write("invalid: yaml: content: [\n  - unclosed\n")

        # Create readonly YAML file
        with open(self.readonly_yaml_file, 'w') as f:
            f.write("key: value\n")
        os.chmod(self.readonly_yaml_file, 0o000)  # Remove all permissions

    def tearDown(self):
        # Restore permissions before cleanup
        if os.path.exists(self.readonly_yaml_file):
            os.chmod(self.readonly_yaml_file, 0o644)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_none_yaml_path(self):
        """Test that None yaml_path returns without error"""
        validators._validate_param_yaml_file(None, "config-file")

    def test_empty_yaml_path(self):
        """Test that empty string yaml_path returns without error"""
        validators._validate_param_yaml_file("", "config-file")

    def test_nonexistent_file(self):
        """Test that non-existent file raises InvalidArgumentValueError"""
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validators._validate_param_yaml_file(self.nonexistent_file, "config-file")
        self.assertIn("file is not found", str(cm.exception))
        self.assertIn("config-file", str(cm.exception))

    def test_unreadable_file(self):
        """Test that unreadable file raises InvalidArgumentValueError"""
        import os

        # Skip on Windows as it handles permissions differently
        if os.name == 'nt':
            self.skipTest("Skipping readonly test on Windows")

        with self.assertRaises(InvalidArgumentValueError) as cm:
            validators._validate_param_yaml_file(self.readonly_yaml_file, "config-file")
        self.assertIn("file is not readable", str(cm.exception))
        self.assertIn("config-file", str(cm.exception))

    def test_invalid_yaml_file(self):
        """Test that invalid YAML content raises InvalidArgumentValueError"""
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validators._validate_param_yaml_file(self.invalid_yaml_file, "config-file")
        self.assertIn("file is not a valid YAML file", str(cm.exception))
        self.assertIn("config-file", str(cm.exception))

    def test_valid_yaml_file(self):
        """Test that valid YAML file passes validation"""
        # Should not raise any exception
        validators._validate_param_yaml_file(self.valid_yaml_file, "config-file")

    def test_different_param_names(self):
        """Test that different parameter names are included in error messages"""
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validators._validate_param_yaml_file(self.nonexistent_file, "my-custom-param")
        self.assertIn("my-custom-param", str(cm.exception))

    @patch('builtins.open')
    def test_general_exception_handling(self, mock_open):
        """Test that general exceptions are caught and re-raised as InvalidArgumentValueError"""
        mock_open.side_effect = PermissionError("Access denied")

        with self.assertRaises(InvalidArgumentValueError) as cm:
            validators._validate_param_yaml_file(self.valid_yaml_file, "config-file")
        self.assertIn("An error occurred while reading the config file", str(cm.exception))
        self.assertIn("config-file", str(cm.exception))

    def test_complex_yaml_file(self):
        """Test validation with complex YAML structure"""
        import os
        complex_yaml_file = os.path.join(self.temp_dir, "complex.yaml")
        with open(complex_yaml_file, 'w') as f:
            f.write("""
apiVersion: v1
kind: ConfigMap
metadata:
  name: test-config
  namespace: default
data:
  config.yaml: |
    server:
      host: localhost
      port: 8080
    features:
      - auth
      - logging
    database:
      url: "postgresql://user:pass@host:5432/db"
      pool_size: 10
""")

        # Should not raise any exception
        validators._validate_param_yaml_file(complex_yaml_file, "config-file")

    def test_empty_yaml_file(self):
        """Test validation with empty YAML file"""
        import os
        empty_yaml_file = os.path.join(self.temp_dir, "empty.yaml")
        with open(empty_yaml_file, 'w') as f:
            f.write("")

        # Should not raise any exception - empty file is valid YAML
        validators._validate_param_yaml_file(empty_yaml_file, "config-file")


class AgentConfigFileNamespace:
    def __init__(self, config_file=None):
        self.config_file = config_file


class TestValidateAgentConfigFile(unittest.TestCase):
    def setUp(self):

        self.temp_dir = tempfile.mkdtemp()
        self.valid_yaml_file = os.path.join(self.temp_dir, "valid_agent.yaml")
        self.invalid_yaml_file = os.path.join(self.temp_dir, "invalid_agent.yaml")
        self.readonly_yaml_file = os.path.join(self.temp_dir, "readonly_agent.yaml")
        self.nonexistent_file = os.path.join(self.temp_dir, "nonexistent_agent.yaml")

        # Create valid YAML file
        with open(self.valid_yaml_file, 'w') as f:
            f.write("""
model=azure/gpt-4.1
""")

        # Create invalid YAML file
        with open(self.invalid_yaml_file, 'w') as f:
            f.write("invalid: yaml: content: [\n  - unclosed\n")

        # Create readonly YAML file
        with open(self.readonly_yaml_file, 'w') as f:
            f.write("agent:\n  config: test\n")
        os.chmod(self.readonly_yaml_file, 0o000)  # Remove all permissions

    def tearDown(self):
        import os
        import shutil

        # Restore permissions before cleanup
        if os.path.exists(self.readonly_yaml_file):
            os.chmod(self.readonly_yaml_file, 0o644)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_none_config_file(self):
        """Test that None config_file returns without error"""
        namespace = AgentConfigFileNamespace(None)
        validators.validate_agent_config_file(namespace)

    def test_empty_config_file(self):
        """Test that empty string config_file returns without error"""
        namespace = AgentConfigFileNamespace("")
        validators.validate_agent_config_file(namespace)

    def test_valid_config_file(self):
        """Test that valid YAML config file passes validation"""
        namespace = AgentConfigFileNamespace(self.valid_yaml_file)
        # Should not raise any exception
        validators.validate_agent_config_file(namespace)

    def test_invalid_yaml_config_file(self):
        """Test that invalid YAML config file raises InvalidArgumentValueError"""
        namespace = AgentConfigFileNamespace(self.invalid_yaml_file)
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validators.validate_agent_config_file(namespace)
        self.assertIn("file is not a valid YAML file", str(cm.exception))
        self.assertIn("config-file", str(cm.exception))

    def test_nonexistent_config_file(self):
        """Test that non-existent config file raises InvalidArgumentValueError"""
        namespace = AgentConfigFileNamespace(self.nonexistent_file)
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validators.validate_agent_config_file(namespace)
        self.assertIn("file is not found", str(cm.exception))
        self.assertIn("config-file", str(cm.exception))

    def test_unreadable_config_file(self):
        """Test that unreadable config file raises InvalidArgumentValueError"""
        import os

        # Skip on Windows as it handles permissions differently
        if os.name == 'nt':
            self.skipTest("Skipping readonly test on Windows")

        namespace = AgentConfigFileNamespace(self.readonly_yaml_file)
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validators.validate_agent_config_file(namespace)
        self.assertIn("file is not readable", str(cm.exception))
        self.assertIn("config-file", str(cm.exception))

    @patch('azext_aks_agent._validators.get_config_dir')
    @patch('azext_aks_agent._validators.os.path.exists')
    def test_default_config_path_nonexistent(self, mock_exists, mock_get_config_dir):
        """Test that default config path that doesn't exist returns without error"""
        mock_get_config_dir.return_value = "/home/user/.azure"
        mock_exists.return_value = False

        default_path = "/home/user/.azure/aksAgent.yaml"
        namespace = AgentConfigFileNamespace(default_path)

        # Should not raise any exception when default path doesn't exist
        validators.validate_agent_config_file(namespace)

    @patch('azext_aks_agent._validators.get_config_dir')
    def test_default_config_path_exists_valid(self, mock_get_config_dir):
        """Test that default config path with valid file passes validation"""
        mock_get_config_dir.return_value = self.temp_dir

        default_path = os.path.join(self.temp_dir, "aksAgent.yaml")
        # Create the default config file
        with open(default_path, 'w') as f:
            f.write("agent:\n  config: default\n")

        namespace = AgentConfigFileNamespace(default_path)
        # Should not raise any exception
        validators.validate_agent_config_file(namespace)

    @patch('azext_aks_agent._validators.get_config_dir')
    def test_default_config_path_exists_invalid(self, mock_get_config_dir):
        """Test that default config path with invalid file raises error"""
        mock_get_config_dir.return_value = self.temp_dir

        default_path = os.path.join(self.temp_dir, "aksAgent.yaml")
        # Create the default config file with invalid YAML
        with open(default_path, 'w') as f:
            f.write("invalid: yaml: [\n  unclosed\n")

        namespace = AgentConfigFileNamespace(default_path)
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validators.validate_agent_config_file(namespace)
        self.assertIn("file is not a valid YAML file", str(cm.exception))

    def test_empty_agent_config_file(self):
        """Test validation with empty agent config file"""
        import os
        empty_config_file = os.path.join(self.temp_dir, "empty_agent.yaml")
        with open(empty_config_file, 'w') as f:
            f.write("")

        namespace = AgentConfigFileNamespace(empty_config_file)
        # Should not raise any exception - empty file is valid YAML
        validators.validate_agent_config_file(namespace)

    @patch('builtins.open')
    def test_file_access_exception(self, mock_open):
        """Test that general file access exceptions are handled properly"""
        mock_open.side_effect = PermissionError("Access denied")

        namespace = AgentConfigFileNamespace(self.valid_yaml_file)
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validators.validate_agent_config_file(namespace)
        self.assertIn("An error occurred while reading the config file", str(cm.exception))
        self.assertIn("config-file", str(cm.exception))

    def test_minimal_valid_agent_config(self):
        """Test validation with minimal valid agent configuration"""
        import os
        minimal_config_file = os.path.join(self.temp_dir, "minimal_agent.yaml")
        with open(minimal_config_file, 'w') as f:
            f.write("agent: {}")

        namespace = AgentConfigFileNamespace(minimal_config_file)
        # Should not raise any exception
        validators.validate_agent_config_file(namespace)


if __name__ == "__main__":
    unittest.main()
