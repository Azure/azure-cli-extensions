# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import yaml
from azext_aks_agent.agent.llm_config_manager import LLMConfigManager
from azure.cli.core.azclierror import AzCLIError


class TestLLMConfigManager(unittest.TestCase):
    """Test cases for LLMConfigManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.yaml")
        self.manager = LLMConfigManager()
        self.manager.config_path = self.config_file

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.config_file):
            os.unlink(self.config_file)
        os.rmdir(self.temp_dir)

    def test_save_new_config(self):
        """Test saving a new configuration when file doesn't exist."""
        config = {
            "MODEL_NAME": "gpt-4",
            "OPENAI_API_KEY": "test-key",
            "OPENAI_API_BASE": "https://api.openai.com/v1"
        }

        self.manager.save("openai", config)

        # Verify file was created and contains correct data
        self.assertTrue(os.path.exists(self.config_file))
        with open(self.config_file, 'r') as f:
            data = yaml.safe_load(f)

        self.assertIn("llms", data)
        self.assertEqual(len(data["llms"]), 1)
        expected_config = {"provider": "openai", **config}
        self.assertEqual(data["llms"][0], expected_config)

    def test_save_append_to_existing_config(self):
        """Test saving a configuration to an existing file."""
        # Create initial config
        initial_config = {
            "provider": "azure",
            "MODEL_NAME": "gpt-3.5",
            "AZURE_OPENAI_API_KEY": "initial-key"
        }
        initial_data = {"llms": [initial_config]}

        with open(self.config_file, 'w') as f:
            yaml.safe_dump(initial_data, f)

        # Add new config
        new_config = {
            "MODEL_NAME": "gpt-4",
            "OPENAI_API_KEY": "new-key"
        }

        self.manager.save("openai", new_config)

        # Verify both configs exist
        with open(self.config_file, 'r') as f:
            data = yaml.safe_load(f)

        self.assertEqual(len(data["llms"]), 2)
        self.assertEqual(data["llms"][0], initial_config)
        expected_new_config = {"provider": "openai", **new_config}
        self.assertEqual(data["llms"][1], expected_new_config)

    def test_save_creates_llms_key_if_missing(self):
        """Test that save creates 'llms' key if config file exists but is malformed."""
        # Create config file without 'llms' key
        malformed_data = {"other_key": "value"}
        with open(self.config_file, 'w') as f:
            yaml.safe_dump(malformed_data, f)

        config = {"MODEL_NAME": "gpt-4"}
        self.manager.save("openai", config)

        with open(self.config_file, 'r') as f:
            data = yaml.safe_load(f)

        self.assertIn("llms", data)
        self.assertEqual(len(data["llms"]), 1)
        expected_config = {"provider": "openai", **config}
        self.assertEqual(data["llms"][0], expected_config)

    @patch("builtins.open", side_effect=IOError("Permission denied"))
    def test_save_handles_file_write_error(self, mock_file):
        """Test that save handles file write errors gracefully."""
        config = {"MODEL_NAME": "gpt-4"}

        with self.assertRaises(IOError):
            self.manager.save("openai", config)

    def test_load_existing_file(self):
        """Test loading configurations from an existing file."""
        configs = [
            {"provider": "openai", "MODEL_NAME": "gpt-4"},
            {"provider": "azure", "MODEL_NAME": "gpt-3.5"}
        ]
        data = {"llms": configs}

        with open(self.config_file, 'w') as f:
            yaml.safe_dump(data, f)

        result = self.manager.load()
        self.assertEqual(result, data)

    def test_load_handles_invalid_yaml(self):
        """Test that load handles invalid YAML content."""
        # Write invalid YAML
        with open(self.config_file, 'w') as f:
            f.write("invalid: yaml: content: {\n")

        with self.assertRaises(yaml.YAMLError):
            self.manager.load()

    def test_get_list_with_configs(self):
        """Test get_list returns list of configurations."""
        configs = [
            {"provider": "openai", "MODEL_NAME": "gpt-4"},
            {"provider": "azure", "MODEL_NAME": "gpt-3.5"}
        ]
        data = {"llms": configs}

        with open(self.config_file, 'w') as f:
            yaml.safe_dump(data, f)

        result = self.manager.get_list()
        self.assertEqual(result, configs)

    def test_get_list_empty_file(self):
        """Test get_list returns empty list when no configs exist."""
        result = self.manager.get_list()
        self.assertEqual(result, [])

    def test_get_list_missing_llms_key(self):
        """Test get_list handles missing 'llms' key gracefully."""
        data = {"other_key": "value"}
        with open(self.config_file, 'w') as f:
            yaml.safe_dump(data, f)

        result = self.manager.get_list()
        self.assertEqual(result, [])

    def test_get_latest_with_configs(self):
        """Test get_latest returns the most recent configuration."""
        configs = [
            {"provider": "openai", "MODEL_NAME": "gpt-3.5"},
            {"provider": "azure", "MODEL_NAME": "gpt-4"}
        ]
        data = {"llms": configs}

        with open(self.config_file, 'w') as f:
            yaml.safe_dump(data, f)

        result = self.manager.get_latest()
        self.assertEqual(result, configs[-1])  # Should return last config

    def test_get_latest_no_configs(self):
        """Test get_latest returns None when no configurations exist."""
        result = self.manager.get_latest()
        self.assertIsNone(result)

    def test_get_specific_found(self):
        """Test get_specific returns correct config when found."""
        configs = [
            {"provider": "openai", "MODEL_NAME": "gpt-3.5"},
            {"provider": "azure", "MODEL_NAME": "gpt-4"},
            {"provider": "openai", "MODEL_NAME": "gpt-4"}
        ]
        data = {"llms": configs}

        with open(self.config_file, 'w') as f:
            yaml.safe_dump(data, f)

        result = self.manager.get_specific("openai", "gpt-4")
        self.assertEqual(result, configs[2])

    def test_get_specific_not_found(self):
        """Test get_specific returns None when config not found."""
        configs = [
            {"provider": "openai", "MODEL_NAME": "gpt-3.5"},
            {"provider": "azure", "MODEL_NAME": "gpt-4"}
        ]
        data = {"llms": configs}

        with open(self.config_file, 'w') as f:
            yaml.safe_dump(data, f)

        result = self.manager.get_specific("openai", "gpt-4")
        self.assertIsNone(result)

    def test_get_model_config_no_model_param_with_configs(self):
        """Test get_model_config returns latest when no model specified."""
        configs = [
            {"provider": "openai", "MODEL_NAME": "gpt-3.5"},
            {"provider": "azure", "MODEL_NAME": "gpt-4"}
        ]
        data = {"llms": configs}

        with open(self.config_file, 'w') as f:
            yaml.safe_dump(data, f)

        result = self.manager.get_model_config(None)
        self.assertEqual(result, configs[-1])

    def test_get_model_config_no_model_param_no_configs(self):
        """Test get_model_config raises error when no model and no configs."""
        with self.assertRaises(AzCLIError) as cm:
            self.manager.get_model_config(None)

        self.assertIn("No LLM configurations found", str(cm.exception))
        self.assertIn("az aks agent-init", str(cm.exception))

    def test_get_model_config_with_provider_model(self):
        """Test get_model_config with provider/model format."""
        configs = [
            {"provider": "openai", "MODEL_NAME": "gpt-3.5"},
            {"provider": "azure", "MODEL_NAME": "gpt-4"}
        ]
        data = {"llms": configs}

        with open(self.config_file, 'w') as f:
            yaml.safe_dump(data, f)

        result = self.manager.get_model_config("azure/gpt-4")
        self.assertEqual(result, configs[1])

    def test_get_model_config_with_model_only(self):
        """Test get_model_config with model only (defaults to openai)."""
        configs = [
            {"provider": "openai", "MODEL_NAME": "gpt-4"},
            {"provider": "azure", "MODEL_NAME": "gpt-4"}
        ]
        data = {"llms": configs}

        with open(self.config_file, 'w') as f:
            yaml.safe_dump(data, f)

        result = self.manager.get_model_config("gpt-4")
        self.assertEqual(result, configs[0])  # Should find openai provider

    def test_get_model_config_model_not_found(self):
        """Test get_model_config raises error when specified model not found."""
        configs = [
            {"provider": "openai", "MODEL_NAME": "gpt-3.5"}
        ]
        data = {"llms": configs}

        with open(self.config_file, 'w') as f:
            yaml.safe_dump(data, f)

        with self.assertRaises(AzCLIError) as cm:
            self.manager.get_model_config("azure/gpt-4")

        self.assertIn("No configuration found for model 'azure/gpt-4'", str(cm.exception))

    def test_is_config_complete_all_valid(self):
        """Test is_config_complete returns True when all validations pass."""
        config = {
            "OPENAI_API_KEY": "test-key",
            "MODEL_NAME": "gpt-4"
        }

        provider_schema = {
            "OPENAI_API_KEY": {"validator": lambda x: x and len(x) > 0},
            "MODEL_NAME": {"validator": lambda x: x and len(x) > 0}
        }

        result = self.manager.is_config_complete(config, provider_schema)
        self.assertTrue(result)

    def test_is_config_complete_missing_key(self):
        """Test is_config_complete returns False when required key is missing."""
        config = {
            "OPENAI_API_KEY": "test-key"
            # Missing MODEL_NAME
        }

        provider_schema = {
            "OPENAI_API_KEY": {"validator": lambda x: x and len(x) > 0},
            "MODEL_NAME": {"validator": lambda x: x and len(x) > 0}
        }

        result = self.manager.is_config_complete(config, provider_schema)
        self.assertFalse(result)

    def test_is_config_complete_invalid_value(self):
        """Test is_config_complete returns False when validation fails."""
        config = {
            "OPENAI_API_KEY": "",  # Empty string should fail validation
            "MODEL_NAME": "gpt-4"
        }

        provider_schema = {
            "OPENAI_API_KEY": {"validator": lambda x: x and len(x) > 0},
            "MODEL_NAME": {"validator": lambda x: x and len(x) > 0}
        }

        result = self.manager.is_config_complete(config, provider_schema)
        self.assertFalse(result)

    def test_is_config_complete_no_validator(self):
        """Test is_config_complete skips keys without validators."""
        config = {
            "OPENAI_API_KEY": "test-key",
            "MODEL_NAME": "gpt-4"
        }

        provider_schema = {
            "OPENAI_API_KEY": {},  # No validator
            "MODEL_NAME": {"validator": lambda x: x and len(x) > 0}
        }

        result = self.manager.is_config_complete(config, provider_schema)
        self.assertTrue(result)

    def test_validate_config_valid_structure(self):
        """Test validate_config with valid YAML structure."""
        valid_config = {
            "llms": [
                {"provider": "openai", "MODEL_NAME": "gpt-4"}
            ]
        }

        # Write valid config to file
        with open(self.config_file, 'w') as f:
            yaml.safe_dump(valid_config, f)

        # Should not raise any exception
        self.manager.validate_config()

    def test_validate_config_missing_llms_key(self):
        """Test validate_config raises error when 'llms' key is missing."""
        invalid_config = {
            "other_key": "value"
        }

        # Write invalid config to file
        with open(self.config_file, 'w') as f:
            yaml.safe_dump(invalid_config, f)

        with self.assertRaises(ValueError) as cm:
            self.manager.validate_config()

        self.assertIn("must contain an 'llms' key", str(cm.exception))

    def test_validate_config_llms_not_list(self):
        """Test validate_config raises error when 'llms' is not a list."""
        invalid_config = {
            "llms": "not a list"
        }

        # Write invalid config to file
        with open(self.config_file, 'w') as f:
            yaml.safe_dump(invalid_config, f)

        with self.assertRaises(ValueError) as cm:
            self.manager.validate_config()

        self.assertIn("'llms' must be a list", str(cm.exception))

    def test_validate_config_empty_llms_list(self):
        """Test validate_config raises error when llms list is empty."""
        invalid_config = {
            "llms": []
        }

        # Write config with empty llms list to file
        with open(self.config_file, 'w') as f:
            yaml.safe_dump(invalid_config, f)

        with self.assertRaises(ValueError) as cm:
            self.manager.validate_config()

        self.assertIn("'llms' list cannot be empty", str(cm.exception))

    def test_validate_config_file_not_found(self):
        """Test validate_config raises error when config file doesn't exist."""
        # Don't create the config file, so it doesn't exist
        with self.assertRaises(ValueError) as cm:
            self.manager.validate_config()

        self.assertIn("Configuration file", str(cm.exception))
        self.assertIn("not found", str(cm.exception))

    def test_validate_config_invalid_yaml(self):
        """Test validate_config raises error for invalid YAML syntax."""
        # Write invalid YAML to file
        with open(self.config_file, 'w') as f:
            f.write("invalid: yaml: content: {\n")

        with self.assertRaises(ValueError) as cm:
            self.manager.validate_config()

        self.assertIn("Invalid YAML syntax", str(cm.exception))

    def test_validate_config_not_dict(self):
        """Test validate_config raises error when config is not a dictionary."""
        # Write a list instead of dict to file
        with open(self.config_file, 'w') as f:
            yaml.safe_dump(["not", "a", "dict"], f)

        with self.assertRaises(ValueError) as cm:
            self.manager.validate_config()

        self.assertIn("must contain a YAML dictionary/mapping", str(cm.exception))

    def test_validate_config_llm_not_dict(self):
        """Test validate_config raises error when LLM config is not a dictionary."""
        invalid_config = {
            "llms": ["not a dict"]
        }

        # Write config with non-dict LLM config to file
        with open(self.config_file, 'w') as f:
            yaml.safe_dump(invalid_config, f)

        with self.assertRaises(ValueError) as cm:
            self.manager.validate_config()

        self.assertIn("each LLM configuration must be a dictionary/mapping", str(cm.exception))

    @patch("azext_aks_agent.agent.llm_config_manager.get_config_dir")
    def test_validate_config_skips_default_config_path(self, mock_get_config_dir):
        """Test validate_config skips validation for default config path."""
        from azext_aks_agent._consts import CONST_AGENT_CONFIG_FILE_NAME

        # Mock the config directory to match our test setup
        mock_get_config_dir.return_value = self.temp_dir

        # Set the manager to use the default config path
        default_config_path = os.path.join(self.temp_dir, CONST_AGENT_CONFIG_FILE_NAME)
        self.manager.config_path = default_config_path

        # Don't create the file - validation should be skipped for default path
        # Should not raise any exception
        self.manager.validate_config()

    def test_save_new_configuration(self):
        """Test save method with new configuration."""
        provider_name = "openai"
        params = {
            "MODEL_NAME": "gpt-4",
            "OPENAI_API_KEY": "test-key-123"
        }

        self.manager.save(provider_name, params)

        # Verify the configuration was saved
        with open(self.config_file, 'r') as f:
            saved_config = yaml.safe_load(f)

        self.assertIn("llms", saved_config)
        self.assertEqual(len(saved_config["llms"]), 1)

        saved_llm = saved_config["llms"][0]
        self.assertEqual(saved_llm["provider"], provider_name)
        self.assertEqual(saved_llm["MODEL_NAME"], "gpt-4")
        self.assertEqual(saved_llm["OPENAI_API_KEY"], "test-key-123")

    def test_save_update_existing_configuration(self):
        """Test save method updates existing configuration."""
        # First save
        provider_name = "openai"
        initial_params = {
            "MODEL_NAME": "gpt-3.5-turbo",
            "OPENAI_API_KEY": "old-key"
        }
        self.manager.save(provider_name, initial_params)

        # Update with same model name
        updated_params = {
            "MODEL_NAME": "gpt-3.5-turbo",
            "OPENAI_API_KEY": "new-key"
        }
        self.manager.save(provider_name, updated_params)

        # Verify only one configuration exists and it's updated
        with open(self.config_file, 'r') as f:
            saved_config = yaml.safe_load(f)

        self.assertEqual(len(saved_config["llms"]), 1)
        saved_llm = saved_config["llms"][0]
        self.assertEqual(saved_llm["OPENAI_API_KEY"], "new-key")

    def test_save_azure_provider_uses_deployment_name(self):
        """Test save method with Azure provider uses DEPLOYMENT_NAME."""
        provider_name = "azure"
        params = {
            "DEPLOYMENT_NAME": "my-gpt-4-deployment",
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
            "AZURE_OPENAI_API_KEY": "azure-key"
        }

        self.manager.save(provider_name, params)

        with open(self.config_file, 'r') as f:
            saved_config = yaml.safe_load(f)

        saved_llm = saved_config["llms"][0]
        self.assertEqual(saved_llm["provider"], "azure")
        self.assertEqual(saved_llm["DEPLOYMENT_NAME"], "my-gpt-4-deployment")

    def test_save_azure_converts_model_name_to_deployment_name(self):
        """Test save method converts MODEL_NAME to DEPLOYMENT_NAME for Azure."""
        # Setup existing config with MODEL_NAME
        existing_config = {
            "llms": [{
                "provider": "azure",
                "MODEL_NAME": "gpt-4",
                "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com"
            }]
        }
        with open(self.config_file, 'w') as f:
            yaml.safe_dump(existing_config, f)

        # Save new Azure config
        provider_name = "azure"
        params = {
            "DEPLOYMENT_NAME": "new-deployment",
            "AZURE_OPENAI_ENDPOINT": "https://test2.openai.azure.com"
        }
        self.manager.save(provider_name, params)

        with open(self.config_file, 'r') as f:
            saved_config = yaml.safe_load(f)

        # Verify existing config was converted and new one added
        self.assertEqual(len(saved_config["llms"]), 2)

        # First config should have DEPLOYMENT_NAME now
        first_llm = saved_config["llms"][0]
        self.assertNotIn("MODEL_NAME", first_llm)
        self.assertIn("DEPLOYMENT_NAME", first_llm)
        self.assertEqual(first_llm["DEPLOYMENT_NAME"], "gpt-4")

    def test_save_missing_model_name_raises_error(self):
        """Test save method raises error when MODEL_NAME is missing for non-Azure provider."""
        provider_name = "openai"
        params = {
            "OPENAI_API_KEY": "test-key"
            # Missing MODEL_NAME
        }

        with self.assertRaises(ValueError) as cm:
            self.manager.save(provider_name, params)

        self.assertIn("MODEL_NAME is required", str(cm.exception))

    def test_save_missing_deployment_name_raises_error(self):
        """Test save method raises error when DEPLOYMENT_NAME is missing for Azure provider."""
        provider_name = "azure"
        params = {
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
            "AZURE_OPENAI_API_KEY": "test-key"
            # Missing DEPLOYMENT_NAME
        }

        with self.assertRaises(ValueError) as cm:
            self.manager.save(provider_name, params)

        self.assertIn("DEPLOYMENT_NAME is required", str(cm.exception))

    def test_save_appends_new_model_to_existing_list(self):
        """Test save method appends new model to existing list."""
        # Setup existing config
        existing_config = {
            "llms": [{
                "provider": "openai",
                "MODEL_NAME": "gpt-3.5-turbo",
                "OPENAI_API_KEY": "key1"
            }]
        }
        with open(self.config_file, 'w') as f:
            yaml.safe_dump(existing_config, f)

        # Add different model
        provider_name = "openai"
        params = {
            "MODEL_NAME": "gpt-4",
            "OPENAI_API_KEY": "key2"
        }
        self.manager.save(provider_name, params)

        with open(self.config_file, 'r') as f:
            saved_config = yaml.safe_load(f)

        # Should have both models
        self.assertEqual(len(saved_config["llms"]), 2)
        models = [llm["MODEL_NAME"] for llm in saved_config["llms"]]
        self.assertIn("gpt-3.5-turbo", models)
        self.assertIn("gpt-4", models)

    def test_save_handles_empty_config_file(self):
        """Test save method handles empty config file."""
        # Create empty config file
        with open(self.config_file, 'w') as f:
            f.write("")

        provider_name = "openai"
        params = {
            "MODEL_NAME": "gpt-4",
            "OPENAI_API_KEY": "test-key"
        }

        self.manager.save(provider_name, params)

        with open(self.config_file, 'r') as f:
            saved_config = yaml.safe_load(f)

        self.assertIn("llms", saved_config)
        self.assertEqual(len(saved_config["llms"]), 1)

    @patch("azext_aks_agent.agent.llm_config_manager.PROVIDER_REGISTRY")
    @patch("azext_aks_agent.agent.llm_config_manager.os.environ", new_callable=dict)
    def test_export_model_config_sets_environment_variables(self, mock_environ, mock_registry):
        """Test export_model_config sets environment variables."""
        # Mock provider
        mock_provider_instance = MagicMock()
        mock_provider_instance.model_name.return_value = "test-model"
        mock_provider = MagicMock(return_value=mock_provider_instance)
        mock_registry.get.return_value = mock_provider

        llm_config = {
            "provider": "openai",
            "MODEL_NAME": "gpt-4",
            "OPENAI_API_KEY": "test-key",
        }

        with patch("azext_aks_agent.agent.llm_config_manager.logger") as mock_logger:
            result = self.manager.export_model_config(llm_config)

        # Verify environment variables were set
        self.assertEqual(mock_environ["OPENAI_API_KEY"], "test-key")
        self.assertEqual("MODEL_NAME", mock_environ)
        self.assertNotIn("provider", mock_environ)

        # Verify provider was called correctly
        mock_registry.get.assert_called_once_with("openai")
        mock_provider_instance.model_name.assert_called_once_with("gpt-4")

        # Verify logging
        mock_logger.info.assert_called_once()

        self.assertEqual(result, "test-model")

    @patch("azext_aks_agent.agent.llm_config_manager.PROVIDER_REGISTRY")
    @patch("azext_aks_agent.agent.llm_config_manager.os.environ", new_callable=dict)
    def test_export_model_config_azure_converts_model_name(self, mock_environ, mock_registry):
        """Test export_model_config converts MODEL_NAME to DEPLOYMENT_NAME for Azure."""
        # Mock provider
        mock_provider_instance = MagicMock()
        mock_provider_instance.model_name.return_value = "azure-model"
        mock_provider = MagicMock(return_value=mock_provider_instance)
        mock_registry.get.return_value = mock_provider

        llm_config = {
            "provider": "azure",
            "MODEL_NAME": "gpt-4-legacy",  # This should be converted
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
            "AZURE_OPENAI_API_KEY": "azure-key"
        }

        with patch("azext_aks_agent.agent.llm_config_manager.logger"):
            result = self.manager.export_model_config(llm_config)

        # Verify MODEL_NAME was converted to DEPLOYMENT_NAME
        self.assertNotIn("MODEL_NAME", llm_config)
        self.assertIn("DEPLOYMENT_NAME", llm_config)
        self.assertEqual(llm_config["DEPLOYMENT_NAME"], "gpt-4-legacy")

        # Verify environment variables
        self.assertEqual("DEPLOYMENT_NAME", mock_environ)
        self.assertEqual(mock_environ["AZURE_OPENAI_ENDPOINT"], "https://test.openai.azure.com")

        # Verify provider was called with deployment name
        mock_provider_instance.model_name.assert_called_once_with("gpt-4-legacy")

        # Verify return value
        self.assertEqual(result, "azure-model")

    @patch("azext_aks_agent.agent.llm_config_manager.PROVIDER_REGISTRY")
    @patch("azext_aks_agent.agent.llm_config_manager.os.environ", new_callable=dict)
    def test_export_model_config_azure_with_deployment_name(self, mock_environ, mock_registry):
        """Test export_model_config with Azure provider using DEPLOYMENT_NAME."""
        # Mock provider
        mock_provider_instance = MagicMock()
        mock_provider_instance.model_name.return_value = "azure-deployment"
        mock_provider = MagicMock(return_value=mock_provider_instance)
        mock_registry.get.return_value = mock_provider

        llm_config = {
            "provider": "azure",
            "DEPLOYMENT_NAME": "my-gpt-4-deployment",
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
            "AZURE_OPENAI_API_KEY": "azure-key"
        }

        with patch("azext_aks_agent.agent.llm_config_manager.logger"):
            result = self.manager.export_model_config(llm_config)

        # Verify DEPLOYMENT_NAME is preserved
        self.assertEqual(llm_config["DEPLOYMENT_NAME"], "my-gpt-4-deployment")
        self.assertEqual("DEPLOYMENT_NAME", mock_environ)

        # Verify provider was called with deployment name
        mock_provider_instance.model_name.assert_called_once_with("my-gpt-4-deployment")

        # Verify return value
        self.assertEqual(result, "azure-deployment")

    @patch("azext_aks_agent.agent.llm_config_manager.PROVIDER_REGISTRY")
    def test_export_model_config_non_azure_provider(self, mock_registry):
        """Test export_model_config with non-Azure provider."""
        # Mock provider
        mock_provider_instance = MagicMock()
        mock_provider_instance.model_name.return_value = "openai-model"
        mock_provider = MagicMock(return_value=mock_provider_instance)
        mock_registry.get.return_value = mock_provider

        llm_config = {
            "provider": "openai",
            "MODEL_NAME": "gpt-4",
            "OPENAI_API_KEY": "test-key"
        }

        with patch("azext_aks_agent.agent.llm_config_manager.logger"):
            with patch("azext_aks_agent.agent.llm_config_manager.os.environ", new_callable=dict):
                result = self.manager.export_model_config(llm_config)

        # Verify MODEL_NAME is preserved for non-Azure providers
        self.assertEqual(llm_config["MODEL_NAME"], "gpt-4")

        # Verify provider was called with model name
        mock_provider_instance.model_name.assert_called_once_with("gpt-4")

        self.assertEqual(result, "openai-model")


if __name__ == '__main__':
    unittest.main()
