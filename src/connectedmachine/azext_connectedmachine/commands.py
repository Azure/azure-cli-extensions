# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_connectedmachine._client_factory import cf_connectedmachine


def load_command_table(self, _):

    connectedmachine_sdk = CliCommandType(
        operations_tmpl='azext_connectedmachine.vendored_sdks.operations#MachinesOperations.{}',
        client_factory=cf_connectedmachine)

    with self.command_group('connectedmachine', connectedmachine_sdk, client_factory=cf_connectedmachine) as g:
        g.custom_command('delete', 'delete_connectedmachine')
        g.custom_command('list', 'list_connectedmachine')
        g.custom_show_command('show', 'show_connectedmachine')

    with self.command_group('connectedmachine', is_preview=True):
        pass
