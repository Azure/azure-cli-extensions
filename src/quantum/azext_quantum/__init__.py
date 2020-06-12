# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=import-outside-toplevel
from azure.cli.core import AzCommandsLoader

import azext_quantum._help  # pylint: disable=unused-import

class QuantumCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        super(QuantumCommandsLoader, self).__init__(cli_ctx=cli_ctx)

    def load_command_table(self, args):
        from azext_quantum.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_quantum._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = QuantumCommandsLoader
