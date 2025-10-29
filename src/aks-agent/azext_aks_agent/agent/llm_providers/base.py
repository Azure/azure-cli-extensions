# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Tuple
from urllib.parse import urlparse

from rich.console import Console

console = Console()
HINT_COLOR = "bright_black"
DEFAULT_COLOR = "bright_black"


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
        The provider name is a human-readable string, e.g., "Azure Open AI", "OpenAI", etc.
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
                "validator": Callable[[str], bool]  # function to validate input
            }
        }
        """
        raise NotImplementedError()

    def prompt_params(self):
        """Prompt user for parameters using parameter_schema when available."""
        from holmes.interactive import SlashCommands
        from holmes.utils.colors import ERROR_COLOR, HELP_COLOR

        schema = self.parameter_schema
        params = {}
        for param, meta in schema.items():
            prompt = meta.get("prompt", f"[bold {HELP_COLOR}]Enter value for {param}: [/]")
            default = meta.get("default")
            hint = meta.get("hint")
            secret = meta.get("secret", False)
            validator: Callable[[str], bool] = meta.get(
                "validator", lambda x: True)

            if default:
                prompt += f" [italic {DEFAULT_COLOR}](Default: {default})[/] "
            if hint:
                prompt += f" [italic {HINT_COLOR}](Hint: {hint})[/] "

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
                    f"Invalid value for {param}. Please try again, or type '{SlashCommands.EXIT.command}' to exit.",
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
    def validate_connection(self, params: dict) -> Tuple[bool, str, str]:
        """
        Validate connection to the model endpoint using provided parameters.
        Returns a tuple of (is_valid: bool, message: str, action: str)
        where action can be "retry_input", "connection_error", or "save".
        """
        raise NotImplementedError()
