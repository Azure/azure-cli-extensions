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
    transform_location_detail_output)


def load_command_table(self, _):

    plan_operations = CliCommandType(
        operations_tmpl='azext_codespaces.vendored_sdks.vsonline.operations.plan_operations#PlanOperations.{}',
        client_factory=cf_codespaces)

    with self.command_group('codespace plan', plan_operations, client_factory=cf_codespaces_plan) as g:
        g.custom_command('list', 'list_plans')
        g.custom_command('create', 'create_plan')
        g.show_command('show', 'get')
        g.command('delete', 'delete')

    with self.command_group('codespace', plan_operations, client_factory=cf_codespaces_plan) as g:
        g.custom_command('list', 'list_codespaces', table_transformer=transform_codespace_list_output)
        g.custom_show_command('show', 'get_codespace', table_transformer=transform_codespace_item_output)
        g.custom_command('create', 'create_codespace', table_transformer=transform_codespace_item_output)
        g.custom_command('open', 'open_codespace')
        g.custom_command('delete', 'delete_codespace', confirmation="Are you sure you want to delete this Codespace?")
        g.custom_command('resume', 'resume_codespace', table_transformer=transform_codespace_item_output)
        g.custom_command('suspend', 'suspend_codespace', table_transformer=transform_codespace_item_output)

    with self.command_group('codespace location', plan_operations, client_factory=cf_codespaces_plan) as g:
        g.custom_command('list', 'list_available_locations', table_transformer=transform_location_list_output)
        g.custom_show_command('show', 'get_location_details', table_transformer=transform_location_detail_output)

    # Mark all commands as in preview
    with self.command_group('codespace', is_preview=True):
        pass
