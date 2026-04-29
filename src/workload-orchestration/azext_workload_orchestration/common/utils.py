# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Shared utilities for workload orchestration CLI commands.

Provides REST wrappers (using send_raw_request for automatic auth/retry/throttle),
LRO polling with Retry-After support, CLI command invocation, and progress output.
"""

# pylint: disable=broad-exception-caught

import json
import logging
import sys

from azure.cli.core.azclierror import CLIInternalError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CmdProxy - bridge between AAZ hooks and helpers expecting cmd.cli_ctx
# ---------------------------------------------------------------------------

class CmdProxy:  # pylint: disable=too-few-public-methods
    """Lightweight proxy to pass CLI context where a full cmd object is expected."""
    def __init__(self, cli_ctx):
        self.cli_ctx = cli_ctx


# ---------------------------------------------------------------------------
# ARM ID parsing
# ---------------------------------------------------------------------------

def parse_arm_id(arm_id):
    """Parse an ARM resource ID into a dict of segment name → value.

    Example:
        parse_arm_id("/subscriptions/abc/resourceGroups/myRG/providers/Microsoft.Edge/contexts/myCtx")
        → {"subscriptions": "abc", "resourcegroups": "myRG", "contexts": "myCtx"}

    Keys are lowercased for case-insensitive lookup.
    Returns empty dict if arm_id is None or empty.
    """
    if not arm_id:
        return {}
    parts = arm_id.strip("/").split("/")
    result = {}
    i = 0
    while i < len(parts) - 1:
        result[parts[i].lower()] = parts[i + 1]
        i += 2
    return result


# ---------------------------------------------------------------------------
# Silent CLI invocation
# ---------------------------------------------------------------------------

def invoke_silent(cli_args):
    """Invoke an az CLI command silently (suppress all stdout/stderr).

    Returns the exit code. Useful for fire-and-forget operations
    where you don't need the output (e.g., setting config, creating
    resources via 'az rest').
    """
    from azure.cli.core import get_default_cli
    import io

    cli = get_default_cli()
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    try:
        return cli.invoke(cli_args)
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr


# ---------------------------------------------------------------------------
# CLI command invocation
# ---------------------------------------------------------------------------

def invoke_cli_command(cmd, command_args, expect_json=True):  # pylint: disable=unused-argument
    """Invoke another az CLI command in-process (shares auth context).

    Uses get_default_cli().invoke() so the child command shares
    the same auth session, telemetry, and CLI context.

    Returns parsed JSON result if expect_json=True, raw result otherwise.
    Raises CLIInternalError on non-zero exit.
    """
    from azure.cli.core import get_default_cli
    import io

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
        # Log the underlying az command at DEBUG only — surfacing it to
        # end users adds noise and can leak resource args. The error text
        # alone is enough for the user; engineers can re-run with --debug.
        logger.debug("az command failed: az %s", " ".join(command_args))
        raise CLIInternalError(full_error)

    result = cli.result.result
    if expect_json and isinstance(result, str):
        try:
            return json.loads(result)
        except (json.JSONDecodeError, TypeError):
            pass
    return result


# ---------------------------------------------------------------------------
# Progress output (uses stderr so -o json/table/tsv is clean)
# ---------------------------------------------------------------------------


def _eprint(*args, **kwargs):
    """Print to stderr."""
    print(*args, file=sys.stderr, **kwargs)


def print_step(step_num, total, message, status=""):
    """Print a formatted step indicator to stderr using tree characters."""
    connector = "└──" if step_num == total else "├──"
    if status:
        _eprint(f"{connector} {message} {status}")
    else:
        _eprint(f"{connector} {message}...")
