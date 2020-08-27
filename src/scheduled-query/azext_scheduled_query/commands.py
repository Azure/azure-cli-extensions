# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_scheduled_query._client_factory import cf_scheduled_query


def load_command_table(self, _):

    # TODO: Add command type here
    # scheduled_query_sdk = CliCommandType(
    #    operations_tmpl='<PATH>.operations#None.{}',
    #    client_factory=cf_scheduled_query)


    with self.command_group('scheduled-query') as g:
        g.custom_command('create', 'create_scheduled_query')
        # g.command('delete', 'delete')
        g.custom_command('list', 'list_scheduled_query')
        # g.show_command('show', 'get')
        # g.generic_update_command('update', setter_name='update', custom_func_name='update_scheduled_query')


    with self.command_group('scheduled-query', is_preview=True):
        pass

