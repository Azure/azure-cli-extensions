# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_serialconsole._client_factory import cf_serialconsole


def load_command_table(self, _):

    # TODO: Add command type here
    # serialconsole_sdk = CliCommandType(
    #    operations_tmpl='<PATH>.operations#None.{}',
    #    client_factory=cf_serialconsole)


    with self.command_group('serialconsole') as g:
        g.custom_command('connect', 'connect_serialconsole')
        g.custom_command('send-nmi', 'send_nmi_serialconsole')
        g.custom_command('reset-vm', 'send_reset_serialconsole')
        g.custom_command('send-sysrq', 'send_sysrq_serialconsole')


    with self.command_group('serialconsole', is_preview=True):
        pass

