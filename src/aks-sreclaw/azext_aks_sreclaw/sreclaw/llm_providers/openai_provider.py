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
    def parameter_schema(self):
        return {
            "models": {
                "secret": False,
                "default": "gpt-5",
                "hint": "comma-separated model names, e.g., gpt-5.4,gpt-5.1",
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
        models_str = params.get("models")
        if not all([api_key, models_str]):
            return "Missing required OpenAI parameters.", "retry_input"

        models = [m.strip() for m in models_str.split(",")]
        model_name = models[0]

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
            return None, "save"
        except requests.exceptions.HTTPError as e:
            if 400 <= resp.status_code < 500:
                return f"Client error: {e} - {resp.text}", "retry_input"
            return f"Server error: {e} - {resp.text}", "connection_error"
        except requests.exceptions.RequestException as e:
            return f"Request error: {e}", "connection_error"
