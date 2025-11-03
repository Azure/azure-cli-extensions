# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import os
from typing import Dict, List, Optional

import yaml
from azext_aks_agent._consts import CONST_AGENT_CONFIG_FILE_NAME
from azure.cli.core.api import get_config_dir
from azure.cli.core.azclierror import AzCLIError


class LLMConfigManager:
    """Manages loading and saving LLM configuration from/to a YAML file."""

    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(
                get_config_dir(), CONST_AGENT_CONFIG_FILE_NAME)
        self.config_path = os.path.expanduser(config_path)

    def validate_config(self):
        default_config_path = os.path.join(get_config_dir(), CONST_AGENT_CONFIG_FILE_NAME)
        # suppose the default config is always valid since it's created by the CLI
        if self.config_path == default_config_path:
            return

        try:
            with open(self.config_path, "r") as f:
                config_data = yaml.safe_load(f)

                # Validate the configuration structure
                if not isinstance(config_data, dict):
                    raise ValueError(
                        f"Configuration file {self.config_path} must contain a YAML dictionary/mapping.")

                if "llms" not in config_data:
                    raise ValueError(
                        f"Configuration file {self.config_path} must contain an 'llms' key.")

                if not isinstance(config_data["llms"], list):
                    raise ValueError(
                        f"Configuration file {self.config_path}: 'llms' must be a list.")

                if len(config_data["llms"]) == 0:
                    raise ValueError(
                        f"Configuration file {self.config_path}: 'llms' list cannot be empty.")

                for llm_config in config_data["llms"]:
                    if not isinstance(llm_config, dict):
                        raise ValueError(
                            f"Configuration file {self.config_path}: "
                            "each LLM configuration must be a dictionary/mapping.")
        except FileNotFoundError:
            raise ValueError(f"Configuration file {self.config_path} not found.")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML syntax in configuration file {self.config_path}: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load configuration file {self.config_path}: {e}")

    def save(self, provider_name: str, params: dict):
        configs = self.load()
        if not isinstance(configs, Dict):
            configs = {}

        models = configs.get("llms", [])
        model_name = params.get("MODEL_NAME")
        if not model_name:
            raise ValueError("MODEL_NAME is required to save configuration.")

        # Check if model already exists, update it and move it to the last;
        # otherwise, append new
        models = [
            cfg for cfg in models if not (
                cfg.get("provider") == provider_name and cfg.get("MODEL_NAME") == model_name)]
        models.append({"provider": provider_name, **params})

        configs["llms"] = models

        with open(self.config_path, "w") as f:
            yaml.safe_dump(configs, f, sort_keys=False)

    def load(self):
        """Load configurations from the YAML file."""
        if not os.path.exists(self.config_path):
            return {}
        with open(self.config_path, "r") as f:
            configs = yaml.safe_load(f)
            return configs if isinstance(configs, Dict) else {}

    def get_list(self) -> List[Dict]:
        """Get the list of all model configurations"""
        return self.load()["llms"] if self.load(
        ) and "llms" in self.load() else []

    def get_latest(self) -> Optional[Dict]:
        """Get the last model configuration"""
        model_configs = self.get_list()
        if model_configs:
            return model_configs[-1]
        return None

    def get_specific(
            self,
            provider_name: str,
            model_name: str) -> Optional[Dict]:
        """
        Get specific model configuration by provider and model name during Q&A with --model provider/model
        """
        model_configs = self.get_list()
        for cfg in model_configs:
            if cfg.get("provider") == provider_name and cfg.get(
                    "MODEL_NAME") == model_name:
                return cfg
        return None

    def get_model_config(self, model) -> Optional[Dict]:
        prompt_for_init = "Run 'az aks agent-init' to set up your LLM endpoint (recommended path).\n" \
            "To configure your LLM manually, create a config file using the templates provided here: "\
            "https://aka.ms/aks/agentic-cli/init"

        if not model:
            llm_config: Optional[Dict] = self.get_latest()
            if not llm_config:
                raise AzCLIError(f"No LLM configurations found. {prompt_for_init}")
            return llm_config

        provider_name = "openai"
        model_name = model
        if "/" in model:
            provider_name, model_name = model.split("/", 1)
        llm_config = self.get_specific(provider_name, model_name)
        if not llm_config:
            raise AzCLIError(
                f"No configuration found for model '{model}'. {prompt_for_init}")
        return llm_config

    def is_config_complete(self, config, provider_schema):
        """
        Check if the given config has all required keys and valid values as per the provider schema.
        """
        for key, meta in provider_schema.items():
            if meta.get("validator") and not meta["validator"](
                    config.get(key)):
                return False
        return True
