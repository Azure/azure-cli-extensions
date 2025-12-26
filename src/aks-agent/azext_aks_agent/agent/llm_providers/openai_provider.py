# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from typing import Tuple

import requests

from .base import LLMProvider, non_empty


class OpenAIProvider(LLMProvider):
    @property
    def readable_name(self) -> str:
        return "OpenAI"

    @property
    def name(self) -> str:
        return "openai"

    @property
    def model_route(self) -> str:
        # Openai model route is empty under the Litellm provider scheme
        return ""

    @property
    def parameter_schema(self):
        return {
            "model": {
                "secret": False,
                "default": "gpt-5",
                "hint": None,
                "validator": non_empty
            },
            "api_key": {
                "secret": True,
                "default": None,
                "hint": None,
                "validator": non_empty
            },
        }

    def validate_connection(self, params: dict) -> Tuple[str, str]:
        api_key = params.get("api_key")
        model_name = params.get("model")
        if not all([api_key, model_name]):
            return "Missing required OpenAI parameters.", "retry_input"

        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}",
                   "Content-Type": "application/json"}
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": "ping"}],
            "max_completion_tokens": 16
        }

        try:
            resp = requests.post(url, headers=headers,
                                 json=payload, timeout=10)
            resp.raise_for_status()
            return None, "save"  # None error means success
        except requests.exceptions.HTTPError as e:
            if 400 <= resp.status_code < 500:
                return f"Client error: {e} - {resp.text}", "retry_input"
            return f"Server error: {e} - {resp.text}", "connection_error"
        except requests.exceptions.RequestException as e:
            return f"Request error: {e}", "connection_error"
