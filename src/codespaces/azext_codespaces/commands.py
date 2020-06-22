# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from ._client_factory import cf_codespaces, cf_codespaces_plan
from ._transformers import (
    transform_codespace_list_output,
    transform_codespace_item_output,
    transform_location_list_output,
    transform_location_detail_output,
    transform_plan_secret_list_output)


def advanced_usage_message(_):
    return 'This command is for advanced usage only.'


def load_command_table(self, _):

    plan_operations = CliCommandType(
        operations_tmpl='azext_codespaces.vendored_sdks.vsonline.operations.plan_operations#PlanOperations.{}',
        client_factory=cf_codespaces)

    with self.command_group('codespace plan', plan_operations, client_factory=cf_codespaces_plan) as g:
        g.custom_command('list', 'list_plans')
        g.custom_command('create', 'create_plan')
        # TODO Re-enable plan update when service-side implemented
        # g.custom_command('update', 'update_plan')
        g.show_command('show', 'get')
        g.command('delete', 'delete', confirmation="Are you sure you want to delete this Codespace plan?")

    with self.command_group('codespace secret', plan_operations, client_factory=cf_codespaces_plan) as g:
        g.custom_command('list', 'list_plan_secrets', table_transformer=transform_plan_secret_list_output)
        g.custom_command('update', 'update_plan_secrets')
        g.custom_command('create', 'create_plan_secret')
        g.custom_command('delete', 'delete_plan_secret')

    with self.command_group('codespace', plan_operations, client_factory=cf_codespaces_plan) as g:
        g.custom_command('list', 'list_codespaces', table_transformer=transform_codespace_list_output)
        g.custom_show_command('show', 'get_codespace', table_transformer=transform_codespace_item_output)
        g.custom_command('create', 'create_codespace', table_transformer=transform_codespace_item_output)
        g.custom_command('open', 'open_codespace')
        g.custom_command('delete', 'delete_codespace', confirmation="Are you sure you want to delete this Codespace?")
        g.custom_command('resume', 'resume_codespace', table_transformer=transform_codespace_item_output)
        g.custom_command('suspend', 'suspend_codespace', table_transformer=transform_codespace_item_output)
        g.custom_command('update', 'update_codespace', table_transformer=transform_codespace_item_output)

    # Hidden commands that should largely be used by the dev team
    with self.command_group('codespace') as g:
        g.custom_command('set-config', 'set_config',
                         deprecate_info=self.deprecate(hide=True, message_func=advanced_usage_message))
        g.custom_command('show-config', 'show_config',
                         deprecate_info=self.deprecate(hide=True, message_func=advanced_usage_message))

    with self.command_group('codespace location') as g:
        g.custom_command('list', 'list_available_locations', table_transformer=transform_location_list_output)
        g.custom_show_command('show', 'get_location_details', table_transformer=transform_location_detail_output)

    # Mark all commands as in preview
    with self.command_group('codespace', is_preview=True):
        pass
