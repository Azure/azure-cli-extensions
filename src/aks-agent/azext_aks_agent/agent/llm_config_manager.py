# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import os
from pathlib import Path
from typing import Dict, List

import yaml
from azext_aks_agent._consts import CONFIG_DIR
from azext_aks_agent.agent.llm_providers import LLMProvider
from knack.log import get_logger

logger = get_logger(__name__)


class LLMConfigManager:
    """Manages loading and saving LLM configuration from/to a YAML file."""

    def __init__(self, model_list: Dict = None):
        self.model_list = model_list if model_list is not None else {}

    def save(self, provider: LLMProvider, params: dict):
        # save the model config, and translate the model name to the one with llm provider route
        model_name = provider.model_name(params.get("model"))
        params["model"] = model_name
        self.model_list[model_name] = params

    def secured_model_list(self) -> Dict[str, dict]:
        secured_config = {}
        for model_name, model_config in self.model_list.items():
            secured_config[model_name] = LLMProvider.to_secured_model_list_config(model_config)
        return secured_config

    def get_llm_model_secret_data(self) -> Dict[str, str]:
        """
        Get Kubernetes secret data for all LLM models in the configuration.
        """
        secrets_data = {}
        for _, model_config in self.model_list.items():
            secret_data = LLMProvider.to_k8s_secret_data(model_config)
            secrets_data.update(secret_data)
        return secrets_data

    def get_env_vars(self, secret_name: str) -> List[Dict[str, str]]:
        """
        Get environment variable mappings for all LLM models in the configuration.
        """
        env_vars_list = []
        for _, model_config in self.model_list.items():
            env_var = LLMProvider.to_env_vars(secret_name, model_config)
            env_vars_list.append(env_var)
        return env_vars_list


class LLMConfigManagerLocal:  # pylint: disable=too-few-public-methods
    """Manages loading and saving LLM configuration from/to a local YAML file."""

    def __init__(self, subscription_id: str, resource_group_name: str, cluster_name: str,
                 config_dir: str = None):
        """
        Initialize the local LLM config manager.

        Args:
            subscription_id: Azure subscription ID for cluster-specific config
            resource_group_name: Azure resource group name for cluster-specific config
            cluster_name: AKS cluster name for cluster-specific config
            config_dir: Directory path for storing config files.
                       Defaults to ~/.aks-agent/config/
        """
        if config_dir is None:
            config_dir = os.path.join(CONFIG_DIR, "config")

        self.config_dir = Path(config_dir)

        # Create a cluster-specific directory: config/<subscription_id>/<resource_group>/<cluster_name>
        cluster_dir = self.config_dir / subscription_id / resource_group_name / cluster_name
        self.config_file = cluster_dir / "model_list.yaml"
        logger.debug("Using cluster-specific config file: %s", self.config_file)

        self.model_list: Dict = {}

        # Load existing config if available
        self._load_config()

    def _load_config(self):
        """Load model list from the local YAML file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and isinstance(data, dict):
                        self.model_list = data
                        logger.debug("Loaded model list from %s: %d models found",
                                     self.config_file, len(self.model_list))
                    else:
                        logger.debug("No model list found in %s", self.config_file)
                        self.model_list = {}
            else:
                logger.debug("Config file not found: %s", self.config_file)
                self.model_list = {}
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning("Failed to load config from %s: %s", self.config_file, e)
            self.model_list = {}

    def _save_config(self):
        """Save model list to the local YAML file."""
        try:
            # Create config directory (including cluster-specific subdirectories) if it doesn't exist
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            # Write model list to YAML file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.model_list, f, default_flow_style=False, sort_keys=False)

            logger.debug("Saved model list to %s: %d models", self.config_file, len(self.model_list))
        except Exception as e:
            logger.error("Failed to save config to %s: %s", self.config_file, e)
            raise

    def save(self, provider: LLMProvider, params: dict):
        """
        Save a model configuration.

        Args:
            provider: LLM provider instance
            params: Model parameters to save
        """
        # Save the model config, and translate the model name to the one with llm provider route
        model_name = provider.model_name(params.get("model"))
        params["model"] = model_name
        self.model_list[model_name] = params

        # Persist to file
        self._save_config()
