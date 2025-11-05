# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from typing import Tuple
from urllib.parse import urlencode, urljoin

import requests

from .base import LLMProvider, is_valid_url, non_empty


def is_valid_api_base(v: str) -> bool:
    # validate the v follows the pattern https://{azure-openai-service-name}.openai.azure.com/
    if not v.startswith("https://") or not v.endswith(".openai.azure.com/"):
        return False

    return is_valid_url(v)


class AzureProvider(LLMProvider):
    @property
    def readable_name(self) -> str:
        return "Azure OpenAI"

    @property
    def model_route(self) -> str:
        return "azure"

    @property
    def parameter_schema(self):
        return {
            "DEPLOYMENT_NAME": {
                "secret": False,
                "default": None,
                "hint": "ensure your deployment name is the same as the model name, e.g., gpt-5",
                "validator": non_empty
            },
            "AZURE_API_KEY": {
                "secret": True,
                "default": None,
                "hint": None,
                "validator": non_empty
            },
            "AZURE_API_BASE": {
                "secret": False,
                "default": None,
                "hint": "https://{azure-openai-service-name}.openai.azure.com/",
                "validator": is_valid_api_base
            },
            "AZURE_API_VERSION": {
                "secret": False,
                "default": "2025-04-01-preview",
                "hint": None,
                "validator": non_empty
            }
        }

    def validate_connection(self, params: dict) -> Tuple[bool, str, str]:
        api_key = params.get("AZURE_API_KEY")
        api_base = params.get("AZURE_API_BASE")
        api_version = params.get("AZURE_API_VERSION")
        deployment_name = params.get("DEPLOYMENT_NAME")

        if not all([api_key, api_base, api_version, deployment_name]):
            return False, "Missing required Azure parameters.", "retry_input"

        # REST API reference: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/api-version-lifecycle?tabs=rest
        url = urljoin(api_base, f"openai/deployments/{deployment_name}/chat/completions")

        query = {"api-version": api_version}
        full_url = f"{url}?{urlencode(query)}"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": deployment_name,
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 16
        }

        try:
            resp = requests.post(full_url, headers=headers,
                                 json=payload, timeout=10)
            resp.raise_for_status()
            return True, "Connection successful.", "save"
        except requests.exceptions.HTTPError as e:
            if 400 <= resp.status_code < 500:
                return False, f"Client error: {e} - {resp.text}", "retry_input"
            return False, f"Server error: {e} - {resp.text}", "connection_error"
        except requests.exceptions.RequestException as e:
            return False, f"Request error: {e}", "connection_error"
