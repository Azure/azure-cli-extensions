# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

import logging
from contextlib import contextmanager


# azure cli core will handle and log the exceptions with metadata_logger, while rich handler may cause duplicate logs.
# ref: https://github.com/Azure/azure-cli/blob/37e3d6e857bfe05dbad6b9594d65589b8cfaee5a/src/azure-cli-core/azure/cli/core/azlogging.py#L207
def mute_rich_logging():
    """
    Remove rich handlers from the root logger to prevent duplicate logging when raising errors.
    """
    root_logger = logging.getLogger()
    rich_handlers = []

    # Find and remove rich handlers
    for handler in root_logger.handlers[:]:  # Create a copy to iterate safely
        if (hasattr(handler, 'console') or
                handler.__class__.__name__ == 'RichHandler' or
                'rich' in handler.__class__.__module__.lower()):
            rich_handlers.append(handler)
            root_logger.removeHandler(handler)


# NOTE(mainred): holmes leverage the log handler RichHandler to provide colorful, readable and well-formatted logs
# making the interactive mode more user-friendly.
# And we removed exising log handlers to avoid duplicate logs.
# Also make the console log consistent, we remove the telemetry and data logger to skip redundant logs.
def init_log():
    # NOTE(mainred): we need to disable INFO logs from LiteLLM before LiteLLM library is loaded, to avoid logging the
    # debug logs from heading of LiteLLM.
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)
    logging.getLogger("telemetry.main").setLevel(logging.WARNING)
    logging.getLogger("telemetry.process").setLevel(logging.WARNING)
    logging.getLogger("telemetry.save").setLevel(logging.WARNING)
    logging.getLogger("telemetry.client").setLevel(logging.WARNING)
    logging.getLogger("az_command_data_logger").setLevel(logging.WARNING)

    from holmes.utils.console.logging import init_logging

    # TODO: make log verbose configurable, currently disabled by [].
    return init_logging([])


@contextmanager
def rich_logging():
    """
    Context manager that initializes logging and automatically mutes rich logging on errors.
    This combines initialization with automatic error handling.

    Usage:
        with rich_logging() as console:
            # Rich logging is available
            console.print("This will use rich logging")

            # If any error is raised, rich logging will be muted automatically
            raise CLIError("This won't be logged by rich handler")
    """
    # Initialize logging first
    console = init_log()

    try:
        yield console
    except Exception:
        # When any exception occurs, mute rich logging to prevent duplicates
        mute_rich_logging()
        # Re-raise the exception so it can be handled normally by CLI
        raise
