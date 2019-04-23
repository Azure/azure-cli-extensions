# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType

from ._validators import validate_swap_disk, validate_restore_swap

# pylint: disable=too-many-locals, too-many-statements
def load_command_table(self, _):

    with self.command_group('hello') as g:
            g.custom_command('world', 'helloworld')

    # TODO add list, show, wait? 
    with self.command_group('vm repair') as g:
        g.custom_command('swap-disk', 'swap_disk', validator=validate_swap_disk)
        g.custom_command('restore-swap', 'restore_swap', validator=validate_restore_swap)
