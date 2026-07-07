# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from typing import Tuple

from .base import LLMProvider, is_valid_url, non_empty


def is_valid_api_base(v: str) -> bool:
    if not v.startswith("https://"):
        return False
    return is_valid_url(v)


class AzureEntraIDProvider(LLMProvider):
    @property
    def readable_name(self) -> str:
        return "Azure OpenAI (Microsoft Entra ID)"

    @property
    def model_route(self) -> str:
        return "azure"

    @property
    def parameter_schema(self):
        return {
            "model": {
                "secret": False,
                "default": None,
                "hint": "ensure your deployment name is the same as the model name, e.g., gpt-5",
                "validator": non_empty,
                "alias": "deployment_name"
            },
            "api_base": {
                "secret": False,
                "default": None,
                "validator": is_valid_api_base
            },
            "api_version": {
                "secret": False,
                "default": "2025-04-01-preview",
                "hint": None,
                "validator": non_empty
            }
        }

    def validate_connection(self, params: dict) -> Tuple[str, str]:
        api_base = params.get("api_base")
        api_version = params.get("api_version")
        deployment_name = params.get("model")

        if not all([api_base, api_version, deployment_name]):
            return "Missing required Azure parameters.", "retry_input"

        return None, "save"
