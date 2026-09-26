# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from typing import Tuple

from openai import AzureOpenAI

from .base import LLMProvider, is_valid_url, non_empty


def is_valid_api_base(v: str) -> bool:
    if not v.startswith("https://"):
        return False
    return is_valid_url(v)


class AzureProvider(LLMProvider):
    @property
    def readable_name(self) -> str:
        return "Azure OpenAI"

    @property
    def name(self) -> str:
        return "azure-openai"

    @property
    def parameter_schema(self):
        return {
            "models": {
                "secret": False,
                "default": None,
                "hint": "comma-separated deployment names, e.g., gpt-5.4,gpt-5.1",
                "validator": non_empty,
                "alias": "models"
            },
            "api_key": {
                "secret": True,
                "default": None,
                "hint": None,
                "validator": non_empty
            },
            "api_base": {
                "secret": False,
                "default": None,
                "hint": "e.g., https://YOUR-RESOURCE-NAME.openai.azure.com/openai/v1/",
                "validator": is_valid_api_base
            }
        }

    def validate_connection(self, params: dict) -> Tuple[str, str]:
        api_key = params.get("api_key")
        api_base = params.get("api_base")
        models_str = params.get("models")

        if not all([api_key, api_base, models_str]):
            return "Missing required Azure OpenAI parameters.", "retry_input"

        models = [m.strip() for m in models_str.split(",")]
        client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=api_base
        )

        for model_name in models:
            try:
                client.responses.create(
                    model=model_name,
                    instructions="You are a helpful assistant.",
                    input="ping",
                    timeout=10
                )
            except Exception as e:  # pylint: disable=broad-exception-caught
                error_str = str(e).lower()
                if any(x in error_str for x in ["api key", "authentication", "unauthorized",
                                                "invalid", "bad request", "deployment"]):
                    return f"Model '{model_name}' validation failed: {e}", "retry_input"
                return f"Model '{model_name}' connection error: {e}", "connection_error"

        return None, "save"
