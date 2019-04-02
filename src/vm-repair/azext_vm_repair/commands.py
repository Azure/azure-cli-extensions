# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType


# pylint: disable=too-many-locals, too-many-statements
def load_command_table(self, _):

    with self.command_group('hello') as g:
            g.custom_command('world', 'helloworld')

    with self.command_group('vm repair') as g:
        g.show_command('show', 'get')
        g.command('swap-disk', 'swap_disk')
        g.command('restore-swap', 'restore_swap')
        g.wait_command('wait')
