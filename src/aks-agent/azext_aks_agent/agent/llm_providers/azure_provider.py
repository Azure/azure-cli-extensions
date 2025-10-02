# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import requests
from typing import Tuple
from urllib.parse import urljoin, urlencode
from .base import LLMProvider, is_url, non_empty


class AzureProvider(LLMProvider):
    name = "azure"

    @property
    def parameter_schema(self):
        return {
            "AZURE_API_KEY": {
                "secret": True,
                "default": None,
                "hint": None,
                "validator": non_empty
            },
            "AZURE_API_BASE": {
                "secret": False,
                "default": None,
                "hint": "https://{your-custom-endpoint}.openai.azure.com/",
                "validator": is_url
            },
            "AZURE_API_VERSION": {
                "secret": False,
                "default": "2025-04-01-preview",
                "hint": None,
                "validator": non_empty
            },
            "MODEL_NAME": {
                "secret": False,
                "default": "gpt-4.1",
                "hint": "should be consistent with your deployed name",
                "validator": non_empty
            },
        }

    def validate_connection(self, params: dict) -> Tuple[bool, str, str]:
        api_key = params.get("AZURE_API_KEY")
        api_base = params.get("AZURE_API_BASE")
        api_version = params.get("AZURE_API_VERSION")
        model_name = params.get("MODEL_NAME")

        if not all([api_key, api_base, api_version, model_name]):
            return False, "Missing required Azure parameters.", "retry_input"

        # REST API reference: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/api-version-lifecycle?tabs=rest
        api_base = api_base.rstrip('/') + '/'
        url = urljoin(api_base, "openai/responses")
        query = {"api-version": api_version}
        full_url = f"{url}?{urlencode(query)}"
        headers = {"api-key": api_key, "Content-Type": "application/json"}
        payload = {"model": model_name,
                   "input": "ping", "max_output_tokens": 16}

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
