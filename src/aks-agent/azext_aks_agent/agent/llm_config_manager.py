# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from typing import Dict, List, Optional

from azext_aks_agent.agent.llm_providers import LLMProvider
from azure.cli.core.azclierror import AzCLIError
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
