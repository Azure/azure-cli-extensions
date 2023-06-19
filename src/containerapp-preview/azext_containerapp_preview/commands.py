# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.command_modules.appservice.commands import ex_handler_factory
from ._utils import (_get_or_add_extension, _get_azext_module, GA_CONTAINERAPP_EXTENSION_NAME)

# pylint: disable=line-too-long


def load_command_table(self, _):
    if not _get_or_add_extension(self, GA_CONTAINERAPP_EXTENSION_NAME):
        return
    azext_commands = _get_azext_module(
        GA_CONTAINERAPP_EXTENSION_NAME, "azext_containerapp.commands")

    with self.command_group('containerapp') as g:
        g.custom_show_command('show', 'show_containerapp', table_transformer=azext_commands.transform_containerapp_output, is_preview=True)
        g.custom_command('list', 'list_containerapp', table_transformer=azext_commands.transform_containerapp_list_output, is_preview=True)
        g.custom_command('delete', 'delete_containerapp', supports_no_wait=True, confirmation=True, exception_handler=ex_handler_factory(), is_preview=True)
        # g.custom_command('update', 'update_containerapp', supports_no_wait=True, exception_handler=ex_handler_factory(), table_transformer=azext_commands.transform_containerapp_output)
        g.custom_command('create', 'create_containerapp', supports_no_wait=True, exception_handler=ex_handler_factory(), table_transformer=azext_commands.transform_containerapp_output, is_preview=True)
