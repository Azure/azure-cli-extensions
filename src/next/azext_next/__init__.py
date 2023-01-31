# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import threading

from azure.cli.core import AzCommandsLoader

from azext_next._help import helps  # pylint: disable=unused-import


class NextCommandsLoader(AzCommandsLoader):

    _instance_lock = threading.Lock()
    _has_reload_command_table = False

    def __new__(cls, cli_ctx=None):  # pylint: disable=unused-argument
        if not hasattr(NextCommandsLoader, "_instance"):
            with NextCommandsLoader._instance_lock:
                if not hasattr(NextCommandsLoader, "_instance"):
                    NextCommandsLoader._instance = super(NextCommandsLoader, cls).__new__(cls)
        return NextCommandsLoader._instance

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        next_custom = CliCommandType(
            operations_tmpl='azext_next.custom#{}')
        super().__init__(cli_ctx=cli_ctx, custom_command_type=next_custom)

    # Because the help content of other modules needs to be loaded when executing "az next"
    # So modify the environment variable AZURE_CORE_USE_COMMAND_INDEX=False, and then reload the command table
    # But commands_loader.load_command_table(args) will not only reload new object of NextCommandsLoader,
    # but also recursively calls load_command_table() again, and fall into infinite nested call
    # So NextCommandsLoader is a singleton, and _has_reload_command_table is used to avoid infinite nested calls
    def load_command_table(self, args):
        # When executing "azdev linter --include-whl-extensions next" in CI, args is none, so judgment is added
        if args:
            from azure.cli.core.util import roughly_parse_command
            command = roughly_parse_command(args)
            if command == 'next' and not self._has_reload_command_table:
                self._has_reload_command_table = True
                from unittest.mock import patch
                with patch.dict("os.environ", {'AZURE_CORE_USE_COMMAND_INDEX': 'False'}):
                    self.cli_ctx.invocation.commands_loader.load_command_table(args)

            from azext_next.utils import log_command_history
            log_command_history(command, args)

        from azext_next.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_next._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = NextCommandsLoader
