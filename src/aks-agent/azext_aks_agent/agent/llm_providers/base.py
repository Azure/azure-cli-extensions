# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from abc import ABC, abstractmethod
from getpass import getpass
from typing import Dict, Callable, Tuple, Any
import re


def non_empty(v: str) -> bool:
    return bool(v and v.strip())


def is_url(v: str) -> bool:
    regex = re.compile(
        r'^(?:http|ftp)s?://'             # http:// or https://
        # domain, IPv4 or localhost
        r'(?:[\w.-]+|\d{1,3}(?:\.\d{1,3}){3}|localhost)'
        r'(?::\d+)?'                      # optional port
        r'(?:/?|[/?]\S+)?$',              # path
        re.IGNORECASE
    )
    return re.match(regex, v) is not None


class LLMProvider(ABC):
    name = "base"

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
        schema = self.parameter_schema
        params = {}
        for param, meta in schema.items():
            prompt = meta.get("prompt", f"Enter value for {param}: ")
            default = meta.get("default")
            hint = meta.get("hint")
            secret = meta.get("secret", False)
            validator: Callable[[str], bool] = meta.get(
                "validator", lambda x: True)

            if default:
                prompt += f" (Default: {default}) "
            if hint:
                prompt += f" [Hint: {hint}] "

            while True:
                if secret:
                    value = getpass(prompt)
                else:
                    value = input(prompt)

                if not value and default is not None:
                    value = default

                value = value.strip()
                if value == "/exit":
                    raise SystemExit(0)
                if validator(value):
                    params[param] = value
                    break
                print(
                    f"Invalid value for {param}. Please try again, or type /exit to quit.")

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
