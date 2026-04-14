# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Shared utilities for onboarding simplification commands.

Provides REST wrappers (using send_raw_request for automatic auth/retry/throttle),
LRO polling with Retry-After support, CLI command invocation, and progress output.
"""

# pylint: disable=broad-exception-caught

import json
import logging

from azure.cli.core.azclierror import CLIInternalError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CmdProxy - bridge between AAZ hooks and helpers expecting cmd.cli_ctx
# ---------------------------------------------------------------------------

class CmdProxy:
    """Lightweight proxy to pass CLI context where a full cmd object is expected.

    AAZ-generated commands don't expose a cmd object in hooks, but many
    helper functions expect cmd.cli_ctx. This proxy bridges the gap.
    """
    def __init__(self, cli_ctx):
        self.cli_ctx = cli_ctx


# ---------------------------------------------------------------------------
# CLI command invocation
# ---------------------------------------------------------------------------

def invoke_cli_command(cmd, command_args, expect_json=True):
    """Invoke another az CLI command in-process (shares auth context).

    Uses get_default_cli().invoke() so the child command shares
    the same auth session, telemetry, and CLI context.

    Returns parsed JSON result if expect_json=True, raw result otherwise.
    Raises CLIInternalError on non-zero exit.
    """
    from azure.cli.core import get_default_cli
    import io
    import sys

    cli = get_default_cli()
    if expect_json and "-o" not in command_args and "--output" not in command_args:
        command_args = list(command_args) + ["-o", "json"]

    logger.debug("Invoking: az %s", " ".join(command_args))

    # Suppress stdout/stderr from child command to avoid raw JSON noise
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    captured_out = io.StringIO()
    captured_err = io.StringIO()
    sys.stdout = captured_out
    sys.stderr = captured_err
    try:
        exit_code = cli.invoke(command_args, out_file=captured_out)
    except TypeError:
        # Older CLI versions may not support out_file
        exit_code = cli.invoke(command_args)
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    if exit_code != 0:
        err_text = captured_err.getvalue().strip()
        # cli.result may contain the error object from the CLI framework
        cli_error = ""
        if hasattr(cli, 'result') and hasattr(cli.result, 'error'):
            cli_error = str(cli.result.error) if cli.result.error else ""
        full_error = cli_error or err_text or f"exit code {exit_code}"
        cmd_str = f"az {' '.join(command_args)}"
        raise CLIInternalError(f"{full_error}\nCommand: {cmd_str}")

    result = cli.result.result
    if expect_json and isinstance(result, str):
        try:
            return json.loads(result)
        except (json.JSONDecodeError, TypeError):
            pass
    return result


# ---------------------------------------------------------------------------
# Progress output
# ---------------------------------------------------------------------------

def print_step(step_num, total, message, status=""):
    """Print a formatted step indicator.

    Examples:
        [1/4] Installing cert-manager...
        [1/4] Installing cert-manager... [OK]
        [1/4] Installing cert-manager... Already installed [OK]
    """
    prefix = f"[{step_num}/{total}]"
    if status:
        print(f"{prefix} {message}... {status}")
    else:
        print(f"{prefix} {message}...")


def print_success(message):
    """Print a success summary line."""
    print(f"\n[OK] {message}")


def print_detail(label, value):
    """Print a detail line (indented)."""
    print(f"  {label}: {value}")
