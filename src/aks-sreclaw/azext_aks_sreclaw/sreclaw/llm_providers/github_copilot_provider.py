# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from typing import Tuple

from .base import LLMProvider, non_empty


class GitHubCopilotProvider(LLMProvider):
    @property
    def readable_name(self) -> str:
        return "GitHub Copilot"

    @property
    def name(self) -> str:
        return "github-copilot"

    @property
    def parameter_schema(self):
        return {
            "models": {
                "secret": False,
                "default": "claude-opus-4.6",
                "hint": "comma-separated model names, e.g., claude-opus-4.6",
                "validator": non_empty
            },
        }

    def validate_connection(self, params: dict) -> Tuple[str, str]:
        models_str = params.get("models")
        if not models_str:
            return "Missing required GitHub Copilot parameters.", "retry_input"
        return None, "save"
