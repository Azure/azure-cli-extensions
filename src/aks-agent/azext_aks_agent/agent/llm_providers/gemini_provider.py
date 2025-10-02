# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import requests
from .base import LLMProvider, non_empty


class GeminiProvider(LLMProvider):
    name = "gemini"

    @property
    def parameter_schema(self):
        return {
            "GEMINI_API_KEY": {
                "secret": True,
                "default": None,
                "hint": None,
                "validator": non_empty
            },
            "MODEL_NAME": {
                "secret": False,
                "default": "gemini-2.5",
                "hint": None,
                "validator": non_empty
            },
        }
    

    def validate_connection(self, params: dict):
        api_key = params.get("GEMINI_API_KEY")
        model_name = params.get("MODEL_NAME")

        if not all([api_key, model_name]):
            return False, "Missing required Gemini parameters.", "retry_input"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
        payload = {
            "contents": [{"role": "user", "parts": [{"text": "ping"}]}]
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