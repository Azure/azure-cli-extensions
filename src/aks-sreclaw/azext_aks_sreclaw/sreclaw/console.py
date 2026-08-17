# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Console utilities for AKS Agent CLI.
Provides a singleton Rich Console instance and color constants for consistent terminal output.
"""

from rich.console import Console

# Color constants for terminal output
HELP_COLOR = "cyan"  # Informational messages, help text
SUCCESS_COLOR = "bold green"  # Success messages
WARNING_COLOR = "bold yellow"  # Warning messages
ERROR_COLOR = "bold red"  # Error messages
INFO_COLOR = "yellow"  # General information
HINT_COLOR = "bright_black"  # Hints for user input
DEFAULT_VALUE_COLOR = "bright_black"  # Default value displays

# Global singleton console instance
_console_instance = None


def get_console() -> Console:
    """
    Get the singleton Rich Console instance.

    This ensures all console output in the AKS agent uses the same
    Console instance for consistent formatting and behavior.

    Returns:
        Console: The shared Rich Console instance
    """
    global _console_instance  # pylint: disable=global-statement
    if _console_instance is None:
        _console_instance = Console()
    return _console_instance
