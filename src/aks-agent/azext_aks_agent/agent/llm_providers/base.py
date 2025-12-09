# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import base64
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Tuple
from urllib.parse import urlparse

from azext_aks_agent.agent.console import (
    DEFAULT_VALUE_COLOR,
    ERROR_COLOR,
    HELP_COLOR,
    HINT_COLOR,
    get_console,
)


def non_empty(v: str) -> bool:
    return bool(v and v.strip())


def is_valid_url(v: str) -> bool:
    try:
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            return False
        return True
    except ValueError:
        return False


class LLMProvider(ABC):

    @property
    @abstractmethod
    def readable_name(self) -> str:
        """Return the provider name for this provider.
        The provider name is a human-readable string, e.g., "Azure OpenAI", "OpenAI", etc.
        """
        return "Base Provider"

    @property
    def name(self) -> str:
        """Return the provider name for this provider.
        provider name is the key to identity a llmprovider.
        https://docs.litellm.ai/docs/providers
        """
        return self.model_route

    @property
    @abstractmethod
    def model_route(self) -> str:
        """Return the model route parameter key for this provider.
        This model route indicates the model prefix of llm providers supported by LiteLLM, for example the azure openai.
        https://docs.litellm.ai/docs/providers
        """
        return "base"

    def model_name(self, model_name) -> str:
        """Return the model name for this provider.
        The models name combines the model route and model name, e.g., "azure/gpt-5"
        https://docs.litellm.ai/docs/providers
        """
        if self.model_route:
            return f"{self.model_route}/{model_name}"

        return model_name

    @property
    @abstractmethod
    def parameter_schema(self) -> Dict[str, Dict[str, Any]]:
        """
        provider may return a schema mapping param -> metadata:
        {
            "PARAM_NAME": {
                "prompt": "Prompt to show user",
                "secret": True/False,
                "default": "default value or None",
                "hint": "Additional hint to show user",
                "validator": Callable[[str], bool]  # function to validate input,
                "alias": "alias" # optional alternative names for the param
            }
        }
        """
        raise NotImplementedError()

    def prompt_params(self):
        """Prompt user for parameters using parameter_schema when available."""
        schema = self.parameter_schema
        params = {}
        for param, meta in schema.items():
            prompt_name = param
            if "alias" in meta:
                prompt_name = meta["alias"]
            prompt = meta.get("prompt", f"[bold {HELP_COLOR}]Enter value for {prompt_name}: [/]")
            default = meta.get("default")
            hint = meta.get("hint")
            secret = meta.get("secret", False)
            validator: Callable[[str], bool] = meta.get(
                "validator", lambda x: True)

            if default:
                prompt += f" [italic {DEFAULT_VALUE_COLOR}](Default: {default})[/] "
            if hint:
                prompt += f" [italic {HINT_COLOR}](Hint: {hint})[/] "

            console = get_console()
            while True:
                if secret:
                    # For password input, we'll handle the display differently
                    value = console.input(prompt, password=secret)
                    # Calculate the masked display value following OpenAI pattern
                    if len(value) <= 8:
                        # For short passwords, show all as asterisks
                        display_value = '*' * len(value)
                    else:
                        # Show first 3 chars + 3 dots + last 4 chars (OpenAI pattern)
                        first_chars = value[:3]
                        last_chars = value[-4:]
                        display_value = f"{first_chars}...{last_chars}"
                    # It seems rich renders the cursor up as plain text not a control sequence,
                    # so when we combine the cursor up and re-print, console prints extra "[1A" unexpectedly.
                    # To avoid that, we use a workaround by printing the cursor up separately.
                    print("\033[1A", end='')
                    console.print(f"{prompt}{display_value}")
                else:
                    value = console.input(prompt, password=False)

                if not value and default is not None:
                    value = default

                value = value.strip()
                if value == "/exit":
                    raise SystemExit(0)
                if validator(value):
                    params[param] = value
                    break
                console.print(
                    f"Invalid value for {prompt_name}. Please try again, or type '/exit' to exit.",
                    style=f"{ERROR_COLOR}")

        return params

    def validate_params(self, params: dict):
        """Validate parameters from provided config file against schema."""
        schema = self.parameter_schema
        for param, meta in schema.items():
            if param not in params:
                raise ValueError(f"Missing required parameter: {param}")
            validator: Callable[[str], bool] = meta.get(
                "validator", lambda x: True)
            if not validator(params[param]):
                raise ValueError(f"Invalid value for parameter: {param}")
        return True

    # pylint: disable=unused-argument
    @abstractmethod
    def validate_connection(self, params: dict) -> Tuple[str, str]:
        """
        Validate connection to the model endpoint using provided parameters.
        Returns a tuple of (error: str | None, action: str)
        where error is None if validation is successful, otherwise contains the error message.
        Action can be "retry_input", "connection_error", or "save".
        """
        # TODO(mainred): leverage 3rd party libraries like litellm instead of
        # calling http request in each provider to complete the connection check.
        raise NotImplementedError()

    @classmethod
    def to_k8s_secret_data(cls, params: dict):
        """Create a Kubernetes secret dictionary from the provider parameters.
        """
        secret_key = cls.sanitize_k8s_secret_key(params)
        secret_value = params.get("api_key")
        secret_data = {
            secret_key: base64.b64encode(secret_value.encode("utf-8")).decode("utf-8"),
        }
        return secret_data

    @classmethod
    def sanitize_k8s_secret_key(cls, params: dict):
        """Create a unique Kubernetes secret key from the provider parameters.
        """
        import re

        # A valid secret config key must consist of alphanumeric characters, '-', '_' or '.' (e.g. 'key.name',
        # or 'KEY_NAME', or 'key-name', regex used for validation is '[-._a-zA-Z0-9]+')
        model_name = params.get("model")

        # Create a valid k8s secret key by combining model_route and model_name
        # Replace any invalid characters with underscores and use dot as separator
        def sanitize_key_part(part):
            # Replace any character that's not alphanumeric or '_' with '_'
            return re.sub(r'[^_a-zA-Z0-9]', '_', str(part)).upper()

        sanitized_route_model_name = sanitize_key_part(model_name)
        secret_key = f"{sanitized_route_model_name}_API_KEY"

        return secret_key

    @classmethod
    def to_secured_model_list_config(cls, params: dict) -> Dict[str, dict]:
        """Create a model config dictionary for the model list from the provider parameters.
        Returns a copy of params with the api_key replaced by environment variable reference.
        """
        secret_key = cls.sanitize_k8s_secret_key(params)
        secured_params = params.copy()
        secured_params.update({"api_key": f"{{{{ env.{secret_key} }}}}"})
        return secured_params

    @classmethod
    def to_env_vars(cls, secret_name, params: dict) -> Dict[str, str]:
        """Create a model config dictionary for the model list from the provider parameters.
        """
        secret_key = cls.sanitize_k8s_secret_key(params)
        return {
            "name": secret_key,
            "valueFrom": {
                "secretKeyRef": {
                    "name": secret_name,
                    "key": secret_key
                }
            }
        }
