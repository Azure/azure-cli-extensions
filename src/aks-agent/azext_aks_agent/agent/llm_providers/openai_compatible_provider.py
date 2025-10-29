# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from urllib.parse import urljoin

import requests

from .base import LLMProvider, is_valid_url, non_empty


class OpenAICompatibleProvider(LLMProvider):
    @property
    def readable_name(self) -> str:
        return "OpenAI Compatible"

    @property
    def model_route(self) -> str:
        # LiteLLM uses "openai" as the provider to route the request to an OpenAI-compatible endpoint
        # https://docs.litellm.ai/docs/providers/openai_compatible
        return "openai"

    @property
    def parameter_schema(self):
        return {
            "MODEL_NAME": {
                "secret": False,
                "default": None,
                "hint": None,
                "validator": non_empty
            },
            "API_KEY": {
                "secret": True,
                "default": None,
                "hint": None,
                "validator": non_empty
            },
            "API_BASE": {
                "secret": False,
                "default": "https://api.openai.com/v1",
                "hint": None,
                "validator": is_valid_url
            },
        }

    def validate_connection(self, params: dict):
        api_key = params.get("API_KEY")
        api_base = params.get("API_BASE")
        model_name = params.get("MODEL_NAME")

        if not all([api_key, api_base, model_name]):
            return False, "Missing required parameters.", "retry_input"

        url = urljoin(api_base, "chat/completions")
        headers = {"Authorization": f"Bearer {api_key}",
                   "Content-Type": "application/json"}
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 16
        }

        try:
            resp = requests.post(url, headers=headers,
                                 json=payload, timeout=10)
            resp.raise_for_status()
            return True, "Connection successful.", "save"
        except requests.exceptions.HTTPError as e:
            if 400 <= resp.status_code < 500:
                return False, f"Client error: {e} - {resp.text}", "retry_input"
            return False, f"Server error: {e} - {resp.text}", "connection_error"
        except requests.exceptions.RequestException as e:
            return False, f"Request error: {e}", "connection_error"
