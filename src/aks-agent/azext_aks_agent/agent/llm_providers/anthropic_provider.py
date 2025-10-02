# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import requests
from .base import LLMProvider, non_empty


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    @property
    def parameter_schema(self):
        return {
            "ANTHROPIC_API_KEY": {
                "secret": True,
                "default": None,
                "hint": None,
                "validator": non_empty
            },
            "MODEL_NAME": {
                "secret": False,
                "default": "claude-3",
                "hint": None,
                "validator": non_empty
            },
        }


    def validate_connection(self, params: dict):
        api_key = params.get("ANTHROPIC_API_KEY")
        model_name = params.get("MODEL_NAME")

        if not all([api_key, model_name]):
            return False, "Missing required Anthropic parameters.", "retry_input"

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
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            resp.raise_for_status()
            return True, "Connection successful.", "save"
        except requests.exceptions.HTTPError as e:
            if 400 <= resp.status_code < 500:
                return False, f"Client error: {e} - {resp.text}", "retry_input"
            else:
                return False, f"Server error: {e} - {resp.text}", "connection_error"
        except requests.exceptions.RequestException as e:
            return False, f"Request error: {e}", "connection_error"