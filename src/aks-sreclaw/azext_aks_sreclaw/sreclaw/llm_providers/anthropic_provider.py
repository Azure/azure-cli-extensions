# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from typing import Tuple

from openai import OpenAI

from .base import LLMProvider, non_empty


class AnthropicProvider(LLMProvider):
    @property
    def readable_name(self) -> str:
        return "Anthropic"

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
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.anthropic.com/v1"
        )

        for model_name in models:
            try:
                client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": "ping"}],
                    max_tokens=16,
                    timeout=10
                )
            except Exception as e:  # pylint: disable=broad-exception-caught
                error_str = str(e).lower()
                if any(x in error_str for x in ["api key", "authentication", "unauthorized",
                                                "invalid", "bad request"]):
                    return f"Model '{model_name}' validation failed: {e}", "retry_input"
                return f"Model '{model_name}' connection error: {e}", "connection_error"

        return None, "save"
