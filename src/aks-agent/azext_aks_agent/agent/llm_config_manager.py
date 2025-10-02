# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import os
from typing import List, Dict, Optional
import yaml

from azure.cli.core.api import get_config_dir
from azext_aks_agent._consts import CONST_AGENT_CONFIG_FILE_NAME



class LLMConfigManager:
    """Manages loading and saving LLM configuration from/to a YAML file."""

    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(get_config_dir(), CONST_AGENT_CONFIG_FILE_NAME)
        self.config_path = os.path.expanduser(config_path)

    def save(self, provider_name: str, params: dict):
        configs = self.load()
        if not isinstance(configs, Dict):
            configs = {}
        
        models = configs.get("llms", [])
        model_name = params.get("MODEL_NAME")
        if not model_name:
            raise ValueError("MODEL_NAME is required to save configuration.")
        
        # Check if model already exists, update it and move it to the last; otherwise, append new
        models = [cfg for cfg in models if not (cfg.get("provider") == provider_name and cfg.get("MODEL_NAME") == model_name)]
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
        return self.load()["llms"] if self.load() and "llms" in self.load() else []

    def get_latest(self) -> Optional[Dict]:
        """Get the last model configuration"""
        model_configs = self.get_list()
        if model_configs:
            return model_configs[-1]
        raise ValueError("No configurations found. Please run `az aks agent init`")

    def get_specific(self, provider_name: str, model_name: str) -> Optional[Dict]:
        """
        Get specific model configuration by provider and model name during Q&A with --model provider/model
        """
        model_configs = self.get_list()
        for cfg in model_configs:
            if cfg.get("provider") == provider_name and cfg.get("MODEL_NAME") == model_name:
                return cfg
        raise ValueError(f"No configuration found for provider '{provider_name}' with model '{model_name}'. Please run `az aks agent init`")

    def is_config_complete(self, config, provider_schema):
        """
        Check if the given config has all required keys and valid values as per the provider schema.
        """
        for key, meta in provider_schema.items():
            if meta.get("validator") and not meta["validator"](config.get(key)):
                return False
        return True


