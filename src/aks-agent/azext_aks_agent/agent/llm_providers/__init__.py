# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import List, Tuple
from rich.console import Console
from holmes.utils.colors import HELP_COLOR, ERROR_COLOR
from holmes.interactive import SlashCommands
from .base import LLMProvider
from .azure_provider import AzureProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .gemini_provider import GeminiProvider
from .openai_compatible_provider import OpenAICompatibleProvider


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
    key = cls.name.lower()
    if key not in PROVIDER_REGISTRY:
        PROVIDER_REGISTRY[key] = cls


def _available_providers() -> List[str]:
    """Return a list of registered provider names (lowercase): ["azure", "openai", ...]"""
    return list(PROVIDER_REGISTRY.keys())


def _provider_choices_numbered() -> List[Tuple[int, str]]:
    """Return numbered choices: [(1, "azure"), (2, "openai"), ...]."""
    return [(i + 1, name) for i, name in enumerate(_available_providers())]


def _get_provider_by_index(idx: int) -> LLMProvider:
    """
    Return provider instance by numeric index (1-based).
    Raises ValueError if index is out of range.
    """
    if 1 <= idx <= len(_PROVIDER_CLASSES):
        console.print("You selected provider:", _PROVIDER_CLASSES[idx - 1].name, style=f"bold {HELP_COLOR}")
        return _PROVIDER_CLASSES[idx - 1]()
    raise ValueError(f"Invalid provider index: {idx}")


def prompt_provider_choice() -> LLMProvider:
    """
    Show a numbered menu and return the chosen provider instance.
    Keeps prompting until a valid selection is made.
    """
    choices = _provider_choices_numbered()
    if not choices:
        raise ValueError("No providers are registered.")
    while True:
        for idx, name in choices:
            console.print(f" {idx}. {name}", style=f"bold {HELP_COLOR}")
        sel_idx = console.input(
            f"[bold {HELP_COLOR}]Enter the number of your LLM provider: [/bold {HELP_COLOR}]").strip().lower()

        if sel_idx == "/exit":
            raise SystemExit(0)
        try:
            return _get_provider_by_index(int(sel_idx))
        except ValueError as e:
            console.print(
                f"{e}. Please enter a valid number, or type '{SlashCommands.EXIT.command}' to exit.",
                style=f"{ERROR_COLOR}")


__all__ = [
    "PROVIDER_REGISTRY",
    "prompt_provider_choice",
]
