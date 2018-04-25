# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.core.commands import CliCommandType

from ._client_factory import cf_signalr
from azure.cli.core.util import empty_on_404


def load_command_table(self, _):

    signalr_custom_util = CliCommandType(
        operations_tmpl='azext_signalr.custom#{}',
        client_factory=cf_signalr
    )

    signalr_key_utils = CliCommandType(
        operations_tmpl='azext_signalr.key#{}',
        client_factory=cf_signalr
    )

    with self.command_group('signalr', signalr_custom_util) as g:
        g.command('create', 'signalr_create')
        g.command('delete', 'signalr_delete')
        g.command('list', 'signalr_list')
        g.command('show', 'signalr_show', exception_handler=empty_on_404)

    with self.command_group('signalr key', signalr_key_utils) as g:
        g.command('list', 'signalr_key_list')
        g.command('renew', 'signalr_key_renew')
