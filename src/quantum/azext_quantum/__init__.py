# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from azure.cli.core import AzCommandsLoader

import azext_quantum._help  # pylint: disable=unused-import


# This is the version reported by the CLI to the service when submitting requests.
# This should be in sync with the extension version in 'setup.py', unless we need to
# submit using a different version.
CLI_REPORTED_VERSION = "1.0.0b3"


class QuantumCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        super().__init__(cli_ctx=cli_ctx)

        # Save the CLI context config for use in load_arguments
        self.cli_ctx_config = cli_ctx.config

    def load_command_table(self, args):
        from azext_quantum.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_quantum._params import load_arguments
        load_arguments(self, command)

        # See if the user is running the latest version of the quantum extension.
        from ._version_check_helper import check_version
        from .operations.workspace import _show_tip
        from datetime import datetime
        message = check_version(self.cli_ctx_config, CLI_REPORTED_VERSION, str(datetime.today()).split(' ', maxsplit=1)[0])
        if message is not None:
            _show_tip(message)


COMMAND_LOADER_CLS = QuantumCommandsLoader
