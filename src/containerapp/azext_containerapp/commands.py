# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_containerapp._client_factory import cf_containerapp, ex_handler_factory


def load_command_table(self, _):

    # TODO: Add command type here
    # containerapp_sdk = CliCommandType(
    #    operations_tmpl='<PATH>.operations#None.{}',
    #    client_factory=cf_containerapp)


    with self.command_group('containerapp') as g:
        g.custom_command('create', 'create_containerapp')


    with self.command_group('containerapp env') as g:
        g.custom_command('show', 'show_kube_environment')
        # g.custom_command('show', 'show_managed_environment')
        g.custom_command('list', 'list_kube_environments')
        # g.custom_command('list', 'list_managed_environments')
        g.custom_command('create', 'create_kube_environment', supports_no_wait=True, exception_handler=ex_handler_factory())
        # g.custom_command('create', 'create_managed_environment', supports_no_wait=True, exception_handler=ex_handler_factory())
        g.custom_command('update', 'update_kube_environment', supports_no_wait=True, exception_handler=ex_handler_factory())
        # g.custom_command('update', 'update_managed_environment', supports_no_wait=True, exception_handler=ex_handler_factory())
        g.custom_command('delete', 'delete_kube_environment', supports_no_wait=True, confirmation=True, exception_handler=ex_handler_factory())
        # g.command('delete', 'delete_managed_environment', supports_no_wait=True, confirmation=True, exception_handler=ex_handler_factory())
