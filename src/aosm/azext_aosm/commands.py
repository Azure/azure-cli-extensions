# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import CliCommandType
from azext_aosm._client_factory import cf_aosm


def load_command_table(self: AzCommandsLoader, _):

    # TODO: Add command type here
    # aosm_sdk = CliCommandType(
    #    operations_tmpl='<PATH>.operations#None.{}',
    #    client_factory=cf_aosm)

    with self.command_group('aosm definition', client_factory=cf_aosm) as g:
        # Add each command and bind it to a function in custom.py
        g.custom_command('generate-config', 'generate_definition_config')
        g.custom_command('build', 'build_definition')
        g.custom_command('delete', 'delete_published_definition')
        g.custom_command('show', 'show_publisher')

    with self.command_group('aosm', is_preview=True):
        pass
