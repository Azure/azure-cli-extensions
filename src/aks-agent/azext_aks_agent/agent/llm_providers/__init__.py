# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import List, Tuple

from rich.console import Console

from .anthropic_provider import AnthropicProvider
from .azure_provider import AzureProvider
from .base import LLMProvider
from .gemini_provider import GeminiProvider
from .openai_compatible_provider import OpenAICompatibleProvider
from .openai_provider import OpenAIProvider

console = Console()

_PROVIDER_CLASSES: List[LLMProvider] = [
    AzureProvider,
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
    OpenAICompatibleProvider,
    # Add new providers here
]

PROVIDER_REGISTRY = {}
for cls in _PROVIDER_CLASSES:
    key = cls().name.lower()
    if key not in PROVIDER_REGISTRY:
        PROVIDER_REGISTRY[key] = cls


def _available_providers() -> List[str]:
    """Return a list of registered provider names (lowercase): ["azure", "openai", ...]"""
    return _PROVIDER_CLASSES


def _provider_choices_numbered() -> List[Tuple[int, str]]:
    """Return numbered choices: [(1, "azure"), (2, "openai"), ...]."""
    return [(i + 1, provider().readable_name) for i, provider in enumerate(_available_providers())]


def _get_provider_by_index(idx: int) -> LLMProvider:
    """
    Return provider instance by numeric index (1-based).
    Raises ValueError if index is out of range.
    """
    from holmes.utils.colors import HELP_COLOR
    if 1 <= idx <= len(_PROVIDER_CLASSES):
        console.print("You selected provider:", _PROVIDER_CLASSES[idx - 1]().readable_name, style=f"bold {HELP_COLOR}")
        return _PROVIDER_CLASSES[idx - 1]()
    raise ValueError(f"Invalid provider index: {idx}")


def prompt_provider_choice() -> LLMProvider:
    """
    Show a numbered menu and return the chosen provider instance.
    Keeps prompting until a valid selection is made.
    """
    from holmes.utils.colors import ERROR_COLOR, HELP_COLOR
    choices = _provider_choices_numbered()
    if not choices:
        raise ValueError("No providers are registered.")
    while True:
        for idx, name in choices:
            console.print(f" {idx}. {name}", style=f"bold {HELP_COLOR}")
        console.print(f" {len(choices) + 1}. For other providers, see https://aka.ms/aks/agentic-cli/init",
                      style=f"bold {HELP_COLOR}")
        sel_idx = console.input(
            f"[bold {HELP_COLOR}]Please choose the LLM provider (1-{len(choices)}): [/bold {HELP_COLOR}]").strip()

        if sel_idx == "/exit":
            raise SystemExit(0)
        try:
            return _get_provider_by_index(int(sel_idx))
        except ValueError as e:
            console.print(
                f"{e}. Please enter a valid number, or type '/exit' to exit.",
                style=f"{ERROR_COLOR}")


__all__ = [
    "PROVIDER_REGISTRY",
    "prompt_provider_choice",
]
