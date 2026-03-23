# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from typing import Tuple

import requests

from .base import LLMProvider, non_empty


class AnthropicProvider(LLMProvider):
    @property
    def readable_name(self) -> str:
        return "Anthropic"

    @property
    def provider(self) -> str:
        return "anthropic"

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def parameter_schema(self):
        return {
            "api_key": {
                "secret": True,
                "default": None,
                "hint": None,
                "validator": non_empty
            },
            "models": {
                "secret": False,
                "default": "claude-sonnet-4",
                "hint": "comma-separated model names, e.g., claude-sonnet-4,claude-opus-4",
                "validator": non_empty
            },
        }

    def validate_connection(self, params: dict) -> Tuple[str, str]:
        api_key = params.get("api_key")
        models_str = params.get("models")
        if not all([api_key, models_str]):
            return "Missing required Anthropic parameters.", "retry_input"

        models = [m.strip() for m in models_str.split(",")]
        model_name = models[0]

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_name,
            "max_tokens": 16,
            "messages": [{"role": "user", "content": "ping"}]
        }

        try:
            resp = requests.post(url, headers=headers,
                                 json=payload, timeout=10)
            resp.raise_for_status()
            return None, "save"
        except requests.exceptions.HTTPError as e:
            if 400 <= resp.status_code < 500:
                return f"Client error: {e} - {resp.text}", "retry_input"
            return f"Server error: {e} - {resp.text}", "connection_error"
        except requests.exceptions.RequestException as e:
            return f"Request error: {e}", "connection_error"
