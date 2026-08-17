# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Dict

from azext_aks_sreclaw.sreclaw.llm_providers import LLMProvider
from knack.log import get_logger

logger = get_logger(__name__)


class LLMConfigManager:
    """Manages loading and saving LLM configuration from/to a YAML file."""

    def __init__(self, model_list: Dict = None):
        self.model_list = model_list if model_list is not None else {}

    def save(self, provider: LLMProvider, params: dict):
        models_str = params.get("models", "")
        models = [m.strip() for m in models_str.split(",") if m.strip()]

        provider_config = {
            "provider": provider.name,
            "models": models
        }

        if "api_base" in params:
            provider_config["api_base"] = params["api_base"]

        if "api_key" in params:
            provider_config["api_key"] = params["api_key"]

        self.model_list[provider.name] = provider_config

    def get_llm_model_secret_data(self) -> Dict[str, str]:
        """
        Get Kubernetes secret data for all LLM providers in the configuration.
        """
        import base64
        secrets_data = {}
        for provider_name, provider_config in self.model_list.items():
            if "api_key" in provider_config:
                secret_key = f"{provider_name}-key"
                api_key = provider_config["api_key"]
                secrets_data[secret_key] = base64.b64encode(api_key.encode("utf-8")).decode("utf-8")
        return secrets_data
