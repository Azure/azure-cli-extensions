# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from typing import Tuple
from urllib.parse import urlencode, urljoin

import requests

from .base import LLMProvider, is_valid_url, non_empty


def is_valid_api_base(v: str) -> bool:
    # A valid api_base should be a URL and starts with https://, and ends with either .openai.azure.com/ or
    # .cognitiveservices.azure.com/. Until there's a convergence on the endpoint format for Azure OpenAI service,
    # we will accept both formats without validation.
    if not v.startswith("https://"):
        return False
    return is_valid_url(v)


class AzureProvider(LLMProvider):
    @property
    def readable_name(self) -> str:
        return "Azure OpenAI"

    @property
    def name(self) -> str:
        return "azure-openai"

    @property
    def parameter_schema(self):
        return {
            "models": {
                "secret": False,
                "default": None,
                "hint": "comma-separated model names, e.g., gpt-5.4,gpt-5.1",
                "validator": non_empty,
                "alias": "models"
            },
            "api_key": {
                "secret": True,
                "default": None,
                "hint": None,
                "validator": non_empty
            },
            "api_base": {
                "secret": False,
                "default": None,
                "hint": "e.g., https://YOUR-RESOURCE-NAME.openai.azure.com/openai/v1/",
                "validator": is_valid_api_base
            }
        }

    def validate_connection(self, params: dict) -> Tuple[str, str]:
        return None, "save"  # None error means success
