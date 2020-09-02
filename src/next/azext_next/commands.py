# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=unused-import
from azure.cli.core.commands import CliCommandType
from azext_next._client_factory import cf_next


def load_command_table(self, _):
    with self.command_group('') as g:
        g.custom_command('next', 'handle_next', is_experimental=True)
