# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_durabletask._client_factory import cf_durabletask, cf_durabletask_namespaces, cf_durabletask_taskhubs


def load_command_table(self, _):

    durabletask_sdk = CliCommandType(
        operations_tmpl='azext_durabletask.vendored_sdks.operations#DurabletaskOperations.{}',
        client_factory=cf_durabletask)

    durabletask_namespace_sdk = CliCommandType(
        operations_tmpl='azext_durabletask.vendored_sdks.operations#NamespacesOperations.{}',
        client_factory=cf_durabletask_namespaces)

    durabletask_taskhub_sdk = CliCommandType(
        operations_tmpl='azext_durabletask.vendored_sdks.operations#TaskHubsOperations.{}',
        client_factory=cf_durabletask_taskhubs)

    with self.command_group('durabletask', durabletask_sdk, client_factory=cf_durabletask) as g:
        g.custom_command('create', 'create_durabletask')
        # g.command('delete', 'delete')
        g.custom_command('list', 'list_durabletask')
        # g.show_command('show', 'get')
        g.generic_update_command('update', setter_name='update', custom_func_name='update_durabletask')


    with self.command_group('durabletask namespace', durabletask_namespace_sdk, client_factory=cf_durabletask_namespaces) as g:
        g.custom_command('create', 'create_namespace')
        g.custom_command('list', 'list_namespace')
        # g.delete_command('delete', 'delete_namespace')
        g.generic_update_command('update', setter_name='update', custom_func_name='update_namespace')


    with self.command_group('durabletask taskhub', durabletask_sdk, client_factory=cf_durabletask_taskhubs) as g:
        g.custom_command('create', 'create_taskhub')
        g.custom_command('list', 'list_taskhub')
        # g.show_command('show', 'show_taskhub')
        g.generic_update_command('update', setter_name='update', custom_func_name='update_taskhub')

    with self.command_group('durabletask', is_preview=True):
        pass

