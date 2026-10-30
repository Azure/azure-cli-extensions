# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from azure.cli.core import AzCommandsLoader
from azure.cli.core.extension import get_extension
from knack.events import EVENT_INVOKER_PRE_PARSE_ARGS

# This is required to populate help for the extension
import azext_quantum._help  # pylint: disable=unused-import

# This is the version reported by the CLI to the service when submitting requests.
# This will be the version of the quantum extension that is currently installed
# This does not work for `azdev extension add` for local dev; install wheel file to mimic real extension installation.
ext = get_extension("quantum")
CLI_REPORTED_VERSION = ext.version if ext else "unknown"


def _reject_removed_job_storage_argument(cli_ctx, **kwargs):
    """Reject the removed job option without echoing its secret-bearing value."""
    invocation = cli_ctx.invocation
    if invocation is None or cli_ctx.data.get('completer_active'):
        return
    if invocation.data.get('command_string') not in (
            'quantum job submit', 'quantum run', 'quantum execute'):
        return
    # Argparse also accepted these unambiguous abbreviations; --s was ambiguous.
    # Match only the option name, not prefixes of unrelated options or their values.
    removed_options = ('--st', '--sto', '--stor', '--stora', '--storag', '--storage')
    if not any(arg.partition('=')[0] in removed_options for arg in kwargs.get('args', ())):
        return

    from azure.cli.core.azclierror import UnrecognizedArgumentError

    # These commands have no positional arguments. Reject even after "--" or alongside help,
    # rather than letting an unknown-argument error echo the value. Workspace options are separate.
    error = UnrecognizedArgumentError(
        'The --storage option has been removed.',
        'Remove --storage from the command. Jobs use storage linked to the Azure Quantum workspace.',
    )
    # Use the normal renderer, but not parser.error(), which also receives raw arguments for
    # recommendations. This protects the error path, not core debug logging before extension load.
    error.print_error()
    error.send_telemetry()
    invocation.parser.exit(2)


class QuantumCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        super().__init__(cli_ctx=cli_ctx)

        # Save the CLI context config for use in load_arguments
        self.cli_ctx_config = cli_ctx.config

        # A CLI context can load this extension repeatedly (for example in interactive use).
        cli_ctx.unregister_event(EVENT_INVOKER_PRE_PARSE_ARGS, _reject_removed_job_storage_argument)
        cli_ctx.register_event(EVENT_INVOKER_PRE_PARSE_ARGS, _reject_removed_job_storage_argument)

    def load_command_table(self, args):
        from azext_quantum.commands import load_command_table
        load_command_table(self, args)

        # See if the user is running the latest version of the quantum extension.
        from ._version_check_helper import check_version
        from .operations.workspace import _show_tip
        from datetime import datetime
        from collections.abc import Iterable

        # Only when formatted output (https://learn.microsoft.com/en-us/cli/azure/format-output-azure-cli?view=azure-cli-latest&tabs=bash) is NOT requested,
        # we can produce the "new version is available" tip as it may interfere with the output format (ex. JSON).
        if isinstance(args, Iterable) and "--output" not in args and "--out" not in args and "-o" not in args:
            message = check_version(self.cli_ctx_config, CLI_REPORTED_VERSION, str(
                datetime.today()).split(' ', maxsplit=1)[0])

            if message is not None:
                _show_tip(message)

        return self.command_table

    def load_arguments(self, command):
        from azext_quantum._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = QuantumCommandsLoader
