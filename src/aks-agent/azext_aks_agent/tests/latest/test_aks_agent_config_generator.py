# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from azext_aks_agent.agent.config_generator import ConfigurationGenerator


class TestConfigurationGenerator(unittest.TestCase):
    """Test cases for ConfigurationGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_config = {
            "model": "gpt-4",
            "api_key": "test-key",
            "max_steps": 10,
            "toolsets": {
                "some-custom-toolset": {"enabled": True}
            },
            "other_setting": "value"
        }
        
        self.server_url = "http://localhost:8003/sse"

    def test_generate_mcp_config_basic(self):
        """Test basic MCP configuration generation."""
        result = ConfigurationGenerator.generate_mcp_config(self.base_config, self.server_url)
        
        # Should preserve base config
        self.assertEqual(result["model"], "gpt-4")
        self.assertEqual(result["api_key"], "test-key")
        self.assertEqual(result["max_steps"], 10)
        self.assertEqual(result["other_setting"], "value")
        
        # Should add MCP server configuration
        self.assertIn("mcp_servers", result)
        self.assertIn("aks-mcp", result["mcp_servers"])
        
        aks_mcp = result["mcp_servers"]["aks-mcp"]
        self.assertEqual(aks_mcp["description"], "AKS MCP server")
        self.assertEqual(aks_mcp["url"], self.server_url)
        
        # Should disable conflicting toolsets
        toolsets = result["toolsets"]
        self.assertFalse(toolsets["aks/node-health"]["enabled"])
        self.assertFalse(toolsets["aks/core"]["enabled"])
        self.assertFalse(toolsets["kubernetes/core"]["enabled"])
        self.assertFalse(toolsets["kubernetes/logs"]["enabled"])
        self.assertFalse(toolsets["kubernetes/live-metrics"]["enabled"])
        self.assertFalse(toolsets["bash"]["enabled"])
        
        # Should preserve custom toolsets
        self.assertTrue(toolsets["some-custom-toolset"]["enabled"])

    def test_generate_mcp_config_empty_base(self):
        """Test MCP configuration generation with empty base config."""
        result = ConfigurationGenerator.generate_mcp_config({}, self.server_url)
        
        # Should create MCP server configuration
        self.assertIn("mcp_servers", result)
        self.assertIn("aks-mcp", result["mcp_servers"])
        
        # Should create toolsets configuration
        self.assertIn("toolsets", result)
        for toolset_name in ConfigurationGenerator.DEFAULT_CONFLICTING_TOOLSETS:
            self.assertIn(toolset_name, result["toolsets"])
            self.assertFalse(result["toolsets"][toolset_name]["enabled"])

    def test_generate_mcp_config_none_base(self):
        """Test MCP configuration generation with None base config."""
        result = ConfigurationGenerator.generate_mcp_config(None, self.server_url)
        
        # Should handle None gracefully
        self.assertIn("mcp_servers", result)
        self.assertIn("toolsets", result)

    def test_generate_mcp_config_invalid_server_url(self):
        """Test MCP configuration generation with invalid server URL."""
        with self.assertRaises(ValueError):
            ConfigurationGenerator.generate_mcp_config(self.base_config, "")
            
        with self.assertRaises(ValueError):
            ConfigurationGenerator.generate_mcp_config(self.base_config, None)

    def test_generate_mcp_config_preserves_original(self):
        """Test that MCP config generation doesn't modify original config."""
        original_toolsets_count = len(self.base_config["toolsets"])
        
        result = ConfigurationGenerator.generate_mcp_config(self.base_config, self.server_url)
        
        # Original should be unchanged
        self.assertEqual(len(self.base_config["toolsets"]), original_toolsets_count)
        self.assertNotIn("mcp_servers", self.base_config)
        
        # Result should be different
        self.assertGreater(len(result["toolsets"]), original_toolsets_count)
        self.assertIn("mcp_servers", result)

    def test_generate_traditional_config_basic(self):
        """Test basic traditional configuration generation."""
        result = ConfigurationGenerator.generate_traditional_config(self.base_config)
        
        # Should preserve base config
        self.assertEqual(result["model"], "gpt-4")
        self.assertEqual(result["api_key"], "test-key")
        self.assertEqual(result["max_steps"], 10)
        self.assertEqual(result["other_setting"], "value")
        
        # Should not have MCP servers
        self.assertNotIn("mcp_servers", result)
        
        # Should enable all default toolsets
        toolsets = result["toolsets"]
        for toolset_name, toolset_cfg in ConfigurationGenerator.DEFAULT_CONFLICTING_TOOLSETS.items():
            self.assertTrue(toolset_name in toolsets)
            self.assertTrue(toolsets[toolset_name]["enabled"])  # enabled True

    def test_generate_traditional_config_removes_mcp(self):
        """Traditional config should remove any mcp_servers section."""
        base_with_mcp = dict(self.base_config)
        base_with_mcp["mcp_servers"] = {"some-server": {"url": "test"}}
        
        result = ConfigurationGenerator.generate_traditional_config(base_with_mcp)
        
        # Should remove MCP servers
        self.assertNotIn("mcp_servers", result)

    def test_generate_traditional_config_empty_base(self):
        """Test traditional configuration generation with empty base config."""
        result = ConfigurationGenerator.generate_traditional_config({})
        
        # Should create toolsets configuration
        self.assertIn("toolsets", result)
        for toolset_name in ConfigurationGenerator.DEFAULT_CONFLICTING_TOOLSETS:
            self.assertTrue(result["toolsets"][toolset_name]["enabled"])

    def test_generate_traditional_config_none_base(self):
        """Test traditional configuration generation with None base config."""
        result = ConfigurationGenerator.generate_traditional_config(None)
        
        # Should handle None gracefully
        self.assertIn("toolsets", result)

    def test_merge_configs_basic(self):
        """Test basic configuration merging."""
        base = {"a": 1, "b": {"x": 10, "y": 20}, "c": 3}
        override = {"b": {"y": 25, "z": 30}, "d": 4}
        
        result = ConfigurationGenerator.merge_configs(base, override)
        
        # Should merge properly
        self.assertEqual(result["a"], 1)  # From base
        self.assertEqual(result["c"], 3)  # From base
        self.assertEqual(result["d"], 4)  # From override
        
        # Nested merge
        self.assertEqual(result["b"]["x"], 10)  # From base
        self.assertEqual(result["b"]["y"], 25)  # From override
        self.assertEqual(result["b"]["z"], 30)  # From override

    def test_merge_configs_empty_inputs(self):
        """Test configuration merging with empty inputs."""
        base = {"a": 1}
        
        # Empty override
        result = ConfigurationGenerator.merge_configs(base, {})
        self.assertEqual(result, base)
        
        # Empty base
        result = ConfigurationGenerator.merge_configs({}, base)
        self.assertEqual(result, base)
        
        # Both empty
        result = ConfigurationGenerator.merge_configs({}, {})
        self.assertEqual(result, {})
        
        # None inputs
        result = ConfigurationGenerator.merge_configs(None, base)
        self.assertEqual(result, base)
        
        result = ConfigurationGenerator.merge_configs(base, None)
        self.assertEqual(result, base)
        
        result = ConfigurationGenerator.merge_configs(None, None)
        self.assertEqual(result, {})

    def test_merge_configs_preserves_originals(self):
        """Test that merging doesn't modify original configs."""
        base = {"a": 1, "b": {"x": 10}}
        override = {"b": {"y": 20}}
        
        original_base = dict(base)
        original_override = dict(override)
        
        result = ConfigurationGenerator.merge_configs(base, override)
        
        # Originals should be unchanged
        self.assertEqual(base, original_base)
        self.assertEqual(override, original_override)
        
        # Result should be different
        self.assertNotEqual(result, base)
        self.assertNotEqual(result, override)

    def test_validate_mcp_config_valid(self):
        """Test validation of valid MCP configuration."""
        config = ConfigurationGenerator.generate_mcp_config(self.base_config, self.server_url)
        self.assertTrue(ConfigurationGenerator.validate_mcp_config(config))

    def test_validate_mcp_config_invalid_structure(self):
        """Test validation of invalid MCP configuration structures."""
        # Not a dictionary
        self.assertFalse(ConfigurationGenerator.validate_mcp_config("invalid"))
        self.assertFalse(ConfigurationGenerator.validate_mcp_config(None))
        
        # Missing mcp_servers
        config = {"toolsets": {}}
        self.assertFalse(ConfigurationGenerator.validate_mcp_config(config))
        
        # Invalid mcp_servers structure
        config = {"mcp_servers": "invalid"}
        self.assertFalse(ConfigurationGenerator.validate_mcp_config(config))
        
        # Missing aks-mcp server
        config = {"mcp_servers": {"other-server": {}}}
        self.assertFalse(ConfigurationGenerator.validate_mcp_config(config))

    def test_validate_mcp_config_missing_required_fields(self):
        """Test validation with missing required MCP server fields."""
        base_mcp_server = {
            "description": "AKS MCP server",
            "url": "http://localhost:8003/sse"
        }
        
        # Test each required field
        required_fields = ["description", "url"]
        for field in required_fields:
            incomplete_server = dict(base_mcp_server)
            del incomplete_server[field]
            
            config = {
                "mcp_servers": {"aks-mcp": incomplete_server},
                "toolsets": {name: {"enabled": False} for name in ConfigurationGenerator.DEFAULT_CONFLICTING_TOOLSETS}
            }
            
            self.assertFalse(ConfigurationGenerator.validate_mcp_config(config), 
                           f"Should fail validation when missing {field}")

    def test_validate_mcp_config_enabled_conflicting_toolsets(self):
        """Test validation fails with enabled conflicting toolsets."""
        config = {
            "mcp_servers": {
                "aks-mcp": {
                    "description": "AKS MCP server",
                    "url": "http://localhost:8003/sse"
                }
            },
            "toolsets": {
                "aks/core": {"enabled": True}
            }
        }
        
        self.assertFalse(ConfigurationGenerator.validate_mcp_config(config))

    def test_validate_traditional_config_valid(self):
        """Test validation of valid traditional configuration."""
        config = ConfigurationGenerator.generate_traditional_config(self.base_config)
        self.assertTrue(ConfigurationGenerator.validate_traditional_config(config))

    def test_validate_traditional_config_invalid_structure(self):
        """Test validation of invalid traditional configuration structures."""
        # Not a dictionary
        self.assertFalse(ConfigurationGenerator.validate_traditional_config("invalid"))
        self.assertFalse(ConfigurationGenerator.validate_traditional_config(None))

    def test_validate_traditional_config_with_mcp_servers(self):
        """Test validation fails for traditional config with MCP servers."""
        config = {
            "mcp_servers": {"aks-mcp": {"url": "test"}},
            "toolsets": {name: {"enabled": True} for name in ConfigurationGenerator.DEFAULT_CONFLICTING_TOOLSETS}
        }
        
        self.assertFalse(ConfigurationGenerator.validate_traditional_config(config))

    def test_validate_traditional_config_disabled_toolsets(self):
        """Test validation fails for traditional config with disabled required toolsets."""
        config = {
            "toolsets": {
                "aks/core": {"enabled": False}
            }
        }
        
        self.assertFalse(ConfigurationGenerator.validate_traditional_config(config))


if __name__ == '__main__':
    unittest.main()
