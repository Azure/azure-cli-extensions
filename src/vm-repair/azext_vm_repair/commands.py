# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from ._validators import validate_create, validate_restore, validate_run


# pylint: disable=too-many-locals, too-many-statements
def load_command_table(self, _):

    with self.command_group('vm repair') as g:
        g.custom_command('create', 'create', validator=validate_create)
        g.custom_command('restore', 'restore', validator=validate_restore)
        g.custom_command('run', 'run', validator=validate_run)
        g.custom_command('list-scripts', 'list_scripts')
